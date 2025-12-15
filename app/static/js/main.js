/* =========================================================
   REUSABLE HORIZONTAL SLIDER (games, news, etc.)
   ========================================================= */

function initHorizontalSlider({
    sliderSelector,
    leftBtnSelector,
    rightBtnSelector,
    cardWidth,
    gap = 12
}) {
    const slider = document.querySelector(sliderSelector);
    if (!slider) return;

    const btnLeft = document.querySelector(leftBtnSelector);
    const btnRight = document.querySelector(rightBtnSelector);

    if (!btnLeft || !btnRight) return;

    const scrollDistance = cardWidth + gap;

    // Arrow clicks
    btnLeft.addEventListener("click", () => {
        slider.scrollBy({ left: -scrollDistance, behavior: "smooth" });
    });

    btnRight.addEventListener("click", () => {
        slider.scrollBy({ left: scrollDistance, behavior: "smooth" });
    });

    // Show / hide arrows
    function updateArrows() {
        btnLeft.style.visibility =
            slider.scrollLeft <= 0 ? "hidden" : "visible";

        btnRight.style.visibility =
            slider.scrollLeft + slider.clientWidth >= slider.scrollWidth - 1
                ? "hidden"
                : "visible";
    }

    slider.addEventListener("scroll", updateArrows);
    window.addEventListener("resize", updateArrows);
    updateArrows();

    // Mouse drag
    let isDown = false;
    let startX;
    let startScrollLeft;

    slider.addEventListener("mousedown", (e) => {
        isDown = true;
        slider.classList.add("dragging");
        startX = e.pageX - slider.offsetLeft;
        startScrollLeft = slider.scrollLeft;
    });

    ["mouseleave", "mouseup"].forEach(evt =>
        slider.addEventListener(evt, () => {
            isDown = false;
            slider.classList.remove("dragging");
        })
    );

    slider.addEventListener("mousemove", (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        slider.scrollLeft = startScrollLeft - (x - startX);
    });

    // Touch support
    slider.addEventListener("touchstart", (e) => {
        startX = e.touches[0].pageX - slider.offsetLeft;
        startScrollLeft = slider.scrollLeft;
    });

    slider.addEventListener("touchmove", (e) => {
        const x = e.touches[0].pageX - slider.offsetLeft;
        slider.scrollLeft = startScrollLeft - (x - startX);
    });
}

/* =========================================================
   INIT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    // Games slider (postojeći)
    initHorizontalSlider({
        sliderSelector: ".games-slider",
        leftBtnSelector: ".slide-btn.left",
        rightBtnSelector: ".slide-btn.right",
        cardWidth: 160
    });

    // News slider (novi)
    initHorizontalSlider({
        sliderSelector: ".news-slider",
        leftBtnSelector: ".news-btn.left",
        rightBtnSelector: ".news-btn.right",
        cardWidth: 320
    });

});
