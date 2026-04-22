from fastapi import APIRouter
from typing import List
from services.quiz_services import QuizService
from dto.request.quiz_answers_req import QuizAnswersRequest

router = APIRouter(
    prefix="/api/quiz",
    tags=["Quiz"]
)

quiz_service = QuizService(
    monster_path="dataset/json/monsters.json", 
    tree_path="dataset/json/tree.json"
    )

@router.post("", response_model=List[str])
async def get_monsters(answers: QuizAnswersRequest):
    return quiz_service.get_answers(answers)