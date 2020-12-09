from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus


db_conn_str = os.getenv('CONN_STR_MYPLAID')
db_conn_str = quote_plus(db_conn_str)


engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % db_conn_str)


# Create Session
Session = sessionmaker(bind=engine)


class SessionManager(object):
    def __init__(self):
        self.session = Session()

