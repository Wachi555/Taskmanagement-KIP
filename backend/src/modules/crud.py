# Create, Read, Update, Delete for the database

from common.orm_models import Patient, Entry
from .database import SessionLocal

def get_all_patients():
    session = SessionLocal()
    patients = session.query(Patient).all()
    session.close()
    return patients

def get_patient_by_id(patient_id: int):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    session.close()
    return patient

def create_patient(first_name: str, last_name: str, age: int, date_of_birth: str):
    session = SessionLocal()
    new_patient = Patient(first_name=first_name, last_name=last_name, age=age, date_of_birth=date_of_birth)
    session.add(new_patient)
    session.commit()
    session.refresh(new_patient)
    session.close()
    return new_patient.id

def delete_patient(patient_id: int):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        session.delete(patient)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False

def update_patient(patient_id: int, first_name: str = None, last_name: str = None, age: int = None, date_of_birth: str = None):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        if first_name:
            patient.first_name = first_name
        if last_name:
            patient.last_name = last_name
        if age:
            patient.age = age
        if date_of_birth:
            patient.date_of_birth = date_of_birth
        session.commit()
        session.refresh(patient)
        session.close()
        return patient
    else:
        session.close()
        return None

def get_patient_entries(patient_id: int):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        entries = patient.entries
        session.close()
        return entries
    else:
        session.close()
        return None

def create_entry(patient_id: int, entry_date: str, entry_text: str):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        new_entry = Entry(patient_id=patient_id, entry_date=entry_date, entry_text=entry_text)
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        session.close()
        return new_entry.id
    else:
        session.close()
        return None

def delete_entry(entry_id: int):
    session = SessionLocal()
    entry = session.query(Entry).filter(Entry.id == entry_id).first()
    if entry:
        session.delete(entry)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False