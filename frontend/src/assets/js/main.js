(function () {
  "use strict";

  // Spinner (Remove loader once page is ready)
  const spinner = () => {
    window.addEventListener("load", () => {
      const spinnerElement = document.getElementById("spinner");
      if (spinnerElement) {
        spinnerElement.classList.remove("show");
      }
    });
  };
  spinner();

  // Sticky Navbar
  window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".nav-bar");
    if (window.scrollY > 45) {
      navbar?.classList.add("sticky-top", "shadow-sm");
    } else {
      navbar?.classList.remove("sticky-top", "shadow-sm");
    }
  });

  // Back to top button
  window.addEventListener("scroll", () => {
    const backToTop = document.querySelector(".back-to-top");
    if (window.scrollY > 300) {
      backToTop?.classList.add("visible");
    } else {
      backToTop?.classList.remove("visible");
    }
  });

  const backToTopBtn = document.querySelector(".back-to-top");
  if (backToTopBtn) {
    backToTopBtn.addEventListener("click", (event) => {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
