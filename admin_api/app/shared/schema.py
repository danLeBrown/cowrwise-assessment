from uuid import UUID
from pydantic import BaseModel,field_validator
from datetime import datetime

class BaseSchema(BaseModel):
    id: UUID
    created_at: int
    updated_at: int
    
    @field_validator("created_at", "updated_at", mode="before")
    def convert_datetime_to_timestamp(cls, value: datetime) -> int:
        if isinstance(value, datetime):
            return int(value.timestamp())
        return value
    
class UpdateSchema(BaseModel):
    detail: str
