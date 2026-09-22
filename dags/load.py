
# importing libraries
import os
import os.path
import pandas
from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import insert


# 0.0 Setting working directory paths
ROOT_DATA_DIR = "/opt/airflow/data"
#ROOT_DATA_DIR = "/home/kirill/Downloads/TestProjectData"
EXTRACTED_XML_DATA = os.path.join(ROOT_DATA_DIR, "EXTRACTED_XML_DATA")

# 0.1 Importing variables from dotenv
load_dotenv()
pg_user = os.getenv("POSTGRES_USER")
pg_pass = os.getenv("POSTGRES_PASSWORD")
pg_db = os.getenv("POSTGRES_DB")
pg_port = os.getenv("POSTGRES_PORT")

# 0.2 Loading data
org_records = pandas.read_csv(os.path.join(EXTRACTED_XML_DATA, "org_records.csv"))
officer_records = pandas.read_csv(os.path.join(EXTRACTED_XML_DATA, "officer_records.csv"))

# 0.3 Setting column names
org_col_ls: list = ["OrgEin", "TaxYr", "OrgBusinessName", "OrgStreet", "OrgCity", "OrgState", "OrgZip", "OrgWebsite", "OrgFormationYr", "OrgMissionDisc", 
                    "OrgPhoneNumber", "isUpdated", "UpdateDate", "UpdateBy"]

officer_col_ls: list = ["OrgEin", "ObjectId", "ReturnType", "TaxYr", "OfficerFirstName", "OfficerLastName", "OfficerTitle", "OfficerAvgHrsPerWeekRt",
                        "OfficerAvgHrsPerWkDevotedToPosRt", "OfficerAvgHrsPerWeekRltdOrgRt", "OfficerCompAmt", "OfficerReportCompFromOrgAmt",
                        "OfficerReportCompFromRltdOrgAmt", "OfficerOtherCompAmt", "OfficerEmplBenefitProgAmt", "OfficerExpnsAccntOtherAllwncAmt",
                        "isUpdated", "UpdateDate", "UpdateBy"]

ret_990_col_ls: list = ["OrgEin", "ObjectId", "ReturnDate", "ReturnType", "TaxYr", "TotalEmployeeCnt", "GrossReceiptsAmt", "TotalGrossUBIAmt", 
                        "ContribGrantsAmt", "ProgramServiceRevAmt", "InvestIncomeAmt", "OtherRevAmt", "TotalRevAmt", "GrantsAndSimilarPaidAmt", 
                        "BenefitsPaidToMembersAmt", "SalariesCompEmpBnftPaidAmt", "TotalProfFndrsngExpnsAmt", "TotalFndrsngExpnsAmt", "OtherExpnsAmt", 
                        "TotalExpnsAmt", "RevLessExpnsAmt", "TotalAssetsBOYAmt", "TotalAssetsEOYAmt", "TotalLiabilitiesBOYAmt", "TotalLiabilitiesEOYAmt", 
                        "NetAssetsOrFundBalancesBOYAmt", "NetAssetsOrFundBalancesEOYAmt", "ExpnsAmt", "GrantAmt", "RevAmt", "TotalOtherProgSrvcExpnsAmt", 
                        "TotalOtherProgSrvcGrantAmt", "TotalOtherProgSrvcRevAmt", "TotalProgramSrvcExpnsAmt", "TotalReportableCompFromOrgAmt", 
                        "TotalReportableCompRltdOrgAmt", "TotalOtherCompAmt", "FederatedCampaignsAmt", "MembershipDuesAmt", "FundraisingAmt", 
                        "RelatedOrgAmt", "GovGrantsAmt", "AllOtherContrAmt", "NonCashContrAmt", "TotalContrAmt", "isUpdated", "UpdateDate", "UpdateBy"]

ret_990ez_col_ls: list = ["OrgEin", "ObjectId", "ReturnDate", "ReturnType", "TaxYr", "GrossReceiptsAmt", "ContrGiftsGrantsEtcAmt", "ProgSrvcRevenueAmt", 
                          "MembershipDuesAmt", "TotalRevenueAmt", "FeesAndOtherPymtToIndCntrctAmt", "OtherExpnsTotalAmt", "TotalExpnsAmt", 
                          "ExcessOrDeficitForYearAmt", "NetAssetsOrFundBalancesBOYAmt", "OtherChangesInNetAssetsAmt", "NetAssetsOrFundBalancesEOYAmt", 
                          "CashSavingsAndInvestmentsBOYAmt", "CashSavingsAndInvestmentsEOYAmt", "OtherAssetsTotalDetailBOYAmt", 
                          "OtherAssetsTotalDetailEOYAmt", "Form990TotalAssetsBOYAmt", "Form990TotalAssetsEOYAmt", "SumOfTotalLiabilitiesBOYAmt", 
                          "SumOfTotalLiabilitiesEOYAmt", "NetAssetsOrFundBalancesGrpBOYAmt", "NetAssetsOrFundBalancesGrpEOYAmt", 
                          "TotalProgSrvcExpensesAmt", "isUpdated", "UpdateDate", "UpdateBy"]

