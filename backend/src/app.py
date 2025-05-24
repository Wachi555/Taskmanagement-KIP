import json

import uvicorn
# from backend.src.modules import crud as crud
# from backend.src.common.pydantic_models import InputModel, OutputModel
from common.pydantic_models import InputAnamnesis, InputPatient, OutputModel
from modules import crud
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.debug import test_output
from modules.processing import process_anamnesis
from modules.database import init_db
from fastapi import UploadFile, File
import whisper
import tempfile
import os



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


@app.get("/")
async def main():
    return {"message": "Hello World"}

# ==================== Processing routes ========================

@app.post("/process_input")
async def process_input(input_model: InputAnamnesis):
    response = process_anamnesis(input_model.text)
    print(type(response))
    print(response, flush=True)
    return OutputModel(output=response)


@app.post("/process_input_debug")
async def process_input_debug(input_model: InputAnamnesis):
    print(input_model.text, flush=True)
    return OutputModel(output=json.loads(test_output))


# ==================== STT routes =============================

model = whisper.load_model("base") # Options: tiny, base, small, medium, large

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Get the original extension (e.g. .mp3, .wav, .webm)
    _, ext = os.path.splitext(file.filename)
    if not ext:
        ext = ".webm"  # fallback
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(await file.read())
        temp_audio.flush()
        result = model.transcribe(temp_audio.name)
    return {"transcription": result["text"]}


# ==================== Database routes ==========================

@app.get("/patients")
async def get_patients():
    patients = crud.get_all_patients()
    return OutputModel(output=patients)


@app.get("/patient/{patient_id}")
async def get_patient(patient_id: int):
    patient = crud.get_patient_by_id(patient_id)
    if patient:
        return OutputModel(output=patient)
    else:
        return OutputModel(output="", success=False, error_code=404, error_message="Patient not found")


@app.post("/patient")
async def create_patient(input_model: InputPatient):
    patient_id = crud.create_patient(input_model.first_name, input_model.last_name, input_model.date_of_birth, input_model.age)
    patient = crud.get_patient_by_id(patient_id)
    if patient:
        return OutputModel(output=patient)
    else:
        return OutputModel(output="", success=False, error_code=500, error_message="Failed to create patient")


@app.delete("/patient/{patient_id}")
async def delete_patient(patient_id: int):
    success = crud.delete_patient(patient_id)
    if success:
        return OutputModel(output="", success=True)
    else:
        return OutputModel(output="", success=False, error_code=404, error_message="Patient not found")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)
