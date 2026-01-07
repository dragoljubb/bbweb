document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll("[data-tabs]").forEach(tabsRoot => {

    const tabs = tabsRoot.querySelectorAll(".bb-tab");
    const contentSelector = tabsRoot.dataset.tabsContent;
    if (!contentSelector) return;

    const panelsContainer = document.querySelector(contentSelector);
    if (!panelsContainer) return;

    const panels = panelsContainer.querySelectorAll(".bb-tab-panel");

    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        const targetSelector = tab.dataset.tabTarget;
        const targetPanel = panelsContainer.querySelector(targetSelector);
        if (!targetPanel) return;

        // deactivate all
        tabs.forEach(t => t.classList.remove("active"));
        panels.forEach(p => p.classList.remove("active"));

        // activate selected
        tab.classList.add("active");
        targetPanel.classList.add("active");
      });
    });

  });

});