ret_990pf_col_ls: list = ["OrgEin", "ObjectId", "ReturnDate", "ReturnType", "TaxYr", "FMVAssetsEOYAmt", "MethodOfAccountingCashInd", 
                          "ContriRcvdRevAndExpnssAmt", "InterestOnSavRevAndExpnssAmt", "InterestOnSavNetInvstIncmAmt", "InterestOnSavingsAdjNetIncmAmt", 
                          "DividendsRevAndExpnssAmt", "DividendsNetInvstIncmAmt", "DividendsAdjNetIncmAmt", "GrossRentsRevAndExpnssAmt", 
                          "GrossRentsNetInvstIncmAmt", "GrossRentsAdjNetIncmAmt", "NetRentalIncomeOrLossAmt", "GrossSalesPriceAmt", 
                          "CapGainNetIncmNetInvstIncmAmt", "IncmModificationsAdjNetIncmAmt", "GrossSalesLessRetAndAllwncAmt", "CostOfGoodsSoldAmt", 
                          "GrossProfitAdjNetIncmAmt", "OtherIncomeNetInvstIncmAmt", "OtherIncomeAdjNetIncmAmt", "TotalRevAndExpnssAmt", 
                          "TotalNetInvstIncmAmt", "TotalAdjNetIncmAmt", "isUpdated", "UpdateDate", "UpdateBy"]


# 1.1 This function cleans cellphone data
def clean_phone(x):
    '''
    Action: This function cleans org phone number to prevent errors when loading to Postgres.
    '''
    if pandas.notna(x):
        digits = str(int(x))
        if len(digits) == 10:
            return digits
    return None


# 1.2 This function splits organization data and prepares it for loading
def prepare_org_records(org_records: pandas.DataFrame):
    '''
    Action: This function takes extracted XML 990 organizational data and prepares it for Postgres loading. 
    '''

    # adding needed columns for tracking changes
    org_records["isUpdated"] = False
    org_records["UpdateDate"] = None
    org_records["UpdateBy"] = None

    # formatting columns
    org_records["OrgBusinessName"] = org_records["OrgBusinessName"].str.title()
    org_records["OrgStreet"] = org_records["OrgStreet"].str.title()
    org_records["OrgCity"] = org_records["OrgCity"].str.title()
    org_records["OrgZip"] = org_records["OrgZip"].astype(str).str.extract(r"(\d{5})")
    org_records["OrgWebsite"] = org_records["OrgWebsite"].replace(["NaN", "nan", "NA"], None)
    org_records["OrgWebsite"] = org_records["OrgWebsite"].str.lower()
    org_records["OrgMissionDisc"] = org_records["OrgMissionDisc"].str.capitalize()


    # converting column types
    org_records["OrgEin"] = org_records["OrgEin"].astype(str).str.zfill(9)

    org_records["OrgPhoneNumber"] = pandas.Series(
        [clean_phone(x) for x in org_records["OrgPhoneNumber"]],
        index=org_records.index,
        dtype=object
    )
    
    org_records["OrgFormationYr"] = pandas.Series(
        [int(x) if pandas.notna(x) else None for x in org_records["OrgFormationYr"]],
        index=org_records.index,
        dtype=object
    )


    # splitting datasets
    tb_990_return = org_records[org_records["ReturnType"] == "990"]
    tb_990ez_return = org_records[org_records["ReturnType"] == "990EZ"]
    tb_990pf_return = org_records[org_records["ReturnType"] == "990PF"]

    # filtering columns
    tb_organization = org_records.filter(items=org_col_ls)
    tb_990_return = tb_990_return.filter(items=ret_990_col_ls)
    tb_990ez_return = tb_990ez_return.filter(items=ret_990ez_col_ls)
    tb_990pf_return = tb_990pf_return.filter(items=ret_990pf_col_ls)

    # deduping tb_organizations
    tb_organization = tb_organization.sort_values(by=["TaxYr", "OrgEin"], ascending=False)
    tb_organization = tb_organization.drop(["TaxYr"], axis=1)
    tb_organization = tb_organization.drop_duplicates(subset=["OrgEin"], keep="first")

    return tb_organization, tb_990_return, tb_990ez_return, tb_990pf_return


