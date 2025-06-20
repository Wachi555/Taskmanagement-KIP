// Mapping von Patient → Historische Besuche
const data = {
  'Ute Russ': [
    { date: '2023-11-01', event: 'Grippe' },
    { date: '2022-08-15', event: 'Magen-Darm-Infekt' }
  ],
  'Hans Weber': [],
  'Uwe Taniz': [
    { date: '2024-02-20', event: 'Bänderriss' }
  ]
};

module.exports = {
  getFor: (name) => {
    return data[name] || [];
  }
};
