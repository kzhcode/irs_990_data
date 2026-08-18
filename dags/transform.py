
# importing libraries
import os
import pandas
import os.path


# 0. Setting file variables
TEMP_TEST_DIR = "/home/kirill/Downloads/" # temp link since working outside of Docker for now
DATA_DIR = "/opt/airflow/data"

IRS_EO_BMF = os.path.join(DATA_DIR, "eo_bmf_files")
IRS_EO_BMF_EDITED = os.path.join(DATA_DIR, "eo_bmf_files_edited")

IRS_INDEX = os.path.join(DATA_DIR, "index_files")
IRS_INDEX_EDITED = os.path.join(DATA_DIR, "index_files_edited")

IRS_990 = os.path.join(DATA_DIR, "batch_files")


# 1. Function to set up directories in a volume 
def dir_setup_edited():
    '''
    Set up directories for edited and tranformed files. Although it is not really necessary, Brent Never requested
    that transformed files will be saved for later extraction since there will be a need for additional analysis. 
    '''   


    # Testing if eo_bmf_files_edited folder exists
    if os.path.exists(os.path.join(DATA_DIR, "eo_bmf_files_edited")):
        print("The eo_bmf_files_edited folder already exists, moving forward")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(os.path.join(DATA_DIR, "eo_bmf_files_edited"))
        print("Created the eo_bmf_files_edited folder")


    # Testing if index_files_edited folder exists
    if os.path.exists(os.path.join(DATA_DIR, "index_files_edited")):
        print("The index_files_edited folder already exists, moving forward")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(os.path.join(DATA_DIR, "index_files_edited"))
        print("Created the index_files_edited folder")


# 2. Creating a function to process EO BMF files for KS and MO
def transform_irs_eo_bmf():
    '''
    This function extracts organization data specified in the IRS EO BMF.
    
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
    eo_ks = pandas.read_csv(filepath_or_buffer=os.path.join(IRS_EO_BMF, "ks_eo_bmf.csv"), usecols=column_names, dtype=data_types)
    eo_mo = pandas.read_csv(filepath_or_buffer=os.path.join(IRS_EO_BMF, "mo_eo_bmf.csv"), usecols=column_names, dtype=data_types)


    # combining KS and MO datasets
    df_eo_bmf = pandas.concat([eo_ks, eo_mo], ignore_index=True)
    df_eo_bmf.to_csv(os.path.join(IRS_EO_BMF_EDITED, "df_eo_bmf.csv"), na_rep="NA", index=False)

    
    return df_eo_bmf


# 3. Creating a function to process IRS 990 index files
def transform_irs_index(eo_bmf_data):
    '''
    This function extracts index data specified in the IRS Form 990 series download.

    The main purpose of the function is to iterate over 990 index files to match organizational EIN with
    OBJECT_ID that represents the name of an XML file. Finding the BATCH_ID per organization improves memory
    and prevents expensive operations opening and searching XML files. 
    '''


    # pulling a list of ks and mo ein organizations
    ein_list = list(eo_bmf_data["EIN"].array)

    # defining column names to enforce df structure at the end of the func
    col_names = ["RETURN_ID", "FILING_TYPE", "EIN", "SUB_DATE", "TAXPAYER_NAME", "RETURN_TYPE", "OBJECT_ID", "XML_BATCH_ID"]

    # creating a list for ks and mo to store accumelated dfs
    df_list = list()


    # traversing directory with index files
    for i in os.listdir(IRS_INDEX):
        # reading each csv file in a dir as a df
        read_df = pandas.read_csv(os.path.join(IRS_INDEX, i), sep=",", dtype=str)


        # not all columns across years are the same so they need to be adjusted
        for col in col_names:
            if col not in read_df.columns:
                read_df[col] = "NA"


        # fileting dfs and add to the list of dfs
        df_list.append(read_df[read_df["EIN"].isin(ein_list)])
        

    # concating dfs
    df_index = pandas.concat(df_list, axis=0, join="inner", ignore_index=True)
    df_index.to_csv(os.path.join(IRS_INDEX_EDITED, "df_index.csv"), na_rep="NA", index=False)

    # splitting data into return types since different return types will require different db schema
    uniq_return_type = df_index["RETURN_TYPE"].unique()

    for ret_type in uniq_return_type:
        filtered_df_index = df_index[df_index["RETURN_TYPE"] == ret_type]
        filtered_df_index.to_csv(os.path.join(IRS_INDEX_EDITED, f"df_index_{ret_type}.csv"), na_rep="NA", index=False)


if __name__ == "__main__":
    dir_setup_edited()
    df_eo_bmf = transform_irs_eo_bmf()
    transform_irs_index(eo_bmf_data=df_eo_bmf)


