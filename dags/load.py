
# importing libraries
import os
import os.path
import pandas
import sqlalchemy
from dotenv import load_dotenv


# 0.0 Setting working directory paths
#ROOT_DATA_DIR = "/opt/airflow/data"
ROOT_DATA_DIR = "/home/kirill/Downloads/TestProjectData"
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

officer_col_ls: list = ["OrgEin", "ReturnType", "TaxYr", "OfficerFirstName", "OfficerLastName", "OfficerTitle", "OfficerAvgHrsPerWeekRt",
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


# 1. This function splits organization data and prepares it for loading
def prepare_org_records(org_records: pandas.DataFrame):
    '''
    Action: This function takes extracted XML 990 organizational data and prepares it for Postgres loading. 
    '''

    # adding needed columns for tracking changes
    org_records["isUpdated"] = False
    org_records["UpdateDate"] = pandas.NaT
    org_records["UpdateBy"] = pandas.NA

    # formatting columns
    org_records["OrgBusinessName"] = org_records["OrgBusinessName"].str.title()
    org_records["OrgStreet"] = org_records["OrgStreet"].str.title()
    org_records["OrgCity"] = org_records["OrgCity"].str.title()
    org_records["OrgZip"] = org_records["OrgZip"].astype(str).str.extract(r"(\d{5})")
    org_records["OrgWebsite"] = org_records["OrgWebsite"].str.lower()
    org_records["OrgMissionDisc"] = org_records["OrgMissionDisc"].str.capitalize()

    # splitting datasets
    tb_990_return = org_records[org_records["ReturnType"] == "990"]
    tb_990EZ_return = org_records[org_records["ReturnType"] == "990EZ"]
    tb_990PF_return = org_records[org_records["ReturnType"] == "990PF"]

    # filtering columns
    tb_organization = org_records.filter(items=org_col_ls)
    tb_990_return = tb_990_return.filter(items=ret_990_col_ls)
    tb_990EZ_return = tb_990EZ_return.filter(items=ret_990ez_col_ls)
    tb_990PF_return = tb_990PF_return.filter(items=ret_990pf_col_ls)

    # deduping tb_organizations
    tb_organization = tb_organization.sort_values(by=["TaxYr", "OrgEin"], ascending=False)
    tb_organization = tb_organization.drop(["TaxYr"], axis=1)
    tb_organization = tb_organization.drop_duplicates(subset=["OrgEin"], keep="first")

    return tb_organization, tb_990_return, tb_990EZ_return, tb_990PF_return


# 2. This function formats officer salary data and prepares it for loading
def prepare_officer_records(officer_records: pandas.DataFrame, org_records: pandas.DataFrame):
    '''
    Action: This function takes officer salary records and formats it to load into Postgres.
    '''

    # pulling return type by objectid
    ret_type_df = org_records[["ObjectId", "ReturnType"]]
    officer_records = officer_records.merge(ret_type_df, on="ObjectId", how="left")

    # formatting columns
    officer_records["OfficerName"] = officer_records["OfficerName"].str.title()
    officer_records["OfficerTitle"] = officer_records["OfficerTitle"].str.title()

    # splitting officer names into first and last names
    name_parts = officer_records["OfficerName"].str.extract(r"^(?:(?:Dr|Mrs|Mr|Ms)\.?\s+)?(\S+)\s+(?:.*\s+)?(\S+)$")
    officer_records["OfficerFirstName"] = name_parts[0]
    officer_records["OfficerLastName"] = name_parts[1]

    officer_records["isUpdated"] = False
    officer_records["UpdateDate"] = pandas.NaT
    officer_records["UpdateBy"] = pandas.NA

    officer_records = officer_records.filter(items=officer_col_ls)

    return officer_records


# 3. This function sets up database connection
def psql_engine(dialect: str, driver: str, username: str, password: str, host: str, port: str, database: str):
    '''
    Action: This function connects to PostgreSQL database using SQLAlchemy Core v. 1.4.
    '''


    engine = sqlalchemy.create_engine(f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}")

    return engine


if __name__ == "__main__":
    tb_organization, tb_990_return, tb_990EZ_return, tb_990PF_return = prepare_org_records(org_records)
    tb_officer_salary = prepare_officer_records(officer_records, org_records)
    engine = psql_engine("postgresql", "psycopg2", pg_user, pg_pass, "postgres", pg_port, pg_db)

