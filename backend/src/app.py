# import json
import os
import tempfile
from typing import Dict

import uvicorn
from common.pydantic_models import (  # LLMResult,
    InputAnamnesis,
    InputPatient,
    OutputModel,
    UpdatePatient,
)
from database.session import init_db
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from interfaces import database as db
from modules.logger import logger
from modules.processing import process_anamnesis  # , process_anamnesis_default
from modules.STT_service_whisper import whisper_model

# from modules.debug import test_output

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["default"])
async def main() -> Dict[str, str]:
    return {"message": "Hello World"}


# ==================== Processing routes ========================
# @app.post("/process_input", tags=["processing"])
# async def process_input_default(input_model: InputAnamnesis):
#     try:
#         response = process_anamnesis_default(input_model.text)
#     except Exception as e:
#         logger.error(f"Error processing input: {e}")
#         return {
#             "output": "Failed to process input",
#             "success": False,
#             "error_code": 500,
#             "error_message": str(e),
#         }
#     logger.debug(f"Processed input: {input_model.text}")
#     logger.debug(f"Response: {response}")
#     return response


@app.post("/process_input/{selected_patient_id}", tags=["processing"])
async def process_input(
    input_model: InputAnamnesis, selected_patient_id: int
) -> OutputModel:
    try:
        process_anamnesis(input_model.text, selected_patient_id)

    except Exception as e:
        logger.error(f"Error processing input for patient {selected_patient_id}: {e}")
        return OutputModel(
            output="Failed to process input",
            success=False,
            error=str(e),
            status_code=500,
        )

    logger.debug(
        f"Processed input for patient {selected_patient_id}: {input_model.text}"
    )

    try:
        patient = db.get_patient(selected_patient_id)
        patient_entry = db.get_latest_patient_entry(selected_patient_id)
        result = db.get_latest_result_for_entry(patient_entry.id)  # type: ignore
        diagnoses = db.get_diagnoses_for_entry(result.id)  # type: ignore
        examinations = result.examinations  # type: ignore
        experts = result.experts  # type: ignore
        treatments = result.treatments  # type: ignore

    except Exception as e:
        logger.error(f"Error retrieving data for patient {selected_patient_id}: {e}")
        return OutputModel(
            output="Failed to retrieve patient data",
            success=False,
            error=str(e),
            status_code=500,
        )

    logger.debug(f"Retrieved data for patient ID {selected_patient_id}:")
    logger.debug(f"Patient: {patient}")
    logger.debug(f"Patient Entry: {patient_entry}")
    logger.debug(f"Result: {result}")
    logger.debug(f"Diagnoses: {diagnoses}")
    logger.debug(f"Examinations: {examinations}")
    logger.debug(f"Experts: {experts}")
    logger.debug(f"Treatments: {treatments}")

    response = {
        "diagnoses": [
            {"name": d.name, "reason": d.reason, "confidence": d.confidence}
            for d in diagnoses
        ],
        "examinations": [
            {"name": e["name"], "priority": e["priority"]} for e in examinations
        ],
        "treatments": treatments,
        "experts": experts,
        "triage": patient_entry.triage_level,
        "allergies": patient.allergies,
    }
    return OutputModel(output=response)


# @app.post("/process_input_debug", tags=["processing"])
# async def process_input_debug(input_model: InputAnamnesis):
#     return OutputModel(output=json.loads(test_output))


# ==================== STT routes =============================
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> OutputModel:
    try:
        # Get the original extension (e.g. .mp3, .wav, .webm)
        _, ext = os.path.splitext(file.filename)  # type: ignore
        if not ext:
            ext = ".webm"  # fallback
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            temp_audio.write(await file.read())
            temp_audio.flush()
            result = whisper_model.transcribe(temp_audio.name)["text"]

    except Exception as e:
        logger.error(f"Error transcribing audio file: {e}")
        return OutputModel(
            output="Failed to transcribe audio file",
            success=False,
            error=str(e),
            status_code=500,
        )

    logger.debug(f"Transcribed audio file {file.filename} to text: {result}")
    return OutputModel(output=result)


# ==================== Database routes ==========================
# Returns all patients
@app.get("/patients", tags=["database"])
async def get_patients():
    patients = db.get_all_patients()
    if not patients:
        return []

    # patients_dict = {patient.id: patient for patient in patients}
    # Get triage information from patient entries
    for patient in patients:
        patient_id = patient.id
        last_entry = db.get_latest_patient_entry(patient_id)  # type: ignore
        patient.last_triage_level = last_entry.triage_level

    return patients


@app.get("/patient/{patient_id}", tags=["database"])
async def get_patient(patient_id: int):
    patient = db.get_patient(patient_id)
    patient_entry = db.get_latest_patient_entry(patient_id)
    patient.last_triage_level = patient_entry.triage_level
    patient_result = db.get_latest_result_for_entry(patient_entry.id)  # type: ignore
    diagnoses = db.get_diagnoses_for_entry(patient_result.id) if patient_result else []  # type: ignore
    result_dict = {
        "patient": patient,
        "latest_entry": patient_entry,
        "latest_result": patient_result,
        "diagnoses": diagnoses,
    }
    if patient:
        return result_dict
    else:
        return {
            "output": "Patient not found",
            "success": False,
            "error_code": 404,
            "error_message": "Patient not found",
        }


