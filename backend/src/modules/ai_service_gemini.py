import json
import os

from common.pydantic_models import LLMResult, EvaluationInput, ExtractedContent
from dotenv import load_dotenv
from google import genai
from modules.prompts import extraction_prompt, evaluation_prompt, build_evaluation_input

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Gemini API key is not set. Please set the GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=gemini_api_key)

def extract_contents(input_text: str) -> ExtractedContent:
    prompt = extraction_prompt + input_text

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ExtractedContent,
        },
    )

    if response.text:
        return ExtractedContent.model_validate_json(response.text)
        # return json.loads(response.text)
    raise ValueError("No response text found.")

def generate_anamnesis_response(input_contents: EvaluationInput) -> str:
    try:
        prompt = evaluation_prompt + build_evaluation_input(input_contents)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": LLMResult,
            },
        )
        if response.text:
            return LLMResult.model_validate_json(response.text)
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error while trying to generate a response for the anamnesis: {e}")
        print(f"Input contents: {input_contents}")
        raise e


def ask_anything2(input_text: str) -> str:
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=input_text)
        if response.text:
            return response.text
        else:
            return "No response text found."
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."
