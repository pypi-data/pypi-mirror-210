import pandas as pd

from pyplattsapi import plattsapicore

# https://developer.platts.com/servicecatalog#/Mgodf(Beta)/v1/

api_name = "MONTHLY GLOBAL OIL DEMAND FORECAST"
demand_api = f"{plattsapicore.api_url}/mgodf/v1/demand"
metadata_api = f"{plattsapicore.api_url}/mgodf/v1"


def get_demand(filter, field, groupBy):
    params = {
        "filter": filter,
        "field": field,
        "pageSize": 1000,
        "groupBy": groupBy,
        "page": 1,
    }
    res = plattsapicore.generic_api_call(
        api=demand_api, api_name=api_name, params=params
    )

    if "month" in res.columns and "year" in res.columns:
        res.index = res.apply(lambda x: pd.to_datetime(f"{x.year}-{x.month}-1"), 1)
        res.index.name = "date"
    return res


def get_metadata(
    metadata_endpoint: str, filter: str = None, field: str = None, groupBy: str = None
) -> pd.DataFrame:
    params = {
        "filter": filter,
        "field": field,
        "pageSize": 1000,
        "groupBy": groupBy,
        "page": 1,
    }
    url = f"{metadata_api}/{metadata_endpoint}"
    res = plattsapicore.generic_api_call(api=url, api_name=api_name, params=params)
    return res
