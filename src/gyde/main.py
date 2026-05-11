import io
import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gyde Multitenant API")

logger = logging.getLogger("gyde")
security_logger = logging.getLogger("gyde.security")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    security_logger.addHandler(handler)

logger.setLevel(logging.INFO)
security_logger.setLevel(logging.INFO)


@app.middleware("http")
async def log_request(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        "Request start: method=%s path=%s client_ip=%s",
        request.method,
        request.url.path,
        client_ip,
    )
    response = await call_next(request)
    logger.info(
        "Request end: method=%s path=%s status=%s client_ip=%s",
        request.method,
        request.url.path,
        response.status_code,
        client_ip,
    )
    return response


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@app.get("/", status_code=200)
def read_root(request: Request):
    security_logger.info(
        "SECURITY_EVENT=healthcheck_access client_ip=%s path=%s",
        get_client_ip(request),
        request.url.path,
    )
    return {"message": "Gyde Multitenant API is running"}


# Tenant endpoints
@app.post("/tenants", response_model=schemas.TenantResponse, status_code=201)
def create_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    security_logger.info(
        "SECURITY_EVENT=create_tenant client_ip=%s name=%s",
        client_ip,
        tenant.name,
    )
    return crud.create_tenant(db=db, tenant=tenant)


@app.get("/tenants", response_model=List[schemas.TenantResponse])
def list_tenants(db: Session = Depends(get_db), request: Request = None):
    security_logger.info(
        "SECURITY_EVENT=list_tenants client_ip=%s path=%s",
        get_client_ip(request),
        request.url.path,
    )
    return crud.get_tenants(db=db)


@app.get("/tenants/{tenant_id}", response_model=schemas.TenantResponse)
def read_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_tenant = crud.get_tenant(db=db, tenant_id=tenant_id)
    if db_tenant is None:
        security_logger.warning(
            "SECURITY_EVENT=read_tenant_failed client_ip=%s tenant_id=%s",
            client_ip,
            tenant_id,
        )
        raise HTTPException(status_code=404, detail="Tenant not found")

    security_logger.info(
        "SECURITY_EVENT=read_tenant_success client_ip=%s tenant_id=%s",
        client_ip,
        tenant_id,
    )
    return db_tenant


