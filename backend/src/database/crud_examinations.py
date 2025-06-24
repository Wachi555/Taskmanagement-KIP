from typing import List

from database.orm_models import Examination
from database.session import SessionLocal

"""CRUD operations for the Examination model in the database."""


def get_all_examinations() -> List[Examination]:
    session = SessionLocal()
    examinations = session.query(Examination).all()
    session.close()
    return examinations


def get_examination_by_id(examination_id: int) -> Examination:
    session = SessionLocal()
    examination = (
        session.query(Examination).filter(Examination.id == examination_id).first()
    )
    session.close()
    if examination is None:
        raise ValueError(f"Examination with ID {examination_id} not found.")
    return examination


def check_examination_exists(name: str) -> bool:
    session = SessionLocal()
    exists = (
        session.query(Examination).filter(Examination.name == name).first() is not None
    )
    session.close()
    return exists


def get_available_examinations() -> List[Examination]:
    session = SessionLocal()
    examinations = (
        session.query(Examination).filter(Examination.is_available == True).all()
    )
    session.close()
    return examinations


def remove_all_examinations():
    session = SessionLocal()
    session.query(Examination).delete()
    session.commit()
    session.close()


def create_examination(name: str, utilization: int, is_available: bool) -> int:
    session = SessionLocal()
    new_examination = Examination(
        name=name, utilization=utilization, is_available=is_available
    )
    session.add(new_examination)
    session.commit()
    session.refresh(new_examination)
    session.close()
    return new_examination.id  # type: ignore


def delete_examination(examination_id: int):
    session = SessionLocal()
    examination = (
        session.query(Examination).filter(Examination.id == examination_id).first()
    )
    if examination is None:
        session.close()
        raise ValueError(f"Examination with ID {examination_id} not found.")

    session.delete(examination)
    session.commit()
    session.close()
