import pandas as pd
import pytest

from pyplattsapi import refining_margins_crude_arbitrage as m


@pytest.mark.parametrize(
    "filter, FrequencyId",
    [
        (
            "marginId:1",
            1,
        ),
        (
            "marginId:1",
            2,
        ),
    ],
)
def test_margins_data(filter: str, FrequencyId: int):  # , groupBy: str):
    res = m.margins_data(filter=filter, FrequencyId=FrequencyId)
    assert isinstance(res, pd.DataFrame)


def test_margins_catalog():
    res = m.margins_catalog()
    assert res is not None