@app.post("/patient", tags=["database"])
async def insert_patient(input_model: InputPatient):
    patient_id = db.add_patient(input_model)
    if patient_id:
        return {
            "output": f"Patient with ID {patient_id} inserted successfully",
            "success": True,
        }
    else:
        return {
            "output": "Failed to insert patient",
            "success": False,
            "error_code": 500,
            "error_message": "Database error",
        }


@app.delete("/patient/{patient_id}", tags=["database"])
async def delete_patient(patient_id: int):
    success = db.remove_patient(patient_id)
    if success:
        return {
            "output": f"Patient with ID {patient_id} deleted successfully",
            "success": True,
        }
    else:
        return {
            "output": "Failed to delete patient",
            "success": False,
            "error_code": 500,
            "error_message": "Database error",
        }


@app.get("/patient/{patient_id}/history", tags=["database"])
async def get_patient_history(patient_id: int):
    res = []
    entries = db.get_patient_entries(patient_id)
    if entries:
        for entry in entries:
            result = db.get_latest_result_for_entry(entry.id)  # type: ignore
            res.append([entry, result])
        return res
    else:
        return {
            "output": "No entries found for this patient",
            "success": False,
            "error_code": 404,
            "error_message": "No entries found",
        }


@app.get(
    "/patient/update_status/{patient_id}/{status}",
    tags=["database"],
    description="Update patient status. Status: 0 = in history, 1 = waiting, 2 = in treatment",
)
async def update_patient_status(patient_id: int, status: int):
    if status not in [0, 1, 2]:
        return {
            "output": "Invalid status",
            "success": False,
            "error_code": 400,
            "error_message": "Status must be 0 (in history), 1 (waiting), or 2 (in treatment)",
        }
    success = db.update_patient(
        patient_id, is_waiting=(status == 1), in_treatment=(status == 2)
    )
    if success:
        return {
            "output": f"Patient with ID {patient_id} updated successfully",
            "success": True,
        }
    else:
        return {
            "output": "Failed to update patient",
            "success": False,
            "error_code": 500,
            "error_message": "Database error",
        }


@app.get("/patient/{patient_id}/set_triage/{triage_level}", tags=["database"])
async def set_patient_triage(patient_id: int, triage_level: int):
    if triage_level < 0 or triage_level > 5:
        return {
            "output": "Invalid triage level",
            "success": False,
            "error_code": 400,
            "error_message": "Triage level must be between 0 and 5",
        }
    success = db.update_patient(patient_id, triage_level=triage_level)
    if success:
        return {
            "output": f"Patient with ID {patient_id} triage level updated to {triage_level}",
            "success": True,
        }
    else:
        return {
            "output": "Failed to update patient triage level",
            "success": False,
            "error_code": 500,
            "error_message": "Database error",
        }


# Update patient data
@app.post("/patient/update/{patient_id}", tags=["database"])
async def update_patient_data(patient_id: int, input_model: UpdatePatient):
    print(
        f"DEBUG: Updating patient with ID {patient_id} with data: {input_model}",
        flush=True,
    )
    success = db.update_patient(
        patient_id,
        first_name=input_model.first_name,
        last_name=input_model.last_name,
        # gender=input_model.gender,
        date_of_birth=input_model.date_of_birth,
        health_insurance=input_model.health_insurance,
        address=input_model.address,
        # triage_level=input_model.triage_level
    )
    if success:
        return {
            "output": f"Patient with ID {patient_id} updated successfully",
            "success": True,
        }
    else:
        return {
            "output": "Failed to update patient",
            "success": False,
            "error_code": 500,
            "error_message": "Database error",
        }


@app.get("/insert_example_patients", tags=["database"])
async def insert_example_patients():
    example_patients = [
        {
            "first_name": "Json",
            "last_name": "Derulo",
            "gender": "männlich",
            "date_of_birth": "1999-02-13",
            "health_insurance": "krasse kasse",
            "allergies": "",
            "address": "123 Straße",
            "triage_level": 2,
            "symptoms": "Mangelnde Motivation",
        },
        {
            "first_name": "Ute",
            "last_name": "Russ",
            "gender": "weiblich",
            "date_of_birth": "2002-02-20",
            "health_insurance": "volle versicherung",
            "allergies": "",
            "address": "OTH Regensburg",
            "triage_level": 3,
            "symptoms": "Absolut keine Lust mehr",
        },
        {
            "first_name": "Timo",
            "last_name": "Blaumann",
            "gender": "männlich",
            "date_of_birth": "2003-03-03",
            "health_insurance": "absolute absicherer",
            "allergies": "",
            "address": "Vergessen",
            "triage_level": 1,
            "symptoms": "akute Alkoholsucht",
        },
    ]
    for patient in example_patients:
        db.add_patient(InputPatient(**patient))
    return {
        "output": f"{len(example_patients)} example patients inserted successfully",
        "success": True,
    }


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)
