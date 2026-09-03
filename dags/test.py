
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


# 4. Creating a function to process EO BMF files for KS and MO
def transform_irs_eo_bmf():
    '''
    Action: This function transforms data specified in the eo_bmf_files directory, filters it by zip and return type, 
    and loads it into eo_bmf_files_edited directory.
    
    Description: The main purpose of the function is to traverse the directory where raw KS and MO EO BMF files reside to then, 
    combine and reshape data into a signle file and load it into another directory. 

    Important: Currently, the function only extract KS and MO files but later functionality can be added.
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

    # specifying zip codes to filter by: Downtown, Midtown, East, south, Swope, Northland, Wyandotte County, Overland Park, Olathe, Independence, Lee's Summit 
    zip_codes = ["64101", "64105", "64106", "64108", "64109", "64110", "64111", "64112", "64130", '64131', "64132", "64133", "64134",
                 "64136", "64137", "64138", "64150", "64151", '64152', "64153", "64154", "64155", "64156", "64157", "64158", "64161",
                 "64163", "64164", "64167", "66101", "66102", "66103", "66104", "66105", "66106", "66109", "66110", "66111", "66112",
                 "66115", "66117", "66118", "66119", "66160", "66204", "66207", "66210", "66212", "66213", "66221", "66223", "66224",
                 "66061", "66062", "64050", "64052", "64053", '64054', "64055", "64056", "64057", "64063", "64064", "64081", "64082", 
                 "64086"]


    # importing KS and MO EO BMF for further wrangling
    eo_ks = pandas.read_csv(filepath_or_buffer=os.path.join(IRS_EO_BMF_DIR, "ks_eo_bmf.csv"), usecols=column_names, dtype=data_types)
    print("Imported and reshaped original KS_EO_BMF.CSV data")

    eo_mo = pandas.read_csv(filepath_or_buffer=os.path.join(IRS_EO_BMF_DIR, "mo_eo_bmf.csv"), usecols=column_names, dtype=data_types)
    print("Imported and reshaped original MO_EO_BMF.CSV data")


    # combining KS and MO datasets
    df_eo_bmf = pandas.concat([eo_ks, eo_mo], ignore_index=True)
    print("Combined KS_EO_BMF.CSV and MO_EO_BMF.CSV into DF_EO_BMF.CSV")


    # filtering KS and MO combined data by needed zip codes
    df_eo_bmf["ZIP"] = df_eo_bmf["ZIP"].str.extract(r"(\d+)")
    df_eo_bmf = df_eo_bmf[df_eo_bmf["ZIP"].isin(zip_codes)]


    # saving data to the volume
    df_eo_bmf.to_csv(os.path.join(EDITED_IRS_EO_BMF_DIR, "df_eo_bmf.csv"), na_rep="NA", index=False)
    print(f"Saved file DF_EO_BMF.CSV to {EDITED_IRS_EO_BMF_DIR} directory")
    
    return df_eo_bmf

