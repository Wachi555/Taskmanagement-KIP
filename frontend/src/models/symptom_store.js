// Einfaches Mapping von Patient → Liste von Symptomen
const data = {
  'Ute Russ': ['Husten', 'Fieber'],
  'Hans Weber': ['Kopfschmerz'],
  'Uwe Taniz': []
};

module.exports = {
  getFor: (name) => {
    return data[name] || [];
  }
};
