from modules import process_anamnesis, test_output
from common import InputModel, OutputModel


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
    print(type(response))
    print(response)
    return OutputModel(
        output=response
    )

@app.post("/process_input_debug")
async def process_input_debug(input_text: InputModel):
    return OutputModel(output=json.loads(test_output))

# @app.post("/ask_anything")
# async def ask_anything(input_text: InputModel):
#     response = ask_anything2(input_text.text)
#     return {"output": response}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=False)
