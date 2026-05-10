// Reveal-on-scroll
(function () {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  // Nav solid on scroll
  const nav = document.querySelector('.nav');
  if (nav) {
    const update = () => {
      if (window.scrollY > 40) nav.classList.add('solid');
      else nav.classList.remove('solid');
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  // Mobile nav
  const toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      document.body.classList.toggle('nav-mobile-open');
    });
  }

  // Counter animation
  const counters = document.querySelectorAll('[data-count]');
  const cIo = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const target = parseFloat(el.dataset.count);
      const decimals = parseInt(el.dataset.decimals || '0', 10);
      const dur = 1600;
      const t0 = performance.now();
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * eased).toFixed(decimals);
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = target.toFixed(decimals);
      };
      requestAnimationFrame(tick);
      cIo.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach((el) => cIo.observe(el));

  // Hero parallax
  const hero = document.querySelector('[data-parallax]');
  if (hero) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY * 0.3;
      hero.style.transform = `translate3d(0, ${y}px, 0)`;
    }, { passive: true });
  }
})();
