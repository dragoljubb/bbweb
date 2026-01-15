document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll("[data-tabs]").forEach(tabsRoot => {

    const contentSelector = tabsRoot.dataset.tabsContent;
    if (!contentSelector) return;

    const panelsContainer = document.querySelector(contentSelector);
    if (!panelsContainer) return;

    let tabs;

    // CASE 1: data-tabs is on <ul class="bb-tabs">
    if (tabsRoot.classList.contains("bb-tabs")) {
      tabs = tabsRoot.querySelectorAll(":scope > li > .bb-tab, :scope > .bb-tab");
    }
    // CASE 2: data-tabs is on wrapper (games)
    else {
      const tabsList = tabsRoot.querySelector(":scope > .bb-tabs");
      if (!tabsList) return;
      tabs = tabsList.querySelectorAll(":scope > li > .bb-tab, :scope > .bb-tab");
    }

    if (!tabs.length) return;

    // 🔑 samo DIREKTNI paneli
    const panels = panelsContainer.querySelectorAll(":scope > .bb-tab-panel");

    tabs.forEach(tab => {
      tab.addEventListener("click", (e) => {
        e.preventDefault();

        const targetSelector = tab.dataset.tabTarget;
        if (!targetSelector) return;

        const targetPanel = panelsContainer.querySelector(targetSelector);
        if (!targetPanel) return;

        // deactivate only this level
        tabs.forEach(t => t.classList.remove("active"));
        panels.forEach(p => p.classList.remove("active"));

        tab.classList.add("active");
        targetPanel.classList.add("active");
      });
    });

  });

});
