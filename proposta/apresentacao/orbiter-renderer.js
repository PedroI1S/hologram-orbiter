/* O mesmo rotor sólido do slide de arrasto, em três etapas de escrita dos LEDs.
 * Desenho ortográfico em milímetros. A sequência é ilustrativa e desacelerada.
 * draw recebe coordenadas lógicas: o chamador configura a resolução do Canvas.
 */
(() => {
  'use strict';
  const TAU = 2 * Math.PI;
  const DEG = Math.PI / 180;
  const FRONT = -2 * Math.PI / 3;
  const PROFILE = [[-.8,-17],[-4,-7],[-4,9],[-2.8,12],[0,13],[2.8,12],[4,9],[4,-7],[.8,-17]];
  const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));
  const wrapDegrees = value => ((value + 180) % 360 + 360) % 360 - 180;

  function draw(ctx, options = {}) {
    const width = options.width || 368;
    const height = options.height || 270;
    const phase = clamp(Number(options.phaseDegrees) || 0, 0, 120);
    const stage = clamp(Math.floor(Number(options.stage) || 0), 0, 2);
    const pixel = typeof options.pixel === 'function' ? options.pixel : () => 0;
    const fit = Math.min(width / 330, height / 270);
    const scale = .64 * fit;
    const cx = width / 2;
    const baseY = height / 2 + 74 * fit;
    const radius = 100;
    const phases = [0, 1, 2].map(k => FRONT + (-60 + phase + 120 * k) * DEG);

    function project(x, y, z = 0) {
      return [cx + scale * 1.26 * (.866 * x - .5 * y),
        baseY - scale * .41 * (.5 * x + .866 * y) - scale * 1.04 * z];
    }
    function at(r, phi, z) { return project(r * Math.cos(phi), r * Math.sin(phi), z); }
    function stroke(points, color, lineWidth = 1, close = false) {
      if (!points.length) return;
      ctx.beginPath();
      ctx.moveTo(...points[0]);
      for (let i = 1; i < points.length; i++) ctx.lineTo(...points[i]);
      if (close) ctx.closePath();
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth * fit;
      ctx.stroke();
    }
    function polygon(points, fill, outline) {
      ctx.beginPath();
      ctx.moveTo(...points[0]);
      for (let i = 1; i < points.length; i++) ctx.lineTo(...points[i]);
      ctx.closePath();
      ctx.fillStyle = fill;
      ctx.fill();
      if (outline) {
        ctx.strokeStyle = outline;
        ctx.lineWidth = .65 * fit;
        ctx.stroke();
      }
    }
    function cylinder(r, z0, z1, top, side) {
      const upper = [], face = [];
      for (let i = 0; i <= 48; i++) upper.push(at(r, TAU * i / 48, z1));
      for (let i = 0; i <= 24; i++) face.push(at(r, 5 * Math.PI / 6 + Math.PI * i / 24, z0));
      for (let i = 24; i >= 0; i--) face.push(at(r, 5 * Math.PI / 6 + Math.PI * i / 24, z1));
      polygon(face, side, '#39536a');
      polygon(upper, top, '#55768b');
    }
    function emissionColor(value, alpha) {
      return value === 2 ? `rgba(255,225,160,${alpha})` : `rgba(146,199,241,${alpha})`;
    }
    function led(q, value, alpha = 1) {
      ctx.save();
      ctx.globalAlpha *= alpha;
      if (value) {
        ctx.fillStyle = value === 2 ? '#ffe4a6' : '#b7e2ff';
        ctx.shadowColor = value === 2 ? '#ffca71' : '#62baff';
        ctx.shadowBlur = 4.2 * fit;
      } else {
        ctx.fillStyle = '#45677a';
      }
      const w = (value ? 1.7 : 1.05) * fit;
      const h = (value ? 1.85 : 1.25) * fit;
      ctx.fillRect(q[0] - w / 2, q[1] - h / 2, w, h);
      ctx.restore();
    }
    function panel(phi) {
      const radial = [Math.cos(phi), Math.sin(phi)];
      const tangent = [-Math.sin(phi), Math.cos(phi)];
      const pt = (v, z) => project(radial[0] * (radius + v[0]) + tangent[0] * v[1],
        radial[1] * (radius + v[0]) + tangent[1] * v[1], z);
      const faces = PROFILE.map((a, i) => ({ a, b: PROFILE[(i + 1) % PROFILE.length], i }));
      faces.sort((a, b) => pt(a.a, 20)[1] + pt(a.b, 20)[1] - pt(b.a, 20)[1] - pt(b.b, 20)[1]);
      for (const { a, b, i } of faces) {
        polygon([pt(a, 22), pt(b, 22), pt(b, 230), pt(a, 230)], i > 4 ? '#345f7a' : '#487e9c', '#648ca6');
      }
      polygon(PROFILE.map(p => pt(p, 230)), '#83b2ca', '#a3c8da');
      stroke([pt([4.6, 0], 26), pt([4.6, 0], 227)], '#11384e', 2.25);
      const theta = wrapDegrees((phi - FRONT) / DEG);
      for (let row = 0; row < 29; row++) {
        led(pt([4.8, 0], 227 - row * 201 / 28), pixel(theta, row));
      }
    }
    function fixedBase() {
      ctx.save();
      ctx.fillStyle = 'rgba(0,0,0,.2)';
      ctx.beginPath();
      ctx.ellipse(cx, baseY + 16 * fit, 112 * fit, 23 * fit, 0, 0, TAU);
      ctx.fill();
      cylinder(132, -5, 0, '#152b3d', '#102132');
      ctx.restore();
    }
    function rotor() {
      const sorted = [...phases].sort((a, b) => at(radius, a, 0)[1] - at(radius, b, 0)[1]);
      ctx.save();
      if (stage === 2) ctx.globalAlpha *= .63;
      for (const phi of sorted) if (at(radius, phi, 0)[1] < baseY) panel(phi);
      cylinder(31, 0, 75, '#496272', '#273b4a');
      cylinder(22, 75, 99, '#596e78', '#354d5a');
      cylinder(6, 96, 129, '#acc1cb', '#7996a5');
      for (const phi of sorted) {
        stroke([at(24, phi, 127), at(radius - 4, phi, 127)], '#53788f', 5.1);
        stroke([at(25, phi, 129), at(radius - 5, phi, 129)], '#9bb8c9', 1.3);
      }
      cylinder(36, 116, 137, '#67889b', '#2d495c');
      for (const phi of sorted) if (at(radius, phi, 0)[1] >= baseY) panel(phi);
      ctx.restore();
    }
    function accumulatedLight() {
      if (stage === 0 || phase <= 0) return;
      ctx.save();
      ctx.lineCap = 'round';
      // The first written cell is 1° beyond each initial position. Its centre
      // runs from -179° in 2° steps, with exactly 60 columns per 120° sector.
      for (let col = 0; col < 180; col++) {
        const theta = -179 + col * 2;
        const writtenAt = ((theta + 60) % 120 + 120) % 120 + 1;
        if (writtenAt > phase + .0001) continue;
        const phi = FRONT + theta * DEG;
        const age = (phase - writtenAt) / 120;
        for (let row = 0; row < 29; row++) {
          const value = pixel(theta, row);
          if (!value) continue;
          const z = 227 - row * 201 / 28;
          if (stage === 1) {
            // Short adjoining luminous arcs follow the same cylindrical path
            // as a lit LED. Older emission remains as a softer blue/gold wake.
            const alpha = .37 + .52 * Math.exp(-age * 2.1);
            stroke([at(radius + 5, phi - .94 * DEG, z), at(radius + 5, phi, z),
              at(radius + 5, phi + .94 * DEG, z)], emissionColor(value, alpha), 1.5);
          } else {
            const q = at(radius + 5, phi, z);
            ctx.fillStyle = emissionColor(value, .96);
            ctx.shadowColor = value === 2 ? '#ffc15a' : '#62baff';
            ctx.shadowBlur = 2.4 * fit;
            ctx.fillRect(q[0] - .78 * fit, q[1] - .87 * fit, 1.56 * fit, 1.74 * fit);
          }
        }
      }
      ctx.restore();
    }

    ctx.save();
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
    ctx.shadowBlur = 0;
    ctx.setLineDash([]);
    const background = ctx.createLinearGradient(0, 0, width, height);
    background.addColorStop(0, '#10283e');
    background.addColorStop(1, '#071421');
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, width, height);
    fixedBase();
    if (stage === 1) accumulatedLight();
    rotor();
    if (stage === 2) accumulatedLight();
    ctx.restore();
  }

  window.OrbiterRenderer = Object.freeze({ draw });
})();
