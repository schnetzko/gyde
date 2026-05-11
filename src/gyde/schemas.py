from typing import Optional

from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    name: str = Field(..., title="Name")
    post_address: str = Field(..., title="Post Address")


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, title="Name")
    post_address: Optional[str] = Field(None, title="Post Address")


class TenantResponse(TenantBase):
    id: int

    class Config:
        from_attributes = True


class ContactPersonBase(BaseModel):
    first_name: str = Field(..., title="First Name")
    last_name: str = Field(..., title="Last Name")
    email: str = Field(..., title="Email")
    phone: str = Field(..., title="Phone")


class ContactPersonCreate(ContactPersonBase):
    tenant_id: int = Field(..., title="Tenant ID")


class ContactPersonUpdate(BaseModel):
    first_name: Optional[str] = Field(None, title="First Name")
    last_name: Optional[str] = Field(None, title="Last Name")
    email: Optional[str] = Field(None, title="Email")
    phone: Optional[str] = Field(None, title="Phone")


class ContactPersonResponse(ContactPersonBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class WorkshopBase(BaseModel):
    description: str = Field(..., title="Description")
    number_of_courses: int = Field(..., ge=0, title="Number of Courses")


class WorkshopCreate(WorkshopBase):
    tenant_id: int = Field(..., title="Tenant ID")


class WorkshopUpdate(BaseModel):
    description: Optional[str] = Field(None, title="Description")
    number_of_courses: Optional[int] = Field(None, ge=0, title="Number of Courses")


class WorkshopResponse(WorkshopBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    name: str = Field(..., title="Name")
    pdf_text: str = Field(..., title="PDF Text")


class CourseCreate(CourseBase):
    workshop_id: int = Field(..., title="Workshop ID")


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, title="Name")
    pdf_text: Optional[str] = Field(None, title="PDF Text")


class CourseResponse(CourseBase):
    id: int
    workshop_id: int

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    title: str = Field(..., title="Title")
    short_description: str = Field(..., title="Short Description")


class DocumentCreate(DocumentBase):
    tenant_id: int = Field(..., title="Tenant ID")


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, title="Title")
    short_description: Optional[str] = Field(None, title="Short Description")


class DocumentResponse(DocumentBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True