# 2. This function formats officer salary data and prepares it for loading
def prepare_officer_records(officer_records: pandas.DataFrame, org_records: pandas.DataFrame):
    '''
    Action: This function takes officer salary records and formats it to load into Postgres.
    '''

    # pulling return type by objectid
    ret_type_df = org_records[["ObjectId", "ReturnType"]]
    officer_records = officer_records.merge(ret_type_df, on="ObjectId", how="left")

    # converting ein
    officer_records["OrgEin"] = officer_records["OrgEin"].astype(str).str.zfill(9)

    # formatting columns
    officer_records["OfficerName"] = officer_records["OfficerName"].str.title()
    officer_records["OfficerTitle"] = officer_records["OfficerTitle"].str.title()

    # splitting officer names into first and last names
    name_parts = officer_records["OfficerName"].str.extract(r"^(?:(?:Dr|Mrs|Mr|Ms)\.?\s+)?(\S+)\s+(?:.*\s+)?(\S+)$")
    officer_records["OfficerFirstName"] = name_parts[0]
    officer_records["OfficerLastName"] = name_parts[1]
    missing_name_mask = officer_records["OfficerFirstName"].isna() | officer_records["OfficerLastName"].isna()
    if missing_name_mask.any():
        print(f"Dropping {missing_name_mask.sum()} officer record(s) with missing OfficerName within this load batch")
        officer_records = officer_records[~missing_name_mask]

    # deduplicating officer records
    pk_subset = ["OrgEin", "ObjectId", "OfficerFirstName", "OfficerLastName", "TaxYr"]
    dupe_mask = officer_records.duplicated(subset=pk_subset, keep="first")
    if dupe_mask.any():
        print(f"Dropping {dupe_mask.sum()} duplicated officer record(s) within this load batch")
        officer_records = officer_records[~dupe_mask]

    # filling postgresql columns
    officer_records["isUpdated"] = False
    officer_records["UpdateDate"] = None
    officer_records["UpdateBy"] = None

    officer_records = officer_records.filter(items=officer_col_ls)

    return officer_records


# 3. This function sets up database connection
def psql_engine(dialect: str, driver: str, username: str, password: str, host: str, port: str, database: str):
    '''
    Action: This function connects to PostgreSQL database using SQLAlchemy Core v. 1.4.
    '''

    tb_engine = create_engine(f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}", future=True)
    tb_metadata = MetaData()

    return tb_engine, tb_metadata


# 4. This function upserts information into the database
def update_data_psql(tb_engine, tb_metadata, tb_name:str, tb_data: pandas.DataFrame, updtr_name: str):
    '''
    Action: This function takes processed data and inserts it into the database.
    '''


    tracking_cols = ["isUpdated", "UpdateDate", "UpdateBy"]

    # using defined engine to connect to the database
    with tb_engine.connect() as connection:
        # pulling together the connection
        inspctr = inspect(connection)

        # establishing table name recognition
        if tb_name not in inspctr.get_table_names():
            print(f"{tb_name.upper()} does not exist in the database")
            return

        # accessing specified table
        tb_info = Table(tb_name, tb_metadata, autoload_with=connection)

        # pulling pks from the table
        pk_cols = [col.name for col in tb_info.primary_key.columns]

        # convert all NaN/NaT to None
        tb_data = tb_data.astype(object).where(pandas.notnull(tb_data), None)

        # converting DataFrame into a list of row-dicts for execution
        records = tb_data.to_dict(orient='records')

        if not records:
            print(f"No rows to load for {tb_name.upper()}")
            return

        # columns to overwrite on conflict
        update_cols = [
            col.name for col in tb_info.columns
            if col.name not in pk_cols 
            and col.name not in tracking_cols
            and col.computed is None
        ]

        # creating a statement
        stmnt = insert(tb_info).values(records)

        # on conflict
        set_clause = {col_name: stmnt.excluded[col_name] for col_name in update_cols}
        set_clause.update({
            "isUpdated": True,
            "UpdateDate": func.now(),
            "UpdateBy": updtr_name,
        })

        stmnt =stmnt.on_conflict_do_update(
            index_elements=pk_cols,
            set_=set_clause
        )

        connection.execute(stmnt)
        connection.commit()
        print(f"Upserted {len(records)} rows into {tb_name.upper()}")


if __name__ == "__main__":
    tb_organization, tb_990_return, tb_990ez_return, tb_990pf_return = prepare_org_records(org_records)
    tb_officer_salary = prepare_officer_records(officer_records, org_records)
    tb_engine, tb_metadata = psql_engine("postgresql", "psycopg2", pg_user, pg_pass, "postgres", pg_port, pg_db)

    update_data_psql(tb_engine, tb_metadata, "tb_organization", tb_organization, "KMZ")
    update_data_psql(tb_engine, tb_metadata, "tb_990_return", tb_990_return, "KMZ")
    update_data_psql(tb_engine, tb_metadata, "tb_990ez_return", tb_990ez_return, "KMZ")
    update_data_psql(tb_engine, tb_metadata, "tb_990pf_return", tb_990pf_return, "KMZ")
    update_data_psql(tb_engine, tb_metadata, "tb_officer_salary", tb_officer_salary, "KMZ")


