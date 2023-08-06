from __future__ import annotations

import logging

from dbnomics import fetch_series


def test_fetch_series_with_filter_on_one_series_with_filter_parameter_error(
    caplog,
) -> None:
    filters = [
        {
            "code": "interpolate",
            "parameters": {"foo": "bar"},
        }
    ]
    with caplog.at_level(logging.INFO):
        df = fetch_series(
            "AMECO",
            "ZUTN",
            "DEU.1.0.0.0.ZUTN",
            filters=filters,
        )
    assert all(df.filtered == False)  # noqa: == is a Pandas operator
    dbnomics_log_records = [record for record in caplog.records if record.name == "dbnomics"]
    assert len(dbnomics_log_records) == 1
    assert dbnomics_log_records[0].levelname == "ERROR"
    assert "Error with filter parameters" in dbnomics_log_records[0].message


def test_fetch_series_with_filter_on_one_series_with_wrong_frequency(
    caplog,
) -> None:
    filters = [
        {
            "code": "aggregate",
            "parameters": {"frequency": "annual"},
        }
    ]
    with caplog.at_level(logging.INFO):
        df = fetch_series(
            "AMECO",
            "ZUTN",
            "DEU.1.0.0.0.ZUTN",
            filters=filters,
        )
    assert all(df.filtered == False)  # noqa: == is a Pandas operator
    dbnomics_log_records = [record for record in caplog.records if record.name == "dbnomics"]
    assert len(dbnomics_log_records) == 1
    assert dbnomics_log_records[0].levelname == "ERROR"
    assert "Annual is already the lowest frequency" in dbnomics_log_records[0].message


def test_fetch_series_with_filter_on_one_series_with_filter_error(
    caplog,
) -> None:
    filters = [
        {
            "code": "foo",
            "parameters": {},
        }
    ]
    with caplog.at_level(logging.INFO):
        df = fetch_series(
            "AMECO",
            "ZUTN",
            "DEU.1.0.0.0.ZUTN",
            filters=filters,
        )
    assert all(df.filtered == False)  # noqa: == is a Pandas operator
    dbnomics_log_records = [record for record in caplog.records if record.name == "dbnomics"]
    assert len(dbnomics_log_records) == 1
    assert dbnomics_log_records[0].levelname == "ERROR"
    assert "Filter not found" in dbnomics_log_records[0].message
