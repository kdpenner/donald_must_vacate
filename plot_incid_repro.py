import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, datestr2num, MonthLocator, DateFormatter
from datetime import timedelta

incid = pd.read_csv("daily_incidence.csv")
incid["report_date"] = pd.to_datetime(incid["report_date"])
repro = pd.read_csv("repro_num.csv")

important_dates = {
            "2020-03-30": "Stay at home orders issued",
            "2020-06-12": "NoVA phase 2",
            "2020-07-01": "NoVA phase 3",
            "2020-05-29": "NoVA and D.C. phase 1;\nfirst George Floyd protest",
            "2020-06-22": "D.C. phase 2",
            "2020-06-01": "MoCo and Prince George's\nphase 1",
            "2020-06-19": "MoCo phase 2",
            "2020-06-15": "Prince George's phase 2",
            "2020-07-27": "John Lewis viewing",
            "2020-09-23": "RGB viewing",
            "2020-09-26": "ACB Rose Garden event",
            "2020-10-03": "Trump's positive test",
            "2020-05-25": "Memorial Day",
            "2020-07-04": "Independence Day",
            "2020-09-07": "Labor Day"}

delta_incid = timedelta(days=10)
last_incid = incid["report_date"].max() - delta_incid
delta_repro = timedelta(days=17)
last_repro = incid["report_date"].max() - delta_repro

fig = plt.figure(figsize=(7, 10))

ax1 = fig.add_subplot(2, 1, 1)

ax1.step(incid["report_date"], incid["dmv_new_cases"], where="post")
ax1.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5)
ax1.set_ylabel("Number of new positive cases")

ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)

ax2.step(incid["report_date"].loc[repro.index], repro["Median(R)"],
         where="pre")

errs = [repro["Median(R)"]-repro["Quantile.0.025(R)"],
        repro["Quantile.0.975(R)"]-repro["Median(R)"]]

ax2.errorbar(incid["report_date"].loc[repro.index],
             repro["Median(R)"], yerr=errs, fmt="none", ecolor="tab:blue",
             alpha=0.5)

colors = plt.get_cmap("tab20").colors[2:]

for i, day in enumerate(sorted(important_dates.keys())):
    ax2.axvline(datestr2num(day), ymin=0.35, ymax=0.45, color=colors[i],
                linewidth=5, label=important_dates[day])

lim_transform = ax2.transData + ax2.transAxes.inverted()

ax2.axvspan(last_repro, incid["report_date"].loc[repro.index].max(),
            facecolor="gold", label="Likely to change", alpha=0.5)
ax2.axhspan(1, 1.5, xmax=lim_transform.transform((date2num(last_repro), 0))[0],
            facecolor="darkturquoise", alpha=0.5,
            label="Epidemic won't end")
ax2.axhspan(0.5, 1, xmax=lim_transform.transform((date2num(last_repro), 0))[0],
            facecolor="navajowhite", alpha=0.5,
            label="Epidemic will eventually end if sustained")

handles, labels = ax2.get_legend_handles_labels()
handles = [handles[-3]] + handles[-2:] + handles[:-3]
labels = [labels[-3]] + labels[-2:] + labels[:-3]

ax2.legend(handles, labels, loc='lower left', bbox_to_anchor=(1, 0))

ax2.set_ylim([0.5, 1.5])
ax2.set_ylabel("Instantaneous reproduction number")

locator = MonthLocator()
formatter = DateFormatter("%B")
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)

fig.autofmt_xdate()

plt.savefig("dmv_summary.png", bbox_inches="tight")

plt.show()
