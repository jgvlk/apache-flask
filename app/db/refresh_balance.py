from datetime import datetime
import os

from numpy import nan as npnan
import pandas as pd
from plaid import Client

from app.db.connection_manager import SessionManager
from app.db.model import AccessToken, Account, Balance


def refresh_balance(client):
    try:

        now = datetime.now()
        print('|| MSG @', now, '|| refreshing balance data')

        # Initialize DB Session
        db_session = SessionManager().session


        # Query 'access_token' from DB
        query_access_token = db_session.query(
            AccessToken.AccessToken
            ).all()

        df_query_access_token = pd.DataFrame(data=query_access_token)


        # GET Balance
        balance = []
        for index,row in df_query_access_token.iterrows():
            balance_response = client.Accounts.balance.get(access_token=row['AccessToken'])
            balance.extend(balance_response['accounts'])


        # Format Data
        df_balance_data = pd.DataFrame(data=balance)
        df_balance_data = df_balance_data.fillna(npnan).replace([npnan], [None])


        # Write to DB
        for index,row in df_balance_data.iterrows():
            db_session.merge(
                Balance(
                    AccountID=row['account_id'],
                    CurrentBalance=row['balances']['current'],
                    AvailableBalance=row['balances']['available'],
                    BalanceLimit=row['balances']['limit'],
                    ISOCurrencyCode=row['balances']['iso_currency_code'],
                    UnofficialCurrencyCode=row['balances']['unofficial_currency_code'],
                    dModified=datetime.now()
                )
            )


        db_session.commit()

        now = datetime.now()
        print('|| MSG @', now, '|| balance data refresh SUCCESS')

        return 0

    except Exception as ex:

        db_session.rollback()

        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing balance data:', ex)

        return 1

    finally:
        
        db_session.close()

