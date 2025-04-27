from common.models import EvaluationInput

extraction_prompt = """
You are given a german text about a patient in a hospital. 
Your task is to extract all of the following information that the text contains. 
If the text does not contain a certain information, just leave it blank. 
Do not try and come up with information that is not provided in the text.
1. Name
2. Date of Birth
3. Age
4. Symptoms
5. History
6. Medications
7. Allergies
8. Family History
9. Additional Notes
Keep the answers in the german language.
Here is the text: 
"""

evaluation_prompt = """
You are a medical assistant. You are given information about a patient in a hospital.
Your task is to identify the required examinations, possible diseases and medications based on the information provided.
Give each examination a priority from 1 to 5, where 5 is the highest priority.
There can be multiple examinations with the same priority, since the priority is not used to compare examinations, but to decide which patient needs it first.
For the diagnosis, provide the name and a confidence score between 0 and 1 as well as the reason for why you think the patient is affected by this disease or situation.
Keep the results in german.
"""

def build_evaluation_input(input_contents: EvaluationInput) -> str:
    patient_info = (
        # f"Age: {input_contents['age']}\n"
        # f"Symptoms: {', '.join(input_contents['symptoms'])}\n"
        # f"History: {input_contents['history']}\n"
        # f"Medications: {', '.join(input_contents['medications'])}\n"
        # f"Allergies: {', '.join(input_contents['allergies'])}\n"
        # f"Family History: {input_contents['family_history']}\n"
        # f"Additional Notes: {input_contents['additional_notes']}"
        f"Age: {input_contents.age}\n"
        f"Symptoms: {', '.join(input_contents.symptoms)}\n"
        f"History: {input_contents.history}\n"
        f"Medications: {', '.join(input_contents.medications)}\n"
        f"Allergies: {', '.join(input_contents.allergies)}\n"
        f"Family History: {input_contents.family_history}\n"
        f"Additional Notes: {input_contents.additional_notes}"
    )
    return patient_info