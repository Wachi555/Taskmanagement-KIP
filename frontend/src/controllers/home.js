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
async function deletePatientById(id) {
  const res = await fetch(`http://localhost:8000/patient/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Löschen fehlgeschlagen (${res.status})`);
}
async function updatePatientStatusById(id, status) {
  const res = await fetch(`http://localhost:8000/patient/update_status/${id}/0`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Aktualisierung fehlgeschlagen (${res.status})`);
  }
  return res.json();
};
async function updatePatientById(id, payload) {
  const res = await fetch(`http://localhost:8000/patient/update/${id}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Aktualisierung fehlgeschlagen (${res.status})`);
  }
  return res.json();
};







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

     // Wartende Patienten: filtern, mappen und nach triage aufsteigend sortieren
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }))
      .sort((a, b) => a.triage - b.triage);   // 1 vor 2, 2 vor 3, …

    // Aktive Patienten: filtern, mappen und nach triage aufsteigend sortieren
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }))
      .sort((a, b) => a.triage - b.triage);


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

router.get('/patient/update_status/:id/:status', async (req, res) => {
  const { id, status } = req.params;
  console.log(`🔥 Update Patient ${id} to status ${status}`);

  try {
    // 1. Debugging: Loggen bevor der Aufruf passiert
    console.log("Calling backend...");
    
    // 2. Eigentlicher Aufruf
    const result = await updatePatientStatusById(id, status);
    console.log("✅ Backend response:", result);

    // 3. Redirect
    res.redirect('/coordination');
  } catch (error) {
    console.error("❌ FEHLER:", error);
    res.status(500).send(`Update fehlgeschlagen: ${error.message}`);
  }
});


// Koordination
router.get('/coordination', async (req, res) => {
  try {
    const allPatients = await fetchAllPatients();

    // Wartende Patienten: filtern, mappen und nach triage aufsteigend sortieren
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }))
      .sort((a, b) => a.triage - b.triage);   // 1 vor 2, 2 vor 3, …

    // Aktive Patienten: filtern, mappen und nach triage aufsteigend sortieren
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id:     p.id,
        name:   `${p.first_name} ${p.last_name}`,
        triage: p.last_triage_level
      }))
      .sort((a, b) => a.triage - b.triage);


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

    // frontend/controllers/home.js, im router.post('/analyse', …)
    const result = {
      diagnoses: data.output.diagnoses     || [],
      examinations: data.output.examinations || [],
      treatments: data.output.treatments   || "",
      // Experten aus dem String "A, B" parsen
      experts: typeof data.output.experts === 'string'
        ? data.output.experts.split(',').map(s => s.trim()).filter(Boolean)
        : (Array.isArray(data.output.experts) ? data.output.experts : []),
      // Allergien existieren im Output zwar nicht immer – default leeres Array
      allergies: typeof data.output.allergies === 'string'
        ? data.output.allergies.split(',').map(s => s.trim()).filter(Boolean)
        : (Array.isArray(data.output.allergies) ? data.output.allergies : []),
      triage: data.output.triage ?? null,
      symptoms: data.output.symptoms       || []
    };

    res.json(result);

  } catch (error) {
    console.error('Analysefehler:', error);
    res.status(500).json({ error: 'Analyse fehlgeschlagen' });
  }
});

// routes/home.js

