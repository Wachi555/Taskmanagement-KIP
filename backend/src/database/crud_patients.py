from database.session import SessionLocal
from database.orm_models import Patient

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

def create_patient(
        first_name: str, last_name: str, age: int, date_of_birth: str, is_waiting: bool, in_treatment: bool, 
        health_insurance: str, allergies: str, address: str):

    session = SessionLocal()
    new_patient = Patient(
        first_name=first_name, last_name=last_name, age=age, date_of_birth=date_of_birth, is_waiting=is_waiting,
        in_treatment=in_treatment, health_insurance=health_insurance, allergies=allergies, address=address
    )
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

def update_patient(
        patient_id: int, first_name: str = None, last_name: str = None, age: int = None, date_of_birth: str = None, 
        is_waiting: bool = None, in_treatment: bool = None, health_insurance: str = None, allergies: str = None,
        address: str = None):

    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        if first_name is not None:
            patient.first_name = first_name
        if last_name is not None:
            patient.last_name = last_name
        if age is not None:
            patient.age = age
        if date_of_birth is not None:
            patient.date_of_birth = date_of_birth
        if is_waiting is not None:
            patient.is_waiting = is_waiting
        if in_treatment is not None:
            patient.in_treatment = in_treatment
        if health_insurance is not None:
            patient.health_insurance = health_insurance
        if allergies is not None:
            patient.allergies = allergies
        if address is not None:
            patient.address = address
        session.commit()
        session.refresh(patient)
        session.close()
        return patient
    else:
        session.close()
        return None