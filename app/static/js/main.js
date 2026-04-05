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
