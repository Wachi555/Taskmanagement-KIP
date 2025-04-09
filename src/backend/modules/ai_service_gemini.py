import os
from dotenv import load_dotenv
from google import genai
from backend.common import OutputContent
from backend.modules.prompts import test_prompt
import json

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Gemini API key is not set. Please set the GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=gemini_api_key)

def generate_anamnesis_response(input_text: str) -> str:
    try: 
        prompt = f"Your task is the following: <{test_prompt}>\n\nNow with that task, handle the following patient:\n<{input_text}>"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': OutputContent,
            },
        )
        if response.text:
            return json.loads(response.text)
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error while trying to generate a response for the anamnesis: {e}")
        return "An error occurred while processing your request."

def ask_anything2(input_text: str) -> str:
    try: 
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=input_text
        )
        if response.text:
            return response.text
        else:
            return "No response text found."
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."
