import pandas as pd

from pyplattsapi import plattsapicore

api_name = "WORLD REFINERY DATABASE"
runs_api = f"{plattsapicore.api_url}/odata/refinery-data/v2/Runs"
outages_api = f"{plattsapicore.api_url}/refinery-data/v1/outage-alerts"
capacity_api = f"{plattsapicore.api_url}/odata/refinery-data/v2/Capacity"
refinery_api = f"{plattsapicore.api_url}/odata/refinery-data/v2/Refineries"
margins_api = f"{plattsapicore.api_url}/odata/refinery-data/v2/margins"
outage_alerts_api = f"{plattsapicore.api_url}/refinery-data/v1/outage-alerts"


def get_runs(filter: str, field: str = None, groupBy: str = None):
    params = {
        "$filter": filter,
        "pageSize": 1000,
        "groupBy": groupBy,
    }
    res = plattsapicore.generic_odata_call(
        api=runs_api, api_name=api_name, params=params
    )

    qmap = {1: 1, 2: 4, 3: 7, 4: 10}
    res.index = res.apply(
        lambda x: pd.to_datetime(f"{x.Year}-{qmap.get(x.Quarter)}-1"), 1
    )
    res.index.name = "date"
    return res


def get_refineries(filter: str, groupBy: str = None):
    params = {
        "$filter": filter,
        "pageSize": 1000,
        "groupBy": groupBy,
    }
    res = plattsapicore.generic_odata_call(
        api=refinery_api, api_name=api_name, params=params
    )
    return res


def get_outages(filter):
    params = {
        "pageSize": 1000,
        "filter": filter,
        "page": 1,
    }
    res = plattsapicore.no_token_api_call(
        api=outages_api, api_name=api_name, params=params
    )
    df = res["alerts"].apply(lambda col: col[0]).apply(pd.Series)
    res.drop(["alerts"], inplace=True, axis=1)
    res = pd.concat([res, df], axis=1)
    res["startDate"] = pd.to_datetime(res["startDate"], format="%Y-%m-%d")
    res["endDate"] = pd.to_datetime(res["endDate"], format="%Y-%m-%d")
    return res


def get_margins(filter):
    params = {
        "pageSize": 1000,
        "filter": filter,
        "page": 1,
    }
    res = plattsapicore.generic_odata_call(
        api=margins_api, api_name=api_name, params=params
    )
    return res


def create_timeseries(res):
    df1 = pd.DataFrame()
    for index, row in res.iterrows():
        row = tar_to_timeseries(row["outageVol_MBD"], row["startDate"], row["endDate"])
        df1 = pd.concat([df1, row], axis=1)
    df1 = df1.sum(axis=1)
    df1 = df1.rename("capacityOffline")
    df1 = df1.to_frame()
    return df1


def tar_to_timeseries(taramount, startdate, enddate, tarname=None):
    dr = pd.date_range("01/01/2000", "12/01/2030")
    ser = pd.Series(0, index=dr)
    ser[startdate:enddate] = taramount
    ser.name = tarname
    return ser


def get_capacity(filter):
    apply = f"filter({filter})/aggregate(Mbcd with sum as SumMbcd)"

    params = {"pageSize": 1000, "page": 1, "$apply": apply}
    res = plattsapicore.generic_odata_call(
        api=capacity_api, api_name=api_name, params=params
    )
    res = res.loc[0]["SumMbcd"]
    return res


def getlatest(a):
    latestalert = [x for x in a if x["isLatest"] == True][0]
    return latestalert


def get_outage_alert(filter: str = None):
    params = {
        "pageSize": 1000,
        "filter": filter,
        "page": 1,
    }
    res = plattsapicore.no_token_api_call(
        api=outage_alerts_api, api_name=api_name, params=params
    )
    res = pd.merge(
        res,
        res.apply(lambda x: pd.Series(getlatest(x.alerts)), axis=1),
        left_index=True,
        right_index=True,
    )
    return res
