// Phone app live mode (only when served by the ThermoTwin API). Numbers, status and countdown come from the model;
// the cause and steps keep their translated text when the cause is the scripted one.
(function () {
  var HI = { 'Normal': 'सामान्य', 'Advisory': 'सलाह', 'Early warning': 'पूर्व चेतावनी', 'Critical': 'गंभीर', 'Sensor check': 'सेंसर जाँच' };
  function hi() { return document.documentElement.lang === 'hi'; }
  function tierText(t) { return hi() ? (HI[t] || t) : t; }
  function msg(d) {
    var p = d.ttb && d.ttb.p50;
    if (d.tier === 'Normal') return hi() ? 'स्थिर, 2–8 °C के भीतर' : 'Stable, within 2–8 °C';
    if (d.kind === 'freeze' && p && d.tier !== 'Critical') return hi() ? 'लगभग ' + p + ' मिनट में वैक्सीन जम सकती है' : 'Vaccine may freeze in about ' + p + ' min';
    if (d.kind === 'freeze' && d.tier === 'Critical') return hi() ? 'हवा एक घंटे से −0.5 °C या नीचे है' : 'Air at or below −0.5 °C for an hour';
    return d.message;
  }
  function setPill(el, d) {
    el.className = 'pill ' + { 'Normal': 'ok', 'Advisory': 'info', 'Early warning': 'warn', 'Critical': 'crit', 'Sensor check': 'grey' }[d.tier];
    el.removeAttribute('data-i18n');
    el.textContent = tierText(d.tier);
  }
  function msgBox(el, d) {
    el.removeAttribute('data-i18n');
    el.className = 'msg ' + (d.tier === 'Normal' ? 'ok' : 'warn');
    el.textContent = msg(d);
  }

  window.ttLiveUpdate = function () {
    return ttApi('/api/fridges/wagholi-ilr1').then(function (d) {
      var page = document.body.getAttribute('data-page');
      if (page === 'home') {
        var card = document.querySelector('a.card[href="alert-ilr1.html"]');
        card.className = 'card' + (d.tier === 'Critical' ? ' crit' : d.tier === 'Normal' ? '' : ' warn');
        setPill(card.querySelector('.pill'), d);
        card.querySelector('.temp').innerHTML = d.air.toFixed(1) + '<small> °C</small>';
        card.querySelector('.range').textContent = (d.slope_per_10min < 0 ? 'Falling ' : 'Rising ') +
          Math.abs(d.slope_per_10min).toFixed(1) + ' °C every 10 min · safe range 2–8 °C';
        msgBox(card.querySelector('.msg'), d);
        var s = document.querySelectorAll('.summary b');
        s[0].textContent = d.tier === 'Normal' ? '0' : '1';
        s[1].textContent = d.tier === 'Normal' ? '3' : '2';
        document.querySelector('.note').lastChild.textContent = 'Live model · ' + d.clock + ' · WHO alarms run separately';
      }
      if (page === 'detail') {
        setPill(document.getElementById('status'), d);
        msgBox(document.getElementById('lMsg'), d);
        var t = d.ttb;
        document.getElementById('lRange').textContent = t.p50 ? 'Likely between ' + (t.p10 || 10) + ' and ' + (t.p90 || '120+') + ' min · ' + d.clock
                                                               : 'No breach expected in the next 2 h · ' + d.clock;
        document.getElementById('lAir').textContent = d.air.toFixed(1) + ' °C';
        document.getElementById('lVial').textContent = d.vial.toFixed(1) + ' °C';
        document.getElementById('lAir1h').textContent = d.air_in_1h.toFixed(1) + ' °C';
        var note = document.getElementById('lStock');
        if (!note) {
          note = document.createElement('div');
          note.id = 'lStock';
          note.className = 'msg warn';
          note.style.marginTop = '10px';
          document.querySelector('.vals').insertAdjacentElement('afterend', note);
        }
        note.style.display = d.stock_note ? '' : 'none';
        note.textContent = d.stock_note ? (hi() && d.stock_note.indexOf('Protect first') === 0
          ? 'पहले बचाएँ: ' + d.freeze_sensitive.join(', ') : d.stock_note) : '';
        if (d.cause.key !== 'cooling_too_hard' && d.cause.key !== 'none') {
          var name = document.querySelector('[data-i18n="cause.name"]');
          name.removeAttribute('data-i18n');
          name.textContent = d.cause.title;
        }
        var a = d.series.air, v = d.series.vial, n = a.length;
        air = []; vac = [];
        for (var i = Math.max(0, n - 19); i < n; i += 3) { air.push(a[i]); vac.push(v[i]); }
        while (air.length < 7) { air.unshift(air[0]); vac.unshift(vac[0]); }
        var fa = d.forecast.air, fv = d.forecast.vial;
        airF = [fa[0], fa[1], fa[2], (fa[2] + fa[3]) / 2, fa[3]];
        vacF = [fv[0], fv[1], fv[2], (fv[2] + fv[3]) / 2, fv[3]];
        window.ttLiveOn = true;
        drawChart();
      }
    });
  };
})();
