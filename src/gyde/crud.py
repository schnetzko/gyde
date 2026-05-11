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


def create_document(
    db: Session,
    customer_id: str,
    title: str,
    short_description: str,
    document_bytes: bytes,
) -> models.Document:
    db_document = models.Document(
        customer_id=customer_id,
        title=title,
        short_description=short_description,
        document=document_bytes,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def get_documents(db: Session) -> list[models.Document]:
    return db.query(models.Document).order_by(models.Document.id).all()


def update_document(
    db: Session,
    document_id: int,
    document_update: schemas.DocumentUpdate,
    document_bytes: bytes | None = None,
) -> models.Document | None:
    db_document = get_document(db, document_id)
    if db_document is None:
        return None

    if document_update.customer_id is not None:
        db_document.customer_id = document_update.customer_id
    if document_update.title is not None:
        db_document.title = document_update.title
    if document_update.short_description is not None:
        db_document.short_description = document_update.short_description
    if document_bytes is not None:
        db_document.document = document_bytes

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    db_document = get_document(db, document_id)
    if db_document is None:
        return False

    db.delete(db_document)
    db.commit()
    return True


def create_document(
    db: Session,
    customer_id: str,
    title: str,
    short_description: str,
    document_bytes: bytes,
) -> models.Document:
    db_document = models.Document(
        customer_id=customer_id,
        title=title,
        short_description=short_description,
        document=document_bytes,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def get_documents(db: Session) -> list[models.Document]:
    return db.query(models.Document).order_by(models.Document.id).all()


def update_document(
    db: Session,
    document_id: int,
    document_update: schemas.DocumentUpdate,
    document_bytes: bytes | None = None,
) -> models.Document | None:
    db_document = get_document(db, document_id)
    if db_document is None:
        return None

    if document_update.customer_id is not None:
        db_document.customer_id = document_update.customer_id
    if document_update.title is not None:
        db_document.title = document_update.title
    if document_update.short_description is not None:
        db_document.short_description = document_update.short_description
    if document_bytes is not None:
        db_document.document = document_bytes

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    db_document = get_document(db, document_id)
    if db_document is None:
        return False

    db.delete(db_document)
    db.commit()
    return True


def create_document(
    db: Session,
    customer_id: str,
    title: str,
    short_description: str,
    document_bytes: bytes,
) -> models.Document:
    db_document = models.Document(
        customer_id=customer_id,
        title=title,
        short_description=short_description,
        document=document_bytes,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def get_documents(db: Session) -> list[models.Document]:
    return db.query(models.Document).order_by(models.Document.id).all()


def update_document(
    db: Session,
    document_id: int,
    document_update: schemas.DocumentUpdate,
    document_bytes: bytes | None = None,
) -> models.Document | None:
    db_document = get_document(db, document_id)
    if db_document is None:
        return None

    if document_update.customer_id is not None:
        db_document.customer_id = document_update.customer_id
    if document_update.title is not None:
        db_document.title = document_update.title
    if document_update.short_description is not None:
        db_document.short_description = document_update.short_description
    if document_bytes is not None:
        db_document.document = document_bytes

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    db_document = get_document(db, document_id)
    if db_document is None:
        return False

    db.delete(db_document)
    db.commit()
    return True
