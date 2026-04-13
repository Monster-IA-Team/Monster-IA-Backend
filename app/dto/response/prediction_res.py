from pydantic import BaseModel
from typing import List
from dto.response.class_cofidence_res import ClassConfidenceResponse

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    prediction: List[ClassConfidenceResponse]
    num_classes: int