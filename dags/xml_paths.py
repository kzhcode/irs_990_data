
# 0.0. Setting XML schema and variable paths within XML document
NS = {"irs": "http://www.irs.gov/efile"}


# 0.1. Setting paths to extract 990 organization data from XML
FIELD_990_ORG_XPATHS = {
    "ReturnDate": "//irs:ReturnHeader/irs:ReturnTs",
    "ReturnType": "//irs:ReturnHeader/irs:PreparerFirmGrp/irs:ReturnTypeCd",
    "OrgEIN": "//irs:ReturnHeader/irs:Filer/irs:EIN",
    "OrgBusinessName": "//irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt",
    "OrgPhoneNumber": "//irs:ReturnHeader/irs:Filer/irs:PhoneNum",
    "OrgStreet": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:AddressLine1Txt",
    "OrgCity": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:CityNm",
    "OrgState": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:StateAbbreviationCd",
    "OrgZip": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:ZIPCd",
    "OrgWebsite": "//irs:ReturnData/irs:IRS990/irs:WebsiteAddressTxt",
    "OrgFormationYr": "//irs:ReturnData/irs:IRS990/irs:FormationYr",
    "OrgMissionDisc": "//irs:ReturnData/irs:IRS990/irs:ActivityOrMissionDesc",
    "TaxYr": "//irs:ReturnHeader/irs:TaxYr",
    "GrossReceiptsAmt": "//irs:ReturnData/irs:IRS990/irs:GrossReceiptsAmt",
    "TotalEmployeeCnt": "//irs:ReturnData/irs:IRS990/irs:EmployeeCnt",
    "TotalGrossUBIAmt": "//irs:ReturnData/irs:IRS990/irs:TotalGrossUBIAmt",
    "ContribGrantsAmt": "//irs:ReturnData/irs:IRS990/irs:CYContributionsGrantsAmt",
    "ProgramServiceRevAmt": "//irs:ReturnData/irs:IRS990/irs:CYProgramServiceRevenueAmt",
    "InvestIncomeAmt": "//irs:ReturnData/irs:IRS990/irs:CYInvestmentIncomeAmt",
    "OtherRevAmt": "//irs:ReturnData/irs:IRS990/irs:CYOtherRevenueAmt",
    "TotalRevAmt": "//irs:ReturnData/irs:IRS990/irs:CYTotalRevenueAmt",
    "GrantsAndSimilarPaidAmt": "//irs:ReturnData/irs:IRS990/irs:CYGrantsAndSimilarPaidAmt",
    "BenefitsPaidToMembersAmt": "//irs:ReturnData/irs:IRS990/irs:CYBenefitsPaidToMembersAmt",
    "SalariesCompEmpBnftPaidAmt": "//irs:ReturnData/irs:IRS990/irs:CYSalariesCompEmpBnftPaidAmt",
    "TotalProfFndrsngExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:CYTotalProfFndrsngExpnsAmt",
    "TotalFndrsngExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:CYTotalFundraisingExpenseAmt",
    "OtherExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:CYOtherExpensesAmt",
    "TotalExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:CYTotalExpensesAmt",
    "RevLessExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:CYRevenuesLessExpensesAmt",
    "TotalAssetsBOYAmt": "//irs:ReturnData/irs:IRS990/irs:TotalAssetsBOYAmt",
    "TotalAssetsEOYAmt": "//irs:ReturnData/irs:IRS990/irs:TotalAssetsEOYAmt",
    "TotalLiabilitiesBOYAmt": "//irs:ReturnData/irs:IRS990/irs:TotalLiabilitiesBOYAmt",
    "TotalLiabilitiesEOYAmt": "//irs:ReturnData/irs:IRS990/irs:TotalLiabilitiesEOYAmt",
    "NetAssetsOrFundBalancesBOYAmt": "//irs:ReturnData/irs:IRS990/irs:NetAssetsOrFundBalancesBOYAmt",
    "NetAssetsOrFundBalancesEOYAmt": "//irs:ReturnData/irs:IRS990/irs:NetAssetsOrFundBalancesEOYAmt",
    "ExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:ExpenseAmt",
    "GrantAmt": "//irs:ReturnData/irs:IRS990/irs:GrantAmt",
    "RevAmt": "//irs:ReturnData/irs:IRS990/irs:RevenueAmt",
    "TotalOtherProgSrvcExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:TotalOtherProgSrvcExpenseAmt",
    "TotalOtherProgSrvcGrantAmt": "//irs:ReturnData/irs:IRS990/irs:TotalOtherProgSrvcGrantAmt",
    "TotalOtherProgSrvcRevAmt": "//irs:ReturnData/irs:IRS990/irs:TotalOtherProgSrvcRevenueAmt",
    "TotalProgramSrvcExpnsAmt": "//irs:ReturnData/irs:IRS990/irs:TotalProgramServiceExpensesAmt",
    "TotalReportableCompFromOrgAmt": "//irs:ReturnData/irs:IRS990/irs:TotalReportableCompFromOrgAmt",
    "TotalReportableCompRltdOrgAmt": "//irs:ReturnData/irs:IRS990/irs:TotReportableCompRltdOrgAmt",
    "TotalOtherCompAmt": "//irs:ReturnData/irs:IRS990/irs:TotalOtherCompensationAmt",
    "FederatedCampaignsAmt": "//irs:ReturnData/irs:IRS990/irs:FederatedCampaignsAmt",
    "MembershipDuesAmt": "//irs:ReturnData/irs:IRS990/irs:MembershipDuesAmt",
    "FundraisingAmt": "//irs:ReturnData/irs:IRS990/irs:FundraisingAmt",
    "RelatedOrgAmt": "//irs:ReturnData/irs:IRS990/irs:RelatedOrganizationsAmt",
    "GovGrantsAmt": "//irs:ReturnData/irs:IRS990/irs:GovernmentGrantsAmt",
    "AllOtherContrAmt": "//irs:ReturnData/irs:IRS990/irs:AllOtherContributionsAmt",
    "NonCashContrAmt": "//irs:ReturnData/irs:IRS990/irs:NoncashContributionsAmt",
    "TotalContrAmt": "//irs:ReturnData/irs:IRS990/irs:TotalContributionsAmt"
}


