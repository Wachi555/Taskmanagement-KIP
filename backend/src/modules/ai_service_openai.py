import os

from common.pydantic_models import EvaluationInput, ExtractedContent, LLMResult
from dotenv import load_dotenv
from modules.prompts import build_evaluation_input, evaluation_prompt, extraction_prompt
from openai import OpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(
        "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
    )
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"
client = OpenAI(base_url=endpoint, api_key=openai_api_key)


def extract_contents(input_text: str) -> ExtractedContent:
    response = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": extraction_prompt,
            },
            {
                "role": "user",
                "content": input_text,
            },
        ],
        model=model_name,
        # temperature=0.7,
        response_format=ExtractedContent,
    )
    result = response.choices[0].message.parsed

    if result:
        return result
    raise ValueError("No response text found.")


def generate_anamnesis_response(input_contents: EvaluationInput) -> LLMResult:
    try:
        user_prompt = build_evaluation_input(input_contents)
        response = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": evaluation_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            model=model_name,
            # temperature=0.7,
            response_format=LLMResult,
        )
        result = response.choices[0].message.parsed
        if result:
            return result
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error while trying to generate a response for the anamnesis: {e}")
        print(f"Input contents: {input_contents}")
        raise e
