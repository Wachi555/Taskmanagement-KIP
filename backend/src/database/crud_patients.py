from typing import List

from database.orm_models import Patient
from database.session import SessionLocal

"""CRUD operations for the Patient model in the database."""


def get_all_patients() -> List[Patient]:
    session = SessionLocal()
    patients = session.query(Patient).all()
    session.close()
    return patients


def get_patient_by_id(patient_id: int) -> Patient:
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    session.close()
    if patient is None:
        raise ValueError(f"Patient with ID {patient_id} not found.")
    return patient


# Gets a patient by their first name, last name, and date of birth to check if they are already registered.
def get_patient_by_name_and_dob(
    first_name: str, last_name: str, date_of_birth: str
) -> Patient:
    session = SessionLocal()
    patient = (
        session.query(Patient)
        .filter(
            Patient.first_name == first_name,
            Patient.last_name == last_name,
            Patient.date_of_birth == date_of_birth,
        )
        .first()
    )
    session.close()
    if patient is None:
        raise ValueError(
            f"Patient with name {first_name} {last_name} and DOB {date_of_birth} not "
            f"found."
        )
    return patient


def create_patient(
    first_name: str,
    last_name: str,
    gender: str,
    age: int,
    date_of_birth: str,
    is_waiting: bool,
    in_treatment: bool,
    health_insurance: str,
    allergies: str | None,
    address: str,
) -> int:
    session = SessionLocal()
    new_patient = Patient(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        age=age,
        date_of_birth=date_of_birth,
        is_waiting=is_waiting,
        in_treatment=in_treatment,
        health_insurance=health_insurance,
        allergies=allergies,
        address=address,
    )
    session.add(new_patient)
    session.commit()
    session.refresh(new_patient)
    session.close()
    return new_patient.id  # type: ignore


def delete_patient(patient_id: int):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        session.close()
        raise ValueError(f"Patient with ID {patient_id} not found.")

    session.delete(patient)
    session.commit()
    session.close()


def update_patient(patient_id: int, **kwargs):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        session.close()
        raise ValueError(f"Patient with ID {patient_id} not found.")

    for key, value in kwargs.items():
        if hasattr(patient, key) and value is not None:
            setattr(patient, key, value)

    session.commit()
    session.refresh(patient)
    session.close()
