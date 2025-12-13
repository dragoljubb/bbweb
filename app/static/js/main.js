document.addEventListener("DOMContentLoaded", function() {
    const slider = document.querySelector(".games-slider");
    if (!slider) return; // ako ne postoji slider na stranici, prekini

    const btnLeft = document.querySelector(".slide-btn.left");
    const btnRight = document.querySelector(".slide-btn.right");

    // širina kartice + gap (prema CSS-u)
    const scrollDistance = 160 + 12;

    // Klik na strelice
    btnLeft.addEventListener("click", () => {
        slider.scrollBy({ left: -scrollDistance, behavior: "smooth" });
    });

    btnRight.addEventListener("click", () => {
        slider.scrollBy({ left: scrollDistance, behavior: "smooth" });
    });

    // Skrivanje strelica kada nema scrolla
    function updateArrows() {
        if (!slider.scrollLeft) {
            btnLeft.style.visibility = "hidden";
        } else {
            btnLeft.style.visibility = "visible";
        }

        if (slider.scrollLeft + slider.clientWidth >= slider.scrollWidth - 1) {
            btnRight.style.visibility = "hidden";
        } else {
            btnRight.style.visibility = "visible";
        }
    }

    slider.addEventListener("scroll", updateArrows);
    window.addEventListener("resize", updateArrows);
    updateArrows();

    // Optional: touch podrška (klizanje prstom na mobilnim)
    let isDown = false;
    let startX;
    let scrollLeft;

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        slider.classList.add('dragging');
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
    });
    slider.addEventListener('mouseleave', () => { isDown = false; slider.classList.remove('dragging'); });
    slider.addEventListener('mouseup', () => { isDown = false; slider.classList.remove('dragging'); });
    slider.addEventListener('mousemove', (e) => {
        if(!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 1; // scroll-fastness
        slider.scrollLeft = scrollLeft - walk;
    });

    // Touch events
    slider.addEventListener('touchstart', (e) => {
        startX = e.touches[0].pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
    });
    slider.addEventListener('touchmove', (e) => {
        const x = e.touches[0].pageX - slider.offsetLeft;
        const walk = (x - startX) * 1;
        slider.scrollLeft = scrollLeft - walk;
    });
});