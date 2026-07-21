
-- Create tb_organization
CREATE TABLE tb_organization (
    Ein VARCHAR(10) PRIMARY KEY,
    BusinessName text,
    Street text,
    City text,
    State text CONSTRAINT org_state_length_check CHECK (char_length(State) = 2),
    Zip VARCHAR(5) CONSTRAINT org_zip_code_length CHECK (char_length(Zip) = 5),
    Phone VARCHAR(10) CONSTRAINT org_phone_length CHECK (char_length(Phone) = 10),
    OrgExemptCode text,
    EmployeeCount integer,
    CreateDate timestamp,
    isUpdated boolean DEFAULT FALSE,
    UpdateDate timestamp,
    UpdateBy text
);

-- Create tb_employee
CREATE TABLE tb_employee (
    Ein VARCHAR(10) REFERENCES tb_organization (Ein),
    EmployeeId VARCHAR(10) PRIMARY KEY,
    FirstName text,
    LastName text,
    WorkEmail text,
    PersonalEmail text,
    Street text,
    City text,
    State text CONSTRAINT emp_state_length_check CHECK (char_length(State) = 2),
    Zip VARCHAR(5) CONSTRAINT emp_zip_code_length CHECK (char_length(Zip) = 5),
    WorkTitle text,
    WorkPhone VARCHAR(10) CONSTRAINT emp_work_phone_length CHECK (char_length(WorkPhone) = 10),
    PersonalPhone VARCHAR(10) CONSTRAINT emp_persnl_phone_length CHECK (char_length(PersonalPhone) = 10),
    Gender text,
    Race text,
    Note text,
    CreateDate timestamp,
    isUpdated boolean DEFAULT FALSE,
    UpdateDate timestamp,
    UpdateBy text
);

-- Create tb_salary
CREATE TABLE tb_salary (
    EmployeeId VARCHAR(10) REFERENCES tb_employee (EmployeeId),
    Year numeric(4, 0),
    AvgHrsPerWeek numeric(4, 2),
    CompFromOrgAmt numeric,
    CompFromRltdOrgAmt numeric,
    OtherCompAmt numeric,
    CreateDate timestamp,
    isUpdated boolean DEFAULT FALSE,
    UpdateDate timestamp,
    UpdateBy text,
    PRIMARY KEY (EmployeeId, Year)
);

-- Create tb_990data
CREATE TABLE tb_990data (
    Ein VARCHAR(10) REFERENCES tb_organization (Ein),
    Year numeric(4, 0),
    GrossReceiptsAmt numeric,
    NetUnrelatedBusTxblIncmAmt numeric,
    PYContributionsGrantsAmt numeric,
    CYContributionsGrantsAmt numeric,
    PYProgramServiceRevenueAmt numeric,
    CYProgramServiceRevenueAmt numeric,
    PYInvestmentIncomeAmt numeric,
    CYInvestmentIncomeAmt numeric,
    PYOtherRevenueAmt numeric,
    CYOtherRevenueAmt numeric,
    PYTotalRevenueAmt numeric,
    CYTotalRevenueAmt numeric,
    PYGrantsAndSimilarPaidAmt numeric,
    CYGrantsAndSimilarPaidAmt numeric,
    PYBenefitsPaidToMembersAmt numeric,
    CYBenefitsPaidToMembersAmt numeric,
    PYSalariesCompEmpBnftPaidAmt numeric,
    CYSalariesCompEmpBnftPaidAmt numeric,
    PYTotalProfFndrsngExpnsAmt numeric,
    CYTotalProfFndrsngExpnsAmt numeric,
    CYTotalFundraisingExpenseAmt numeric,
    PYOtherExpensesAmt numeric,
    CYOtherExpensesAmt numeric,
    PYTotalExpensesAmt numeric,
    CYTotalExpensesAmt numeric,
    PYRevenuesLessExpensesAmt numeric,
    CYRevenuesLessExpensesAmt numeric,
    TotalAssetsBOYAmt numeric,
    TotalAssetsEOYAmt numeric,
    TotalLiabilitiesBOYAmt numeric,
    TotalLiabilitiesEOYAmt numeric,
    NetAssetsOrFundBalancesBOYAmt numeric,
    NetAssetsOrFundBalancesEOYAmt numeric,
    TotalOtherProgSrvcExpenseAmt numeric,
    TotalProgramServiceExpensesAmt numeric,
    CreateDate timestamp,
    isUpdated boolean DEFAULT FALSE,
    UpdateDate timestamp,
    UpdateBy text,
    PRIMARY KEY (Ein, Year)
);