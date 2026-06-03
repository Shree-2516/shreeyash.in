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
});
