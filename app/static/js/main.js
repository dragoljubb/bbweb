document.addEventListener("DOMContentLoaded", function() {
    // Hero sekcija
    const hero = document.querySelector('.card.bg-primary');
    if (hero) {
        hero.style.opacity = 0;
        hero.style.transition = "opacity 0.8s ease, transform 0.8s ease";
        setTimeout(() => {
            hero.style.opacity = 1;
            hero.style.transform = "translateY(0)";
        }, 100);
    }

    // Kartice utakmica
    const cards = document.querySelectorAll('.card.shadow-sm');
    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        setTimeout(() => {
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, 100);
    });
});
