from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Patients table (one for each patient)
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(String, nullable=False)
    is_waiting = Column(Boolean, nullable=False)
    in_treatment = Column(Boolean, nullable=False)
    health_insurance = Column(String, nullable=False)
    allergies = Column(String, nullable=True)  # JSON or comma-separated list
    address = Column(String, nullable=True)  # Optional field for patient address
    last_triage_level = Column(
        Integer, nullable=True
    )  # Last triage level assigned to the patient
    latest_entry_id = Column(
        Integer, ForeignKey("patient_entries.id"), nullable=True
    )


# Entries table (one for each entry in the patient's history)
class PatientEntry(Base):
    __tablename__ = "patient_entries"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    entry_date = Column(String, nullable=False)
    patient_history = Column(String, nullable=False)
    additional_notes = Column(String, nullable=True)
    extracted_contents_json = Column(
        String, nullable=False
    )  # JSON string containing extracted content
    symptoms = Column(String, nullable=True)  # JSON or comma-separated list
    medications = Column(String, nullable=True)  # JSON or comma-separated list
    triage_level = Column(Integer, nullable=False)
    anamnesis_text = Column(String, nullable=False)
    latest_result_id = Column(Integer, ForeignKey("results.id"), nullable=True)


# Examinations table (one for each examination type)
class Examination(Base):
    __tablename__ = "examinations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)
    utilization = Column(Integer, nullable=False)  # 1: low, 2: medium, 3: high


# Experts table (one for each type of expert)
class Expert(Base):
    __tablename__ = "experts"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)


# Results table (one for each patient entry -> might get more if feedback is implemented)
class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True)
    patient_entry_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    experts = Column(String, nullable=True)
    examinations = Column(String, nullable=True)
    treatments = Column(String, nullable=True)


# Unique for each result, but one result can have multiple diagnoses
class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey("results.id"), nullable=False)
    name = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
