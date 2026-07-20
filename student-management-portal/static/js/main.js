/**
 * CampusLink — shared client behaviour
 * Loaded from base.html via {% static 'js/main.js' %}
 */
(function () {
  "use strict";

  const sidebar = document.getElementById("sidebar");
  const menuToggle = document.getElementById("menuToggle");

  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", function () {
      sidebar.classList.toggle("is-open");
      const open = sidebar.classList.contains("is-open");
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Close sidebar when a nav link is tapped on small screens
    sidebar.querySelectorAll(".nav-link").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 860px)").matches) {
          sidebar.classList.remove("is-open");
          menuToggle.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  // Lightweight client-side filter for the students table (demo JS)
  const search = document.getElementById("globalSearch");
  const studentsTable = document.getElementById("studentsTable");

  if (search && studentsTable) {
    search.addEventListener("input", function () {
      const query = search.value.trim().toLowerCase();
      studentsTable.querySelectorAll("tbody tr").forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.hidden = query !== "" && !text.includes(query);
      });
    });
  }

  // Subtle entrance marker for debugging / teaching demos
  document.documentElement.dataset.jsReady = "true";
})();
