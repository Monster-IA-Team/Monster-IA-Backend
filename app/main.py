from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from typing import List

from services.schedule_services import ScheduleService
from services.quiz_services import QuizService
from services.prediction_services import PredictionService

from dto.response.prediction_res import PredictionResponse
from dto.request.schedule_req import ScheduleRequest
from dto.response.schedule_res import ScheduleResponse
from dto.request.quiz_answers_req import QuizAnswersRequest

app = FastAPI(
    title="Monster IA API", 
    description="V1 of Monster IA API", 
    version="1.0"
    )

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
    )

quiz_service = QuizService(
    monster_path="dataset/json/monsters.json", 
    tree_path="dataset/json/tree.json"
    )

prediction_service = PredictionService()

schedule_service = ScheduleService()

@app.post("/api/get_monsters", response_model=List[str])
async def get_monsters(answers: QuizAnswersRequest):
    return quiz_service.get_answers(answers)

@app.post("/api/predict_monster", response_model=PredictionResponse)
async def predict_monster(file: UploadFile = File(...)):
    content = await file.read()
    return prediction_service.predict(content)

@app.post("/api/calculate_schedule", response_model=ScheduleResponse)
async def calculate_schedule(req: ScheduleRequest):
    return schedule_service.calculate_schedule(req)