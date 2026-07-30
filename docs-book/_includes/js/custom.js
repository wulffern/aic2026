// Sidebar dropdown for the open page: its main headings appear as
// anchor links under the active navigation entry, collapsible with the
// theme's own expander arrow. A chapter stays one scrollable page.
// _includes/js/custom.js is just-the-docs' documented extension hook.
document.addEventListener("DOMContentLoaded", function () {
  var active = document.querySelector(".site-nav .nav-list-link.active");
  var content = document.querySelector(".main-content");
  if (!active || !content) { return; }

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
    var li = document.createElement("li");
    li.className = "nav-list-item";
    var a = document.createElement("a");
    a.className = "nav-list-link";
    a.href = "#" + h.id;
    a.textContent = text;
    li.appendChild(a);
    ul.appendChild(li);
  });

  if (!ul.children.length) { return; }

  var li = active.parentElement;
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
