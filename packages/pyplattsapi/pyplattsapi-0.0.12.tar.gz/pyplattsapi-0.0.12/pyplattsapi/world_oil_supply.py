import pandas as pd

from pyplattsapi import plattsapicore

# https://developer.platts.com/servicecatalog#/WorldOilSupply(Beta)/v2/

api_name = "WORLD OIL SUPPLY"
production_api = f"{plattsapicore.api_url}/wos/v2/production"
metadata_api = f"{plattsapicore.api_url}/wos/v2/metadata_endpoint"


def get_production(filter, field, groupBy, scenarioTermId: int = 2):
    params = {
        "filter": filter,
        "scenarioTermId": scenarioTermId,
        "field": field,
        "pageSize": 1000,
        "groupBy": groupBy,
        "page": 1,
    }
    res = plattsapicore.generic_api_call(
        api=production_api, api_name=api_name, params=params
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
    url = metadata_api.replace("metadata_endpoint", metadata_endpoint)
    res = plattsapicore.generic_api_call(api=url, api_name=api_name, params=params)
    return res
