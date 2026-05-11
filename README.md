# Gyde Multitenant FastAPI Service

FastAPI based multitenant application with PostgreSQL-backed CRUD for tenants, contact persons, workshops, courses, and documents.

## Tech stack

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL via `psycopg2-binary`
- `python-dotenv` for environment configuration
- `pytest` and `httpx` for testing

## Setup

1. Install `uv` if you don't already have it:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a local environment file and configure the database URL:
   ```bash
   cp .env.example .env
   ```

   The default connection string is:
   ```text
   postgresql://postgres:postgres@localhost:5432/postgres
   ```

3. Initialize the uv environment and install dependencies:
   ```bash
   uv sync
   ```

4. Start a local PostgreSQL database using Docker Compose (optional but recommended):
   ```bash
   docker compose up -d
   ```

5. Run the app with uv-managed dependencies:
   ```bash
   uv run uvicorn gyde.main:app --reload
   ```

## Run tests

Use the uv environment to run the test suite:
```bash
uv run pytest
```

## Load sample test data

Start the API and then run:
```bash
uv run python load_test_data.py
```

This will create a demo tenant with sample workshops, contacts, and courses.

To load custom data from JSON files:
```bash
uv run python load_test_data.py --tenant-file custom_tenant.json --workshops-file custom_workshops.json --contacts-file custom_contacts.json
```

## API Structure

The API is organized around tenants, where each tenant has isolated data including:

- Contact persons
- Workshops
- Courses (nested under workshops)
- Documents

All endpoints are scoped under `/tenants/{tenant_id}/` to ensure data isolation.

## Endpoints

### Tenants

- `POST /tenants` - create a tenant
- `GET /tenants` - list all tenants
- `GET /tenants/{tenant_id}` - get a specific tenant
- `PUT /tenants/{tenant_id}` - update a tenant
- `DELETE /tenants/{tenant_id}` - delete a tenant

### Contact Persons

- `POST /tenants/{tenant_id}/contacts` - create a contact person for a tenant
- `GET /tenants/{tenant_id}/contacts` - list all contact persons for a tenant
- `GET /tenants/{tenant_id}/contacts/{contact_id}` - get a specific contact person
- `PUT /tenants/{tenant_id}/contacts/{contact_id}` - update a contact person
- `DELETE /tenants/{tenant_id}/contacts/{contact_id}` - delete a contact person

### Workshops

- `POST /tenants/{tenant_id}/workshops` - create a workshop for a tenant
- `GET /tenants/{tenant_id}/workshops` - list all workshops for a tenant
- `GET /tenants/{tenant_id}/workshops/{workshop_id}` - get a specific workshop
- `PUT /tenants/{tenant_id}/workshops/{workshop_id}` - update a workshop
- `DELETE /tenants/{tenant_id}/workshops/{workshop_id}` - delete a workshop

### Courses

- `POST /tenants/{tenant_id}/workshops/{workshop_id}/courses` - create a course for a workshop
- `GET /tenants/{tenant_id}/workshops/{workshop_id}/courses` - list all courses for a workshop
- `GET /tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}` - get a specific course
- `PUT /tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}` - update a course
- `DELETE /tenants/{tenant_id}/workshops/{workshop_id}/courses/{course_id}` - delete a course

### Documents

- `POST /tenants/{tenant_id}/documents` - upload a PDF document with metadata (title, short_description)
- `GET /tenants/{tenant_id}/documents` - list saved document metadata for a tenant
- `GET /tenants/{tenant_id}/documents/{document_id}` - download a saved PDF document
- `PUT /tenants/{tenant_id}/documents/{document_id}` - update document metadata or PDF file
- `DELETE /tenants/{tenant_id}/documents/{document_id}` - delete a saved document

## Data Model

### Tenant
- `id`: Unique identifier
- `name`: Tenant name
- `post_address`: Postal address

### ContactPerson
- `id`: Unique identifier
- `first_name`: First name
- `last_name`: Last name
- `email`: Email address
- `phone`: Phone number
- `tenant_id`: Reference to owning tenant

### Workshop
- `id`: Unique identifier
- `description`: Workshop description
- `number_of_courses`: Number of courses in the workshop
- `tenant_id`: Reference to owning tenant

### Course
- `id`: Unique identifier
- `name`: Course name
- `pdf_text`: PDF content as text
- `workshop_id`: Reference to parent workshop

### Document
- `id`: Unique identifier
- `title`: Document title
- `short_description`: Brief description
- `document`: PDF file content (binary)
- `tenant_id`: Reference to owning tenant

## Security

The API includes security logging for all operations, tracking client IP addresses and operation details. All data is properly isolated by tenant to ensure multitenancy.
