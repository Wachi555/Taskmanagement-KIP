from modules import *
from common import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

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
async def process_input(input_text: InputModel):
    response = process_anamnesis(input_text.text)
    return OutputModel(
        output=json.loads(response)
    )

@app.post("/ask_anything")
async def ask_anything(input_text: InputModel):
    response = ask_anything2(input_text.text)
    return {"output": response}


if __name__ == "__main__":
    initialize_gemini_api()
    uvicorn.run(app, port=8000, reload=False)
