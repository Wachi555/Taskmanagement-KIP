// frontend/controllers/home.js
const express = require('express');
const fetch = require('node-fetch').default;
const router = express.Router();

// ============================
// HILFSFUNKTIONEN
// ============================

async function fetchAllPatients() {
  const res = await fetch("http://localhost:8000/patients");
  if (!res.ok) throw new Error("Patienten konnten nicht geladen werden");
  return await res.json();
}

async function fetchPatientById(id) {
  const res = await fetch(`http://localhost:8000/patient/${id}`);
  if (!res.ok) throw new Error("Patient nicht gefunden");
  return await res.json();
}

// ============================
// ROUTEN
// ============================

// Startseite (Anmeldung)
router.get('/', (req, res) => {
  res.render('index', {
    layout: false,
    appName: 'Notaufnahme Universitätsklinikum Regensburg',
    showSidebarToggle: false
  });
});

// Dashboard
router.get('/dashboard', async (req, res) => {
  try {
    const allPatients = await fetchAllPatients();
    const waitingPatients = allPatients.filter(p => p.is_waiting);
    const activePatients = allPatients.filter(p => p.in_treatment);

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
  } catch (error) {
    res.status(500).render('500', { message: 'Fehler beim Laden der Patienten' });
  }
});

// Registrierung
router.get('/registration', async (req, res) => {
  try {
    const allPatients = await fetchAllPatients();

    // Wartende Patienten: nur die benötigten Felder extrahieren
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }));

    // Aktive Patienten: analog
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }));

    res.render('registration', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      allPatients,
      waitingPatients,
      activePatients,
      levels: [1, 2, 3, 4, 5],
      showHome: true,
      errorMessage: null
    });
  } catch (error) {
    console.error("Fehler beim Laden der Patienten:", error.message);

    res.render('registration', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      allPatients: [],
      waitingPatients: [],
      activePatients: [],
      levels: [1, 2, 3, 4, 5],
      showHome: true,
      errorMessage: 'Fehler beim Laden der Patienten. Die Liste konnte nicht angezeigt werden.'
    });
  }
});



// Koordination
router.get('/coordination', async (req, res) => {
  try {
    const allPatients = await fetchAllPatients();

    // Wartende Patienten: id, name, triage
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }));

    // In Behandlung: id, name, triage
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }));

    res.render('coordination', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      waitingPatients,
      activePatients,
      showHome: true,
      showSidebarToggle: false
    });
  } catch (error) {
    console.error("Fehler beim Laden der Patienten für Coordination:", error);
    res.status(500).render('500', { message: 'Fehler beim Laden der Patienten' });
  }
});


// Neues Patientenformular
router.get('/new-patient', (req, res) => {
  res.render('new-patient', {
    layout: 'main',
    appName: 'Notaufnahme Universitätsklinikum Regensburg'
  });
});

router.post('/new-patient', async (req, res) => {
  // 0) Loggen, was im Request-Body angekommen ist
  console.log('▶️ POST /new-patient bekommen, req.body =', req.body);

  // 1) Destructure der Felder, wie Dein Frontend sie sendet
  const {
    first_name,
    last_name = "",
    date_of_birth,
    address,
    health_insurance,
    allergies = "",
    symptoms,
    triage_level,
    is_waiting = true,
    in_treatment = false
  } = req.body;

  // Optional: einfache Validierung
  if (!first_name || !last_name) {
    console.error('❌ Fehlende Namen-Felder');
    return res.status(400).render('registration', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      errorMessage: 'Vor- und Nachname sind erforderlich.',
      allPatients: [], waitingPatients: [], activePatients: [],
      levels: [1,2,3,4,5], showHome: true
    });
  }

  // 2) Payload bauen und loggen
  const payload = {
    first_name,
    last_name,
    date_of_birth,
    address,
    health_insurance,
    allergies,
    // Wenn Symptome als kommaseparierter String kommen, splitten:
    symptoms: typeof symptoms === 'string'
      ? symptoms.split(',').map(s => s.trim()).filter(Boolean)
      : (Array.isArray(symptoms) ? symptoms : []),
    triage_level: Number(triage_level),
    is_waiting: Boolean(is_waiting),
    in_treatment: Boolean(in_treatment)
  };
  console.log('↗️ Proxye POST → http://localhost:8000/patients mit', payload);

  try {
    // 3) Patienten anlegen
    const resp = await fetch("http://localhost:8000/patients", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });
    console.log(`⬇️ Backend antwortete mit Status ${resp.status}`);

    if (!resp.ok) {
      const text = await resp.text();
      console.error(`❌ Backend-Fehler (Status ${resp.status}):`, text);
      return res.status(500).render('registration', {
        layout: 'main',
        appName: 'Notaufnahme Universitätsklinikum Regensburg',
        errorMessage: `Patient konnte nicht gespeichert werden (Status ${resp.status}).`,
        allPatients: [], waitingPatients: [], activePatients: [],
        levels: [1,2,3,4,5], showHome: true
      });
    }

    // 4) Erfolgreich → zurück zur Liste
    return res.redirect('/registration');

  } catch (error) {
    console.error("🚨 Fehler beim Speichern:", error);
    return res.status(500).render('registration', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      errorMessage: `Patient konnte nicht gespeichert werden: ${error.message}`,
      allPatients: [], waitingPatients: [], activePatients: [],
      levels: [1,2,3,4,5], showHome: true
    });
  }
});




