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
  const id = parseInt(req.params.id);

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
      history: patient.history || []
    });
  } catch (error) {
    res.status(404).render('404', {
      layout: 'main',
      message: 'Patient nicht gefunden'
    });
  }
});

// Patientenübersicht
router.get('/patient/:id/overview', async (req, res) => {
  const id = parseInt(req.params.id);

  try {
    const result = await fetchPatientById(id);
    const patient = result.patient;

    res.render('patient-overview', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: false,
      data: patient,
      diagnosis: result.latessult?.diagnosis || [],
      triage: result.latessult?.triage ?? null,
      exams: result.latessult?.examinations || [],
      experts: result.latessult?.treatments || [],
      symptoms: result.latessult?.symptoms || []
    });
  } catch (error) {
    res.status(404).render('404', {
      layout: 'main',
      message: 'Patient nicht gefunden'
    });
  }
});

module.exports = router;
