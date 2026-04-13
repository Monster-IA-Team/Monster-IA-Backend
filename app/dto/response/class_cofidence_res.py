from pydantic import BaseModel

class ClassConfidenceResponse(BaseModel):
    class_name: str
    confidence: float