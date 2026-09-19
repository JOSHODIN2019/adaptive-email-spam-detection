(() => {
  "use strict";

  const API = {
    health: "/api/health",
    predict: "/api/predict",
    predictEml: "/api/predict/eml",
    feedback: "/api/feedback",
    events: "/api/events",
  };

  let currentPredictionId = null;

  const PANEL_TITLES = {
    "panel-analyzer": "Analyzer",
    "panel-activity": "Activity Log",
  };

  // ---------- Tabs (sidebar nav) ----------
  const tabs = Array.from(document.querySelectorAll(".side-tab"));
  const panels = Object.fromEntries(
    Array.from(document.querySelectorAll(".panel")).map((p) => [p.id, p])
  );
  const panelTitleEl = document.getElementById("panel-title");

  function activateTab(tab) {
    tabs.forEach((t) => {
      const selected = t === tab;
      t.setAttribute("aria-selected", String(selected));
      panels[t.dataset.panel].hidden = !selected;
    });
    panelTitleEl.textContent = PANEL_TITLES[tab.dataset.panel] || "";
    closeSidebarOnMobile();
    if (tab.dataset.panel === "panel-activity") loadEvents();
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => activateTab(tab));
    tab.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown" || e.key === "ArrowRight") tabs[(i + 1) % tabs.length].focus();
      if (e.key === "ArrowUp" || e.key === "ArrowLeft") tabs[(i - 1 + tabs.length) % tabs.length].focus();
    });
  });

  // ---------- Sidebar (mobile) + theme toggle ----------
  const sidebarEl = document.querySelector(".sidebar");
  const sidebarToggleBtn = document.getElementById("sidebar-toggle");
  const sidebarBackdrop = document.getElementById("sidebar-backdrop");

  function closeSidebarOnMobile() {
    sidebarEl.classList.remove("open");
    sidebarBackdrop.classList.remove("open");
    sidebarToggleBtn.setAttribute("aria-expanded", "false");
  }

  sidebarToggleBtn.addEventListener("click", () => {
    const isOpen = sidebarEl.classList.toggle("open");
    sidebarBackdrop.classList.toggle("open", isOpen);
    sidebarToggleBtn.setAttribute("aria-expanded", String(isOpen));
  });

  sidebarBackdrop.addEventListener("click", closeSidebarOnMobile);

  const themeToggleBtn = document.getElementById("theme-toggle");

  function currentEffectiveTheme() {
    const stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  themeToggleBtn.addEventListener("click", () => {
    const next = currentEffectiveTheme() === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
  });

  // ---------- Helpers ----------
  async function apiFetch(url, options) {
    const res = await fetch(url, options);
    let body;
    try {
      body = await res.json();
    } catch {
      throw new Error(`Server returned an unreadable response (HTTP ${res.status})`);
    }
    if (!res.ok && !("success" in body)) {
      throw new Error(body.detail || `Request failed (HTTP ${res.status})`);
    }
    if (body.success === false) {
      throw new Error(body.error?.message || "Request failed");
    }
    return body.data;
  }

  // A real prediction often completes in well under 50ms, too fast for the
  // loading animation to ever be perceived. This pads the visible loading
  // state up to a minimum duration so it never flashes by unnoticed, without
  // slowing down genuinely slow requests.
  async function withMinimumDelay(promise, minMs = 500) {
    const start = Date.now();
    const result = await promise;
    const elapsed = Date.now() - start;
    if (elapsed < minMs) {
      await new Promise((resolve) => setTimeout(resolve, minMs - elapsed));
    }
    return result;
  }

  function formatTimestamp(unixSeconds) {
    if (!unixSeconds) return "—";
    return new Date(unixSeconds * 1000).toLocaleString();
  }

  // ---------- Analyzer ----------
  const form = document.getElementById("predict-form");
  const bodyField = document.getElementById("body");
  const bodyError = document.getElementById("body-error");
  const analyzeBtn = document.getElementById("analyze-btn");
  const clearBtn = document.getElementById("clear-btn");
  const uploadBtn = document.getElementById("upload-btn");
  const emlFileInput = document.getElementById("eml-file");

  const resultEmpty = document.getElementById("result-empty");
  const resultLoading = document.getElementById("result-loading");
  const resultError = document.getElementById("result-error");
  const resultContent = document.getElementById("result-content");

  function setResultState(state, message) {
    resultEmpty.hidden = state !== "empty";
    resultLoading.hidden = state !== "loading";
    resultError.hidden = state !== "error";
    resultContent.hidden = state !== "content";
    if (state === "error") resultError.textContent = message;
  }

  function displayLabel(labelName) {
    return labelName === "ham" ? "Legitimate" : "Spam";
  }

  function renderPrediction(data) {
    currentPredictionId = data.prediction_id;

    const staticBadge = document.getElementById("static-badge");
    staticBadge.textContent = displayLabel(data.static_prediction.label_name);
    staticBadge.className = `result-badge ${data.static_prediction.label_name}`;

    const adaptiveBadge = document.getElementById("adaptive-badge");
    adaptiveBadge.textContent = displayLabel(data.adaptive_prediction.label_name);
    adaptiveBadge.className = `result-badge ${data.adaptive_prediction.label_name}`;

    document.getElementById("disclaimer-text").textContent = data.disclaimer;
    document.getElementById("feedback-status").textContent = "";
    document.getElementById("feedback-status").className = "feedback-status";
    resetTrainingAnimation();
    setFeedbackButtonsEnabled(true);

    setResultState("content");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = document.getElementById("subject").value;
    const body = bodyField.value;

    if (!body.trim()) {
      bodyError.hidden = false;
      bodyField.focus();
      return;
    }
    bodyError.hidden = true;

    analyzeBtn.disabled = true;
    analyzeBtn.classList.add("is-loading");
    setResultState("loading");
    try {
      const data = await withMinimumDelay(apiFetch(API.predict, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, body }),
      }));
      renderPrediction(data);
    } catch (err) {
      setResultState("error", err.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.classList.remove("is-loading");
    }
  });

  clearBtn.addEventListener("click", () => {
    form.reset();
    bodyError.hidden = true;
    setResultState("empty");
    currentPredictionId = null;
  });

  uploadBtn.addEventListener("click", async () => {
    const file = emlFileInput.files[0];
    if (!file) {
      setResultState("error", "Choose a .eml file first.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    uploadBtn.disabled = true;
    uploadBtn.classList.add("is-loading");
    setResultState("loading");
    try {
      const data = await withMinimumDelay(apiFetch(API.predictEml, { method: "POST", body: formData }));
      document.getElementById("subject").value = data.parsed_subject || "";
      renderPrediction(data);
    } catch (err) {
      setResultState("error", err.message);
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.classList.remove("is-loading");
    }
  });

  // ---------- Feedback ----------
  const feedbackSpamBtn = document.getElementById("feedback-spam");
  const feedbackLegitBtn = document.getElementById("feedback-legit");
  const feedbackStatusEl = document.getElementById("feedback-status");
  const feedbackTrainingEl = document.getElementById("feedback-training");
  const trainingDotsEl = document.querySelector("#feedback-training .training-dots");
  const trainingCheckmarkEl = document.querySelector("#feedback-training .training-checkmark");
  const trainingLabelEl = document.getElementById("training-label");

  function setFeedbackButtonsEnabled(enabled) {
    feedbackSpamBtn.disabled = !enabled;
    feedbackLegitBtn.disabled = !enabled;
  }

  function resetTrainingAnimation() {
    feedbackTrainingEl.hidden = true;
    feedbackTrainingEl.classList.remove("success");
    trainingDotsEl.hidden = false;
    trainingCheckmarkEl.hidden = true;
    trainingLabelEl.textContent = "Teaching the adaptive model…";
  }

  async function submitFeedback(correctedLabel) {
    if (!currentPredictionId) return;
    setFeedbackButtonsEnabled(false);
    feedbackStatusEl.className = "feedback-status";
    feedbackStatusEl.textContent = "";
    resetTrainingAnimation();
    feedbackTrainingEl.hidden = false;
    try {
      const data = await apiFetch(API.feedback, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prediction_id: currentPredictionId, corrected_label: correctedLabel }),
      });

      // Play a brief success transition (checkmark + glow) before settling
      // into the plain confirmation text.
      trainingDotsEl.hidden = true;
      trainingCheckmarkEl.hidden = false;
      trainingLabelEl.textContent = "Model updated";
      feedbackTrainingEl.classList.add("success");
      await new Promise((resolve) => setTimeout(resolve, 700));

      resetTrainingAnimation();
      feedbackStatusEl.className = "feedback-status success";
      feedbackStatusEl.textContent = data.message;
    } catch (err) {
      resetTrainingAnimation();
      feedbackStatusEl.className = "feedback-status error";
      feedbackStatusEl.textContent = err.message;
      setFeedbackButtonsEnabled(true);
    }
  }

  feedbackSpamBtn.addEventListener("click", () => submitFeedback("spam"));
  feedbackLegitBtn.addEventListener("click", () => submitFeedback("legitimate"));

  // ---------- Activity Log ----------
  const eventFilter = document.getElementById("event-filter");
  const refreshEventsBtn = document.getElementById("refresh-events-btn");

  async function loadEvents() {
    const eventsEmpty = document.getElementById("events-empty");
    const eventsList = document.getElementById("events-list");
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (eventFilter.value) params.set("event_type", eventFilter.value);
      const data = await apiFetch(`${API.events}?${params.toString()}`);
      const events = data.events || [];
      eventsEmpty.hidden = events.length > 0;
      eventsList.hidden = events.length === 0;
      eventsList.innerHTML = "";
      events.slice().reverse().forEach((evt) => {
        const li = document.createElement("li");
        const detail = evt.body_preview || evt.corrected_label || evt.model_version || "";

        const typeTag = document.createElement("span");
        typeTag.className = `event-type-tag ${evt.stream}`;
        typeTag.textContent = evt.stream;

        const timeSpan = document.createElement("span");
        timeSpan.className = "event-time";
        timeSpan.textContent = formatTimestamp(evt.timestamp);

        const detailSpan = document.createElement("span");
        detailSpan.textContent = detail;

        li.append(typeTag, timeSpan, detailSpan);
        eventsList.appendChild(li);
      });
    } catch (err) {
      eventsEmpty.hidden = false;
      eventsEmpty.querySelector("p").textContent = `Failed to load events: ${err.message}`;
    }
  }

  eventFilter.addEventListener("change", loadEvents);
  refreshEventsBtn.addEventListener("click", loadEvents);

  // ---------- Init ----------
  setResultState("empty");
})();
