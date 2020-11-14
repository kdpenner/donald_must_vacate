import os
import sys
from datetime import date, timedelta
import requests
import io
import json
from functools import reduce
import pandas as pd
from sodapy import Socrata

# Virginia is professional

apptoken = os.environ.get("VDH_APPTOKEN")

client = Socrata("data.virginia.gov", apptoken)

results = client.get("bre9-aqqr", where=(
  "vdh_health_district == 'Arlington' OR vdh_health_district == 'Fairfax' "
  "OR vdh_health_district == 'Alexandria' OR vdh_health_district == 'Loudoun' "
  "OR vdh_health_district == 'Prince William'"),
  select="total_cases, vdh_health_district, report_date", limit=1000000)

client.close()

df_va = pd.DataFrame.from_records(results)
df_va["report_date"] = pd.to_datetime(df_va["report_date"])
df_va["total_cases"] = pd.to_numeric(df_va["total_cases"])
df_va.rename({"total_cases": "va_total_cases"}, axis=1, inplace=True)
df_va = df_va.groupby("report_date").sum()

# D.C. is not

today = date.today()
month = today.strftime("%B-")
dayofmonth = today.strftime("%d")
dayofmonth = dayofmonth.lstrip("0")
year = today.strftime("-%Y")
today_str = month + dayofmonth + year

base_url_dc = (r"https://coronavirus.dc.gov/sites/default/files/dc/sites/"
               "coronavirus/page_content/attachments/")
fname_dc = "DC-COVID-19-Data-for-" + today_str + ".xlsx"

full_url_dc = base_url_dc + fname_dc

req_dc = requests.get(full_url_dc)
offset_day = timedelta(days=1)

while req_dc.status_code != 200:
    earlier = today - offset_day
    month = earlier.strftime("%B-")
    dayofmonth = earlier.strftime("%d")
    dayofmonth = dayofmonth.lstrip("0")
    year = earlier.strftime("-%Y")
    earlier_str = month + dayofmonth + year
    fname_dc = "DC-COVID-19-Data-for-" + earlier_str + ".xlsx"
    full_url_dc = base_url_dc + fname_dc
    req_dc = requests.get(full_url_dc)
    offset_day += offset_day

print("File: "+fname_dc)
df_dc_excel = pd.read_excel(io.BytesIO(req_dc.content))
df_dc = df_dc_excel.iloc[3, 2:].T
df_dc.dropna(inplace=True)
df_dc.index = pd.to_datetime(df_dc.index)
df_dc.rename("dc_total_cases", inplace=True)

# MD is inbetween

full_url_md = (r"https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/"
               "services/MDCOVID19_CasesByCounty/FeatureServer/0/query?"
               "where=1%3D1&outFields=DATE,Montgomery,Prince_Georges&"
               "returnGeometry=false&f=json")

req_md = requests.get(full_url_md)

if req_md.status_code == 200:
    json_md = json.loads(req_md.content)
    json_md_features = [feature['attributes']
                        for feature in json_md['features']]
    df_md_json = pd.DataFrame(json_md_features)
else:
    print("MD dl had an error")
    sys.exit(1)

df_md_json.index = pd.to_datetime(df_md_json["DATE"], unit="ms").dt.date
df_md = df_md_json.drop("DATE", axis=1)
df_md["md_total_cases"] = df_md.sum(axis=1)
df_md.drop(["Montgomery", "Prince_Georges"], axis=1, inplace=True)

df = reduce(lambda left, right: pd.merge(left=left, right=right, how="inner",
            left_index=True, right_index=True), [df_va, df_dc, df_md])

df["dmv_total_cases"] = df.sum(axis=1)

df["dmv_new_cases"] = df["dmv_total_cases"].diff(1)
df.index.name = "report_date"

df.to_csv("daily_incidence.csv")
