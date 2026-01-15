document.addEventListener("click", function (e) {

  const tab = e.target.closest(".bb-tab");
  if (!tab) return;

  e.preventDefault();

  const container = tab.closest(".tabs-container");
  if (!container) return;

  const targetSelector = tab.dataset.tab;
  if (!targetSelector) return;

  const targetPanel = container.querySelector(targetSelector);
  if (!targetPanel) return;

  container.querySelectorAll(":scope > .bb-tabs .bb-tab")
    .forEach(t => t.classList.remove("active"));

  container.querySelectorAll(":scope > .bb-tab-panel")
    .forEach(p => p.classList.remove("active"));

  tab.classList.add("active");
  targetPanel.classList.add("active");

});
