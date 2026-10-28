// Part 4: proof on known answers. Part 5: the integration (one new tab inside HMS) and what happens next.
SLIDES.push({
  sec: 4, name: 'Proof', title: 'Does it work? <mark>Test on known answers</mark>', menu: 'Results',
  body: `
  ${flow(box('file', '30 known answers', 'legacy'), arr('compare'), box('check', 'ClaimTrail’s answers', 'ours'))}
  <div class="bigs">
    <div class="bign"><b>30 / 30</b><span>claims right</span></div>
    <div class="bign"><b>2 min</b><span>instead of 3 days</span></div>
    <div class="bign"><b>0</b><span>typing errors</span></div>
    <div class="bign accent"><b>₹2 lakh</b><span>of wrong cuts spotted</span></div>
  </div>`,
});

SLIDES.push({
  sec: 5, name: 'Integration', title: 'Then: <mark>one new tab</mark> inside HMS', menu: 'Integration',
  body: `
  <div class="flow mid">
    ${box('mail', 'Mail', 'legacy')}${arr('new e-mails')}
    <div class="zone"><span class="label">Same HMS, same look</span>
      ${flow(box('laptop', 'New tab', 'ours', 'Claim Reconciliation'), arr('runs'), box('spark', 'ClaimTrail', 'ours'))}
    </div>${arr('post')}${box('db', 'Same database', 'legacy', 'settlements filled')}
  </div>
  ${flow(box('mail', 'Import', 'step', 'staff click once'), arr('', 'step'), box('search', 'Check', 'step', 'results in old HMS style'),
    arr('', 'step'), box('check', 'Post', 'good step', 'no retyping'))}`,
});

SLIDES.push({
  sec: 5, name: 'Integration', title: 'Safe by design, <mark>then scale</mark>', menu: 'Safe + next steps',
  body: `
  ${flow(box('mail', 'Only new e-mails'), '<div style="width:40px"></div>', box('db', 'Never overwrites', '', 'settled claims'),
    '<div style="width:40px"></div>', box('user', 'A person checks', 'person', 'before anything is posted'))}
  ${flow(box('check', 'Now', '', 'proven on 1 month'), arr(), box('hospital', 'Pilot', '', '1 clerk, real e-mail'), arr(),
    box('layers', 'Every month', 'ours', 'no more retyping'))}
  ${say('Staff stop retyping. They check, and post.')}`,
});
