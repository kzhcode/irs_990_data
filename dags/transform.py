
# importing libraries
import os
import os.path
import glob
import pathlib
import shutil
import pandas
from lxml import etree
import zipfile_deflate64 as zipfile
from xml_paths import NS, FIELD_990_ORG_XPATHS, FIELD_990EZ_ORG_XPATHS, FIELD_990PF_ORG_XPATHS, OFFICER_990_XPATHS, OFFICER_990EZ_XPATHS


# 0.0 Setting working directory paths
ROOT_DATA_DIR = "/opt/airflow/data"

IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_EO_BMF_FILES")
EDITED_IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_EO_BMF_FILES")

IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_INDEX_FILES")
EDITED_IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_INDEX_FILES")

IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_990_FILES")
EDITED_IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "EDITED_990_FILES")

EXTRACTED_XML_DATA = os.path.join(ROOT_DATA_DIR, "EXTRACTED_XML_DATA")


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
        print(f"Created {EDITED_IRS_990_DIR.upper()} directory")


    # Testing if extracted_xml_data folder exists
    if os.path.exists(EXTRACTED_XML_DATA):
        print(f"{EXTRACTED_XML_DATA.upper()} directory already exists")
    else:
        os.mkdir(EXTRACTED_XML_DATA)
        print(f"Created {EXTRACTED_XML_DATA.upper()} directory")


# 2. This function flattens a single extracted folder
def flatten_single_dir(target_dir: str):
    '''
    Action: If target_dir contains exactly one entry and that entry is a folder, moves that folder's contents up
    into target_dir and removes the empty nested folder.
    '''
 
    contents = list(os.scandir(target_dir))
 
    if len(contents) == 1 and contents[0].is_dir():
        nested_dir = contents[0]
        print(f"Nested folder detected in {target_dir.upper()}: {nested_dir.name.upper()}")
 
        for item in os.scandir(nested_dir.path):
            shutil.move(item.path, target_dir)
 
        os.rmdir(nested_dir.path)
        print(f"Flattened {target_dir.upper()}")


