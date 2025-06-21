from datetime import datetime
from typing import List
import json


def calculate_age(birth_year: str) -> int:
    try:
        birth_date = datetime.strptime(birth_year, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        print(f"Invalid date format for birth year: {birth_year}. Expected format is 'yyyy-mm-dd'.")
        return -1

def stitch_together(a: List[str], b: List[str]) -> str:
    res = ""
    if a is not None and a != []:
        res = ", ".join(a)
    if b is not None and b != []:
        if res:
            res += ", "
        res += ", ".join(b)
    return res if res else "n/a"
    
def parse_med_server_json(json_data: str) -> tuple[list[str], list[tuple[str, int]]]:
    """
    Parses the JSON data from the medical server and returns a list of experts and the available test/treatments.
    
    Args:
        json_data (str): The JSON data as a string.
        
    Returns:
        tuple: A tuple containing two lists - experts and tests/treatments with their current usage (ocupancy).
    """
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
  
    if not isinstance(data, dict):
        raise ValueError("JSON data must be a dictionary.")

    try:
        experts = data.get("experts", [])
        tests_treatments = data.get("tests_treatments", [])

    except KeyError as e:
        raise ValueError(f"Missing expected key in JSON data: {e}")
    
    if not isinstance(experts, list) or not isinstance(tests_treatments, list):
        raise ValueError("Expected 'experts' and 'tests_treatments' to be lists.")
    
    return experts, tests_treatments