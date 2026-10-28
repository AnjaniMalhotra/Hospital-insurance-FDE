// Insurer Desk (demo tool): log in as an insurer, review each claim's itemised bill, decide, send ONE e-mail.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const rs = (n) => Number(n).toLocaleString('en-IN');
const post = (url, body) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
let desk = null;
const COLOUR = { suraksha: '#005293', kavach: '#961E2D', jeevan: '#C2410C', swasthya: '#B8860B', arogya: '#008060', sanjeevani: '#582C83' };

async function start() {
  const res = await fetch('/api/claims');
  desk = await res.json();
  $('login-view').hidden = res.status !== 401;
  $('desk-view').hidden = res.status === 401;
  if (res.status === 401) return showLogins();
  $('hospital').innerHTML = (desk.hospitals || []).map((h) => `<option${h === desk.hospital ? ' selected' : ''}>${esc(h)}</option>`).join('');
  if (!res.ok) { $('rows').innerHTML = `<tr><td colspan="7" class="err">${esc(desk.error)}</td></tr>`; return; }
  $('who').textContent = desk.insurer;
  $('format').textContent = `Your template: ${desk.format}. Select up to ${desk.batch} claim(s) per e-mail.`;
  $('terms').innerHTML = `<b>Your policy terms:</b> room rent payable up to Rs. ${rs(desk.room_limit)}/day ·
    co-pay ${desk.co_pay * 100}% where the policy has it · consumables (gloves, masks) are non-payable.
    Review the bill, pick the reason: the deduction is worked out from the bill.`;
  const options = `<option value="">Pay in full</option>
    <optgroup label="Fair cut (policy allows)">${desk.fair.map((r) => `<option>${esc(r)}</option>`).join('')}</optgroup>
    <optgroup label="Unfair cut">${desk.unfair.map((r) => `<option>${esc(r)}</option>`).join('')}</optgroup>`;
  $('rows').innerHTML = desk.claims.map((c, i) => `<tr data-i="${i}"><td><input type="checkbox"></td>
    <td>${esc(c.claim_id)}<br><button class="sm" data-bill="${i}">Review bill ▾</button></td><td>${esc(c.patient_name)}</td>
    <td class="num">${rs(c.amount_claimed)}</td><td>${esc(c.status)}</td><td><select>${options}</select></td>
    <td class="num"><input type="number" min="0" step="100" size="8" value="0" disabled></td></tr>
    <tr class="bill" id="bill-${i}" hidden><td colspan="7">${billTable(c)}</td></tr>`).join('')
    || '<tr><td colspan="7">No claims from Nirmaya yet.</td></tr>';
  tick();
}

function billTable(c) {  // the itemised bill, with what your policy says about each line
  const note = (b) => {
    if (b.head === 'Room rent' && b.rate > desk.room_limit) {
      return `above your limit of Rs. ${rs(desk.room_limit)}/day (excess Rs. ${rs(b.qty * (b.rate - desk.room_limit))})`;
    }
    return b.head.startsWith('Consumables') ? 'non-payable under the policy' : '';
  };
  return `<table><tr><th>Bill head</th><th>Details</th><th class="num">Amount (Rs.)</th><th>Policy check</th></tr>
    ${c.bill.map((b) => `<tr data-head="${esc(b.head)}"><td>${esc(b.head)}</td>
      <td>${b.head === 'Room rent' ? `${b.qty} days x Rs. ${rs(b.rate)}/day` : ''}</td><td class="num">${rs(b.amount)}</td>
      <td class="flag">${note(b)}</td></tr>`).join('')}
    <tr><td colspan="2"><b>Total billed</b></td><td class="num"><b>${rs(c.amount_claimed)}</b></td><td></td></tr></table>`;
}

