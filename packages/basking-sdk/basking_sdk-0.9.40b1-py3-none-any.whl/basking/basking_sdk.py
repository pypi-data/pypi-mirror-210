# pylint: disable=line-too-long, import-error, invalid-name
"""
Basking.io — Python SDK
"""

import logging
import os
import re

import boto3
import botocore
from botocore.config import Config
from pytz import timezone

from .constant import (
    TIMEOUT_MESSAGE
)
from .graphql_query import GraphqlQuery
from .insight import Insight
from .location import Location
from .occupancy import Occupancy
from .organization import Organization
from .user import User
from .utils import Utils


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class Basking:
    """ Class Basking
    """

    def __init__(self, *args, log_level='WARNING', api_url=None, **kwargs):
        # Setting the logger
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(log_level)

        # cognito
        self.auth_type = 'env_variables'
        config = Config(signature_version=botocore.UNSIGNED)
        self.boto3_client = boto3.client('cognito-idp', os.getenv('BASKING_AWS_REGION', 'eu-central-1'), config=config)
        self.occupancy = Occupancy(basking_obj=self)
        self.location = Location(basking_obj=self)
        self.organization = Organization(basking_obj=self)
        self.graphql_query = GraphqlQuery(basking_obj=self, api_url=api_url)
        self.insight = Insight(basking_obj=self)
        self.user = User(basking_obj=self)
        self.utils = Utils(basking_obj=self)

    def date_obj_to_timestamp_ms(self, date_obj, tz_str):
        """
        converts a date obj into a dateobj with timezone and then into ms for the api

        :param date_obj: datetime object
        :type date_obj: datetime object.
        :param tz_str: timezone
        :type tz_str: str.

        :return: converted datetime in ms
        """

        try:
            tz = timezone(tz_str)
            date_obj_tz = tz.localize(date_obj)
            timestamp = int(date_obj_tz.timestamp())
            self.log.debug('got %s for %s in tz=%s', timestamp, date_obj, tz_str)
            return timestamp
        except Exception as e:
            print(f"error in data_obj_timestamp -- > {e}")
            self.log.error('error on timezone for %s', tz_str)

    # Internal Methods
    @staticmethod
    def check_if_datetime_obj_tz_aware(dateobject):
        """
        check datetime is aware

        :param dateobject: date_time object
        :type dateobject: datetime object.

        :return: True or False
        """

        if dateobject.tzinfo and dateobject.tzinfo.utcoffset(dateobject):
            return True
        return False

    def api_timeout_handler(self, api_data):
        """
        for handle api timeout error coming from graphql_query

        :param api_data: api_data
        :type api_data: dict

        :return: error message

        """
        if 'message' in api_data:
            if api_data['message'] == 'Endpoint request timed out':
                self.log.error(api_data['message'])
                return TIMEOUT_MESSAGE

    def basking_handle_api_return_errors(self, api_return_data):
        """
        checks if there are errors in the return from the API

        :param api_return_data: api return data
        :type api_return_data: dict

        :return: TRUE if has error
        """

        has_errors = False
        if 'errors' in api_return_data:
            self.log.error('Error in query:')
            self.log.error(api_return_data['errors'])
            has_errors = True
        return has_errors
