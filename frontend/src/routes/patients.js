// routes/patients.js
const express       = require('express');
const router        = express.Router();
// Falls dein patient_store in 'models', nicht 'stores'
const { getAll, getDetails } = require('../models/patient_store');
const symptomStore  = require('../models/symptom_store');
const historyStore  = require('../models/history_store');

router.get('/patient/:name', (req, res) => {
  const name = decodeURIComponent(req.params.name);

  // Alle Patientennamen abrufen
  const allNames = getAll();
  if (!allNames.includes(name)) {
    return res.status(404).send('Patient nicht gefunden');
  }

  // Alle Detaildaten aus dem Store holen
  const patientDetails = getDetails(name);
  if (!patientDetails) {
    return res.status(404).send('Patient nicht gefunden');
  }

  // Symptome und Historie
  const symptoms = symptomStore.getFor(name) || [];
  const history  = historyStore.getFor(name)  || [];

  // Sidebar-Daten: keine Warteschlange, alle Patienten in Behandlung
  const waitingPatients = [];
  const patients = allNames;

  res.render('patient', {
    layout: 'main',

    // Sidebar-Context
    waitingPatients,
    patients,

    // Detail-Context
    patient: {
      name:    patientDetails.name,
      dob:     patientDetails.dob,
      gender:  patientDetails.gender
    },
    symptoms,
    history
  });
});

module.exports = router;
