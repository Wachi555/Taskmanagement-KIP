import json
from datetime import datetime
from typing import Dict, List, Optional

import database.crud_diagnoses as crud_diagnoses
import database.crud_examinations as crud_examinations
import database.crud_experts as crud_experts
import database.crud_patient_entries as crud_patient_entries
import database.crud_patients as crud_patients
import database.crud_results as crud_results
from common.pydantic_models import ExtractedContent, InputPatient, LLMResult
from database.orm_models import (
    Diagnosis,
    Examination,
    Expert,
    Patient,
    PatientEntry,
    Result,
)
from modules.helpers import calculate_age, stitch_together


# --- General Database Functions ---
def save_extracted_contents(patient_id: int, contents: ExtractedContent):
    """
    Save the extracted contents from the LLM to the latest patient entry and update the
    patient's allergies.

    Args:
        patient_id (int): The ID of the patient whose entry is being updated.
        contents (ExtractedContent): The extracted contents from the LLM, containing
            patient history, additional notes, medications, symptoms, allergies, and
            history.
    """
    latest_entry = get_latest_patient_entry(patient_id)
    crud_patient_entries.update_patient_entry(
        latest_entry.id,  # type: ignore
        extracted_contents_json=contents.model_dump_json(),
        patient_history=stitch_together(latest_entry.patient_history, contents.history),  # type: ignore
        additional_notes=stitch_together(
            latest_entry.additional_notes, contents.additional_notes  # type: ignore
        ),
        medications=stitch_together(latest_entry.medications, contents.medications),  # type: ignore
        symptoms=stitch_together(latest_entry.symptoms, contents.symptoms),  # type: ignore
    )

    patient = get_patient(patient_id)
    crud_patients.update_patient(
        patient_id, allergies=stitch_together(patient.allergies, contents.allergies)  # type: ignore
    )


def save_anamnesis_response(patient_id: int, response: LLMResult, anamnesis_text: str):
    """
    Save the response from the LLM to the latest patient entry and create a new result
    for the patient.

    Args:
        patient_id (int): The ID of the patient whose entry is being updated.
        response (LLMResult): The response from the LLM, containing experts,
            examinations, treatments, and diagnoses.
        anamnesis_text (str): The text of the anamnesis provided by the LLM.
    """
    latest_entry = get_latest_patient_entry(patient_id)
    experts_string_list = [expert.type for expert in response.experts]
    examinations_dict_list = [
        {"name": examination.name, "priority": examination.priority}
        for examination in response.examinations
        if examination
    ]
    examinations_string_list = [
        json.dumps(examination) for examination in examinations_dict_list if examination
    ]
    result_id = crud_results.create_result(
        latest_entry.id,  # type: ignore
        ", ".join(experts_string_list),
        "; ".join(examinations_string_list),
        treatments=", ".join(response.treatments),
    )
    update_patient_entry(
        latest_entry.id, latest_result_id=result_id, anamnesis_text=anamnesis_text  # type: ignore
    )

    # Create diagnoses for the result
    for diagnosis in response.diagnoses:
        crud_diagnoses.create_diagnosis(
            result_id, diagnosis.name, diagnosis.reason, diagnosis.confidence  # type: ignore
        )


# --- Patient Management ---
def add_patient(patient: InputPatient) -> int:
    """
    Add a new patient to the database. If the patient already exists, update their
    information.

    Args:
        patient (InputPatient): The patient data to be added or updated.

    Returns:
        patient_id (int): The ID of the patient that was added or updated.
    """
    try:
        existing_patient = crud_patients.get_patient_by_name_and_dob(
            patient.first_name, patient.last_name, patient.date_of_birth
        )
    except ValueError:
        # Patient does not exist, continue with creation
        age = calculate_age(patient.date_of_birth)
        patient_id = crud_patients.create_patient(
            patient.first_name,
            patient.last_name,
            patient.gender,
            age,
            patient.date_of_birth,
            is_waiting=True,
            in_treatment=False,
            health_insurance=patient.health_insurance,
            allergies=None,
            address=patient.address,
        )
    else:
        # Patient already exists, update their information
        age = calculate_age(existing_patient.date_of_birth)  # type: ignore
        crud_patients.update_patient(
            existing_patient.id,  # type: ignore
            age=age,
            is_waiting=True,
            in_treatment=False,
            health_insurance=patient.health_insurance,
            address=patient.address,
            last_triage_level=patient.triage_level,
        )
        patient_id = existing_patient.id

    # Create a new patient entry for the newly added or updated patient
    entry_id = crud_patient_entries.create_patient_entry(
        patient_id,  # type: ignore
        entry_date=datetime.now().date().strftime("%Y-%m-%d"),
        patient_history="",
        additional_notes="",
        extracted_contents_json="",
        symptoms=patient.symptoms,
        medications="",
        triage_level=patient.triage_level,
        anamnesis_text="",
    )
    update_patient(patient_id, latest_entry_id=entry_id)  # type: ignore
    return patient_id  # type: ignore


