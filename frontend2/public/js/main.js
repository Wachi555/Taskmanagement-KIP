// public/js/main.js

document.addEventListener("DOMContentLoaded", () => {
  // Sidebar-Toggle
  const toggleBtn = document.getElementById("toggle-sidebar");
  const sidebar   = document.getElementById("sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // Analyse-Button
  const processBtn = document.getElementById("process-btn");
  if (processBtn) {
    processBtn.addEventListener("click", processInput);
  }
});

async function processInput() {
  const text             = document.getElementById("inputText").value;
  const patientUl        = document.getElementById("patientData");
  const resultUl         = document.getElementById("resultData");
  const triageContainer  = document.getElementById("triageIndicator");

  // Reset aller Bereiche
  patientUl.innerHTML       = "";
  resultUl.innerHTML        = "";
  if (triageContainer) {
    triageContainer.innerHTML = "";
  }

  try {
    const res  = await fetch("/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();

    // 0) Triagestufen-Kreise neu bauen
    if (triageContainer) {
      const levels = [1, 2, 3, 4, 5];
      triageContainer.innerHTML = levels.map(l => {
        const isActive = l === data.triage ? "active" : "";
        return `<div
          class="triage-circle level-${l} ${isActive}"
          title="Triagestufe ${l}"
        ></div>`;
      }).join("");
    }

    // 1) Patientendaten-Liste befüllen
    Object.entries(data.data).forEach(([key, val]) => {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.innerHTML = `<strong>${key}:</strong> ${val}`;
      patientUl.appendChild(li);
    });

    // 2) Auswertung-Liste befüllen

    // Triagestufe als List-Item
    let li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>Triagestufe:</strong> ${data.triage}`;
    resultUl.appendChild(li);

    // Untersuchungen
    li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>Untersuchungen:</strong> ${
      data.exams.length ? data.exams.join(", ") : "–"
    }`;
    resultUl.appendChild(li);

    // Experten
    li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>Experten:</strong> ${
      data.experts.length ? data.experts.join(", ") : "–"
    }`;
    resultUl.appendChild(li);

  } catch (err) {
    // Fehler anzeigen
    const li = document.createElement("li");
    li.className = "list-group-item text-danger";
    li.textContent = `🚨 Error: ${err.message}`;
    resultUl.appendChild(li);
  }
}
