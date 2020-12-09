from datetime import datetime
import os

from numpy import nan as npnan
import pandas as pd
from plaid import Client
from sqlalchemy import or_, text

from app.db.connection_manager import SessionManager
from app.db.model import AccessToken, Account, Institution, LiabilityStudentLoan, LiabilityCreditCard, LiabilityMortgage


def refresh_liability(client):
    try:

        now = datetime.now()
        print('|| MSG @', now, '|| refreshing liability data')
        
        # Initialize DB Session
        db_session = SessionManager().session


        # Query Lookups from DB
        query_access_token_account = db_session.query(
                Account.AccountID,
                AccessToken.AccessToken,
                Institution.InstitutionID
            ).join(
                AccessToken, Account.AccessToken==AccessToken.AccessToken
            ).join(
                Institution, AccessToken.InstitutionID==Institution.InstitutionID
            ).filter(
                or_(
                    Account.AccountType == 'credit',
                    Account.AccountType == 'loan'
                )
            ).all()

        df_query_access_token_account = pd.DataFrame(data=query_access_token_account)
        df_query_access_token_account_dedup = df_query_access_token_account[['AccessToken', 'InstitutionID']].drop_duplicates()


        # Get Products by Institution
        institution = {}
        for index,row in df_query_access_token_account_dedup.iterrows():
            institution_response = client.Institutions.get_by_id(row['InstitutionID'], ['US'])
            institution[row['InstitutionID']] = institution_response['institution']['products']


        # GET Liabilities
        credit = []
        mortgage = []
        student = []
        for index,row in df_query_access_token_account_dedup.iterrows():
            if 'liabilities' in institution[row['InstitutionID']]:
                liability_response = client.Liabilities.get(access_token=row['AccessToken'])
                credit.extend(liability_response['liabilities']['credit'])
                mortgage.extend(liability_response['liabilities']['mortgage'])
                student.extend(liability_response['liabilities']['student'])


        # Format Data
        df_credit_data = pd.DataFrame(data=credit)
        df_mortgage_data = pd.DataFrame(data=mortgage)
        df_student_data = pd.DataFrame(data=student)

        df_credit_data = df_credit_data.fillna(npnan).replace([npnan], [None])
        df_mortgage_data = df_mortgage_data.fillna(npnan).replace([npnan], [None])
        df_student_data = df_student_data.fillna(npnan).replace([npnan], [None])


        # Write Credit Data to DB
        for index,row in df_credit_data.iterrows():

            if len(row['aprs']) == 0:
                APRPercentage = None
                APRType = None
                BalanceSubjectToAPR = None
                InterestChargeAmount = None
            else:
                APRPercentage = row['aprs'][index]['interest_charge_amount']
                APRType = row['aprs'][index]['apr_type']
                BalanceSubjectToAPR = row['aprs'][index]['balance_subject_to_apr']
                InterestChargeAmount = row['aprs'][index]['interest_charge_amount']

            db_session.merge(
                LiabilityCreditCard(
                    AccountID=row['account_id'],
                    APRPercentage=APRPercentage,
                    APRType=APRType,
                    BalanceSubjectToAPR=BalanceSubjectToAPR,
                    InterestChargeAmount=InterestChargeAmount,
                    IsOverdue=row['is_overdue'],
                    LastPaymentAmount=row['last_payment_amount'],
                    LastPaymentDate=row['last_payment_date'],
                    LastStatementBalance=row['last_statement_balance'],
                    LastStatementIssueDate=row['last_statement_issue_date'],
                    MinimumPaymentAmount=row['minimum_payment_amount'],
                    NextPaymentDueDate=row['next_payment_due_date'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()


        # Write Student Loan Data to DB
        for index,row in df_student_data.iterrows():
            db_session.merge(
                LiabilityStudentLoan(
                    AccountID=row['account_id'],
                    AccountNumber=row['account_number'],
                    DisbursementDates=None,
                    ExpectedPayoffDate=row['expected_payoff_date'],
                    Guarantor=row['guarantor'],
                    InterestRatePercentage=row['interest_rate_percentage'],
                    IsOverdue=row['is_overdue'],
                    LastPaymentAmount=row['last_payment_amount'],
                    LastStatementBalance=row['last_statement_balance'],
                    LastStatementIssueDate=row['last_statement_issue_date'],
                    LoanName=row['loan_name'],
                    LoanStatusType=row['loan_status']['type'],
                    LoanStatusEndDate=row['loan_status']['end_date'],
                    MinimumPaymentAmount=row['minimum_payment_amount'],
                    NextPaymentDueDate=row['next_payment_due_date'],
                    OriginationDate=row['origination_date'],
                    OriginationPrincipalAmount=row['origination_principal_amount'],
                    OutstandingInterestAmount=row['outstanding_interest_amount'],
                    PaymentReferenceNumber=row['payment_reference_number'],
                    PSLFEstimatedEligibilityDate=row['pslf_status']['estimated_eligibility_date'],
                    PSLFPaymentsMade=row['pslf_status']['payments_made'],
                    PSLFPaymentsRemaining=row['pslf_status']['payments_remaining'],
                    RepaymentPlanType=row['repayment_plan']['type'],
                    RepaymentPlanDescription=row['repayment_plan']['description'],
                    SequenceNumber=row['sequence_number'],
                    ServicerStreet=row['servicer_address']['street'],
                    ServicerCity=row['servicer_address']['city'],
                    ServicerRegion=row['servicer_address']['region'],
                    ServicerPostalCode=row['servicer_address']['postal_code'],
                    ServicerCountry=row['servicer_address']['country'],
                    YTDInterestPaid=row['ytd_interest_paid'],
                    YTDPrincipalPaid=row['ytd_principal_paid'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()


        # Write Mortgage Data to DB
        for index,row in df_mortgage_data.iterrows():
            db_session.merge(
                LiabilityMortgage(
                    AccountID=row['account_id'],
                    AccountNumber=row['account_number'],
                    CurrentLateFee=row['current_late_fee'],
                    EscrowBalance=row['escrow_balance'],
                    HasPMI=row['has_pmi'],
                    LastPaymentAmount=row['last_payment_amount'],
                    LastPaymentDate=row['last_payment_date'],
                    LoanTerm=row['loan_term'],
                    LoanTypeDescription=row['loan_type_description'],
                    MaturityDate=row['maturity_date'],
                    NextMonthlyPayment=row['next_monthly_payment'],
                    NextPaymentDueDate=row['next_payment_due_date'],
                    OriginationDate=row['origination_date'],
                    OriginationPrincipalAmount=row['origination_principal_amount'],
                    PastDueAmount=row['past_due_amount'],
                    PropertyStreet=row['property_address']['street'],
                    PropertyCity=row['property_address']['city'],
                    PropertyRegion=row['property_address']['region'],
                    PropertyCountry=row['property_address']['country'],
                    PropertyPostalCode=row['property_address']['postal_code'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()

        now = datetime.now()
        print('|| MSG @', now, '|| liability data refresh SUCCESS')

        return 0

    except Exception as ex:

        db_session.rollback()
        
        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing liability data:', ex.args)

        return 1

    finally:
        
        db_session.close()

