// Part 1: cover, what an FDE does, the problem. Also the small diagram helpers every slide uses.
window.SLIDES = window.SLIDES || [];
// box(): an icon with a short label · arr(): an arrow with a short label · flow(): a row of them · say(): one takeaway
window.box = (icon, label, cls = '', sub = '') => `<div class="box ${cls}"><span class="ico" data-i="${icon}"></span>
  <b>${label}</b>${sub ? `<small>${sub}</small>` : ''}</div>`;
window.arr = (label = '', cls = '') => `<div class="arr ${cls}"><small>${label}</small><i data-i="arrow"></i></div>`;
window.flow = (...items) => `<div class="flow">${items.join('')}</div>`;
window.col = (...items) => `<div class="col">${items.join('')}</div>`;
window.say = (text, cls = '') => `<p class="say ${cls}">${text}</p>`;
window.tag = (t) => `<em class="${t === 'AI' ? 'ai' : ''}">${t}</em>`;
// tbl(): a schema table. rows = [[field, type, example?], ...]
window.tbl = (name, rows, cls = '', note = '') => `<div class="tbl ${cls}"><h4>${name}${note ? `<span>${note}</span>` : ''}</h4>
  <table>${rows.map(([f, t, v]) => `<tr><td>${f}</td><td class="t">${t || ''}</td>${v === undefined ? '' : `<td class="v">${v}</td>`}</tr>`).join('')}</table></div>`;

SLIDES.push({
  cover: true, name: 'Welcome', menu: 'Reconciling claims without retyping',
  body: `
  <div class="stack" style="gap:20px;justify-items:start">
    <span class="label accent">FDE training · Project 1</span>
    <h1>Insurance settlements, <mark>without the retyping</mark></h1>
    <p class="lead">Today every insurer e-mail is read and typed into the hospital system by hand. Slow, error-prone, and most claims never get checked.</p>
  </div>
  ${flow(box('mail', 'Insurer e-mails', 'legacy'), arr(), box('spark', 'Read automatically', 'ours'), arr(),
    box('check', 'Claims reconciled', 'good'))}`,
});

SLIDES.push({
  sec: 1, name: 'The role', title: 'What does an <mark>FDE</mark> do?', menu: 'What is an FDE?',
  body: `
  ${flow(box('user', 'Listen', '', 'talk to the client'), arr(), box('search', 'Find the real problem', '', 'open the real files'),
    arr(), box('pen', 'Build small', '', 'next to their system'), arr(), box('check', 'Prove it works', 'ours', 'with real numbers'))}
  ${say('Work inside the client’s world. Never replace their systems.')}`,
});

SLIDES.push({
  sec: 1, name: 'The problem', title: 'Every settlement is <mark>retyped by hand</mark>', menu: 'The problem',
  body: `
  ${flow(box('mail', 'Open e-mail', 'legacy step', 'whose claim is it?'), arr('', 'step'),
    box('file', 'Read it', 'legacy step', '6 different formats'), arr('', 'step'),
    box('search', 'Find patient', 'bad step', 'misspelt name → wrong match'), arr('', 'step'),
    box('pen', 'Type it in', 'bad step', 'typos in amounts'), arr('', 'step'),
    box('scale', 'Fair or unfair?', 'bad step', 'decided from memory'))}
  <div class="bigs step">
    <div class="bign"><b>3 days</b><span>of typing every month</span></div>
    <div class="bign"><b>40 / 300</b><span>claims ever checked</span></div>
    <div class="bign accent"><b>Errors</b><span>nobody catches</span></div>
  </div>`,
});
