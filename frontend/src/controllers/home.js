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

// POST-Route für den Analyse-Request
router.post('/analyse', async (req, res) => {
  // später: hier Text + Audio verarbeiten
  try {
    var inputText = req.body.text; 

    console.log("Input text: ", inputText);
    
    const response = await fetch("http://localhost:8000/process_input_debug", { // Hier auf /process_input umstellen wenn haupt-Anfrage gewünscht
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({text: inputText}) // Changed to match InputModel structure
    });

    if (!response.ok) {
      throw new Error('Failed to fetch data: ' + response.statusText);
    }
    console.log("Response ok:", response.ok);
    
    const data = await response.json();
    
    const result = {
      data: {
        Name: 'Patient', 
        'Symptome': data.output.symptoms.join(', ')
      },
      triage: 3, // Defaultwert, da noch nicht in der API
      exams: data.output.examinations.map(exam => exam.name),
      experts: data.output.treatments // Aktuell noch nicht in der API deshalb derweil die treatments genommen
    };
  // const result = {
  //   data:    { Name: 'Müller, Anna', 'Geb. Datum': '12.03.1980', Symptome: 'Husten, Fieber' },
  //   triage:  3,
  //   exams:   ['Blutentnahme', 'Röntgen'],
  //   experts: ['HNO', 'Internist']
  // };
    
    res.json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

module.exports = router;
