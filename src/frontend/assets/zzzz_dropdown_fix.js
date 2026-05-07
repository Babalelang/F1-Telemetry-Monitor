(function () {
  var BG = "#2a2e3a";
  var HOVER = "#343a4d";
  var MENU = "#2a2e3a";
  var TEXT = "#ffffff";

  function set(el, prop, value) {
    if (el && el.style) el.style.setProperty(prop, value, "important");
  }

  function clearBox(el) {
    set(el, "background", "transparent");
    set(el, "background-color", "transparent");
    set(el, "border", "0");
    set(el, "box-shadow", "none");
  }

  function paint() {
    document.querySelectorAll(".f1-dropdown > div, .dash-dropdown").forEach(clearBox);

    document.querySelectorAll(".Select-control").forEach(function (el) {
      set(el, "background", BG);
      set(el, "background-color", BG);
      set(el, "border", "1px solid rgba(255,255,255,0.25)");
      set(el, "border-radius", "8px");
      set(el, "box-shadow", "0 2px 8px rgba(0,0,0,0.3)");
      set(el, "height", "42px");
      set(el, "min-height", "42px");
      set(el, "color", TEXT);
    });

    document.querySelectorAll(
      ".Select-multi-value-wrapper, .Select-value, .Select-placeholder, .Select-input"
    ).forEach(clearBox);

    document.querySelectorAll(".Select-input input, .Select-input > input").forEach(function (el) {
      clearBox(el);
      set(el, "color", TEXT);
      set(el, "-webkit-text-fill-color", TEXT);
      set(el, "caret-color", TEXT);
      set(el, "height", "38px");
    });

    document.querySelectorAll(".Select-value-label, .Select-value-label *, .Select-placeholder").forEach(function (el) {
      set(el, "color", TEXT);
      set(el, "-webkit-text-fill-color", TEXT);
      set(el, "opacity", "1");
    });

    document.querySelectorAll(".Select-menu-outer, .Select-menu, .VirtualizedSelectGrid").forEach(function (el) {
      set(el, "background", MENU);
      set(el, "background-color", MENU);
      set(el, "color", TEXT);
      set(el, "border-color", "rgba(255,255,255,0.25)");
    });

    document.querySelectorAll(".Select-option, .VirtualizedSelectOption").forEach(function (el) {
      set(el, "background", MENU);
      set(el, "background-color", MENU);
      set(el, "color", TEXT);
      set(el, "-webkit-text-fill-color", TEXT);
    });

    document.querySelectorAll(".Select-option.is-focused, .VirtualizedSelectFocusedOption").forEach(function (el) {
      set(el, "background", "rgba(232,0,45,0.28)");
      set(el, "background-color", "rgba(232,0,45,0.28)");
    });

    /* React-Select v5+ portal-rendered menus (outside .f1-dropdown) */
    document.querySelectorAll('div[class*="-menu"]').forEach(function (el) {
      if (el.className && /\b\w+-menu\b/.test(el.className)) {
        set(el, "background", MENU);
        set(el, "background-color", MENU);
        set(el, "border", "1px solid rgba(255,255,255,0.22)");
        set(el, "border-radius", "10px");
        set(el, "box-shadow", "0 18px 60px rgba(0,0,0,0.72)");
        set(el, "z-index", "99999");
        set(el, "overflow", "hidden");
      }
    });
    document.querySelectorAll('div[class*="-MenuList"], div[class*="-menuList"]').forEach(function (el) {
      set(el, "background", MENU);
      set(el, "background-color", MENU);
      set(el, "padding", "4px");
    });
    document.querySelectorAll('div[class*="-option"]').forEach(function (el) {
      set(el, "background", MENU);
      set(el, "background-color", MENU);
      set(el, "color", TEXT);
      set(el, "-webkit-text-fill-color", TEXT);
      set(el, "font-family", "'JetBrains Mono', monospace");
      set(el, "font-size", "13px");
      set(el, "padding", "9px 12px");
      set(el, "border-radius", "6px");
      set(el, "cursor", "pointer");
    });
    document.querySelectorAll('div[class*="option--is-focused"]').forEach(function (el) {
      set(el, "background", "rgba(255,255,255,0.11)");
      set(el, "background-color", "rgba(255,255,255,0.11)");
    });
    document.querySelectorAll('div[class*="option--is-selected"]').forEach(function (el) {
      set(el, "background", "rgba(232,0,45,0.24)");
      set(el, "background-color", "rgba(232,0,45,0.24)");
    });
    document.querySelectorAll('div[class*="-control"]').forEach(function (el) {
      set(el, "background", BG);
      set(el, "background-color", BG);
      set(el, "border-color", "rgba(255,255,255,0.22)");
      set(el, "color", TEXT);
      set(el, "min-height", "42px");
    });
    document.querySelectorAll('div[class*="-singleValue"], div[class*="-placeholder"], div[class*="-Input"] input').forEach(function (el) {
      set(el, "color", TEXT);
      set(el, "-webkit-text-fill-color", TEXT);
    });
    document.querySelectorAll('div[class*="-indicatorSeparator"]').forEach(function (el) {
      set(el, "display", "none");
    });
  }

  function start() {
    paint();
    var obs = new MutationObserver(function () {
      requestAnimationFrame(paint);
    });
    obs.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class", "style"],
    });
    /* Repaint on click to catch menu open events */
    document.addEventListener("mousedown", function () {
      setTimeout(paint, 50);
      setTimeout(paint, 150);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
