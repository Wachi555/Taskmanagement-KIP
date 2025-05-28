// src/stores/patient_store.js
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
  // …
];

module.exports = {
  getAll: () => patients.map(p => p.name),
  getDetails: (name) => patients.find(p => p.name === name)
};
