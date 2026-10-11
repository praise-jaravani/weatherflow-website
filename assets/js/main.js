/* WeatherFLOW — progressive enhancement only.
   The site is fully readable with scripting disabled; everything below adds
   motion and affordances on top of working HTML. No dependencies, no network. */
(function () {
  "use strict";

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- scroll reveal, staggered among siblings ------------------------- */
  function reveal() {
    var sel = [
      "section:not(.hero):not(.page-head) > .wrap > h2",
      "section:not(.hero):not(.page-head) > .wrap > h3",
      "section:not(.hero):not(.page-head) > .wrap > p",
      "section:not(.hero):not(.page-head) > .wrap > .eyebrow",
      "section:not(.hero):not(.page-head) > .wrap > .prose",
      "section:not(.hero):not(.page-head) > .wrap > .grid",
      "section:not(.hero):not(.page-head) > .wrap > figure",
      "section:not(.hero):not(.page-head) > .wrap > .table-scroll",
      "section:not(.hero):not(.page-head) > .wrap > .note",
      "section:not(.hero):not(.page-head) > .wrap > .doclist",
      "section:not(.hero):not(.page-head) > .wrap > .people",
      "section:not(.hero):not(.page-head) > .wrap > .stat-row",
      "section:not(.hero):not(.page-head) > .wrap > details.bib",
      "section:not(.hero):not(.page-head) > .wrap > dl.kv",
      "section:not(.hero):not(.page-head) > .wrap > .next-prev",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > h2",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > h3",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > p",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > .finding",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > .note",
      "section:not(.hero):not(.page-head) > .wrap > .prose-wide > .next-prev"
    ].join(",");

    var items = Array.prototype.slice.call(document.querySelectorAll(sel));
    if (!items.length) return;

    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      // stagger whatever enters together, capped so nothing waits long
      var shown = 0;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.style.setProperty("--rd", Math.min(shown, 5) * 0.07 + "s");
        en.target.classList.add("in");
        shown++;
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });

    items.forEach(function (el) { io.observe(el); });

    // anything already above the fold should not wait for a scroll
    requestAnimationFrame(function () {
      items.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.92) {
          el.classList.add("in");
          io.unobserve(el);
        }
      });
    });
  }

  /* ---- sticky-header state + reading progress -------------------------- */
  function chrome() {
    var header = document.querySelector(".site-header");
    var bar = document.querySelector(".progress");
    if (!header) return;
    var ticking = false;

    function update() {
      var y = window.pageYOffset || document.documentElement.scrollTop;
      header.classList.toggle("stuck", y > 8);
      if (bar) {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.setProperty("--p", h > 0 ? Math.min(y / h, 1) : 0);
      }
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  }

  /* ---- stat tiles count up once, when first seen ----------------------- */
  function counters() {
    var tiles = Array.prototype.slice.call(document.querySelectorAll(".stat .n"));
    if (!tiles.length || reduced || !("IntersectionObserver" in window)) return;

    tiles.forEach(function (el) {
      var txt = el.textContent.trim();
      var m = txt.match(/^([\d,\s]*\d)(.*)$/);
      if (!m) return;
      var target = parseInt(m[1].replace(/[\s,]/g, ""), 10);
      if (!isFinite(target) || target <= 0) return;
      el.dataset.final = txt;
      el.dataset.target = target;
      el.dataset.suffix = m[2];
      el.dataset.grouped = /[\s,]/.test(m[1]) ? "1" : "";
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        io.unobserve(el);
        if (!el.dataset.target) return;
        var target = +el.dataset.target,
            suffix = el.dataset.suffix || "",
            grouped = el.dataset.grouped,
            dur = 900,
            t0 = null;
        function step(ts) {
          if (t0 === null) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          var v = Math.round(target * eased);
          el.textContent = (grouped ? v.toLocaleString("en-ZA") : v) + suffix;
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = el.dataset.final;
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.4 });

    tiles.forEach(function (el) { io.observe(el); });
  }

  function init() { reveal(); chrome(); counters(); }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
