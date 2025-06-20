// frontend/controllers/home.js
const express = require('express');
const router = express.Router();
const store = require('../models/patient_store');

// Welche Patienten sind derzeit wartend?
const mockWaiting = ['Hans Weber', 'Uwe Taniz'];

// Anmeldemaske (Startseite)
router.get('/', (req, res) => {
  res.render('index', {
    layout: false,
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    showSidebarToggle: false
  });
});

// Dashboard
router.get('/dashboard', (req, res) => {
  const allPatients = store.getAll();
  const waitingPatients = allPatients
    .filter(name => mockWaiting.includes(name))
    .map(name => ({ name }));
  const activePatients = allPatients
    .filter(name => !mockWaiting.includes(name));

  res.render('dashboard', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    waitingPatients,
    patients: activePatients,
    data: {},
    triage: null,
    exams: [],
    experts: [],
    symptoms: [],
    levels: [1, 2, 3, 4, 5],
    showHome: true
  });
});

// Registrierung (alle Patienten, Wartende, Aktive)
router.get('/registration', (req, res) => {
  const allPatients = store.getAllDetailed();
  const waitingPatients = allPatients.filter(p => mockWaiting.includes(p.name));
  const activePatients = allPatients.filter(p => !mockWaiting.includes(p.name));

  res.render('registration', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    allPatients,
    waitingPatients,
    activePatients,
    levels: [1, 2, 3, 4, 5],
    showHome: true
  });
});

// Koordination
router.get('/coordination', (req, res) => {
  const allPatients = store.getAllDetailed();
  const waitingPatients = allPatients.filter(p => mockWaiting.includes(p.name));
  const activePatients  = allPatients.filter(p => !mockWaiting.includes(p.name));

  res.render('coordination', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    waitingPatients,
    activePatients,
    showHome: true,
    showSidebarToggle: false
  });
});

// Formular für neuen Patienten
router.get('/new-patient', (req, res) => {
  res.render('new-patient', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg'
  });
});

// Neuen Patienten speichern
router.post('/new-patient', (req, res) => {
  const name = req.body.name?.trim();
  if (name) {
    store.add({ name, symptoms: [] });
  }
  res.redirect('/registration');
});

// Analyse POST → API call an Python-Backend
router.post('/analyse', async (req, res) => {
  try {
    const inputText = req.body.text;
    const response = await fetch('http://localhost:8000/process_input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText })
    });
    if (!response.ok) throw new Error(`Backend-Fehler: ${response.status}`);
    const data = await response.json();

    // Ergebnis-Objekt, das an das Frontend geht
    const result = {
      data: {
        Name: data.output.name || '–',
        Symptome: (data.output.symptoms || []).join(', ')
      },
      diagnosis: data.output.diagnosis || [],
      triage: data.output.triage ?? null,
      exams: data.output.examinations || [],    // Array von { name, priority }
      experts: data.output.treatments || [],    // Array von Strings
      symptoms: data.output.symptoms || []
    };

    res.json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Patienten-Detail-Sichten
// patient-input (Eingabe)
router.get('/patient/:name', (req, res, next) => {
  const name = decodeURIComponent(req.params.name);
  const patientData = store.findByName(name);
  if (!patientData) {
    return res.status(404).render('404', { layout: 'main', message: 'Patient nicht gefunden' });
  }

  res.render('patient-input', {
    layout: 'patient',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    showHome: true,
    showSidebarToggle: true,
    data: patientData,
    symptoms: patientData.symptoms
  });
});

// patient-overview (Übersicht)
router.get('/patient/:name/overview', (req, res) => {
  const name = decodeURIComponent(req.params.name);
  const patientData = store.findByName(name);
  if (!patientData) {
    return res.status(404).render('404', { layout: 'main', message: 'Patient nicht gefunden' });
  }

  res.render('patient-overview', {
    layout: 'patient',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    showHome: true,
    showSidebarToggle: false,
    data: patientData,
    diagnosis:    patientData.diagnosis || [],
    triage:       patientData.triage,
    exams:        patientData.examinations || [],
    experts:      patientData.treatments || [],
    symptoms:     patientData.symptoms
  });
});

module.exports = router;
