/* Small progressive enhancements. The site works without JavaScript. */
(function () {
  "use strict";

  /* 1. E-mail address
     The address is never written in the HTML, so simple harvesting bots
     that scan page source for "name@domain" do not find it. Elements with
     data-user / data-domain are turned into a working mailto: link. */
  document.querySelectorAll("[data-user][data-domain]").forEach(function (el) {
    var addr = el.getAttribute("data-user") + "@" + el.getAttribute("data-domain");
    el.setAttribute("href", "mailto:" + addr);
    var label = el.querySelector("[data-email-label]");
    if (label) label.textContent = addr;
  });

  /* 2. Publication filters (publications page only) */
  var list = document.getElementById("publist");
  if (!list) return;

  var items = Array.prototype.slice.call(list.querySelectorAll(".pub"));
  var groups = Array.prototype.slice.call(list.querySelectorAll(".year-group"));
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip[data-topic]"));
  var search = document.getElementById("pubsearch");
  var count = document.getElementById("pubcount");
  var empty = document.getElementById("pubempty");
  var topic = "all";

  function norm(s) {           // case- and accent-insensitive matching
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  items.forEach(function (li) { li._text = norm(li.textContent); });

  function apply() {
    var q = norm(search.value.trim());
    var shown = 0;
    items.forEach(function (li) {
      var topics = (li.getAttribute("data-topics") || "").split(" ");
      var ok = (topic === "all" || topics.indexOf(topic) !== -1) && (!q || li._text.indexOf(q) !== -1);
      li.hidden = !ok;
      if (ok) shown++;
    });
    groups.forEach(function (g) { g.hidden = !g.querySelector(".pub:not([hidden])"); });
    count.textContent = shown + (shown === 1 ? " item" : " items");
    empty.hidden = shown !== 0;
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      topic = c.getAttribute("data-topic");
      chips.forEach(function (o) { o.setAttribute("aria-pressed", String(o === c)); });
      apply();
    });
  });
  search.addEventListener("input", apply);
  document.querySelector(".filters").hidden = false;   // only show controls when JS runs
  apply();
})();
