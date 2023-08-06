import pandas as pd
import pytest

from pyplattsapi import global_oil_demand


@pytest.mark.parametrize(
    "filter, field, groupBy",
    [
        (
            'countryname:"Italy" and productName:"Naphtha"',
            None,
            None,
        ),
        (
            'countryname:"Saudi Arabia" and productName:"Naphtha"',
            "sum(value)",
            "countryName, year, month",
        ),
    ],
)
def test_get_demand(filter: str, field: str, groupBy: str):
    res = global_oil_demand.get_demand(filter=filter, field=field, groupBy=groupBy)
    assert isinstance(res, pd.DataFrame)


@pytest.mark.parametrize(
    "metadata_endpoint, filter, field, groupBy",
    [
        (
            "countries",
            None,
            None,
            None,
        ),
    ],
)
def test_get_metadata(metadata_endpoint: str, filter: str, field: str, groupBy: str):
    res = global_oil_demand.get_metadata(
        metadata_endpoint=metadata_endpoint, filter=filter, field=field, groupBy=groupBy
    )
    assert isinstance(res, pd.DataFrame)
