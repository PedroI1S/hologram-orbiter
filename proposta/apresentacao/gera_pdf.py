#!/usr/bin/env python3
"""Gera apresentacao.pdf a partir de apresentacao.html (um slide 1280 x 720 px por página).

Abre um navegador Chromium (Chromium, Chrome, Brave ou Edge) em modo headless e usa o
protocolo DevTools por pipe: espera a página carregar, as fontes ficarem prontas e os
gráficos serem desenhados, e então chama Page.printToPDF. Não depende de pacotes externos.

Uso:  python3 gera_pdf.py [--navegador /caminho/do/navegador]
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CANDIDATOS = ["chromium", "chromium-browser", "google-chrome-stable", "google-chrome",
              "/opt/brave-bin/brave", "brave", "brave-browser", "microsoft-edge"]


def _ambiente():
    # O Chromium cria um socket dentro do TMPDIR; caminhos longos (> 107 bytes no total) o derrubam.
    env = os.environ.copy()
    if len(tempfile.gettempdir()) > 60 and os.path.isdir("/tmp"):
        env["TMPDIR"] = "/tmp"
    return env


class Navegador:
    def __init__(self, executavel: str, perfil: str):
        self._para_nav_r, self._para_nav_w = os.pipe()
        self._do_nav_r, self._do_nav_w = os.pipe()

        def prepara_fds():
            # O protocolo por pipe usa o fd 3 para leitura e o fd 4 para escrita.
            a, b = os.dup(self._para_nav_r), os.dup(self._do_nav_w)
            os.dup2(a, 3)
            os.dup2(b, 4)

        self.proc = subprocess.Popen(
            [executavel, "--headless=new", "--remote-debugging-pipe", f"--user-data-dir={perfil}",
             "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-extensions",
             "--disable-component-update", "--disable-background-networking", "--disable-sync",
             "--password-store=basic", "--use-mock-keychain", "about:blank"],
            preexec_fn=prepara_fds, close_fds=False, env=_ambiente(),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(self._para_nav_r)
        os.close(self._do_nav_w)
        self._buffer = b""
        self._id = 0
        self._eventos = []

    def _envia(self, metodo, params=None, sessao=None):
        self._id += 1
        msg = {"id": self._id, "method": metodo, "params": params or {}}
        if sessao:
            msg["sessionId"] = sessao
        os.write(self._para_nav_w, json.dumps(msg).encode() + b"\0")
        return self._id

    def _proxima(self, limite):
        while b"\0" not in self._buffer:
            if time.monotonic() > limite:
                raise TimeoutError("o navegador não respondeu a tempo")
            parte = os.read(self._do_nav_r, 1 << 16)
            if not parte:
                raise RuntimeError("o navegador fechou o canal DevTools")
            self._buffer += parte
        bruto, self._buffer = self._buffer.split(b"\0", 1)
        return json.loads(bruto)

    def chama(self, metodo, params=None, sessao=None, espera=60):
        ident = self._envia(metodo, params, sessao)
        limite = time.monotonic() + espera
        while True:
            msg = self._proxima(limite)
            if msg.get("id") == ident:
                if "error" in msg:
                    raise RuntimeError(f"{metodo}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self._eventos.append(msg)

    def espera_evento(self, metodo, sessao, espera=60):
        limite = time.monotonic() + espera
        while True:
            for i, msg in enumerate(self._eventos):
                if msg["method"] == metodo and msg.get("sessionId") == sessao:
                    return self._eventos.pop(i)
            self._eventos.append(self._proxima(limite))

    def fecha(self):
        try:
            self._envia("Browser.close")
        except OSError:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--navegador", default=os.environ.get("NAVEGADOR"))
    ap.add_argument("--entrada", default=str(AQUI / "apresentacao.html"))
    ap.add_argument("--saida", default=str(AQUI / "apresentacao.pdf"))
    args = ap.parse_args()

    executavel = args.navegador or next((c for c in CANDIDATOS if shutil.which(c)), None)
    if not executavel:
        sys.exit("Nenhum navegador Chromium encontrado; use --navegador /caminho/do/navegador.")

    perfil = tempfile.mkdtemp(prefix="ho-pdf-")
    nav = Navegador(executavel, perfil)
    try:
        alvo = nav.chama("Target.createTarget", {"url": "about:blank"})["targetId"]
        sessao = nav.chama("Target.attachToTarget", {"targetId": alvo, "flatten": True})["sessionId"]
        nav.chama("Page.enable", sessao=sessao)
        nav.chama("Page.navigate", {"url": Path(args.entrada).resolve().as_uri()}, sessao=sessao)
        nav.espera_evento("Page.loadEventFired", sessao)
        # Espera o carregamento, as fontes e dois quadros de pintura.
        pronto = ("new Promise(ok => { const vai = () => document.fonts.ready.then(() => "
                  "requestAnimationFrame(() => requestAnimationFrame(() => ok(document.fonts.status)))); "
                  "document.readyState === 'complete' ? vai() : addEventListener('load', vai); })")
        for _ in range(3):
            try:
                r = nav.chama("Runtime.evaluate", {"expression": pronto, "awaitPromise": True,
                                                   "returnByValue": True}, sessao=sessao, espera=60)
                break
            except RuntimeError:
                time.sleep(0.5)  # contexto ainda sendo trocado pela navegação
        else:
            raise RuntimeError("a página não terminou de carregar")
        if r.get("result", {}).get("value") != "loaded":
            print("aviso: fontes não carregadas por completo:", r, file=sys.stderr)
        pdf = nav.chama("Page.printToPDF", {"printBackground": True, "preferCSSPageSize": True,
                                            "displayHeaderFooter": False,
                                            "marginTop": 0, "marginBottom": 0,
                                            "marginLeft": 0, "marginRight": 0},
                        sessao=sessao, espera=180)
        Path(args.saida).write_bytes(base64.b64decode(pdf["data"]))
        print("PDF gerado:", args.saida)
    finally:
        nav.fecha()
        shutil.rmtree(perfil, ignore_errors=True)


if __name__ == "__main__":
    main()
