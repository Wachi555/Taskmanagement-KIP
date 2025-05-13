# from modules.ai_service_gemini import generate_anamnesis_response, extract_contents
from modules.ai_service_openai import generate_anamnesis_response, extract_contents


def process_anamnesis(input_text: str) -> str:
    try:
        print("DEBUG: Extracting contents from input text")
        contents = extract_contents(input_text)
        print(f"DEBUG: Extracted contents: {contents}")
        result = generate_anamnesis_response(contents)
        if result:
            return result
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."
