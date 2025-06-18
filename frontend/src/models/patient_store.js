// frontend/models/patient_store.js

// Einfache In-Memory-Datenbank (kann später durch DB ersetzt werden)
let patients = [
  { name: 'Hans Weber', triage: 3 },
  { name: 'Uwe Taniz', triage: 2 },
  { name: 'Ute Russ', triage: 4 }
];

// Alle Namen (für alte Views)
function getAll() {
  return patients.map(p => p.name);
}

// Detailliert (Name + Triage)
function getAllDetailed() {
  return [...patients]; // defensive copy
}

// Einzelnen Patienten suchen
function findByName(name) {
  return patients.find(p => p.name === name);
}

// Neuen Patienten hinzufügen (ohne Duplikate)
function add(name) {
  const exists = patients.some(p => p.name === name);
  if (!exists) {
    patients.push({ name, triage: null }); // triage kann später gesetzt werden
  }
}

module.exports = {
  getAll,
  getAllDetailed,
  findByName,
  add
};
