/* Um mesmo ciclo alimenta as três vistas: emissão instantânea, rastro e imagem.
 * A varredura real de 120° leva 11,11 ms a 1800 rpm; aqui dura 5,4 s.
 * A imagem acumulada é uma explicação do princípio, não um modelo da retina.
 * A cena sólida usa o mesmo desenho e projeção da animação de arrasto (slide 4).
 */
(() => {
  'use strict';
  const ids=['pov-instante','pov-varredura','pov-imagem'];
  const canvases=ids.map(id=>document.getElementById(id));
  if(canvases.some(c=>!c))return;
  const ctxs=canvases.map(c=>c.getContext('2d'));
  const slider=document.getElementById('pov-progress');
  const value=document.getElementById('pov-progress-value');
  const play=document.getElementById('pov-play');
  const reset=document.getElementById('pov-reset');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const W=368,H=298;
  const pixel=(a,row)=>window.orbiterDiagram.pixel(((a+180)%360+360)%360-180,row);
  let progress=reduced.matches?120:0,elapsed=reduced.matches?5.4:0;
  let active=false,globalPaused=reduced.matches,printing=false,playing=true;
  let raf=0,lastTime=null,lastDraw=0;
  function label(g,text,x,y,color='#9bb7cc',size=12,align='left'){
    g.font=`500 ${size}px "HO Fira Sans",sans-serif`;
    g.fillStyle=color;g.textAlign=align;g.fillText(text,x,y);
  }
  function paint(p=progress){
    ctxs.forEach((g,index)=>{
      g.setTransform(canvases[index].width/W,0,0,canvases[index].height/H,0,0);
      window.OrbiterRenderer.draw(g,{width:W,height:H,phaseDegrees:p,stage:index,pixel});
      label(g,['01 / LEDS EM MOVIMENTO','02 / RASTRO LUMINOSO','03 / IMAGEM FORMADA'][index],17,23,'#b0c6d8',11);
      if(index===0){
        label(g,'3 painéis / 29 LEDs por painel',W/2,H-13,'#bad4e5',12,'center');
      }else if(index===1){
        label(g,`${2*Math.floor((p+.001)/2)}° percorridos por painel`,W/2,H-13,'#bad4e5',12,'center');
      }else{
        const count=3*Math.floor((p+.001)/2);
        label(g,p>=120?'180 colunas / ciclo completo':`${count} de 180 colunas escritas`,W/2,H-13,p>=120?'#ffe0a0':'#bad4e5',12,'center');
      }
    });
  }
  function controls(p=progress){
    const angle=2*Math.floor((p+.001)/2);
    slider.value=String(angle);
    const ms=(angle/10.8).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1});
    value.textContent=`${angle}° / ${ms} ms`;
    slider.setAttribute('aria-valuetext',`${angle} graus por painel, ${ms} milissegundos reais`);
    play.textContent=reduced.matches?'Movimento reduzido':globalPaused?'Animações pausadas':playing?'Pausar sequência':'Continuar sequência';
    play.disabled=globalPaused||reduced.matches;
    play.setAttribute('aria-pressed',String(!playing||globalPaused||reduced.matches));
  }
  function canRun(){return active&&playing&&!globalPaused&&!printing&&!document.hidden;}
  function schedule(){
    if(!canRun()){cancelAnimationFrame(raf);raf=0;lastTime=null;return;}
    if(!raf)raf=requestAnimationFrame(tick);
  }
  function tick(time){
    raf=0;if(!canRun())return;
    if(lastTime===null)lastTime=time;
    if(time-lastDraw>=1000/30){
      elapsed=(elapsed+Math.min((time-lastTime)/1000,.08))%7;
      progress=Math.min(120,elapsed/5.4*120);
      controls();paint();lastTime=time;lastDraw=time;
    }
    schedule();
  }
  slider.addEventListener('input',()=>{progress=Number(slider.value);elapsed=progress/120*5.4;playing=false;controls();paint();schedule();});
  play.addEventListener('click',()=>{playing=!playing;if(playing&&progress>=120){progress=0;elapsed=0;}controls();schedule();});
  reset.addEventListener('click',()=>{progress=0;elapsed=0;controls();paint();schedule();});
  window.addEventListener('orbiter:motion',({detail})=>{
    const wasPrinting=printing;
    active=detail.activeId==='principio';globalPaused=detail.paused;printing=detail.printing;
    controls(printing?120:progress);schedule();
    if(printing)paint(120);else if(wasPrinting)paint();
  });
  document.addEventListener('visibilitychange',schedule);
  document.fonts.ready.then(()=>paint(printing?120:progress));
  controls();paint();
})();