# 3. Creating a function to extract IRS 990 XML files from zipped files
def unzip_990_files():
    '''
    Action: Accessing compressed IRS 990 files at ORIGINAL_990_FILES directory and unzipping them into EDITED_990_FILES directory.
    
    Description: This function takes compressed IRS 990 files and extracts them into another directory. Originally, these XML files
    were going to be accessed directly within compressed files. However, there are issues with compression that IRS enforces on these
    files. Additionally, further exploration showed that compressed files have a compression type of 0, which isnt useful for processing.
 
    Extraction is incremental and safe to retry. Each archive is extracted and flattened inside a temporary ".tmp" folder, which is
    renamed to the final batch folder only after it is complete. Batches whose final folder already exists are skipped. Corrupt
    archives are logged, the remaining archives are still processed, and the function raises at the end so the failure is visible.
    '''
 
    failed_archives: list = []
 
    # traversing directory with zipped 990 files
    for i_member in os.scandir(IRS_990_DIR):
 
        # only processing complete zip files (ignores ".part" downloads and anything else)
        if not i_member.is_file() or not i_member.name.lower().endswith(".zip"):
            print(f"Skipping non-zip entry {i_member.name.upper()}")
            continue
 
        batch_name = pathlib.Path(i_member.name).stem
        final_dir = os.path.join(EDITED_IRS_990_DIR, batch_name)
        temp_dir = f"{final_dir}.tmp"
 
        # skipping batches that were fully extracted in an earlier run or attempt
        if os.path.isdir(final_dir):
            print(f"{batch_name.upper()} already extracted, skipping")
            continue
 
        # removing leftovers of a previously interrupted extraction
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Removed stale partial extraction {temp_dir.upper()}")
 
        # checking the archive is a readable zip before extracting
        if not zipfile.is_zipfile(i_member.path):
            print(f"{i_member.name.upper()} is not a valid zip file")
            failed_archives.append(i_member.name)
            continue
 
        try:
            print(f"Opened zipped file {i_member.name.upper()}")
            with zipfile.ZipFile(i_member.path, mode="r") as i_zip:
                i_zip.extractall(temp_dir)
 
            # flattening inside the temporary folder so the final folder is complete when it appears
            flatten_single_dir(temp_dir)
 
            # publishing the finished folder under its final name
            os.rename(temp_dir, final_dir)
            print(f"Extracted members out of zipped {i_member.name.upper()}")
 
        except (zipfile.BadZipFile, OSError) as err:
            print(f"Could not extract {i_member.name.upper()}: {err}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            failed_archives.append(i_member.name)
 
    if failed_archives:
        raise RuntimeError(f"Failed to extract {len(failed_archives)} archive(s): {failed_archives}")


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
                 "66211", "66212", "66213", "66221", "66223", "66224"]
 
 
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
    missing_batch_id = df_index["XML_BATCH_ID"].isna() | (df_index["XML_BATCH_ID"] == "NA")
 
    df_index_na = df_index[missing_batch_id]
    df_index_not_na = df_index[~missing_batch_id]
 
    df_index_na.to_csv(os.path.join(EDITED_IRS_INDEX_DIR, "df_index_na.csv"), na_rep="NA", index=False)
    df_index_not_na.to_csv(os.path.join(EDITED_IRS_INDEX_DIR, "df_index_not_na.csv"), na_rep="NA", index=False)
 
 
    return df_index_not_na, df_index_na


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
            record_collector[field_name] = found_record[0].text
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
    tax_yr = xml_root.xpath("//irs:ReturnHeader/irs:TaxYr", namespaces=ns)
    officer_elements = xml_root.xpath(officer_field, namespaces=ns)
 
    # iterating over officer fields
    for officer_element in officer_elements:
 
        # defining a record collector for each officer
        record_collector: dict = {}
 
        # adding org ein to each record
        if org_ein:
            record_collector["OrgEin"] = org_ein[0].text
            record_collector["TaxYr"] = tax_yr[0].text
        else:
            record_collector["OrgEin"] = None
            record_collector["TaxYr"] = None
 
        # iterating over officer fields
        for field_name, xpath_name in xml_fields.items():
            found_record = officer_element.xpath(xpath_name, namespaces=ns)
            if found_record:
                record_collector[field_name] = found_record[0].text
            else:
                record_collector[field_name] = None
 
        # adding to officer records list
        officer_records.append(record_collector)
 
    return officer_records


# 9. This function extract records from XML documents with a known XML_BATCH_ID
def extract_xml_rec_with_id(df_index_not_na: pandas.DataFrame, ns: dict):
    '''
    Action: This function takes a known XML_BATCH_ID, finds needed XML record and extracts data based on defined parameters.
    '''
 
    # list of recors
    org_records_with_id: list = []
    officer_records_with_id: list = []
 
    # grouping folders and accessing xml records
    for xml_batch_id, group in df_index_not_na.groupby("XML_BATCH_ID"):
 
        # creating a path to each XML folder
        batch_folder = os.path.join(EDITED_IRS_990_DIR, xml_batch_id)
 
        # iterating over over each record
        for i_row in group.itertuples():
 
            # extracting ein and object_id
            ein, object_id, return_type = i_row.EIN, i_row.OBJECT_ID, i_row.RETURN_TYPE
 
            # creating full XML file path
            file_path = os.path.join(batch_folder, f"{object_id}_public.xml")
 
            if os.path.exists(file_path):
                print(f"File {file_path} exists")
 
                # parsing XML with error capabilities
                try:
                    xml_data = etree.parse(file_path)
                    xml_root = xml_data.getroot()
 
                except (etree.XMLSyntaxError, OSError) as err:
                    print(f"Could not parse {file_path} for {ein}: {err}")
                    continue
 
                # establishing empty list for officer_record
                officer_record: list = []
                
                if return_type == "990":
                    record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990_ORG_XPATHS, ns=NS)
                    officer_field = "//irs:ReturnData/irs:IRS990/irs:Form990PartVIISectionAGrp"
                    officer_record = extract_officer_fields(xml_root=xml_root, officer_field=officer_field, xml_fields=OFFICER_990_XPATHS, ns=NS)
 
                elif return_type == "990EZ":
                    record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990EZ_ORG_XPATHS, ns=NS)
                    officer_field = "//irs:ReturnData/irs:IRS990EZ/irs:OfficerDirectorTrusteeEmplGrp"
                    officer_record = extract_officer_fields(xml_root=xml_root, officer_field=officer_field, xml_fields=OFFICER_990EZ_XPATHS, ns=NS)
 
                elif return_type == "990PF":
                    record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990PF_ORG_XPATHS, ns=NS)
                    # no paths for officers defined in 990PF organizations
 
                else:
                    print(f"Unknown or missing ReturnTypeCd for {ein} in {file_path}")
                    continue
 
                # creating records for orgs
                record["RefEin"] = ein
                record["ObjectId"] = object_id
                record["ReturnType"] = return_type
                org_records_with_id.append(record)
 
                # creating records for officers
                for i_officer in officer_record:
                    i_officer["OrgEin"] = ein
                    i_officer["ObjectId"] = object_id
                    officer_records_with_id.append(i_officer)
 
 
            else:
                print(f"File {file_path} does not exist")
 
    return org_records_with_id, officer_records_with_id


