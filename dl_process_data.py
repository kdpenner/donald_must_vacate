import os
import sys
from datetime import date, timedelta
import requests
import io
import json
from functools import reduce
import pandas as pd
from sodapy import Socrata
import numpy as np


def make_url_dc(offset=timedelta()):
    date_ = date.today() - offset
    month = date_.strftime("%B-")
    dayofmonth = date_.strftime("%d")
    dayofmonth = dayofmonth.lstrip("0")
    year = date_.strftime("-%Y")
    date_str = month + dayofmonth + year
    base_url_dc = (r"https://coronavirus.dc.gov/sites/default/files/dc/sites/"
                   "coronavirus/page_content/attachments/")
    fname_dc = "DC-COVID-19-Data-for-" + date_str + ".xlsx"
    full_url_dc = base_url_dc + fname_dc
    return full_url_dc


# Virginia is professional

apptoken = os.environ.get("VDH_APPTOKEN")

client = Socrata("data.virginia.gov", apptoken)

results_cases = client.get("bre9-aqqr", where=(
  "vdh_health_district == 'Arlington' OR vdh_health_district == 'Fairfax' "
  "OR vdh_health_district == 'Alexandria' OR vdh_health_district == 'Loudoun' "
  "OR vdh_health_district == 'Prince William'"),
  select="total_cases, vdh_health_district, report_date", limit=1000000)

results_tests = client.get("3u5k-c2gr", where=(
  "health_district == 'Arlington' OR health_district == 'Fairfax' "
  "OR health_district == 'Alexandria' OR health_district == 'Loudoun' "
  "OR health_district == 'Prince William'"),
  select="number_of_pcr_testing, number_of_antigen_testing_encounters, "
  "lab_report_date", limit=1000000)

client.close()

df_va_cases = pd.DataFrame.from_records(results_cases)
df_va_tests = pd.DataFrame.from_records(results_tests)

df_va_tests["lab_report_date"].loc[
    df_va_tests["lab_report_date"] == "Not Reported"] = "NaN"
df_va_tests["lab_report_date"] = pd.to_datetime(df_va_tests["lab_report_date"])
df_va_tests = df_va_tests.astype(
                        {"number_of_pcr_testing": np.int,
                         "number_of_antigen_testing_encounters": np.int})

df_va_cases["report_date"] = pd.to_datetime(df_va_cases["report_date"])
df_va_cases["total_cases"] = pd.to_numeric(df_va_cases["total_cases"])
df_va_cases.rename({"total_cases": "va_total_cases"}, axis=1, inplace=True)

df_va_tests["va_new_tests"] = df_va_tests[
                        ["number_of_pcr_testing",
                         "number_of_antigen_testing_encounters"]].sum(axis=1)
df_va_tests.drop(["number_of_pcr_testing",
                  "number_of_antigen_testing_encounters"],
                 axis=1, inplace=True)

df_va_cases = df_va_cases.groupby("report_date").sum()
df_va_tests = df_va_tests.groupby("lab_report_date").sum()

df_va = pd.merge(left=df_va_cases, right=df_va_tests, left_index=True,
                 right_index=True, how="inner")

# D.C. is not

url_dc = make_url_dc()

req_dc = requests.get(url_dc)
offset_day = timedelta(days=1)

while req_dc.status_code != 200:
    url_dc = make_url_dc(offset=offset_day)
    req_dc = requests.get(url_dc)
    offset_day += offset_day

print("URL: "+url_dc)
df_dc_excel = pd.read_excel(io.BytesIO(req_dc.content))
if df_dc_excel.iloc[3, 1] != "Total Positives":
    print("DC file format has changed")
    sys.exit(1)

df_dc = df_dc_excel.iloc[[1, 3], 2:-1].T
df_dc.index = pd.to_datetime(df_dc.index)
df_dc.rename({1: "dc_total_tests", 3: "dc_total_cases"}, axis=1, inplace=True)

