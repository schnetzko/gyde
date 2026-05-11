from sqlalchemy.orm import Session

from . import models, schemas


# Tenant CRUD
def create_tenant(db: Session, tenant: schemas.TenantCreate) -> models.Tenant:
    db_tenant = models.Tenant(
        name=tenant.name,
        post_address=tenant.post_address,
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenant(db: Session, tenant_id: int) -> models.Tenant | None:
    return db.get(models.Tenant, tenant_id)


def get_tenants(db: Session) -> list[models.Tenant]:
    return db.query(models.Tenant).order_by(models.Tenant.id).all()


def update_tenant(db: Session, tenant_id: int, tenant_update: schemas.TenantUpdate) -> models.Tenant | None:
    db_tenant = get_tenant(db, tenant_id)
    if db_tenant is None:
        return None

    if tenant_update.name is not None:
        db_tenant.name = tenant_update.name
    if tenant_update.post_address is not None:
        db_tenant.post_address = tenant_update.post_address

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def delete_tenant(db: Session, tenant_id: int) -> bool:
    db_tenant = get_tenant(db, tenant_id)
    if db_tenant is None:
        return False

    db.delete(db_tenant)
    db.commit()
    return True


# ContactPerson CRUD
def create_contact_person(db: Session, contact: schemas.ContactPersonCreate) -> models.ContactPerson:
    db_contact = models.ContactPerson(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        tenant_id=contact.tenant_id,
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contact_person(db: Session, contact_id: int) -> models.ContactPerson | None:
    return db.get(models.ContactPerson, contact_id)


def get_contact_persons_by_tenant(db: Session, tenant_id: int) -> list[models.ContactPerson]:
    return db.query(models.ContactPerson).filter(models.ContactPerson.tenant_id == tenant_id).order_by(models.ContactPerson.id).all()


def update_contact_person(db: Session, contact_id: int, contact_update: schemas.ContactPersonUpdate) -> models.ContactPerson | None:
    db_contact = get_contact_person(db, contact_id)
    if db_contact is None:
        return None

    if contact_update.first_name is not None:
        db_contact.first_name = contact_update.first_name
    if contact_update.last_name is not None:
        db_contact.last_name = contact_update.last_name
    if contact_update.email is not None:
        db_contact.email = contact_update.email
    if contact_update.phone is not None:
        db_contact.phone = contact_update.phone

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact_person(db: Session, contact_id: int) -> bool:
    db_contact = get_contact_person(db, contact_id)
    if db_contact is None:
        return False

    db.delete(db_contact)
    db.commit()
    return True


# Workshop CRUD
def create_workshop(db: Session, workshop: schemas.WorkshopCreate) -> models.Workshop:
    db_workshop = models.Workshop(
        description=workshop.description,
        number_of_courses=workshop.number_of_courses,
        tenant_id=workshop.tenant_id,
    )
    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    return db_workshop


def get_workshop(db: Session, workshop_id: int) -> models.Workshop | None:
    return db.get(models.Workshop, workshop_id)


def get_workshops_by_tenant(db: Session, tenant_id: int) -> list[models.Workshop]:
    return db.query(models.Workshop).filter(models.Workshop.tenant_id == tenant_id).order_by(models.Workshop.id).all()


def update_workshop(db: Session, workshop_id: int, workshop_update: schemas.WorkshopUpdate) -> models.Workshop | None:
    db_workshop = get_workshop(db, workshop_id)
    if db_workshop is None:
        return None

    if workshop_update.description is not None:
        db_workshop.description = workshop_update.description
    if workshop_update.number_of_courses is not None:
        db_workshop.number_of_courses = workshop_update.number_of_courses

    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    return db_workshop


def delete_workshop(db: Session, workshop_id: int) -> bool:
    db_workshop = get_workshop(db, workshop_id)
    if db_workshop is None:
        return False

    db.delete(db_workshop)
    db.commit()
    return True


# Course CRUD
def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(
        name=course.name,
        pdf_text=course.pdf_text.encode('utf-8'),
        workshop_id=course.workshop_id,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_course(db: Session, course_id: int) -> models.Course | None:
    return db.get(models.Course, course_id)


def get_courses_by_workshop(db: Session, workshop_id: int) -> list[models.Course]:
    return db.query(models.Course).filter(models.Course.workshop_id == workshop_id).order_by(models.Course.id).all()


def update_course(db: Session, course_id: int, course_update: schemas.CourseUpdate) -> models.Course | None:
    db_course = get_course(db, course_id)
    if db_course is None:
        return None

    if course_update.name is not None:
        db_course.name = course_update.name
    if course_update.pdf_text is not None:
        db_course.pdf_text = course_update.pdf_text.encode('utf-8')

    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    db_course = get_course(db, course_id)
    if db_course is None:
        return False

    db.delete(db_course)
    db.commit()
    return True


# Document CRUD
def create_document(db: Session, document: schemas.DocumentCreate, document_bytes: bytes) -> models.Document:
    db_document = models.Document(
        title=document.title,
        short_description=document.short_description,
        document=document_bytes,
        tenant_id=document.tenant_id,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def get_documents_by_tenant(db: Session, tenant_id: int) -> list[models.Document]:
    return db.query(models.Document).filter(models.Document.tenant_id == tenant_id).order_by(models.Document.id).all()


def update_document(
    db: Session,
    document_id: int,
    document_update: schemas.DocumentUpdate,
    document_bytes: bytes | None = None,
) -> models.Document | None:
    db_document = get_document(db, document_id)
    if db_document is None:
        return None

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
