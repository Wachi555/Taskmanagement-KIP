from typing import List, Optional

from pydantic import BaseModel


# Pydantic model for the structured output of the LLM
class Diagnosis(BaseModel):
    name: str
    reason: Optional[str] = None
    confidence: Optional[float] = None


# Pydantic model for the structured output of the LLM
class Examination(BaseModel):
    name: str
    priority: int


# Pydantic model for the structured output of the LLM
class Expert(BaseModel):
    type: str


# Main pydantic model for the LLM result
class LLMResult(BaseModel):
    diagnoses: List[Diagnosis]
    examinations: List[Examination]
    treatments: List[str]
    experts: List[Expert]


# ==== Input Output from Frontend ====
# Input from frontend for processing the anamnesis text
class InputAnamnesis(BaseModel):
    text: str


# Patient data from frontend for creating a new patient
class InputPatient(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str = "unbekannt"
    health_insurance: str
    triage_level: int
    symptoms: str
    address: str


# Patient data from frontend for updating an existing patient
class UpdatePatient(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    health_insurance: Optional[str] = None


# ===============================================================


# What content the model should extract from the anamnesis text
class ExtractedContent(BaseModel):
    history: str
    medications: List[str]
    allergies: List[str]
    additional_notes: str
    symptoms: List[str]


# What the model recieves to evaluate the patient
class EvaluationInput(BaseModel):
    age: int
    symptoms: List[str]
    history: str
    medications: List[str]
    allergies: List[str]
    additional_notes: str
