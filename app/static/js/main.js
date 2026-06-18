function scrollToProjects() {
    const projectsSection = document.getElementById("projects");

    if (!projectsSection) {
        return;
    }

    projectsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

window.addEventListener("load", () => {
    if (!window.location.hash) {
        return;
    }

    window.history.replaceState(null, "", window.location.pathname + window.location.search);
    window.scrollTo({
        top: 0,
        behavior: "auto"
    });
});

// Auto-dismiss flash notifications after 3.5 seconds
document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(flash => {
        const dismiss = () => {
            if (flash.classList.contains("fade-out")) return;
            flash.classList.add("fade-out");
            setTimeout(() => {
                flash.remove();
            }, 400);
        };

        // Auto-dismiss after 3.5 seconds
        const timeoutId = setTimeout(dismiss, 3500);

        // Allow click to dismiss immediately
        flash.addEventListener("click", () => {
            clearTimeout(timeoutId);
            dismiss();
        });
    });

    // Mobile Navigation Toggle
    const navToggle = document.querySelector(".nav-toggle");
    const siteNav = document.querySelector(".site-nav");
    const navLinks = document.querySelectorAll(".site-nav-links a");

    if (navToggle && siteNav) {
        navToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            const isOpen = siteNav.classList.toggle("nav-open");
            navToggle.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", isOpen);
        });

        // Close mobile menu when clicking a link
        navLinks.forEach(link => {
            link.addEventListener("click", () => {
                siteNav.classList.remove("nav-open");
                navToggle.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
            });
        });

        // Close menu when clicking outside of it
        document.addEventListener("click", (e) => {
            if (!siteNav.contains(e.target) && siteNav.classList.contains("nav-open")) {
                siteNav.classList.remove("nav-open");
                navToggle.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
            }
        });
    }

    // Animate skill bars on load
    const skillBars = document.querySelectorAll(".skill-bar[data-pct]");
    setTimeout(() => {
        skillBars.forEach(bar => {
            const pct = bar.getAttribute("data-pct");
            bar.style.width = pct + "%";
        });
    }, 100);

    // Toggle Projects Card Visibility
    const toggleProjectsBtn = document.getElementById("toggle-projects-btn");
    const projectGrid = document.querySelector(".project-grid");
    if (toggleProjectsBtn && projectGrid) {
        toggleProjectsBtn.addEventListener("click", () => {
            const isExpanded = projectGrid.classList.toggle("show-all");
            toggleProjectsBtn.innerText = isExpanded ? "Show Less" : "View All Projects";
            if (!isExpanded) {
                document.getElementById("projects").scrollIntoView({ behavior: "smooth" });
            }
        });
    }

    // Toggle Certifications Card Visibility
    const toggleCertsBtn = document.getElementById("toggle-certs-btn");
    const certGrid = document.querySelector(".certificate-grid");
    if (toggleCertsBtn && certGrid) {
        toggleCertsBtn.addEventListener("click", () => {
            const isExpanded = certGrid.classList.toggle("show-all");
            toggleCertsBtn.innerText = isExpanded ? "Show Less" : "View All Certifications";
            if (!isExpanded) {
                document.getElementById("certificates").scrollIntoView({ behavior: "smooth" });
            }
        });
    }

    // Light & Dark Theme Toggle
    const themeToggleBtn = document.getElementById("theme-toggle");
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
        });
    }
});

