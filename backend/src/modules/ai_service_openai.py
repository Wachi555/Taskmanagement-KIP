import os
from dotenv import load_dotenv
from openai import OpenAI
from modules.prompts import test_prompt
from common import OutputContent

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(base_url=endpoint, api_key=openai_api_key)

def generate_anamnesis_response(input_text: str) -> str:
    try: 
        response = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": test_prompt,
                },
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model=model_name,
            # temperature=0.7,
            response_format=OutputContent,
        )
        result = response.choices[0].message.parsed
        if result:
            return result
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error while trying to generate a response for the anamnesis: {e}")
        return "An error occurred while processing your request."

