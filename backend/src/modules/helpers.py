import json
from datetime import datetime
from typing import List, Tuple

from modules.logger import logger


def calculate_age(birth_year: str) -> int:
    """
    Calculate the age based on the provided birth year in 'yyyy-mm-dd' format.

    Args:
        birth_year (str): The birth date in 'yyyy-mm-dd' format.

    Returns:
        age (int): The calculated age. Returns -1 if the date format is invalid.
    """
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
            f"Invalid date format for birth year: {birth_year}. Expected format is "
            f"'yyyy-mm-dd'."
        )
        return -1


def stitch_together(a: str | List[str], b: str | List[str]) -> str:
    """
    Stitch together two strings or lists of strings into a single string, separating
    them with a comma and space. If either input is None or empty, the result will be an
    empty string.

    Args:
        a (str | List[str]): The first string or list of strings.
        b (str | List[str]): The second string or list of strings.

    Returns:
        res (str): A single string containing the concatenated values of a and b,
            separated by a comma and space. If both a and b are empty or None, returns
            an empty string.
    """
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
    return res


def parse_med_server_json(file_path: str) -> Tuple[List[str], List[Tuple[str, int]]]:
    """
    Parse a JSON file containing medical server data to extract available experts and
    examinations.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        experts, examinations (Tuple[List[str], List[Tuple[str, int]]]): A tuple
            containing a list of expert names and a list of tuples with examination
            names and their utilization rates.
    """
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
    prompt: str, available_experts: List, available_examinations: List
) -> str:
    """
    Build a system prompt that includes the provided prompt and lists of available
    experts and examinations. If no experts or examinations are available, it returns
    the original prompt.

    Args:
        prompt (str): The initial prompt to be included in the system prompt.
        available_experts (List): A list of available experts, where each expert has a
            'name' attribute.
        available_examinations (List): A list of available examinations, where each
            examination has a 'name' and 'utilization' attribute.

    Returns:
        system_prompt (str): The constructed system prompt that includes the initial
            prompt and the lists of available experts and examinations.
    """
    if available_experts == [] and available_examinations == []:
        logger.info("No available experts or examinations found.")
        return prompt
    expert_string_list = [expert.name for expert in available_experts]
    expert_list = ", ".join(expert_string_list)
    examination_list = ", ".join(
        [
            f"{exam.name} (Utilization: {exam.utilization})"
            for exam in available_examinations
        ]
    )

    system_prompt = (
        f"{prompt}\n\n"
        "The following information is available:\n"
        f"Available experts: {expert_list}\n"
        f"Available examinations: {examination_list}\n"
    )
    return system_prompt
