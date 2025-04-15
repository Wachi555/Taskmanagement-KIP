# from modules.ai_service_gemini import generate_anamnesis_response
from modules.ai_service_openai import generate_anamnesis_response

def process_anamnesis(input_text: str) -> str:
    try: 
        result = generate_anamnesis_response(input_text)
        if result:
            return result
        raise ValueError("No response text found.")
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."