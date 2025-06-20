from sqlalchemy import Column, Integer, Boolean, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Patients table (one for each patient)
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(String, nullable=False)
    is_waiting = Column(Boolean, nullable=False)
    in_treatment = Column(Boolean, nullable=False)
    health_insurance = Column(String, nullable=False)
    allergies = Column(String, nullable=True)  # JSON or comma-separated list
    

# ========================================================================

# Entries table (one for each entry in the patient's history)
class PatientEntry(Base):
    __tablename__ = 'patient_entries'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    entry_date = Column(String, nullable=False)
    patient_history = Column(String, nullable=False)
    additional_notes = Column(String, nullable=True)
    extracted_contents_json = Column(String, nullable=False)
    symptoms = Column(String, nullable=True)  # JSON or comma-separated list
    medications = Column(String, nullable=True)  # JSON or comma-separated list
    

# class Symptom(Base):
#     __tablename__ = 'symptoms'

#     id = Column(Integer, primary_key=True)
#     patient_entry_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
#     name = Column(String, nullable=False)

# class Medication(Base):
#     __tablename__ = 'medications'

#     id = Column(Integer, primary_key=True)
#     patient_entry_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
#     name = Column(String, nullable=False)
#     dosage = Column(String, nullable=False)
    
# class Allergy(Base):
#     __tablename__ = 'allergies'

#     id = Column(Integer, primary_key=True)
#     patient_entry_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
#     name = Column(String, nullable=False)
    
# ========================================================================

class Examination(Base):
    __tablename__ = 'examinations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)

class ExaminationToResult(Base):
    __tablename__ = 'examination_to_result'

    id = Column(Integer, primary_key=True)
    examination_id = Column(Integer, ForeignKey('examinations.id'), nullable=False)
    result_id = Column(Integer, ForeignKey('results.id'), nullable=False)
    priority = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)

# Chosen expert table (one for each expert for each result -> The reason will be stored with the expert)
class Expert(Base):
    __tablename__ = 'experts'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)

class ExpertToResult(Base):
    __tablename__ = 'expert_to_result'

    id = Column(Integer, primary_key=True)
    expert_id = Column(Integer, ForeignKey('experts.id'), nullable=False)
    result_id = Column(Integer, ForeignKey('results.id'), nullable=False)
    reason = Column(String, nullable=False)

# Results table (one for each patient entry -> might get more if feedback is implemented)
class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    patient_entry_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    triage_level = Column(Integer, nullable=False)

# Unique for each result, but one result can have multiple diagnoses
class Diagnosis(Base):
    __tablename__ = 'diagnoses'

    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id'), nullable=False)
    name = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
