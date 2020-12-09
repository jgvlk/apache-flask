from datetime import datetime, timedelta

import os

from numpy import nan as npnan
import pandas as pd
from plaid import Client

from app.db.connection_manager import SessionManager
from app.db.model import AccessToken, Account, Institution, InvestmentHolding, InvestmentSecurity, InvestmentTransaction


def refresh_investment(client):
    try:

        now = datetime.now()
        print('|| MSG @', now, '|| refreshing investment data')

        # Initialize DB Session
        db_session = SessionManager().session


        # Query 'access_token' & 'account' from DB
        query_access_token_account = db_session.query(
            Account.AccountID,
            AccessToken.AccessToken,
            ).join(
                AccessToken
            ).filter(
                Account.AccountType == 'investment'
            ).all()

        df_query_access_token_account = pd.DataFrame(data=query_access_token_account)
        l_investment_access_token = df_query_access_token_account['AccessToken'].unique()


        # Pull Holdings for an Item
        holding = []
        security = []
        for access_token in l_investment_access_token:
            investment_response = client.Holdings.get(access_token=access_token)
            holding.extend(investment_response['holdings'])
            security.extend(investment_response['securities'])


        # Handle 'securities' Response
        df_security_data = pd.DataFrame(data=security)
        df_security_data = df_security_data.fillna(npnan).replace([npnan], [None])


        # Write Securities to DB
        for index,row in df_security_data.iterrows():

            ### Check if institution_id is already in DB ###
            ### If not, call institution endpoint and insert to [dbo].[Institution] first ###
            if row['institution_id'] is not None:
                
                query_institution_id = db_session.query(Institution.InstitutionID).filter(Institution.InstitutionID == row['institution_id']).first()
                
                if query_institution_id is None:
                    institution_response = client.Institutions.get_by_id(row['institution_id'], 'US')

                    # Create Record in [dbo].[Institution]
                    db_session.merge(
                        Institution(
                            InstitutionID=row['institution_id'],
                            InstitutionName=institution_response['institution']['name'],
                            dModified=datetime.now()
                        )
                    )

                    db_session.commit()

            db_session.merge(
                InvestmentSecurity(
                    InvestmentSecurityID=row['security_id'],
                    InstitutionID=row['institution_id'],
                    ISIN=row['isin'],
                    CUSIP=row['cusip'],
                    SEDOL=row['sedol'],
                    InstitutionSecurityID=row['institution_security_id'],
                    ProxyInvestmentSecurityID=row['proxy_security_id'],
                    Name=row['name'],
                    TickerSymbol=row['ticker_symbol'],
                    IsCashEquivalent=row['is_cash_equivalent'],
                    Type=row['type'],
                    ClosePrice=row['close_price'],
                    ClosePriceAsOf=row['close_price_as_of'],
                    ISOCurrencyCode=row['iso_currency_code'],
                    UnofficialCurrencyCode=row['unofficial_currency_code'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()


        # Handle 'holdings' Response
        query_account_lookup = db_session.query(
            Account.AccountID
            ).all()

        query_investment_security_lookup = db_session.query(
            InvestmentSecurity.InvestmentSecurityID
            ).all()

        df_query_investment_security_lookup = pd.DataFrame(data=query_investment_security_lookup)

        df_holding_data = pd.DataFrame(data=holding)
        df_holding_data = df_holding_data.fillna(npnan).replace([npnan], [None])


        # Write Holdings to DB
        for index,row in df_holding_data.iterrows():
            db_session.merge(
                InvestmentHolding(
                    AccountID=row['account_id'],
                    InvestmentSecurityID=row['security_id'],
                    InstitutionPrice=row['institution_price'],
                    InstitutionPriceAsOf=row['institution_price_as_of'],
                    InstitutionValue=row['institution_value'],
                    CostBasis=row['cost_basis'],
                    Quantity=row['quantity'],
                    ISOCurrencyCode=row['iso_currency_code'],
                    UnofficialCurrencyCode=row['unofficial_currency_code'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()


        # GET Investment Transactions
        investment_transaction = []
        end_date = datetime.date(datetime.now())
        start_date = (end_date - timedelta(days=365))
        end_date = end_date.strftime("%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")
        for access_token in l_investment_access_token:
            investment_transaction_response = client.InvestmentTransactions.get(access_token=access_token, start_date=start_date, end_date=end_date)

            while len(investment_transaction) < investment_transaction_response['total_investment_transactions']:
                investment_transaction_response = client.InvestmentTransactions.get(
                    access_token=access_token,
                    start_date=start_date,
                    end_date=end_date,
                    offset=len(investment_transaction)
                )
                investment_transaction.extend(investment_transaction_response['investment_transactions'])


        # Format Data
        df_investment_transaction_data = pd.DataFrame(data=investment_transaction)
        df_investment_transaction_data = df_investment_transaction_data.fillna(npnan).replace([npnan], [None])


        # Write Investment Transactions to DB
        for index,row in df_investment_transaction_data.iterrows():
            db_session.merge(
                InvestmentTransaction(
                    InvestmentTransactionID=row['investment_transaction_id'],
                    AccountID=row['account_id'],
                    InvestmentSecurityID=row['security_id'],
                    Date=row['date'],
                    Name=row['name'],
                    Quantity=row['quantity'],
                    Amount=row['amount'],
                    Price=row['price'],
                    Fees=row['fees'],
                    Type=row['type'],
                    SubType=row['subtype'],
                    ISOCurrencyCode=row['iso_currency_code'],
                    UnofficialCurrencyCode=row['unofficial_currency_code'],
                    CancelTransactionID=row['cancel_transaction_id']
                )
            )


        db_session.commit()

        now = datetime.now()
        print('|| MSG @', now, '|| category data refresh SUCCESS')

        return 0

    except Exception as ex:

        db_session.rollback()

        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        
        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing investment data:', ex)

        return 1

    finally:
        
        db_session.close()