// Patient Input mit Sidebar-Daten
router.get('/patient/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);

  try {
    // 1) Patient holen
    const result = await fetchPatientById(id);
    const patient = result.patient;
    const latestEntry = result.latest_entry || {};
    const latestResult = result.latest_result || {};
    const diagnoses = result.diagnoses || [];

    // Symptome parsen
    const parsedSymptoms = latestEntry.symptoms
      ? latestEntry.symptoms.split(',').map(s => s.trim())
      : [];

      // Alten Code ersetzen durch
      let allergies = [];

      // 1) Versuche, aus extracted_contents_json zu lesen
      if (latestEntry.extracted_contents_json) {
        try {
          const extracted = JSON.parse(latestEntry.extracted_contents_json);
          if (Array.isArray(extracted.allergies) && extracted.allergies.length > 0) {
            // Nur übernehmen, wenn wirklich Allergien drinstehen
            allergies = extracted.allergies;
          }
        } catch (e) {
          console.warn("⚠️ Allergie-Parsing fehlgeschlagen:", e.message);
        }
      }

      // 2) Fallback auf patient.allergies, wenn extracted leer oder nicht vorhanden
      if (allergies.length === 0 && patient.allergies) {
        allergies = typeof patient.allergies === 'string'
          ? patient.allergies.split(',').map(s => s.trim()).filter(Boolean)
          : (Array.isArray(patient.allergies) ? patient.allergies : []);
      }


    // Behandlungen & Experten als Array (auch wenn als String gespeichert)
    const treatments = typeof latestResult.treatments === 'string'
      ? latestResult.treatments.split(',').map(s => s.trim()).filter(Boolean)
      : (Array.isArray(latestResult.treatments) ? latestResult.treatments : []);

    const experts = typeof latestResult.experts === 'string'
      ? latestResult.experts.split(',').map(s => s.trim()).filter(Boolean)
      : (Array.isArray(latestResult.experts) ? latestResult.experts : []);

    const exams = Array.isArray(latestResult.examinations)
      ? latestResult.examinations.sort((a, b) => a.priority - b.priority)
      : [];

    // Aktuelles Triage-Level
    const currentTriage = latestEntry.triage ?? patient.last_triage_level;

    // 2) Sidebar-Daten
    const allPatients = await fetchAllPatients();
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({
        id: p.id,
        name: `${p.first_name} ${p.last_name}`
      }));
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({
        id: p.id,
        name: `${p.first_name} ${p.last_name}`
      }));

    // 3) Rendern patient-input.hbs mit Triage + Ergebnissen
    res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,

      // Sidebar
      waitingPatients,
      activePatients,
      id,

      // Triage-Indicator im Header
      levels: [1, 2, 3, 4, 5],
      triage: currentTriage,

      // Patientendaten
      data: {
        name: `${patient.first_name} ${patient.last_name}`,
        dob: patient.date_of_birth,
        gender: patient.gender,
        adresse: patient.address,
        krankenkasse: patient.health_insurance,
        symptoms: parsedSymptoms,
        history: result.history || []
      },

      // Ergebnisse
      diagnoses,
      exams,
      treatments,
      experts,
      allergies
    });

  } catch (error) {
    console.error("Fehler beim Laden des Patienten:", error);

    const allPatients = await fetchAllPatients().catch(() => []);
    const waitingPatients = allPatients
      .filter(p => p.is_waiting)
      .map(p => ({ id: p.id, name: `${p.first_name} ${p.last_name}` }));
    const activePatients = allPatients
      .filter(p => p.in_treatment)
      .map(p => ({ id: p.id, name: `${p.first_name} ${p.last_name}` }));

    return res.render('patient-input', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: true,

      waitingPatients,
      activePatients,
      id,
      levels: [1, 2, 3, 4, 5],
      triage: null,

      data: {},
      diagnoses: [],
      exams: [],
      treatments: [],
      experts: [],
      allergies: [],
      errorMessage: 'Patient nicht gefunden'
    });
  }
});




// --- Bearbeiten: Formular anzeigen ---
// --- Bearbeiten: Formular anzeigen ---
router.get('/patient/:id/edit', async (req, res) => {
  const id = Number(req.params.id);
  try {
    const result = await fetchPatientById(id);
    const patient = result.patient || result;
    
    res.render('patient-edit', {
      layout: 'main',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      patient,
      levels: [1, 2, 3, 4, 5],
      showHome: true
    });
  } catch (error) {
    console.error("Fehler beim Laden des Patienten zum Bearbeiten:", error);
    res.status(404).render('500', { 
      message: 'Patient nicht gefunden',
      error: error.message
    });
  }
});

