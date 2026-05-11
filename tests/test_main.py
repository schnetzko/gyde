from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from gyde import models
from gyde.database import Base

with patch.object(models.Base.metadata, "create_all", lambda bind: None):
    from gyde import main

SQLALCHEMY_TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main.app.dependency_overrides[main.get_db] = override_get_db
client = TestClient(main.app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Gyde Record API is running"}


def test_record_crud_lifecycle():
    record_data = {"description": "Test record", "number_of_courses": 3}

    create_response = client.post("/records", json=record_data)
    assert create_response.status_code == 201
    created_record = create_response.json()
    assert created_record["description"] == record_data["description"]
    assert created_record["number_of_courses"] == record_data["number_of_courses"]
    assert "id" in created_record

    record_id = created_record["id"]

    list_response = client.get("/records")
    assert list_response.status_code == 200
    records = list_response.json()
    assert len(records) == 1
    assert records[0]["id"] == record_id

    get_response = client.get(f"/records/{record_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == record_id

    update_data = {"description": "Updated description", "number_of_courses": 5}
    update_response = client.put(f"/records/{record_id}", json=update_data)
    assert update_response.status_code == 200
    updated_record = update_response.json()
    assert updated_record["description"] == update_data["description"]
    assert updated_record["number_of_courses"] == update_data["number_of_courses"]

    delete_response = client.delete(f"/records/{record_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/records/{record_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Record not found"


def test_load_test_data_via_endpoints():
    sample_records = [
        {"description": "Test record one", "number_of_courses": 1},
        {"description": "Test record two", "number_of_courses": 2},
        {"description": "Test record three", "number_of_courses": 3},
    ]

    created_ids = []
    for record in sample_records:
        response = client.post("/records", json=record)
        assert response.status_code == 201
        created_data = response.json()
        assert created_data["description"] == record["description"]
        assert created_data["number_of_courses"] == record["number_of_courses"]
        created_ids.append(created_data["id"])

    list_response = client.get("/records")
    assert list_response.status_code == 200
    records = list_response.json()
    assert len(records) == len(sample_records)
    assert [record["id"] for record in records] == created_ids

    # Confirm records were persisted in the underlying database
    with TestingSessionLocal() as db:
        db_records = db.query(models.Record).order_by(models.Record.id).all()
        assert len(db_records) == len(sample_records)
        assert [record.description for record in db_records] == [record["description"] for record in sample_records]
        assert [record.number_of_courses for record in db_records] == [record["number_of_courses"] for record in sample_records]


def test_document_crud_lifecycle():
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R >>\nstartxref\n9\n%%EOF"

    create_response = client.post(
        "/documents",
        data={
            "customer_id": "CUST-001",
            "title": "Project Proposal",
            "short_description": "A short project summary.",
        },
        files={"document": ("proposal.pdf", pdf_bytes, "application/pdf")},
    )
    assert create_response.status_code == 201
    document_meta = create_response.json()
    assert document_meta["customer_id"] == "CUST-001"
    assert document_meta["title"] == "Project Proposal"
    assert document_meta["short_description"] == "A short project summary."
    assert "id" in document_meta

    document_id = document_meta["id"]

    list_response = client.get("/documents")
    assert list_response.status_code == 200
    documents = list_response.json()
    assert len(documents) == 1
    assert documents[0]["id"] == document_id

    get_pdf = client.get(f"/documents/{document_id}")
    assert get_pdf.status_code == 200
    assert get_pdf.headers["content-type"] == "application/pdf"
    assert get_pdf.content == pdf_bytes

    updated_pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R >>\nstartxref\n9\n%%EOF\n"
    update_response = client.put(
        f"/documents/{document_id}",
        data={
            "customer_id": "CUST-002",
            "title": "Project Proposal v2",
        },
        files={"document": ("proposal_v2.pdf", updated_pdf_bytes, "application/pdf")},
    )
    assert update_response.status_code == 200
    updated_meta = update_response.json()
    assert updated_meta["customer_id"] == "CUST-002"
    assert updated_meta["title"] == "Project Proposal v2"

    get_updated_pdf = client.get(f"/documents/{document_id}")
    assert get_updated_pdf.status_code == 200
    assert get_updated_pdf.headers["content-type"] == "application/pdf"
    assert get_updated_pdf.content == updated_pdf_bytes

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/documents/{document_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Document not found"
