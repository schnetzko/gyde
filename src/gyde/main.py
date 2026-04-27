import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
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
