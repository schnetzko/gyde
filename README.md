# Gyde FastAPI CRUD Service

A simple FastAPI application with PostgreSQL-backed CRUD for records.

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

To load custom records from a JSON file:
```bash
uv run python load_test_data.py --file sample_records.json
```

## Endpoints

- `POST /records` - create/upload a record
- `GET /records` - read all records
- `GET /records/{record_id}` - read a single record
- `PUT /records/{record_id}` - update a record
- `DELETE /records/{record_id}` - delete a record
- `POST /documents` - upload a PDF document with metadata (customer_id, title, short_description)
- `GET /documents` - list saved document metadata
- `GET /documents/{document_id}` - download a saved PDF document
- `PUT /documents/{document_id}` - update document metadata or PDF file
- `DELETE /documents/{document_id}` - delete a saved document
