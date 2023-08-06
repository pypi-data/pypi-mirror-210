import pandas as pd

from pyplattsapi import plattsapicore

#'https://developer.platts.com/servicecatalog#/EnergyPriceForecast(Beta)/v1/'
api_name = "WORLD REFINERY DATABASE"


def get_price_forecast(symbol: str):
    forecasts_api = (
        f"{plattsapicore.api_url}/energy-price-forecast/v1/prices-short-term"
    )
    filter = "priceSymbol: " + f'"{symbol}"' + "AND categoryName: " + '"Oil"'
    params = {
        "filter": filter,
        "pageSize": 1000,
    }
    try:
        res = plattsapicore.generic_api_call(
            api=forecasts_api, api_name=api_name, params=params
        )
    except:
        filter = "priceSymbol: " + f'"{symbol}"' + "AND categoryName: " + '"NGL"'
        params = {
            "filter": filter,
            "pageSize": 1000,
        }
        res = plattsapicore.generic_api_call(
            api=forecasts_api, api_name=api_name, params=params
        )
    res.index = res.apply(lambda x: pd.to_datetime(f"{x.year}-{x.month}-1"), 1)
    res.index.name = "date"
    return res
