// frontend/routes/patients.js

const express = require('express');
const router  = express.Router();
const store   = require('../models/patient_store');

// Detail-Seite für einen einzelnen Patienten
router.get('/patient/:name', (req, res, next) => {
  const name = decodeURIComponent(req.params.name);
  console.log('Lookup-Name:', name);

  // Einzelnen Datensatz per findByName holen
  const patientData = store.findByName(name);
  console.log('Gefundener Datensatz:', patientData);

  if (!patientData) {
    // Patient nicht gefunden → 404-Seite
    return res.status(404).render('404', {
      layout: 'main',
      message: 'Patient nicht gefunden'
    });
  }

  res.render('patient-input', {
    layout: 'patient',
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    showHome: true,
    showSidebarToggle: true,
    data: patientData,
    // hier die beiden Arrays aus deinem patientData-Objekt
    exams:   patientData.examinations,
    experts: patientData.treatments
  });
});

module.exports = router;
