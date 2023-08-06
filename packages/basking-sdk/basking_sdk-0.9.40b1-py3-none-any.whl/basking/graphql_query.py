# pylint: disable=invalid-name
"""
Basking.io — Python SDK
- Graphql Query Class: handles all graphql queries.
"""
import logging
import os
import re
import urllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import Optional
from urllib.error import HTTPError

import backoff
from graphqlclient import GraphQLClient

from .constant import BASKING_API_URL
from .queries import *


@dataclass
class Authentication:
    AccessToken: str
    ExpiresIn: int
    TokenType: str
    IdToken: str
    RefreshToken: str = field(default=None)
    expires: datetime = field(init=False)

    def __str__(self):
        return f"Auth token (expires: {self.expires})"


class GraphqlQuery:
    """
    # TODO: Deprecate all static methods in favor of a query class
    graphql_query class
    """
    _ggraphql_client = None
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

    def __init__(self, basking_obj, api_url=None):
        self.basking = basking_obj
        self.basking_api_url = api_url if api_url else BASKING_API_URL
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)
        self.log.debug('Started Basking SDK in debugging level using %s', self.basking_api_url)
        self._auth_client = os.getenv('BASKING_AUTH_CLIENT', '3ehjj0o7hel3dpcmr8uu1ncckd')
        self._graphql_client = GraphQLClient(self.basking_api_url)
        self._auth = self.authenticate()

    def _authenticate(self):
        response = self.basking.boto3_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': os.environ['BASKING_USERNAME'],
                'PASSWORD': os.environ['BASKING_USER_PASSWORD']
            },
            ClientId=self._auth_client,
        )
        return Authentication(**response['AuthenticationResult'])

    def _refresh_token(self):
        _refresh_token = self._auth.RefreshToken
        response = self.basking.boto3_client.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={"REFRESH_TOKEN": _refresh_token},
            ClientId=self._auth_client,
        )
        auth = Authentication(**response['AuthenticationResult'])
        auth.RefreshToken = _refresh_token
        return auth

    def authenticate(self) -> Optional[Authentication]:
        """
         Authenticates with AWS Cognito. Sets token expiry to T-10s for safety
         Will attempt refreshing the token first, if possible
         Handling authentication errors is the callers responsibility
        """
        try:
            auth = self._refresh_token()
        except:
            auth = self._authenticate()
        finally:
            auth.expires = datetime.now() + timedelta(seconds=auth.ExpiresIn - 10)
            self._graphql_client.inject_token(auth.IdToken)
            return auth

    @backoff.on_exception(backoff.expo, urllib.error.HTTPError, max_tries=8)
    def graphql_executor(self, query: str, variables: dict) -> Optional[dict]:
        try:
            if self._auth.expires <= datetime.now():
                self.authenticate()

            try:
                query_name = re.findall(r'\W*\w+ (.+?)\(.*', query.strip())[0]
            except Exception:
                query_name = 'uknnown_at_this_time'
            self.log.info(f"Executing {query_name}({variables})")
            return self._graphql_client.execute(
                query=query,
                variables=variables
            )
        except AttributeError:
            self.log.error("cannot execute query", exc_info=True)
        except HTTPError:
            self.log.error('API server error', exc_info=True)

    @staticmethod
    def get_building_occupancy_stats_daily_graphql_query(building_id, start_date, end_date, capacity_type=None) -> (
            str, dict):
        """graphql query for get_building_occupancy_stats_daily function
        :return: graphql query, variables
        """
        variables = {
            'id': str(building_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        if capacity_type:
            variables['capacityType'] = capacity_type
            query = GET_LOCATION_STATS_DAILY
        else:
            query = '\n'.join(filter(lambda x: 'capacityType' not in x, GET_LOCATION_STATS_DAILY.splitlines()))

        return query, variables

    @staticmethod
    def get_building_graphql_query(building_id):
        """graphql query for get_building function

        :param building_id: building_id
        :type building_id: str.

        :return: graphql query, variables

        """
        variables = {
            'buildingid': str(building_id)
        }
        return GET_LOCATION, variables

    @staticmethod
    def get_building_occupancy_hourly_pagination_graphql_query(
            building_id,
            start_date: date,
            end_date: date,
            capacity_type=None
    ) -> (str, dict):
        """graphql query and variables for _get_building_occupancy_hourly_pagination function
        """
        variables = {
            'id': str(building_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
            "floorAreaId": 0,
        }

        if capacity_type:
            variables['capacityType'] = capacity_type
            query = GET_LOCATION_OCCUPANCY_HOURLY
        else:
            query = '\n'.join(filter(lambda x: 'capacityType' not in x, GET_LOCATION_OCCUPANCY_HOURLY.splitlines()))

        return query, variables

    @staticmethod
    def get_floor_heatmap_kpi_graphql_query(
            basking_floor_id,
            start_date: date,
            end_date: date
    ) -> (str, dict):

        """graphql query for get_floor_heatmap_kpi function
        """

        variables = {
            'floorId': str(basking_floor_id),
            'startDate': start_date.strftime('%s'),
            'endDate': end_date.strftime('%s')
        }
        return GET_FLOOR_HEATMAP_KPI, variables

    @staticmethod
    def get_floor_meta_info_graphql_query(basking_floor_id):
        """graphql query for get_floor_meta_info function

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.

        :return: graphql query, variables

        """

        variables = {
            'basking_floor_id': str(basking_floor_id)
        }
        return GET_FLOOR_METADATA, variables

    @staticmethod
    def get_floor_areas_for_floor_graphql_query(basking_floor_id):
        """graphql query for get_floor_areas_for_floor function

        :param basking_floor_id: basking_floor_id
        :type basking_floor_id: str.

        :return: graphql query, variables

        """
        variables = {
            'basking_floor_id': str(basking_floor_id)
        }
        return GET_FLOOR_AREAS, variables

    @staticmethod
    def get_adjusted_capacity_graphql_query(building_id):
        """graphql query for get_adjusted_capacity function

        :param building_id: building_id
        :type building_id: str.

        :return: graphql query, variables

        """

        variables = {
            'locationId': str(building_id),
        }
        return GET_ADJUSTED_CAPACITY, variables

    @staticmethod
    def get_user_buildings_graphql_query():
        """graphql query for get_user_buildings function

        :return: query
        """
        return GET_USER_LOCATIONS

    @staticmethod
    def get_location_duration_of_visits_graphql_query(building_id, start_date, end_date, capacity_type=None) -> (
    str, dict):
        """graphql query for get_duration_of_visits_histogram function
        """

        variables = {
            'id': str(building_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        if capacity_type:
            variables['capacityType'] = capacity_type
            query = GET_LOCATION_VISIT_DURATION
        else:
            query = '\n'.join(filter(lambda x: 'capacityType' not in x, GET_LOCATION_VISIT_DURATION.splitlines()))

        return query, variables

    @staticmethod
    def get_location_frequency_of_visits_graphql_query(building_id, start_date, end_date, capacity_type=None) -> (
    str, dict):
        """graphql query for get_frequency_of_visits_histogram function
        """
        variables = {
            'id': str(building_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        if capacity_type:
            variables['capacityType'] = capacity_type
            query = GET_LOCATION_VISIT_FREQ
        else:
            query = '\n'.join(filter(lambda x: 'capacityType' not in x, GET_LOCATION_VISIT_FREQ.splitlines()))

        return query, variables

    @staticmethod
    def get_hoteling_by_org_graphql_query(organizationid: int, start_date: date, end_date: date) -> (str, dict):
        """graphql query for get_hoteling_by_org function
        """
        variables = {
            'id': str(organizationid),
            'startDate': start_date.strftime('%s'),
            'endDate': end_date.strftime('%s'),
        }
        return GET_ORG_HOTELING, variables

    @staticmethod
    def get_organization_details_graphql_query(organization_id_str):
        """graphql query for get_organization function

        :param organization_id_str: organizationid
        :type organization_id_str: str.

        :return: graphql query, variables

        """

        variables = {
            'id': organization_id_str,
        }
        return GET_ORG_DETAILS, variables

    @staticmethod
    def get_user_organizations_graphql_query():
        """
        graphql query for get_user_organizations function.

        :return: query.
        """

        return GET_USER_ORGS

    @staticmethod
    def get_location_popular_days_of_visits_graphql_query(
            building_id,
            start_date,
            end_date,
            capacity_type=None,
    ) -> (str, dict):
        """graphql query for get_location_popular_days_of_visits


        """
        variables = {
            "id": str(building_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        if capacity_type:
            variables['capacityType'] = capacity_type
            query = GET_LOCATION_POPULAR_VISIT_DAYS
        else:
            query = '\n'.join(filter(lambda x: 'capacityType' not in x, GET_LOCATION_POPULAR_VISIT_DAYS.splitlines()))

        return query, variables

    @staticmethod
    def get_organization_frequency_of_visits_graphql_query(organization_id, start_date, end_date) -> (str, dict):
        """graphql query for het_frequency_of_visits
        """
        variables = {
            "id": str(organization_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }

        return GET_ORG_VISIT_FREQ, variables

    @staticmethod
    def get_organization_duration_of_visits_graphql_query(organization_id, start_date, end_date) -> (str, dict):
        """graphql query for het_frequency_of_visits
        """

        variables = {
            "id": str(organization_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }

        return GET_ORG_VISIT_DURATION, variables

    @staticmethod
    def get_insight_graphql_query(building_id: str, start_date: datetime, end_date: datetime) -> (str, dict):
        """get_insight_data graphql query

        """
        variables = {
            "id": building_id,
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        return GET_INSIGHTS, variables

    @staticmethod
    def get_organization_popular_days_of_visits_graphql_query(organization_id, start_date, end_date) -> (str, dict):
        """graphql query for get_organization_popular_days_of_visits
        """
        variables = {
            "id": str(organization_id),
            'from': start_date.strftime(GraphqlQuery.DATE_FORMAT),
            'to': end_date.strftime(GraphqlQuery.DATE_FORMAT),
        }
        return GET_ORG_POPULAR_VISIT_DAYS, variables

    @staticmethod
    def get_org_locations_graphql_query(organization_id):
        """graphql query for get_org_location

        :param organization_id: organization_id
        :type organization_id: int.

        :return: graphql query, variables
        """
        variables = {
            "id": int(organization_id)
        }
        return GET_ORG_LOCATIONS, variables

    @staticmethod
    def get_user_graphql_query():
        """
        graphql query for get_user function.

        :return: query.
        """
        return GET_USER
