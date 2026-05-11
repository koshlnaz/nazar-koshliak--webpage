// ============= CINEMATIC SCROLL =============
document.body.classList.add('loading');

window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('loader').classList.add('gone');
    document.body.classList.remove('loading');
    initCinematic();
  }, 1700);
});

function initCinematic() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    document.querySelectorAll('[data-reveal]').forEach((el) => { el.style.opacity = 1; el.style.transform = 'none'; });
    return;
  }
  gsap.registerPlugin(ScrollTrigger);

  // Progress bar + Burj Khalifa progress indicator
  const burj = document.getElementById('burj-progress');
  const burjFill = document.querySelector('.burj-fill');
  const burjPct = document.querySelector('.burj-pct');
  let burjIdleTimer = null;
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: (self) => {
      const p = self.progress;
      document.getElementById('progress').style.width = (p * 100) + '%';
      if (burjFill) {
        // Fill grows from bottom (y=200) up to y=0 as p goes 0 → 1
        burjFill.setAttribute('y', String(200 - p * 200));
      }
      if (burjPct) burjPct.textContent = Math.round(p * 100);
      if (burj) {
        burj.classList.add('scrolling');
        clearTimeout(burjIdleTimer);
        burjIdleTimer = setTimeout(() => burj.classList.remove('scrolling'), 600);
      }
    }
  });

  // Solid nav after first scene
  ScrollTrigger.create({
    trigger: '#scene-hero', start: 'top 80%',
    onEnter: () => document.querySelector('.nav').classList.add('solid'),
    onLeaveBack: () => document.querySelector('.nav').classList.remove('solid'),
  });

  // Generic reveal-up
  document.querySelectorAll('[data-reveal]').forEach((el) => {
    gsap.to(el, {
      opacity: 1, y: 0, duration: 1.1, ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
  });

  // SCENE 2 — Hero pin: side stats stagger as user enters
  gsap.from('.hero-side-row', {
    x: 60, opacity: 0, stagger: 0.12, duration: 1, ease: 'power3.out',
    scrollTrigger: { trigger: '#scene-hero', start: 'top 60%' },
  });

  // SCENE 3 — Title card: lines fade with parallax
  gsap.utils.toArray('.title-line').forEach((line, i) => {
    gsap.fromTo(line, { y: 60 }, {
      y: -60, ease: 'none',
      scrollTrigger: { trigger: '#scene-title', start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });

  // SCENE 4 — Skyline parallax
  const skyBack = document.querySelector('.sky-back');
  const skyFront = document.querySelector('.sky-front');
  if (skyBack && skyFront) {
    gsap.to(skyBack, {
      x: '-30%', ease: 'none',
      scrollTrigger: { trigger: '#scene-skyline', start: 'top top', end: 'bottom top', scrub: true },
    });
    gsap.to(skyFront, {
      x: '-50%', ease: 'none',
      scrollTrigger: { trigger: '#scene-skyline', start: 'top top', end: 'bottom top', scrub: true },
    });
    gsap.fromTo('.sky-headline',
      { scale: 0.7, opacity: 0 },
      {
        scale: 1, opacity: 1, ease: 'none',
        scrollTrigger: { trigger: '#scene-skyline', start: 'top top', end: '40% top', scrub: true },
      });
    gsap.to('.sky-headline', {
      opacity: 0, ease: 'none',
      scrollTrigger: { trigger: '#scene-skyline', start: '60% top', end: 'bottom top', scrub: true },
    });
  }

  // SCENE 5 — Journey progress bar
  const jpFill = document.querySelector('.jp-fill');
  if (jpFill) {
    gsap.to(jpFill, {
      width: '100%', ease: 'none',
      scrollTrigger: { trigger: '.journey-track', start: 'top 70%', end: 'bottom 50%', scrub: true },
    });
  }
  gsap.from('.chapter', {
    y: 80, opacity: 0, stagger: 0.15, duration: 1, ease: 'power3.out',
    scrollTrigger: { trigger: '.journey-track', start: 'top 75%' },
  });

  // SCENE 6 — Orbit spin tied to scroll
  const orbitSpin = document.querySelector('[data-orbit-spin]');
  if (orbitSpin) {
    gsap.to(orbitSpin, {
      rotation: 360, ease: 'none',
      scrollTrigger: { trigger: '#scene-orbit', start: 'top top', end: 'bottom top', scrub: 1 },
    });
    // counter-rotate labels so they stay upright
    gsap.utils.toArray('.orbit-counter').forEach((el) => {
      gsap.to(el, {
        rotation: -360, ease: 'none',
        scrollTrigger: { trigger: '#scene-orbit', start: 'top top', end: 'bottom top', scrub: 1 },
      });
    });
  }

  // SCENE 7 — Process: horizontal scroll
  const processTrack = document.querySelector('[data-process-track]');
  const processStage = document.querySelector('.process-stage');
  if (processTrack && processStage) {
    const scrollDistance = () => Math.max(0, processTrack.scrollWidth - window.innerWidth + 80);
    gsap.set(processTrack, { x: 0 });
    gsap.to(processTrack, {
      x: () => -scrollDistance(),
      ease: 'none',
      scrollTrigger: {
        trigger: '#scene-process',
        pin: true,
        start: 'top top',
        end: () => '+=' + scrollDistance(),
        invalidateOnRefresh: true,
        scrub: 1,
      },
    });
    // step counter
    const ppFill = document.querySelector('.pp-fill');
    const ppNum = document.querySelector('[data-pp-num]');
    ScrollTrigger.create({
      trigger: '#scene-process', start: 'top top',
      end: () => '+=' + scrollDistance(),
      onUpdate: (self) => {
        const p = self.progress;
        if (ppFill) ppFill.style.width = (p * 100) + '%';
        if (ppNum) ppNum.textContent = String(Math.min(6, Math.max(1, Math.ceil(p * 6) || 1))).padStart(2, '0');
      },
    });
  }

  // SCENE 8 — Counters
  document.querySelectorAll('[data-counter]').forEach((el) => {
    const target = parseFloat(el.dataset.counter);
    const suffix = el.dataset.suffix || '';
    const decimals = (target % 1 !== 0) ? 1 : 0;
    const obj = { v: 0 };
    ScrollTrigger.create({
      trigger: el, start: 'top 80%', once: true,
      onEnter: () => {
        gsap.to(obj, {
          v: target, duration: 1.8, ease: 'power3.out',
          onUpdate: () => { el.innerHTML = obj.v.toFixed(decimals) + (suffix ? '<sup>' + suffix + '</sup>' : ''); },
        });
      },
    });
  });

  // SCENE 9 — Devs light up sequentially
  gsap.utils.toArray('.dev-line').forEach((line, i) => {
    gsap.from(line, {
      opacity: 0, y: 40, duration: 0.6, ease: 'power3.out',
      scrollTrigger: { trigger: line, start: 'top 90%', once: true },
    });
  });
  ScrollTrigger.create({
    trigger: '#scene-devs', start: 'top 60%', once: true,
    onEnter: () => {
      const lines = document.querySelectorAll('.dev-line');
      lines.forEach((line, i) => {
        setTimeout(() => {
          line.classList.add('lit');
          setTimeout(() => line.classList.remove('lit'), 300);
        }, i * 180);
      });
    },
  });

  // SCENE 10 — Close: parallax image
  const closeImg = document.querySelector('.close-image img');
  if (closeImg) {
    gsap.fromTo(closeImg, { scale: 1.15, y: '5%' }, {
      scale: 1, y: '-5%', ease: 'none',
      scrollTrigger: { trigger: '#scene-close', start: 'top bottom', end: 'bottom top', scrub: true },
    });
  }

  ScrollTrigger.refresh();
}

// ============= LANGUAGE SWITCHER =============
const I18N = {
  en: { home: 'Home', about: 'About', services: 'Services', experience: 'Experience', contact: 'Contact', cta: 'Book a consultation' },
  ru: { home: 'Главная', about: 'Обо мне', services: 'Услуги', experience: 'Опыт', contact: 'Контакты', cta: 'Записаться на встречу' },
  ua: { home: 'Головна', about: 'Про мене', services: 'Послуги', experience: 'Досвід', contact: 'Контакти', cta: 'Записатись на зустріч' },
  cz: { home: 'Domů', about: 'O mně', services: 'Služby', experience: 'Zkušenosti', contact: 'Kontakt', cta: 'Domluvit konzultaci' },
  de: { home: 'Start', about: 'Über mich', services: 'Leistungen', experience: 'Erfahrung', contact: 'Kontakt', cta: 'Beratung buchen' },
};

function buildLangSwitcher() {
  const nav = document.querySelector('.nav-cinematic') || document.querySelector('.nav');
  if (!nav) return;
  const cta = nav.querySelector('.nav-cta');
  const wrap = document.createElement('div');
  wrap.className = 'nav-lang';
  ['en', 'ru', 'ua', 'cz', 'de'].forEach((code) => {
    const btn = document.createElement('button');
    btn.textContent = code.toUpperCase();
    btn.dataset.lang = code;
    btn.onclick = () => setLang(code);
    wrap.appendChild(btn);
  });
  if (cta) nav.insertBefore(wrap, cta);
  else nav.appendChild(wrap);
  setLang(localStorage.getItem('nk-lang') || 'en');
}

function setLang(code) {
  const dict = I18N[code] || I18N.en;
  document.querySelectorAll('.nav-lang button').forEach((b) => {
    b.classList.toggle('active', b.dataset.lang === code);
  });
  document.querySelectorAll('.nav-links a').forEach((a) => {
    const key = a.getAttribute('href').replace('.html', '').replace('index', 'home');
    if (dict[key]) a.textContent = dict[key];
  });
  const cta = document.querySelector('.nav-cta');
  if (cta) cta.textContent = dict.cta;
  localStorage.setItem('nk-lang', code);
  document.documentElement.lang = code === 'ua' ? 'uk' : code === 'cz' ? 'cs' : code;
}

// language switcher disabled — site is English-only
// document.addEventListener('DOMContentLoaded', buildLangSwitcher);
