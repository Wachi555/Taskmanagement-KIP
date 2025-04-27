// frontend/controllers/home.js

const express = require('express');
const router  = express.Router();

// Da models/ jetzt direkt unter frontend/ liegt,
const store   = require('../models/patient_store');

// GET-Route für die Startseite
router.get('/', (req, res) => {
  res.render('index', {
    appName:  'Task Management Demo',
    patients: store.getAll(),  // z.B. ['Ute Russ','Hans Weber','Uwe Taniz']
    data:     {},              // leer beim ersten Laden
    triage:   null,
    exams:    [],
    experts:  [],
    levels:   [1,2,3,4,5]
  });
});

// POST-Route für den Analyse-Request (Mockup)
router.post('/analyse', (req, res) => {
  // später: hier Text + Audio verarbeiten
  const result = {
    data:    { Name: 'Müller, Anna', 'Geb. Datum': '12.03.1980', Symptome: 'Husten, Fieber' },
    triage:  3,
    exams:   ['Blutentnahme', 'Röntgen'],
    experts: ['HNO', 'Internist']
  };
  res.json(result);
});

module.exports = router;
