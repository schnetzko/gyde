from sqlalchemy.orm import Session

from . import models, schemas


def create_record(db: Session, record: schemas.RecordCreate) -> models.Record:
    db_record = models.Record(
        description=record.description,
        number_of_courses=record.number_of_courses,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_record(db: Session, record_id: int) -> models.Record | None:
    return db.get(models.Record, record_id)


def get_records(db: Session) -> list[models.Record]:
    return db.query(models.Record).order_by(models.Record.id).all()


def update_record(db: Session, record_id: int, record_update: schemas.RecordUpdate) -> models.Record | None:
    db_record = get_record(db, record_id)
    if db_record is None:
        return None

    if record_update.description is not None:
        db_record.description = record_update.description
    if record_update.number_of_courses is not None:
        db_record.number_of_courses = record_update.number_of_courses

    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, record_id: int) -> bool:
    db_record = get_record(db, record_id)
    if db_record is None:
        return False

    db.delete(db_record)
    db.commit()
    return True
