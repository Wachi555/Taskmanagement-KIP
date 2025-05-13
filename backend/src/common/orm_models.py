from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Patients table (one for each patient)
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(String, nullable=False)
    # Optional for easy access to a patient's entries
    entries = relationship("Entry", back_populates="patient")

# Entries table (one for each entry in the patient's history)
class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    entry_date = Column(String, nullable=False)
    entry_text = Column(String, nullable=False)
    # Optional for easy access to the patient of an entry
    patient = relationship("Patient", back_populates="entries")
    