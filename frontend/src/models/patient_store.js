const BASE_URL = "http://localhost:8000"; // ggf. anpassen bei Deployment

let patients = []; // In-Memory-Cache

// ==============================
// LADEN
// ==============================

// Alle Patienten laden und cachen
async function loadFromBackend() {
  const res = await fetch(`${BASE_URL}/patients`);
  if (!res.ok) throw new Error("Fehler beim Laden der Patienten");
  patients = await res.json();
}

// Einzelnen Patienten mit Details laden
async function getPatient(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}`);
  if (!res.ok) throw new Error(`Patient ${id} nicht gefunden`);
  return await res.json(); // enthält: patient, latest_entry, latessult
}

// Historie für Patient
async function getPatientEntries(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}/entries`);
  if (!res.ok) throw new Error("Fehler beim Laden der Einträge");
  return await res.json();
}

// ==============================
// SPEICHERN / LÖSCHEN
// ==============================

// Neuen Patienten anlegen
async function addPatient(data) {
  const res = await fetch(`${BASE_URL}/patient`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const json = await res.json();
  if (!json.success) throw new Error(json.error_message || "Fehler beim Anlegen");
  return json;
}

// Patienten löschen
async function deletePatient(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}`, {
    method: "DELETE"
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.error_message || "Löschen fehlgeschlagen");
  return json;
}

// ==============================
// STATUS / TRIAGE
// ==============================

// Triage-Stufe setzen (0–5)
async function setTriage(id, level) {
  const res = await fetch(`${BASE_URL}/patient/${id}/set_triage/${level}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error_message || "Triage-Update fehlgeschlagen");
  return json;
}

// Patientenstatus setzen
// status: 0 = Historie, 1 = Wartend, 2 = In Behandlung
async function setStatus(id, status) {
  const res = await fetch(`${BASE_URL}/patient/update_status/${id}/${status}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error_message || "Status-Update fehlgeschlagen");
  return json;
}

// ==============================
// ANAMNESE
// ==============================

// Anamnese verarbeiten (Patient muss existieren)
async function analyze(id, text) {
  const res = await fetch(`${BASE_URL}/process_input/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  const json = await res.json();
  return json.output;
}

// Debug-Version (ohne Patient)
async function analyzeDebug(text) {
  const res = await fetch(`${BASE_URL}/process_input_debug`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  const json = await res.json();
  return json.output;
}

// ==============================
// HELPER
// ==============================

function getAll() {
  return patients.map(p => `${p.first_name} ${p.last_name}`);
}

function getAllDetailed() {
  return patients.map(p => ({ ...p }));
}

function findByName(name) {
  return patients.find(p => `${p.first_name} ${p.last_name}` === name) || null;
}

function findById(id) {
  return patients.find(p => p.id === id) || null;
}

// ==============================
// EXPORT
// ==============================

window.patientStore = {
  loadFromBackend,
  getPatient,
  getPatientEntries,
  addPatient,
  deletePatient,
  setTriage,
  setStatus,
  analyze,
  analyzeDebug,
  getAll,
  getAllDetailed,
  findByName,
  findById
};
