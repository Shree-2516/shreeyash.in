const items = document.querySelectorAll(".timeline-item");
const progress = document.querySelector(".timeline-progress");
const timeline = document.querySelector(".timeline");
const depthElements = document.querySelectorAll("[data-depth]");

function updateTimeline() {
    let visibleCount = 0;
    let activeItem = null;

    items.forEach((item) => {
        const rect = item.getBoundingClientRect();
        const visible = rect.top < window.innerHeight - 100;

        if (visible) {
            item.classList.add("show");
            visibleCount += 1;
        }

        if (rect.top < window.innerHeight * 0.55 && rect.bottom > window.innerHeight * 0.2) {
            activeItem = item;
        }
    });

    items.forEach((item) => {
        item.classList.toggle("is-active", item === activeItem);
    });

    if (!progress || !timeline || items.length === 0) {
        return;
    }

    const maxHeight = timeline.offsetHeight;
    const ratio = Math.max(visibleCount / items.length, 0.08);
    progress.style.height = `${maxHeight * ratio}px`;
}

function updateDepth() {
    const scrollY = window.scrollY;

    depthElements.forEach((element) => {
        const depth = Number(element.dataset.depth || 0);
        const translateY = scrollY * depth * -0.08;
        const rotateX = Math.min(scrollY * depth * 0.02, 6);
        element.style.transform = `translate3d(0, ${translateY}px, 0) rotateX(${rotateX}deg)`;
    });
}

function attachTilt() {
    const cards = document.querySelectorAll(".content, .journey-hero-copy, .journey-hero-panel, .goal-card");

    cards.forEach((card) => {
        card.addEventListener("mousemove", (event) => {
            if (window.innerWidth < 760) {
                return;
            }

            const rect = card.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width;
            const y = (event.clientY - rect.top) / rect.height;
            const rotateY = (x - 0.5) * 8;
            const rotateX = (0.5 - y) * 8;
            card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });
}

window.addEventListener("scroll", () => {
    updateTimeline();
    updateDepth();
});

window.addEventListener("load", () => {
    updateTimeline();
    updateDepth();
    attachTilt();
});
