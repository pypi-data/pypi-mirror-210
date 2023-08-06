# pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals

"""
Basking.io — Python SDK
- User Class: handles all functionality related to users.
"""

import json
import logging
import pandas as pd


class User:
    """ User class """

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_user(self, pandify=False):
        """
        Returns user information that is logged in

        Example of use:
        ::
            basking.user.get_user(pandify=False)

        Example of returned data:
        ::

            'data': {
                'viewer':
                    {
                        'id': '3a9e3082-a5c9-47ff-b741-812ee1ec3af7',
                        'email': 'demo@gmail.com',
                        'name': 'demo',
                        'firstName': 'demo',
                        'lastName': '',
                        'primaryOrgId': 123,
                        'createdAt': '2022-01-25T13:04:44Z',
                        'measurementUnits': 'Metric',
                        'currency': 'EUR',
                        'isAdjCapacityNormalizationEnabled': False, '
                        disableQueryCache': False
                    }
                }


        :param pandify: if True, returns a Pandas DataFrame. Else, returns a dictionary.
        :type pandify: bool.

        :return: Pandas DataFrame or dictionary

        """

        query = self.basking.graphql_query.get_user_graphql_query()

        result = self.basking.graphql_query.graphql_executor(query=query, variables={})

        data = json.loads(result)

        if 'message' in data:
            self.basking.api_timeout_handler(data)

        data = data['data']['viewer']

        if pandify:
            df = pd.DataFrame(data)
            df.set_index('id', inplace=True)
            return df
        return data
