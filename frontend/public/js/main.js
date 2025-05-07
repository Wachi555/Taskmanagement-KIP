// public/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  // Sidebar ein-/ausblenden
  setupSidebarToggle();
  
  // Analyse-Button Event
  setupAnalyzeButton();
  
  // Event-Delegation für alle Ausklapp-Buttons
  setupExamToggle();
});

// Sidebar-Toggle Funktion
function setupSidebarToggle() {
  const toggleBtn = document.getElementById("toggle-sidebar");
  const sidebar = document.getElementById("sidebar");
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
      localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Sidebar-Status aus localStorage wiederherstellen
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
      sidebar.classList.add("collapsed");
    }
  }
}

// Analyse-Button Setup
function setupAnalyzeButton() {
  const processBtn = document.getElementById("process-btn");
  if (processBtn) {
    processBtn.addEventListener("click", async () => {
      try {
        await processInput();
      } catch (error) {
        console.error("Analyse fehlgeschlagen:", error);
        showError(error.message);
      }
    });
  }
}

// Ausklappfunktion für Untersuchungen
function setupExamToggle() {
  const resultData = document.getElementById("resultData");
  if (resultData) {
    resultData.addEventListener("click", (e) => {
      const toggleBtn = e.target.closest(".toggle-exams");
      if (!toggleBtn) return;
      
      const container = toggleBtn.closest(".exams-container");
      const examsList = container.querySelector(".exams-list");
      const icon = toggleBtn.querySelector("i");
      
      toggleExamsList(examsList, icon);
    });
  }
}

// Untersuchungsliste ein-/ausblenden
function toggleExamsList(examsList, icon) {
  const isHidden = examsList.style.display === "none";
  
  examsList.style.display = isHidden ? "block" : "none";
  icon.classList.toggle("bi-chevron-down", !isHidden);
  icon.classList.toggle("bi-chevron-up", isHidden);
  
  // Animation für flüssiges Ein-/Ausblenden
  examsList.style.overflow = "hidden";
  examsList.style.transition = "max-height 0.3s ease, opacity 0.2s ease";
  examsList.style.maxHeight = isHidden ? `${examsList.scrollHeight}px` : "0";
  examsList.style.opacity = isHidden ? "1" : "0";
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
  
  // Patientendaten
  displayPatientData(data.data);
  
  // Auswertung
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
  
  // Triage-Kreise
  [1, 2, 3, 4, 5].forEach(level => {
    const circle = document.createElement("div");
    circle.className = `triage-circle level-${level} ${level === triageLevel ? 'active' : ''}`;
    circle.title = `Triagestufe ${level}`;
    triageContainer.appendChild(circle);
  });
  
  // Triage-Text
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
      ${exams.length ? 
        `<button class="btn btn-sm btn-outline-secondary toggle-exams">
          <i class="bi bi-chevron-down"></i>
        </button>` : '–'}
    </div>
    ${exams.length ? 
      `<ul class="exams-list list-group list-group-flush mt-2" style="display:none; max-height:0; opacity:0;">
        ${exams.map(exam => `<li class="list-group-item">${exam}</li>`).join('')}
      </ul>` : ''}
  `;
  
  resultUl.appendChild(li);
}

// Experten anzeigen
function displayExperts(experts) {
  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong>Experten:</strong> ${experts.length ? experts.join(", ") : "–"}`;
  document.getElementById("resultData").appendChild(li);
}

// Ladeanzeige
function showLoading(show) {
  const spinner = document.getElementById("loading-spinner");
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