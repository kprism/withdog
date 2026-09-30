(() => {
  const slides=[...document.querySelectorAll('.hero-slide')],slideNo=document.querySelector('#slideNo'),pauseBtn=document.querySelector('#pauseBtn');let current=0,playing=true,timer;
  function show(index){current=(index+slides.length)%slides.length;slides.forEach((s,i)=>s.classList.toggle('active',i===current));if(slideNo)slideNo.textContent=current+1;}
  function start(){clearInterval(timer);timer=setInterval(()=>show(current+1),5000);}
  document.querySelectorAll('[data-dir]').forEach(btn=>btn.addEventListener('click',()=>{show(current+Number(btn.dataset.dir));if(playing)start();}));
  pauseBtn?.addEventListener('click',()=>{playing=!playing;pauseBtn.textContent=playing?'Ⅱ':'▶';playing?start():clearInterval(timer);});
  document.querySelector('#botButton')?.addEventListener('click',()=>alert('상담 봇은 별도 모듈로 연결할 예정입니다.'));
  document.querySelector('.mobile-menu')?.addEventListener('click',()=>document.querySelector('.quick-nav')?.scrollIntoView({behavior:'smooth'}));
  const actions=[...document.querySelectorAll('.header-actions button')];
  actions[0]?.addEventListener('click',()=>location.href='auth-preview.html?tab=login');
  actions[1]?.addEventListener('click',()=>location.href='auth-preview.html?tab=member');
  document.querySelector('.quick-nav a[href="#partners"]')?.addEventListener('click',e=>{e.preventDefault();location.href='auth-preview.html?tab=partner';});
  show(0);start();
})();