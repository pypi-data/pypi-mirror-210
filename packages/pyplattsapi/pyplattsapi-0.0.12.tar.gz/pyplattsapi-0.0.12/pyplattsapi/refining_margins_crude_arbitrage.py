import time

import pandas as pd
import requests

from pyplattsapi import plattsapicore

# https://developer.platts.com/servicecatalog#/ArbFlow(Beta)/v1/


api_name = "REFINING MARGINS AND CRUDE ARBITRAGE"
production_api = f"{plattsapicore.api_url}/arbflow/data/v1/margins"


def margins_data(filter: str, FrequencyId: int = 1):
    margins_data_api = f"{plattsapicore.api_url}/arbflow/data/v1/margins-data"
    params = {
        "pageSize": 1000,
        "FrequencyId": FrequencyId,
        "filter": filter,
        "sort": "marginDate:desc",
    }
    res = plattsapicore.generic_api_call(
        margins_data_api, api_name=api_name, params=params
    )
    res.index = res["marginDate"]
    return res


def margins_catalog():
    margins_catalog_api = f"{plattsapicore.api_url}/arbflow/data/v1/margins-catalog"
    params = {"pageSize": 1000}
    response = requests.get(
        url=margins_catalog_api,
        headers=plattsapicore.build_header(api_name),
        params=params,
    )
    d = response.json()
    d["results"]
    df = pd.concat([pd.Series(x) for x in d["results"]], axis=1).T
    return df


def margins_metadata():
    margins_metadata_api = f"{plattsapicore.api_url}/arbflow/data/v1/margins"
    params = {"pageSize": 1000}
    response = requests.get(
        url=margins_metadata_api,
        headers=plattsapicore.build_header(api_name),
        params=params,
    )
    d = response.json()
    d["results"]
    df = pd.concat([pd.Series(x) for x in d["results"]], axis=1).T
    return df
