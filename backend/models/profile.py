from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union
from datetime import datetime

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    role: str
    seniority_level: str
    years_experience: Optional[int] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    primary_goal: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProfileCreateRequest(BaseModel):
    role: str
    seniority_level: str
    years_experience: Optional[Union[int, str]] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    primary_goal: Optional[str] = None
    
    @field_validator('years_experience', mode='before')
    @classmethod
    def parse_years(cls, v):
        if v is None or v == '' or v == 'null':
            return None
        if isinstance(v, int):
            return v
        try:
            return int(v)
        except (ValueError, TypeError):
            return None