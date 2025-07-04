import os
from typing import List

import modules.helpers as helpers
from common.pydantic_models import EvaluationInput, ExtractedContent, LLMResult
from database.orm_models import Examination, Expert
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
    """
    Extract structured content from the input text using a predefined extraction prompt.

    Args:
        input_text (str): The text from which to extract content.

    Returns:
        result (ExtractedContent): The structured content extracted from the input text.
    """
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
        response_format=ExtractedContent,
    )
    result = response.choices[0].message.parsed

    if result:
        return result
    raise ValueError("No response text found.")


def generate_anamnesis_response(
    input_contents: EvaluationInput,
    available_experts: List[Expert],
    available_examinations: List[Examination],
) -> LLMResult:
    """
    Generate a response based on the provided evaluation input and available experts and
    examinations.

    Args:
        input_contents (EvaluationInput): The structured input data for the evaluation.
        available_experts (List[Expert]): List of available experts.
        available_examinations (List[Examination]): List of available examinations.

    Returns:
        result (LLMResult): The generated response from the model.
    """
    user_prompt = build_evaluation_input(input_contents)
    system_prompt = helpers.build_system_prompt(
        evaluation_prompt, available_experts, available_examinations
    )
    response = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        model=model_name,
        response_format=LLMResult,
    )
    result = response.choices[0].message.parsed
    if not result:
        raise ValueError("No response text found.")
    return result
