// Live mode: when the page is served by the ThermoTwin API (python backend/run_all.py), pull real model output every
// 2 s and show a demo-clock bar. When the API is absent (static demo), nothing changes and the fixed data stays.
(function () {
  var TIER_CLASS = { 'Normal': 'ok', 'Advisory': 'info', 'Early warning': 'warn', 'Critical': 'crit', 'Sensor check': 'sensor' };
  window.ttTierClass = function (t) { return TIER_CLASS[t] || 'grey'; };

  function api(path, body) {
    var ctl = new AbortController();
    setTimeout(function () { ctl.abort(); }, 6000);   // generous: a busy demo laptop can be slow; offline mode fails fast anyway
    return fetch(path, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: ctl.signal }
                            : { signal: ctl.signal }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  window.ttApi = api;

  function bar(state) {
    var b = document.getElementById('ttLiveBar');
    if (!b) {
      b = document.createElement('div');
      b.id = 'ttLiveBar';
      b.style.cssText = 'position:fixed;left:12px;bottom:' + (document.querySelector('nav.tabs') ? '78px' : '12px') +
        ';z-index:9999;background:#14211c;color:#fff;border-radius:12px;padding:6px 8px;display:flex;align-items:center;gap:6px;' +
        'font:12px "Segoe UI",system-ui,sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.25)';
      b.innerHTML = '<span style="background:#15803d;border-radius:6px;padding:1px 6px;font-weight:700">LIVE MODEL</span>' +
        '<span id="ttClock" style="min-width:92px"></span>' +
        ['play', 'pause', 'step', 'reset'].map(function (a) {
          var label = { play: '▶', pause: '❚❚', step: '+1 h', reset: '⟲' }[a];
          return '<button data-a="' + a + '" title="' + a + '" style="background:#2a3b34;color:#fff;border:0;border-radius:6px;padding:3px 7px;cursor:pointer;font:inherit">' + label + '</button>';
        }).join('');
      b.addEventListener('click', function (e) {
        var x = e.target.closest('button'); if (!x) return;
        var a = x.dataset.a;
        api('/api/clock', a === 'step' ? { action: 'step', ticks: 6 } : { action: a }).then(tick);
      });
      document.body.appendChild(b);
      document.addEventListener('keydown', function (e) {
        if (e.target.matches('input, textarea')) return;
        if (e.key === 'l' || e.key === 'L') b.style.display = b.style.display === 'none' ? 'flex' : 'none';
      });
    }
    document.getElementById('ttClock').textContent = state.clock + (state.playing ? ' ▸' : '');
  }

  function tick() {
    var upd = window.ttLiveUpdate;
    return api('/api/fridges').then(function (d) {
      bar(d.state);
      if (upd) return upd(d);
    }).catch(function () {});
  }

  api('/api/state').then(function () {
    document.documentElement.classList.add('tt-live');
    tick();
    setInterval(tick, 2000);
  }).catch(function () { /* static demo: keep fixed data */ });
})();