# 0.2. Setting paths to extract 990 officers data from XML
OFFICER_990_XPATHS = {
    "OfficerName": "irs:PersonNm",
    "OfficerTitle": "irs:TitleTxt",
    "OfficerAvgHrsPerWeekRt": "irs:AverageHoursPerWeekRt",
    "OfficerAvgHrsPerWeekRltdOrgRt": "irs:AverageHoursPerWeekRltdOrgRt",
    "OfficerReportCompFromOrgAmt": "irs:ReportableCompFromOrgAmt",
    "OfficerReportCompFromRltdOrgAmt": "irs:ReportableCompFromRltdOrgAmt",
    "OfficerOtherCompAmt": "irs:OtherCompensationAmt"
}


# 0.3. Setting paths to extract 990EZ organization data from XML
FIELD_990EZ_ORG_XPATHS = {
    "ReturnDate": "//irs:ReturnHeader/irs:ReturnTs",
    "ReturnType": "//irs:ReturnHeader/irs:PreparerFirmGrp/irs:ReturnTypeCd",
    "OrgEIN": "//irs:ReturnHeader/irs:Filer/irs:EIN",
    "OrgBusinessName": "//irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt",
    "OrgPhoneNumber": "//irs:ReturnHeader/irs:Filer/irs:PhoneNum",
    "OrgStreet": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:AddressLine1Txt",
    "OrgCity": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:CityNm",
    "OrgState": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:StateAbbreviationCd",
    "OrgZip": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:ZIPCd",
    "OrgWebsite": "//irs:ReturnData/irs:IRS990EZ/irs:WebsiteAddressTxt",
    "OrgMissionDisc": "//irs:ReturnData/irs:IRS990EZ/irs:PrimaryExemptPurposeTxt",
    "TaxYr": "//irs:ReturnHeader/irs:TaxYr",
    "GrossReceiptsAmt": "//irs:ReturnData/irs:IRS990EZ/irs:GrossReceiptsAmt",
    "ContrGiftsGrantsEtcAmt": "//irs:ReturnData/irs:IRS990EZ/irs:ContributionsGiftsGrantsEtcAmt",
    "ProgSrvcRevenueAmt": "//irs:ReturnData/irs:IRS990EZ/irs:ProgramServiceRevenueAmt",
    "MembershipDuesAmt": "//irs:ReturnData/irs:IRS990EZ/irs:MembershipDuesAmt",
    "TotalRevenueAmt": "//irs:ReturnData/irs:IRS990EZ/irs:TotalRevenueAmt",
    "FeesAndOtherPymtToIndCntrctAmt": "//irs:ReturnData/irs:IRS990EZ/irs:FeesAndOtherPymtToIndCntrctAmt",
    "OtherExpnsTotalAmt": "//irs:ReturnData/irs:IRS990EZ/irs:OtherExpensesTotalAmt",
    "TotalExpnsAmt": "//irs:ReturnData/irs:IRS990EZ/irs:TotalExpensesAmt",
    "ExcessOrDeficitForYearAmt": "//irs:ReturnData/irs:IRS990EZ/irs:ExcessOrDeficitForYearAmt",
    "NetAssetsOrFundBalancesBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:NetAssetsOrFundBalancesBOYAmt",
    "OtherChangesInNetAssetsAmt": "//irs:ReturnData/irs:IRS990EZ/irs:OtherChangesInNetAssetsAmt",
    "NetAssetsOrFundBalancesEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:NetAssetsOrFundBalancesEOYAmt",
    "CashSavingsAndInvestmentsBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:CashSavingsAndInvestmentsGrp/irs:BOYAmt",
    "CashSavingsAndInvestmentsEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:CashSavingsAndInvestmentsGrp/irs:EOYAmt",
    "OtherAssetsTotalDetailBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:OtherAssetsTotalDetail/irs:BOYAmt",
    "OtherAssetsTotalDetailEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:OtherAssetsTotalDetail/irs:EOYAmt",
    "Form990TotalAssetsBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:Form990TotalAssetsGrp/irs:BOYAmt",
    "Form990TotalAssetsEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:Form990TotalAssetsGrp/irs:EOYAmt",
    "SumOfTotalLiabilitiesBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:SumOfTotalLiabilitiesGrp/irs:BOYAmt",
    "SumOfTotalLiabilitiesEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:SumOfTotalLiabilitiesGrp/irs:EOYAmt",
    "NetAssetsOrFundBalancesGrpBOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:NetAssetsOrFundBalancesGrp/irs:BOYAmt",
    "NetAssetsOrFundBalancesGrpEOYAmt": "//irs:ReturnData/irs:IRS990EZ/irs:NetAssetsOrFundBalancesGrp/irs:EOYAmt",
    "TotalProgSrvcExpensesAmt": "//irs:ReturnData/irs:IRS990EZ/irs:TotalProgramServiceExpensesAmt"
}


