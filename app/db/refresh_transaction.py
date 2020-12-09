from datetime import datetime, timedelta
import os

from numpy import nan as npnan
import pandas as pd
from plaid import Client

from app.db.connection_manager import SessionManager
from app.db.model import AccessToken, Account, Transaction


def refresh_transaction(client):
    try:

        now = datetime.now()
        print('|| MSG @', now, '|| refreshing transaction data')

        # Initialize DB Session
        db_session = SessionManager().session


        # Query 'access_token' from DB
        query_access_token = db_session.query(
            AccessToken.AccessToken
            ).all()

        df_query_access_token = pd.DataFrame(data=query_access_token)

        query_account_id = db_session.query(
            Account.AccountID,
            Account.AccessToken
            ).all()

        df_query_account_id = pd.DataFrame(data=query_account_id)


        # GET Transaction
        ### DYNAMICALLY CREATE START/END DATE RANGE FROM EXISTING TRANSACTIONS ###
        ### GET MAX DATE FROM TABLE AND MAKE 'start_date' 30 days prior to that ###
        ### IF FIRST CALL FOR THAT ACCOUNT, GET ALL TRANSACTIONS ###
        transaction = []
        end_date = datetime.date(datetime.now())
        start_date = (end_date - timedelta(days=365))
        end_date = end_date.strftime("%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")
        for index,row in df_query_access_token.iterrows():
            transaction_response = client.Transactions.get(access_token=row['AccessToken'], start_date=start_date, end_date=end_date)

            while len(transaction) < transaction_response['total_transactions']:
                transaction_response = client.Transactions.get(
                    access_token=row['AccessToken'],
                    start_date=start_date,
                    end_date=end_date,
                    offset=len(transaction)
                )
                transaction.extend(transaction_response['transactions'])


        # Format Data
        df_transaction_data = pd.DataFrame(data=transaction)
        df_transaction_data = df_transaction_data.fillna(npnan).replace([npnan], [None])


        # Write to DB
        for index,row in df_transaction_data.iterrows():
            db_session.merge(
                Transaction(
                    AccountID=row['account_id'],
                    TransactionID=row['transaction_id'],
                    CategoryID=row['category_id'],
                    AuthorizedDate=row['authorized_date'],
                    Date=row['date'],
                    TransactionType=row['transaction_type'],
                    Name=row['name'],
                    Amount=row['amount'],
                    ISOCurrencyCode=row['iso_currency_code'],
                    UnofficialCurrencyCode=row['unofficial_currency_code'],
                    PaymentChannel=row['payment_channel'],
                    PendingStatus=row['pending'],
                    PendingTransactionID=row['pending_transaction_id'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()

        now = datetime.now()
        print('|| MSG @', now, '|| transaction data refresh SUCCESS')

        return 0

    except Exception as ex:

        db_session.rollback()
        
        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing transaction data:', ex)

        return 1

    finally:

        db_session.close()

