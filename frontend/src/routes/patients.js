// frontend/routes/patients.js

const express = require('express');
const fetch = require('node-fetch').default;
const router = express.Router();

// Alle Patienten vom Backend holen
async function fetchAllPatients() {
  const res = await fetch("http://localhost:8000/patients");
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Patienten konnten nicht geladen werden");
  return json.output;
}

// Einzelnen Patienten vom Backend holen
async function fetchPatientById(id) {
  const res = await fetch(`http://localhost:8000/patient/${id}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Patient nicht gefunden");
  return json.output;
}

// Detail-Seite für Patienten-Eingabe
router.get('/patient/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  try {
    // Einzelnen Patienten laden
    const result = await fetchPatientById(id);
    const patient = result.patient;

    // Sidebar-Daten: alle Patienten laden, filtern, mappen und nach Triagestufe sortieren
    const allPatients = await fetchAllPatients();

    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: Number(p.last_triage_level)
      }))
      .sort((a, b) => a.triage - b.triage);

    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: Number(p.last_triage_level)
      }))
      .sort((a, b) => a.triage - b.triage);

    // Rendern mit Sidebar-Daten und Patientendaten
    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,
      data: patient,
      exams: patient.examinations || [],
      experts: patient.treatments || [],
      history: patient.history || [],
      errorMessage: null,
      waitingPatients,
      activePatients
    });
  } catch (error) {
    console.error(`Fehler beim Laden des Patienten-Inputs (${id}):`, error);

    // Bei Fehler trotzdem Sidebar-Daten laden
    let waitingPatients = [];
    let activePatients = [];
    try {
      const allPatients = await fetchAllPatients();
      waitingPatients = allPatients
        .filter(p => p.is_waiting)
        .map(p => ({
          id: p.id,
          name: `${p.first_name} ${p.last_name}`,
          triage: Number(p.last_triage_level)
        }))
        .sort((a, b) => a.triage - b.triage);
      activePatients = allPatients
        .filter(p => p.in_treatment)
        .map(p => ({
          id: p.id,
          name: `${p.first_name} ${p.last_name}`,
          triage: Number(p.last_triage_level)
        }))
        .sort((a, b) => a.triage - b.triage);
    } catch (loadError) {
      console.error('Fehler beim Laden der Sidebar-Daten:', loadError);
    }

    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,
      data: {},
      exams: [],
      experts: [],
      history: [],
      errorMessage: 'Patient nicht gefunden',
      waitingPatients,
      activePatients
    });
  }
});

module.exports = router;
