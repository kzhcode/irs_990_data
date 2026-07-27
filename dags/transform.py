
# importing libraries
import os
import pandas
import lxml


# 0. Setting file variables
TEMP_TEST_DIR = "/home/kirill/Downloads/" # temp link since working outside of Docker for now
DATA_DIR = "/opt/airflow/data"
IRS_EO_BMF = os.path.join(DATA_DIR, "eo_bmf_files")
IRS_INDEX = os.path.join(DATA_DIR, "index_files")
IRS_990 = os.path.join(DATA_DIR, "batch_files")


# 1. Creating a function to process EO BMF files for KS and MO
def transform_irs_eo_bmf():
    '''This function extracts organization data specified in the IRS EO BMF.
    
    The main purpose of the function is to traverse the directory where EO BMF files live to
    then extract and reshape organizational data that will later be loaded into the database.

    IMPORTANT: Currently, the function only extract KS and MO files but later functionality can be added.
    
    Column names being extracted from EO BMF are:

    EIN, NAME, STREET, CITY, STATE, ZIP, GROUP, SUBSECTION, AFFILIATION,
    CLASSIFICATION, RULING, DEDUCTIBILITY, FOUNDATION, ACTIVITY, ORGANIZATION,
    STATUS, ASSET_CD, INCOME_CD, FILING_REQ_CD, PF_FILING_REQ_CD, ACCT_PD, NTEE_CD
    '''


    # reducing datasets only to needed columns for later database import
    column_names = ["EIN", "NAME", "STREET", "CITY", "STATE", "ZIP", "GROUP", "SUBSECTION", "AFFILIATION",
        "CLASSIFICATION", "RULING", "DEDUCTIBILITY", "FOUNDATION", "ACTIVITY", "ORGANIZATION", "STATUS", 
        "ASSET_CD", "INCOME_CD", "FILING_REQ_CD", "PF_FILING_REQ_CD", "ACCT_PD", "NTEE_CD"]

    # creating a dict to have more control over assigning data types when importg KS and MO EO BMF data
    data_types = {"EIN": str, "NAME": str, "STREET": str, "CITY": str, "STATE": str, "ZIP": str, "GROUP": str,
                  "SUBSECTION": str, "AFFILIATION": int, "CLASSIFICATION": str, "RULING": str, "DEDUCTIBILITY": int,
                  "FOUNDATION": int, "ACTIVITY": str, "ORGANIZATION": int, "STATUS": str, "ASSET_CD": int, "INCOME_CD": int,
                  "FILING_REQ_CD": str, "PF_FILING_REQ_CD": int, "ACCT_PD": str, "NTEE_CD": str}

    # importing KS and MO EO BMF for further wrangling
    eo_ks = pandas.read_csv(filepath_or_buffer=os.path.join(TEMP_TEST_DIR, "eo_ks.csv"), usecols=column_names, dtype=data_types)
    eo_mo = pandas.read_csv(filepath_or_buffer=os.path.join(TEMP_TEST_DIR, "eo_mo.csv"), usecols=column_names, dtype=data_types)

    # changing ein format to use XX-XXXXXXX format
    eo_ks["EIN"] = eo_ks["EIN"].str.replace("(..)(.+)", r"\1-\2", regex=True)
    eo_mo["EIN"] = eo_mo["EIN"].str.replace("(..)(.+)", r"\1-\2", regex=True)

    # combining KS and MO datasets
    df = pandas.concat([eo_ks, eo_mo], ignore_index=True)
    
    return df


