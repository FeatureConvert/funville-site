// The only script on the site: folds the menu behind a button on narrow screens.
// Without it the menu simply shows in full. Loaded in <head>, so the page never jumps.
document.documentElement.classList.add("js");
document.addEventListener("DOMContentLoaded", function () {
  var nav = document.getElementById("site-nav");
  var btn = document.querySelector(".nav-toggle");
  if (!nav || !btn) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("open")) {
      nav.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      btn.focus();
    }
  });
});
