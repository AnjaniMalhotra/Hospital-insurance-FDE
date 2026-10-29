// Part 3: the idea (ClaimTrail): before vs after, where it sits, its pipeline, and the schema the AI fills in (AI reads, code decides).
SLIDES.push({
  sec: 3, name: 'The idea', title: 'After AI: <mark>staff only review</mark>', menu: 'After AI',
  body: `<img class="shot" src="img/after-ai.png" alt="After AI: ClaimTrail reads the mail and HMS read-only, then fetch, AI reads, rules decide, post the claims; HMS shows a Reconciliation tab, staff review and post. About 2 minutes, 30 of 30 correct, unfair cuts found.">`,
});

SLIDES.push({
  sec: 3, name: 'The idea', title: 'The idea: <mark>ClaimTrail</mark>, next to HMS', menu: 'Where it sits',
  body: `
  <div class="flow mid">${col(box('mail', 'Mail', 'legacy'), box('db', 'HMS', 'legacy'))}${arr('read only')}
    ${box('spark', 'ClaimTrail', 'ours wide', 'reads · matches · decides')}${arr()}${box('user', 'Billing team', '', 'checks and posts')}</div>
  ${say('It only reads. Nothing in the hospital changes.')}`,
});

SLIDES.push({
  sec: 3, name: 'The idea', title: 'The pipeline, <mark>for one e-mail</mark>', menu: 'The pipeline',
  body: `
  ${flow(box('mail', 'Fetch', 'step', `${tag('CODE')}<br>new e-mails + claims`), arr('', 'step'),
    box('spark', 'Read', 'ours step', `${tag('AI')}<br>e-mail → clean rows`), arr('', 'step'),
    box('link', 'Match', 'step', `${tag('CODE')}<br>row → HSP-1011`), arr('', 'step'),
    box('scale', 'Decide', 'step', `${tag('CODE')}<br>fair or unfair`), arr('', 'step'),
    box('check', 'Post', 'good step', `${tag('STAFF')}<br>into HMS`))}
  ${say('No retyping. Staff only check and post.', 'step')}`,
});

SLIDES.push({
  sec: 3, name: 'The idea', title: 'AI fills a <mark>fixed schema</mark>', menu: 'The AI schema',
  body: `
  <div class="flow mid">
    ${box('mail', 'Any e-mail', 'legacy', 'letter, table, PDF,<br>1 or many patients')}${arr('AI reads')}
    ${tbl('Settlement', [['claim_no', 'str | None', '—'], ['patient_name', 'str', 'aanjali sharma'], ['billed', 'float', '311600'],
      ['paid', 'float', '233200'], ['reason', 'str', 'tests disallowed'], ['category', 'Literal', 'OTHER']], 'ours', 'pydantic · one per patient')}
    ${arr('code checks')}
    ${box('scale', 'Unfair · ₹78,400', 'bad', 'fair only if room, gloves or co-pay')}
  </div>
  ${say('Same shape for every insurer. AI never decides money.')}`,
});
