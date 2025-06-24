from common.pydantic_models import EvaluationInput
from interfaces import database as db

# from modules.ai_service_gemini import extract_contents, generate_anamnesis_response
from modules.ai_service_openai import extract_contents, generate_anamnesis_response
from modules.logger import logger


def process_anamnesis(input_text: str, current_patient_id: int):
    """
    Process the anamnesis input text for a given patient. This function extracts
    relevant information from the input text, builds an evaluation input, and generates
    an anamnesis response using the AI service. The results are saved in the database.

    Args:
        input_text (str): The input text containing anamnesis information.
        current_patient_id (int): The ID of the patient for whom the anamnesis is being
            processed.
    """
    # Extract text contents and store them in the database
    contents = extract_contents(input_text)
    logger.debug(f"Response from extract_contents: {contents}")
    db.save_extracted_contents(current_patient_id, contents)

    # Process the extracted contents
    patient = db.get_patient(current_patient_id)
    latest_entry = db.get_latest_patient_entry(current_patient_id)
    eval_input = EvaluationInput(
        age=patient.age,  # type: ignore
        symptoms=latest_entry.symptoms.split(", ") if latest_entry.symptoms else [],  # type: ignore
        history=(
            latest_entry.patient_history if latest_entry.patient_history else ""  # type: ignore
        ),
        medications=(
            latest_entry.medications.split(", ") if latest_entry.medications else []  # type: ignore
        ),
        allergies=patient.allergies.split(", ") if patient.allergies else [],  # type: ignore
        additional_notes=(
            latest_entry.additional_notes if latest_entry.additional_notes else ""  # type: ignore
        ),
    )
    # Build the evaluation input from the extracted contents
    result = generate_anamnesis_response(
        eval_input,
        available_experts=db.get_available_experts(),
        available_examinations=db.get_available_examinations(),
    )
    logger.debug(f"Response from generate_anamnesis_response: {result}")
    db.save_anamnesis_response(current_patient_id, result, input_text)  # type: ignore
