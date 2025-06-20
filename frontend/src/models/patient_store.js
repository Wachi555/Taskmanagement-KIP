// frontend/models/patient_store.js

// Einfache In-Memory-Datenbank mit erweiterten Mock-Daten inklusive Historie
const patients = [
  {
    name: 'Hans Weber',
    triage: 3,
    dob: '1978-05-12',
    gender: 'männlich',
    symptoms: ['Kopfschmerzen', 'Schwindel'],
    registrationDate: '2025-06-18',
    adresse: 'Musterstraße 10, 93047 Regensburg',
    krankenkasse: 'AOK Bayern',
    history: [
      { date: '2025-06-10', findings: 'Beinbruch' },
      { date: '2025-03-22', findings: 'Hautausschlag' }
    ]
  },
  {
    name: 'Uwe Taniz',
    triage: 2,
    dob: '1985-11-03',
    gender: 'männlich',
    symptoms: ['Husten', 'Fieber'],
    registrationDate: '2025-06-19',
    adresse: 'Bahnhofstraße 5, 93047 Regensburg',
    krankenkasse: 'Techniker Krankenkasse',
    history: [
      { date: '2025-01-15', findings: 'Schlaganfall' }
    ]
  },
  {
    name: 'Ute Russ',
    triage: 4,
    dob: '1990-07-21',
    gender: 'weiblich',
    symptoms: ['Brustschmerzen'],
    registrationDate: '2025-06-17',
    adresse: 'Ringstraße 2, 93047 Regensburg',
    krankenkasse: 'Barmer',
    history: []
  }
];

// Nur die Namen (für ältere Views)
function getAll() {
  return patients.map(p => p.name);
}

// Detaillierte Daten (Name, Triage und alle Mock-Felder)
function getAllDetailed() {
  // gibt eine Kopie, damit das Original nicht verändert wird
  return patients.map(p => ({ ...p }));
}

// Einzelnen Patienten suchen (mit allen Feldern)
function findByName(name) {
  return patients.find(p => p.name === name) || null;
}

// Neuen Patienten hinzufügen (mit Default-Mock-Werten)
function add(patientData) {
  const name = typeof patientData === 'string'
    ? patientData
    : patientData.name;

  // Keine Duplikate
  if (patients.some(p => p.name === name)) return;

  const now = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const newPatient = {
    name,
    triage: patientData.triage ?? null,
    dob: patientData.dob ?? null,
    gender: patientData.gender ?? null,
    symptoms: patientData.symptoms ?? [],      
    registrationDate: patientData.registrationDate ?? now,
    adresse: patientData.adresse ?? null,
    krankenkasse: patientData.krankenkasse ?? null,
    history: patientData.history ?? []
  };

  patients.push(newPatient);
}

module.exports = {
  getAll,
  getAllDetailed,
  findByName,
  add
};