def get_patient(patient_id: int) -> Patient:
    """
    Get a patient by their ID and calculate their age based on their date of birth.

    Args:
        patient_id (int): The ID of the patient to retrieve.

    Returns:
        patient (Patient): The patient object with the specified ID.
    """
    patient = crud_patients.get_patient_by_id(patient_id)
    patient_age = calculate_age(patient.date_of_birth)  # type: ignore
    patient.age = patient_age  # type: ignore
    update_patient(patient_id, age=patient.age)
    return patient


def get_all_patients() -> List[Patient]:
    """
    Get all patients from the database and calculate their ages based on their date of
    birth.

    Returns:
        patients (List[Patient]): A list of all patients with their ages calculated.
    """
    patients = crud_patients.get_all_patients()
    for patient in patients:
        patient_age = calculate_age(patient.date_of_birth)  # type: ignore
        patient.age = patient_age  # type: ignore
        update_patient(patient.id, age=patient_age)  # type: ignore
    return patients


def remove_patient(patient_id: int):
    """
    Remove a patient from the database by their ID.

    Args:
        patient_id (int): The ID of the patient to remove.
    """
    crud_patients.delete_patient(patient_id)


def update_patient(patient_id: int, **kwargs):
    """
    Update a patient's information in the database.

    Args:
        patient_id (int): The ID of the patient to update.
        **kwargs: The fields to update.
    """
    crud_patients.update_patient(patient_id, **kwargs)
    latest_entry = get_latest_patient_entry(patient_id)
    crud_patient_entries.update_patient_entry(
        latest_entry.id, triage_level=kwargs.get("triage_level")  # type: ignore
    )


# --- Patient Entry Management ---
def get_patient_entries(patient_id: int) -> List[PatientEntry]:
    """
    Get all entries for a patient by their ID.

    Args:
        patient_id (int): The ID of the patient whose entries are to be retrieved.

    Returns:
        entries (List[PatientEntry]): A list of all entries for the specified patient.
    """
    entries = crud_patient_entries.get_patient_entries(patient_id)
    return entries


def get_latest_patient_entry(patient_id: int) -> PatientEntry:
    """
    Get the latest entry for a patient by their ID.

    Args:
        patient_id (int): The ID of the patient whose latest entry is to be retrieved.

    Returns:
        entry (PatientEntry): The latest entry for the specified patient.
    """
    patient = crud_patients.get_patient_by_id(patient_id)
    if patient.latest_entry_id is None:
        raise ValueError(f"No entries found for patient with ID {patient_id}.")
    entry = crud_patient_entries.get_patient_entry(patient.latest_entry_id)  # type: ignore
    return entry


def get_patient_entry(entry_id: int) -> PatientEntry:
    """
    Get a specific patient entry by its ID.

    Args:
        entry_id (int): The ID of the patient entry to retrieve.

    Returns:
        entry (PatientEntry): The patient entry with the specified ID.
    """
    entry = crud_patient_entries.get_patient_entry(entry_id)
    return entry


def add_patient_entry(
    patient_id: int,
    entry_date: str,
    patient_history: str,
    additional_notes: str,
    extracted_contents_json: str,
    symptoms: str,
    medications: str,
    triage_level: int,
    anamnesis_text: str,
    latest_result_id: Optional[int] = None,
) -> int:
    """
    Add a new entry for a patient.

    Args:
        patient_id (int): The ID of the patient for whom the entry is being created.
        entry_date (str): The date of the entry in 'YYYY-MM-DD' format.
        patient_history (str): The patient's medical history.
        additional_notes (str): Any additional notes related to the patient.
        extracted_contents_json (str): JSON string containing extracted contents from
            LLM.
        symptoms (str): The symptoms reported by the patient.
        medications (str): The medications taken by the patient.
        triage_level (int): The triage level assigned to the patient.
        anamnesis_text (str): The anamnesis text provided by the LLM.
        latest_result_id (Optional[int]): The ID of the latest result associated with
            this entry.

    Returns:
        entry_id (int): The ID of the newly created patient entry.
    """
    entry_id = crud_patient_entries.create_patient_entry(
        patient_id,
        entry_date,
        patient_history,
        additional_notes,
        extracted_contents_json,
        symptoms,
        medications,
        triage_level,
        anamnesis_text=anamnesis_text,
        latest_result_id=latest_result_id,
    )
    return entry_id


