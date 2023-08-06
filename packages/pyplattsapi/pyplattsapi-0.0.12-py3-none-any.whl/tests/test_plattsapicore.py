import pytest
from pyplattsapi import plattsapicore


def test_get_access_token():
    api_dataset = "WORLD OIL SUPPLY"
    res = plattsapicore.get_access_token(api_dataset=api_dataset)
    print(res)
    assert res is not None


def test_build_header():
    res = plattsapicore.build_header(api_dataset="WORLD OIL SUPPLY")
    assert "Authorization" in res


#
#
# def test_get_capacity_changes_by_country():
#     res = pyplattsapi.world_refinery_database.getCountryCapacityChangesTimeSeries('China')
#     assert 'Mbdc' in res.columns
#     assert 'Mmtcd' in res.columns
#     assert 'Mmtcy' in res.columns
#
#
# def test_get_yearly_runs_by_country():
#     res = pyplattsapi.world_refinery_database.getCountryYearlyRunsTimeSeries('China')
#     assert 'Mbdc' in res.columns
#     assert 'Mmtcd' in res.columns
#     assert 'Mmtcy' in res.columns
#
#
# def test_get_yearly_margins_by_type():
#     res = pyplattsapi.world_refinery_database.getMarginsbyType('Dated Brent NWE Cracking')
#     assert 'Date' in res.columns
#     assert 'Margin' in res.columns
#
#
# def test_us_inventories_by_product():
#     res = pyplattsapi.oil_inventory.getUSInventoriesByProduct('Central Atlantic Distillate')
#     assert 'Date' in res.columns
#     assert 'Volume' in res.columns
#
#
# def test_us_imports_by_product():
#     res = pyplattsapi.oil_inventory.getUSImportsByProduct('Fuel Oil')
#     assert 'ArrivalDate' in res.columns
#     assert 'Volume' in res.columns
#
#
# def test_us_crude_exports():
#     res = pyplattsapi.oil_inventory.getUSCrudeExports()
#     assert 'EIAWeekEnding' in res.columns
#     assert 'ForecastType' in res.columns
#     assert 'Volume_MBD' in res.columns
