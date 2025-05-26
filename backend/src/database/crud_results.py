from sqlalchemy.orm import SessionLocal
from orm_models import Result

def create_result(patient_entry_id: int, triage_level: int):
    session = SessionLocal()
    new_result = Result(patient_entry_id=patient_entry_id, triage_level=triage_level)
    session.add(new_result)
    session.commit()
    session.refresh(new_result)
    session.close()
    return new_result.id

def get_result_by_id(result_id: int):
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    session.close()
    return result

def get_results_by_patient_entry_id(patient_entry_id: int):
    session = SessionLocal()
    results = session.query(Result).filter(Result.patient_entry_id == patient_entry_id).all()
    session.close()
    return results

def update_result(result_id: int, triage_level: int):
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    if result:
        result.triage_level = triage_level
        session.commit()
        session.refresh(result)
        session.close()
        return result
    else:
        session.close()
        return None
    
def delete_result(result_id: int):
    session = SessionLocal()
    result = session.query(Result).filter(Result.id == result_id).first()
    if result:
        session.delete(result)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False
