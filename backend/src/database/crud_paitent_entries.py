from database.orm_models import Patient, PatientEntry
from database.session import SessionLocal


def get_patient_entries(patient_id: int):
    session = SessionLocal()
    entries = (
        session.query(PatientEntry).filter(PatientEntry.patient_id == patient_id).all()
    )
    session.close()
    return entries


def get_patient_entry(entry_id: int):
    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    session.close()
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
):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
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
        return new_entry.id
    else:
        session.close()
        return None


def delete_entry(entry_id: int):
    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    if entry:
        session.delete(entry)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False


def update_patient_entry(
    entry_id: int,
    entry_date: str | None = None,
    patient_history: str | None = None,
    additional_notes: str | None = None,
    extracted_contents_json: str | None = None,
    symptoms: str | None = None,
    medications: str | None = None,
    triage_level: int | None = None,
):

    session = SessionLocal()
    entry = session.query(PatientEntry).filter(PatientEntry.id == entry_id).first()
    if entry:
        if entry_date is not None:
            entry.entry_date = entry_date
        if patient_history is not None:
            entry.patient_history = patient_history
        if additional_notes is not None:
            entry.additional_notes = additional_notes
        if extracted_contents_json is not None:
            entry.extracted_contents_json = extracted_contents_json
        if symptoms is not None:
            entry.symptoms = symptoms
        if medications is not None:
            entry.medications = medications
        if triage_level is not None:
            entry.triage_level = triage_level
        session.commit()
        session.refresh(entry)
        session.close()
        return True
    else:
        session.close()
        return False
