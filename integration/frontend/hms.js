// Shared by the HMS pages: the header + menu, and a helper to call the HMS API (which reads/writes the database).
const rs = (n) => (n === '' || n == null ? '' : Number(n).toLocaleString('en-IN'));
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const param = (k) => new URLSearchParams(location.search).get(k);

async function api(path, body) {
  const options = body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : {};
  const res = await fetch(path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

// Header: blue title bar, grey menu (current page highlighted), breadcrumb from the page's data-crumb
const page = location.pathname.split('/').pop() || 'patients.html';
const links = [['patients.html', 'Patients'], ['claims.html', 'Insurance Claims'],
  ['reconcile.html', 'Claim Reconciliation <sup class="new">NEW</sup>'], ['login.html', 'Logout']];
const hms = document.getElementById('hms');
hms.innerHTML = `<div class="hms-top"><b>Nirmaya HMS v4.2 &middot; Hospital Management System</b>
  <span>User: BILLING02 (Billing &amp; Insurance) | ${new Date().toLocaleDateString('en-IN')}</span></div>
  <div class="hms-menu">${links.map(([href, text]) => `<a href="${href}"${href === page ? ' class="on"' : ''}>${text}</a>`).join(' | ')}</div>
  <div class="crumb">${hms.dataset.crumb}</div>`;
