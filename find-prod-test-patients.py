#!/usr/bin/env python3
"""
Find patients by org Id from ddb
Usage:
    python find_patients_from_org_id.py -o <YOUR_ORG_ID>
"""

import argparse
import sys

import boto3
from boto3.dynamodb.conditions import Attr

DEFAULT_ORG_ID = "e55e48b3-32f7-4ee0-b3af-6fd062e471d0"
TABLE_NAME = "Patient"
REGION = "us-east-1"


def find_patients(org_id=DEFAULT_ORG_ID, table_name=TABLE_NAME):
    patients_found: list[str] = []

    try:
        dynamodb = boto3.resource("dynamodb", region_name=REGION)
        table = dynamodb.Table(table_name)  # type: ignore

        print(
            (
                f"Searching for patients with insuranceOrg: {org_id}. "
                "This may take a while..."
            )
        )
        print("Press Ctrl+C to stop when you have enough results\n")
        scan_kwargs = {"FilterExpression": Attr("insuranceOrg").eq(org_id)}

        pages_scanned = 0
        done = False
        start_key = None

        while not done:
            pages_scanned += 1
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key

            response = table.scan(**scan_kwargs)
            items = response.get("Items", [])

            for item in items:
                patient_id = item.get("id")
                if patient_id:
                    print("\nFOUND PATIENT\n")
                    print(patient_id)
                    print()
                    patients_found.append(patient_id)

            start_key = response.get("LastEvaluatedKey")
            done = start_key is None

            if pages_scanned % 100 == 0:
                print(
                    f"Scanned {pages_scanned} pages and found "
                    f"{len(patients_found)} patients"
                )

        print(f"\nFound {len(patients_found)} total patients for: {org_id}")
        for id in patients_found:
            print(id)

    except KeyboardInterrupt:
        print(f"\nStopped by user. Found {len(patients_found)} patients")
        for id in patients_found:
            print(id)
        sys.exit(0)

    except Exception as e:
        print(f"\nProgram crashed unexpectedly: {e} \n Patients found:")
        for id in patients_found:
            print(id)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Find patients by org ID")

    parser.add_argument(
        "-o",
        "--org-id",
        help="Organization UUID to search for",
        default=DEFAULT_ORG_ID,
    )

    args = parser.parse_args()

    find_patients(args.org_id)


if __name__ == "__main__":
    main()
