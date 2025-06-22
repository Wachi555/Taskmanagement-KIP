from typing import List

from database.orm_models import Examination
from database.session import SessionLocal


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


def create_examination(name: str, is_available: bool) -> int:
    session = SessionLocal()
    new_examination = Examination(name=name, is_available=is_available)
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


# def get_examinations_for_result(result_id: int):
#     session = SessionLocal()
#     examinations = session.query(Examination).join(ExaminationToResult).filter(ExaminationToResult.result_id == result_id).all()
#     session.close()
#     return examinations


# def add_examination_to_result(examination_id: int, result_id: int):
#     session = SessionLocal()
#     new_examination_to_result = ExaminationToResult(examination_id=examination_id, result_id=result_id)
#     session.add(new_examination_to_result)
#     session.commit()
#     session.refresh(new_examination_to_result)
#     session.close()
#     return new_examination_to_result.id


# def remove_examination_from_result(examination_id: int, result_id: int):
#     session = SessionLocal()
#     examination_to_result = session.query(ExaminationToResult).filter(
#         ExaminationToResult.examination_id == examination_id,
#         ExaminationToResult.result_id == result_id
#     ).first()
#     if examination_to_result:
#         session.delete(examination_to_result)
#         session.commit()
#         session.close()
#         return True
#     else:
#         session.close()
#         return False
