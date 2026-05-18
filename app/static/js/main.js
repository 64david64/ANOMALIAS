document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.getElementById("navToggle");
    const navLinks = document.getElementById("navLinks");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            navLinks.classList.toggle("is-open");
        });
    }

    const currentPath = window.location.pathname;

    document.querySelectorAll(".nav-links a").forEach((link) => {
        const href = link.getAttribute("href");

        if (href === currentPath) {
            link.classList.add("active");
        }
    });
});