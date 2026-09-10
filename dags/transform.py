
# importing libraries
import os
import pandas
import os.path
import shutil
import datetime
import zipfile_deflate64 as zipfile


# 0.0 Setting working directory paths
ROOT_DATA_DIR = "/opt/airflow/data"

IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_EO_BMF_FILES")
EDITED_IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_EO_BMF_FILES")

IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_INDEX_FILES")
EDITED_IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_INDEX_FILES")

IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_990_FILES")
EDITED_IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_990_FILES")


# 1. Function to set up directories in a volume 
def dir_setup_edited():
    '''
    Set up directories for edited and tranformed files. Although it is not really necessary, Brent Never requested
    that transformed files will be saved for later extraction since there will be a need for additional analysis. 
    '''   


    # Testing if edited_eo_bmf_files folder exists
    if os.path.exists(EDITED_IRS_EO_BMF_DIR):
        print(f"{EDITED_IRS_EO_BMF_DIR.upper()} directory already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(EDITED_IRS_EO_BMF_DIR)
        print(f"Created {EDITED_IRS_EO_BMF_DIR.upper()} directory")


    # Testing if edited_index_files folder exists
    if os.path.exists(EDITED_IRS_INDEX_DIR):
        print(f"{EDITED_IRS_INDEX_DIR.upper()} directory already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(EDITED_IRS_INDEX_DIR)
        print(f"Created {EDITED_IRS_INDEX_DIR.upper()} directory")


    # Testing if edited_990_files folder exists
    if os.path.exists(EDITED_IRS_990_DIR):
        print(f"{EDITED_IRS_990_DIR.upper()} directory already exists")
    else:
        os.mkdir(EDITED_IRS_990_DIR)
        print(f"Created {EDITED_IRS_990_DIR} directory")


# 2. Creating a function to extract IRS 990 XML files from zipped files
def unzip_990_files():
    '''
    Action: Accessing compressed IRS 990 files at ORIGINAL_990_FILES directory and unzipping them into EDITED_990_FILES directory.
    
    Description: This function takes compressed IRS 990 files and extracts them into another directory. Originally, these XML files
    were going to be accessed directly within compressed files. However, there are issues with compression that IRS enforces on these
    files. Additionally, further exploration showed that compressed files have a compression type of 0, which isnt useful for processing.
    '''

    # traversing directory with zipped 990 files
    for i_member in os.scandir(IRS_990_DIR):
        print(f"Opened zipped file {i_member.name.upper()}")

        # per each zip file in a folder creating ZipFile object
        i_zip = zipfile.ZipFile(i_member, mode="r")

        # creating a zip file Path object
        i_zip_path = zipfile.Path(i_member)

        # extracting all members
        i_zip.extractall(os.path.join(EDITED_IRS_990_DIR, i_zip_path.stem))
        print(f"Extracted members out of zipped {i_member.name.upper()}")


# 3. Creating a function to flatten extracted IRS files
def flatten_nested_990_files():
    '''
    Action: Access extracted IRS 990 files and flatten them within their respective folders.

    Description: This functions flattens extracted IRS 990 files. This is needed because IRS sometimes nests compressed files. To prevent this
    from happening after extraction, this function steps in. 
    '''

    # traversing each extracted folder (one per original zip file)
    for i_extracted in os.scandir(EDITED_IRS_990_DIR):

        if not i_extracted.is_dir():
            continue

        # list what's directly inside this extracted folder
        contents = list(os.scandir(i_extracted.path))

        # nested case: exactly one entry, and it's a directory
        if len(contents) == 1 and contents[0].is_dir():
            nested_dir = contents[0]
            print(f"Nested folder detected in {i_extracted.name.upper()}: {nested_dir.name.upper()}")

            # move every item out of the nested folder, up into the parent
            for item in os.scandir(nested_dir.path):
                shutil.move(item.path, i_extracted.path)

            # remove the now-empty nested folder
            os.rmdir(nested_dir.path)
            print(f"Flattened {i_extracted.name}")

        else:
            print(f"No nesting detected in {i_extracted.name.upper()}")


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
    zip_codes = ["64050", "64051", "64052", "64053", "64054", "64055", "64056", "64057", "64058", "64059", "64060", "64061", "64062", "64063", "64064",
                 "64080", "64081", "64082", "64083", "64084", "64085", "64086",
                 "64101", "64102", "64103", "64104", "64105", "64106", "64107", "64108", "64109", "64110", "64111", "64112", "64113", "64114", "64115",
                 "64116", "64117", "64118", "64119", "64120", "64121", "64122", "64123", "64124", "64125", "64126", "64127", "64128", "64129", "64130",
                 "64131", "64132", "64133", "64134", "64135", "64136", "64137", "64138", "64139", "64140", "64141", "64142", "64143", "64144", "64145",
                 "64146", "64147", "64148", "64149", "64150", "64151", '64152', "64153", "64154", "64155", "64156", "64157", "64158", "64159", "64160",
                 "64161", "64162", "64163", "64164", "64165", "64166", "64167", "64168", "64169", "64170", "64171", "64172", "64173", "64174", "64175",
                 "64176", "64177", "64178", "64179", "64180", "64181", "64182", "64183", "64184", "64185", "64186", "64187", "64188", "64189", "64190",
                 "64191", "64192", "64193", "64194", "64195", "64196", "64197", "64198", "64199",
                 "66061", "66062", "66101", "66102", "66103", "66104", "66105", "66106", "66107", "66108", "66109", "66110", "66111", "66112", "66113",
                 "66115", "66117", "66118", "66119", "66160", "66200", "66201", "66202", "66203", "66204", "66206", "66207", "66208", "66209", "66210",
                 "66211", "66212", "66213", "66221", "66223", "66224"
                 ]


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


# 5. Creating a function to process IRS 990 index files
def transform_irs_index(df_eo_bmf):
    '''
    Action: This function takes the combined EO BMF data for KS and MO, extracts their EINs, and then filters files 
    within the index_files directory to include data only on needed EINs. 

    Description: The main purpose of the function is to iterate over the IRS 990 index files, match KS/MO selected EINs within 
    these files and create a DataFrame that references each EIN's location and unique number within the IRS 990 Index files. 

    This is a crucial step because the IRS 990 Index files are compressed. To extract XML data from compressed files, references 
    between EIN's, XML_BATCH_ID, and OBJECT_ID need to be established, which this function accomplishes.
    '''


    # pulling a list of ks and mo ein organizations
    ein_list = list(df_eo_bmf["EIN"].array)
    print("Extracted list of EINs from DF_EO_BMF.CSV")

    # defining column names to enforce df structure at the end of the func
    col_names = ["RETURN_ID", "FILING_TYPE", "EIN", "SUB_DATE", "TAXPAYER_NAME", "RETURN_TYPE", "OBJECT_ID", "XML_BATCH_ID"]

    # defining return type to filter by
    return_types = ["990", "990EZ", "990PF"]

    # creating a list for ks and mo to store accumelated dfs
    df_list = list()


    # traversing directory with index files
    for i in os.listdir(IRS_INDEX_DIR):
        # reading each csv file in a dir as a df
        read_df = pandas.read_csv(os.path.join(IRS_INDEX_DIR, i), sep=",", dtype=str)
        print(f"Opened file named: {i.upper()}")

        # not all columns across years are the same so they need to be adjusted
        print(f"Examining columns structure of the file: {i.upper()}")
        for col in col_names:
            if col not in read_df.columns:
                read_df[col] = "NA"
                print(f"File named: {i.upper()} was missing a column named: {col.upper()}")
   
        print(f"Column structure of file named: {i.upper()} is good")
                

        # fileting dfs and add to the list of dfs
        df_list.append(read_df[read_df["EIN"].isin(ein_list)])
        print(f"Filtering data to only specified EINs")
        

    # concating dfs from a list of dfs
    df_index = pandas.concat(df_list, axis=0, join="inner", ignore_index=True)

    # filtering combined df by return type needed
    df_index = df_index[df_index["RETURN_TYPE"].isin(return_types)]

    df_index.to_csv(os.path.join(EDITED_IRS_INDEX_DIR, "df_index.csv"), na_rep="NA", index=False)
    print("Saving filtered and combined master data file named DF_INDEX.CSV")

    # splitting data into return types since different return types will require different db schema
    uniq_return_type = df_index["RETURN_TYPE"].unique()

    for ret_type in uniq_return_type:
        filtered_df_index = df_index[df_index["RETURN_TYPE"] == ret_type]
        filtered_df_index.to_csv(os.path.join(EDITED_IRS_INDEX_DIR, f"df_index_{ret_type}.csv"), na_rep="NA", index=False)
        print(f"Saving {str(ret_type).upper()} as a separate file named DF_INDEX_{str(ret_type).upper()}.CSV")

    return df_index


if __name__ == "__main__":
    dir_setup_edited()
    unzip_990_files()
    flatten_nested_990_files()
    data_1 = transform_irs_eo_bmf()
    data_2 = transform_irs_index(data_1)


