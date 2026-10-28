// Slide engine: renders window.SLIDES, keyboard / click / swipe navigation, build steps, slide menu, icons.
const ICONS = {
  menu: 'M4 7h16M4 12h16M4 17h16', arrow: 'M2 12c10-1 30-1 46 0M40 5l8 7-8 7',
  hospital: 'M3 21h18M5 21V7l7-4 7 4v14M9 21v-5h6v5M12 8v4M10 10h4',
  file: 'M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h5',
  bank: 'M3 21h18M4 10h16M6 10v8M10 10v8M14 10v8M18 10v8M12 3l9 5H3z', mail: 'M3 5h18v14H3zM3 6l9 7 9-7',
  user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0', search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM21 21l-4.3-4.3',
  link: 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1',
  scale: 'M12 3v18M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0zM8 21h8', pen: 'M4 20h4L19 9l-4-4L4 16zM14 6l4 4',
  spark: 'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z', clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2',
  engine: 'M7 7h10v10H7zM10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4', cloud: 'M7 18a4 4 0 0 1-.5-8A6 6 0 0 1 18 9a4.5 4.5 0 0 1-.5 9z',
  laptop: 'M4 5h16v11H4zM2 19h20', rupee: 'M6 4h12M6 9h12M6 4h3a5 5 0 0 1 0 10H6l9 7', check: 'M5 12l5 5L20 7',
  alert: 'M12 3l10 18H2zM12 10v5M12 18h.01', layers: 'M12 3l9 5-9 5-9-5zM3 13l9 5 9-5', glasses: 'M2 13a4 4 0 1 0 8 0 4 4 0 0 0-8 0zM14 13a4 4 0 1 0 8 0 4 4 0 0 0-8 0zM10 13h4M2 13l2-6M22 13l-2-6',
  doc: 'M8 3h8l4 4v14H4V3zM8 11h8M8 15h6', table: 'M3 5h18v14H3zM3 10h18M3 15h18M9 5v14', x: 'M6 6l12 12M18 6L6 18',
  db: 'M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3', heart: 'M12 21s-8-5-8-11a5 5 0 0 1 8-4 5 5 0 0 1 8 4c0 6-8 11-8 11z',
};
const svg = (name, box = name === 'arrow' ? '0 0 52 24' : '0 0 24 24') => `<svg class="i" viewBox="${box}" aria-hidden="true"><path d="${ICONS[name] || ''}"/></svg>`;

const slides = window.SLIDES;
const $ = (id) => document.getElementById(id);
const pad = (n) => String(n).padStart(2, '0');

$('stage').innerHTML = slides.map((s, i) => `<section class="slide${s.cover ? ' cover' : ''}" id="s${i + 1}" aria-label="Slide ${i + 1}">
  ${s.cover ? '' : `<p class="eyebrow"><b>// ${pad(s.sec)}</b>${s.name}</p><h1>${s.title}</h1>`}
  <div class="body">${s.body}</div></section>`).join('');
document.querySelectorAll('[data-i]').forEach((el) => { el.innerHTML = svg(el.dataset.i); });
const els = [...document.querySelectorAll('.slide')];

let cur = 0, step = 0;
const steps = (i) => [...els[i].querySelectorAll('.step')];

function show(i, atEnd = false) {
  cur = Math.max(0, Math.min(slides.length - 1, i));
  const st = steps(cur);
  step = atEnd ? st.length : 0;
  st.forEach((el, k) => el.classList.toggle('hide', k >= step));
  els.forEach((el, k) => { el.classList.toggle('on', k === cur); el.inert = k !== cur; });
  $('progress').style.width = `${((cur + 1) / slides.length) * 100}%`;
  $('count').textContent = `${cur + 1} / ${slides.length}`;
  $('rail-num').textContent = pad(cur + 1);
  $('rail-sec').textContent = slides[cur].name;
  $('back').disabled = cur === 0 && step === 0;
  $('next').disabled = cur === slides.length - 1 && step === st.length;
  document.querySelectorAll('#menu a').forEach((a, k) => a.classList.toggle('here', k === cur));
  history.replaceState(null, '', `#${cur + 1}`);
  els[cur].scrollTop = 0;
}
function next() {
  const st = steps(cur);
  if (step < st.length) { st[step++].classList.remove('hide'); return refreshButtons(); }
  if (cur < slides.length - 1) show(cur + 1);
}
function prev() {
  const st = steps(cur);
  if (step > 0) { st[--step].classList.add('hide'); return refreshButtons(); }
  if (cur > 0) show(cur - 1, true);
}
function refreshButtons() {
  $('back').disabled = cur === 0 && step === 0;
  $('next').disabled = cur === slides.length - 1 && step === steps(cur).length;
}

// Slide menu, grouped by section
let last = '';
$('menu-list').innerHTML = slides.map((s, i) => {
  const head = s.name !== last ? `<h4>${s.cover ? 'Start' : `${pad(s.sec)} · ${s.name}`}</h4>` : '';
  last = s.name;
  return `${head}<a href="#${i + 1}" data-go="${i}"><span>${pad(i + 1)}</span>${s.menu || s.title.replace(/<[^>]+>/g, '')}</a>`;
}).join('');
const toggleMenu = (open) => $('menu').classList.toggle('open', open ?? !$('menu').classList.contains('open'));
$('menu').addEventListener('click', (e) => {
  const a = e.target.closest('[data-go]');
  if (a) { e.preventDefault(); show(Number(a.dataset.go)); }
  if (a || e.target === $('menu')) toggleMenu(false);
});
$('menu-btn').innerHTML = svg('menu');
$('menu-btn').onclick = () => toggleMenu();
$('next').onclick = next;
$('back').onclick = prev;

document.addEventListener('keydown', (e) => {
  if (e.target.matches('input, textarea, select')) return;
  if (e.key === ' ' && e.target.closest('button, summary, a')) return;
  if (['ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); next(); }
  else if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); prev(); }
  else if (e.key === 'Home') show(0);
  else if (e.key === 'End') show(slides.length - 1, true);
  else if (e.key === 'm') toggleMenu();
  else if (e.key === 'Escape') toggleMenu(false);
  else if (e.key === 'f') (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.());
});
let x0 = null;
document.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
document.addEventListener('touchend', (e) => {
  const dx = x0 === null ? 0 : e.changedTouches[0].clientX - x0;
  if (Math.abs(dx) > 60) (dx < 0 ? next : prev)();
  x0 = null;
});

show((parseInt(location.hash.slice(1), 10) || 1) - 1);