@app.put("/tenants/{tenant_id}", response_model=schemas.TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant: schemas.TenantUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_tenant = crud.update_tenant(db=db, tenant_id=tenant_id, tenant_update=tenant)
    if db_tenant is None:
        security_logger.warning(
            "SECURITY_EVENT=update_tenant_failed client_ip=%s tenant_id=%s",
            client_ip,
            tenant_id,
        )
        raise HTTPException(status_code=404, detail="Tenant not found")

    security_logger.info(
        "SECURITY_EVENT=update_tenant_success client_ip=%s tenant_id=%s",
        client_ip,
        tenant_id,
    )
    return db_tenant


@app.delete("/tenants/{tenant_id}", status_code=204)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    deleted = crud.delete_tenant(db=db, tenant_id=tenant_id)
    if not deleted:
        security_logger.warning(
            "SECURITY_EVENT=delete_tenant_failed client_ip=%s tenant_id=%s",
            client_ip,
            tenant_id,
        )
        raise HTTPException(status_code=404, detail="Tenant not found")

    security_logger.info(
        "SECURITY_EVENT=delete_tenant_success client_ip=%s tenant_id=%s",
        client_ip,
        tenant_id,
    )
    return None


# Contact Person endpoints
@app.post("/tenants/{tenant_id}/contacts", response_model=schemas.ContactPersonResponse, status_code=201)
def create_contact_person(
    tenant_id: int,
    contact: schemas.ContactPersonCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    if contact.tenant_id != tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID mismatch")

    client_ip = get_client_ip(request)
    security_logger.info(
        "SECURITY_EVENT=create_contact_person client_ip=%s tenant_id=%s email=%s",
        client_ip,
        tenant_id,
        contact.email,
    )
    return crud.create_contact_person(db=db, contact=contact)


@app.get("/tenants/{tenant_id}/contacts", response_model=List[schemas.ContactPersonResponse])
def list_contact_persons(
    tenant_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    security_logger.info(
        "SECURITY_EVENT=list_contact_persons client_ip=%s tenant_id=%s",
        get_client_ip(request),
        tenant_id,
    )
    return crud.get_contact_persons_by_tenant(db=db, tenant_id=tenant_id)


@app.get("/tenants/{tenant_id}/contacts/{contact_id}", response_model=schemas.ContactPersonResponse)
def read_contact_person(
    tenant_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_contact = crud.get_contact_person(db=db, contact_id=contact_id)
    if db_contact is None or db_contact.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=read_contact_person_failed client_ip=%s tenant_id=%s contact_id=%s",
            client_ip,
            tenant_id,
            contact_id,
        )
        raise HTTPException(status_code=404, detail="Contact person not found")

    security_logger.info(
        "SECURITY_EVENT=read_contact_person_success client_ip=%s tenant_id=%s contact_id=%s",
        client_ip,
        tenant_id,
        contact_id,
    )
    return db_contact


@app.put("/tenants/{tenant_id}/contacts/{contact_id}", response_model=schemas.ContactPersonResponse)
def update_contact_person(
    tenant_id: int,
    contact_id: int,
    contact: schemas.ContactPersonUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_contact = crud.get_contact_person(db=db, contact_id=contact_id)
    if db_contact is None or db_contact.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=update_contact_person_failed client_ip=%s tenant_id=%s contact_id=%s",
            client_ip,
            tenant_id,
            contact_id,
        )
        raise HTTPException(status_code=404, detail="Contact person not found")

    updated_contact = crud.update_contact_person(db=db, contact_id=contact_id, contact_update=contact)
    security_logger.info(
        "SECURITY_EVENT=update_contact_person_success client_ip=%s tenant_id=%s contact_id=%s",
        client_ip,
        tenant_id,
        contact_id,
    )
    return updated_contact


@app.delete("/tenants/{tenant_id}/contacts/{contact_id}", status_code=204)
def delete_contact_person(
    tenant_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_contact = crud.get_contact_person(db=db, contact_id=contact_id)
    if db_contact is None or db_contact.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=delete_contact_person_failed client_ip=%s tenant_id=%s contact_id=%s",
            client_ip,
            tenant_id,
            contact_id,
        )
        raise HTTPException(status_code=404, detail="Contact person not found")

    deleted = crud.delete_contact_person(db=db, contact_id=contact_id)
    security_logger.info(
        "SECURITY_EVENT=delete_contact_person_success client_ip=%s tenant_id=%s contact_id=%s",
        client_ip,
        tenant_id,
        contact_id,
    )
    return None


# Workshop endpoints
@app.post("/tenants/{tenant_id}/workshops", response_model=schemas.WorkshopResponse, status_code=201)
def create_workshop(
    tenant_id: int,
    workshop: schemas.WorkshopCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    if workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID mismatch")

    client_ip = get_client_ip(request)
    security_logger.info(
        "SECURITY_EVENT=create_workshop client_ip=%s tenant_id=%s description=%s",
        client_ip,
        tenant_id,
        workshop.description,
    )
    return crud.create_workshop(db=db, workshop=workshop)


@app.get("/tenants/{tenant_id}/workshops", response_model=List[schemas.WorkshopResponse])
def list_workshops(
    tenant_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    security_logger.info(
        "SECURITY_EVENT=list_workshops client_ip=%s tenant_id=%s",
        get_client_ip(request),
        tenant_id,
    )
    return crud.get_workshops_by_tenant(db=db, tenant_id=tenant_id)


@app.get("/tenants/{tenant_id}/workshops/{workshop_id}", response_model=schemas.WorkshopResponse)
def read_workshop(
    tenant_id: int,
    workshop_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=read_workshop_failed client_ip=%s tenant_id=%s workshop_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
        )
        raise HTTPException(status_code=404, detail="Workshop not found")

    security_logger.info(
        "SECURITY_EVENT=read_workshop_success client_ip=%s tenant_id=%s workshop_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
    )
    return db_workshop


@app.put("/tenants/{tenant_id}/workshops/{workshop_id}", response_model=schemas.WorkshopResponse)
def update_workshop(
    tenant_id: int,
    workshop_id: int,
    workshop: schemas.WorkshopUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=update_workshop_failed client_ip=%s tenant_id=%s workshop_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
        )
        raise HTTPException(status_code=404, detail="Workshop not found")

    updated_workshop = crud.update_workshop(db=db, workshop_id=workshop_id, workshop_update=workshop)
    security_logger.info(
        "SECURITY_EVENT=update_workshop_success client_ip=%s tenant_id=%s workshop_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
    )
    return updated_workshop


@app.delete("/tenants/{tenant_id}/workshops/{workshop_id}", status_code=204)
def delete_workshop(
    tenant_id: int,
    workshop_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=delete_workshop_failed client_ip=%s tenant_id=%s workshop_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
        )
        raise HTTPException(status_code=404, detail="Workshop not found")

    deleted = crud.delete_workshop(db=db, workshop_id=workshop_id)
    security_logger.info(
        "SECURITY_EVENT=delete_workshop_success client_ip=%s tenant_id=%s workshop_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
    )
    return None


# Course endpoints
@app.post("/tenants/{tenant_id}/workshops/{workshop_id}/courses", response_model=schemas.CourseResponse, status_code=201)
def create_course(
    tenant_id: int,
    workshop_id: int,
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    if course.workshop_id != workshop_id:
        raise HTTPException(status_code=400, detail="Workshop ID mismatch")

    # Verify workshop belongs to tenant
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workshop not found")

    client_ip = get_client_ip(request)
    security_logger.info(
        "SECURITY_EVENT=create_course client_ip=%s tenant_id=%s workshop_id=%s name=%s",
        client_ip,
        tenant_id,
        workshop_id,
        course.name,
    )
    return crud.create_course(db=db, course=course)


@app.get("/tenants/{tenant_id}/workshops/{workshop_id}/courses", response_model=List[schemas.CourseResponse])
def list_courses(
    tenant_id: int,
    workshop_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    # Verify workshop belongs to tenant
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workshop not found")

    security_logger.info(
        "SECURITY_EVENT=list_courses client_ip=%s tenant_id=%s workshop_id=%s",
        get_client_ip(request),
        tenant_id,
        workshop_id,
    )
    return crud.get_courses_by_workshop(db=db, workshop_id=workshop_id)


@app.get("/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}", response_model=schemas.CourseResponse)
def read_course(
    tenant_id: int,
    workshop_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_course = crud.get_course(db=db, course_id=course_id)
    if db_course is None or db_course.workshop_id != workshop_id:
        security_logger.warning(
            "SECURITY_EVENT=read_course_failed client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
            course_id,
        )
        raise HTTPException(status_code=404, detail="Course not found")

    # Verify workshop belongs to tenant
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workshop not found")

    security_logger.info(
        "SECURITY_EVENT=read_course_success client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
        course_id,
    )
    return db_course


@app.put("/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}", response_model=schemas.CourseResponse)
def update_course(
    tenant_id: int,
    workshop_id: int,
    course_id: int,
    course: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_course = crud.get_course(db=db, course_id=course_id)
    if db_course is None or db_course.workshop_id != workshop_id:
        security_logger.warning(
            "SECURITY_EVENT=update_course_failed client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
            course_id,
        )
        raise HTTPException(status_code=404, detail="Course not found")

    # Verify workshop belongs to tenant
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workshop not found")

    updated_course = crud.update_course(db=db, course_id=course_id, course_update=course)
    security_logger.info(
        "SECURITY_EVENT=update_course_success client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
        course_id,
    )
    return updated_course


@app.delete("/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}", status_code=204)
def delete_course(
    tenant_id: int,
    workshop_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_course = crud.get_course(db=db, course_id=course_id)
    if db_course is None or db_course.workshop_id != workshop_id:
        security_logger.warning(
            "SECURITY_EVENT=delete_course_failed client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
            client_ip,
            tenant_id,
            workshop_id,
            course_id,
        )
        raise HTTPException(status_code=404, detail="Course not found")

    # Verify workshop belongs to tenant
    db_workshop = crud.get_workshop(db=db, workshop_id=workshop_id)
    if db_workshop is None or db_workshop.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workshop not found")

    deleted = crud.delete_course(db=db, course_id=course_id)
    security_logger.info(
        "SECURITY_EVENT=delete_course_success client_ip=%s tenant_id=%s workshop_id=%s course_id=%s",
        client_ip,
        tenant_id,
        workshop_id,
        course_id,
    )
    return None


# Document endpoints
@app.post("/tenants/{tenant_id}/documents", response_model=schemas.DocumentResponse, status_code=201)
def create_document(
    tenant_id: int,
    title: str = Form(...),
    short_description: str = Form(...),
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None,
):
    if document.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Document must be a PDF file.")

    document_bytes = document.file.read()
    document_data = schemas.DocumentCreate(
        title=title,
        short_description=short_description,
        tenant_id=tenant_id,
    )
    created_document = crud.create_document(
        db=db,
        document=document_data,
        document_bytes=document_bytes,
    )

    security_logger.info(
        "SECURITY_EVENT=create_document client_ip=%s tenant_id=%s title=%s",
        get_client_ip(request),
        tenant_id,
        title,
    )
    return created_document


@app.get("/tenants/{tenant_id}/documents", response_model=List[schemas.DocumentResponse])
def list_documents(
    tenant_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    security_logger.info(
        "SECURITY_EVENT=list_documents client_ip=%s tenant_id=%s",
        get_client_ip(request),
        tenant_id,
    )
    return crud.get_documents_by_tenant(db=db, tenant_id=tenant_id)


@app.get("/tenants/{tenant_id}/documents/{document_id}", response_class=StreamingResponse)
def read_document(
    tenant_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_document = crud.get_document(db=db, document_id=document_id)
    if db_document is None or db_document.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=read_document_failed client_ip=%s tenant_id=%s document_id=%s",
            client_ip,
            tenant_id,
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    security_logger.info(
        "SECURITY_EVENT=read_document_success client_ip=%s tenant_id=%s document_id=%s",
        client_ip,
        tenant_id,
        document_id,
    )
    return StreamingResponse(
        io.BytesIO(db_document.document),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={db_document.title}.pdf"},
    )


@app.put("/tenants/{tenant_id}/documents/{document_id}", response_model=schemas.DocumentResponse)
def update_document(
    tenant_id: int,
    document_id: int,
    title: str = Form(...),
    short_description: str = Form(...),
    document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_document = crud.get_document(db=db, document_id=document_id)
    if db_document is None or db_document.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=update_document_failed client_ip=%s tenant_id=%s document_id=%s",
            client_ip,
            tenant_id,
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    document_bytes = None
    if document:
        if document.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Document must be a PDF file.")
        document_bytes = document.file.read()

    document_update = schemas.DocumentUpdate(
        title=title,
        short_description=short_description,
    )
    updated_document = crud.update_document(
        db=db,
        document_id=document_id,
        document_update=document_update,
        document_bytes=document_bytes,
    )
    security_logger.info(
        "SECURITY_EVENT=update_document_success client_ip=%s tenant_id=%s document_id=%s",
        client_ip,
        tenant_id,
        document_id,
    )
    return updated_document


@app.delete("/tenants/{tenant_id}/documents/{document_id}", status_code=204)
def delete_document(
    tenant_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_document = crud.get_document(db=db, document_id=document_id)
    if db_document is None or db_document.tenant_id != tenant_id:
        security_logger.warning(
            "SECURITY_EVENT=delete_document_failed client_ip=%s tenant_id=%s document_id=%s",
            client_ip,
            tenant_id,
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    deleted = crud.delete_document(db=db, document_id=document_id)
    security_logger.info(
        "SECURITY_EVENT=delete_document_success client_ip=%s tenant_id=%s document_id=%s",
        client_ip,
        tenant_id,
        document_id,
    )
    return None
