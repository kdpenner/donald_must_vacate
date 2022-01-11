import os
# import sys
from datetime import timedelta
import requests
import json
from functools import reduce
import pandas as pd
from sodapy import Socrata
import numpy as np


# Virginia

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

results_vaccines = client.get("28k2-x2rj", where=(
  "health_district == 'Arlington' OR health_district == 'Fairfax' "
  "OR health_district == 'Alexandria' OR health_district == 'Loudoun' "
  "OR health_district == 'Prince William'"),
  select="administration_date, vaccine_manufacturer, dose_number, "
  "vaccine_doses_administered",
  limit=1000000)

client.close()

# VA cases

df_va_cases = pd.DataFrame.from_records(results_cases)

df_va_cases["report_date"] = pd.to_datetime(df_va_cases["report_date"])
df_va_cases["total_cases"] = pd.to_numeric(df_va_cases["total_cases"])
df_va_cases.rename({"total_cases": "va_total_cases"}, axis=1, inplace=True)
df_va_cases = df_va_cases.groupby("report_date").sum()
df_va_cases = df_va_cases.asfreq("1d", method="pad")

# VA tests

df_va_tests = pd.DataFrame.from_records(results_tests)

df_va_tests["lab_report_date"].loc[
    df_va_tests["lab_report_date"] == "Not Reported"] = "NaN"
df_va_tests["lab_report_date"] = pd.to_datetime(df_va_tests["lab_report_date"])
df_va_tests = df_va_tests.astype(
                        {"number_of_pcr_testing": np.int,
                         "number_of_antigen_testing_encounters": np.int})

df_va_tests["va_new_tests"] = df_va_tests[
                        ["number_of_pcr_testing",
                         "number_of_antigen_testing_encounters"]].sum(axis=1)
df_va_tests.drop(["number_of_pcr_testing",
                  "number_of_antigen_testing_encounters"],
                 axis=1, inplace=True)

df_va_tests = df_va_tests.groupby("lab_report_date").sum()

# VA vaccines

df_va_vaccines = pd.DataFrame.from_records(results_vaccines)
df_va_vaccines["administration_date"] = pd.to_datetime(
    df_va_vaccines["administration_date"])
df_va_vaccines["dose_number"] = pd.to_numeric(df_va_vaccines["dose_number"])
df_va_vaccines["vaccine_doses_administered"] = pd.to_numeric(
    df_va_vaccines["vaccine_doses_administered"])
df_va_vaccines = df_va_vaccines[
    df_va_vaccines["vaccine_manufacturer"] != "Non-Specified"]
df_va_vaccines.loc[
    df_va_vaccines["vaccine_manufacturer"].isin(["Pfizer", "Moderna"]) &
    (df_va_vaccines["dose_number"].isin([1, 3])),
    "vaccine_doses_administered"] = 0
df_va_vaccines.loc[
    (df_va_vaccines["vaccine_manufacturer"] == "J&J") &
    (df_va_vaccines["dose_number"] == 2),
    "vaccine_doses_administered"] = 0
df_va_vaccines.drop("dose_number", axis=1, inplace=True)
df_va_vaccines.rename({"vaccine_doses_administered": "va_vaccinated"},
                      axis=1, inplace=True)
df_va_vaccines = df_va_vaccines.groupby("administration_date").sum()
df_va_vaccines = df_va_vaccines.cumsum()

# VA merge and resample

df_va = reduce(lambda left, right: pd.merge(left=left, right=right,
               how="left", left_index=True, right_index=True),
               [df_va_cases, df_va_tests, df_va_vaccines])

# if df_va["va_total_cases"].isna().any():
#     print("VA missing day, find out what to do")
#     sys.exit(1)

print("Last VA day is {0}".format(df_va.index[-1].strftime("%Y-%m-%d")))

# D.C. cases

url_dc_cases = ("https://em.dcgis.dc.gov/dcgis/rest/services/COVID_19/"
                "OpenData_COVID19/FeatureServer/3/query?outFields="
                "DATE_REPORTED,OVERALL_TESTED_TST,TOTAL_POSITIVES_TST&"
                "where=1=1&returnGeometry=false&f=json")
req_dc_cases = requests.get(url_dc_cases)
json_dc_cases = json.loads(req_dc_cases.content)
json_dc_cases_features = [feature["attributes"]
                          for feature in json_dc_cases["features"]]
df_dc_cases = pd.DataFrame(json_dc_cases_features)
df_dc_cases.index = pd.to_datetime(df_dc_cases["DATE_REPORTED"],
                                   unit="ms").dt.date
df_dc_cases.drop("DATE_REPORTED", axis=1, inplace=True)
df_dc_cases.rename({"OVERALL_TESTED_TST": "dc_total_tests",
                    "TOTAL_POSITIVES_TST": "dc_total_cases"},
                   axis=1, inplace=True)
df_dc_cases.sort_index(inplace=True)
df_dc_cases.fillna(method="pad", axis=0, inplace=True)
df_dc_cases = df_dc_cases.asfreq("1d", method="pad")
df_dc_cases["dc_new_tests"] = df_dc_cases["dc_total_tests"].diff(1)
df_dc_cases.drop("dc_total_tests", axis=1, inplace=True)

# D.C. vaccines

url_dc_vaccines = ("https://em.dcgis.dc.gov/dcgis/rest/services/COVID_19/"
                   "OpenData_COVID19/FeatureServer/45/query?outFields="
                   "VACC_DATE,RUNNING_SUM_OF_SECOND_TOTAL&"
                   "where=1=1&returnGeometry=false&f=json")
req_dc_vaccines = requests.get(url_dc_vaccines)
json_dc_vaccines = json.loads(req_dc_vaccines.content)
json_dc_vaccines_features = [feature["attributes"]
                             for feature in json_dc_vaccines["features"]]
