test_output = """
{
  "diagnosis": [
    {
      "name": "Gastroenteritis",
      "reason": "The patient's abdominal pain could indicate an inflammation of the stomach or intestines due to a viral or bacterial infection.",
      "confidence": 0.7
    },
    {
      "name": "Peptic Ulcer Disease",
      "reason": "Persistent abdominal pain is a common symptom of ulcers in the stomach or intestines.",
      "confidence": 0.6
    }
  ],
  "examinations": [
    {
      "name": "Physical examination of the abdomen",
      "priority": 5
    },
    {
      "name": "Abdominal ultrasound",
      "priority": 4
    },
    {
      "name": "Complete blood count",
      "priority": 4
    },
    {
      "name": "Stool analysis",
      "priority": 3
    }
  ],
  "treatments": [
    "Antiemetics for nausea",
    "Pain relievers for abdominal pain",
    "Proton pump inhibitors for possible ulcer symptoms"
  ],
  "symptoms": [
    "Abdominal pain"
  ]
}
"""
