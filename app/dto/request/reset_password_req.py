import re
from pydantic import BaseModel, field_validator, model_validator

class ResetPasswordRequet(BaseModel):
    token: str
    password: str
    confirm_password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'ResetPasswordRequet':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self