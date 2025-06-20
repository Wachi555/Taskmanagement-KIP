import json

import uvicorn
from common.models import InputModel, OutputModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from modules.debug import test_output
from modules.processing import process_anamnesis
import whisper
import tempfile
import os

app = FastAPI()

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


@app.post("/process_input")
async def process_input(input_model: InputModel):
    response = process_anamnesis(input_model.text)
    print(type(response))
    print(response, flush=True)
    return OutputModel(output=response)


@app.post("/process_input_debug")
async def process_input_debug(input_model: InputModel):
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

# @app.post("/ask_anything")
# async def ask_anything(input_text: InputModel):
#     response = ask_anything2(input_text.text)
#     return {"output": response}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)
