// Maintenance page, live mode: Cooling Health Index and days-until-service from the slow-loop model.
// Only runs when the page is served by the ThermoTwin API; the static rows below stay as the demo mock-up.
(function () {
  function bar(h) {
    var c = h >= 85 ? '#15803d' : h >= 70 ? '#b45309' : '#b91c1c';
    return '<div style="display:flex;align-items:center;gap:8px"><div style="width:90px;height:8px;border-radius:4px;background:#e5e7eb">' +
      '<div style="width:' + h + '%;height:8px;border-radius:4px;background:' + c + '"></div></div><b>' + h + '</b></div>';
  }
  window.ttLiveUpdate = function (d) {
    var card = document.getElementById('ttHealth');
    if (!card) {
      card = document.createElement('div');
      card.id = 'ttHealth';
      card.className = 'card';
      card.style.marginBottom = '16px';
      card.innerHTML = '<h2>Cooling health · live model</h2>' +
        '<p class="hint">Each unit vs its own normal over the last 24 h: 100 = cooling like new. ' +
        'A third model predicts days until service from the trend.</p>' +
        '<table><thead><tr><th>Facility · unit</th><th>Cooling health</th><th>What the model sees</th><th>Service</th></tr></thead><tbody></tbody></table>';
      var first = document.querySelector('main .card') || document.querySelector('.card');
      first.parentNode.insertBefore(card, first);
    }
    var rows = d.fridges.slice().sort(function (a, b) {
      return (a.maintenance.health_index == null ? 101 : a.maintenance.health_index) -
             (b.maintenance.health_index == null ? 101 : b.maintenance.health_index);
    });
    card.querySelector('tbody').innerHTML = rows.map(function (f) {
      var m = f.maintenance;
      var svc = m.due ? '<span class="pill warn">Book technician' + (m.days_to_service ? ' · ~' + m.days_to_service + ' d' : '') + '</span>'
                      : '<span class="pill ok">Not needed</span>';
      return '<tr><td><b>' + f.facility + ' · ' + f.fridge + '</b></td><td>' +
        (m.health_index == null ? '<span class="pill grey">Learning</span>' : bar(m.health_index)) +
        '</td><td>' + m.message + '</td><td>' + svc + '</td></tr>';
    }).join('');
  };
})();