df_dc.loc["2020-03-20", "dc_total_tests"] = df_dc.loc[
                                            ["2020-03-19", "2020-03-21"],
                                            "dc_total_tests"].mean()
df_dc.dropna(inplace=True)
df_dc["dc_new_tests"] = df_dc["dc_total_tests"].diff(1)
df_dc.loc[df_dc.index[0], "dc_new_tests"] = df_dc.loc[df_dc.index[0],
                                                      "dc_total_tests"]
df_dc.drop("dc_total_tests", axis=1, inplace=True)

# MD is inbetween

url_md_cases = (r"https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/"
                "services/MDCOVID19_CasesByCounty/FeatureServer/0/query?"
                "where=1=1&outFields=DATE,Montgomery,Prince_Georges&"
                "returnGeometry=false&f=json")

url_md_tests = (r"https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/"
                "services/MDCOVID19_DailyTestingVolumeByCounty/FeatureServer/"
                "0/query?outFields=*&where=1=1&f=json&returnGeometry=false")

req_md_cases = requests.get(url_md_cases)

json_md_cases = json.loads(req_md_cases.content)
json_md_cases_features = [feature["attributes"]
                          for feature in json_md_cases["features"]]
df_md_json_cases = pd.DataFrame(json_md_cases_features)
df_md_json_cases.index = pd.to_datetime(df_md_json_cases["DATE"],
                                        unit="ms").dt.date
df_md_json_cases = df_md_json_cases.drop("DATE", axis=1)
df_md_json_cases["md_total_cases"] = df_md_json_cases.sum(axis=1)
df_md_json_cases.drop(["Montgomery", "Prince_Georges"], axis=1, inplace=True)


req_md_tests = requests.get(url_md_tests)

json_md_tests = json.loads(req_md_tests.content)
json_md_tests_features = []

for county in json_md_tests["features"]:
    if county["attributes"]["County"] in ["Montgomery", "Prince George\'s"]:
        for test_date in county["attributes"].keys():
            if test_date not in ["OBJECTID", "County"]:
                t = {
                     "Date": test_date,
                     county["attributes"]["County"]:
                     county["attributes"][test_date]}
                json_md_tests_features.append(t)

df_md_json_tests = pd.DataFrame(json_md_tests_features)
df_md_json_tests["Date"] = df_md_json_tests["Date"].str.lstrip("d_")
df_md_json_tests["Date"] = pd.to_datetime(df_md_json_tests["Date"],
                                          format="%m_%d_%Y")
df_md_json_tests = df_md_json_tests.groupby("Date").sum().sum(axis=1)
df_md_json_tests.rename("md_new_tests", inplace=True)

df_md = pd.merge(left=df_md_json_cases, right=df_md_json_tests, how="outer",
                 left_index=True, right_index=True)

df = reduce(lambda left, right: pd.merge(left=left, right=right, how="inner",
            left_index=True, right_index=True), [df_va, df_dc, df_md])

mask_total_cases = df.columns.str.contains("_total_cases")
df["dmv_total_cases"] = df.loc[:, mask_total_cases].sum(axis=1)
mask_new_cases = df.columns.str.contains("_new_tests")
df["dmv_new_tests"] = df.loc[:, mask_new_cases].sum(axis=1)

df["dmv_new_cases"] = df["dmv_total_cases"].diff(1)
df["va_new_cases"] = df["va_total_cases"].diff(1)
df["dc_new_cases"] = df["dc_total_cases"].diff(1)
df["md_new_cases"] = df["md_total_cases"].diff(1)

df.loc[df.index[0], "dmv_new_cases"] = df.loc[df.index[0], "dmv_total_cases"]
df.loc[df.index[0], "va_new_cases"] = df.loc[df.index[0], "va_total_cases"]
df.loc[df.index[0], "dc_new_cases"] = df.loc[df.index[0], "dc_total_cases"]
df.loc[df.index[0], "md_new_cases"] = df.loc[df.index[0], "md_total_cases"]
df.index.name = "report_date"

df.to_csv("daily_incidence.csv")
