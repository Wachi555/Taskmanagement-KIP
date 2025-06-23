import json
from datetime import datetime
from typing import List, Optional

import database.crud_diagnoses as crud_diagnoses
import database.crud_examinations as crud_examinations
import database.crud_experts as crud_experts
import database.crud_patient_entries as crud_patient_entries
import database.crud_patients as crud_patients
import database.crud_results as crud_results

# import database.crud_medications as crud_medications
# import database.crud_symptoms as crud_symptoms
from common.pydantic_models import (  # Examination,; Expert,
    ExtractedContent,
    InputPatient,
    LLMResult,
)
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
    latest_entry = get_latest_patient_entry(patient_id)
    crud_patient_entries.update_patient_entry(
        latest_entry.id,  # type: ignore
        extracted_contents_json=contents.model_dump_json(),
        patient_history=stitch_together(latest_entry.patient_history, contents.history),  # type: ignore
        additional_notes=stitch_together(
            latest_entry.additional_notes, contents.additional_notes  # type: ignore
        ),
        medications=stitch_together(latest_entry.medications, contents.medications),  # type: ignore
    )

    patient = get_patient(patient_id)
    crud_patients.update_patient(
        patient_id, allergies=stitch_together(patient.allergies, contents.allergies)  # type: ignore
    )


def save_anamnesis_response(patient_id: int, response: LLMResult):
    # # Create new result in database:
    # # TODO: Remove this when Openai is used again
    # response.experts = [Expert(type="Allgemeinmedizin"), Expert(type="Dermatologie")]
    # response.examinations = [
    #     Examination(name="Hautuntersuchung", priority=1),
    #     Examination(name="Blutuntersuchung", priority=2),
    # ]
    # response.diagnoses = [
    #     Diagnosis(name="Hautausschlag", reason="Allergische Reaktion", confidence=0.85),
    # ]
    # response.treatments = ["Antihistaminikum", "Kühlen der betroffenen Stelle"]
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
    update_patient_entry(latest_entry.id, latest_result_id=result_id)  # type: ignore
    # res = crud_results.get_result_by_id(result_id)

    # Create diagnoses for the result
    for diagnosis in response.diagnoses:
        crud_diagnoses.create_diagnosis(
            result_id, diagnosis.name, diagnosis.reason, diagnosis.confidence  # type: ignore
        )


# --- Patient Management ---
# Add a patient to the database
def add_patient(patient: InputPatient) -> int:
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
    # TODO: Actually input data instead of empty strings
    crud_patient_entries.create_patient_entry(
        patient_id,  # type: ignore
        entry_date=datetime.now().date().strftime("%Y-%m-%d"),  # TODO: Check format
        patient_history="",
        additional_notes="",
        extracted_contents_json="",
        symptoms=patient.symptoms,
        medications="",
        triage_level=patient.triage_level,
    )
    return patient_id  # type: ignore


# Get a patient by ID
def get_patient(patient_id: int) -> Patient:
    patient = crud_patients.get_patient_by_id(patient_id)
    patient_age = calculate_age(patient.date_of_birth)  # type: ignore
    patient.age = patient_age  # type: ignore
    update_patient(patient_id, age=patient.age)
    return patient


# Get all patients
def get_all_patients() -> List[Patient]:
    patients = crud_patients.get_all_patients()
    for patient in patients:
        patient_age = calculate_age(patient.date_of_birth)  # type: ignore
        patient.age = patient_age  # type: ignore
        update_patient(patient.id, age=patient_age)  # type: ignore
    return patients


# Remove patient from the database
def remove_patient(patient_id: int):
    crud_patients.delete_patient(patient_id)


# Update patient information
def update_patient(patient_id: int, **kwargs):
    crud_patients.update_patient(patient_id, **kwargs)
    latest_entry = get_latest_patient_entry(patient_id)
    crud_patient_entries.update_patient_entry(
        latest_entry.id, triage_level=kwargs.get("triage_level")  # type: ignore
    )


# --- Patient Entry Management ---
# Get all entries for a patient
def get_patient_entries(patient_id: int) -> List[PatientEntry]:
    entries = crud_patient_entries.get_patient_entries(patient_id)
    return entries


# Get the latest entry for a patient
def get_latest_patient_entry(patient_id: int) -> PatientEntry:
    entry = crud_patient_entries.get_latest_patient_entry(patient_id)
    return entry


# Get a specific entry for a patient
def get_patient_entry(entry_id: int) -> PatientEntry:
    entry = crud_patient_entries.get_patient_entry(entry_id)
    return entry


# Add an entry for a patient
# TODO: Not utilized yet
def add_patient_entry(
    patient_id: int,
    entry_date: str,
    patient_history: str,
    additional_notes: str,
    extracted_contents_json: str,
    symptoms: str,
    medications: str,
    triage_level: int,
    latest_result_id: Optional[int] = None,
) -> int:
    entry_id = crud_patient_entries.create_patient_entry(
        patient_id,
        entry_date,
        patient_history,
        additional_notes,
        extracted_contents_json,
        symptoms,
        medications,
        triage_level,
        latest_result_id=latest_result_id,
    )
    return entry_id


# Update an entry for a patient
def update_patient_entry(
    entry_id: int,
    entry_date: Optional[str] = None,
    patient_history: Optional[str] = None,
    additional_notes: Optional[str] = None,
    extracted_contents_json: Optional[str] = None,
    symptoms: Optional[str] = None,
    medications: Optional[str] = None,
    triage_level: Optional[int] = None,
    latest_result_id: Optional[int] = None,
):
    crud_patient_entries.update_patient_entry(
        entry_id,
        entry_date=entry_date,
        patient_history=patient_history,
        additional_notes=additional_notes,
        extracted_contents_json=extracted_contents_json,
        symptoms=symptoms,
        medications=medications,
        triage_level=triage_level,
        latest_result_id=latest_result_id,
    )


