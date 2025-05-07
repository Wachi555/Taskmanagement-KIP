const path    = require('path');
const express = require('express');
const { engine } = require('express-handlebars');
const homeCtrl   = require('./src/controllers/home');

const app = express();

app.engine('hbs', engine({
  extname:     '.hbs',
  layoutsDir:  path.join(__dirname, 'src', 'views', 'layouts'),
  partialsDir: path.join(__dirname, 'src', 'views', 'partials'),
  helpers: {
    eq: (a, b) => a === b
  }
}));

app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'src', 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use('/', homeCtrl);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server läuft auf http://localhost:${PORT}`));
