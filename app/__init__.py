import base64
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from numpy import nan as npnan
import pandas as pd
import plaid
from pprint import pprint
import sqlalchemy

from app.db.model import AccessToken, Account, Balance, Category, Institution, Transaction
from app.db.connection_manager import SessionManager
from app.db.myplaid_data_refresh import RefreshAll
from app.utilities.json_serialize_helper import json_serial


# CONFIG #

db_conn_str = os.getenv('CONN_STR_MYPLAID')
db_conn_str = quote_plus(db_conn_str)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % db_conn_str
db = SQLAlchemy(app)
db_session = db.session
port = 8080

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_sSECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions,assets').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment=PLAID_ENV, api_version='2020-09-14')


# APP #

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/accounts/create')
def accounts_create():
    return render_template('link-create.html')


@app.route('/accounts/update')
def accounts_update():
    return render_template('link-update.html')


@app.route('/api/addAccount', methods=['POST'])
def add_account():

    try:

        # GET access_token
        public_token = request.get_json()
        exchange_response = client.Item.public_token.exchange(public_token)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # GET accounts
        accounts_response = client.Accounts.get(access_token)
        accounts = accounts_response['accounts']

        # GET institution
        ### TO DO ##
        ### There should be a check here to see if the instituion_id is already in the db
        ###
        institution_id = accounts_response['item']['institution_id']
        institution_response = client.Institutions.get_by_id(institution_id, PLAID_COUNTRY_CODES)
        institution_name = institution_response['institution']['name']

        # Create Record in [dbo].[Institution]
        db.session.add(
            Institution(
                InstitutionID=institution_id,
                InstitutionName=institution_name
            )
        )

        db_session.flush()

        # INSERT [dbo].[AccessToken]
        db.session.add(
            AccessToken(
                AccessToken=access_token,
                ItemID=item_id,
                Environment='sandbox',
                InstitutionID=institution_id
            )
        )

        db_session.flush()


        # INSERT [dbo].[Account]
        for account in accounts:
            db.session.add(
                Account(
                    AccountID=account['account_id'],
                    AccessToken=access_token,
                    Mask=account['mask'],
                    Name=account['name'],
                    OfficialName=account['official_name'],
                    AccountType=account['type'],
                    AccountSubType=account['subtype']
                )
            )

        db_session.flush()

        # GET Balance

        balance_response = client.Accounts.balance.get(access_token=access_token)

        balance = balance_response['accounts']

        # Format Balance Data
        df_balance_data = pd.DataFrame(data=balance)
        df_balance_data = df_balance_data.fillna(npnan).replace([npnan], [None])

        # INSERT [dbo].[Balance]
        for index,row in df_balance_data.iterrows():
            db.session.add(
                Balance(
                    AccountID=row['account_id'],
                    CurrentBalance=row['balances']['current'],
                    AvailableBalance=row['balances']['available'],
                    BalanceLimit=row['balances']['limit'],
                    ISOCurrencyCode=row['balances']['iso_currency_code'],
                    UnofficialCurrencyCode=row['balances']['unofficial_currency_code']
                )
            )

        db_session.commit()

        print('POST api/addAccount SUCCESSFULL')

        return jsonify(exchange_response)

    except plaid.errors.PlaidError as e:

        print('POST /api/addAccount ERROR')

        return jsonify(format_error(e))


@app.route('/api/createLinkToken', methods=['POST'])
def create_link_token():
    try:
        configs = {
            'user': {
                'client_user_id': 'test-user-id'
            }, # This should correspond to a unique id for the current user.
            'products': ['transactions'],
            'client_name': 'myplaid_dev',
            'country_codes': ['US'],
            'language': 'en',
            'link_customization_name': 'sandbox'
        }

        response = client.LinkToken.create(configs)
        link_token = response['link_token']

        print('POST /api/createLinkToken SUCCESSFULL')

        return jsonify(link_token)

    except plaid.errors.PlaidError as e:

        print('POST /api/createLinkToken/ ERROR')

        return jsonify(format_error(e))


@app.route('/api/getAccounts', methods=['GET'])
def get_account():
        query_access_token = db_session.query(AccessToken.AccessToken, Institution.InstitutionName).join(Institution).all()

        resp_l = []
        for a in query_access_token:
            item_response = client.Item.get(access_token=a[0])
            resp_l.append([a[1], item_response])

        response = {'response': []}

        d = {}
        for i in resp_l:
            ins_name = i[0]
            d[i[0]] = i[1]['item']

        for i in d:
            wd = {}
            ins_name = i
            wd = {ins_name: d[i]}
            response['response'].append(wd)

        response = json.dumps(response)

        return jsonify(response)


@app.route('/api/institutions')
def get_access_token():

    query_access_token = db_session.query(Institution.InstitutionName).all()

    query_access_token_keys = query_access_token[0].keys()
    
    d = {'institutions': []}
    for key in query_access_token_keys:
        for r in query_access_token:
            d2 = {}
            d2[key] = r[0]
            d['institutions'].append(d2)

    response = json.dumps(d)

    return jsonify(response)


@app.route('/api/refreshUserData', methods=['POST'])
def refresh_user_data():
    rc = 1
    try:

        statusd = RefreshAll(client, db_session)
        
        response = {
            'response': [
                {
                    'status': 'ok'
                },
                {
                    'message': 'myplaid data refresh completed'
                },
                {
                    'refresh_status': statusd
                }
            ]
        }

        return jsonify(response)

    except Exception as e:
        
        print(e)
        
        response =  {
            'response': [
                {
                    'status': 'error'
                },
                {
                    'message': e
                },
                {
                    'refresh_status': statusd
                }
            ]
        }

        return jsonify(response)


@app.route('/api/updateLinkToken', methods=['POST'])
def update_link_token():

    try:
    #     ############################################
    #     ### USE WHEN USER LOGINS ARE IMPLEMENTED ###
    #     ############################################
    #     # \/                                    \/ #

    #     # parser_link_token = reqparse.RequestParser()
    #     # parser_link_token.add_argument('user_id', required=True)

    #     # args = parser_link_token.parse_args()
    #     # user_id = args['user_id']

    #     # /\                                    /\ #
    #     ############################################

        data = request.get_json()
        institution_name = data['institution_name']
        query_get_access_token = db_session.query(AccessToken.AccessToken).join(Institution).filter(Institution.InstitutionName == institution_name).one()
        access_token = query_get_access_token[0]

        client.Sandbox.item.reset_login(access_token)
        
        configs = {
            'user': {
                'client_user_id': 'test-user-id',
            }, # This should correspond to a unique id for the current user.
            'client_name': 'myplaid_dev',
            'country_codes': ['US'],
            'language': 'en',
            'access_token': access_token,
            'link_customiztion_name': 'sandbox'
        }

        response = client.LinkToken.create(configs)
        link_token = response['link_token']

        response = {'link_token': [{'token': link_token}]}
        
        print('POST /api/updateLinkToken SUCCESSFULL')

        return jsonify(link_token)

    except plaid.errors.PlaidError as e:

        print('POST /api/updateLinkToken ERROR')

        return jsonify(format_error(e))


def format_error(e):
    error_message = {'error': [
        {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message}]}
    return error_message

