(() => {
  const slides = [...document.querySelectorAll('.hero-slide')];
  const slideNo = document.querySelector('#slideNo');
  const pauseBtn = document.querySelector('#pauseBtn');
  let current = 0;
  let playing = true;
  let timer;

  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle('active', i === current));
    slideNo.textContent = current + 1;
  }

  function start() {
    clearInterval(timer);
    timer = setInterval(() => show(current + 1), 5000);
  }

  document.querySelectorAll('[data-dir]').forEach(btn => {
    btn.addEventListener('click', () => {
      show(current + Number(btn.dataset.dir));
      if (playing) start();
    });
  });

  pauseBtn.addEventListener('click', () => {
    playing = !playing;
    pauseBtn.textContent = playing ? 'Ⅱ' : '▶';
    playing ? start() : clearInterval(timer);
  });

  document.querySelector('#botButton').addEventListener('click', () => {
    alert('상담 봇은 별도 모듈로 연결할 예정입니다.');
  });

  document.querySelector('.mobile-menu').addEventListener('click', () => {
    document.querySelector('.quick-nav').scrollIntoView({behavior:'smooth'});
  });

  show(0);
  start();
})();