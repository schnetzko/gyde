from sqlalchemy import Column, Integer, LargeBinary, Text

from .database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    number_of_courses = Column(Integer, nullable=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
    document = Column(LargeBinary, nullable=False)
