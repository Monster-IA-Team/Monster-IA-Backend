from typing import Optional
from sqlmodel import Session, select
from fastapi import Depends

from models.taste_preference import TastePreference
from configuration.database import get_session

class TasteRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
    
    def save(self, preferemces: TastePreference):
        self.session.add(preferemces)
        self.session.commit()
        self.session.refresh(preferemces)