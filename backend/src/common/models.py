from typing import List, Optional

from pydantic import BaseModel


class InputModel(BaseModel):
    text: str


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


class OutputModel(BaseModel):
    output: OutputContent
    success: bool = True
    error: str = None
    error_code: int = None
