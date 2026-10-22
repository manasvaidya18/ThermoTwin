// Shared shell for the district website: sidebar tabs, top bar, Emergency SOP checklist, SMS broadcast and toasts.
(function () {
  var b = document.body;
  var page = b.getAttribute('data-page');
  var ic = function (d) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + d + '</svg>'; };
  var tabs = [
    ['overview', 'overview.html', 'Overview', ic('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'), '', ''],
    ['facilities', 'facilities.html', 'Facilities', ic('<path d="M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6"/>'), '64', ''],
    ['alerts', 'alerts.html', 'Alerts', ic('<path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10 20a2 2 0 0 0 4 0"/>'), '3', 'warn'],
    ['maintenance', 'maintenance.html', 'Maintenance', ic('<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>'), '4', ''],
    ['exposure', 'exposure.html', 'Exposure Ledger', ic('<path d="M7 3h8l4 4v14H7z"/><path d="M11 12h5M11 16h5"/>'), '', ''],
    ['benchmark', 'benchmark.html', 'Benchmark', ic('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'), '', ''],
    ['settings', 'settings.html', 'Settings', ic('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'), '', '']
  ];
  var active = page === 'fridge' ? 'facilities' : page;

  var side = document.createElement('aside');
  side.className = 'side';
  side.innerHTML = '<div class="brandrow"><img src="../shared/logo.svg" alt=""><div><b>ThermoTwin</b><span>Pune District · 186 fridges</span></div></div>' +
    '<nav>' + tabs.map(function (t) {
      return '<a href="' + t[1] + '" class="' + (t[0] === active ? 'on' : '') + '">' + t[3] + t[2] +
        (t[4] ? '<span class="count ' + t[5] + '">' + t[4] + '</span>' : '') + '</a>';
    }).join('') + '</nav>' +
    '<a class="btn ' + (page === 'copilot' ? 'primary' : 'soft') + ' ask" href="copilot.html">' +
    ic('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>').replace('<svg', '<svg width="16" height="16"') + 'Ask ThermoTwin</a>' +
    '<div class="foot">Advisory layer. WHO PQS alarms and the certified logger stay the official record.</div>';

  var wrap = document.createElement('div');
  wrap.className = 'wrap';
  var top = document.createElement('div');
  top.className = 'topbar';
  top.innerHTML = '<div><h1>' + (b.getAttribute('data-title') || '') + '</h1><div class="sub">' + (b.getAttribute('data-sub') || '') + '</div></div>' +
    '<div class="grow"></div>' +
    '<button class="btn" data-act="sop">Emergency SOP</button>' +
    '<button class="btn" data-act="sms">SMS broadcast</button>' +
    '<button class="btn" data-act="export">Export report</button>' +
    '<div class="user"><div class="avatar">AD</div><div><b>Dr. Anita Deshmukh</b>District Immunisation Officer</div></div>';

  var main = document.querySelector('main');
  b.insertBefore(side, b.firstChild);
  b.insertBefore(wrap, main);
  wrap.appendChild(top);
  wrap.appendChild(main);

  // Toast
  var toast = document.createElement('div');
  toast.className = 'toast';
  b.appendChild(toast);
  window.ttToast = function (t) {
    toast.textContent = t; toast.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(function () { toast.classList.remove('show'); }, 2800);
  };

  // Modals
  function modal(html) {
    var bg = document.createElement('div');
    bg.className = 'modal-bg';
    bg.innerHTML = '<div class="modal">' + html + '</div>';
    bg.addEventListener('click', function (e) { if (e.target === bg || e.target.hasAttribute('data-close')) bg.classList.remove('show'); });
    b.appendChild(bg);
    return bg;
  }
  var sop = modal('<h2>Emergency SOP checklist</h2><p class="muted small">For a fridge in Critical or a confirmed power failure.</p>' +
    ['Keep the fridge door shut; note the time', 'Check the holdover clock on the fridge page', 'Call the facility in-charge and confirm the reading',
     'If holdover is under 1 h, use Lifeboat routing to move stock', 'Mark affected vials for review; do not discard without the officer',
     'Log the incident and close it once the fridge recovers'].map(function (s) {
      return '<label class="chk"><input type="checkbox"> <span>' + s + '</span></label>';
    }).join('') + '<div class="row" style="justify-content:flex-end;margin-top:14px"><button class="btn" data-close>Close</button></div>');
  var sms = modal('<h2>SMS broadcast</h2><p class="muted small">Sent through DLT-registered templates to the selected group.</p>' +
    '<div style="margin:10px 0"><select style="width:100%"><option>All facility in-charges · Pune district (64)</option><option>Haveli taluka (9)</option><option>Junnar taluka (6)</option></select></div>' +
    '<textarea rows="4" style="width:100%">Heat-wave advisory: keep ILR doors shut between 12 and 4 pm and check readings twice a day. – District Immunisation Office</textarea>' +
    '<div class="row" style="justify-content:flex-end;margin-top:12px"><button class="btn" data-close>Cancel</button><button class="btn primary" id="smsSend">Send to 64</button></div>');
  sms.querySelector('#smsSend').addEventListener('click', function () { sms.classList.remove('show'); ttToast('Demo: SMS queued to 64 facility in-charges.'); });

  top.addEventListener('click', function (e) {
    var a = e.target.closest('[data-act]');
    if (!a) return;
    if (a.dataset.act === 'sop') sop.classList.add('show');
    if (a.dataset.act === 'sms') sms.classList.add('show');
    if (a.dataset.act === 'export') ttToast('Demo: district report (PDF) would download here.');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') document.querySelectorAll('.modal-bg.show').forEach(function (m) { m.classList.remove('show'); });
  });

  // Simple chip filters: <div class="chips" data-filter="name"> + rows with data-tags="a b c"
  document.querySelectorAll('.chips[data-filter]').forEach(function (group) {
    group.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      group.querySelectorAll('button').forEach(function (x) { x.classList.toggle('on', x === btn); });
      var f = btn.dataset.f;
      document.querySelectorAll('[data-group="' + group.dataset.filter + '"] [data-tags]').forEach(function (r) {
        r.style.display = f === 'all' || r.dataset.tags.split(' ').indexOf(f) !== -1 ? '' : 'none';
      });
    });
  });
  // Clickable rows
  document.querySelectorAll('[data-href]').forEach(function (r) {
    r.classList.add('click');
    r.addEventListener('click', function (e) { if (!e.target.closest('button, a')) location.href = r.dataset.href; });
  });
})();
