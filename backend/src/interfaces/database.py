import database.crud_patients as crud_patients
import database.crud_paitent_entries as crud_paitent_entries
import database.crud_results as crud_results
import database.crud_symptoms as crud_symptoms
import database.crud_medications as crud_medications
import database.crud_diagnoses as crud_diagnoses
import database.crud_experts as crud_experts
import database.crud_examinations as crud_examinations

from common.pydantic_models import InputPatient

from datetime import datetime

# --- Patient Management ---

# Add a patient to the database
def add_patient(patient: InputPatient) -> int:

    age = 0 # TODO: Calculate age from date_of_birth

    patient_id = crud_patients.create_patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        age=age,
        date_of_birth=patient.date_of_birth,
        is_waiting=True,
        in_treatment=False,  # Default value
        health_insurance=patient.health_insurance,
        allergies=None, # Default value, can be updated later
        address=patient.address
    )
    
    # create initial patient entry
    if patient_id is None:
        print("Error: Could not create patient.")
        return None
    
    entry_id = crud_paitent_entries.create_patient_entry(
        patient_id=patient_id,
        entry_date=datetime.now().date(),  # TODO: Check for correct date format
        patient_history="",
        additional_notes="",
        extracted_contents_json="",  # Empty string for now
        symptoms=patient.symptoms,
        medications="", # Empty string for now
        triage_level=patient.triage_level 
    )

    if entry_id is None:
        print("Error: Could not create initial patient entry.")
        return None
    
    return patient_id 

# Get a patient by ID
def get_patient(patient_id: int):
    patient = crud_patients.get_patient_by_id(patient_id)
    if patient:
        return patient
    else:
        # TODO: Maybe raise an exception or return a specific error message
        # TODO: The none return has to caught in the frontend
        print(f"Error: Patient with ID {patient_id} not found.")
        return None

# Get all patients
def get_all_patients():
    patients = crud_patients.get_all_patients()
    if patients:
        return patients
    else:
        ...

# Remove patient from the database
def remove_patient(patient_id: int):
    success = crud_patients.delete_patient(patient_id)
    if success:
        return True
    else:
        ...

# Update patient information
def update_patient(patient_id: int, patient: InputPatient):
    updated_patient = crud_patients.update_patient(
        patient_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        age=patient.age,
        date_of_birth=patient.date_of_birth,
        is_waiting=patient.is_waiting
    )
    if updated_patient:
        return updated_patient
    else:
        ...

# --- Patient Entry Management ---

# Get all entries for a patient
def get_patient_entries(patient_id: int):
    entries = crud_paitent_entries.get_patient_entries(patient_id)
    if entries:
        return entries
    else:
        ...
        
# Get the latest entry for a patient
def get_latest_patient_entry(patient_id: int):
    entries = crud_paitent_entries.get_patient_entries(patient_id)
    if entries:
        latest_entry = max(entries, key=lambda entry: entry.entry_date)
        return latest_entry
    else:
        ...

# Get a specific entry for a patient
def get_patient_entry(entry_id: int):
    entry = crud_paitent_entries.get_patient_entry(entry_id)
    if entry:
        return entry
    else:
        ...

# Add an entry for a patient
def add_patient_entry(patient_id: int, date: str, patient_history: str, additional_notes: str, symptoms: str, medications: str, content_json: str):
    entry_id = crud_paitent_entries.create_patient_entry(patient_id, date, patient_history, additional_notes, content_json, symptoms, medications)
    if entry_id:
        return entry_id
    else:
        ...
        
# Update an entry for a patient
def update_patient_entry(entry_id: int, entry_data):
    updated_entry = crud_paitent_entries.update_patient_entry(entry_id, entry_data)
    if updated_entry:
        return updated_entry
    else:
        ...
        
# Remove an entry for a patient
def remove_patient_entry(entry_id: int):
    success = crud_paitent_entries.delete_patient_entry(entry_id)
    if success:
        return True
    else:
        ...
        
# --- Symptom Management ---

# Get all symptoms for a patient entry
def get_symptoms_for_entry(entry_id: int):
    symptoms = crud_symptoms.get_symptoms_for_entry(entry_id)
    if symptoms:
        return symptoms
    else:
        ...

# Add a symptom to a patient entry
def add_symptom_to_entry(entry_id: int, symptom_data):
    symptom_id = crud_symptoms.create_symptom(entry_id, symptom_data)
    if symptom_id:
        return symptom_id
    else:
        ...

# Remove a symptom from a patient entry
def remove_symptom_from_entry(symptom_id: int):
    success = crud_symptoms.delete_symptom(symptom_id)
    if success:
        return True
    else:
        ...

# --- Medication Management ---

