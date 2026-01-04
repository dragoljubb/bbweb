document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('playerSearch');
  const playersGrid = document.getElementById('playersGrid');
  const playerCards = Array.from(playersGrid.children);
  const loadMoreBtn = document.getElementById('loadMorePlayers');

  let visibleCount = 24; // inicijalno 6 redova x 4

  function showPlayers() {
    let shown = 0;
    const filterActive = searchInput.value.trim() !== "";

    playerCards.forEach(card => {
      const match = card.dataset.match === "true";

      if (filterActive) {
        // kad je filter aktivan, prikaži sve koji odgovaraju
        card.style.display = match ? 'block' : 'none';
      } else {
        // kad filter nije aktivan, prikaži samo prvih visibleCount
        if (match && shown < visibleCount) {
          card.style.display = 'block';
          shown++;
        } else {
          card.style.display = 'none';
        }
      }
    });

    // dugme Load More: sakrij ako filter aktivan ili nema više za prikaz
    const anyHidden = playerCards.some(c => c.dataset.match === "true" && c.style.display === 'none');
    loadMoreBtn.style.display = (!filterActive && anyHidden) ? 'inline-block' : 'none';
  }

  // inicijalno
  showPlayers();

  // Search filter
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.toLowerCase().trim();

    playerCards.forEach(card => {
      const name = card.dataset.name;
      card.dataset.match = name.includes(query) ? "true" : "false";
    });

    showPlayers();
  });

  // Load more dugme
  loadMoreBtn.addEventListener('click', () => {
    visibleCount += 24; // dodaj sledećih 24
    showPlayers();
  });
});
