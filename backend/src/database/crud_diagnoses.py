from database.session import SessionLocal
from database.orm_models import Diagnosis

def get_diagnoses_for_entry(result_id: int):
    session = SessionLocal()
    diagnoses = session.query(Diagnosis).filter(Diagnosis.result_id == result_id).all()
    session.close()
    return diagnoses

def create_diagnosis(result_id: int, name: str, reason: str, confidence: float):
    session = SessionLocal()
    new_diagnosis = Diagnosis(result_id=result_id, name=name, reason=reason, confidence=confidence)
    session.add(new_diagnosis)
    session.commit()
    session.refresh(new_diagnosis)
    session.close()
    return new_diagnosis.id

def delete_diagnosis(diagnosis_id: int):
    session = SessionLocal()
    diagnosis = session.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    if diagnosis:
        session.delete(diagnosis)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False