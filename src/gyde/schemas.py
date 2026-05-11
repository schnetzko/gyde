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


class DocumentBase(BaseModel):
    customer_id: str = Field(..., title="Customer ID")
    title: str = Field(..., title="Title")
    short_description: str = Field(..., title="Short Description")


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    customer_id: Optional[str] = Field(None, title="Customer ID")
    title: Optional[str] = Field(None, title="Title")
    short_description: Optional[str] = Field(None, title="Short Description")


class DocumentResponse(DocumentBase):
    id: int

    class Config:
        orm_mode = True
