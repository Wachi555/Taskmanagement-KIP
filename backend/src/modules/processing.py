# from modules.ai_service_gemini import generate_anamnesis_response, extract_contents
from modules.ai_service_openai import generate_anamnesis_response, extract_contents
from interfaces import database as db
import datetime


def process_anamnesis(input_text: str, current_patient_id: int) -> str:
    try:
        # Extract text contents and store them in the database
        contents = extract_contents(input_text)
        # TODO: Create new patient entry in database with the extracted contents as json
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        entry_id = db.add_patient_entry(current_patient_id, current_date, contents.history, contents.additional_notes, contents.model_dump_json())
        # TODO: Save upper database part to database
        symptoms = contents.symptoms
        for symptom in symptoms:
            db.add_symptom_to_entry(entry_id, symptom, current_date)
        medications = contents.medications
        for medication in medications:
            db.add_medication_to_entry(entry_id, medication, "N/A") # Dosage not implemented yet
        allergies = contents.allergies
        # TODO: Allergy implementation in db
        ...
        
        # Process the extracted contents
        result = generate_anamnesis_response(contents)
        # TODO: Save result in database
        if result:
            return result
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."