async function showLogins() {
  const list = await (await fetch('/api/logins')).json();
  $('logins').innerHTML = list.map((l) => `<button type="button" class="acct" data-u="${esc(l.login)}">
    <span class="dot" style="background:${COLOUR[l.login] || '#6B7280'}">${esc(l.insurer[0])}</span>
    <span><b>${esc(l.insurer)}</b><small>${esc(l.format)}</small><code>${esc(l.login)}</code></span></button>`).join('');
}

function tick() {  // keep the selection within this insurer's batch size
  const rows = [...$('rows').querySelectorAll('tr[data-i]')];
  const n = rows.filter((tr) => tr.querySelector('input[type=checkbox]').checked).length;
  rows.forEach((tr) => {
    const box = tr.querySelector('input[type=checkbox]');
    box.disabled = !box.checked && n >= desk.batch;
    tr.classList.toggle('sel', box.checked);
  });
  $('send').disabled = !n;
  $('send').textContent = n > 1 ? `Send ONE settlement e-mail for ${n} claims` : 'Send settlement e-mail';
}

const ticked = () => $('rows').querySelectorAll('tr[data-i] input[type=checkbox]:checked').length;

function choose(tr) {  // a reason was picked: suggest its deduction, open the bill and highlight the line it cuts
  const i = tr.dataset.i, reason = tr.querySelector('select').value;
  const cut = tr.querySelector('input[type=number]'), box = tr.querySelector('input[type=checkbox]');
  cut.disabled = !reason;
  cut.value = reason ? desk.claims[i].suggest[reason] : 0;
  if (reason) $(`bill-${i}`).hidden = false;
  $(`bill-${i}`).querySelectorAll('tr[data-head]').forEach((row) => row.classList.toggle('cut', row.dataset.head === desk.head[reason]));
  if (!box.checked && ticked() < desk.batch) box.checked = true;
}

$('logins').addEventListener('click', (e) => {
  const tile = e.target.closest('[data-u]');
  if (!tile) return;
  document.querySelectorAll('.acct').forEach((t) => t.classList.toggle('on', t === tile));
  $('user').value = tile.dataset.u;
  $('pass').value = 'demo';
  $('login-msg').textContent = '';
});
$('login-form').onsubmit = async (e) => {  // the Sign in button, or Enter in either box
  e.preventDefault();
  const res = await post('/api/login', { login: $('user').value.trim(), password: $('pass').value });
  if (res.ok) start(); else $('login-msg').textContent = (await res.json()).error;
};
$('hospital').onchange = async () => { await post('/api/hospital', { name: $('hospital').value }); $('msg').textContent = ''; start(); };
$('logout').onclick = async () => { await post('/api/logout', {}); $('msg').textContent = ''; start(); };
$('rows').addEventListener('click', (e) => { const b = e.target.closest('[data-bill]'); if (b) $(`bill-${b.dataset.bill}`).hidden = !$(`bill-${b.dataset.bill}`).hidden; });
$('rows').addEventListener('change', (e) => { if (e.target.tagName === 'SELECT') choose(e.target.closest('tr')); tick(); });

$('send').onclick = async () => {
  const items = [...$('rows').querySelectorAll('tr[data-i]')].filter((tr) => tr.querySelector('input[type=checkbox]').checked)
    .map((tr) => { const c = desk.claims[tr.dataset.i], reason = tr.querySelector('select').value;
      return { claim_id: c.claim_id, reason, paid: c.amount_claimed - (reason ? Number(tr.querySelector('input[type=number]').value) || 0 : 0) }; });
  $('msg').className = ''; $('msg').textContent = 'Sending…';
  const res = await post('/api/send', { items });
  const d = await res.json();
  $('msg').className = res.ok ? 'ok' : 'err';
  $('msg').innerHTML = res.ok ? `Sent “${esc(d.subject)}” (${d.claims} claim(s)${d.attachments.length ? `, ${esc(d.attachments.join(', '))}`
    : ', details in the e-mail body'}) to ${esc(d.to)} by SMTP. <a href="${esc(d.mail)}" target="_blank">Open Nirmaya Mail ↗</a>` : esc(d.error);
  if (res.ok) start();
};
start();