# 0.4. Setting paths to extract 990EZ officers data from XML
OFFICER_990EZ_XPATHS = {
    "OfficerName": "irs:PersonNm",
    "OfficerTitle": "irs:TitleTxt",
    "OfficerAvgHrsPerWkDevotedToPosRt": "irs:AverageHrsPerWkDevotedToPosRt",
    "OfficerCompAmt": "irs:CompensationAmt",
    "OfficerEmplBenefitProgAmt": "irs:EmployeeBenefitProgramAmt",
    "OfficerExpnsAccntOtherAllwncAmt": "irs:ExpenseAccountOtherAllwncAmt"
}


# 0.5. Setting paths to extract 990PF organization data from XML
FIELD_990PF_ORG_XPATHS = {
    "ReturnDate": "//irs:ReturnHeader/irs:ReturnTs",
    "ReturnType": "//irs:ReturnHeader/irs:ReturnTypeCd",
    "OrgEIN": "//irs:ReturnHeader/irs:Filer/irs:EIN",
    "OrgBusinessName": "//irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt",
    "OrgPhoneNumber": "//irs:ReturnHeader/irs:Filer/irs:PhoneNum",
    "OrgStreet": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:AddressLine1Txt",
    "OrgCity": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:CityNm",
    "OrgState": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:StateAbbreviationCd",
    "OrgZip": "//irs:ReturnHeader/irs:Filer/irs:USAddress/irs:ZIPCd",
    "TaxYr": "//irs:ReturnHeader/irs:TaxYr",
    "FMVAssetsEOYAmt": "//irs:ReturnData/irs:IRS990PF/irs:FMVAssetsEOYAmt",
    "MethodOfAccountingCashInd": "//irs:ReturnData/irs:IRS990PF/irs:MethodOfAccountingCashInd",
    "ContriRcvdRevAndExpnssAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:ContriRcvdRevAndExpnssAmt",
    "InterestOnSavRevAndExpnssAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:InterestOnSavRevAndExpnssAmt",
    "InterestOnSavNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:InterestOnSavNetInvstIncmAmt",
    "InterestOnSavingsAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:InterestOnSavingsAdjNetIncmAmt",
    "DividendsRevAndExpnssAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:DividendsRevAndExpnssAmt",
    "DividendsNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:DividendsNetInvstIncmAmt",
    "DividendsAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:DividendsAdjNetIncmAmt",
    "GrossRentsRevAndExpnssAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossRentsRevAndExpnssAmt",
    "GrossRentsNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossRentsNetInvstIncmAmt",
    "GrossRentsAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossRentsAdjNetIncmAmt",
    "NetRentalIncomeOrLossAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:NetRentalIncomeOrLossAmt",
    "GrossSalesPriceAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossSalesPriceAmt",
    "CapGainNetIncmNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:CapGainNetIncmNetInvstIncmAmt",
    "IncmModificationsAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:IncmModificationsAdjNetIncmAmt",
    "GrossSalesLessRetAndAllwncAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossSalesLessRetAndAllwncAmt",
    "CostOfGoodsSoldAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:CostOfGoodsSoldAmt",
    "GrossProfitAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:GrossProfitAdjNetIncmAmt",
    "OtherIncomeNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:OtherIncomeNetInvstIncmAmt",
    "OtherIncomeAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:OtherIncomeAdjNetIncmAmt",
    "TotalRevAndExpnssAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:TotalRevAndExpnssAmt",
    "TotalNetInvstIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:TotalNetInvstIncmAmt",
    "TotalAdjNetIncmAmt": "//irs:ReturnData/irs:IRS990PF/irs:AnalysisOfRevenueAndExpenses/irs:TotalAdjNetIncmAmt"
}

