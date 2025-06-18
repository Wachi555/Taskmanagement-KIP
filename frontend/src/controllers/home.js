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
    levels: [1, 2, 3, 4, 5]
  });
});

// Registrierung (alle Patienten, Wartende, Aktive)
router.get('/registration', (req, res) => {
  const allPatients = store.getAllDetailed(); // [{ name, triage }]
  const waitingPatients = allPatients.filter(p => mockWaiting.includes(p.name));
  const activePatients = allPatients.filter(p => !mockWaiting.includes(p.name));

  res.render('registration', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    allPatients,
    waitingPatients,
    activePatients,
    levels: [1, 2, 3, 4, 5]
  });
});

// Koordination (einfaches Beispiel)
router.get('/coordination', (req, res) => {
  const allPatients = store.getAll();
  const waitingPatients = allPatients
    .filter(name => mockWaiting.includes(name))
    .map(name => ({ name }));

  const activePatients = allPatients
    .filter(name => !mockWaiting.includes(name));

  res.render('registration', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    waitingPatients,
    patients: activePatients
  });
});

// Formular für neuen Patienten
router.get('/new-patient', (req, res) => {
  res.render('new-patient', {
    layout: 'main',
    appName: 'Notaufnahme'
  });
});

// Neuen Patienten speichern
router.post('/new-patient', (req, res) => {
  const name = req.body.name?.trim();
  if (name) {
    store.add(name); // du brauchst eine add-Funktion im patient_store
  }
  res.redirect('/registration');
});

// Analyse POST → API call an Python-Backend
router.post('/analyse', async (req, res) => {
  try {
    const inputText = req.body.text;
    const response = await fetch("http://localhost:8000/process_input", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText })
    });

    if (!response.ok) throw new Error('Failed to fetch data');

    const data = await response.json();
    const result = {
      data: {
        Name: 'Patient',
        Symptome: data.output.symptoms.join(', ')
      },
      triage: 3,
      exams: data.output.examinations.map(e => e.name),
      experts: data.output.treatments
    };

    res.json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

module.exports = router;
