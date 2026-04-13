from pydantic import BaseModel, Field

class QuizAnswersRequest(BaseModel):
    shop_type: int = Field(..., description="0 = Stacjonarnie, 1 = Online")
    is_zabka: bool = Field(..., description="True = Żabka, False = Inne (tylko dla shop_type == 0)")
    high_budget: bool = Field(..., description="True = Tak, False = Nie (tylko dla shop_type == 1)")
    sugar_free: bool = Field(..., description="True = Tak, False = Nie")
    taste_preference: int = Field(..., description="0 = Słodki, 1 = Umiarkowany, 2 = Kwaśny")
