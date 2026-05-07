/* assets/help.js — Floating help button + game-style graph tooltips */
(function () {
  /* ── Floating Help Button & Modal ─────────────────────────────────────── */
  var helpBtn = document.createElement("div");
  helpBtn.className = "help-btn";
  helpBtn.innerHTML = "?";
  helpBtn.setAttribute("aria-label", "Help");

  var modal = document.createElement("div");
  modal.className = "help-modal";
  modal.innerHTML =
    '<div class="help-close">\u2715</div>' +
    "<h4>F1 Telemetry Dashboard Guide</h4>" +
    "<p><b>Speed Trace</b> \u2013 Car speed around the lap. Higher = faster sections.</p>" +
    "<p><b>Throttle / Brake</b> \u2013 Driver inputs; 100 % = full application.</p>" +
    "<p><b>Gear</b> \u2013 Current gear (1\u20138). Shows shift points.</p>" +
    "<p><b>Track Map</b> \u2013 Circuit layout colored by speed (purple = fast, yellow = slow).</p>" +
    "<p><b>Driver Compare</b> \u2013 Overlay two drivers\u2019 speed traces to see where one gains.</p>" +
    "<p><b>Race Replay</b> \u2013 Animated car positions with live leaderboard.</p>" +
    "<p><b>Calendar</b> \u2013 Click any race card to pre-load that session.</p>" +
    '<p style="margin-top:10px;font-size:10px;color:#888;">Hover the red ? icons on graphs for specific tips.</p>';

  document.body.appendChild(helpBtn);
  document.body.appendChild(modal);

  helpBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    modal.classList.toggle("active");
  });
  modal.querySelector(".help-close").addEventListener("click", function () {
    modal.classList.remove("active");
  });
  document.addEventListener("click", function (e) {
    if (!modal.contains(e.target) && e.target !== helpBtn) {
      modal.classList.remove("active");
    }
  });

  /* ── Inject styles for help button, modal, and graph tooltips ─────────── */
  var css = document.createElement("style");
  css.textContent =
    ".help-btn{position:fixed;bottom:24px;right:24px;width:44px;height:44px;" +
    "border-radius:50%;background:rgba(232,0,45,0.85);color:#fff;font-family:'Orbitron',sans-serif;" +
    "font-size:20px;font-weight:700;display:flex;align-items:center;justify-content:center;" +
    "cursor:pointer;z-index:100001;box-shadow:0 4px 20px rgba(232,0,45,0.5);" +
    "transition:transform .2s,box-shadow .2s;}" +
    ".help-btn:hover{transform:scale(1.1);box-shadow:0 6px 30px rgba(232,0,45,0.7);}" +
    ".help-modal{position:fixed;bottom:80px;right:24px;width:340px;max-height:70vh;" +
    "background:linear-gradient(135deg,#1a1e2a,#141720);border:1px solid rgba(232,0,45,0.3);" +
    "border-radius:14px;padding:22px 20px;color:rgba(255,255,255,0.88);font-family:'Rajdhani',sans-serif;" +
    "font-size:14px;line-height:1.55;z-index:100002;display:none;overflow-y:auto;" +
    "box-shadow:0 16px 60px rgba(0,0,0,0.7),0 0 30px rgba(232,0,45,0.08);}" +
    ".help-modal.active{display:block;animation:helpIn .25s ease both;}" +
    "@keyframes helpIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}" +
    ".help-modal h4{font-family:'Orbitron',sans-serif;font-size:14px;color:#E8002D;" +
    "letter-spacing:.08em;margin-bottom:14px;text-transform:uppercase;}" +
    ".help-modal p{margin-bottom:8px;}" +
    ".help-close{position:absolute;top:10px;right:14px;cursor:pointer;color:rgba(255,255,255,0.4);" +
    "font-size:16px;transition:color .15s;}" +
    ".help-close:hover{color:#fff;}";
  document.head.appendChild(css);
})();