# Remove an entry for a patient
def remove_patient_entry(entry_id: int):
    crud_patient_entries.delete_patient_entry(entry_id)


# # --- Symptom Management ---
# # Get all symptoms for a patient entry
# def get_symptoms_for_entry(entry_id: int):
#     symptoms = crud_symptoms.get_symptoms_for_entry(entry_id)
#     if symptoms:
#         return symptoms
#     else:
#         ...


# # Add a symptom to a patient entry
# def add_symptom_to_entry(entry_id: int, symptom_data):
#     symptom_id = crud_symptoms.create_symptom(entry_id, symptom_data)
#     if symptom_id:
#         return symptom_id
#     else:
#         ...


# # Remove a symptom from a patient entry
# def remove_symptom_from_entry(symptom_id: int):
#     success = crud_symptoms.delete_symptom(symptom_id)
#     if success:
#         return True
#     else:
#         ...


# # --- Medication Management ---
# # Get all medications for a patient entry
# def get_medications_for_entry(entry_id: int):
#     medications = crud_medications.get_medications_for_entry(entry_id)
#     if medications:
#         return medications
#     else:
#         ...


# # Add a medication to a patient entry
# def add_medication_to_entry(entry_id: int, name: str, dosage: str):
#     medication_id = crud_medications.create_medication(entry_id, name, dosage)
#     if medication_id:
#         return medication_id
#     else:
#         ...


# # Remove a medication from a patient entry
# def remove_medication_from_entry(medication_id: int):
#     success = crud_medications.delete_medication(medication_id)
#     if success:
#         return True
#     else:
#         ...


# --- Diagnosis Management ---
# Get all diagnoses for a patient entry
def get_diagnoses_for_entry(entry_id: int) -> List[Diagnosis]:
    diagnoses = crud_diagnoses.get_diagnoses_for_entry(entry_id)
    return diagnoses  # type: ignore


# Add a diagnosis to a patient entry
def add_diagnosis_to_entry(
    entry_id: int, name: str, reason: str, confidence: float
) -> int:
    diagnosis_id = crud_diagnoses.create_diagnosis(entry_id, name, reason, confidence)
    return diagnosis_id


# Remove a diagnosis from a patient entry
def remove_diagnosis_from_entry(diagnosis_id: int):
    crud_diagnoses.delete_diagnosis(diagnosis_id)


# --- Result Management ---
# Get all results for a patient entry
def get_results_for_entry(entry_id: int) -> List[Result]:
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


# Get the latest result for a patient entry
def get_latest_result_for_entry(entry_id: int) -> Optional[Result]:
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


# Add a result to a patient entry
def add_result_to_entry(
    entry_id: int, experts: str, examinations: str, treatments: str
):
    result_id = crud_results.create_result(entry_id, experts, examinations, treatments)
    return result_id


# Remove a result from a patient entry
def remove_result_from_entry(result_id: int):
    crud_results.delete_result(result_id)


# --- Experts Management ---
# Get an expert by ID
def get_expert(expert_id: int) -> Expert:
    expert = crud_experts.get_expert_by_id(expert_id)
    return expert


# Get all experts
def get_all_experts() -> List[Expert]:
    experts = crud_experts.get_all_experts()
    return experts


# Add an expert to the database
def add_expert(name: str, is_available: bool) -> int:
    expert_id = crud_experts.create_expert(name, is_available)
    return expert_id


# Remove an expert from the database
def remove_expert(expert_id: int):
    crud_experts.delete_expert(expert_id)


# # Get experts for result
# def get_experts_for_result(result_id: int):
#     experts = crud_experts.get_experts_for_result(result_id)
#     if experts:
#         return experts
#     else:
#         ...


# # Add an expert to a result
# def add_expert_to_result(result_id: int, expert_data):
#     expert_id = crud_experts.create_expert(result_id, expert_data)
#     if expert_id:
#         return expert_id
#     else:
#         ...


# # Remove an expert from a result
# def remove_expert_from_result(expert_id: int, result_id: int):
#     success = crud_experts.remove_expert_from_result(expert_id, result_id)
#     if success:
#         return True
#     else:
#         ...


# --- Examination Management ---
def get_all_examinations() -> List[Examination]:
    examinations = crud_examinations.get_all_examinations()
    return examinations


def get_examination_by_id(examination_id: int) -> Examination:
    examination = crud_examinations.get_examination_by_id(examination_id)
    return examination


# Add an examination to the database
def add_examination(name: str, is_available: bool) -> int:
    examination_id = crud_examinations.create_examination(name, is_available)
    return examination_id


# Remove an examination from the database
def remove_examination(examination_id: int):
    crud_examinations.delete_examination(examination_id)


# # Get all examinations for a result
# def get_examinations_for_result(result_id: int):
#     examinations = crud_examinations.get_examinations_for_result(result_id)
#     if examinations:
#         return examinations
#     else:
#         ...


# # Add an examination to a result
# def add_examination_to_result(examination_id: int, result_id: int):
#     examination_id = crud_examinations.add_examination_to_result(
#         examination_id, result_id
#     )
#     if examination_id:
#         return examination_id
#     else:
#         ...


# # Remove an examination from a result
# def remove_examination_from_result(examination_id: int, result_id: int):
#     success = crud_examinations.remove_examination_from_result(
#         examination_id, result_id
#     )
#     if success:
#         return True
#     else:
#         ...
