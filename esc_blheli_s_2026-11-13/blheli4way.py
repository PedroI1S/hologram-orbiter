"""MSP passthrough + BLHeli 4-way interface (SiLabs BLB) via Arduino Uno passthrough.

Usage: blheli4way.py PORT read OUTDIR
       blheli4way.py PORT write OUTDIR off=val [off=val ...]
"""
import sys, time, json, hashlib, struct
import serial

CFG_ADDR, CFG_LEN, PAGE_SIZE = 0x1A00, 0x70, 0x200


def crc16_xmodem(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


class Link:
    def __init__(self, port):
        self.s = serial.Serial(port, 115200, timeout=1.0)
        time.sleep(2.5)  # Uno resets on open
        self.s.reset_input_buffer()

    def msp(self, cmd, payload=b""):
        size = len(payload)
        ck = size ^ cmd
        for b in payload:
            ck ^= b
        self.s.write(b"$M<" + bytes([size, cmd]) + payload + bytes([ck]))
        hdr = self.s.read(5)
        if len(hdr) < 5 or hdr[:3] != b"$M>":
            raise RuntimeError("MSP %d: bad header %r" % (cmd, hdr))
        n = hdr[3]
        body = self.s.read(n + 1)
        return body[:n]

    def fw(self, cmd, addr=0, params=b"\x00", tries=3):
        frame = bytes([0x2F, cmd, addr >> 8, addr & 0xFF, len(params) & 0xFF]) + params
        frame += struct.pack(">H", crc16_xmodem(frame))
        for _ in range(tries):
            self.s.reset_input_buffer()
            self.s.write(frame)
            hdr = self.s.read(5)
            if len(hdr) < 5 or hdr[0] != 0x2E:
                time.sleep(0.2)
                continue
            n = hdr[4] or 256
            rest = self.s.read(n + 3)
            data, ack, crc = rest[:n], rest[n], rest[n + 1:n + 3]
            if crc16_xmodem(hdr + rest[:n + 1]) != struct.unpack(">H", crc)[0]:
                time.sleep(0.2)
                continue
            if ack != 0:
                raise RuntimeError("4way cmd 0x%02X ack 0x%02X" % (cmd, ack))
            return data
        raise RuntimeError("4way cmd 0x%02X: no valid reply" % cmd)

    def read(self, addr, n):
        out = b""
        while n:
            k = min(n, 128)
            out += self.fw(0x3A, addr, bytes([k]))
            addr += k
            n -= k
        return out

    def write(self, addr, data):
        while data:
            k = data[:128]
            self.fw(0x3B, addr, k)
            addr += len(k)
            data = data[len(k):]


def decode(c):
    sp = {9: "0.50", 10: "0.75", 8: "0.38", 11: "1.00"}
    return {
        "revision": "%d.%d" % (c[0], c[1]), "layout_rev": c[2],
        "startup_power_raw": c[9], "startup_power": sp.get(c[9], "?"),
        "motor_direction_raw": c[11],
        "motor_direction": {1: "Normal", 2: "Reversed", 3: "Bidirectional", 4: "Bidirectional Reversed"}.get(c[11]),
        "commutation_timing_raw": c[21], "ppm_min_us": 1000 + 4 * c[25], "ppm_max_us": 1000 + 4 * c[26],
        "beep_strength": c[27], "beacon_strength": c[28], "beacon_delay": c[29],
        "demag_raw": c[31], "demag": {1: "Off", 2: "Low", 3: "High"}.get(c[31]),
        "temperature_protection_raw": c[35], "low_rpm_power_protection_raw": c[36],
        "brake_on_stop_raw": c[39], "led_control": c[40],
        "layout": c[64:80].decode("ascii", "replace").strip(),
        "mcu": c[80:96].decode("ascii", "replace").strip(),
        "name": c[96:112].decode("ascii", "replace").strip(),
    }


def main():
    port, mode, outdir = sys.argv[1:4]
    L = Link(port)
    info = {"fc_variant": L.msp(2).decode(errors="replace"), "api": list(L.msp(1))}
    n_esc = L.msp(245)
    info["passthrough_escs"] = list(n_esc)
    time.sleep(0.5)
    info["if_name"] = L.fw(0x32).decode(errors="replace")
    info["if_version"] = list(L.fw(0x33))
    try:
        sig = L.fw(0x37, 0, b"\x00")
        info["init_flash"] = sig.hex()
        page = L.read(CFG_ADDR, PAGE_SIZE)
        cfg = page[:CFG_LEN]
        info["before_sha256"] = hashlib.sha256(cfg).hexdigest()
        info["before"] = decode(cfg)
        open(outdir + "/esc1-pagina-antes-0x1a00.bin", "wb").write(page)
        open(outdir + "/esc1-config-antes-0x1a00.bin", "wb").write(cfg)
        if mode == "write":
            new = bytearray(page)
            changes = []
            for kv in sys.argv[4:]:
                off, val = (int(x, 0) for x in kv.split("="))
                changes.append({"offset": off, "before": page[off], "after": val})
                new[off] = val
            L.fw(0x39, 0, bytes([CFG_ADDR // PAGE_SIZE]))  # page erase
            L.write(CFG_ADDR, bytes(new[:CFG_LEN]))
            reads = [L.read(CFG_ADDR, CFG_LEN) for _ in range(2)]
            ok = all(r == bytes(new[:CFG_LEN]) for r in reads)
            open(outdir + "/esc1-config-gravada-0x1a00.bin", "wb").write(reads[0])
            info.update(changes=changes, readback_ok=ok, readback_confirmations=sum(r == bytes(new[:CFG_LEN]) for r in reads),
                        after_sha256=hashlib.sha256(reads[0]).hexdigest(), after=decode(reads[0]))
    finally:
        try:
            L.fw(0x35, 0, b"\x00")  # device reset
        except Exception as e:
            info["reset_error"] = str(e)
        try:
            L.fw(0x34)  # interface exit
        except Exception as e:
            info["exit_error"] = str(e)
        L.s.close()
        print(json.dumps(info, indent=2, ensure_ascii=False))


main()
