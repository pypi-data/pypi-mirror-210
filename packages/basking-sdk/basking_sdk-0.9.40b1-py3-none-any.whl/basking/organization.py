# pylint: disable=invalid-name, pointless-string-statement, line-too-long
"""
Basking.io — Python SDK
Organization Class: handles all functionality related to organizations.
"""
import calendar
import json
import logging
from datetime import datetime, date

import pandas as pd


class Organization:
    """
    Organizations describe companies that use Basking.

    The organization class can be accessed as follows
    ::
        basking.organization
    """

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_user_organizations(self, pandify=False):
        """
        Returns a list of organizations that the logged in user has access to.

        Example of use:
        ::
            basking.organization.get_user_organizations(pandify=False)

        Example of returned data:
        ::
            "data": {
                "viewer": {
                    "organizationId": 1,
                    "organizations": [
                        {
                            "id": "1",
                            "name": "Basking Automation GmbH"
                        },
                        {
                            "id": "2",
                            "name": "Organization Name 2"
                        }
                    ]
                }
            }

        :param pandify: if True, returns a Pandas DataFrame. Else, returns a dictionary.
        :type pandify: bool.

        :return: Pandas DataFrame or dictionary

        """

        query = self.basking.graphql_query.get_user_organizations_graphql_query()

        result = self.basking.graphql_query.graphql_executor(query=query, variables={})

        data = json.loads(result)
        if 'message' in data:
            self.basking.api_timeout_handler(data)

        data = data['data']['viewer']['organizations']

        if pandify:
            df = pd.DataFrame(data)
            df.set_index('id', inplace=True)
            return df
        return data

    def get_organization_details(
            self,
            organization_id,
    ):
        """
        Returns the organization details for a given organization id.

        Example of use
        ::
            basking.organization.get_organization_details(
                organization_id=my_id
            )

        :param organization_id: The ID of the organization to query.
        :type organization_id: str.

        :return: organization meta data object.
        """

        if not isinstance(organization_id, str):
            raise ValueError('organization_id_str has to be of type str')
        query, variables = self.basking.graphql_query.get_organization_details_graphql_query(
            organization_id
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
        data = json.loads(result)

        if 'message' in data:
            self.basking.api_timeout_handler(data)

        if 'errors' in data:
            self.log.error(data)
            return data
        # no errors in the api call
        data = data['data']['organization']
        return data

    def get_hoteling_by_org(
            self,
            organization_id:int,
            start_date: date,
            end_date: date,
            pandify=False
    ):
        """
        Returns the hoteling data for the organization.
        Hoteling is a mobility metric that describes movement of employees between offices from an organization.
        You can learn more about this feature under https://basking.io/covid-19/

        Example of use
        ::
            basking.organization.get_hoteling_by_org(
                organization_id=my_id,
                start_unix_timestamp=start_time,
                end_date=end_time,
                pandify=True
            )

        Please note: The elements that have the "to" field empty are currently not used by the basking frontend
        and can thus be droped in the subsequent code.

        Example of returned data
        ::
            {
                "data": {
                    "organization": {
                        "hoteling": [
                            {
                                "from": "Sydney Grosvenor Place",
                                "to": "",
                                "count": 0,
                                "country": "Australia",
                                "countryRegion": "APAC"
                            },
                            {
                                "from": "Calgary 8th Avenue",
                                "to": "",
                                "count": 0,
                                "country": "Canada",
                                "countryRegion": "Canada"
                            }
                        ]
                    }
                }
            }
"""
        query, variables = self.basking.graphql_query.get_hoteling_by_org_graphql_query(
            organization_id,
            start_date,
            end_date
        )

        result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)

        try:
            data = json.loads(result)
            if 'message' in data:
                self.basking.api_timeout_handler(data)
            data = data['data']['organization']['hoteling']
            if pandify:
                df = pd.DataFrame(data)
                return df
            return data
        except TypeError:
            self.log.error("no data found")

    def get_org_locations(
            self,
            organization_id
    ):
        """
           Returns the information of all locations for a given organization that the current user has access to.

           :param organization_id: organization_id
           :type organization_id: int.

           :return: Data of location in json.
        """
        try:
            query, variables = self.basking.graphql_query.get_org_locations_graphql_query(organization_id)
            result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
            data = json.loads(result)
            if not data['data']['locations']:
                self.log.error('no data')
            return data

        except (TypeError, ValueError):
            self.log.error('no data')

    def locations_rank_by_occupancy(
            self,
            organization_id,
            start_date:date,
            end_date:date,
            ranking_metric='average_daily_peak_pct',
            ranking_order="desc",
            pandify=None
    ):

        """
          Ranks all locations for a given organization during the provided period by the metric described in `ranking_metric`. At the moment, the following options are available:
            - `average_daily_peak_pct`: The average of daily peaks is a metric used across the application. It represents the usage of the office at its peak during working days. This is the default and recommended ranking metric.
            - `peak_occupancy_pct`: The highest peak during the period. We recommend not using this metric because the highest peak could be an anomaly and might not be representative.


           :param organization_id: organization_id
           :type organization_id: int.
           :param ranking_metric: take only average_daily_peak_pct and peak_occupancy_pct
           :type ranking_metric: str.
            :param ranking_order: take order of data like ascending aur descending
           :type ranking_order: str.
           :param pandify: if True makes the call return a panda dataframe else return json.
           :type pandify: bool.

           :return: Data frame or array of popular days of visits at organization level.
        """

        possible_ranking_metrics = [
            'average_daily_peak_pct',
            'peak_occupancy_pct'
        ]
        if ranking_metric not in possible_ranking_metrics:
            raise ValueError('Invalid ranking metric. Possible options are %s', possible_ranking_metrics)
        if not ranking_order:
            ranking_order = "desc"
        try:
            main_dict = {}
            org_data = self.get_org_locations(
                organization_id=organization_id
            )
            locations_in_org = org_data['data']['locations']

            for location in locations_in_org:
                building_id = location['id']
                days = location['workingDays']

                daily_data = self.basking.occupancy.get_building_occupancy_stats_daily(
                    building_id=building_id,
                    start_date=start_date,
                    end_date=end_date,
                    pandify=True
                )

                daily_peak_data = []
                for date_d in daily_data.index:
                    df_data = daily_data.query('date')
                    week_day = calendar.day_name[date_d.weekday()]
                    if week_day in days:
                        daily_peak_data.append(df_data.loc[date_d]['occupancy_daily_peak'])
                if len(daily_peak_data) != 0 and location['capacity'] > 0:
                    avg_of_daily_peak = sum(daily_peak_data) / len(daily_peak_data)
                    avg_of_daily_peak_pct = int((avg_of_daily_peak * 100) / location['capacity'])
                    max_val = max(daily_peak_data)
                    max_val_pct = int((max_val * 100) / location['capacity'])
                else:
                    avg_of_daily_peak, avg_of_daily_peak_pct, max_val, max_val_pct = 0, 0, 0, 0

                main_dict.update({building_id: {"building_name": location['name']}})
                if ranking_metric == "average_daily_peak_pct":
                    main_dict[building_id].update({'avg_peak_pct': avg_of_daily_peak_pct})
                elif ranking_metric == "peak_occupancy_pct":
                    main_dict[building_id].update({'max_peak_pct': max_val_pct})
            df = pd.DataFrame.from_dict(main_dict, orient='index')
            df.index.name = 'building_id'
            if ranking_order == 'asc':
                if ranking_metric == "average_daily_peak_pct":
                    sorted_df = df.sort_values(by=['avg_peak_pct'], ascending=[True])
                elif ranking_metric == "peak_occupancy_pct":
                    sorted_df = df.sort_values(by=['max_peak_pct'], ascending=[True])
                sorted_json = sorted_df.to_json(orient='records')
            elif ranking_order == 'desc':
                if ranking_metric == "average_daily_peak_pct":
                    sorted_df = df.sort_values(by=['avg_peak_pct'], ascending=[False])
                elif ranking_metric == "peak_occupancy_pct":
                    sorted_df = df.sort_values(by=['max_peak_pct'], ascending=[False])
                sorted_json = sorted_df.to_json(orient='records')

            if pandify:
                return sorted_df
            return sorted_json
        except (TypeError, KeyError):
            return self.log.error("no data")