# 10. This function walks EDITED_IRS_990_DIR once and builds a lookup of OBJECT_ID to file path
def build_object_id_lookup():
    '''
    Action: This function walks every folder inside EDITED_IRS_990_DIR once and builds a dict mapping
    OBJECT_ID to its full file path, so rows can be located without relying on SUB_DATE or folder naming.
    '''
 
    object_id_lookup: dict = {}
 
    # walking every folder and subfolder inside EDITED_IRS_990_DIR
    for dirpath, dirnames, filenames in os.walk(EDITED_IRS_990_DIR):
        for filename in filenames:
 
            # only considering files matching the expected naming pattern
            if filename.endswith("_public.xml"):
                object_id = filename.removesuffix("_public.xml")
                full_path = os.path.join(dirpath, filename)
 
                if object_id in object_id_lookup:
                    print(f"Duplicate OBJECT_ID {object_id} found at {full_path}, keeping first match: {object_id_lookup[object_id]}")
                else:
                    object_id_lookup[object_id] = full_path
 
    print(f"Built lookup with {len(object_id_lookup)} files")
 
    return object_id_lookup


# 11. This function extracts records from XML documents with an unknown XML_BATCH_ID, using SUB_DATE to locate folders
def extract_xml_rec_without_id(df_index_na: pandas.DataFrame, object_id_lookup: dict):
    '''
    Action: This function takes rows lacking XML_BATCH_ID, locates each file via a prebuilt OBJECT_ID lookup,
    finds needed XML record and extracts data based on defined parameters.
    '''
 
    # list of records
    org_records_without_id: list = []
    officer_records_without_id: list = []
 
    # iterating over each row directly, no SUB_DATE grouping needed
    for i_row in df_index_na.itertuples():
 
        # extracting ein, object_id, and return_type
        ein, object_id, return_type = i_row.EIN, i_row.OBJECT_ID, i_row.RETURN_TYPE
 
        # looking up the file path directly by OBJECT_ID
        file_path = object_id_lookup.get(object_id)
 
        if file_path:
            print(f"File {file_path} exists")
 
            # parsing XML with error capabilities
            try:
                xml_data = etree.parse(file_path)
                xml_root = xml_data.getroot()
 
            except (etree.XMLSyntaxError, OSError) as err:
                print(f"Could not parse {file_path} for {ein}: {err}")
                continue
 
            # officer_record defaults to an empty list — 990PF has no officers
            officer_record = []
 
            if return_type == "990":
                record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990_ORG_XPATHS, ns=NS)
                officer_field = "//irs:ReturnData/irs:IRS990/irs:Form990PartVIISectionAGrp"
                officer_record = extract_officer_fields(xml_root=xml_root, officer_field=officer_field, xml_fields=OFFICER_990_XPATHS, ns=NS)
 
            elif return_type == "990EZ":
                record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990EZ_ORG_XPATHS, ns=NS)
                officer_field = "//irs:ReturnData/irs:IRS990EZ/irs:OfficerDirectorTrusteeEmplGrp"
                officer_record = extract_officer_fields(xml_root=xml_root, officer_field=officer_field, xml_fields=OFFICER_990EZ_XPATHS, ns=NS)
 
            elif return_type == "990PF":
                record = extract_org_fields(xml_root=xml_root, xml_fields=FIELD_990PF_ORG_XPATHS, ns=NS)
                # no officer XPaths defined for 990PF — officer_record stays an empty list
 
            else:
                print(f"Unknown or missing ReturnTypeCd for {ein} in {file_path}")
                continue
 
            # creating records for orgs
            record["RefEin"] = ein
            record["ObjectId"] = object_id
            record["ReturnType"] = return_type
            org_records_without_id.append(record)
 
            # creating records for officers — loop since officer_record can hold multiple people
            for single_officer in officer_record:
                single_officer["ObjectId"] = object_id
                officer_records_without_id.append(single_officer)
 
        else:
            print(f"No file found for OBJECT_ID {object_id}")
 
    return org_records_without_id, officer_records_without_id


