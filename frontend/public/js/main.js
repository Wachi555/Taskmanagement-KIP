import { setupAudioRecorder } from './audio.js';

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const path = window.location.pathname;

    // Nur Dashboard (oder weitere Full-View-Seiten) per JS rendern:
    if (path === "/dashboard" || path.startsWith("/patient/")) {
      await window.patientStore.loadFromBackend();
      const patients = window.patientStore.getAllDetailed();
      renderPatientSidebar(patients);
    }
  } catch (err) {
    console.error("Fehler beim Laden der Patienten:", err);
  }

  // Diese Setups laufen überall und finden deine <button.move-to-active>
  setupAnalyzeButton();
  setupSidebarSearch();
  setupMoveButtons();
  setupFullViewSearch();
  setupAudioRecorder();
  setupDeleteButtons();
});

function setupDeleteButtons() {
  document
    .getElementById('all-patient-list')
    .addEventListener('click', async e => {
      const btn = e.target.closest('.delete-patient');
      if (!btn) return;
      const id = btn.dataset.id;
      if (!confirm('Soll dieser Patient wirklich gelöscht werden?')) return;

      try {
        const resp = await fetch(`/patient/${id}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error(await resp.text());
        // Zeile entfernen
        btn.closest('li.list-group-item').remove();
      } catch (err) {
        console.error('Löschen fehlgeschlagen', err);
        alert('Fehler beim Löschen: ' + err.message);
      }
    });
}

function setupFullViewSearch() {
  // Suchfunktion für "Alle Patienten"
  const searchAll = document.getElementById('search-all');
  if (searchAll) {
    searchAll.addEventListener('input', () => {
      filterPatientList(searchAll.value, '.col-md-6.border-end .list-group-item:not(.text-muted)');
    });
  }

  // Suchfunktion für "Wartende Patienten"
  const searchWaiting = document.getElementById('search-waiting');
  if (searchWaiting) {
    searchWaiting.addEventListener('input', () => {
      filterPatientList(searchWaiting.value, '#pane-waiting .list-group-item:not(.text-muted)');
    });
  }

  // Suchfunktion für "Aktive Patienten"
  const searchActive = document.getElementById('search-active');
  if (searchActive) {
    searchActive.addEventListener('input', () => {
      filterPatientList(searchActive.value, '#pane-active .list-group-item:not(.text-muted)');
    });
  }
}

function filterPatientList(searchTerm, itemSelector) {
  const term = searchTerm.toLowerCase();
  const items = document.querySelectorAll(itemSelector);

  let anyVisible = false;
  items.forEach(item => {
    const nameElement = item.querySelector('.patient-name');
    const name = nameElement?.textContent.toLowerCase() || '';
    
    if (term && !name.includes(term)) {
      item.style.display = 'none';
    } else {
      item.style.display = '';
      anyVisible = true;
    }
  });

  // Falls keine Ergebnisse: "Keine Patienten gefunden" anzeigen
  const container = items[0]?.closest('.list-group');
  if (!container) return;

  const existingNoResults = container.querySelector('.no-results');
  if (!anyVisible && !existingNoResults) {
    const noResults = document.createElement('li');
    noResults.className = 'list-group-item text-muted text-center no-results';
    noResults.textContent = 'Keine Patienten gefunden';
    container.appendChild(noResults);
  } else if (anyVisible && existingNoResults) {
    existingNoResults.remove();
  }
}



function getCurrentPatientId() {
  const match = window.location.pathname.match(/\/patient\/(\d+)/);
  return match ? parseInt(match[1], 10) : null;
}

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

async function processInput() {
  const text = document.getElementById("inputText").value.trim();
  if (!text) {
    showError("Bitte geben Sie einen Text ein");
    return;
  }

  const patientId = getCurrentPatientId();
  if (!patientId) {
    showError("Kein Patient ausgewählt.");
    return;
  }

  showLoading(true);
  try {
    const result = await window.patientStore.analyze(patientId, text);
    displayResults(result);
  } catch (error) {
    showError("Analyse fehlgeschlagen: " + error.message);
    throw error;
  } finally {
    showLoading(false);
  }
}

function renderPatientSidebar(patients) {
  const waitingList = document.querySelector("#pane-waiting ul.list-group");
  const activeList = document.querySelector("#active-patient-list");
  if (!waitingList || !activeList) return;

  // Listen leeren
  waitingList.innerHTML = "";
  activeList.innerHTML = "";

  // Platzhalter
  const noWaiting = document.createElement("li");
  noWaiting.className = "list-group-item text-muted text-center";
  noWaiting.textContent = "Keine wartenden Patienten";

  const noActive = document.createElement("li");
  noActive.className = "list-group-item text-muted text-center";
  noActive.textContent = "Keine aktiven Patienten";

  // 1. Patienten in zwei Gruppen aufteilen
  const waitingPatients = patients.filter(p => p.is_waiting);
  const activePatients = patients.filter(p => p.in_treatment);

  // 2. Sortierfunktion (identisch zur Serverseitigen)
  const sortByTriage = (a, b) => {
    const triageA = a.last_triage_level ?? 5; // Fallback für undefined
    const triageB = b.last_triage_level ?? 5;
    return triageA - triageB; // Aufsteigend: 1 (höchste Prio) zuerst
  };

  // 3. Gruppen sortieren
  waitingPatients.sort(sortByTriage);
  activePatients.sort(sortByTriage);

  // 4. Patienten rendern
  const renderPatient = (p, isWaiting) => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center";
    li.innerHTML = `
      <a 
        href="${isWaiting 
          ? `/patient/${p.id}/overview` 
          : `/patient/${p.id}`}" 
        class="text-decoration-none patient-name"
      >
        ${p.first_name} ${p.last_name}
      </a>
      <span class="d-flex align-items-center">
        <!-- Triage-Indikator -->
        <span class="triage-indicator me-2">
          <span class="triage-circle level-${p.last_triage_level} active"></span>
        </span>
        <!-- Move-Button -->
        ${isWaiting ? `
          <button
            class="btn btn-icon-only move-to-active"
            type="button"
            data-id="${p.id}"
            data-name="${p.first_name} ${p.last_name}"
            data-triage="${p.last_triage_level}"
          >
            <i class="bi bi-arrow-right-circle"></i>
          </button>
        ` : ``}
      </span>
    `;
    return li;
  };


  // Wartende Patienten
  if (waitingPatients.length > 0) {
    waitingPatients.forEach(p => waitingList.appendChild(renderPatient(p, true)));
  } else {
    waitingList.appendChild(noWaiting);
  }

  // Aktive Patienten
  if (activePatients.length > 0) {
    activePatients.forEach(p => activeList.appendChild(renderPatient(p, false)));
  } else {
    activeList.appendChild(noActive);
  }
}

function setupMoveButtons() {
  const waitingPane = document.getElementById("pane-waiting");
  const activeList = document.getElementById("active-patient-list");

  if (!waitingPane || !activeList) return;

  waitingPane.addEventListener("click", async (e) => {
    const btn = e.target.closest(".move-to-active");
    if (!btn) return;

    const id     = btn.getAttribute("data-id");
    const name   = btn.getAttribute("data-name");
    const triage = btn.getAttribute("data-triage");
    const listItem = btn.closest("li");
    if (!id || !listItem) return;

    try {
      // 1) Backend-Call: Status von wartend (1) → in Behandlung (2)
      const resp = await fetch(
        `http://localhost:8000/patient/update_status/${id}/2`,
        { method: 'GET' }
      );
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Status ${resp.status}: ${txt}`);
      }

      // 2) Client-seitig verschieben
      const hint = activeList.querySelector("li.text-muted");
      if (hint) hint.remove();

      const already = [...activeList.querySelectorAll("a")]
        .some(a => a.textContent.trim() === name);
      if (!already) {
        const href = window.location.pathname.startsWith("/coordination")
          ? `/patient/${id}`
          : `/patient/${id}/overview`;

        const newItem = document.createElement("li");
        newItem.className = "list-group-item d-flex justify-content-between align-items-center";
        newItem.innerHTML = `
          <a href="${href}" class="text-decoration-none patient-name">${name}</a>
          <span class="triage-indicator ms-2">
            <span class="triage-circle level-${triage} active"></span>
          </span>
        `;
        activeList.appendChild(newItem);
      }

      // 3) Alt-Item entfernen & evtl. Hinweis wieder anfügen
      listItem.remove();
      const remaining = waitingPane.querySelectorAll("ul.list-group > li:not(.text-muted)");
      if (remaining.length === 0) {
        const noRes = document.createElement("li");
        noRes.className = "list-group-item text-muted text-center";
        noRes.textContent = "Keine wartenden Patienten";
        waitingPane.querySelector("ul.list-group").appendChild(noRes);
      }

    } catch (err) {
      console.error('Fehler beim Verschieben:', err);
      alert('Patient konnte nicht verschoben werden:\n' + err.message);
    }
  });
}

function setupSidebarSearch() {
  const searchInput = document.getElementById("sidebar-search");
  const tabList     = document.getElementById("sidebarTabs");
  if (!searchInput) return;

  const filterSidebar = () => {
    const query = searchInput.value.trim().toLowerCase();
    // nur das aktive Tab-Pane greifen
    const activePane = document.querySelector(
      "#sidebarTabsContent .tab-pane.active"
    );
    if (!activePane) return;

    const ul = activePane.querySelector("ul.list-group");
    if (!ul) return;

    // alte No-Results entfernen
    ul.querySelectorAll(".no-results").forEach(el => el.remove());

    // alle echten Patient-li sammeln
    const items = Array.from(ul.children)
      .filter(li => li.classList.contains("list-group-item"));

    let anyVisible = false;
    items.forEach(li => {
      const a    = li.querySelector("a.patient-name");
      const name = (a?.textContent || "").trim().toLowerCase();
      if (query && !name.includes(query)) {
        li.style.display = "none";
      } else {
        li.style.display = "";
        anyVisible = true;
      }
    });

    // wenn nichts sichtbar ist, eine entsprechende Zeile anhängen
    if (!anyVisible) {
      const noRes = document.createElement("li");
      noRes.className = "list-group-item text-center text-muted no-results";
      noRes.textContent = "Keine Patienten gefunden.";
      ul.appendChild(noRes);
    }
  };

  // bei jeder Eingabe filtern
  searchInput.addEventListener("input", filterSidebar);
  // beim Tab-Wechsel auch filtern (Suche bleibt im Feld erhalten)
  tabList?.addEventListener("shown.bs.tab", filterSidebar);
}

function displayResults(result) {
  resetResults();

  // Diagnosen: { name: "xyz" } → ["xyz"]
  const diagnoses = Array.isArray(result.diagnoses)
    ? result.diagnoses.map(d => d.name)
    : toArray(result.diagnoses);
  document.getElementById("diagnoses").textContent =
    diagnoses.length ? diagnoses.join(", ") : "–";

  // Untersuchungen: als Liste mit Priorität-Badge
  const examsEl = document.getElementById("examinations");
  examsEl.innerHTML = "";
  if (Array.isArray(result.examinations) && result.examinations.length > 0) {
    result.examinations.forEach(e => {
      const li = document.createElement("li");
      li.innerHTML = `${e.name} <span class="badge bg-secondary">${e.priority}</span>`;
      examsEl.appendChild(li);
    });
  } else {
    examsEl.innerHTML = "<li>–</li>";
  }

  // Behandlungen
  const treatments = toArray(result.treatments);
  document.getElementById("treatments").textContent =
    treatments.length ? treatments.join(", ") : "–";

  // Experten
  const experts = toArray(result.experts);
  document.getElementById("experts").textContent =
    experts.length ? experts.join(", ") : "–";

  // Allergien (mit Fallback auf initial aus Template)
  // const allergiesEl = document.getElementById("allergies");
  const newAllergies = toArray(result.allergies);
  // if (newAllergies.length) {
  document.getElementById("allergies").textContent =
    newAllergies.length ? newAllergies.join(", "):"-";
  // } else {
    // const fallback = allergiesEl.dataset.initial;
    // allergiesEl.textContent =
      // fallback && fallback.trim() !== "" ? fallback : "–";
  // }
}


function resetResults() {
  document.getElementById("diagnoses").textContent = "–";
  document.getElementById("examinations").innerHTML = "";
  document.getElementById("treatments").textContent = "–";
  document.getElementById("experts").textContent = "–";
  document.getElementById("allergies").textContent = "–";
}

// Hilfsfunktion: wandelt Strings wie "A, B" in ["A", "B"]
function toArray(input) {
  if (Array.isArray(input)) return input;
  if (typeof input === "string") {
    return input.split(",").map(s => s.trim()).filter(Boolean);
  }
  return [];
}



function displayTriageLevel(triageLevel) {
  const triageContainer = document.getElementById("triageIndicator");
  triageContainer.innerHTML = "";
  const circle = document.createElement("div");
  circle.className = `triage-circle level-${triageLevel} active`;
  circle.title = `Triagestufe ${triageLevel}`;
  triageContainer.appendChild(circle);

  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong class="me-2">Triagestufe:</strong> ${triageLevel}`;
  document.getElementById("resultData").appendChild(li);
}

function displayExams(exams) {
  const ul = document.getElementById("resultData");
  const li = document.createElement("li");
  li.className = "list-group-item d-block";
  const label = document.createElement("strong");
  label.className = "d-block mb-2";
  label.textContent = "Untersuchungen:";
  li.appendChild(label);

  const examsList = document.createElement("ul");
  examsList.className = "list-group list-group-flush";

  exams.forEach((e, idx) => {
    const item = document.createElement("li");
    item.className = "list-group-item d-flex justify-content-between align-items-center";

    const wrapper = document.createElement("div");
    wrapper.className = "form-check";

    const checkbox = document.createElement("input");
    checkbox.className = "form-check-input";
    checkbox.type = "checkbox";
    const safeId = `exam-${idx}`;
    checkbox.id = safeId;

    const chkLabel = document.createElement("label");
    chkLabel.className = "form-check-label";
    chkLabel.htmlFor = safeId;
    chkLabel.textContent = e.name;

    wrapper.appendChild(checkbox);
    wrapper.appendChild(chkLabel);

    const badge = document.createElement("span");
    badge.className = "badge bg-secondary";
    badge.textContent = e.priority;

    item.appendChild(wrapper);
    item.appendChild(badge);
    examsList.appendChild(item);
  });

  li.appendChild(examsList);
  ul.appendChild(li);
}

function displayExperts(experts) {
  const ul = document.getElementById("resultData");
  const li = document.createElement("li");
  li.className = "list-group-item";
  const list = Array.isArray(experts) 
    ? experts 
    : (experts || "").split(",").map(s=>s.trim()).filter(Boolean);
  li.innerHTML = `<strong class="me-3">Experten:</strong> ${list.length ? list.join(", ") : "–"}`;
  ul.appendChild(li);
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
