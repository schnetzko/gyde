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
    assert response.json() == {"message": "Gyde Multitenant API is running"}


def test_tenant_crud_lifecycle():
    tenant_data = {"name": "Test Tenant", "post_address": "123 Test St"}

    create_response = client.post("/tenants", json=tenant_data)
    assert create_response.status_code == 201
    created_tenant = create_response.json()
    assert created_tenant["name"] == tenant_data["name"]
    assert created_tenant["post_address"] == tenant_data["post_address"]
    assert "id" in created_tenant

    tenant_id = created_tenant["id"]

    list_response = client.get("/tenants")
    assert list_response.status_code == 200
    tenants = list_response.json()
    assert len(tenants) == 1
    assert tenants[0]["id"] == tenant_id

    get_response = client.get(f"/tenants/{tenant_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == tenant_id

    update_data = {"name": "Updated Tenant", "post_address": "456 Updated St"}
    update_response = client.put(f"/tenants/{tenant_id}", json=update_data)
    assert update_response.status_code == 200
    updated_tenant = update_response.json()
    assert updated_tenant["name"] == update_data["name"]
    assert updated_tenant["post_address"] == update_data["post_address"]

    delete_response = client.delete(f"/tenants/{tenant_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/tenants/{tenant_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Tenant not found"


def test_contact_person_crud_lifecycle():
    # First create a tenant
    tenant_data = {"name": "Contact Test Tenant", "post_address": "789 Contact St"}
    tenant_response = client.post("/tenants", json=tenant_data)
    assert tenant_response.status_code == 201
    tenant_id = tenant_response.json()["id"]

    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "tenant_id": tenant_id
    }

    create_response = client.post(f"/tenants/{tenant_id}/contacts", json=contact_data)
    assert create_response.status_code == 201
    created_contact = create_response.json()
    assert created_contact["first_name"] == contact_data["first_name"]
    assert created_contact["last_name"] == contact_data["last_name"]
    assert created_contact["email"] == contact_data["email"]
    assert created_contact["phone"] == contact_data["phone"]
    assert created_contact["tenant_id"] == tenant_id
    assert "id" in created_contact

    contact_id = created_contact["id"]

    list_response = client.get(f"/tenants/{tenant_id}/contacts")
    assert list_response.status_code == 200
    contacts = list_response.json()
    assert len(contacts) == 1
    assert contacts[0]["id"] == contact_id

    get_response = client.get(f"/tenants/{tenant_id}/contacts/{contact_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == contact_id

    update_data = {"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@example.com"}
    update_response = client.put(f"/tenants/{tenant_id}/contacts/{contact_id}", json=update_data)
    assert update_response.status_code == 200
    updated_contact = update_response.json()
    assert updated_contact["first_name"] == update_data["first_name"]
    assert updated_contact["last_name"] == update_data["last_name"]
    assert updated_contact["email"] == update_data["email"]

    delete_response = client.delete(f"/tenants/{tenant_id}/contacts/{contact_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/tenants/{tenant_id}/contacts/{contact_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Contact person not found"


def test_workshop_crud_lifecycle():
    # First create a tenant
    tenant_data = {"name": "Workshop Test Tenant", "post_address": "101 Workshop Ave"}
    tenant_response = client.post("/tenants", json=tenant_data)
    assert tenant_response.status_code == 201
    tenant_id = tenant_response.json()["id"]

    workshop_data = {"description": "Test workshop", "number_of_courses": 3, "tenant_id": tenant_id}

    create_response = client.post(f"/tenants/{tenant_id}/workshops", json=workshop_data)
    assert create_response.status_code == 201
    created_workshop = create_response.json()
    assert created_workshop["description"] == workshop_data["description"]
    assert created_workshop["number_of_courses"] == workshop_data["number_of_courses"]
    assert created_workshop["tenant_id"] == tenant_id
    assert "id" in created_workshop

    workshop_id = created_workshop["id"]

    list_response = client.get(f"/tenants/{tenant_id}/workshops")
    assert list_response.status_code == 200
    workshops = list_response.json()
    assert len(workshops) == 1
    assert workshops[0]["id"] == workshop_id

    get_response = client.get(f"/tenants/{tenant_id}/workshops/{workshop_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == workshop_id

    update_data = {"description": "Updated workshop", "number_of_courses": 5}
    update_response = client.put(f"/tenants/{tenant_id}/workshops/{workshop_id}", json=update_data)
    assert update_response.status_code == 200
    updated_workshop = update_response.json()
    assert updated_workshop["description"] == update_data["description"]
    assert updated_workshop["number_of_courses"] == update_data["number_of_courses"]

    delete_response = client.delete(f"/tenants/{tenant_id}/workshops/{workshop_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/tenants/{tenant_id}/workshops/{workshop_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Workshop not found"


def test_course_crud_lifecycle():
    # First create a tenant and workshop
    tenant_data = {"name": "Course Test Tenant", "post_address": "202 Course Blvd"}
    tenant_response = client.post("/tenants", json=tenant_data)
    assert tenant_response.status_code == 201
    tenant_id = tenant_response.json()["id"]

    workshop_data = {"description": "Course workshop", "number_of_courses": 2, "tenant_id": tenant_id}
    workshop_response = client.post(f"/tenants/{tenant_id}/workshops", json=workshop_data)
    assert workshop_response.status_code == 201
    workshop_id = workshop_response.json()["id"]

    course_data = {"name": "Test Course", "pdf_text": "PDF content", "workshop_id": workshop_id}

    create_response = client.post(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses", json=course_data)
    assert create_response.status_code == 201
    created_course = create_response.json()
    assert created_course["name"] == course_data["name"]
    assert created_course["pdf_text"] == course_data["pdf_text"]
    assert created_course["workshop_id"] == workshop_id
    assert "id" in created_course

    course_id = created_course["id"]

    list_response = client.get(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses")
    assert list_response.status_code == 200
    courses = list_response.json()
    assert len(courses) == 1
    assert courses[0]["id"] == course_id

    get_response = client.get(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == course_id

    update_data = {"name": "Updated Course", "pdf_text": "Updated PDF content"}
    update_response = client.put(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}", json=update_data)
    assert update_response.status_code == 200
    updated_course = update_response.json()
    assert updated_course["name"] == update_data["name"]
    assert updated_course["pdf_text"] == update_data["pdf_text"]

    delete_response = client.delete(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Course not found"


def test_document_crud_lifecycle():
    # First create a tenant
    tenant_data = {"name": "Document Test Tenant", "post_address": "303 Document Rd"}
    tenant_response = client.post("/tenants", json=tenant_data)
    assert tenant_response.status_code == 201
    tenant_id = tenant_response.json()["id"]

    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R >>\nstartxref\n9\n%%EOF"

    create_response = client.post(
        f"/tenants/{tenant_id}/documents",
        data={
            "title": "Test Document",
            "short_description": "A test PDF document.",
        },
        files={"document": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert create_response.status_code == 201
    document_meta = create_response.json()
    assert document_meta["title"] == "Test Document"
    assert document_meta["short_description"] == "A test PDF document."
    assert document_meta["tenant_id"] == tenant_id
    assert "id" in document_meta

    document_id = document_meta["id"]

    list_response = client.get(f"/tenants/{tenant_id}/documents")
    assert list_response.status_code == 200
    documents = list_response.json()
    assert len(documents) == 1
    assert documents[0]["id"] == document_id

    get_pdf = client.get(f"/tenants/{tenant_id}/documents/{document_id}")
    assert get_pdf.status_code == 200
    assert get_pdf.headers["content-type"] == "application/pdf"
    assert get_pdf.content == pdf_bytes

    updated_pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R >>\nstartxref\n9\n%%EOF\n"
    update_response = client.put(
        f"/tenants/{tenant_id}/documents/{document_id}",
        data={
            "title": "Updated Document",
            "short_description": "An updated test PDF document.",
        },
        files={"document": ("updated.pdf", updated_pdf_bytes, "application/pdf")},
    )
    assert update_response.status_code == 200
    updated_meta = update_response.json()
    assert updated_meta["title"] == "Updated Document"
    assert updated_meta["short_description"] == "An updated test PDF document."

    get_updated_pdf = client.get(f"/tenants/{tenant_id}/documents/{document_id}")
    assert get_updated_pdf.status_code == 200
    assert get_updated_pdf.headers["content-type"] == "application/pdf"
    assert get_updated_pdf.content == updated_pdf_bytes

    delete_response = client.delete(f"/tenants/{tenant_id}/documents/{document_id}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    missing_response = client.get(f"/tenants/{tenant_id}/documents/{document_id}")
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Document not found"
