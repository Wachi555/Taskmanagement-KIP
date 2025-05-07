let patients = ['Ute Russ', 'Hans Weber', 'Uwe Taniz'];

module.exports = {
  // Liefert das komplette Array
  getAll: () => patients,

  // Fügt einen neuen Patienten hinzu
  add: (name) => { 
    patients.push(name); 
  },

  // Entfernt einen Patienten nach Namen
  remove: (name) => {
    patients = patients.filter(p => p !== name);
  }
};
