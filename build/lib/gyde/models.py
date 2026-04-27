from sqlalchemy import Column, Integer, Text

from database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    number_of_courses = Column(Integer, nullable=False)