def update_patient_entry(
    entry_id: int,
    entry_date: Optional[str] = None,
    patient_history: Optional[str] = None,
    additional_notes: Optional[str] = None,
    extracted_contents_json: Optional[str] = None,
    symptoms: Optional[str] = None,
    medications: Optional[str] = None,
    triage_level: Optional[int] = None,
    anamnesis_text: Optional[str] = None,
    latest_result_id: Optional[int] = None,
):
    """
    Update an existing entry for a patient.

    Args:
        entry_id (int): The ID of the patient entry to update.
        entry_date (Optional[str]): The date of the entry in 'YYYY-MM-DD' format.
        patient_history (Optional[str]): The patient's medical history.
        additional_notes (Optional[str]): Any additional notes related to the patient.
        extracted_contents_json (Optional[str]): JSON string containing extracted
            contents from LLM.
        symptoms (Optional[str]): The symptoms reported by the patient.
        medications (Optional[str]): The medications taken by the patient.
        triage_level (Optional[int]): The triage level assigned to the patient.
        anamnesis_text (Optional[str]): The anamnesis text provided by the LLM.
        latest_result_id (Optional[int]): The ID of the latest result associated with
            this entry.
    """
    crud_patient_entries.update_patient_entry(
        entry_id,
        entry_date=entry_date,
        patient_history=patient_history,
        additional_notes=additional_notes,
        extracted_contents_json=extracted_contents_json,
        symptoms=symptoms,
        medications=medications,
        triage_level=triage_level,
        anamnesis_text=anamnesis_text,
        latest_result_id=latest_result_id,
    )


def remove_patient_entry(entry_id: int):
    """
    Remove a patient entry by its ID.

    Args:
        entry_id (int): The ID of the patient entry to remove.
    """
    crud_patient_entries.delete_patient_entry(entry_id)


# --- Diagnosis Management ---
def get_diagnoses_for_entry(entry_id: int) -> List[Diagnosis]:
    """
    Get all diagnoses for a patient entry by its ID.

    Args:
        entry_id (int): The ID of the patient entry whose diagnoses are to be retrieved.

    Returns:
        diagnoses (List[Diagnosis]): A list of diagnoses associated with the specified patient
            entry.
    """
    diagnoses = crud_diagnoses.get_diagnoses_for_entry(entry_id)
    return diagnoses  # type: ignore


def add_diagnosis_to_entry(
    entry_id: int, name: str, reason: str, confidence: float
) -> int:
    """
    Add a diagnosis to a patient entry.

    Args:
        entry_id (int): The ID of the patient entry to which the diagnosis is being
            added.
        name (str): The name of the diagnosis.
        reason (str): The reason for the diagnosis.
        confidence (float): The confidence level of the diagnosis.

    Returns:
        diagnosis_id (int): The ID of the newly created diagnosis.
    """
    diagnosis_id = crud_diagnoses.create_diagnosis(entry_id, name, reason, confidence)
    return diagnosis_id


def remove_diagnosis_from_entry(diagnosis_id: int):
    """
    Remove a diagnosis from a patient entry by its ID.

    Args:
        diagnosis_id (int): The ID of the diagnosis to remove.
    """
    crud_diagnoses.delete_diagnosis(diagnosis_id)


# --- Result Management ---
def get_results_for_entry(entry_id: int) -> List[Result]:
    """
    Get all results for a patient entry by its ID.

    Args:
        entry_id (int): The ID of the patient entry whose results are to be retrieved.

    Returns:
        results (List[Result]): A list of results associated with the specified patient
            entry.
    """
    results = crud_results.get_results_by_patient_entry_id(entry_id)
    for result in results:
        exams = result.examinations
        exams = (
            [json.loads(exam.strip()) for exam in exams.split("; ") if exam]
            if exams  # type: ignore
            else []
        )
        result.examinations = exams  # type: ignore
    return results


def get_latest_result_for_entry(entry_id: int) -> Optional[Result]:
    """
    Get the latest result for a patient entry by its ID.

    Args:
        entry_id (int): The ID of the patient entry whose latest result is to be
            retrieved.

    Returns:
        result (Optional[Result]): The latest result associated with the specified patient entry.
    """
    entry = crud_patient_entries.get_patient_entry(entry_id)
    if entry.latest_result_id is None:
        return None
    result = crud_results.get_result_by_id(entry.latest_result_id)  # type: ignore
    exams = result.examinations
    exams = (
        [json.loads(exam.strip()) for exam in exams.split("; ") if exam]
        if exams  # type: ignore
        else []
    )
    result.examinations = exams  # type: ignore
    return result


