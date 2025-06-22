# from database.session import SessionLocal
# from database.orm_models import Medication


# def get_medications_for_entry(entry_id: int):
#     session = SessionLocal()
#     medications = session.query(Medication).filter(Medication.patient_entry_id == entry_id).all()
#     session.close()
#     return medications


# def create_medication(entry_id: int, name: str, dosage: str):
#     session = SessionLocal()
#     new_medication = Medication(patient_entry_id=entry_id, name=name, dosage=dosage)
#     session.add(new_medication)
#     session.commit()
#     session.refresh(new_medication)
#     session.close()
#     return new_medication.id


# def delete_medication(medication_id: int):
#     session = SessionLocal()
#     medication = session.query(Medication).filter(Medication.id == medication_id).first()
#     if medication:
#         session.delete(medication)
#         session.commit()
#         session.close()
#         return True
#     else:
#         session.close()
#         return False
