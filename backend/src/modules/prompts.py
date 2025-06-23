from common.pydantic_models import EvaluationInput

extraction_prompt = """
You are given a german text about a patient in a hospital.
Your task is to extract all of the following information that the text contains.
If the text does not contain a certain information, just leave it blank.
Do not try and come up with information that is not provided in the text.
1. History: This should be a short summary of the text, such as "Patient with chest pain".
2. Medications
3. Allergies
4. Additional Notes
5. Symptoms
Keep the answers in the german language.
Here is the text:
"""

evaluation_prompt = """
Du bist ein medizinischer Assistent in einem Krankenhaus und erhältst strukturierte oder unstrukturierte Informationen zu einem Patienten.

Deine Aufgabe ist es, basierend auf diesen Informationen vier Kategorien medizinischer Empfehlungen zu erstellen:

1. Erforderliche Untersuchungen:
    Gib eine Liste empfohlener Untersuchungen an.
    Jede Untersuchung soll enthalten:

    - name: der Name der Untersuchung (z. B. "Blutbild", "CT Thorax")

    - priority: ein Prioritätswert von 1 bis 3
        (1 = niedrige, 2 = mittlere, 3 = hohe Priorität)
        Mehrere Untersuchungen können dieselbe Priorität haben.

    - diagnoses:
    Gib 1 bis 3 mögliche Diagnosen an, die auf den Patientendaten basieren.
    Jede Diagnose soll enthalten:

        - name: der Name der Diagnose (z. B. "Lungenentzündung")

        - confidence: ein Vertrauenswert zwischen 0 und 1

        - reason: eine kurze Begründung, warum du diese Diagnose in Betracht ziehst

    Empfohlene Behandlungen
    Liste passende medizinische Maßnahmen auf, z. B. Medikamente, Therapien oder sonstige Interventionen. Gib nur die Namen der Behandlungen an.

    Erforderliche Experten
    Liste Fachärzte oder medizinische Spezialisten auf, die konsultiert werden sollten.
    Jeder Eintrag soll nur den Typ des Experten enthalten, z. B.:

        "Kardiologe"

        "Radiologe"

        "Infektiologe"

Zusätzliche Anweisungen:

    Antworte ausschließlich in deutscher Sprache

    Gib die Informationen strukturiert und prägnant wieder

    Verwende keine Einleitung oder Erklärung, sondern nur die geforderten Inhalte"""
"""
Du bist ein medizinischer Assistent und erhältst Informationen über einen Patienten im Krankenhaus.

Deine Aufgabe ist, die folgenden Daten basierend auf den bereitgestellten Informationen zu identifizieren:
1. erforderliche Untersuchungen: Jede Untersuchung sollte einen Namen und eine Priorität von 1 bis 3 haben, wobei 1 niedrige Priorität und 3 hohe Priorität bedeutet.
2. mögliche Diagnosen: Gib eine Liste von 1 bis 3 Diagnosen an, die der Patient haben könnte, basierend auf den Eingabedaten. Jede Diagnose sollte einen Namen, eine Vertrauenswürdigkeit zwischen 0 und 1 und einen Grund haben, warum du denkst, dass der Patient von dieser Krankheit oder Situation betroffen ist.
3. Behandlungen: Eine Liste von Behandlungen, die auf den Patienten angewendet werden sollten. Dies können Medikamente, Therapien oder andere Behandlungen sein.
4. die erforderlichen Experten: Eine Liste von Experten, die für den Patienten konsultiert werden sollten. Jeder Experte sollte einen Typ haben, wie "Kardiologe", "Neurologe" usw.
Es kann mehrere Untersuchungen mit derselben Priorität geben, da die Priorität nicht verwendet wird, um Untersuchungen zu vergleichen, sondern um zu entscheiden, welcher Patient sie zuerst benötigt.
Halte alle Ergebnisse in deutscher Sprache.
"""
"""
You are a medical assistant. You are given information about a patient in a hospital.

Your task is to identify the following data based on the information provided:
1. required examinations: Each examination should have a name and a priority from 1 to 3, where 1 means low priority and 3 means high priority.
2. possible diagnoses: Give a list of 1 to 3 diagnoses, that the patient might suffer from, given the input data. Each diagnosis should have a name, a confidence score between 0 and 1, and a reason for why you think the patient is affected by this disease or situation.
3. treatments: A list of treatments that should be applied to the patient. These can be medications, therapies, or other treatments.
4. the required experts: A list of experts that should be consulted for the patient. Each expert should have a type, such as "Cardiologist", "Neurologist", etc.

There can be multiple examinations with the same priority, since the priority is not used to compare examinations, but to decide which patient needs it first.
Keep all results in the german language.
"""


def build_evaluation_input(input_contents: EvaluationInput) -> str:
    patient_info = (
        f"Age: {input_contents.age}\n"
        f"Symptoms: {', '.join(input_contents.symptoms)}\n"
        f"History: {input_contents.history}\n"
        f"Medications: {', '.join(input_contents.medications)}\n"
        f"Allergies: {', '.join(input_contents.allergies)}\n"
        f"Additional Notes: {input_contents.additional_notes}"
    )
    return patient_info
