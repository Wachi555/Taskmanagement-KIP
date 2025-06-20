import json

import uvicorn
from common.pydantic_models import InputAnamnesis, InputPatient, OutputModel
from interfaces import database as db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.debug import test_output
from modules.processing import process_anamnesis
from database.session import init_db

app = FastAPI()
init_db()

# TODO: Add ResponseModels -> Success: bool, Error-messages, etc.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["default"])
async def main():
    return {"message": "Hello World"}

# ==================== Processing routes ========================

@app.post("/process_input/{selected_patient_id}", tags=["processing"])
async def process_input(input_model: InputAnamnesis, selected_patient_id: int):
    response = process_anamnesis(input_model.text, selected_patient_id)
    return OutputModel(output=response)


@app.post("/process_input_debug", tags=["processing"])
async def process_input_debug(input_model: InputAnamnesis):
    return OutputModel(output=json.loads(test_output))

# ==================== Database routes ==========================

# Returns all patients
@app.get("/patients", tags=["database"])
async def get_patients():
    patients = db.get_all_patients()
    if not patients:
        return []

    patients_dict = {patient.id: patient for patient in patients}
    # Get triage information from patient entries
    for patient in patients:
        patient_id = patient.id
        last_entry = db.get_latest_patient_entry(patient_id)
        triage_level = last_entry.triage_level if last_entry else -1
        patient.last_triage_level = triage_level

    return patients

@app.get("/patient/{patient_id}", tags=["database"])
async def get_patient(patient_id: int):
    patient = db.get_patient(patient_id)
    patient_entry = db.get_latest_patient_entry(patient_id)
    if patient_entry:
        patient.last_triage_level = patient_entry.triage_level
    else:
        patient.last_triage_level = -1
    patient_result = db.get_results_for_entry(patient_entry.id) if patient_entry else None # TODO: Handle multiple results
    patient_result = patient_result[0] if patient_result else None
    result_dict = {
        "patient": patient,
        "latest_entry": patient_entry,
        "latessult": patient_result
    }
    if patient:
        return result_dict
    else:
        return {"output": "Patient not found", "success": False, "error_code": 404, "error_message": "Patient not found"}

@app.post("/patient", tags=["database"])
async def insert_patient(input_model: InputPatient):
    patient_id = db.add_patient(input_model)
    if patient_id:
        return {"output": f"Patient with ID {patient_id} inserted successfully", "success": True}
    else:
        return {"output": "Failed to insert patient", "success": False, "error_code": 500, "error_message": "Database error"}

@app.delete("/patient/{patient_id}", tags=["database"])
async def delete_patient(patient_id: int):
    success = db.remove_patient(patient_id)
    if success:
        return {"output": f"Patient with ID {patient_id} deleted successfully", "success": True}
    else:
        return {"output": "Failed to delete patient", "success": False, "error_code": 500, "error_message": "Database error"}

@app.get("/patient/{patient_id}/entries", tags=["database"])
async def get_patient_entries(patient_id: int):
    entries = db.get_patient_entries(patient_id)
    if entries:
        return entries
    else:
        return {"output": "No entries found for this patient", "success": False, "error_code": 404, "error_message": "No entries found"}

@app.get("/patient/update_status/{patient_id}/{status}", tags=["database"], description="Update patient status. Status: 0 = in history, 1 = waiting, 2 = in treatment")
async def update_patient_status(patient_id: int, status: int):
    if status not in [0, 1, 2]:
        return {"output": "Invalid status", "success": False, "error_code": 400, "error_message": "Status must be 0 (in history), 1 (waiting), or 2 (in treatment)"}
    success = db.update_patient(patient_id, is_waiting=(status == 1), in_treatment=(status == 2))
    if success:
        return {"output": f"Patient with ID {patient_id} updated successfully", "success": True}
    else:
        return {"output": "Failed to update patient", "success": False, "error_code": 500, "error_message": "Database error"}

@app.get("/patient/{patient_id}/set_triage/{triage_level}", tags=["database"])
async def set_patient_triage(patient_id: int, triage_level: int):
    if triage_level < 0 or triage_level > 5:
        return {"output": "Invalid triage level", "success": False, "error_code": 400, "error_message": "Triage level must be between 0 and 5"}
    success = db.update_patient(patient_id, triage_level=triage_level)
    if success:
        return {"output": f"Patient with ID {patient_id} triage level updated to {triage_level}", "success": True}
    else:
        return {"output": "Failed to update patient triage level", "success": False, "error_code": 500, "error_message": "Database error"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)