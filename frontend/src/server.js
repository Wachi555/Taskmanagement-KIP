// src/server.js

const path       = require('path');
const express    = require('express');
const { engine } = require('express-handlebars');

const homeRoutes    = require('./controllers/home');
const patientRoutes = require('./routes/patients');
const audioCtrl  = require('./controllers/audio.js');


const app = express();

// Handlebars konfigurieren mit allen Helpers
app.engine('hbs', engine({
  extname:    '.hbs',
  layoutsDir: path.join(__dirname, 'views', 'layouts'),
  partialsDir: path.join(__dirname, 'views', 'partials'),
  helpers: {
    eq: (a, b) => a === b,
    encodeURI: (s) => encodeURIComponent(s),
    encodeURIComponent: (s) => encodeURIComponent(s),
    formatDate: (dateString) => {
      if (!dateString) return '';
      const [year, month, day] = dateString.split('-');
      return `${day}.${month}.${year}`;
    },
    // Neuer Helper für Triage-Sortierung
    sortByTriage: function(patients) {
      if (!patients) return [];
      // Sicherstellen, dass wir ein Array haben
      const patientsArray = Array.isArray(patients) ? patients : Object.values(patients);
      // Sortieren nach Triage-Level (numerisch)
      return patientsArray.slice().sort((a, b) => {
        // Fallback auf 0 wenn triage undefined/null
        const aTriage = Number(a.triage) || 0;
        const bTriage = Number(b.triage) || 0;
        return aTriage - bTriage;
      });
    }
  }
}));

app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));

// Static-Files und Body-Parser
app.use(express.static(path.join(__dirname, '../public')));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use('/', audioCtrl);

// Routen einbinden
app.use('/', homeRoutes);
app.use('/', patientRoutes);

const PORT = 4000;
app.listen(PORT, () =>
  console.log(`Server läuft auf http://localhost:${PORT}`)
);