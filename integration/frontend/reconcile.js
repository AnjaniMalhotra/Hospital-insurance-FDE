// Claim Reconciliation tab. The HMS server (backend/reconcile.py) runs ClaimTrail for us (fetch, AI read, rules),
// then writes the results into the HMS database when we press "Post".
const $ = (id) => document.getElementById(id);
const RESULT = { PAID_FULL: 'Paid in full', FAIR_CUT: 'Fair cut', UNFAIR_CUT: 'Unfair cut', NO_LETTER: 'No letter read',
  IN_HMS: 'Already settled in HMS' };
let rows = [];

// Steps 1 + 2: import the mailbox and let ClaimTrail read and match every letter
$('mailbox').onclick = async () => {
  $('mailbox').disabled = true;
  $('status').textContent = 'Importing letters from the billing mailbox and reading them... please wait.';
  try {
    const out = await api('/api/reconcile', {});
    rows = out.rows;
    $('status').textContent = out.letters
      ? `Checked ${out.letters} unprocessed letter(s): ${out.filled} claim(s) filled in, ${out.pending} not readable yet (retried next time). Skipped ${out.already} e-mail(s) already processed.`
      : `Nothing new in the mailbox. ${out.already} e-mail(s) already processed.`;
    $('show').value = out.filled ? 'NEW' : '';
    draw();
  } catch (err) {
    $('status').textContent = `Could not reconcile: ${err.message}`;
  }
  $('mailbox').disabled = false;
};

// Step 3: summary + results table (old HMS style)
function draw() {
  $('results').hidden = false;
  const by = (r) => rows.filter((x) => x.result === r);
  const sum = (list) => list.reduce((t, x) => t + (x.cut || 0), 0);
  const cuts = [...by('FAIR_CUT'), ...by('UNFAIR_CUT')];
  $('summary').innerHTML = `<tr><th>Claims filled in</th><th>Total deduction (Rs.)</th><th>Appealable (Rs.)</th><th>No letter read</th></tr>
    <tr><td>${rows.length - by('NO_LETTER').length} of ${rows.length}</td><td class="num">${rs(sum(cuts))} (${cuts.length} claims)</td>
    <td class="num"><b>${rs(sum(by('UNFAIR_CUT')))}</b> (${by('UNFAIR_CUT').length} appeal letters)</td>
    <td>${by('NO_LETTER').length}</td></tr>`;
  const show = $('show').value;
  $('rows').innerHTML = rows.filter((x) => !show || (show === 'NEW' ? x.new : x.result === show)).map((x) => `<tr>
    <td>${esc(x.claim_id)}${x.new ? ' <sup class="new">NEW</sup>' : ''}</td><td>${esc(x.patient_name).toUpperCase()}</td><td>${esc(x.insurer)}</td>
    <td>${esc(x.name_on_letter || '-')}</td><td>${esc(x.matched_by || '-')}</td><td class="num">${rs(x.amount_claimed)}</td>
    <td class="num">${x.paid == null ? '' : rs(x.paid)}</td><td class="num">${x.cut > 100 ? rs(x.cut) : ''}</td>
    <td>${esc(x.reason || '')}</td><td class="res-${x.result}">${RESULT[x.result]}</td>
    <td>${x.letter_file ? `<a href="/letters/${encodeURIComponent(x.letter_file)}" target="_blank">${x.letter_file.endsWith('.pdf') ? 'PDF' : 'E-mail'}</a>` : ''}</td></tr>`).join('');
}
$('show').onchange = draw;

// Step 4: the HMS server writes the results into its own database
$('post').onclick = async () => {
  try {
    const r = await api('/api/reconcile/post', {});
    $('posted').innerHTML = `Posted ${r.posted} claim(s)${r.skipped ? `, skipped ${r.skipped} already settled` : ''}. <a href="claims.html">Open Claims Register &raquo;</a>`;
  } catch (err) { $('posted').textContent = err.message; }
};
