from typing import List

from database.orm_models import Result
from database.session import SessionLocal

"""CRUD operations for the Result model in the database."""


def create_result(
    patient_entry_id: int, experts: str, examinations: str, treatments: str
) -> int:
    session = SessionLocal()
    new_result = Result(
        patient_entry_id=patient_entry_id,
        experts=experts,
        examinations=examinations,
        treatments=treatments,
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)
    session.close()
    return new_result.id  # type: ignore


def get_result_by_id(result_id: int) -> Result:
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    session.close()
    if result is None:
        raise ValueError(f"Result with ID {result_id} not found.")
    return result


def get_results_by_patient_entry_id(patient_entry_id: int) -> List[Result]:
    session = SessionLocal()
    results = (
        session.query(Result).filter(Result.patient_entry_id == patient_entry_id).all()
    )
    session.close()
    return results


def update_result(result_id: int, triage_level: int):
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    if result is None:
        session.close()
        raise ValueError(f"Result with ID {result_id} not found.")

    result.triage_level = triage_level
    session.commit()
    session.refresh(result)
    session.close()


def delete_result(result_id: int):
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    if result is None:
        session.close()
        raise ValueError(f"Result with ID {result_id} not found.")

    session.delete(result)
    session.commit()
    session.close()
