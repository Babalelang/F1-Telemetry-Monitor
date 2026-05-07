/*
 * teamdots.js — place in assets/
 * Watches for dropdown option elements and sets --dot-color
 * from the driver's team color, enabling colored dots in dropdowns.
 */

(function () {
  var TEAM_COLORS = {
    // Red Bull
    VER: "#3671C6", HAD: "#3671C6",
    // Mercedes
    RUS: "#27F4D2", ANT: "#27F4D2",
    // Ferrari
    LEC: "#E8002D", HAM: "#E8002D",
    // McLaren
    NOR: "#FF8000", PIA: "#FF8000",
    // Aston Martin
    ALO: "#358C75", STR: "#358C75",
    // Alpine
    GAS: "#FF87BC", DOO: "#FF87BC",
    // Williams
    ALB: "#64C4FF", SAI: "#64C4FF",
    // Racing Bulls
    TSU: "#5E8FAA", LAW: "#5E8FAA",
    // Haas
    BEA: "#B6BABD", OCO: "#B6BABD",
    // Kick Sauber
    BOT: "#52C374", ZHO: "#52C374",
    // Legacy
    PER: "#3671C6", MAG: "#B6BABD", HUL: "#B6BABD",
  };

  function applyDots() {
    document.querySelectorAll('.f1-dropdown [class*="-option"]').forEach(function (el) {
      var txt = el.innerText && el.innerText.trim().toUpperCase();
      var color = txt && TEAM_COLORS[txt];
      if (color) el.style.setProperty("--dot-color", color);
    });
    document.querySelectorAll('.f1-dropdown [class*="-singleValue"]').forEach(function (el) {
      var txt = el.innerText && el.innerText.trim().toUpperCase();
      var color = txt && TEAM_COLORS[txt];
      if (color) el.style.setProperty("--dot-color", color);
    });
  }

  var observer = new MutationObserver(applyDots);
  observer.observe(document.body, { childList: true, subtree: true });
  applyDots();
})();

