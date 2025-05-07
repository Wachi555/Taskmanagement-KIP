// public/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  setupSidebarToggle();
  setupAnalyzeButton();
  // setupExamToggle wird in displayExams aufgerufen,
  // sobald der Button im DOM ist.
});

// Sidebar ein-/ausblenden
function setupSidebarToggle() {
  const toggleBtn = document.getElementById("toggle-sidebar");
  const sidebar = document.getElementById("sidebar");
  
  if (!toggleBtn || !sidebar) return;
  
  // Klick-Handler
  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    localStorage.setItem(
      'sidebarCollapsed',
      sidebar.classList.contains('collapsed')
    );
  });
  
  // Status beim Laden wiederherstellen
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
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

// Hauptanalysefunktion
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
    if (!response.ok) {
      throw new Error(`Serverfehler: ${response.status}`);
    }
    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(error.message);
    throw error;
  } finally {
    showLoading(false);
  }
}

// Ergebnisse anzeigen
function displayResults(data) {
  resetResults();
  displayPatientData(data.data);
  displayTriageLevel(data.triage);
  displayExams(data.exams);
  displayExperts(data.experts);
}

// Ergebnisse zurücksetzen
function resetResults() {
  document.getElementById("patientData").innerHTML = "";
  document.getElementById("resultData").innerHTML = "";
  document.getElementById("triageIndicator").innerHTML = "";
}

// Patientendaten anzeigen
function displayPatientData(patientData) {
  const patientUl = document.getElementById("patientData");
  Object.entries(patientData).forEach(([key, val]) => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>${key}:</strong> ${val}`;
    patientUl.appendChild(li);
  });
}

// Triagestufe anzeigen
function displayTriageLevel(triageLevel) {
  const triageContainer = document.getElementById("triageIndicator");
  const resultUl = document.getElementById("resultData");

  // Kreise
  [1,2,3,4,5].forEach(level => {
    const circle = document.createElement("div");
    circle.className = `triage-circle level-${level} ${
      level === triageLevel ? 'active' : ''
    }`;
    circle.title = `Triagestufe ${level}`;
    triageContainer.appendChild(circle);
  });

  // Text
  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong>Triagestufe:</strong> ${triageLevel}`;
  resultUl.appendChild(li);
}

// Untersuchungen anzeigen
function displayExams(exams) {
  const resultUl = document.getElementById("resultData");
  const li = document.createElement("li");
  li.className = "list-group-item exams-container";

  li.innerHTML = `
    <div class="d-flex justify-content-between align-items-center">
      <strong>Untersuchungen:</strong>
      <button id="toggleExams"
              class="btn btn-sm btn-outline-secondary"
              aria-expanded="false">
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
      <input class="form-check-input me-2"
             type="checkbox"
             id="exam-${idx}" />
      <label class="form-check-label flex-grow-1"
             for="exam-${idx}">
        ${exam}
      </label>
    `;
    examsList.appendChild(item);
  });

  // Toggle-Listener erst nach DOM-Befüllung
  setupExamToggle();
}

// Toggle-Button für Untersuchungen
function setupExamToggle() {
  const btn  = document.getElementById("toggleExams");
  const list = document.getElementById("examsList");
  if (!btn || !list) return;

  btn.addEventListener("click", () => {
    const expanded = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!expanded));
    list.classList.toggle("open");
  });
}

// Experten anzeigen
function displayExperts(experts) {
  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `
    <strong>Experten:</strong>
    ${experts.length ? experts.join(", ") : "–"}
  `;
  document.getElementById("resultData").appendChild(li);
}

// Ladeanzeige
function showLoading(show) {
  const spinner    = document.getElementById("loading-spinner");
  const processBtn = document.getElementById("process-btn");
  if (spinner) spinner.style.display = show ? "inline-block" : "none";
  if (processBtn) processBtn.disabled = show;
}

// Fehlermeldung anzeigen
function showError(message) {
  const resultUl = document.getElementById("resultData");
  resultUl.innerHTML = `
    <li class="list-group-item text-danger">
      <strong>Fehler:</strong> ${message}
    </li>
  `;
}
