from common.orm_models import Patient, Entry

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

example_patients = [
  Patient(
    id=1,
    first_name="Hans",
    last_name="Müller",
    age=32,
    date_of_birth="1993-01-01",
    entries=[
      Entry(
        id=1,
        entry_date="2023-10-01",
        entry_text="Patient reports abdominal pain and nausea."
      ),
      Entry(
        id=2,
        entry_date="2023-10-02",
        entry_text="Patient has a history of gastroenteritis."
      )
    ]
  ),
  Patient(
    id=2,
    first_name="Jane",
    last_name="Smith",
    age=25,
    date_of_birth="1998-05-15",
    entries=[
      Entry(
        id=3,
        entry_date="2023-10-03",
        entry_text="Patient has a family history of diabetes."
      ),
      Entry(
        id=4,
        entry_date="2023-10-04",
        entry_text="Patient reports fatigue and increased thirst."
      )
    ]
  )
]