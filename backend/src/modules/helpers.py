import json
from datetime import datetime
from typing import List

from modules.logger import logger


def calculate_age(birth_year: str) -> int:
    try:
        birth_date = datetime.strptime(birth_year, "%Y-%m-%d")
        today = datetime.now()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        return age
    except ValueError:
        logger.error(
            f"Invalid date format for birth year: {birth_year}. "
            f"Expected format is 'yyyy-mm-dd'."
        )
        return -1


def stitch_together(a: str | List[str], b: str | List[str]) -> str:
    # print(f"Stitching together: {a} and {b}")
    res = ""
    if isinstance(a, str):
        a = [a]
    if isinstance(b, str):
        b = [b]
    if a is not None and a != [] and a != [""]:
        res = ", ".join(a)
    if b is not None and b != [] and b != [""]:
        if res:
            res += ", "
        res += ", ".join(b)
    # print(f"Stitched result: {res}")
    return res


def parse_med_server_json(file_path: str) -> tuple[list[str], list[tuple[str, int]]]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = file.read()
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    if not isinstance(data, dict):
        raise ValueError("JSON data must be a dictionary.")

    try:
        experts = data.get("experts", [])
        examinations = data.get("examinations", [])

    except KeyError as e:
        raise ValueError(f"Missing expected key in JSON data: {e}")

    if not isinstance(experts, list) or not isinstance(examinations, list):
        raise ValueError("Expected 'experts' and 'examinations' to be lists.")

    return experts, examinations

def build_system_prompt(
    prompt: str, available_experts: List[any], available_examinations: List[any]
) -> str:
    if available_experts == [] and available_examinations == []:
        logger.info("No available experts or examinations found.")
        return prompt
    expert_string_list = [expert.name for expert in available_experts]
    expert_list = ", ".join(expert_string_list)
    examination_list = ", ".join(
        [f"{exam.name} (Utilization: {exam.utilization})" for exam in available_examinations]
    )
    
    system_prompt = (
        f"{prompt}\n\n"
        "The following information is available:\n"
        f"Available experts: {expert_list}\n"
        f"Available examinations: {examination_list}\n"
    )
    
    print(f"DEBUG: System prompt built: {system_prompt}")  # Debugging output
    return system_prompt
