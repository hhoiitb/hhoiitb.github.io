// H2O Engineering Lab — interactions
(function () {
  var doc = document.documentElement;
  var header = document.querySelector('.site-header');

  // header turns solid on scroll
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 40 || header.hasAttribute('data-solid'));
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // mobile menu
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      doc.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) toggle.click();
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.parentElement.classList.toggle('sub-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // reveal on scroll
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // animated logo: drawn when it scrolls into view, click to replay
  document.querySelectorAll('[data-logo-anim]').forEach(function (box) {
    var tpl = box.querySelector('template');
    if (!tpl || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var play = function () {
      var old = box.querySelector('svg');
      if (old) old.remove();
      box.appendChild(tpl.content.cloneNode(true));
      box.classList.add('playing');
    };
    if ('IntersectionObserver' in window) {
      var lo = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { play(); lo.disconnect(); }
      }, { threshold: 0.4 });
      lo.observe(box);
    } else { play(); }
    box.style.cursor = 'pointer';
    box.addEventListener('click', play);
  });

  // research filter chips
  document.querySelectorAll('[data-filters]').forEach(function (bar) {
    var cards = document.querySelectorAll('.rcard[data-theme]');
    bar.querySelectorAll('[data-filter]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        var f = chip.getAttribute('data-filter');
        bar.querySelectorAll('.chip').forEach(function (c) { c.classList.toggle('on', c === chip); });
        cards.forEach(function (c) {
          c.classList.toggle('hide', f !== 'all' && c.getAttribute('data-theme') !== f);
          c.classList.add('in');
        });
      });
    });
  });

  // horizontal photo track
  document.querySelectorAll('[data-track]').forEach(function (wrap) {
    var track = wrap.querySelector('.track');
    wrap.querySelectorAll('[data-dir]').forEach(function (b) {
      b.addEventListener('click', function () {
        track.scrollBy({ left: track.clientWidth * 0.8 * Number(b.getAttribute('data-dir')), behavior: 'smooth' });
      });
    });
  });

  // lightbox
  var groups = {};
  document.querySelectorAll('[data-lb]').forEach(function (btn) {
    var g = btn.getAttribute('data-lb');
    (groups[g] = groups[g] || []).push(btn);
  });
  if (Object.keys(groups).length) {
    var icon = function (d) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="' + d + '"/></svg>'; };
    var lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Image viewer');
    lb.innerHTML = '<img alt=""><button class="lb-close" aria-label="Close">' + icon('M6 6l12 12M18 6L6 18') +
      '</button><button class="lb-prev" aria-label="Previous image">' + icon('M15 6l-6 6 6 6') +
      '</button><button class="lb-next" aria-label="Next image">' + icon('M9 6l6 6-6 6') + '</button><div class="lb-count"></div>';
    document.body.appendChild(lb);
    var img = lb.querySelector('img'), count = lb.querySelector('.lb-count');
    var cur = [], idx = 0, last = null;
    var show = function () {
      var b = cur[idx], src = b.getAttribute('data-full') || b.querySelector('img').src;
      img.src = src; img.alt = b.querySelector('img').alt;
      count.textContent = cur.length > 1 ? (idx + 1) + ' / ' + cur.length : '';
      lb.querySelector('.lb-prev').style.display = lb.querySelector('.lb-next').style.display = cur.length > 1 ? '' : 'none';
    };
    var close = function () { lb.classList.remove('open'); doc.style.overflow = ''; if (last) last.focus(); };
    Object.keys(groups).forEach(function (g) {
      groups[g].forEach(function (b, i) {
        b.addEventListener('click', function () {
          cur = groups[g]; idx = i; last = b; show();
          lb.classList.add('open'); doc.style.overflow = 'hidden';
          lb.querySelector('.lb-close').focus();
        });
      });
    });
    var step = function (d) { idx = (idx + d + cur.length) % cur.length; show(); };
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { step(-1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { step(1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
  }

  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
