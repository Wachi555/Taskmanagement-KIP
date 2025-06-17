document.addEventListener("DOMContentLoaded", () => {
  setupSidebarToggle();
  setupAnalyzeButton();
  setupSidebarSearch();
  setupMoveButtons();
});

// Sidebar ein-/ausblenden
function setupSidebarToggle() {
  const toggleBtn = document.getElementById("toggle-sidebar");
  const sidebar = document.getElementById("sidebar");
  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"));
  });

  if (localStorage.getItem("sidebarCollapsed") === "true") {
    sidebar.classList.add("collapsed");
  }
}

// Analyse-Button-Setup
function setupAnalyzeButton() {
  const processBtn = document.getElementById("process-btn");
  if (!processBtn) return;

  processBtn.addEventListener("click", async () => {
    try {
      await processInput();
    } catch (error) {
      console.error("Analyse fehlgeschlagen:", error);
      showError(error.message);
    }
  });
}

// Patienten verschieben (Wartend → In Behandlung)
function setupMoveButtons() {
  const waitingPane = document.getElementById("pane-waiting") || document.querySelector(".waiting-patients");
  const activePane = document.getElementById("pane-main") || document.querySelector(".active-patients");

  if (!waitingPane || !activePane) return;

  waitingPane.addEventListener("click", (e) => {
    const btn = e.target.closest(".move-to-active");
    if (!btn) return;

    const name = btn.getAttribute("data-name");
    const listItem = btn.closest("li");

    if (!name || !listItem) return;

    // Entferne ggf. alten Hinweis in aktiver Liste
    const activeList = activePane.querySelector("ul.list-group");
    const hint = activeList.querySelector("li.text-muted");
    if (hint) hint.remove();

    // Prüfen ob Patient bereits in aktiver Liste existiert
    const alreadyExists = [...activeList.querySelectorAll("a")].some(a => a.textContent === name);
    if (alreadyExists) return;

    // Hinzufügen zur aktiven Liste
    const newItem = document.createElement("li");
    newItem.className = "list-group-item";
    newItem.innerHTML = `<a href="/patient/${encodeURIComponent(name)}" class="text-decoration-none patient-name">${name}</a>`;
    activeList.appendChild(newItem);

    // Entfernen aus Warteliste
    listItem.remove();

    // Falls keine Patienten mehr wartend → Hinweis einblenden
    const remaining = waitingPane.querySelectorAll("li.list-group-item:not(.text-muted)");
    if (remaining.length === 0) {
      const noRes = document.createElement("li");
      noRes.className = "list-group-item text-center text-muted";
      noRes.textContent = "Keine wartenden Patienten.";
      waitingPane.querySelector("ul.list-group").appendChild(noRes);
    }
  });
}

// Sidebar-Suche
function setupSidebarSearch() {
  const searchInput = document.getElementById("sidebar-search");
  const tabList = document.getElementById("sidebarTabs");
  if (!searchInput || !tabList) return;

  function filterSidebarList() {
    const filter = searchInput.value.trim().toLowerCase();
    const activePane = document.querySelector(".tab-pane.show.active") || document.querySelector(".waiting-patients, .active-patients");
    if (!activePane) return;

    const listItems = activePane.querySelectorAll("li.list-group-item");
    let anyVisible = false;

    activePane.querySelectorAll(".no-results").forEach(e => e.remove());

    listItems.forEach(li => {
      if (li.classList.contains("no-results")) return;

      const nameEl = li.querySelector(".patient-name, a");
      const text = nameEl ? nameEl.textContent.trim().toLowerCase() : "";

      if (filter === "" || text.includes(filter)) {
        li.style.display = "";
        anyVisible = true;
      } else {
        li.style.display = "none";
      }
    });

    if (!anyVisible) {
      const noRes = document.createElement("li");
      noRes.className = "list-group-item text-center text-muted no-results";
      noRes.textContent = "Keine Patienten gefunden.";
      activePane.querySelector(".list-group").appendChild(noRes);
    }
  }

  searchInput.addEventListener("input", filterSidebarList);
  tabList.addEventListener("shown.bs.tab", () => {
    searchInput.value = "";
    filterSidebarList();
  });
}

// Analyse
async function processInput() {
  const text = document.getElementById("inputText").value.trim();
  if (!text) {
    showError("Bitte geben Sie einen Text ein");
    return;
  }

  showLoading(true);
  try {
    const response = await fetch("/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!response.ok) throw new Error(`Serverfehler: ${response.status}`);

    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(error.message);
    throw error;
  } finally {
    showLoading(false);
  }
}

function displayResults(data) {
  resetResults();
  displayPatientData(data.data);
  displayTriageLevel(data.triage);
  displayExams(data.exams);
  displayExperts(data.experts);
}

function resetResults() {
  document.getElementById("patientData").innerHTML = "";
  document.getElementById("resultData").innerHTML = "";
  document.getElementById("triageIndicator").innerHTML = "";
}

function displayPatientData(patientData) {
  const patientUl = document.getElementById("patientData");
  Object.entries(patientData).forEach(([key, val]) => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>${key}:</strong> ${val}`;
    patientUl.appendChild(li);
  });
}

function displayTriageLevel(triageLevel) {
  const triageContainer = document.getElementById("triageIndicator");
  const resultUl = document.getElementById("resultData");

  [1, 2, 3, 4, 5].forEach(level => {
    const circle = document.createElement("div");
    circle.className = `triage-circle level-${level} ${level === triageLevel ? 'active' : ''}`;
    circle.title = `Triagestufe ${level}`;
    triageContainer.appendChild(circle);
  });

  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong>Triagestufe:</strong> ${triageLevel}`;
  resultUl.appendChild(li);
}

function displayExams(exams) {
  const resultUl = document.getElementById("resultData");
  const li = document.createElement("li");
  li.className = "list-group-item exams-container";

  li.innerHTML = `
    <div class="d-flex justify-content-between align-items-center">
      <strong>Untersuchungen:</strong>
      <button id="toggleExams" class="btn btn-sm btn-outline-secondary" aria-expanded="false">
        <i class="bi bi-chevron-down"></i>
      </button>
    </div>
    <ul id="examsList" class="list-group list-group-flush mt-2"></ul>
  `;
  resultUl.appendChild(li);

  const examsList = li.querySelector("#examsList");
  exams.forEach((exam, idx) => {
    const item = document.createElement("li");
    item.className = "list-group-item d-flex align-items-center";
    item.innerHTML = `
      <input class="form-check-input me-2" type="checkbox" id="exam-${idx}" />
      <label class="form-check-label flex-grow-1" for="exam-${idx}">
        ${exam}
      </label>
    `;
    examsList.appendChild(item);
  });

  setupExamToggle();
}

function setupExamToggle() {
  const btn = document.getElementById("toggleExams");
  const list = document.getElementById("examsList");
  if (!btn || !list) return;

  btn.addEventListener("click", () => {
    const expanded = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!expanded));
    list.classList.toggle("open");
  });
}

function displayExperts(experts) {
  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong>Experten:</strong> ${experts.length ? experts.join(", ") : "–"}`;
  document.getElementById("resultData").appendChild(li);
}

function showLoading(show) {
  const spinner = document.getElementById("loading-spinner");
  const processBtn = document.getElementById("process-btn");
  if (spinner) spinner.style.display = show ? "inline-block" : "none";
  if (processBtn) processBtn.disabled = show;
}

function showError(message) {
  const resultUl = document.getElementById("resultData");
  resultUl.innerHTML = `
    <li class="list-group-item text-danger">
      <strong>Fehler:</strong> ${message}
    </li>
  `;
}