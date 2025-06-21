import { setupAudioRecorder } from './audio.js';

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const path = window.location.pathname;

    // Nur Dashboard (oder weitere Full-View-Seiten) per JS rendern:
    if (path === "/dashboard") {
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
});



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

    const a = document.createElement("a");
    a.href = isWaiting ? `/patient/${p.id}/overview` : `/patient/${p.id}`;
    a.className = "text-decoration-none patient-name";
    a.textContent = `${p.first_name} ${p.last_name}`;

    const triageSpan = document.createElement("span");
    triageSpan.className = "triage-indicator ms-2";
    triageSpan.innerHTML = `<span class="triage-circle level-${p.last_triage_level ?? '-'} active"></span>`;

    li.appendChild(a);
    li.appendChild(triageSpan);
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

function setupFullViewSearch() {
  const all = document.querySelector("#search-all input");
  const waiting = document.querySelector("#search-waiting input");
  const active = document.querySelector("#search-active input");

  if (all) {
    all.addEventListener("input", () => {
      const filter = all.value.trim().toLowerCase();
      document.querySelectorAll(".col-md-6.border-end ul.list-group > li").forEach(li => {
        const name = (li.querySelector(".patient-name") || li).textContent.trim().toLowerCase();
        li.style.display = name.includes(filter) ? "" : "none";
      });
    });
  }

  if (waiting) {
    waiting.addEventListener("input", () => {
      const filter = waiting.value.trim().toLowerCase();
      document.querySelectorAll("#pane-waiting ul.list-group > li").forEach(li => {
        const name = (li.querySelector(".patient-name") || li).textContent.trim().toLowerCase();
        li.style.display = name.includes(filter) ? "" : "none";
      });
    });
  }

  if (active) {
    active.addEventListener("input", () => {
      const filter = active.value.trim().toLowerCase();
      document.querySelectorAll("#active-patient-list > li").forEach(li => {
        const name = (li.querySelector(".patient-name, a") || li).textContent.trim().toLowerCase();
        li.style.display = name.includes(filter) ? "" : "none";
      });
    });
  }
}

function displayResults(result) {
  resetResults();
  displayDiagnosis(result.diagnosis);
  displayTriageLevel(result.triage);
  displayExams(result.exams);
  displayExperts(result.experts);
}

function resetResults() {
  document.getElementById("resultData").innerHTML = "";
}

function displayDiagnosis(diagnosis) {
  if (!diagnosis?.length) return;
  const ul = document.getElementById("resultData");
  const names = diagnosis.map(d => d.name).join(", ");
  const li = document.createElement("li");
  li.className = "list-group-item";
  li.innerHTML = `<strong class="me-2">Mögliche Diagnosen:</strong> ${names}`;
  ul.appendChild(li);
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
  const li = document.createElement("li");
  li.className = "list-group-item d-block";
  li.innerHTML = `
    <strong class="d-block mb-2">Experten:</strong>
    <ul class="mt-1 ms-3">
      ${experts.length ? experts.map(e => `<li>${e}</li>`).join("") : "<li>–</li>"}
    </ul>
  `;
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
