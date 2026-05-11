import io
import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gyde Record API")

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
    return {"message": "Gyde Record API is running"}


@app.post("/records", response_model=schemas.RecordResponse, status_code=201)
def upload_data(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    security_logger.info(
        "SECURITY_EVENT=create_record client_ip=%s description=%s number_of_courses=%s",
        client_ip,
        record.description,
        record.number_of_courses,
    )
    return crud.create_record(db=db, record=record)


@app.get("/records", response_model=List[schemas.RecordResponse])
def read_data(db: Session = Depends(get_db), request: Request = None):
    security_logger.info(
        "SECURITY_EVENT=list_records client_ip=%s path=%s",
        get_client_ip(request),
        request.url.path,
    )
    return crud.get_records(db=db)


@app.get("/records/{record_id}", response_model=schemas.RecordResponse)
def read_single_data(
    record_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_record = crud.get_record(db=db, record_id=record_id)
    if db_record is None:
        security_logger.warning(
            "SECURITY_EVENT=read_record_failed client_ip=%s record_id=%s",
            client_ip,
            record_id,
        )
        raise HTTPException(status_code=404, detail="Record not found")

    security_logger.info(
        "SECURITY_EVENT=read_record_success client_ip=%s record_id=%s",
        client_ip,
        record_id,
    )
    return db_record


@app.put("/records/{record_id}", response_model=schemas.RecordResponse)
def update_data(
    record_id: int,
    record: schemas.RecordUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    db_record = crud.update_record(db=db, record_id=record_id, record_update=record)
    if db_record is None:
        security_logger.warning(
            "SECURITY_EVENT=update_record_failed client_ip=%s record_id=%s",
            client_ip,
            record_id,
        )
        raise HTTPException(status_code=404, detail="Record not found")

    security_logger.info(
        "SECURITY_EVENT=update_record_success client_ip=%s record_id=%s updated_fields=%s",
        client_ip,
        record_id,
        {"description": record.description, "number_of_courses": record.number_of_courses},
    )
    return db_record


@app.delete("/records/{record_id}", status_code=204)
def delete_data(
    record_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    deleted = crud.delete_record(db=db, record_id=record_id)
    if not deleted:
        security_logger.warning(
            "SECURITY_EVENT=delete_record_failed client_ip=%s record_id=%s",
            client_ip,
            record_id,
        )
        raise HTTPException(status_code=404, detail="Record not found")

    security_logger.info(
        "SECURITY_EVENT=delete_record_success client_ip=%s record_id=%s",
        client_ip,
        record_id,
    )
    return None


@app.post("/documents", response_model=schemas.DocumentResponse, status_code=201)
def create_document(
    customer_id: str = Form(...),
    title: str = Form(...),
    short_description: str = Form(...),
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None,
):
    if document.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Document must be a PDF file.")

    document_bytes = document.file.read()
    created_document = crud.create_document(
        db=db,
        customer_id=customer_id,
        title=title,
        short_description=short_description,
        document_bytes=document_bytes,
    )

    security_logger.info(
        "SECURITY_EVENT=create_document client_ip=%s title=%s customer_id=%s",
        get_client_ip(request),
        title,
        customer_id,
    )
    return created_document


@app.get("/documents", response_model=list[schemas.DocumentResponse])
def read_documents(db: Session = Depends(get_db), request: Request = None):
    security_logger.info(
        "SECURITY_EVENT=list_documents client_ip=%s path=%s",
        get_client_ip(request),
        request.url.path,
    )
    return crud.get_documents(db=db)


@app.get("/documents/{document_id}")
def read_document_pdf(
    document_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    db_document = crud.get_document(db=db, document_id=document_id)
    if db_document is None:
        security_logger.warning(
            "SECURITY_EVENT=read_document_failed client_ip=%s document_id=%s",
            get_client_ip(request),
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    security_logger.info(
        "SECURITY_EVENT=read_document_success client_ip=%s document_id=%s",
        get_client_ip(request),
        document_id,
    )
    pdf_stream = io.BytesIO(db_document.document)
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f'inline; filename="{db_document.title}.pdf"'
    return response


@app.put("/documents/{document_id}", response_model=schemas.DocumentResponse)
def update_document(
    document_id: int,
    customer_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    document: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    document_bytes = None
    if document is not None:
        if document.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Document must be a PDF file.")
        document_bytes = document.file.read()

    document_update = schemas.DocumentUpdate(
        customer_id=customer_id,
        title=title,
        short_description=short_description,
    )
    updated_document = crud.update_document(
        db=db,
        document_id=document_id,
        document_update=document_update,
        document_bytes=document_bytes,
    )

    if updated_document is None:
        security_logger.warning(
            "SECURITY_EVENT=update_document_failed client_ip=%s document_id=%s",
            get_client_ip(request),
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    security_logger.info(
        "SECURITY_EVENT=update_document_success client_ip=%s document_id=%s",
        get_client_ip(request),
        document_id,
    )
    return updated_document


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    client_ip = get_client_ip(request)
    deleted = crud.delete_document(db=db, document_id=document_id)
    if not deleted:
        security_logger.warning(
            "SECURITY_EVENT=delete_document_failed client_ip=%s document_id=%s",
            client_ip,
            document_id,
        )
        raise HTTPException(status_code=404, detail="Document not found")

    security_logger.info(
        "SECURITY_EVENT=delete_document_success client_ip=%s document_id=%s",
        client_ip,
        document_id,
    )
    return None
