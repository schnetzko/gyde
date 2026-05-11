#!/usr/bin/env python3
"""Load sample test data into the running Gyde Multitenant API."""

import argparse
import json
import sys

SAMPLE_TENANT = {"name": "Demo Tenant", "post_address": "123 Demo Street, Demo City"}

SAMPLE_WORKSHOPS = [
    {"description": "Introduction to Gyde", "number_of_courses": 1},
    {"description": "FastAPI CRUD tutorial", "number_of_courses": 3},
    {"description": "PostgreSQL integration demo", "number_of_courses": 2},
    {"description": "End-to-end test workshop", "number_of_courses": 5},
]

SAMPLE_CONTACTS = [
    {"first_name": "John", "last_name": "Doe", "email": "john.doe@demo.com", "phone": "+1234567890"},
    {"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@demo.com", "phone": "+1234567891"},
]

SAMPLE_COURSES = [
    {"name": "Getting Started", "pdf_text": "Welcome to the course!"},
    {"name": "Advanced Topics", "pdf_text": "Deep dive into advanced concepts"},
]

SAMPLE_DOCUMENTS = [
    {"title": "Sample Document 1", "short_description": "A sample PDF document", "document_bytes": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"},
    {"title": "Sample Document 2", "short_description": "Another sample PDF document", "document_bytes": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Sample Doc) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"},
]


def post_tenant(base_url, tenant):
    url = base_url.rstrip("/") + "/tenants"
    try:
        import httpx

        with httpx.Client() as client:
            response = client.post(url, json=tenant)
            print_result("TENANT", tenant, response.status_code, response.text)
            if response.status_code == 201:
                return response.json()["id"]
    except ImportError:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        data = json.dumps(tenant).encode("utf-8")
        request = Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request) as response:
                body = response.read().decode("utf-8")
                print_result("TENANT", tenant, response.status, body)
                return json.loads(body)["id"]
        except HTTPError as exc:
            print_result("TENANT", tenant, exc.code, exc.read().decode("utf-8"))
        except URLError as exc:
            print(f"Failed to connect to {url}: {exc}")
            sys.exit(1)


def post_contacts(base_url, tenant_id, contacts):
    url = base_url.rstrip("/") + f"/tenants/{tenant_id}/contacts"
    try:
        import httpx

        with httpx.Client() as client:
            for contact in contacts:
                contact_data = {**contact, "tenant_id": tenant_id}
                response = client.post(url, json=contact_data)
                print_result("CONTACT", contact, response.status_code, response.text)
    except ImportError:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        for contact in contacts:
            contact_data = {**contact, "tenant_id": tenant_id}
            data = json.dumps(contact_data).encode("utf-8")
            request = Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request) as response:
                    body = response.read().decode("utf-8")
                    print_result("CONTACT", contact, response.status, body)
            except HTTPError as exc:
                print_result("CONTACT", contact, exc.code, exc.read().decode("utf-8"))
            except URLError as exc:
                print(f"Failed to connect to {url}: {exc}")
                sys.exit(1)


def post_workshops(base_url, tenant_id, workshops):
    url = base_url.rstrip("/") + f"/tenants/{tenant_id}/workshops"
    try:
        import httpx

        with httpx.Client() as client:
            for workshop in workshops:
                workshop_data = {**workshop, "tenant_id": tenant_id}
                response = client.post(url, json=workshop_data)
                print_result("WORKSHOP", workshop, response.status_code, response.text)
                if response.status_code == 201:
                    workshop_id = response.json()["id"]
                    # Create sample courses for each workshop
                    post_courses(base_url, tenant_id, workshop_id, SAMPLE_COURSES)
    except ImportError:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        for workshop in workshops:
            workshop_data = {**workshop, "tenant_id": tenant_id}
            data = json.dumps(workshop_data).encode("utf-8")
            request = Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request) as response:
                    body = response.read().decode("utf-8")
                    print_result("WORKSHOP", workshop, response.status, body)
            except HTTPError as exc:
                print_result("WORKSHOP", workshop, exc.code, exc.read().decode("utf-8"))
            except URLError as exc:
                print(f"Failed to connect to {url}: {exc}")
                sys.exit(1)


def post_courses(base_url, tenant_id, workshop_id, courses):
    url = base_url.rstrip("/") + f"/tenants/{tenant_id}/workshops/{workshop_id}/courses"
    try:
        import httpx

        with httpx.Client() as client:
            for course in courses:
                course_data = {**course, "workshop_id": workshop_id}
                response = client.post(url, json=course_data)
                print_result("COURSE", course, response.status_code, response.text)
    except ImportError:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        for course in courses:
            course_data = {**course, "workshop_id": workshop_id}
            data = json.dumps(course_data).encode("utf-8")
            request = Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request) as response:
                    body = response.read().decode("utf-8")
                    print_result("COURSE", course, response.status, body)
            except HTTPError as exc:
                print_result("COURSE", course, exc.code, exc.read().decode("utf-8"))
            except URLError as exc:
                print(f"Failed to connect to {url}: {exc}")
                sys.exit(1)


def post_documents(base_url, tenant_id, documents):
    url = base_url.rstrip("/") + f"/tenants/{tenant_id}/documents"
    try:
        import httpx

        with httpx.Client() as client:
            for document in documents:
                files = {
                    "document": ("sample.pdf", document["document_bytes"], "application/pdf")
                }
                data = {
                    "title": document["title"],
                    "short_description": document["short_description"]
                }
                response = client.post(url, data=data, files=files)
                print_result("DOCUMENT", document, response.status_code, response.text)
    except ImportError:
        # For urllib, multipart is more complex, so skip for now
        print("Documents require httpx for multipart upload. Install httpx or use the API directly.")
        return


def print_result(entity_type, data, status, body):
    print(f"POST {entity_type}: {data}")
    print(f"Status: {status}")
    print(f"Response: {body}")
    print("---")


def parse_args():
    parser = argparse.ArgumentParser(description="Load sample test data into the Gyde Multitenant API.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL for the running API (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--tenant-file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="Optional JSON file with tenant data.",
    )
    parser.add_argument(
        "--workshops-file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="Optional JSON file with a list of workshop objects.",
    )
    parser.add_argument(
        "--contacts-file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="Optional JSON file with a list of contact objects.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    tenant = SAMPLE_TENANT
    if args.tenant_file:
        tenant = json.load(args.tenant_file)
        if not isinstance(tenant, dict):
            print("Tenant JSON file must contain a tenant object.")
            sys.exit(1)

    workshops = SAMPLE_WORKSHOPS
    if args.workshops_file:
        workshops = json.load(args.workshops_file)
        if not isinstance(workshops, list):
            print("Workshops JSON file must contain a list of workshop objects.")
            sys.exit(1)

    contacts = SAMPLE_CONTACTS
    if args.contacts_file:
        contacts = json.load(args.contacts_file)
        if not isinstance(contacts, list):
            print("Contacts JSON file must contain a list of contact objects.")
            sys.exit(1)

    # Create tenant first
    tenant_id = post_tenant(args.base_url, tenant)
    if not tenant_id:
        print("Failed to create tenant. Exiting.")
        sys.exit(1)

    # Create contacts for the tenant
    post_contacts(args.base_url, tenant_id, contacts)

    # Create documents for the tenant
    post_documents(args.base_url, tenant_id, SAMPLE_DOCUMENTS)

    # Create workshops for the tenant
    post_workshops(args.base_url, tenant_id, workshops)


if __name__ == "__main__":
    main()
