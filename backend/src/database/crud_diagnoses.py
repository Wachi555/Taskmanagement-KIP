from typing import List

from database.orm_models import Diagnosis
from database.session import SessionLocal

"""CRUD operations for the Diagnosis model in the database."""


def get_diagnoses_for_entry(result_id: int) -> List[Diagnosis]:
    session = SessionLocal()
    diagnoses = session.query(Diagnosis).filter(Diagnosis.result_id == result_id).all()
    session.close()
    return diagnoses


def create_diagnosis(result_id: int, name: str, reason: str, confidence: float) -> int:
    session = SessionLocal()
    new_diagnosis = Diagnosis(
        result_id=result_id, name=name, reason=reason, confidence=confidence
    )
    session.add(new_diagnosis)
    session.commit()
    session.refresh(new_diagnosis)
    session.close()
    return new_diagnosis.id  # type: ignore


def delete_diagnosis(diagnosis_id: int):
    session = SessionLocal()
    diagnosis = session.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    if diagnosis is None:
        session.close()
        raise ValueError(f"Diagnosis with ID {diagnosis_id} not found.")

    session.delete(diagnosis)
    session.commit()
    session.close()