# Get all medications for a patient entry
def get_medications_for_entry(entry_id: int):
    medications = crud_medications.get_medications_for_entry(entry_id)
    if medications:
        return medications
    else:
        ...
        
# Add a medication to a patient entry
def add_medication_to_entry(entry_id: int, name: str, dosage: str):
    medication_id = crud_medications.create_medication(entry_id, name, dosage)
    if medication_id:
        return medication_id
    else:
        ...
        
# Remove a medication from a patient entry
def remove_medication_from_entry(medication_id: int):
    success = crud_medications.delete_medication(medication_id)
    if success:
        return True
    else:
        ...

# --- Allergy Management ---
# TODO
        
# --- Diagnosis Management ---

# Get all diagnoses for a patient entry
def get_diagnoses_for_entry(entry_id: int):
    diagnoses = crud_diagnoses.get_diagnoses_for_entry(entry_id)
    if diagnoses:
        return diagnoses
    else:
        ...
        
# Add a diagnosis to a patient entry
def add_diagnosis_to_entry(entry_id: int, diagnosis_data):
    diagnosis_id = crud_diagnoses.create_diagnosis(entry_id, diagnosis_data)
    if diagnosis_id:
        return diagnosis_id
    else:
        ...

# Remove a diagnosis from a patient entry
def remove_diagnosis_from_entry(diagnosis_id: int):
    success = crud_diagnoses.delete_diagnosis(diagnosis_id)
    if success:
        return True
    else:
        ...
        
# --- Result Management ---

# Get all results for a patient entry
def get_results_for_entry(entry_id: int):
    results = crud_results.get_results_by_patient_entry_id(entry_id)
    if results:
        return results
    else:
        ...
        
# Add a result to a patient entry
def add_result_to_entry(entry_id: int, result_data):
    result_id = crud_results.create_result(entry_id, result_data)
    if result_id:
        return result_id
    else:
        ...
        
# Remove a result from a patient entry
def remove_result_from_entry(result_id: int):
    success = crud_results.delete_result(result_id)
    if success:
        return True
    else:
        ...
        
# --- Experts Management ---

def get_expert(expert_id: int):
    expert = crud_experts.get_expert_by_id(expert_id)
    if expert:
        return expert
    else:
        ...
        
# Get all experts
def get_all_experts():
    experts = crud_experts.get_all_experts()
    if experts:
        return experts
    else:
        ...
        
# Add an expert to the database
def add_expert(name: str, is_available: bool):
    expert_id = crud_experts.create_expert(name, is_available)
    if expert_id:
        return expert_id
    else:
        ...
        
# Remove an expert from the database
def remove_expert(expert_id: int):
    success = crud_experts.delete_expert(expert_id)
    if success:
        return True
    else:
        ...

# Get experts for result
def get_experts_for_result(result_id: int):
    experts = crud_experts.get_experts_for_result(result_id)
    if experts:
        return experts
    else:
        ...
        
# Add an expert to a result
def add_expert_to_result(result_id: int, expert_data):
    expert_id = crud_experts.create_expert(result_id, expert_data)
    if expert_id:
        return expert_id
    else:
        ...
        
# Remove an expert from a result
def remove_expert_from_result(expert_id: int, result_id: int):
    success = crud_experts.remove_expert_from_result(expert_id, result_id)
    if success:
        return True
    else:
        ...
        
# --- Examination Management ---

def get_all_examinations():
    examinations = crud_examinations.get_all_examinations()
    if examinations:
        return examinations
    else:
        ...

def get_examination_by_id(examination_id: int):
    examination = crud_examinations.get_examination_by_id(examination_id)
    if examination:
        return examination
    else:
        ...
        
# Add an examination to the database
def add_examination(name: str, is_available: bool):
    examination_id = crud_examinations.create_examination(name, is_available)
    if examination_id:
        return examination_id
    else:
        ...
        
# Remove an examination from the database
def remove_examination(examination_id: int):
    success = crud_examinations.delete_examination(examination_id)
    if success:
        return True
    else:
        ...

# Get all examinations for a result
def get_examinations_for_result(result_id: int):
    examinations = crud_examinations.get_examinations_for_result(result_id)
    if examinations:
        return examinations
    else:
        ...
        
# Add an examination to a result
def add_examination_to_result(examination_id: int, result_id: int):
    examination_id = crud_examinations.add_examination_to_result(examination_id, result_id)
    if examination_id:
        return examination_id
    else:
        ...
        
# Remove an examination from a result
def remove_examination_from_result(examination_id: int, result_id: int):
    success = crud_examinations.remove_examination_from_result(examination_id, result_id)
    if success:
        return True
    else:
        ...