# pylint: disable=line-too-long, invalid-name, too-many-arguments, too-many-locals

"""
Basking.io — Python SDK
- Insight Class: handles all functionality related to insight.
"""

import json
import logging
from datetime import date
from typing import Union, List

import pandas
import pandas as pd


class Insight:
    """insight class"""

    def __init__(self, basking_obj):
        self.basking = basking_obj
        self.log = logging.getLogger(self.__class__.__name__)
        basking_log_level = logging.getLogger(self.basking.__class__.__name__).level
        self.log.setLevel(basking_log_level)

    def get_location_insights(
            self,
            building_id: str,
            start_date: date,
            end_date: date,
            pandify=True
    ) -> Union[pandas.DataFrame, List[dict]]:
        """
        Returns insights data for a given location
        """
        start_timestamp = self.basking.utils.convert_timestamp_to_building_timezone(building_id, start_date)
        end_timestamp = self.basking.utils.convert_timestamp_to_building_timezone(building_id, end_date)

        try:
            query, variables = self.basking.graphql_query.get_insight_graphql_query(building_id=building_id,
                                                                                    start_date=start_timestamp,
                                                                                    end_date=end_timestamp)
            result = self.basking.graphql_query.graphql_executor(query=query, variables=variables)
            data = json.loads(result)
            if 'message' in data:
                self.basking.api_timeout_handler(data)

            if 'errors' in data:
                self.log.error('Error in query:')
                self.log.error(data['errors'])
                return data

            # here we can assume we have no errors
            data['data']['getBuildingInsights']['staffAllocationIncreasePct'] = 100 * (
                    data['data']['getBuildingInsights']['staffAllocationIncrease'] - 1
            )
            if pandify:
                df = pd.DataFrame.from_dict(data['data']['getBuildingInsights'], orient='index').T
                return df
            return data
        except TypeError:
            self.log.error('invalid data')
