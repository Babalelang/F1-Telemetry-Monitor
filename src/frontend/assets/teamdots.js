/*
 * teamdots.js — place this in frontend/assets/
 * Dash auto-loads all JS files from assets/ on every page.
 *
 * Watches for dropdown option elements and sets --dot-color
 * from the option's title attribute (which we set to the team hex in layout.py).
 */

(function () {
  var TEAM_COLORS = {
    VER:"#3671C6",PER:"#3671C6",HAM:"#27F4D2",RUS:"#27F4D2",
    LEC:"#E8002D",SAI:"#E8002D",NOR:"#FF8000",PIA:"#FF8000",
    ALO:"#358C75",STR:"#358C75",OCO:"#FF87BC",GAS:"#FF87BC",
    ALB:"#64C4FF",SAR:"#64C4FF",TSU:"#5E8FAA",LAW:"#5E8FAA",
    HAD:"#5E8FAA",HUL:"#B6BABD",MAG:"#B6BABD",BOR:"#B6BABD",
    BOT:"#00E701",ZHO:"#00E701",ANT:"#27F4D2",DOO:"#FF8000"
  };

  function applyDots() {
    // react-select v5 renders options with data-value or inner text
    document.querySelectorAll('.f1-dropdown [class*="-option"]').forEach(function(el) {
      var txt = el.innerText && el.innerText.trim().toUpperCase();
      var color = txt && TEAM_COLORS[txt];
      if (color) {
        el.style.setProperty("--dot-color", color);
      }
    });
    // Also color the selected value pill
    document.querySelectorAll('.f1-dropdown [class*="-singleValue"]').forEach(function(el) {
      var txt = el.innerText && el.innerText.trim().toUpperCase();
      var color = txt && TEAM_COLORS[txt];
      if (color) {
        el.style.setProperty("--dot-color", color);
      }
    });
  }

  // Run on mutations so it catches dynamically rendered options
  var observer = new MutationObserver(applyDots);
  observer.observe(document.body, { childList: true, subtree: true });
  // Also run immediately on load
  applyDots();
})();