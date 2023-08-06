#!/usr/bin/env python
"""Tests for `applovin_report` package."""
# pylint: disable=redefined-outer-name

import os
from datetime import datetime, timedelta

import pandas as pd
import pytest

from applovin_report import RevenueReport


@pytest.fixture
def api_key():
    api_key = os.environ.get("APPLOVIN_API_KEY", None)
    assert api_key is not None
    return api_key


def test_revenue_report(api_key):
    report = RevenueReport(api_key=api_key)

    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = start_date

    _columns = [
        "day",
        "package_name",
        "platform",
        "country",
        "application",
        "max_ad_unit_test",
        "max_ad_unit_id",
        "network",
        "network_placement",
        "ad_format",
        "attempts",
        "responses",
        "fill_rate",
        "impressions",
        "estimated_revenue",
        "ecpm",
    ]

    result = report.get_report(
        start_date=start_date,
        end_date=end_date,
        columns=_columns,
        filter_package_name="com.citybay.farming.citybuilding",
    )

    assert len(result) > 0


def test_revenue_report_batch(api_key):
    report = RevenueReport(api_key=api_key)

    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = start_date

    _columns = [
        "day",
        "package_name",
        "platform",
        "country",
        "application",
        "max_ad_unit_test",
        "max_ad_unit_id",
        "network",
        "network_placement",
        "ad_format",
        "attempts",
        "responses",
        "fill_rate",
        "impressions",
        "estimated_revenue",
        "ecpm",
    ]

    result = pd.DataFrame(columns=_columns)
    for x in report.get_report_batch(
        start_date=start_date,
        end_date=end_date,
        columns=_columns,
        batch_size=100000,
        filter_package_name="com.citybay.farming.citybuilding",
    ):
        result = pd.concat([result, x], ignore_index=True)

    assert len(result) > 0
