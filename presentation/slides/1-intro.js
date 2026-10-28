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
  sec: 1, name: 'The domain', title: 'How a hospital gets <mark>paid by insurance</mark>', menu: 'How insurance claims work',
  body: `
  ${flow(box('user', 'Patient admitted', '', 'has a health policy'), arr(),
    box('table', 'Itemised bill', '', 'room, tests, medicines…'), arr('claim'),
    box('bank', 'Insurer / TPA', '', 'checks the bill against the policy'), arr('settlement'),
    box('mail', 'E-mail to hospital', '', 'paid in full, or less + why'), arr(),
    box('db', 'Hospital system', 'good', 'records what was paid'))}
  ${say('Cashless: the insurer pays the hospital directly, not the patient.')}`,
});

SLIDES.push({
  sec: 1, name: 'The domain', title: 'Words you’ll <mark>hear</mark>', menu: 'Key terms',
  body: `
  ${flow(box('file', 'Claim', '', 'the hospital asks the insurer to pay a patient’s bill'),
    box('bank', 'Insurer / TPA', '', 'pays the claim; a TPA processes it for the insurer'),
    box('table', 'Itemised bill', '', 'the bill split into heads: room, tests, implants'),
    box('mail', 'Settlement', '', 'the insurer’s reply: amount paid + reason'))}
  ${flow(box('alert', 'Deduction', 'bad', 'billed − paid: the money cut'),
    box('user', 'Co-pay', '', 'the patient’s share, e.g. 10%'),
    box('hospital', 'Room-rent limit', '', 'the most a policy pays per day for the room'),
    box('check', 'Reconciliation', 'good', 'matching what was paid to what was billed'))}`,
});

SLIDES.push({
  sec: 1, name: 'The domain', title: 'One claim, <mark>in columns</mark>', menu: 'A claim record',
  body: `
  <table class="datatbl">
    <tr class="group"><th colspan="4">HMS knows</th><th colspan="2">Insurer’s e-mail says</th><th colspan="2">Worked out</th></tr>
    <tr><th>Claim</th><th>Patient</th><th>Insurer</th><th>Billed ₹</th><th>Paid ₹</th><th>Reason</th><th>Deduction ₹</th><th>Fair?</th></tr>
    <tr><td>HSP-1001</td><td>Ramesh Kumar</td><td>Suraksha</td><td class="num">1,66,000</td><td class="num">1,66,000</td>
      <td>-</td><td class="num">0</td><td>Paid in full</td></tr>
    <tr><td>HSP-1025</td><td>Imran Khan</td><td>Suraksha</td><td class="num">2,75,200</td><td class="num">2,67,700</td>
      <td>Room rent above policy limit</td><td class="num">7,500</td><td class="fair">Fair</td></tr>
    <tr><td>HSP-1023</td><td>Manoj Tiwari</td><td>Arogya</td><td class="num">1,01,400</td><td class="num">95,200</td>
      <td>Non-payable items (gloves, masks)</td><td class="num">6,200</td><td class="fair">Fair</td></tr>
    <tr class="hi"><td>HSP-1011</td><td>Anjali Sharma</td><td>Arogya</td><td class="num">3,11,600</td><td class="num">2,33,200</td>
      <td>Investigation charges disallowed</td><td class="num">78,400</td><td class="unfair">Unfair</td></tr>
  </table>
  ${say('Fair = the policy allows it. Anything else is worth challenging.')}`,
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
