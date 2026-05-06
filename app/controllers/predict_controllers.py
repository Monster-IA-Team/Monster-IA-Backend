from fastapi import APIRouter, File, UploadFile, Depends
from dependencies.auth import auth_handler

from services.prediction_services import PredictionService

from dto.response.prediction_res import PredictionResponse

router = APIRouter(
    prefix="/api/predict",
    tags=["IA Prediction"]
)

prediction_service = PredictionService()

@router.post("", response_model=PredictionResponse)
async def predict_monster(file: UploadFile = File(...)):
    content = await file.read()
    return prediction_service.predict(content)