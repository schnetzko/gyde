from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, Text

from .database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    post_address = Column(Text, nullable=False)


class ContactPerson(Base):
    __tablename__ = "contact_persons"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)


class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    number_of_courses = Column(Integer, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    pdf_text = Column(LargeBinary, nullable=False)
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
    document = Column(LargeBinary, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
