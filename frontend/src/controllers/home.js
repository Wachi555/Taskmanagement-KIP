// frontend/controllers/home.js
const express = require('express');
const router  = express.Router();
const store   = require('../models/patient_store');

// Mock: Wer ist wartend?
const mockWaiting = ['Hans Weber', 'Uwe Taniz'];

router.get('/', (req, res) => {
  const allPatients = store.getAll(); // ['Ute Russ', 'Hans Weber', 'Uwe Taniz']

  const waitingPatients = allPatients
    .filter(name => mockWaiting.includes(name))
    .map(name => ({ name }));

  const activePatients = allPatients.filter(name => !mockWaiting.includes(name));

  res.render('index', {
    appName:         'Task Management Demo',
    waitingPatients: waitingPatients,
    patients:        activePatients,
    data:            {},
    triage:          null,
    exams:           [],
    experts:         [],
    levels:          [1, 2, 3, 4, 5]
  });
});

router.post('/analyse', async (req, res) => {
  try {
    const inputText = req.body.text;
    const response = await fetch("http://localhost:8000/process_input", {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ text: inputText })
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
