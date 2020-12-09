import os
from datetime import datetime
import time

from numpy import nan as npnan
import pandas as pd
from plaid import Client

from app.db.connection_manager import SessionManager
from app.db.model import AccessToken, Account, Balance, BatchLog, TableRefreshLog
from app.db.refresh_balance import refresh_balance
from app.db.refresh_category import refresh_category
from app.db.refresh_investment import refresh_investment
from app.db.refresh_liability import refresh_liability
from app.db.refresh_transaction import refresh_transaction
from app.utilities.json_serialize_helper import json_serial


def RefreshAll(client, db_session):

    try:

        statusd = {}

        # Log to audit table [aud].[__BatchLog]
        batch_start = datetime.now()
        print('|| MSG @', batch_start, '|| myplaid data refresh starting...')

        db_session.add(
            BatchLog(
                Start=batch_start,
                End=None,
                IsSuccessful=0
            )
        )

        db_session.flush()

        ####################
        ##### FIX THIS #####
        # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
        batch_log_id = db_session.query(BatchLog.BatchLogID).all()
        i = len(batch_log_id) - 1
        batch_log_id = batch_log_id[i][0]
        ####################
        ####################

        db_session.commit()


        try:

            # Refresh balance data
            # Log to audit table [aud].[TableRefreshLog]
            table_refresh_start = datetime.now()
            item_name = 'Balance'

            db_session.add(
                TableRefreshLog(
                    BatchLogID=batch_log_id,
                    ItemName=item_name,
                    Start=table_refresh_start,
                    End=None,
                    IsSuccessful=0
                )
            )

            db_session.flush()

            # Set table_refresh_id
            ####################
            ##### FIX THIS #####
            # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
            table_refresh_id = db_session.query(TableRefreshLog.TableRefreshLogID).filter(TableRefreshLog.ItemName == item_name).all()
            b = len(table_refresh_id) - 1
            table_refresh_id = table_refresh_id[b][0]
            ####################
            ####################

            db_session.flush()

            # Refresh balance data
            ret_refresh_balance = refresh_balance(client)


            # Log IsSuccessful = 1 to audit table [aud].[TableRefreshLog]
            if ret_refresh_balance == 0:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end, 'IsSuccessful': 1}, synchronize_session=False)

                statusd['refresh_balance'] = 0

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            if ret_refresh_balance == 1:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

                statusd['refresh_balance'] = 1
            
            db_session.commit()

        except Exception as e:

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            table_refresh_end = datetime.now()
            db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

            db_session.commit()


        #########################################################################################
        #########################################################################################


        try:

            # Refresh category data
            # Log to audit table [aud].[TableRefreshLog]
            table_refresh_start = datetime.now()
            item_name = 'Category'

            db_session.add(
                TableRefreshLog(
                    BatchLogID=batch_log_id,
                    ItemName=item_name,
                    Start=table_refresh_start,
                    End=None,
                    IsSuccessful=0
                )
            )

            db_session.flush()

            # Set table_refresh_id
            ####################
            ##### FIX THIS #####
            # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
            table_refresh_id = db_session.query(TableRefreshLog.TableRefreshLogID).filter(TableRefreshLog.ItemName == item_name).all()
            b = len(table_refresh_id) - 1
            table_refresh_id = table_refresh_id[b][0]
            ####################
            ####################

            db_session.flush()


            # Refresh category data
            ret_refresh_category = refresh_category(client)


            # Log IsSuccessful = 1 to audit table [aud].[TableRefreshLog]
            if ret_refresh_category == 0:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end, 'IsSuccessful': 1}, synchronize_session=False)

                statusd['refresh_category'] = 0

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            if ret_refresh_category == 1:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

                statusd['refresh_category'] = 1

            db_session.commit()

        except Exception as e:

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            table_refresh_end = datetime.now()
            db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

            db_session.commit()


        #########################################################################################
        #########################################################################################


        try:

            # Refresh investment data
            # Log to audit table [aud].[TableRefreshLog]
            table_refresh_start = datetime.now()
            item_name = 'Investment'

            db_session.add(
                TableRefreshLog(
                    BatchLogID=batch_log_id,
                    ItemName=item_name,
                    Start=table_refresh_start,
                    End=None,
                    IsSuccessful=0
                )
            )

            db_session.flush()

            # Set table_refresh_id
            ####################
            ##### FIX THIS #####
            # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
            table_refresh_id = db_session.query(TableRefreshLog.TableRefreshLogID).filter(TableRefreshLog.ItemName == item_name).all()
            b = len(table_refresh_id) - 1
            table_refresh_id = table_refresh_id[b][0]
            ####################
            ####################

            db_session.flush()


            # Refresh investment data
            ret_refresh_investment = refresh_investment(client)


            # Log IsSuccessful = 1 to audit table [aud].[TableRefreshLog]
            if ret_refresh_investment == 0:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end, 'IsSuccessful': 1}, synchronize_session=False)

                statusd['refresh_investment'] = 0

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            if ret_refresh_investment == 1:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

                statusd['refresh_investment'] = 1

            db_session.commit()

        except Exception as e:

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            table_refresh_end = datetime.now()
            db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

            db_session.commit()


        #########################################################################################
        #########################################################################################

        try:

            # Refresh liability data
            # Log to audit table [aud].[TableRefreshLog]
            table_refresh_start = datetime.now()
            item_name = 'Liability'

            db_session.add(
                TableRefreshLog(
                    BatchLogID=batch_log_id,
                    ItemName=item_name,
                    Start=table_refresh_start,
                    End=None,
                    IsSuccessful=0
                )
            )

            db_session.flush()

            # Set table_refresh_id
            ####################
            ##### FIX THIS #####
            # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
            table_refresh_id = db_session.query(TableRefreshLog.TableRefreshLogID).filter(TableRefreshLog.ItemName == item_name).all()
            b = len(table_refresh_id) - 1
            table_refresh_id = table_refresh_id[b][0]
            ####################
            ####################

            db_session.flush()


            # Refresh liability data
            ret_refresh_liability = refresh_liability(client)


            # Log IsSuccessful = 1 to audit table [aud].[TableRefreshLog]
            if ret_refresh_liability == 0:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end, 'IsSuccessful': 1}, synchronize_session=False)

                statusd['refresh_liability'] = 0

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            if ret_refresh_liability == 1:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

                statusd['refresh_liability'] = 1

            db_session.commit()

        except Exception as e:

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            table_refresh_end = datetime.now()
            db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

            db_session.commit()


        #########################################################################################
        #########################################################################################

        try:

            # Refresh transaction data
            # Log to audit table [aud].[TableRefreshLog]
            table_refresh_start = datetime.now()
            item_name = 'Transaction'

            db_session.add(
                TableRefreshLog(
                    BatchLogID=batch_log_id,
                    ItemName=item_name,
                    Start=table_refresh_start,
                    End=None,
                    IsSuccessful=0
                )
            )

            db_session.flush()

            # Set table_refresh_id
            ####################
            ##### FIX THIS #####
            # SEE IF THERE'S A BETTER WAY TO GET BACK THE LAST INSERTED ID FOR THIS SESSION
            table_refresh_id = db_session.query(TableRefreshLog.TableRefreshLogID).filter(TableRefreshLog.ItemName == item_name).all()
            b = len(table_refresh_id) - 1
            table_refresh_id = table_refresh_id[b][0]
            ####################
            ####################

            db_session.flush()


            # Refresh transaction data
            ret_refresh_transaction = refresh_transaction(client)


            # Log IsSuccessful = 1 to audit table [aud].[TableRefreshLog]
            if ret_refresh_transaction == 0:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end, 'IsSuccessful': 1}, synchronize_session=False)

                statusd['refresh_transaction'] = 0

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            if ret_refresh_transaction == 1:
                table_refresh_end = datetime.now()
                db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

                statusd['refresh_transaction'] = 1
            db_session.commit()

        except Exception as e:

            # Log IsSuccessful = 0 to audit table [aud].[TableRefreshLog]
            table_refresh_end = datetime.now()
            db_session.query(TableRefreshLog).filter(TableRefreshLog.TableRefreshLogID == table_refresh_id).update({'End': table_refresh_end}, synchronize_session=False)

            db_session.commit()


        #########################################################################################
        #########################################################################################

        # Log IsSuccessful = 1 to audit table [aud].[BatchLog]
        batch_end = datetime.now()
        db_session.query(BatchLog).filter(BatchLog.BatchLogID == batch_log_id).update({'End': batch_end, 'IsSuccessful': 1}, synchronize_session=False)

        db_session.commit()


        if 1 in statusd.values():
            now = datetime.now()
            print('|| MSG @', now, '|| myplaid data refresh completed with errors')
        else:
            now = datetime.now()
            print('|| MSG @', now, '|| myplaid data refresh completed')

        return statusd

    except Exception as ex:

        batch_end = datetime.now()
        db_session.query(BatchLog).filter(BatchLog.BatchLogID == batch_log_id).update({'End': batch_end, 'IsSuccessful': 0}, synchronize_session=False)

        db_session.commit()
        
        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing myplaid data:', ex)
        
        return statusd

    finally:

        db_session.close()

