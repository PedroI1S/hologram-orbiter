/* Escoamento qualitativo inspirado no canvas de convecção dos slides de termologia.
 * Não resolve Navier–Stokes. Partículas traçadoras seguem um campo prescrito;
 * números vêm de v=ωr, f=3n e P/P0=(n/n0)^3(r/r0)^3, área e Cd constantes.
 * Geometria: 3 painéis a 120°, lâmina208, corda30, espessura8 mm.
 * +θ é anti-horário visto de +Z. Ar recebe impulso +tangente; arrasto −tangente.
 */
(() => {
  'use strict';
  const canvas = document.getElementById('orbiter-flow');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const byId = id => document.getElementById(id);
  const rpmControl = byId('arrasto-rpm'), radiusControl = byId('arrasto-raio');
  const airControl = byId('arrasto-air'), imageControl = byId('arrasto-image');
  const scene = byId('arrasto-scene'), chart = byId('arrasto-chart'), view = byId('arrasto-view');
  const TAU = 2*Math.PI, W = 760, H = 420;
  const COLORS = { air:'#65cfe5', force:'#ff946f', velocity:'#c9e7ff', led:'#ffe4a6' };
  const clamp = (x,a,b) => Math.max(a,Math.min(b,x));
  const fmt = (n,d=0) => n.toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
  let rpm = 1800, radius = 100, angle = .4, simTime = 0;
  let active = false, paused = false, printing = false, showChart = false;
  let raf = 0, lastTime = null, lastDraw = 0, seed = 8531;
  const random = () => {seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
  const particles = [];
  const PHYSICAL_TO_VISIBLE = 1/120; // 1800 rpm vira uma volta visível a cada 4 s.
  const angularSpeed = () => TAU*(rpm/60)*PHYSICAL_TO_VISIBLE;
  // Orthographic view, elevated above the rotor. All dimensions below are mm.
  function project(x,y,z=0) { return [273+1.26*(.866*x-.5*y), 349-.41*(.5*x+.866*y)-1.04*z]; }
  function world(r,a,z) { return [r*Math.cos(a),r*Math.sin(a),z]; }
  function at(r,a,z) { return project(...world(r,a,z)); }
  function stroke(points,color,width=1,close=false) {
    if(!points.length)return;
    ctx.beginPath();ctx.moveTo(...points[0]);
    for(let i=1;i<points.length;i++)ctx.lineTo(...points[i]);
    if(close)ctx.closePath();
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
  }
  function polygon(points,fill,outline) {
    ctx.beginPath();ctx.moveTo(...points[0]);points.slice(1).forEach(p=>ctx.lineTo(...p));ctx.closePath();
    ctx.fillStyle=fill;ctx.fill();
    if(outline){ctx.strokeStyle=outline;ctx.lineWidth=.8;ctx.stroke();}
  }
  function ring(r,z,color,width=1,start=0,end=TAU) {
    const pts=[];for(let i=0;i<=80;i++)pts.push(at(r,start+(end-start)*i/80,z));
    stroke(pts,color,width);
  }
  function cylinder(r,z0,z1,top,side) {
    const bottom=[],upper=[];
    for(let i=0;i<=48;i++){bottom.push(at(r,TAU*i/48,z0));upper.push(at(r,TAU*i/48,z1));}
    const face=[];
    for(let i=0;i<=24;i++)face.push(at(r,5*Math.PI/6+Math.PI*i/24,z0));
    for(let i=24;i>=0;i--)face.push(at(r,5*Math.PI/6+Math.PI*i/24,z1));
    polygon(face,side,'#39536a');polygon(upper,top,'#55768b');
  }
  function arrow(x,y,dx,dy,color,width=2.2) {
    const length=Math.hypot(dx,dy);if(length<.01)return;
    const ux=dx/length,uy=dy/length,head=7;
    stroke([[x,y],[x+dx,y+dy]],color,width);
    polygon([[x+dx,y+dy],[x+dx-head*ux+head*.48*uy,y+dy-head*uy-head*.48*ux],[x+dx-head*ux-head*.48*uy,y+dy-head*uy+head*.48*ux]],color);
  }
  function text(value,x,y,size=13,color='#9ab6ce',align='left') {
    ctx.font=`${size>=18?'600':'400'} ${size}px "HO Fira Sans",sans-serif`;
    ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(value,x,y);
  }
  function resetParticles() {
    particles.length=0;seed=8531;
    for(let i=0;i<390;i++){
      const a=random()*TAU, r=radius+(random()-.5)*85;
      const p={a,r,z:29+random()*200,phase:random()*TAU,weight:.4+random()*.6,trail:[],strength:0};
      // Initial curved traces keep the paused/printed scene explanatory.
      for(let j=5;j>=0;j--)p.trail.push(world(r,a-j*.018,p.z));
      particles.push(p);
    }
  }
  function step(dt) {
    const omega=angularSpeed();
    angle=(angle+omega*dt)%TAU;simTime+=dt;
    for(const p of particles){
      let behind=TAU;
      for(let k=0;k<3;k++)behind=Math.min(behind,((angle+k*TAU/3-p.a)%TAU+TAU)%TAU);
      const band=Math.exp(-(((p.r-radius)/21)**2));
      // A blade runs ahead of air which it entrains locally. No rigid-body swirl.
      const wake=band*Math.exp(-behind/.68);
      const circulation=(.028*band+.48*wake)*p.weight;
      p.a=(p.a+omega*circulation*dt)%TAU;
      p.r+=omega*dt*(1.9*wake+1.1*band*Math.sin(behind*8+p.phase+simTime*.5));
      if(p.r>radius+48 || p.r<radius-48){p.r=radius+(random()-.5)*65;p.a=random()*TAU;p.trail=[];}
      p.strength=wake;
      p.trail.push(world(p.r,p.a,p.z+1.8*band*Math.sin(p.phase+simTime*.5)));
      if(p.trail.length>7)p.trail.shift();
    }
  }
  function drawAir() {
    if(!airControl.checked)return;
    ctx.lineCap='round';
    // Curved wakes start at the trailing edge, stretch behind the passing panel,
    // and fade. These are illustrative traces, not a quantitative flow solution.
    if(rpm>0){
      for(let k=0;k<3;k++)for(let level=0;level<7;level++){
        const phi=angle+k*TAU/3,z=39+level*29;
        for(let j=0;j<18;j++){
          const age=j/18,older=(j+1)/18,span=1.05;
          const rr=radius+Math.sin(age*8+level)*age*6;
          const rr2=radius+Math.sin(older*8+level)*older*6;
          const alpha=(1-age)*.28*clamp(rpm/1800,.15,1.25);
          stroke([at(rr,phi-.13-age*span,z),at(rr2,phi-.13-older*span,z)],`rgba(101,207,229,${alpha})`,2.2);
        }
      }
    }
    for(const p of particles){
      const alpha=.12+p.strength*.5;
      if(rpm>0)stroke(p.trail.map(v=>project(...v)),`rgba(101,207,229,${alpha})`,1.2);
      const q=project(...p.trail[p.trail.length-1]);
      ctx.beginPath();ctx.arc(q[0],q[1],.85+p.strength*.6,0,TAU);ctx.fillStyle=`rgba(142,228,246,${alpha+.12})`;ctx.fill();
    }
  }
  function panel(phi) {
    const radial=[Math.cos(phi),Math.sin(phi)],tangent=[-Math.sin(phi),Math.cos(phi)];
    // Blunt leading edge +tangent, tapered trailing edge −tangent.
    const profile=[[-.8,-17],[-4,-7],[-4,9],[-2.8,12],[0,13],[2.8,12],[4,9],[4,-7],[.8,-17]];
    const pt=(v,z)=>project(radial[0]*(radius+v[0])+tangent[0]*v[1],radial[1]*(radius+v[0])+tangent[1]*v[1],z);
    const faces=profile.map((p,i)=>({a:p,b:profile[(i+1)%profile.length],i}));
    faces.sort((a,b)=>(pt(a.a,20)[1]+pt(a.b,20)[1])-(pt(b.a,20)[1]+pt(b.b,20)[1]));
    for(const {a,b,i} of faces)polygon([pt(a,22),pt(b,22),pt(b,230),pt(a,230)],i>4?'#345f7a':'#487e9c','#648ca6');
    polygon(profile.map(p=>pt(p,230)),'#83b2ca','#a3c8da');
    const ledBottom=pt([4.6,0],26),ledTop=pt([4.6,0],227);
    stroke([ledBottom,ledTop],'#11384e',3.5);
    for(let i=0;i<29;i++){
      const q=pt([4.8,0],26+i*(201/28));
      const lit=rpm>0 && imageControl.checked && (i>5&&i<23);
      ctx.fillStyle=lit?COLORS.led:'#74c7e6';
      if(lit){ctx.shadowColor='#ffca71';ctx.shadowBlur=5;}
      ctx.fillRect(q[0]-1.1,q[1]-1.25,2.2,2.5);ctx.shadowBlur=0;
    }
  }
  function drawHologram() {
    if(!imageControl.checked || rpm<=0)return;
    // A persistent luminous test pattern on the swept cylinder, drawn separately
    // from tracer particles. Not a prediction of flicker perception at any rpm.
    const camera=-Math.PI/3;
    for(let col=-44;col<=44;col++){
      const s=col*2.5,phi=camera+col*Math.PI/90;
      for(let row=0;row<29;row++){
        const y=(row-14)*6.94;
        const disk=s*s+y*y<48*48;
        const a=-.25,xr=s*Math.cos(a)+y*Math.sin(a),yr=-s*Math.sin(a)+y*Math.cos(a);
        const q=(xr/83)**2+(yr/20)**2;
        const rings=q>.69&&q<1.15&&(!disk||yr>0);
        if(!rings&&(!disk||row===10||row===18))continue;
        const pos=at(radius+5,phi,126-y);
        ctx.fillStyle=rings?'rgba(255,225,160,.78)':'rgba(146,199,241,.51)';
        ctx.fillRect(pos[0]-1.05,pos[1]-1.05,2.1,2.1);
      }
    }
  }
  function drawRotor() {
    const phases=[angle,angle+TAU/3,angle+2*TAU/3];
    phases.sort((a,b)=>at(radius,a,0)[1]-at(radius,b,0)[1]);
    cylinder(132,-5,0,'#152b3d','#102132');
    ring(132,0,'#355067');
    for(const phi of phases)if(at(radius,phi,0)[1]<349)panel(phi);
    cylinder(31,0,75,'#496272','#273b4a');
    cylinder(22,75,99,'#596e78','#354d5a');
    cylinder(6,96,129,'#acc1cb','#7996a5');
    for(const phi of phases){
      stroke([at(24,phi,127),at(radius-4,phi,127)],'#53788f',8);
      stroke([at(25,phi,129),at(radius-5,phi,129)],'#9bb8c9',2);
    }
    cylinder(36,116,137,'#67889b','#2d495c');
    for(const phi of phases)if(at(radius,phi,0)[1]>=349)panel(phi);
    drawHologram();
    if(rpm>0){
      const pos=world(radius,angle,148),q=project(...pos);
      const end=project(pos[0]+36*Math.sin(angle),pos[1]-36*Math.cos(angle),pos[2]);
      arrow(q[0],q[1],end[0]-q[0],end[1]-q[1],COLORS.force,2.7);
    }
  }
  function topView() {
    const cx=621,cy=169,scale=.63,r=radius*scale;
    text('VISTA DE CIMA',cx,43,12,'#a8bfd1','center');
    ctx.setLineDash([3,5]);ctx.strokeStyle='#3a586d';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(cx,cy,r,0,TAU);ctx.stroke();ctx.setLineDash([]);
    ctx.beginPath();ctx.arc(cx,cy,22,0,TAU);ctx.fillStyle='#39566d';ctx.fill();
    for(let k=0;k<3;k++){
      const phi=angle+k*TAU/3,x=cx+r*Math.cos(phi),y=cy-r*Math.sin(phi);
      stroke([[cx+20*Math.cos(phi),cy-20*Math.sin(phi)],[x,y]],'#7599b1',3);
      if(airControl.checked&&rpm>0){
        for(let j=0;j<20;j++){
          const a=phi-.16-j*.038,b=a-.036;
          stroke([[cx+r*Math.cos(a),cy-r*Math.sin(a)],[cx+r*Math.cos(b),cy-r*Math.sin(b)]],`rgba(101,207,229,${.6*(1-j/20)})`,4);
        }
      }
      ctx.save();ctx.translate(x,y);ctx.rotate(-phi);
      ctx.fillStyle='#94cbe7';ctx.beginPath();ctx.moveTo(-2.5,11);ctx.lineTo(-2.5,-7);ctx.quadraticCurveTo(0,-12,2.5,-7);ctx.lineTo(2.5,11);ctx.closePath();ctx.fill();ctx.restore();
    }
    // One highlighted panel separates motion (+tangent) and drag (−tangent).
    const x=cx+r*Math.cos(angle),y=cy-r*Math.sin(angle),tx=-Math.sin(angle),ty=-Math.cos(angle);
    if(rpm>0){
      arrow(x,y,tx*39,ty*39,COLORS.velocity);
      const forceLength=24+18*clamp((rpm/1800)**2*(radius/100)**2,0,2);
      arrow(x,y,-tx*forceLength,-ty*forceLength,COLORS.force);
    }
    arrow(549,281,27,0,COLORS.velocity);text('movimento do painel',590,286,13,'#d9e9f2');
    arrow(576,308,-27,0,COLORS.force);text('arrasto no painel',590,313,13,COLORS.force);
    ctx.beginPath();ctx.arc(562,339,2.5,0,TAU);ctx.fillStyle=COLORS.air;ctx.fill();
    text('ar e esteira',590,344,13,COLORS.air);
    text('Giro anti-horário',cx,381,14,'#d2e4ef','center');
    text('visto de cima',cx,399,12,'#9ab6ce','center');
  }
  function draw() {
    ctx.setTransform(canvas.width/W,0,0,canvas.height/H,0,0);
    const bg=ctx.createLinearGradient(0,0,W,H);bg.addColorStop(0,'#10283e');bg.addColorStop(1,'#071421');
    ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
    text('ROTOR + AR',22,29,12,'#b0c6d8');
    text(rpm===0?'ROTOR PARADO':'MOVIMENTO DESACELERADO',22,H-17,11,'#8aa7be');
    drawAir();drawRotor();
    stroke([[516,28],[516,H-24]],'#274254');
    topView();
  }
  function values() {
    rpm=Number(rpmControl.value);radius=Number(radiusControl.value);
    byId('arrasto-rpm-value').textContent=`${fmt(rpm)} rpm`;
    byId('arrasto-raio-value').textContent=`${fmt(radius)} mm`;
    byId('arrasto-speed').textContent=`${fmt(TAU*(rpm/60)*(radius/1000),1)} m/s`;
    byId('arrasto-rate').textContent=`${fmt(3*rpm/60)} Hz`;
    byId('arrasto-power').textContent=`${fmt((rpm/1800)**3*(radius/100)**3,2)}×`;
    rpmControl.setAttribute('aria-valuetext',`${fmt(rpm)} rotações por minuto`);
    radiusControl.setAttribute('aria-valuetext',`${fmt(radius)} milímetros`);
  }
  function canRun() {return active&&!paused&&!printing&&!showChart&&!document.hidden&&rpm>0;}
  function schedule() {
    if(!canRun()){cancelAnimationFrame(raf);raf=0;lastTime=null;return;}
    if(!raf)raf=requestAnimationFrame(tick);
  }
  function tick(time) {
    raf=0;if(!canRun())return;
    if(lastTime===null)lastTime=time;
    if(time-lastDraw>=1000/30){step(clamp((time-lastTime)/1000,0,.06));draw();lastTime=time;lastDraw=time;}
    schedule();
  }
  rpmControl.addEventListener('input',()=>{values();draw();schedule();});
  radiusControl.addEventListener('input',()=>{values();resetParticles();draw();schedule();});
  airControl.addEventListener('change',draw);imageControl.addEventListener('change',draw);
  byId('arrasto-reset').addEventListener('click',()=>{rpmControl.value=1800;radiusControl.value=100;angle=.4;simTime=0;values();resetParticles();draw();schedule();});
  view.addEventListener('click',()=>{
    showChart=!showChart;scene.hidden=showChart;chart.hidden=!showChart;
    view.textContent=showChart?'Ver animação':'Ver gráfico';
    view.setAttribute('aria-pressed',String(showChart));
    schedule();if(!showChart)draw();
  });
  window.addEventListener('orbiter:motion',({detail})=>{
    active=detail.activeId==='dimensionamento';paused=detail.paused;printing=detail.printing;
    schedule();
  });
  document.addEventListener('visibilitychange',schedule);
  // Fonts may finish loading after the initial canvas paint, including on file://.
  document.fonts.ready.then(draw);
  values();resetParticles();
  for(let i=0;i<55;i++)step(1/30);
  draw();
})();
