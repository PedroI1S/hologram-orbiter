/* Navegação, entradas progressivas e movimento do diagrama já presente no HTML. */
(() => {
  'use strict';
  const raiz = document.documentElement;
  const quadros = [...document.querySelectorAll('.quadro')];
  const slides = quadros.map(q => q.querySelector('.slide'));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const movimento = document.getElementById('bt-movimento');
  const apresentar = document.getElementById('bt-apresentar');
  let atual = 0, pausado = reduced.matches, impresso = false;
  let raf = 0, tempoAnterior = null, acumulado = 0, tempoDesenho = -Infinity;
  let estadoCanvas = '';
  let controleTimer;
  const seletores = '.cab,.capa-inst,.capa-meio,.capa-pe,.capa-painel,.render,.editorial > *,.gallery-three > *,.takeaway,.chart-story > .grafico,.princ > .lead,.etapa,.eq-linha,.tests > .lead,.test-table tbody tr,.bottom-line,.planning > .lead,.schedule li,.schedule-notes,.closing-copy > *,.refs';
  slides.forEach((s, k) => {
    s.querySelectorAll(seletores).forEach((e,i) => {
      // A mesma imagem pode pertencer a mais de um seletor, mas só recebe uma entrada.
      if (e.parentElement.closest('[data-reveal]')) return;
      e.dataset.reveal = '';
      e.style.setProperty('--delay', `${Math.min(i * 85, 510)}ms`);
    });
    if (s.classList.contains('capa')) return;
    const rod = document.createElement('footer');
    rod.className = 'rod';
    rod.innerHTML = `<span>Hologram Orbiter · pré-projeto · UTFPR-PB</span><span class="leds" aria-hidden="true">${slides.map((_,i)=>`<i class="${i<k?'feito':i===k?'agora':''}"></i>`).join('')}</span><span class="pag"><b>${String(k+1).padStart(2,'0')}</b> / ${slides.length}</span>`;
    s.append(rod);
  });
  document.querySelectorAll('#g-raio > path[clip-path]').forEach(p => {
    p.classList.add('chart-line');
    p.style.setProperty('--comprimento', p.getTotalLength());
  });
  function ajusta() {
    const ap = raiz.classList.contains('apresentando');
    const s = ap ? Math.min(raiz.clientWidth/1280, innerHeight/720) : Math.min(1,(raiz.clientWidth-32)/1280);
    raiz.style.setProperty('--s', Math.max(.1,s).toFixed(4));
  }
  function status() {
    document.getElementById('slide-status').textContent = `${atual+1} / ${slides.length}`;
    document.getElementById('bt-anterior').disabled = atual===0;
    document.getElementById('bt-proximo').disabled = atual===slides.length-1;
    apresentar.textContent = raiz.classList.contains('apresentando') ? 'Sair' : 'Apresentar';
    apresentar.setAttribute('aria-label',raiz.classList.contains('apresentando') ? 'Sair do modo apresentação (F ou Esc)' : 'Entrar no modo apresentação (F)');
  }
  function foco(k) {
    atual = Math.max(0,Math.min(quadros.length-1,k));
    quadros.forEach((q,i)=>{
      q.classList.toggle('atual',i===atual);
      q.classList.toggle('em-foco',i===atual);
      q.inert = raiz.classList.contains('apresentando') && i!==atual;
    });
    status();
    agenda();
  }
  function mostra(k, scroll=true) {
    foco(k);
    history.replaceState(null,'',`#${quadros[atual].id}`);
    if (scroll && !raiz.classList.contains('apresentando')) quadros[atual].scrollIntoView({block:'center',behavior:'instant'});
  }
  function entra() {
    raiz.classList.add('apresentando');
    foco(atual); ajusta(); controles();
    slides[atual].tabIndex = -1;
    slides[atual].focus({preventScroll:true});
    if (raiz.requestFullscreen && !document.fullscreenElement) raiz.requestFullscreen().catch(()=>{});
  }
  function sai() {
    raiz.classList.remove('apresentando');
    quadros.forEach(q=>q.inert=false);
    ajusta(); status();
    quadros[atual].scrollIntoView({block:'center',behavior:'instant'});
    if (document.fullscreenElement) document.exitFullscreen().catch(()=>{});
  }
  function controles() {
    raiz.classList.add('controles');
    clearTimeout(controleTimer);
    controleTimer = setTimeout(()=>raiz.classList.remove('controles'),2400);
  }
  function sincronizaMovimento() {
    raiz.classList.toggle('sem-movimento',pausado || reduced.matches);
    movimento.setAttribute('aria-pressed',String(pausado || reduced.matches));
    movimento.textContent = reduced.matches ? 'Movimento reduzido' : pausado ? 'Retomar animações' : 'Pausar animações';
    movimento.disabled = reduced.matches;
    agenda();
  }
  function animavel() {
    return !pausado && !reduced.matches && !impresso && !document.hidden && !!quadros[atual].querySelector('svg[data-cilindro]:not([data-cilindro="imagem"])');
  }
  function agenda() {
    const detalhe = {activeId:quadros[atual].id, paused:pausado || reduced.matches || document.hidden, printing:impresso};
    const chave = JSON.stringify(detalhe);
    if (chave !== estadoCanvas) {
      estadoCanvas = chave;
      window.dispatchEvent(new CustomEvent('orbiter:motion', {detail:detalhe}));
    }
    if (!animavel()) { cancelAnimationFrame(raf); raf=0; tempoAnterior=null; return; }
    if (!raf) raf=requestAnimationFrame(anima);
  }
  function anima(tempo) {
    raf=0;
    if (!animavel()) return;
    if (tempoAnterior!==null) acumulado+=Math.min(tempo-tempoAnterior,100);
    tempoAnterior=tempo;
    // 15 fps são suficientes para a demonstração lenta. Nada é redesenhado fora do slide ativo.
    if (tempo-tempoDesenho>=1000/15) {
      const fase=(acumulado/50)%360;
      const {cilindro,CIL}=window.orbiterDiagram;
      quadros[atual].querySelectorAll('svg[data-cilindro]:not([data-cilindro="imagem"])').forEach(svg=>{
        const cfg=CIL[svg.dataset.cilindro];
        svg.replaceChildren();
        cilindro(svg,{...cfg,fases:cfg.fases.map(f=>f+fase)});
      });
      tempoDesenho=tempo;
    }
    agenda();
  }
  const observer=new IntersectionObserver(entries=>{
    if (raiz.classList.contains('apresentando')) return;
    const visible=entries.filter(e=>e.isIntersecting && e.intersectionRatio>=.55).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
    if (visible.length) foco(quadros.indexOf(visible[0].target));
  },{threshold:[.55,.75]});
  quadros.forEach(q=>observer.observe(q));
  const interactive = target => target.closest('button,a,input,select,textarea,[contenteditable],.alvo,[data-no-nav]');
  document.addEventListener('keydown',ev=>{
    if (ev.altKey||ev.ctrlKey||ev.metaKey) return;
    const entrada = ev.target.closest('input,select,textarea,[contenteditable]');
    const atalhoNaSimulacao = entrada?.matches('input[type="range"],input[type="checkbox"]') && ['f','m','escape'].includes(ev.key.toLowerCase());
    if (entrada && !atalhoNaSimulacao) return;
    const k=ev.key, ap=raiz.classList.contains('apresentando');
    // Enter e espaço preservam a ativação nativa dos controles focados.
    if (['Enter',' '].includes(k) && ev.target.closest('button,a')) return;
    if (k.toLowerCase()==='f') ap?sai():entra();
    else if (k.toLowerCase()==='m' && !reduced.matches) { pausado=!pausado; sincronizaMovimento(); }
    else if (k==='Escape' && ap) sai();
    else if (['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(k) && ap) mostra(atual+1);
    else if (['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(k) && ap) mostra(atual-1);
    else if (k==='Home' && ap) mostra(0);
    else if (k==='End' && ap) mostra(quadros.length-1);
    else return;
    ev.preventDefault();
  });
  let touchStart=null, ignorarCliqueAte=0;
  document.addEventListener('pointerdown',ev=>{if(ev.pointerType==='touch'&&!interactive(ev.target))touchStart={x:ev.clientX,y:ev.clientY};});
  document.addEventListener('pointercancel',()=>{touchStart=null;});
  document.addEventListener('pointerup',ev=>{
    if(!touchStart)return;
    const dx=ev.clientX-touchStart.x,dy=ev.clientY-touchStart.y;
    touchStart=null;
    if(raiz.classList.contains('apresentando')&&Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)) {
      mostra(atual+(dx<0?1:-1)); ignorarCliqueAte=performance.now()+500;
    }
  });
  document.addEventListener('click',ev=>{
    if(!raiz.classList.contains('apresentando')||interactive(ev.target)||ev.target.closest('.hud')||performance.now()<ignorarCliqueAte)return;
    mostra(atual+(ev.clientX<innerWidth/3?-1:1));
  });
  document.addEventListener('pointermove',ev=>{if(ev.clientY>innerHeight-100)controles();});
  document.getElementById('bt-anterior').addEventListener('click',()=>mostra(atual-1));
  document.getElementById('bt-proximo').addEventListener('click',()=>mostra(atual+1));
  apresentar.addEventListener('click',()=>raiz.classList.contains('apresentando')?sai():entra());
  movimento.addEventListener('click',()=>{pausado=!pausado;sincronizaMovimento();});
  document.addEventListener('fullscreenchange',()=>{
    if(!document.fullscreenElement&&raiz.classList.contains('apresentando'))sai();
    else ajusta();
  });
  document.addEventListener('visibilitychange',agenda);
  reduced.addEventListener('change',()=>{pausado=reduced.matches;sincronizaMovimento();});
  window.addEventListener('resize',ajusta);
  window.addEventListener('beforeprint',()=>{impresso=true;agenda();});
  window.addEventListener('afterprint',()=>{impresso=false;agenda();});
  function peloHash() { const k=quadros.findIndex(q=>`#${q.id}`===location.hash);if(k>=0)mostra(k); }
  window.addEventListener('hashchange',peloHash);
  ajusta(); foco(0); sincronizaMovimento(); peloHash();
})();
