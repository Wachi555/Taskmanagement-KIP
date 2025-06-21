from modules.ai_service_gemini import generate_anamnesis_response, extract_contents
#from modules.ai_service_openai import generate_anamnesis_response, extract_contents
from interfaces import database as db
from common.pydantic_models import EvaluationInput

import traceback


# just for testing purposes, this function is not used in the actual application
def process_anamnesis_default(input_text: str) -> str:
    # Extract text contents and store them in the database
    contents = extract_contents(input_text)
    result = generate_anamnesis_response(contents)
    if result:
        return result

def process_anamnesis(input_text: str, current_patient_id: int) -> str:
    try:
        # Extract text contents and store them in the database
        contents = extract_contents(input_text)
        db.save_extracted_contents(current_patient_id, contents)
        
        # Process the extracted contents
        patient = db.get_patient(current_patient_id)
        latest_entry = db.get_latest_patient_entry(current_patient_id)
        eval_input = EvaluationInput(
            age=patient.age,
            symptoms=latest_entry.symptoms.split(", ") if latest_entry.symptoms else [],
            history=latest_entry.patient_history if latest_entry.patient_history else "",
            medications=latest_entry.medications.split(", ") if latest_entry.medications else [],
            allergies=patient.allergies.split(", ") if patient.allergies else [],
            additional_notes=latest_entry.additional_notes if latest_entry.additional_notes else ""
        )
        result = generate_anamnesis_response(eval_input)
        db.save_anamnesis_response(current_patient_id, result)
        print(f"Response form extract_contents: {contents}", flush=True)
        print(f"Response from generate_anamnesis_response: {result}", flush=True)
        if result:
            return True
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return False