# 12. Combine extracted data
def combine_extracted_data(org_records_with_id, officer_records_with_id, org_records_without_id, officer_records_without_id):
    '''
    Action: This function takes extracted org and officer records and combines them into their respective dataframes.
    '''
 
    # converting each list of dicts into a dataframe before concatenating
    org_records_with_id = pandas.DataFrame(org_records_with_id)
    officer_records_with_id = pandas.DataFrame(officer_records_with_id)
    org_records_without_id = pandas.DataFrame(org_records_without_id)
    officer_records_without_id = pandas.DataFrame(officer_records_without_id)
 
    # combining org and officer records, keeping all columns from both sources
    org_records = pandas.concat([org_records_with_id, org_records_without_id], axis=0, join="outer", ignore_index=True)
    officer_records = pandas.concat([officer_records_with_id, officer_records_without_id], axis=0, join="outer", ignore_index=True)
 
    org_records.to_csv(os.path.join(EXTRACTED_XML_DATA, "org_records.csv"), na_rep="NA", index=False)
    officer_records.to_csv(os.path.join(EXTRACTED_XML_DATA, "officer_records.csv"), na_rep="NA", index=False)
 
    return org_records, officer_records

# 13. This function removes the unzipped XML files folder once extraction is complete
def cleanup_edited_xml_dir():
    '''
    Action: This function deletes the EDITED_IRS_990_DIR folder and all its contents, since the underlying
    zipped files are retained separately and this folder can be regenerated by re-unzipping if needed.
    '''
 
    if os.path.exists(EDITED_IRS_990_DIR):
        try:
            shutil.rmtree(EDITED_IRS_990_DIR)
            print(f"Deleted folder: {EDITED_IRS_990_DIR.upper()}")
        except PermissionError as err:
            print(f"Could not fully delete {EDITED_IRS_990_DIR.upper()}: {err}")
            raise
    else:
        print(f"Folder {EDITED_IRS_990_DIR.upper()} does not exist, nothing to clean up")


if __name__ == "__main__":
    dir_setup_edited()
    unzip_990_files()
    df_eo_bmf = transform_irs_eo_bmf()
    df_index = transform_irs_index(df_eo_bmf)
    df_index_not_na, df_index_na = process_irs_index(df_index)
    object_id_lookup = build_object_id_lookup()
    org_records_with_id, officer_records_with_id = extract_xml_rec_with_id(df_index_not_na, NS)
    org_records_without_id, officer_records_without_id = extract_xml_rec_without_id(df_index_na, object_id_lookup)
    org_records, officer_records = combine_extracted_data(org_records_with_id, officer_records_with_id, org_records_without_id, officer_records_without_id)
    cleanup_edited_xml_dir()

