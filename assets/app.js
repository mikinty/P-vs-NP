/* Client-side search + claim filters for the P vs NP page.
   Vanilla JS, no dependencies. */

(function () {
  "use strict";

  var searchInput = document.getElementById("search");
  var filterButtons = Array.prototype.slice.call(
    document.querySelectorAll(".filter")
  );
  var attempts = Array.prototype.slice.call(
    document.querySelectorAll("#attempt-list .attempt")
  );
  var resultCount = document.getElementById("result-count");
  var noResults = document.getElementById("no-results");

  if (!attempts.length) return;

  // Pre-compute lowercase haystacks so filtering is fast.
  var haystacks = attempts.map(function (el) {
    return el.textContent.toLowerCase().replace(/\s+/g, " ");
  });

  var activeFilter = "";

  function apply() {
    var query = (searchInput.value || "").trim().toLowerCase();
    var visible = 0;

    attempts.forEach(function (el, i) {
      var matchesFilter =
        !activeFilter ||
        (" " + el.getAttribute("data-claims") + " ").indexOf(
          " " + activeFilter + " "
        ) !== -1;
      var matchesQuery = !query || haystacks[i].indexOf(query) !== -1;
      var show = matchesFilter && matchesQuery;
      el.classList.toggle("hidden", !show);
      if (show) visible++;
    });

    resultCount.textContent =
      "Showing " + visible + " of " + attempts.length + " attempts";
    noResults.classList.toggle("hidden", visible !== 0);
  }

  searchInput.addEventListener("input", apply);

  filterButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filterButtons.forEach(function (b) {
        b.classList.remove("active");
      });
      btn.classList.add("active");
      activeFilter = btn.getAttribute("data-filter") || "";
      apply();
    });
  });

  // Dark-mode toggle: cycles light -> dark, remembers the choice.
  var toggle = document.getElementById("theme-toggle");
  var root = document.documentElement;

  function setTheme(theme) {
    if (theme === "light" || theme === "dark") {
      root.setAttribute("data-theme", theme);
    } else {
      root.removeAttribute("data-theme");
    }
    try {
      localStorage.setItem("pvsnp-theme", theme);
    } catch (e) {
      /* private mode etc. — ignore */
    }
  }

  toggle.addEventListener("click", function () {
    var prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    var current = root.getAttribute("data-theme") || (prefersDark ? "dark" : "light");
    setTheme(current === "dark" ? "light" : "dark");
  });

  try {
    var saved = localStorage.getItem("pvsnp-theme");
    if (saved) setTheme(saved);
  } catch (e) {
    /* ignore */
  }

  apply();
})();