df_dc_vaccines = pd.DataFrame(json_dc_vaccines_features)
df_dc_vaccines.index = pd.to_datetime(df_dc_vaccines["VACC_DATE"],
                                      unit="ms").dt.date
df_dc_vaccines.drop("VACC_DATE", axis=1, inplace=True)
df_dc_vaccines.rename({"RUNNING_SUM_OF_SECOND_TOTAL": "dc_vaccinated"},
                      axis=1, inplace=True)
df_dc_vaccines = df_dc_vaccines.groupby("VACC_DATE").sum()

# D.C. merge

df_dc = pd.merge(left=df_dc_cases, right=df_dc_vaccines,
                 left_index=True, right_index=True, how="left")

print("Last D.C. day is {0}".format(df_dc.index[-1].strftime("%Y-%m-%d")))

# MD

md_base = "https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/"

# MD cases

url_md_cases = (md_base + "MDCOVID19_CasesByCounty/FeatureServer/0/query?"
                "where=1=1&outFields=DATE,Montgomery,Prince_Georges&"
                "returnGeometry=false&f=json")

req_md_cases = requests.get(url_md_cases)

json_md_cases = json.loads(req_md_cases.content)
json_md_cases_features = [feature["attributes"]
                          for feature in json_md_cases["features"]]
df_md_json_cases = pd.DataFrame(json_md_cases_features)
df_md_json_cases.index = pd.to_datetime(df_md_json_cases["DATE"],
                                        unit="ms").dt.date
df_md_json_cases = df_md_json_cases.drop("DATE", axis=1)
df_md_json_cases["md_total_cases"] = df_md_json_cases.sum(axis=1)
df_md_json_cases = df_md_json_cases.asfreq("1d", method="pad")

# MD tests

url_md_tests = (md_base + r"MDCOVID19_DailyTestingVolumeByCounty/"
                "FeatureServer/0/query?outFields=*&"
                "where=County='Montgomery' OR County='Prince George''s'&"
                "f=json&returnGeometry=false")

req_md_tests = requests.get(url_md_tests)

json_md_tests = json.loads(req_md_tests.content)
json_md_tests_features = []

for county in json_md_tests["features"]:
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

# MD vaccines

url_md_vaccines = (md_base + "MD_COVID19_TotalVaccinationsCounty"
                   "FirstandSecondSingleDose/FeatureServer/0/query?"
                   "outFields=VACCINATION_DATE,SecondDoseCumulative,"
                   "SingleDoseCumulative&"
                   "where=County='Montgomery' OR County='Prince George''s'&"
                   "returnGeometry=false&f=json")

req_md_vaccines = requests.get(url_md_vaccines)

json_md_vaccines = json.loads(req_md_vaccines.content)
json_md_vaccines_features = [feature["attributes"]
                             for feature in json_md_vaccines["features"]]
df_md_json_vaccines = pd.DataFrame(json_md_vaccines_features)
df_md_json_vaccines.index = pd.to_datetime(
    df_md_json_vaccines["VACCINATION_DATE"], unit="ms").dt.date
df_md_json_vaccines = df_md_json_vaccines.drop("VACCINATION_DATE", axis=1)
df_md_json_vaccines = df_md_json_vaccines.groupby("VACCINATION_DATE").sum()
df_md_json_vaccines = df_md_json_vaccines.sum(axis=1)
df_md_json_vaccines.rename("md_vaccinated", inplace=True)

# MD merge and resample

df_md = reduce(lambda left, right: pd.merge(left=left, right=right,
               how="outer", left_index=True, right_index=True),
               [df_md_json_cases, df_md_json_tests, df_md_json_vaccines])

# if df_md["md_total_cases"].isna().any():
#     print("MD missing day, find out what to do")
#     sys.exit(1)

print("Last MD day is {0}".format(df_md.index[-1].strftime("%Y-%m-%d")))

# Merge all

df = reduce(lambda left, right: pd.merge(left=left, right=right, how="inner",
            left_index=True, right_index=True), [df_va, df_dc, df_md])
df.sort_index(inplace=True)

# Cases

mask_total_cases = df.columns.str.contains("_total_cases")
df["dmv_total_cases"] = df.loc[:, mask_total_cases].sum(axis=1, min_count=3)

df["dmv_new_cases"] = df["dmv_total_cases"].diff(1)
df["va_new_cases"] = df["va_total_cases"].diff(1)
df["dc_new_cases"] = df["dc_total_cases"].diff(1)
df["md_new_cases"] = df["md_total_cases"].diff(1)

df.loc[df.index[0], "dmv_new_cases"] = df.loc[df.index[0], "dmv_total_cases"]
df.loc[df.index[0], "va_new_cases"] = df.loc[df.index[0], "va_total_cases"]
df.loc[df.index[0], "dc_new_cases"] = df.loc[df.index[0], "dc_total_cases"]
df.loc[df.index[0], "md_new_cases"] = df.loc[df.index[0], "md_total_cases"]
df.index.name = "report_date"

# Tests

mask_new_tests = df.columns.str.endswith("_new_tests")
df["dmv_new_tests"] = df.loc[:, mask_new_tests].sum(axis=1, min_count=3)

# Vaccinations

mask_vaccinated = df.columns.str.contains("_vaccinated")
df["dmv_vaccinated"] = df.loc[:, mask_vaccinated].sum(axis=1, min_count=3)

tendaysago = timedelta(days=10)

num_cases = df.loc[df.index[-1] - tendaysago:, "dmv_new_cases"].sum()

print("{0} new cases in past 10 days".format(num_cases))

df.to_csv("daily_incidence.csv", float_format="%0.2f")
