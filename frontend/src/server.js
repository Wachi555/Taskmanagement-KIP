// src/server.js

const path       = require('path');
const express    = require('express');
const { engine } = require('express-handlebars');

const homeRoutes    = require('./controllers/home');
const patientRoutes = require('./routes/patients');

const app = express();

// Handlebars konfigurieren mit formatDate Helper
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
    }
  }
}));
app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));

// Static-Files und Body-Parser
app.use(express.static(path.join(__dirname, '../public')));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Routen einbinden
app.use('/', homeRoutes);
app.use('/', patientRoutes);

const PORT = 4000;
app.listen(PORT, () =>
  console.log(`Server läuft auf http://localhost:${PORT}`)
);
