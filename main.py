#!/usr/bin/env python3

import csv
from collections import defaultdict
from itertools import groupby
from operator import itemgetter
import json
from pathlib import Path
from pprint import pprint
from sys import stdout
import pandas as pd

from flatten_dict import flatten

# turn xlsx files into csv files
# xlsx_file = "welcome_sdl_letters.xlsx"
# df = pd.read_excel(xlsx_file)

# welcome_sdl_letters = "welcome_sdl_letters.csv"
# df.to_csv(welcome_sdl_letters, index=False)

xlsx_file2 = "welcome_sdl_letters2.xlsx"
df = pd.read_excel(xlsx_file2)

welcome_sdl_letters2 = "welcome_sdl_letters2.csv"
df.to_csv(welcome_sdl_letters2, index=False)

orgs_file_name = "orgs-dev.json"
pdf_templates_file_name = "pdf-templates-dev.json"

# Load json lines into native python list for iterations later
orgs = []
for line in Path(orgs_file_name).read_text().splitlines():
    orgs.append(json.loads(line))

pdf_templates = []
for line in Path(pdf_templates_file_name).read_text().splitlines():
    pdf_templates.append(json.loads(line))

pdf_template_by_id = {i["id"]: i for i in pdf_templates}
pdf_template_ids = set(pdf_template_by_id.keys())

# here we compile a data structure(s) that will tell us which
# pdf template id's contain an orgTemplate as a key
# listed under one of "show_for, hide_for, or strings_replacement"
org_template_pdf_template_sets: dict[str, set] = defaultdict(set)
# create a pdf template id to name lookup dictionary
pdf_template_id2name = {
    pdf_template["id"]: pdf_template["name"] for pdf_template in pdf_templates
}


def find_org_templates_referenced(pdf_templates):
    get_org_template = itemgetter(0)
    return {
        org_template: set(pdf_template_id[1] for pdf_template_id in pdf_template_ids)
        for org_template, pdf_template_ids in groupby(
            sorted(
                find_org_templates_referenced_in(pdf_templates), key=get_org_template
            ),
            get_org_template,
        )
    }


def find_org_templates_referenced_in(pdf_templates):
    for pdf_template in pdf_templates:
        flattened_pdf_template = flatten(pdf_template, enumerate_types=(list,))
        for path, value in flattened_pdf_template.items():
            if referenced_in_show_for(path) or referenced_in_hide_for(path):
                yield before_colon(str(value)), pdf_template["id"]
            elif referenced_in_string_replacements(path):
                yield before_colon(
                    str(path[path.index("string_replacements") + 1])
                ), pdf_template["id"]


def referenced_in_show_for(path):
    return path[-2] == "show_for" and isinstance(path[-1], int)


def referenced_in_hide_for(path):
    return path[-2] == "hide_for" and isinstance(path[-1], int)


def referenced_in_string_replacements(path):
    return "string_replacements" in path


def before_colon(input_str):
    return input_str.split(":")[0]


# check each template and return the ones with show_for, hide_for, and string_replacements
# return all the found_org_template -> id
# for each template
# 1. we flatten it
# 2. we check whether it has 'show_for', 'hide_for', 'string_replacments'
# 3. if they do, then return the corresponding value, which is an org template
for pdf_template in pdf_templates:
    pdf_template_id = pdf_template["id"]
    pdf_template_name = pdf_template["name"]
    flattened_pdf_template = flatten(pdf_template, enumerate_types=(list,))

    for path, value in flattened_pdf_template.items():
        if len(path) > 2:
            if path[-2] in ("show_for", "hide_for") and isinstance(path[-1], int):
                found_org_template = str(value)
            elif "string_replacements" in path:
                found_org_template = str(path[path.index("string_replacements") + 1])
            else:
                continue

            found_org_template = found_org_template.split(":")[0]

            org_template_pdf_template_sets[found_org_template].add(pdf_template_id)

# Scaffolding for csv file
fieldnames = [
    "PDF Template ID",
    "PDF Template Name",
    "OrgTemplate ID",
    "Organization Name",
    "Organization ID",
]

writer = csv.DictWriter(stdout, fieldnames=fieldnames, dialect="excel-tab")
writer.writeheader()

rows: list[dict] = []

# Here we iterate through the orgs and are only interested in orgs with orgTemplate keys.
# We create a table row for every unique organization.
for org in orgs:
    org_name = org["name"]
    org_id = org["id"]
    org_template = org.get("report", {}).get("orgTemplate")
    org_json = json.dumps(org)

    for pdf_template_id in org_template_pdf_template_sets.get(org_template, []):
        # if not org_template_pdf_template_sets[org_template]:
        #     # ou_health is only used in one dev template
        #     # but 3 organizations in dev reference it in report.orgTemplate...
        #     continue

        if pdf_template_id not in org_json:
            continue

        pdf_template_name = pdf_template_id2name[pdf_template_id]

        rows.append(
            {
                "PDF Template ID": pdf_template_id,
                "PDF Template Name": pdf_template_name,
                "OrgTemplate ID": org_template,
                "Organization Name": f"{org_name}",
                "Organization ID": f"{org_id}",
            }
        )

    for pdf_template_id in pdf_template_ids:
        if pdf_template_id not in org_json:
            continue

        pdf_template_name = pdf_template_id2name[pdf_template_id]

        rows.append(
            {
                "PDF Template ID": pdf_template_id,
                "PDF Template Name": pdf_template_name,
                "OrgTemplate ID": org_template,
                "Organization Name": f"{org_name}",
                "Organization ID": f"{org_id}",
            }
        )

    with open("template-org-mapping.csv", mode="r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        for row in csv_reader:
            if row[1] == org["id"]:
                templateID = str(row[3])
                org_name = org["name"]
                org_id = org["id"]
                org_template = org.get("report", {}).get("orgTemplate")
                if templateID in pdf_template_by_id:
                    pdf_template_name = pdf_template_by_id[templateID].get("name")

                rows.append(
                    {
                        "PDF Template ID": row[3],
                        "PDF Template Name": pdf_template_name,
                        "OrgTemplate ID": org_template,
                        "Organization Name": f"{org_name}",
                        "Organization ID": f"{org_id}",
                    }
                )

    with open(welcome_sdl_letters2, mode="r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        for row in csv_reader:
            if row[1] == org["id"]:
                templateID = str(row[3])
                org_name = org["name"]
                org_id = org["id"]
                org_template = org.get("report", {}).get("orgTemplate")
                if templateID in pdf_template_by_id:
                    pdf_template_name = pdf_template_by_id[templateID].get("name")

                rows.append(
                    {
                        "PDF Template ID": row[3],
                        "PDF Template Name": pdf_template_name,
                        "OrgTemplate ID": org_template,
                        "Organization Name": f"{org_name}",
                        "Organization ID": f"{org_id}",
                    }
                )

# to de-duplicate the data:

temp_set: set[str] = set()

for row in rows:
    data = json.dumps(row, sort_keys=True)
    temp_set.add(data)

new_rows: list[dict] = []
for json_string in temp_set:
    data_obj = json.loads(json_string)
    new_rows.append(data_obj)

new_rows.sort(
    key=lambda x: (
        x["PDF Template Name"],
        x["PDF Template ID"],
        x["Organization Name"],
        x["Organization ID"],
    )
)


writer.writerows(new_rows)
