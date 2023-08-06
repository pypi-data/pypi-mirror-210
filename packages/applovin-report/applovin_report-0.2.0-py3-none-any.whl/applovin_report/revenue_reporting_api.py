import time
import traceback
from datetime import datetime, timedelta
from typing import Iterator

import requests
from pandas import DataFrame


class RevenueReport:
    """
    Detailed documentation for this API can be found at: [Revenue Report API](https://dash.applovin.com/documentation/mediation/reporting-api/max-ad-revenue)
    """

    ENDPOINT = "https://r.applovin.com/maxReport"

    def __init__(self, api_key: str | list[str]):
        """
        Args:
            api_key: API key(s) to use for the report

        Returns:
            None

        Doc Author:
            minhpc@ikameglobal.com
        """
        self.api_key = api_key

    def get_report(
        self,
        start_date: str = None,
        end_date: str = None,
        columns: list[str] = None,
        limit: int = 100000,
        max_retries: int = 3,
        retry_interval: int = 30,
        **kwargs,
    ) -> DataFrame:
        """
        Retrieve a report from the MAX Revenue Report API.


        Args:
            start_date: YYYY-MM-DD, within the last 45 days
            end_date: YYYY-MM-DD, within the last 45 days
            columns: List of columns to include in the report
            limit: Set the number of rows to return
            max_retries: Set the number of retries
            retry_interval: Set the number of seconds to wait between retries
            **kwargs: Additional parameters to pass to the API

        Returns:
            A pandas DataFrame containing the report data

        Doc Author:
            minhpc@ikameglobal.com
        """
        if not start_date or not end_date:
            start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        params = {
            "api_key": self.api_key,
            "start": start_date,
            "end": end_date,
            "columns": ",".join(columns),
            "format": "json",
            "limit": limit,
            **kwargs,
        }

        for i in range(max_retries + 1):
            response = requests.get(url=RevenueReport.ENDPOINT, params=params)

            if response.status_code == 200:
                return DataFrame(response.json()["results"])
            else:
                print(f"Retrying... ({i + 1}/{max_retries})")
                time.sleep(retry_interval)

        print(traceback.format_exc())
        raise Exception(f"Error: {response.status_code}")

    def get_report_batch(
        self,
        start_date: str = None,
        end_date: str = None,
        columns: list[str] = None,
        batch_size: int = 100000,
        max_retries: int = 3,
        retry_interval: int = 30,
        **kwargs,
    ) -> Iterator[DataFrame]:
        """
        Retrieve a report from the MAX Revenue Report API in batches.

        Args:
            start_date: YYYY-MM-DD, within the last 45 days
            end_date: YYYY-MM-DD, within the last 45 days
            columns: List of columns to include in the report
            batch_size: Number of rows to return per batch
            max_retries: Number of retries
            retry_interval: Number of seconds to wait between retries
            **kwargs: Additional parameters to pass to the API

        Returns:
            A generator that yields a pandas DataFrame containing the report data

        Doc Author:
            minhpc@ikameglobal.com
        """
        if not start_date or not end_date:
            start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        offset = 0
        has_next_batch = True
        while has_next_batch:
            params = {
                "api_key": self.api_key,
                "start": start_date,
                "end": end_date,
                "columns": ",".join(columns),
                "format": "json",
                "offset": offset,
                "limit": batch_size,
                **kwargs,
            }

            response = None
            for i in range(max_retries + 1):
                response = requests.get(url=RevenueReport.ENDPOINT, params=params)
                if response.status_code == 200:
                    break
                print(f"Retrying... ({i + 1}/{max_retries})")
                time.sleep(retry_interval)
            if response.status_code != 200:
                print(traceback.format_exc())
                raise Exception(f"Error: {response.status_code}\nLast offset: {offset}\nBatch size: {batch_size}")

            results = response.json()["results"]
            has_next_batch = len(results) == batch_size
            offset += batch_size
            yield DataFrame(results)
