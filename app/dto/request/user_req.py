from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class UserRegisterReq(SQLModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

class UserLoginReq(SQLModel):
    email: EmailStr
    password: str