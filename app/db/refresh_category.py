from datetime import datetime
import os

from numpy import nan as npnan
import pandas as pd
from plaid import Client

from app.db.connection_manager import SessionManager
from app.db.model import Category


def refresh_category(client):
    try:

        now = datetime.now()
        print('|| MSG @', now, '|| refreshing category data')        

        # Initialize DB Session
        db_session = SessionManager().session


        # GET Category
        category_response = client.Categories.get()
        categories = category_response['categories']


        # Write to DB
        for category in categories:

            h = category['hierarchy']

            if len(h) == 1:
                category_hierarchy_1 = h[0]

                db_session.merge(
                    Category(
                        CategoryID=category['category_id'],
                        CategoryGroup=category['group'],
                        CategoryHierarchy1=category_hierarchy_1,
                        CategoryHierarchy2=None,
                        CategoryHierarchy3=None,
                        dModified=datetime.now()
                    )
                )

            if len(h) == 2:
                category_hierarchy_1 = h[0]
                category_hierarchy_2 = h[1]

                db_session.merge(
                    Category(
                        CategoryID=category['category_id'],
                        CategoryGroup=category['group'],
                        CategoryHierarchy1=category_hierarchy_1,
                        CategoryHierarchy2=category_hierarchy_2,
                        CategoryHierarchy3=None,
                        dModified=datetime.now()
                    )
                )

            if len(h) == 3:
                category_hierarchy_1 = h[0]
                category_hierarchy_2 = h[1]
                category_hierarchy_3 = h[2]

                db_session.merge(
                    Category(
                        CategoryID=category['category_id'],
                        CategoryGroup=category['group'],
                        CategoryHierarchy1=category_hierarchy_1,
                        CategoryHierarchy2=category_hierarchy_2,
                        CategoryHierarchy3=category_hierarchy_3,
                        dModified=datetime.now()
                    )
                )


        db_session.commit()

        now = datetime.now()
        print('|| MSG @', now, '|| category data refresh SUCCESS')

        return 0

    except Exception as ex:

        db_session.rollback()

        now = datetime.now()
        print('|| ERR @', now, '|| an error occured while refreshing category data:', ex)

        return 1

    finally:

        db_session.close()

