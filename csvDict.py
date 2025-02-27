import json
import ijson
from flatten_dict import flatten

'''
csv_dict = [
    'PDF_template_id': '52a5797f-c925-4d1e-86a8-b9f16aa58dba',
    'PDF_template_name': "CL_HRHC_BCBSVT",
    'orgTemplate': '"cambia"',
    'Org_Name_and id' : {
                      }
]
'''

# this is a list of templates as dicts
pdfTemplatesDev = []

# turn the template jsonl files into a list of dicts
with open("foundPDFs.jsonl", "r") as f:
    for line in f:
        data = json.loads(line)
        pdfTemplatesDev.append(data)
        # print(data)


# this is a list of only the template ids and name, as dicts 
list_of_csv_dicts = []

    
# iterate through the list and create new dicts with the template ids and names
for template in pdfTemplatesDev:
    new_dict = dict(
        PDF_template_id = template['id'],
        PDF_template_name = template['name']
    )
    list_of_csv_dicts.append(new_dict)


# this is a full list of all the orgs, as dicts 
orgsDEV = []

# turn the org jsonl file into a list of dicts, add then into orgsDev
# with open('new_json_files/example_org.jsonl', 'r') as f:
#     for line in f:
#         data = json.loads(line)
#         orgsDEV.append(data)

# Preview the data 
with open('orgs-dev.jsonl', 'r') as f:
    # parser = ijson.parse(f)
    # for prefix, data_type, value in parser:
    #     print(f'prefix_parent: {prefix}, data_type: {data_type}, value: {value}')
    for line in f:
        parser = ijson.items(line, 'report')
        for report in parser:
            print(report['report'])

# orgs_data = []

# for org in orgsDEV:
#     temp_org_dict ={}
#     if 'report' in org:
#         if 'orgTemplate' in org['report']:
#             print('orgTemplate' in org['report'])