def add_result_to_entry(
    entry_id: int, experts: str, examinations: str, treatments: str
) -> int:
    """
    Add a new result to a patient entry.

    Args:
        entry_id (int): The ID of the patient entry to which the result is being added.
        experts (str): A string containing the names of experts involved in the result.
        examinations (str): A string containing the names of examinations conducted.
        treatments (str): A string containing the treatments recommended or
            administered.

    Returns:
        result_id (int): The ID of the newly created result.
    """
    result_id = crud_results.create_result(entry_id, experts, examinations, treatments)
    return result_id


def remove_result_from_entry(result_id: int):
    """
    Remove a result from a patient entry by its ID.

    Args:
        result_id (int): The ID of the result to remove.
    """
    crud_results.delete_result(result_id)


# --- Experts Management ---
def get_available_experts() -> List[Expert]:
    """
    Get all available experts from the database.

    Returns:
        experts (List[Expert]): A list of available experts.
    """
    experts = crud_experts.get_available_experts()
    return experts


def store_experts(experts: List[str]):
    """
    Store a list of experts in the database. This will remove all existing experts and
    add the new ones.

    Args:
        experts (List[str]): A list of expert names to be stored in the database.
    """
    crud_experts.remove_all_experts()
    for expert in experts:
        crud_experts.create_expert(name=expert, is_available=True)


def get_expert(expert_id: int) -> Expert:
    """
    Get an expert by their ID.

    Args:
        expert_id (int): The ID of the expert to retrieve.

    Returns:
        expert (Expert): The expert object with the specified ID.
    """
    expert = crud_experts.get_expert_by_id(expert_id)
    return expert


def get_all_experts() -> List[Expert]:
    """
    Get all experts from the database.

    Returns:
        experts (List[Expert]): A list of all experts.
    """
    experts = crud_experts.get_all_experts()
    return experts


def add_expert(name: str, is_available: bool) -> int:
    """
    Add a new expert to the database.

    Args:
        name (str): The name of the expert to be added.
        is_available (bool): Availability status of the expert.

    Returns:
        expert_id (int): The ID of the newly created expert.
    """
    expert_id = crud_experts.create_expert(name, is_available)
    return expert_id


def remove_expert(expert_id: int):
    """
    Remove an expert from the database by their ID.

    Args:
        expert_id (int): The ID of the expert to remove.
    """
    crud_experts.delete_expert(expert_id)


# --- Examination Management ---
def store_examinations(examinations: List[Dict[str, int]]):
    """
    Store a list of examinations in the database. This will remove all existing
    examinations and add the new ones.

    Args:
        examinations (List[Dict[str, int]]): A list of dictionaries containing
            examination names and their utilization.
    """
    crud_examinations.remove_all_examinations()
    for examination in examinations:
        crud_examinations.create_examination(
            name=examination["name"],  # type: ignore
            is_available=True,
            utilization=examination["auslastung"],
        )


def get_available_examinations() -> List[Examination]:
    """
    Get all available examinations from the database.

    Returns:
        examinations (List[Examination]): A list of available examinations.
    """
    examinations = crud_examinations.get_available_examinations()
    return examinations


def get_all_examinations() -> List[Examination]:
    """
    Get all examinations from the database.

    Returns:
        examinations (List[Examination]): A list of all examinations.
    """
    examinations = crud_examinations.get_all_examinations()
    return examinations


def get_examination_by_id(examination_id: int) -> Examination:
    """
    Get an examination by its ID.

    Args:
        examination_id (int): The ID of the examination to retrieve.

    Returns:
        examination (Examination): The examination object with the specified ID.
    """
    examination = crud_examinations.get_examination_by_id(examination_id)
    return examination


def add_examination(name: str, utilization: int, is_available: bool) -> int:
    """
    Add a new examination to the database.

    Args:
        name (str): The name of the examination to be added.
        utilization (int): The utilization percentage of the examination.
        is_available (bool): Availability status of the examination.

    Returns:
        examination_id (int): The ID of the newly created examination.
    """
    examination_id = crud_examinations.create_examination(
        name, utilization, is_available
    )
    return examination_id


def remove_examination(examination_id: int):
    """
    Remove an examination from the database by its ID.

    Args:
        examination_id (int): The ID of the examination to remove.
    """
    crud_examinations.delete_examination(examination_id)
