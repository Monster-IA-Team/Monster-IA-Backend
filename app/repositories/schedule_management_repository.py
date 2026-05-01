from sqlmodel import Session, select
from fastapi import Depends
import uuid
from typing import List, Optional
from configuration.database import get_session
from models.planner import Planner
from models.task import Task

class PlannerRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def save_planner(self, planner: Planner, tasks: List[Task]):
        self.session.add(planner)
        for task in tasks:
            task.planners_id = planner.id
            self.session.add(task)
        self.session.commit()
        self.session.refresh(planner)
        return planner

    def get_all_by_user(self, user_id: uuid.UUID) -> List[Planner]:
        stmt = select(Planner).where(Planner.user_id == user_id)
        return self.session.exec(stmt).all()

    def get_by_id(self, planner_id: uuid.UUID) -> Optional[Planner]:
        return self.session.get(Planner, planner_id)

    def delete(self, planner: Planner):
        self.session.delete(planner)
        self.session.commit()