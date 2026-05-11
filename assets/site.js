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

  // Burj Khalifa scroll progress indicator
  const burj = document.getElementById('burj-progress');
  if (burj) {
    const burjFill = burj.querySelector('.burj-fill');
    const burjPct = burj.querySelector('.burj-pct');
    let burjIdleTimer = null;
    // Show after small scroll (no big hero section on inner pages)
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const p = max > 0 ? window.scrollY / max : 0;
      if (window.scrollY > 100) burj.classList.add('show');
      else burj.classList.remove('show');
      if (burjFill) burjFill.setAttribute('y', String(200 - p * 200));
      if (burjPct) burjPct.textContent = Math.round(p * 100);
      if (burj.classList.contains('show')) {
        burj.classList.add('scrolling');
        clearTimeout(burjIdleTimer);
        burjIdleTimer = setTimeout(() => burj.classList.remove('scrolling'), 600);
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
