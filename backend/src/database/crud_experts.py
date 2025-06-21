from database.session import SessionLocal
from database.orm_models import Expert

def get_expert_by_id(expert_id: int):
    session = SessionLocal()
    expert = session.query(Expert).filter(Expert.id == expert_id).first()
    session.close()
    return expert

def get_all_experts():
    session = SessionLocal()
    experts = session.query(Expert).all()
    session.close()
    return experts

def create_expert(name: str, is_available: bool):
    session = SessionLocal()
    new_expert = Expert(name=name, is_available=is_available)
    session.add(new_expert)
    session.commit()
    session.refresh(new_expert)
    session.close()
    return new_expert.id

def delete_expert(expert_id: int):
    session = SessionLocal()
    expert = session.query(Expert).filter(Expert.id == expert_id).first()
    if expert:
        session.delete(expert)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False

# def get_experts_for_result(result_id: int):
#     session = SessionLocal()
#     experts = session.query(Expert).join(ExpertToResult).filter(ExpertToResult.result_id == result_id).all()
#     session.close()
#     return experts

# def add_expert_to_result(expert_id: int, result_id: int):
#     session = SessionLocal()
#     new_expert_to_result = ExpertToResult(expert_id=expert_id, result_id=result_id)
#     session.add(new_expert_to_result)
#     session.commit()
#     session.refresh(new_expert_to_result)
#     session.close()
#     return new_expert_to_result.id

# def remove_expert_from_result(expert_id: int, result_id: int):
#     session = SessionLocal()
#     expert_to_result = session.query(ExpertToResult).filter(
#         ExpertToResult.expert_id == expert_id,
#         ExpertToResult.result_id == result_id
#     ).first()
#     if expert_to_result:
#         session.delete(expert_to_result)
#         session.commit()
#         session.close()
#         return True
#     else:
#         session.close()
#         return False