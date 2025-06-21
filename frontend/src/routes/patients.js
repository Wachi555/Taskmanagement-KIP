// frontend/routes/patients.js

const express = require('express');
const fetch = require('node-fetch').default;
const router = express.Router();

// Einzelnen Patienten vom Backend holen
async function fetchPatientById(id) {
  const res = await fetch(`http://localhost:8000/patient/${id}`);
  if (!res.ok) throw new Error("Patient nicht gefunden");
  return await res.json();
}

// Detail-Seite für Patienten-Eingabe
router.get('/patient/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  try {
    const result = await fetchPatientById(id);
    const patient = result.patient;
    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,
      data: patient,
      exams: patient.examinations || [],
      experts: patient.treatments || [],
      history: patient.history || [],
      errorMessage: null
    });
  } catch (error) {
    console.error(`Fehler beim Laden des Patienten-Inputs (${id}):`, error);
    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,
      data: {},
      exams: [],
      experts: [],
      history: [],
      errorMessage: 'Patient nicht gefunden'
    });
  }
});

module.exports = router;