// server (Port 4000):
// statt router.patch(...)
router.post('/patient/update/:id', async (req, res) => {
  console.log('POST /patient/update/' + req.params.id, 'body=', req.body);
  try {
    await updatePatientById(Number(req.params.id), req.body);
    return res.json({ success: true });
  } catch (error) {
    console.error('🚨 Error in POST /patient/update/:id', error);
    return res.status(500).json({ success: false, message: error.message });
  }
});




// --- Löschen: Patient entfernen ---
router.delete('/patient/:id', async (req, res) => {
  const id = Number(req.params.id);
  try {
    await deletePatientById(id);
    res.json({ success: true });
  } catch (error) {
    console.error("Fehler beim Löschen des Patienten:", error);
    res.status(500).json({ success: false, message: error.message });
  }
});

// --- Patient Overview (Übersicht) ---
router.get('/patient/:id/overview', async (req, res) => {
  const id = parseInt(req.params.id, 10);

  try {
    // 1) Daten vom Backend holen
    const result       = await fetchPatientById(id);
    const patient      = result.patient;
    const latestEntry  = result.latest_entry  || {};
    const latestResult = result.latest_result || {};
    const diagnoses    = result.diagnoses     || [];

    // 2) Symptome parsen
    const symptoms = (latestEntry.symptoms || '')
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);

    // 3) Allergien parsen (entweder aus String-Feld oder aus extracted_contents_json)
      let allergies = [];

      // Versuch, aus extracted_contents_json zu lesen
      if (latestEntry.extracted_contents_json) {
        try {
          const extracted = JSON.parse(latestEntry.extracted_contents_json);
          // Nur übernehmen, wenn tatsächlich Allergien vorhanden sind
          if (Array.isArray(extracted.allergies) && extracted.allergies.length > 0) {
            allergies = extracted.allergies;
          }
        } catch (e) {
          console.warn("⚠️ Allergie-Parsing fehlgeschlagen:", e.message);
        }
      }

      // Fallback, falls keine Allergien im JSON waren
      if (allergies.length === 0 && patient.allergies) {
        allergies = typeof patient.allergies === 'string'
          ? patient.allergies.split(',').map(s => s.trim()).filter(Boolean)
          : (Array.isArray(patient.allergies) ? patient.allergies : []);
      }

    // 4) Rendern
    return res.render('patient-overview', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: false,

      // Patient-Grunddaten
      data: {
        name:         `${patient.first_name} ${patient.last_name}`,
        dob:          patient.date_of_birth,
        gender:       patient.gender      || 'unbekannt',
        adresse:      patient.address,
        krankenkasse: patient.health_insurance
      },

      // Ergebnisse
      diagnoses:   diagnoses,  // Array von { name, confidence, … }
      triage:      latestEntry.triage_level ?? patient.last_triage_level,
      exams:       latestResult.examinations || [],
      treatments:  typeof latestResult.treatments === 'string'
                     ? latestResult.treatments.split(',').map(s=>s.trim())
                     : (Array.isArray(latestResult.treatments) ? latestResult.treatments : []),
      experts:     typeof latestResult.experts === 'string'
                     ? latestResult.experts.split(',').map(s=>s.trim())
                     : (Array.isArray(latestResult.experts) ? latestResult.experts : []),
      symptoms,
      allergies,   // neu!

      errorMessage: null
    });

  } catch (error) {
    console.error(`Fehler beim Laden der Übersicht von Patient ${id}:`, error);

    // Fallback mit leeren Daten
    return res.render('patient-overview', {
      layout: 'patient',
      appName: 'Notaufnahme Universitätsklinikum Regensburg',
      showHome: true,
      showSidebarToggle: false,

      data:        {},
      diagnoses:   [],
      triage:      null,
      exams:       [],
      treatments:  [],
      experts:     [],
      symptoms:    [],
      allergies:   [],

      errorMessage: 'Patient nicht gefunden oder fehlerhafte Daten'
    });
  }
});



module.exports = router;
