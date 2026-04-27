from typing import Optional

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    description: str = Field(..., title="Description")
    number_of_courses: int = Field(..., ge=0, title="Number of Courses")


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    description: Optional[str] = Field(None, title="Description")
    number_of_courses: Optional[int] = Field(None, ge=0, title="Number of Courses")


class RecordResponse(RecordBase):
    id: int

    class Config:
        orm_mode = True
