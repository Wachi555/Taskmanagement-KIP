from common.pydantic_models import EvaluationInput

extraction_prompt = """
You are given a german text about a patient in a hospital.
Your task is to extract all of the following information that the text contains.
If the text does not contain a certain information, just leave it blank.
Do not try and come up with information that is not provided in the text.
1. History
2. Medications
3. Allergies
4. Additional Notes
Keep the answers in the german language.
Here is the text:
"""

evaluation_prompt = """
You are a medical assistant. You are given information about a patient in a hospital.

Your task is to identify the following data based on the information provided:
1. required examinations: Each examination should have a name and a priority from 1 to 5, where 5 is the highest and 1 is the lowest priority.
2. possible diagnoses: Each diagnosis should have a name, a confidence score between 0 and 1, and a reason for why you think the patient is affected by this disease or situation.
3. treatments: A list of treatments that should be applied to the patient. These can be medications, therapies, or other treatments.
4. the required experts: A list of experts that should be consulted for the patient. Each expert should have a type, such as "Cardiologist", "Neurologist", etc.

There can be multiple examinations with the same priority, since the priority is not used to compare examinations, but to decide which patient needs it first.
Keep all results in the german language.
"""


def build_evaluation_input(input_contents: EvaluationInput) -> str:
    patient_info = (
        f"Age: {input_contents.age}\n"
        if input_contents.age > -1
        else "Age: Unknown\n"
        f"Symptoms: {', '.join(input_contents.symptoms)}\n"
        f"History: {input_contents.history}\n"
        f"Medications: {', '.join(input_contents.medications)}\n"
        f"Allergies: {', '.join(input_contents.allergies)}\n"
        f"Additional Notes: {input_contents.additional_notes}"
    )
    return patient_info
