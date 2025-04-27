from typing import List, Optional

from pydantic import BaseModel

class Diagnosis(BaseModel):
    name: str
    reason: Optional[str] = None
    confidence: Optional[float] = None


class Examination(BaseModel):
    name: str
    priority: Optional[int] = None


class OutputContent(BaseModel):
    diagnosis: List[Diagnosis]
    examinations: List[Examination]
    treatments: List[str]
    symptoms: List[str]

# ===============================================================

class InputModel(BaseModel):
    text: str

class OutputModel(BaseModel):
    output: OutputContent
    success: bool = True
    error: str = None
    error_code: int = None

# ===============================================================

class ExtractedContent(BaseModel):
    name: str
    date_of_birth: str
    age: int
    symptoms: List[str]
    history: str
    medications: List[str]
    allergies: List[str]
    family_history: str
    additional_notes: str


class EvaluationInput(BaseModel):
    age: int
    symptoms: List[str]
    history: str
    medications: List[str]
    allergies: List[str]
    family_history: str
    additional_notes: str