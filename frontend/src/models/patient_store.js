// src/models/patient_store.js
let patients = [
  {
    name: 'Ute Russ',
    dob: '12.05.1975',
    gender: 'w',
    symptoms: ['Husten','Fieber'],
    history: [
      { date: '2023-11-01', event: 'Grippe' },
      { date: '2022-08-15', event: 'Magen-Darm-Infekt' }
    ]
  },
  {
    name: 'Hans Weber',
    dob: '02.11.1968',
    gender: 'm',
    symptoms: ['Brustschmerzen'],
    history: []
  },
  {
    name: 'Uwe Taniz',
    dob: '01.01.1990',
    gender: 'm',
    symptoms: ['Atemnot'],
    history: []
  }
];

module.exports = {
  getAll: () => patients.map(p => p.name),
  getDetails: (name) => patients.find(p => p.name === name)
};
