
# importing libraries
import os
import pandas
import os.path


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
    #eo_ks["EIN"] = eo_ks["EIN"].str.replace("(..)(.+)", r"\1-\2", regex=True)
    #eo_mo["EIN"] = eo_mo["EIN"].str.replace("(..)(.+)", r"\1-\2", regex=True)

    # combining KS and MO datasets
    df_eo_bmf = pandas.concat([eo_ks, eo_mo], ignore_index=True)
    
    return df_eo_bmf


# 2. Creating a function to process IRS 990 index files
def transform_irs_index(data):
    '''This function extracts index data specified in the IRS Form 990 series download.

    The main purpose of the function is to iterate over 990 index files to match organizational EIN with
    OBJECT_ID that represents the name of an XML file. Finding the BATCH_ID per organization improves memory
    and prevents expensive operations opening and searching XML files. 
    '''

    # pulling a list of ks and mo ein organizations
    ks_ein_list = list(data[data["STATE"] == "KS"]["EIN"].array)
    mo_ein_list = list(data[data["STATE"] == "MO"]["EIN"].array)

    # defining column names to enforce df structure at the end of the func
    col_names = ["RETURN_ID", "FILING_TYPE", "EIN", "SUB_DATE", "TAXPAYER_NAME", "RETURN_TYPE", "OBJECT_ID", "XML_BATCH_ID"]

    # creating a list for ks and mo to store accumelated dfs
    ks_df_list = list()
    mo_df_list = list()

    # creating a path to index files inside the airflow container
    index_dir = os.path.join(TEMP_TEST_DIR, "index_files")

    # traversing directory with index files
    for i in os.listdir(index_dir):
        # reading each csv file in a dir as a df
        read_df = pandas.read_csv(os.path.join(index_dir, i), sep=",", usecols=col_names, dtype=str)

        # fileting dfs and add to the list of dfs
        ks_df_list.append(read_df[read_df["EIN"].isin(ks_ein_list)])
        mo_df_list.append(read_df[read_df["EIN"].isin(mo_ein_list)])

    # concating dfs
    df_index_ks = pandas.concat(ks_df_list, axis=0, join="inner", ignore_index=True)
    df_index_mo = pandas.concat(mo_df_list, axis=0, join="inner", ignore_index=True)

    return df_index_ks, df_index_mo

        


if __name__ == "__main__":
    df_eo_bmf = transform_irs_eo_bmf()
    df_index_ks, df_index_mo = transform_irs_index(data=df_eo_bmf)


