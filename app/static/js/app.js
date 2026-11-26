(function () {
  // Flash / Toast notifications
  const ensureFlashWrap = () => {
    let wrap = document.querySelector(".flash-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "flash-wrap";
      wrap.setAttribute("role", "status");
      wrap.setAttribute("aria-live", "polite");
      const main = document.querySelector(".app-main, .public-main") || document.body;
      const topbar = main.querySelector(".topbar");
      if (topbar) {
        topbar.insertAdjacentElement("afterend", wrap);
      } else {
        main.prepend(wrap);
      }
    }
    return wrap;
  };

  const bindFlash = (flash) => {
    const dismiss = () => {
      flash.classList.add("is-closing");
      setTimeout(() => flash.remove(), 240);
    };
    const closeBtn = flash.querySelector(".flash-close");
    if (closeBtn) closeBtn.addEventListener("click", dismiss);
    setTimeout(dismiss, 5000);
  };

  document.querySelectorAll(".flash").forEach(bindFlash);

  document.querySelectorAll(".progress-track [data-progress]").forEach((bar) => {
    const progress = Number(bar.dataset.progress);
    if (Number.isFinite(progress)) {
      bar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
    }
  });

  const showToast = (message, category = "warning") => {
    const wrap = ensureFlashWrap();
    const flash = document.createElement("div");
    flash.className = `flash ${category}`;
    const span = document.createElement("span");
    span.textContent = message;
    const btn = document.createElement("button");
    btn.className = "flash-close";
    btn.type = "button";
    btn.setAttribute("aria-label", "Dismiss notification");
    btn.innerHTML = "&times;";
    flash.append(span, btn);
    wrap.appendChild(flash);
    bindFlash(flash);
  };

  // Sidebar collapse (desktop) & drawer (mobile)
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const collapseBtn = document.getElementById("sidebarCollapseBtn");
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const mobileCloseBtn = document.getElementById("sidebarMobileClose");

  if (collapseBtn) {
    collapseBtn.addEventListener("click", () => {
      document.body.classList.toggle("sidebar-collapsed");
      const collapsed = document.body.classList.contains("sidebar-collapsed");
      localStorage.setItem("skillradar.sidebarCollapsed", collapsed ? "1" : "0");
      setTimeout(() => window.dispatchEvent(new Event("resize")), 220);
    });
  }

  const closeMobileSidebar = () => {
    if (!sidebar) return;
    sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("open");
    if (mobileMenuBtn) mobileMenuBtn.setAttribute("aria-expanded", "false");
  };

  const openMobileSidebar = () => {
    if (!sidebar) return;
    sidebar.classList.add("open");
    if (backdrop) backdrop.classList.add("open");
    if (mobileMenuBtn) mobileMenuBtn.setAttribute("aria-expanded", "true");
  };

  if (mobileMenuBtn) mobileMenuBtn.addEventListener("click", openMobileSidebar);
  if (mobileCloseBtn) mobileCloseBtn.addEventListener("click", closeMobileSidebar);
  if (backdrop) backdrop.addEventListener("click", closeMobileSidebar);

  // Accessible Confirmation Modal
  let confirmCallback = null;
  const getConfirmModal = () => {
    let modal = document.getElementById("srConfirmModal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "srConfirmModal";
    modal.className = "modal-backdrop";
    modal.hidden = true;
    modal.innerHTML = `
      <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="srConfirmTitle">
        <h3 id="srConfirmTitle">Confirm action</h3>
        <p id="srConfirmMessage"></p>
        <div class="modal-actions">
          <button type="button" class="button ghost" data-modal-cancel>Cancel</button>
          <button type="button" class="button primary" data-modal-ok>Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    const closeModal = () => {
      modal.hidden = true;
      confirmCallback = null;
    };
    modal.querySelector("[data-modal-cancel]").addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
    modal.querySelector("[data-modal-ok]").addEventListener("click", () => {
      const cb = confirmCallback;
      closeModal();
      if (cb) cb();
    });
    return modal;
  };

  const openConfirmModal = (title, message, okLabel, onConfirm) => {
    const modal = getConfirmModal();
    modal.querySelector("#srConfirmTitle").textContent = title || "Confirm action";
    modal.querySelector("#srConfirmMessage").textContent = message;
    modal.querySelector("[data-modal-ok]").textContent = okLabel || "Confirm";
    confirmCallback = onConfirm;
    modal.hidden = false;
    modal.querySelector("[data-modal-ok]").focus();
  };

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMobileSidebar();
      const modal = document.getElementById("srConfirmModal");
      if (modal && !modal.hidden) modal.hidden = true;
    }
  });

  // Password visibility toggles
  document.querySelectorAll("[data-toggle-password]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-toggle-password");
      const input = document.getElementById(targetId);
      if (!input) return;
      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      btn.textContent = isHidden ? "Hide" : "Show";
      btn.setAttribute("aria-pressed", isHidden ? "true" : "false");
    });
  });

  // Expandable detail toggles
  document.querySelectorAll("[data-expand-target]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const panel = document.getElementById(btn.getAttribute("data-expand-target"));
      if (!panel) return;
      const expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      panel.hidden = expanded;
      const showLabel = btn.getAttribute("data-label-show") || "Show details";
      const hideLabel = btn.getAttribute("data-label-hide") || "Hide details";
      btn.textContent = expanded ? showLabel : hideLabel;
    });
  });

  // Filter pills + search input for cards/rows
  document.querySelectorAll("[data-filter-group]").forEach((toolbar) => {
    const groupSelector = toolbar.getAttribute("data-filter-group");
    const items = () => Array.from(document.querySelectorAll(groupSelector));
    const emptyEl = document.querySelector(toolbar.getAttribute("data-filter-empty") || "");
    const searchInput = toolbar.querySelector("[data-filter-search]");
    let activeFilter = "all";

    const applyFilters = () => {
      const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
      let visibleCount = 0;
      items().forEach((el) => {
        const status = (el.getAttribute("data-filter-value") || "").toLowerCase();
        const text = (el.getAttribute("data-search-text") || el.textContent || "").toLowerCase();
        const matchFilter = activeFilter === "all" || status === activeFilter;
        const matchQuery = !query || text.includes(query);
        const show = matchFilter && matchQuery;
        el.hidden = !show;
        if (show) visibleCount += 1;
      });
      if (emptyEl) emptyEl.hidden = visibleCount > 0;
    };

    toolbar.querySelectorAll("[data-filter]").forEach((pill) => {
      pill.addEventListener("click", () => {
        toolbar.querySelectorAll("[data-filter]").forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        activeFilter = pill.getAttribute("data-filter").toLowerCase();
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", applyFilters);
    }
  });

  // Form loading state & optional confirmation modal
  document.querySelectorAll("form[data-enhance-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (form.dataset.confirmed === "1") return;
      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
        showToast("Please complete all required fields accurately.", "danger");
        return;
      }

      const confirmMsg = form.getAttribute("data-confirm");
      const shouldConfirm = confirmMsg && form.getAttribute("data-confirm-active") !== "false";
      if (shouldConfirm) {
        event.preventDefault();
        openConfirmModal(
          form.getAttribute("data-confirm-title") || "Confirm action",
          confirmMsg,
          form.getAttribute("data-confirm-ok") || "Continue",
          () => {
            form.dataset.confirmed = "1";
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
              const loadingText = submitBtn.getAttribute("data-loading-text");
              if (loadingText) submitBtn.textContent = loadingText;
              submitBtn.disabled = true;
            }
            form.submit();
          }
        );
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        const loadingText = submitBtn.getAttribute("data-loading-text");
        if (loadingText) submitBtn.textContent = loadingText;
        submitBtn.disabled = true;
      }
    });
  });

  // Shared Chart.js styling & helpers
  const baseTooltip = {
    backgroundColor: "#0f172a",
    titleColor: "#f8fafc",
    bodyColor: "#e2e8f0",
    padding: 10,
    cornerRadius: 8,
    displayColors: true,
    boxPadding: 4
  };

  const baseLegend = {
    position: "bottom",
    labels: {
      usePointStyle: true,
      pointStyle: "circle",
      padding: 16,
      color: "#475569",
      font: { family: "Inter, sans-serif", size: 12, weight: "600" }
    }
  };

  window.SkillRadar = {
    toast: showToast,
    confirm: openConfirmModal,
    radarChart(canvasId, labels, current, target) {
      const el = document.getElementById(canvasId);
      if (!window.Chart || !el || !labels || !labels.length) return null;
      return new Chart(el, {
        type: "radar",
        data: {
          labels,
          datasets: [
            {
              label: "Current Level",
              data: current,
              borderColor: "#4f46e5",
              backgroundColor: "rgba(79, 70, 229, 0.16)",
              pointBackgroundColor: "#4f46e5",
              pointBorderColor: "#ffffff",
              pointHoverRadius: 5,
              borderWidth: 2
            },
            {
              label: "Career Target",
              data: target,
              borderColor: "#0891b2",
              backgroundColor: "rgba(8, 145, 178, 0.08)",
              pointBackgroundColor: "#0891b2",
              pointBorderColor: "#ffffff",
              pointHoverRadius: 5,
              borderDash: [4, 4],
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 500 },
          plugins: {
            legend: baseLegend,
            tooltip: {
              ...baseTooltip,
              callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}/5` }
            }
          },
          scales: {
            r: {
              beginAtZero: true,
              min: 0,
              max: 5,
              ticks: { stepSize: 1, backdropColor: "transparent", color: "#64748b", font: { size: 11 } },
              grid: { color: "#e2e8f0" },
              angleLines: { color: "#e2e8f0" },
              pointLabels: { color: "#0f172a", font: { family: "Inter, sans-serif", size: 12, weight: "600" } }
            }
          }
        }
      });
    },

    barChart(canvasId, labels, current, target) {
      const el = document.getElementById(canvasId);
      if (!window.Chart || !el || !labels || !labels.length) return null;
      return new Chart(el, {
        type: "bar",
        data: {
          labels,
          datasets: [
            { label: "Current Level", data: current, backgroundColor: "#4f46e5", borderRadius: 6 },
            { label: "Target Level", data: target, backgroundColor: "#0891b2", borderRadius: 6 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 500 },
          plugins: {
            legend: baseLegend,
            tooltip: {
              ...baseTooltip,
              callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}/5` }
            }
          },
          scales: {
            y: { beginAtZero: true, max: 5, ticks: { stepSize: 1, color: "#64748b" }, grid: { color: "#f1f5f9" } },
            x: { ticks: { color: "#475569" }, grid: { display: false } }
          }
        }
      });
    },

    doughnutChart(canvasId, labels, values) {
      const el = document.getElementById(canvasId);
      if (!window.Chart || !el || !values || !values.some((v) => v > 0)) return null;
      return new Chart(el, {
        type: "doughnut",
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: ["#94a3b8", "#0891b2", "#059669", "#4f46e5", "#d97706"],
            borderColor: "#ffffff",
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "66%",
          animation: { duration: 500 },
          plugins: {
            legend: baseLegend,
            tooltip: {
              ...baseTooltip,
              callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw} task${ctx.raw === 1 ? "" : "s"}` }
            }
          }
        }
      });
    },

    lineChart(canvasId, labels, values) {
      const el = document.getElementById(canvasId);
      if (!window.Chart || !el || !labels || !labels.length) return null;
      return new Chart(el, {
        type: "line",
        data: {
          labels,
          datasets: [{
            label: "Final Skill Level",
            data: values,
            borderColor: "#4f46e5",
            backgroundColor: "rgba(79, 70, 229, 0.12)",
            pointBackgroundColor: "#4f46e5",
            pointBorderColor: "#ffffff",
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 450 },
          plugins: {
            legend: baseLegend,
            tooltip: {
              ...baseTooltip,
              callbacks: { label: (ctx) => `Final Level: ${ctx.raw}/5` }
            }
          },
          scales: {
            y: { beginAtZero: true, max: 5, ticks: { stepSize: 1, color: "#64748b" }, grid: { color: "#f1f5f9" } },
            x: { ticks: { color: "#475569", maxRotation: 30 }, grid: { display: false } }
          }
        }
      });
    }
  };
})();
