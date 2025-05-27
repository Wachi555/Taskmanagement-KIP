from database.session import SessionLocal
from database.orm_models import Symptom

def get_symptoms_for_entry(entry_id: int):
    session = SessionLocal()
    symptoms = session.query(Symptom).filter(Symptom.entry_id == entry_id).all()
    session.close()
    return symptoms

def create_symptom(entry_id: int, symptom_data: dict):
    session = SessionLocal()
    new_symptom = Symptom(entry_id=entry_id, **symptom_data)
    session.add(new_symptom)
    session.commit()
    session.refresh(new_symptom)
    session.close()
    return new_symptom.id

def delete_symptom(symptom_id: int):
    session = SessionLocal()
    symptom = session.query(Symptom).filter(Symptom.id == symptom_id).first()
    if symptom:
        session.delete(symptom)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False