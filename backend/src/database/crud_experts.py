from typing import List

from database.orm_models import Expert
from database.session import SessionLocal

"""CRUD operations for the Expert model in the database."""

def get_expert_by_id(expert_id: int) -> Expert:
    session = SessionLocal()
    expert = session.query(Expert).filter(Expert.id == expert_id).first()
    session.close()
    if expert is None:
        raise ValueError(f"Expert with ID {expert_id} not found.")
    return expert


def get_all_experts() -> List[Expert]:
    session = SessionLocal()
    experts = session.query(Expert).all()
    session.close()
    return experts

def remove_all_experts():
    session = SessionLocal()
    session.query(Expert).delete()
    session.commit()
    session.close()

def get_available_experts() -> List[Expert]:
    session = SessionLocal()
    experts = session.query(Expert).filter(Expert.is_available == True).all()
    session.close()
    return experts

def create_expert(name: str, is_available: bool) -> int:
    session = SessionLocal()
    new_expert = Expert(name=name, is_available=is_available)
    session.add(new_expert)
    session.commit()
    session.refresh(new_expert)
    session.close()
    return new_expert.id  # type: ignore


def delete_expert(expert_id: int):
    session = SessionLocal()
    expert = session.query(Expert).filter(Expert.id == expert_id).first()
    if expert is None:
        session.close()
        raise ValueError(f"Expert with ID {expert_id} not found.")

    session.delete(expert)
    session.commit()
    session.close()
