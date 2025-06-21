from typing import List, Optional

from pydantic import BaseModel

class Diagnosis(BaseModel):
    name: str
    reason: Optional[str] = None
    confidence: Optional[float] = None

class Examination(BaseModel):
    name: str
    priority: int = None

class Expert(BaseModel):
    type: str

# Structured output for the LLM result
class LLMResult(BaseModel):
    diagnosis: List[Diagnosis]
    examinations: List[Examination]
    treatments: List[str]
    experts: List[Expert]
    # overall_priority: int # TODO: They requested "prioritisation based on current capacity/utilisation of the hospital" -> Doesn't really make sense, bc. either a patient is important or not?

# ==== Input Output from Frontend ====

# Input from frontend for processing the anamnesis text
class InputAnamnesis(BaseModel):
    text: str

# Patient data from frontend for creating a new patient
class InputPatient(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    health_insurance: str
    triage_level: int
    symptoms: str
    address: str

# What the frontend receives from the backend after processing the anamnesis text
class OutputModel(BaseModel):
    output: LLMResult
    success: bool = True
    error: str = None
    status_code: int = None

# ===============================================================

# What content the model should extract from the anamnesis text
class ExtractedContent(BaseModel):
    history: str
    medications: List[str]
    allergies: List[str]
    additional_notes: str

# What the model recieves to evaluate the patient
class EvaluationInput(BaseModel):
    age: int
    symptoms: List[str]
    history: str
    medications: List[str]
    allergies: List[str]
    additional_notes: str