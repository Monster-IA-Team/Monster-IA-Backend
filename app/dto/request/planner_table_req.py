from pydantic import BaseModel, Field
from typing import Literal, Optional

class PlannerManagementReq(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=10, le=50, description="Number of records per page (10, 20, 30, 40, 50)")
    sort_by: str = Field(default="created_at", description="The record by which we sort")
    sort_order: Literal["asc", "desc"] = Field(default="desc", description="Sorting direction")