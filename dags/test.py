
# importing libraries
import os
import shutil
import pandas
import os.path
import pathlib
import datetime
import zipfile_deflate64 as zipfile
from lxml import etree

# 0. Setting file variables
ROOT_DATA_DIR = "/home/kirill/Downloads/TestProjectData"

IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_EO_BMF_FILES")
EDITED_IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_EO_BMF_FILES")

IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_990_FILES")

EDITED_IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_990_FILES")
EDITED_IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_INDEX_FILES")


data = pandas.read_csv(f"{EDITED_IRS_INDEX_DIR}/df_index.csv")


# 6. This function cleans up IRS index data and creates XML_BATCH_ID refenrece
def process_irs_index(df_index):
    '''
    Action: This function takes IRS index files with filtered data, cleans it and separates it into two groups. First 
    group focuses on records with XML_BATCH_ID and second group focuses on records without XML_BATCH_ID. 
    '''

    # filtering only columns needed for further processing
    df_index = df_index[["EIN", "SUB_DATE", "RETURN_TYPE", "OBJECT_ID", "XML_BATCH_ID"]]

    # separating SUB_DATE into 4 digit date and complex string date for parsing
    df_index_dt_good = df_index[df_index["SUB_DATE"].str.contains(r"^\d{4}", na=False)].copy()
    df_index_dt_bad = df_index[~df_index["SUB_DATE"].str.contains(r"^\d{4}", na=False)].copy()

    # columns with string date need parsing and selecting 
    df_index_dt_bad["SUB_DATE"] = pandas.to_datetime(df_index_dt_bad["SUB_DATE"], format="%m/%d/%Y %I:%M:%S %p")
    df_index_dt_bad["SUB_DATE"] = df_index_dt_bad["SUB_DATE"].dt.year.astype(str)

    # combining two datasets together
    df_index = pandas.concat([df_index_dt_good, df_index_dt_bad])

    # separating data with known XML_BATCH_ID and without
    df_index_na = df_index[df_index["XML_BATCH_ID"].isna()]
    df_index_not_na = df_index[~df_index["XML_BATCH_ID"].isna()]


    return df_index_not_na, df_index_na

df_index_not_na, df_index_na = process_irs_index(data)

# 7. This function defines how to extract XML fields related to organization itself
def extract_org_fields(xml_root, xml_fields: dict, ns: dict):
    '''
    Action: This function defines how to extract XML fields related to organization itself and accepts names of these XML fields. 
    '''


    # defining a dict to collect records
    record_collector: dict = {}

    # iterating over fields and adding them to records
    for field_name, xpath_name in xml_fields.items():
        found_record = xml_root.xpath(xpath_name, namespaces=ns)
        if found_record:
            record_collector[field_name] = found_record[0]
        else:
            record_collector[field_name] = None


    return record_collector


# 8. This function defines how to extract XML fields related to officers
def extract_officer_fields(xml_root, officer_field, xml_fields: dict, ns: dict):
    '''
    Action: This function defines how to extract XML field related to officers and accept names of these XML fields.
    '''


    # defining a dict collect records and officer records
    officer_records: list = []

    # defining xpath to officer elements
    org_ein = xml_root.xpath("//irs:ReturnHeader/irs:Filer/irs:EIN", namespaces=ns)
    officer_elements = xml_root.xpath(officer_field, namespaces=ns)

    # iterating over officer fields
    for officer_element in officer_elements:

        # defining a record collector for each officer
        record_collector: dict = {}

        # adding org ein to each record
        if org_ein:
            record_collector["OrgEIN"] = org_ein[0]
        else:
            record_collector["OrgEIN"] = None

        # iterating over officer fields
        for field_name, xpath_name in xml_fields.items():
            found_record = officer_element.xpath(xpath_name, namespaces=ns)
            if found_record:
                record_collector[field_name] = found_record[0]
            else:
                record_collector[field_name] = None

        # adding to officer records list
        officer_records.append(record_collector)


    return officer_records





    




