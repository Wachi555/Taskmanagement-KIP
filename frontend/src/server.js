// src/server.js

const path       = require('path');
const express    = require('express');
const { engine } = require('express-handlebars');

const homeRoutes    = require('./controllers/home');
const patientRoutes = require('./routes/patients');
const audioCtrl     = require('./controllers/audio');

const app = express();

// 1) Body-Parser für JSON und URL-encoded (Forms)
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// 2) Handlebars konfigurieren mit allen Helpers
app.engine('hbs', engine({
  extname:    '.hbs',
  layoutsDir: path.join(__dirname, 'views', 'layouts'),
  partialsDir: path.join(__dirname, 'views', 'partials'),
  helpers: {
    eq: (a, b) => a === b,
    encodeURI: s => encodeURIComponent(s),
    encodeURIComponent: s => encodeURIComponent(s),
    formatDate: dateString => {
      if (!dateString) return '';
      const [year, month, day] = dateString.split('-');
      return `${day}.${month}.${year}`;
    },
    sortByTriage: patients => {
      if (!patients) return [];
      const arr = Array.isArray(patients) ? patients : Object.values(patients);
      return arr.slice().sort((a, b) => (Number(a.triage) || 0) - (Number(b.triage) || 0));
    }
  }
}));
app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));

// 3) Audio-Controller (falls er eigene Routen hat)
app.use('/', audioCtrl);

// 4) Haupt-Router
app.use('/', homeRoutes);
app.use('/', patientRoutes);

// 5) Statische Dateien (CSS, JS, Bilder)
app.use(express.static(path.join(__dirname, '../public')));

// 6) 404-Catch-All (muss ganz am Ende stehen)
app.use((req, res) => {
  res.status(404).render('404');  // lege in views/404.hbs eine entsprechende Seite an
});

// Server starten
const PORT = 4000;
app.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
});
