const BASE_URL = "http://localhost:8000"; // ggf. anpassen bei Deployment

let patients = []; // In-Memory-Cache

// ==============================
// LADEN
// ==============================

// Alle Patienten laden und cachen
async function loadFromBackend() {
  const res = await fetch(`${BASE_URL}/patients`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Fehler beim Laden der Patienten");
  patients = json.output;
}

// Einzelnen Patienten mit Details laden
async function getPatient(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || `Patient ${id} nicht gefunden`);
  return json.output;
}

// Historie für Patient
async function getPatientEntries(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}/entries`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Fehler beim Laden der Einträge");
  return json.output;
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
  if (!json.success) throw new Error(json.error || "Fehler beim Anlegen");
  return json.output;
}

// Patienten löschen
async function deletePatient(id) {
  const res = await fetch(`${BASE_URL}/patient/${id}`, {
    method: "DELETE"
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Löschen fehlgeschlagen");
  return json.output;
}

// ==============================
// STATUS / TRIAGE
// ==============================

// Triage-Stufe setzen (0–5)
async function setTriage(id, level) {
  const res = await fetch(`${BASE_URL}/patient/${id}/set_triage/${level}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Triage-Update fehlgeschlagen");
  return json.output;
}

// Patientenstatus setzen
// status: 0 = Historie, 1 = Wartend, 2 = In Behandlung
async function setStatus(id, status) {
  const res = await fetch(`${BASE_URL}/patient/update_status/${id}/${status}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Status-Update fehlgeschlagen");
  return json.output;
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
  if (!json.success) throw new Error(json.error || "Fehler bei der Anamnese-Verarbeitung");
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
  if (!json.success) throw new Error(json.error || "Fehler bei der Debug-Anamnese");
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
