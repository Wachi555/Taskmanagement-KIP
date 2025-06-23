import traceback

from common.pydantic_models import EvaluationInput, LLMResult, ExtractedContent
from interfaces import database as db
from modules.ai_service_openai import extract_contents, generate_anamnesis_response

# from modules.ai_service_gemini import extract_contents, generate_anamnesis_response


# just for testing purposes, this function is not used in the actual application
def process_anamnesis_default(input_text: str) -> LLMResult:
    # Extract text contents and store them in the database
    contents = extract_contents(input_text)
    result = generate_anamnesis_response(contents)  # type: ignore
    return result


def process_anamnesis(input_text: str, current_patient_id: int) -> bool:
    try:
        # Extract text contents and store them in the database
        contents = extract_contents(input_text)
        # contents = ExtractedContent.model_validate_json('{"history":"Der Patient berichtet über übermäßigen Alkoholkonsum.","medications":[],"allergies":[],"additional_notes":""}{"history":"Der Patient berichtet über übermäßigen Alkoholkonsum.","medications":[],"allergies":[],"additional_notes":""}')
        # print(contents.model_dump_json(), flush=True)
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
        result = generate_anamnesis_response(eval_input, available_experts=db.get_available_experts(), available_examinations=db.get_available_examinations())  
        # result = LLMResult.model_validate_json('{"diagnoses":[{"name":"Erkrankung der Atemwege","reason":"Der Patient berichtet Atemnot. Es ist wichtig, Atemwegserkrankungen auszuschließen.","confidence":0.7},{"name":"Infektion","reason":"Die Symptome können mit einer Infektion zusammenhängen.","confidence":0.5}],"examinations":[{"name":"Blutbild","priority":5},{"name":"Lungenröntgen","priority":4}],"treatments":["Ruhe und Flüssigkeitszufuhr","Mögliche Verabreichung von Antibiotika bei Bestätigung einer bakteriellen Infektion"],"experts":[{"type":"Hausarzt"},{"type":"Pulmologe"}]}')
        # print(result.model_dump_json(), flush=True)
        db.save_anamnesis_response(current_patient_id, result, input_text)  # type: ignore
        print(f"Response form extract_contents: {contents}", flush=True)
        print(f"Response from generate_anamnesis_response: {result}", flush=True)
        return True

    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        return False
