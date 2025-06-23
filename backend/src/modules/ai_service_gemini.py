# import json
import os

from common.pydantic_models import EvaluationInput, ExtractedContent, LLMResult
from dotenv import load_dotenv
from google import genai
from modules.prompts import build_evaluation_input, evaluation_prompt, extraction_prompt

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError(
        "Gemini API key is not set. Please set the GEMINI_API_KEY environment variable."
    )
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

    if not response.text:
        raise ValueError("No response text found.")
    return ExtractedContent.model_validate_json(response.text)


def generate_anamnesis_response(input_contents: EvaluationInput) -> LLMResult:
    prompt = evaluation_prompt + build_evaluation_input(input_contents)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": LLMResult,
        },
    )
    if not response.text:
        raise ValueError("No response text found.")
    return LLMResult.model_validate_json(response.text)


def ask_anything2(input_text: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=input_text
    )
    if not response.text:
        return "No response text found."
    return response.text
