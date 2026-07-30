// Sidebar dropdown for the open page: its main headings appear as
// anchor links under the active navigation entry, so a chapter stays
// one scrollable page but can be navigated from the nav pane.
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

  if (ul.children.length) {
    active.parentElement.appendChild(ul);
  }
});
