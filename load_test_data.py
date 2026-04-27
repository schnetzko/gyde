#!/usr/bin/env python3
"""Load sample test records into the running Gyde API."""

import argparse
import json
import sys

SAMPLE_RECORDS = [
    {"description": "Introduction to Gyde", "number_of_courses": 1},
    {"description": "FastAPI CRUD tutorial", "number_of_courses": 3},
    {"description": "PostgreSQL integration demo", "number_of_courses": 2},
    {"description": "End-to-end test record", "number_of_courses": 5},
]


def post_records(base_url, records):
    url = base_url.rstrip("/") + "/records"
    try:
        import httpx

        with httpx.Client() as client:
            for record in records:
                response = client.post(url, json=record)
                print_result(record, response.status_code, response.text)
    except ImportError:
        from urllib.error import HTTPError, URLError
        from urllib.request import Request, urlopen

        for record in records:
            data = json.dumps(record).encode("utf-8")
            request = Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request) as response:
                    body = response.read().decode("utf-8")
                    print_result(record, response.status, body)
            except HTTPError as exc:
                print_result(record, exc.code, exc.read().decode("utf-8"))
            except URLError as exc:
                print(f"Failed to connect to {url}: {exc}")
                sys.exit(1)


def print_result(record, status, body):
    print("POST", record)
    print("Status:", status)
    print("Response:", body)
    print("---")


def parse_args():
    parser = argparse.ArgumentParser(description="Load sample test data into the Gyde API.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL for the running API (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="Optional JSON file with a list of records to load instead of sample data.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.file:
        records = json.load(args.file)
        if not isinstance(records, list):
            print("JSON file must contain a list of record objects.")
            sys.exit(1)
    else:
        records = SAMPLE_RECORDS

    post_records(args.base_url, records)


if __name__ == "__main__":
    main()
