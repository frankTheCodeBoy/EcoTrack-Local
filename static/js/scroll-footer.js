(function () {
  let footerAnimated = false;
  let throttleTimeout = null;

  document.addEventListener("scroll", function () {
    if (footerAnimated || throttleTimeout) return;

    throttleTimeout = setTimeout(() => {
      const footer = document.getElementById("page-footer");
      const scrollPosition = window.scrollY + window.innerHeight;
      const pageHeight = document.body.offsetHeight;

      if (scrollPosition >= pageHeight - 50) {
        footer.classList.add("footer-animate");
        footerAnimated = true;
      }

      throttleTimeout = null;
    }, 100);
  });
})();
