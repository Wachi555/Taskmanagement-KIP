from typing import List

from database.orm_models import Patient, PatientEntry
from database.session import SessionLocal


def get_patient_entries(patient_id: int) -> List[PatientEntry]:
    session = SessionLocal()
    entries = (
        session.query(PatientEntry).filter(PatientEntry.patient_id == patient_id).all()
    )
    session.close()
    return entries


def get_latest_patient_entry(patient_id: int) -> PatientEntry:  # TODO: Test
    session = SessionLocal()
    entry = (
        session.query(PatientEntry)
        .filter(PatientEntry.patient_id == patient_id)
        .order_by(PatientEntry.entry_date.desc())
        .first()
    )
    session.close()
    if entry is None:
        raise ValueError(f"No entries found for patient with ID {patient_id}.")
    return entry


def get_patient_entry(entry_id: int) -> PatientEntry:
    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    session.close()
    if entry is None:
        raise ValueError(f"Patient entry with ID {entry_id} not found.")
    return entry


# TODO: How is the schema supposed to look like for this (parameters)?
def create_patient_entry(
    patient_id: int,
    entry_date: str,
    patient_history: str,
    additional_notes: str,
    extracted_contents_json: str,
    symptoms: str,
    medications: str,
    triage_level: int,
) -> int:
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        session.close()
        raise ValueError(f"Patient with ID {patient_id} not found.")

    new_entry = PatientEntry(
        patient_id=patient_id,
        entry_date=entry_date,
        patient_history=patient_history,
        additional_notes=additional_notes,
        extracted_contents_json=extracted_contents_json,
        symptoms=symptoms,
        medications=medications,
        triage_level=triage_level,
    )
    session.add(new_entry)
    session.commit()
    session.refresh(new_entry)
    session.close()
    return new_entry.id  # type: ignore


def delete_patient_entry(entry_id: int):
    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    if entry is None:
        session.close()
        raise ValueError(f"Patient entry with ID {entry_id} not found.")

    session.delete(entry)
    session.commit()
    session.close()


def update_patient_entry(entry_id: int, **kwargs):  # TODO: Test if kwargs work
    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    if entry is None:
        session.close()
        raise ValueError(f"Patient entry with ID {entry_id} not found.")

    for key, value in kwargs.items():
        if hasattr(entry, key) and value is not None:
            setattr(entry, key, value)

    session.commit()
    session.refresh(entry)
    session.close()
