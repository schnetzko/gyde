from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gyde Record API")


@app.get("/", status_code=200)
def read_root():
    return {"message": "Gyde Record API is running"}


@app.post("/records", response_model=schemas.RecordResponse, status_code=201)
def upload_data(record: schemas.RecordCreate, db: Session = Depends(get_db)):
    return crud.create_record(db=db, record=record)


@app.get("/records", response_model=List[schemas.RecordResponse])
def read_data(db: Session = Depends(get_db)):
    return crud.get_records(db=db)


@app.get("/records/{record_id}", response_model=schemas.RecordResponse)
def read_single_data(record_id: int, db: Session = Depends(get_db)):
    db_record = crud.get_record(db=db, record_id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@app.put("/records/{record_id}", response_model=schemas.RecordResponse)
def update_data(record_id: int, record: schemas.RecordUpdate, db: Session = Depends(get_db)):
    db_record = crud.update_record(db=db, record_id=record_id, record_update=record)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record


@app.delete("/records/{record_id}", status_code=204)
def delete_data(record_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_record(db=db, record_id=record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return None
