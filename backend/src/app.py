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
    return patients

@app.get("/patient/{patient_id}", tags=["database"])
async def get_patient(patient_id: int):
    patient = db.get_patient(patient_id)
    if patient:
        return patient
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



if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)