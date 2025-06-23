import requests
import pytest
from hypothesis import given, strategies as st
from src.modules.helpers import calculate_age, stitch_together, parse_med_server_json

# CONFIG
BACKEND_URL = "http://localhost:8000"

# ========== API TESTS ==========

def test_main_route():
    r = requests.get(f"{BACKEND_URL}/")
    assert r.status_code == 200
    assert "message" in r.json()

@pytest.mark.parametrize("triage_level", [-1, 6, 999])
def test_set_patient_triage_invalid_levels(triage_level):
    r = requests.get(f"{BACKEND_URL}/patient/1/set_triage/{triage_level}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False or data["output"] == "Invalid triage level"

def test_insert_example_patients():
    r = requests.get(f"{BACKEND_URL}/insert_example_patients")
    assert r.status_code == 200
    assert r.json().get("success") is True

def test_get_patients():
    r = requests.get(f"{BACKEND_URL}/patients")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_transcribe_empty_file():
    files = {'file': ('empty.wav', b'')}
    r = requests.post(f"{BACKEND_URL}/transcribe", files=files)
    assert r.status_code in [200, 422, 500]

# ========== HELPER TESTS ==========

@pytest.mark.parametrize("date_str,expected", [
    ("2000-01-01", lambda x: x >= 0),
    ("3000-01-01", lambda x: x < 0),  # future date
    ("invalid-date", lambda x: x == -1),
])
def test_calculate_age_cases(date_str, expected):
    result = calculate_age(date_str)
    assert expected(result)

@pytest.mark.parametrize("a,b,expected", [
    ("foo", "bar", "foo, bar"),
    (["foo"], ["bar"], "foo, bar"),
    ("foo", ["bar", "baz"], "foo, bar, baz"),
    ([], [], ""),
    ("", "", ""),
])
def test_stitch_together_various(a, b, expected):
    assert stitch_together(a, b) == expected

def test_parse_med_server_json_valid():
    test_json = '{"experts": ["Dr. A"], "tests_treatments": [["X-Ray", 2]]}'
    experts, tests = parse_med_server_json(test_json)
    assert experts == ["Dr. A"]
    assert tests == [["X-Ray", 2]]

@pytest.mark.parametrize("bad_json", ["", "{", "[]", '{"experts": "notalist"}'])
def test_parse_med_server_json_invalid(bad_json):
    with pytest.raises(ValueError):
        parse_med_server_json(bad_json)

# ========== EDGE-CASE DB TESTS ==========

def test_update_patient_status_invalid_status():
    r = requests.get(f"{BACKEND_URL}/patient/update_status/1/999")
    assert r.status_code == 200
    assert r.json()["success"] is False or "Invalid status" in r.json()["output"]

# ========== PROCESSING TESTS ==========

@pytest.mark.parametrize("text", ["", "Normal symptoms"])
def test_process_input_debug(text):
    payload = {"text": text}
    r = requests.post(f"{BACKEND_URL}/process_input_debug", json=payload)
    assert r.status_code == 200
    assert "output" in r.json()

