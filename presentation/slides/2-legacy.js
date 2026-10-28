// Part 2: the legacy system: how it is connected, what its database stores, and why the e-mails are hard to read.
SLIDES.push({
  sec: 2, name: 'The legacy system', title: 'Two systems and <mark>one busy person</mark>', menu: 'Legacy architecture',
  body: `
  <div class="flow mid">
    ${box('file', '6 insurers', 'legacy', 'outside the hospital')}${arr('e-mail')}
    <div class="zone"><span class="label">Nirmaya hospital</span>
      ${flow(box('mail', 'Mail', 'legacy', 'knows what was paid'), arr('reads', 'dash'), box('user', 'Billing clerk', 'person'),
        arr('types', 'dash'), box('db', 'HMS', 'legacy', 'knows what was billed'))}
    </div>
  </div>
  ${say('Mail and HMS never talk. Only a person connects them.')}`,
});

SLIDES.push({
  sec: 2, name: 'The legacy system', title: 'What HMS <mark>stores</mark>', menu: 'HMS database schema',
  body: `
  <div class="flow mid">
    ${tbl('patients', [['uhid', 'key'], ['name', 'text'], ['insurer', 'text'], ['policy', 'text'], ['admitted', 'date']])}
    ${arr('1 → many')}
    ${tbl('claims', [['claim_id', 'key'], ['uhid', '→ patients'], ['insurer', 'text'], ['billed', 'rupees'], ['status', 'SUBMITTED…']])}
    ${arr('1 → many')}
    ${col(tbl('bill_items', [['claim_id', '→ claims'], ['head', 'room, tests…'], ['amount', 'rupees']]),
      tbl('settlements', [['claim_id', '→ claims'], ['paid', 'rupees'], ['deduction', 'rupees'], ['reason', 'text']], 'hand', 'typed by hand'))}
  </div>
  ${say('HMS knows the bill. The <span style="color:#B00020">settlement</span> is retyped from each e-mail.')}`,
});

SLIDES.push({
  sec: 2, name: 'The legacy system', title: 'Six insurers, <mark>six formats</mark>', menu: 'Why e-mails are hard',
  body: `
  ${flow(box('file', 'Suraksha', 'legacy', 'PDF letter'), box('file', 'Arogya', 'legacy', 'PDF, no claim number'),
    box('mail', 'Jeevan', 'legacy', 'text in the e-mail'), box('table', 'Kavach', 'legacy', 'PDF table, 3 patients'),
    box('table', 'Swasthya', 'legacy', 'e-mail table, 3 patients'), box('layers', 'Sanjeevani', 'legacy', 'PDF, table per patient'))}
  ${say('No single rule can read all six. <mark>This is the job for AI.</mark>')}`,
});
