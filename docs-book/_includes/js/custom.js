// Sidebar dropdown for the open page: its main headings appear as
// anchor links under the active navigation entry, collapsible with the
// theme's own expander arrow. A chapter stays one scrollable page.
// _includes/js/custom.js is just-the-docs' documented extension hook.
document.addEventListener("DOMContentLoaded", function () {
  var active = document.querySelector(".site-nav .nav-list-link.active");
  var content = document.querySelector(".main-content");
  if (!active || !content) { return; }

  var li = active.parentElement;
  // section landing pages carry the theme's own expander already
  if (li.querySelector(".nav-list-expander")) { return; }

  // main headings only; fall back to h2 for pages written without h1
  var heads = content.querySelectorAll("h1[id]");
  if (heads.length < 2) {
    heads = content.querySelectorAll("h2[id]");
  }

  var pagetitle = document.title.split("|")[0].trim().toLowerCase();
  var ul = document.createElement("ul");
  ul.className = "nav-list";

  heads.forEach(function (h) {
    var text = h.textContent.trim();
    if (!text || text.toLowerCase() === pagetitle) { return; }
    var item = document.createElement("li");
    item.className = "nav-list-item";
    var a = document.createElement("a");
    a.className = "nav-list-link";
    a.href = "#" + h.id;
    a.textContent = text;
    item.appendChild(a);
    ul.appendChild(item);
  });

  if (!ul.children.length) { return; }

  ul.style.display = "block";

  // the theme's expander arrow, wired to fold the heading list
  var btn = document.createElement("button");
  btn.className = "nav-list-expander btn-reset";
  btn.setAttribute("aria-label", "toggle heading list");
  btn.setAttribute("aria-pressed", "true");
  btn.innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true" style="transform: rotate(90deg);">' +
    '<use xlink:href="#svg-arrow-right"></use></svg>';
  btn.addEventListener("click", function (e) {
    e.preventDefault();
    var open = ul.style.display !== "none";
    ul.style.display = open ? "none" : "block";
    btn.querySelector("svg").style.transform =
      open ? "" : "rotate(90deg)";
    btn.setAttribute("aria-pressed", open ? "false" : "true");
  });

  li.insertBefore(btn, active);
  li.appendChild(ul);
});

// Dark mode toggle. The bootstrap script in head_custom.html has
// already picked the scheme before paint; this button swaps the
// stylesheet and remembers the choice.
document.addEventListener("DOMContentLoaded", function () {
  var btn = document.getElementById("theme-toggle");
  if (!btn) { return; }
  btn.addEventListener("click", function () {
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    var next = dark ? "default" : "dark";
    var link = document.querySelector(
      'link[rel="stylesheet"][href*="just-the-docs-"]');
    if (link) {
      link.href = link.href.replace(
        dark ? "just-the-docs-dark" : "just-the-docs-default",
        dark ? "just-the-docs-default" : "just-the-docs-dark");
    }
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("aic-theme", next);
  });
});

// Select a word in the text and a small pill offers to search the site
// for it, feeding the theme's own lunr search box. Desktop only: below
// the md breakpoint the search input is hidden and native selection
// menus take over.
document.addEventListener("DOMContentLoaded", function () {
  var content = document.querySelector(".main-content");
  var input = document.getElementById("search-input");
  if (!content || !input) { return; }

  var pill = null;

  function removePill() {
    if (pill) { pill.remove(); pill = null; }
  }

  function selectedText() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) { return null; }
    if (!content.contains(sel.anchorNode)) { return null; }
    var text = sel.toString().trim().replace(/\s+/g, " ");
    if (!text || text.length > 60 || text.split(" ").length > 4) {
      return null;
    }
    return text;
  }

  document.addEventListener("mouseup", function (e) {
    if (pill && pill.contains(e.target)) { return; }
    // wait for the browser to finalize the selection
    setTimeout(function () {
      removePill();
      if (window.innerWidth < 800) { return; }
      var text = selectedText();
      if (!text) { return; }

      var rect = window.getSelection().getRangeAt(0).getBoundingClientRect();
      pill = document.createElement("button");
      pill.className = "select-search-btn";
      pill.textContent = "Search: " + text;
      pill.style.left = (rect.left + window.scrollX) + "px";
      pill.style.top = (rect.bottom + window.scrollY + 4) + "px";
      // keep the selection visible under the pointer
      pill.addEventListener("mousedown", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
      });
      // stopPropagation keeps the theme's document click handler from
      // hiding the results we are about to show
      pill.addEventListener("click", function (ev) {
        ev.stopPropagation();
        removePill();
        input.value = text;
        input.focus(); // the theme's focus handler runs the search
      });
      document.body.appendChild(pill);
    }, 0);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { removePill(); }
  });
  document.addEventListener("scroll", removePill, { passive: true });
});
