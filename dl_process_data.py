import os
import sys
from datetime import date
import requests
import io
import numpy as np
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt

# Virginia is professional

apptoken = os.environ.get("VDH_APPTOKEN")

client = Socrata("data.virginia.gov", apptoken)

results = client.get("bre9-aqqr", where=("vdh_health_district == 'Arlington' OR "
                                        "vdh_health_district == 'Fairfax' OR "
                                        "vdh_health_district == 'Alexandria' OR "
                                        "vdh_health_district == 'Loudoun' OR "
                                        "vdh_health_district == 'Prince William'"),
                    select="total_cases, vdh_health_district, report_date",
                    limit=1000000)

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
dayofmonth = '8'
year = today.strftime("-%Y")
today_str = month + dayofmonth + year

base_url = r"https://coronavirus.dc.gov/sites/default/files/dc/sites/coronavirus/page_content/attachments/"
fname = "DC-COVID-19-Updated-Data-for-" + today_str + ".xlsx"

full_url = base_url + fname

req_dc = requests.get(full_url)

if req_dc.status_code == 200:
    df_dc_excel = pd.read_excel(io.BytesIO(req_dc.content))
else:
    print("File probably not found, try later")
    sys.exit(1)

df_dc = df_dc_excel.iloc[3, 2:].T
df_dc.dropna(inplace=True)
df_dc.index = pd.to_datetime(df_dc.index)
df_dc.rename("dc_total_cases", inplace=True)

df = pd.merge(left=df_va, right=df_dc, how="inner", left_index=True, right_index=True)
df["dmv_total_cases"] = df.sum(axis=1)

df["dmv_new_cases"] = df["dmv_total_cases"].diff(1)
df.index.name = "report_date"

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(df.index, df["dmv_new_cases"])

plt.show()

df.to_csv("daily_incidence.csv")