// Analyse POST (Debug fallback)
router.post('/analyse', async (req, res) => {
  try {
    const inputText = req.body.text;
    const response = await fetch('http://localhost:8000/process_input_debug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText })
    });
    if (!response.ok) throw new Error(`Backend-Fehler: ${response.status}`);
    const data = await response.json();

    const result = {
      data: {
        Name: data.output.name || '–',
        Symptome: (data.output.symptoms || []).join(', ')
      },
      diagnosis: data.output.diagnosis || [],
      triage: data.output.triage ?? null,
      exams: data.output.examinations || [],
      experts: data.output.treatments || [],
      symptoms: data.output.symptoms || []
    };

    res.json(result);
  } catch (error) {
    console.error('Analysefehler:', error);
    res.status(500).json({ error: 'Analyse fehlgeschlagen' });
  }
});

// Patient Input
router.get('/patient/:id', async (req, res) => {
  const id = parseInt(req.params.id);
  try {
    const result = await fetchPatientById(id);
    const patient = result.patient;
    const latestEntry = result.latessult; // enthält Symptome, Diagnose etc.

    // Symptome als Array
    const parsedSymptoms = latestEntry?.symptoms
      ? latestEntry.symptoms.split(',').map(s => s.trim())
      : [];

    // Historie vorbereiten (z. B. alte Einträge mit Befund + Datum)
    const transformedHistory = result.history?.map(entry => ({
      date: entry.entry_date,
      findings: entry.patient_history
    })) || [];

    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,
      data: {
        name: `${patient.first_name} ${patient.last_name}`,
        dob: patient.date_of_birth,
        gender: patient.gender || 'unbekannt', // wenn du kein gender-Feld hast
        adresse: patient.address,
        krankenkasse: patient.health_insurance,
        symptoms: parsedSymptoms,
        history: transformedHistory
      }
    });
  } catch (error) {
    console.error("Fehler beim Laden des Patienten:", error);
    res.status(404).render('404', {
      layout: 'main',
      message: 'Patient nicht gefunden'
    });
  }
});

// Patient Overview (Übersicht)
router.get('/patient/:id/overview', async (req, res) => {
  const id = parseInt(req.params.id, 10);

  try {
    // Daten vom Backend holen
    const result  = await fetchPatientById(id);
    const patient = result.patient;
    const latest  = result.latest_entry || result.latestResult || result.latessult || {};

    const symptoms = (latest.symptoms || '')
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);

    // Erfolgreiches Rendern
    return res.render('patient-overview', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: false,
      data: {
        name:         `${patient.first_name} ${patient.last_name}`,
        dob:          patient.date_of_birth,
        gender:       patient.gender || 'unbekannt',
        adresse:      patient.address,
        krankenkasse: patient.health_insurance
      },
      diagnosis: latest.diagnosis   || [],
      triage:    latest.triage      ?? null,
      exams:     latest.examinations || [],
      experts:   latest.treatments   || [],
      symptoms,
      errorMessage: null
    });

  } catch (error) {
    console.error(`Fehler beim Laden der Übersicht von Patient ${id}:`, error);

    // ab hier: immer patient-overview rendern – keine 404-Seite
    return res.render('patient-overview', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: false,
      data:      {},
      diagnosis: [],
      triage:    null,
      exams:     [],
      experts:   [],
      symptoms:  [],
      errorMessage: 'Patient nicht gefunden oder fehlerhafte Daten'
    });
  }
});





module.exports = router;
