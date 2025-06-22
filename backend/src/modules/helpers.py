import json
from datetime import datetime
from typing import List


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
        print(
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
    if a is not None and a != []:
        res = ", ".join(a)
    if b is not None and b != []:
        if res:
            res += ", "
        res += ", ".join(b)
    # print(f"Stitched result: {res}")
    return res


def parse_med_server_json(json_data: str) -> tuple[list[str], list[tuple[str, int]]]:
    """
    Parses the JSON data from the medical server and returns a list of experts and the
    available test/treatments.

    Args:
        json_data (str): The JSON data as a string.

    Returns:
        tuple: A tuple containing two lists - experts and tests/treatments with their
            current usage (occupancy).
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
