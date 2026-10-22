// Shared header, bottom tabs, EN/Hindi toggle and toast for the phone app.
(function () {
  var T = {
    hi: {
      'clinic': 'पीएचसी वाघोली, पुणे',
      'tab.home': 'होम', 'tab.alerts': 'अलर्ट', 'tab.help': 'मदद',
      'home.title': '3 फ्रिज की निगरानी', 'home.attn': 'ध्यान दें', 'home.normal': 'सामान्य',
      'st.normal': 'सामान्य', 'st.early': 'पूर्व चेतावनी', 'st.watch': 'रिकवरी पर नज़र',
      'ilr1.msg': 'लगभग 60 मिनट में 0 °C से नीचे जा सकता है',
      'cta.see': 'क्या करें देखें →',
      'back': '← वापस',
      'cause.title': 'संभावित कारण', 'cause.name': 'थर्मोस्टैट बहुत ठंडा सेट है',
      'steps.title': 'अभी क्या करें',
      'step1': 'थर्मोस्टैट नॉब को एक स्टेप गर्म की ओर घुमाएँ',
      'step2': 'जमने से खराब होने वाली वैक्सीन को दीवारों से दूर रखें',
      'step3': '20 मिनट बाद फिर जाँचें',
      'btn.done': 'मैंने कर दिया', 'btn.call': 'सुपरवाइज़र को कॉल करें'
    }
  };
  var original = {};

  function getLang() { try { return localStorage.getItem('tt-lang') || 'en'; } catch (e) { return 'en'; } }
  function setLang(l) { try { localStorage.setItem('tt-lang', l); } catch (e) {} applyLang(l); }

  function applyLang(l) {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var k = el.getAttribute('data-i18n');
      if (!(k in original)) original[k] = el.textContent;
      el.textContent = l === 'hi' && T.hi[k] ? T.hi[k] : original[k];
    });
    document.querySelectorAll('.lang button').forEach(function (b) { b.classList.toggle('on', b.dataset.l === l); });
    document.documentElement.lang = l;
  }

  var page = document.body.getAttribute('data-page');
  var header = document.createElement('header');
  header.className = 'top';
  header.innerHTML = (page === 'detail'
      ? '<a class="back" href="alerts.html" data-i18n="back">← Back</a><div class="brand"></div>'
      : '<img class="logo" src="../shared/logo.svg" alt=""><div class="brand"><b>ThermoTwin</b><span data-i18n="clinic">PHC Wagholi, Pune</span></div>') +
    '<div class="lang"><button data-l="en">EN</button><button data-l="hi">हिं</button></div>';
  document.body.insertBefore(header, document.body.firstChild);

  var icons = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
    alerts: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>',
    help: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14"/><circle cx="12" cy="17.5" r=".6" fill="currentColor"/></svg>'
  };
  var active = page === 'detail' ? 'alerts' : page;
  var nav = document.createElement('nav');
  nav.className = 'tabs';
  [['home', 'home.html', 'Home'], ['alerts', 'alerts.html', 'Alerts'], ['help', 'help.html', 'Help']].forEach(function (t) {
    var a = document.createElement('a');
    a.href = t[1];
    a.className = t[0] === active ? 'on' : '';
    a.innerHTML = icons[t[0]] + '<span data-i18n="tab.' + t[0] + '">' + t[2] + '</span>' +
      (t[0] === 'alerts' ? '<span class="badge">1</span>' : '');
    nav.appendChild(a);
  });
  document.body.appendChild(nav);

  header.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.l); });
  });

  window.ttToast = function (text) {
    var t = document.querySelector('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = text;
    t.classList.add('show');
    setTimeout(function () { t.classList.remove('show'); }, 2600);
  };

  applyLang(getLang());
})();
