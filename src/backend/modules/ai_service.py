import os
from dotenv import load_dotenv
from google import genai
from common import OutputContent

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

def initialize_gemini_api():
    if not gemini_api_key:
        raise ValueError("Gemini API key is not set. Please set the GEMINI_API_KEY environment variable.")
    print("Gemini API initialized successfully.")

def process_anamnesis(input_text: str) -> str:
    try: 
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=input_text,
            config={
                'response_mime_type': 'application/json',
                'response_schema': OutputContent,
            },
        )
        if response.text:
            return response.text
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error: {e}")
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
