import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, datestr2num, MonthLocator, DateFormatter
from datetime import date, timedelta
import calc_prob


matplotlib.rc("font", **{"family": "sans-serif", "sans-serif": "Helvetica",
                         "weight": "bold", "size": 16})

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
            "2020-09-23": "RBG viewing",
            "2020-09-26": "ACB Rose Garden event",
            "2020-10-03": "Trump's positive test",
            "2020-05-25": "Memorial Day",
            "2020-07-04": "Independence Day",
            "2020-09-07": "Labor Day"}

delta_incid = timedelta(days=10)
last_incid = incid["report_date"].max() - delta_incid
delta_repro = timedelta(days=17)
last_repro = incid["report_date"].max() - delta_repro

fig = plt.figure(figsize=(7, 15))

ax1 = fig.add_subplot(3, 1, 1)

ax1.step(incid["report_date"], incid["dmv_new_cases"], where="pre")
ax1.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5)
ax1.set_ylabel("Daily number of\nnew positive cases")

ax2 = fig.add_subplot(3, 1, 2, sharex=ax1)

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
            label="Pandemic won't end\nif sustained")
ax2.axhspan(0.5, 1, xmax=lim_transform.transform((date2num(last_repro), 0))[0],
            facecolor="navajowhite", alpha=0.5,
            label="Pandemic will eventually end\nif sustained")

handles, labels = ax2.get_legend_handles_labels()
handles = [handles[-3]] + handles[-2:] + handles[:-3]
labels = [labels[-3]] + labels[-2:] + labels[:-3]

ax2.legend(handles, labels, loc='lower left', bbox_to_anchor=(1, -0.5))

ax2.set_ylim([0.5, 1.5])
ax2.set_ylabel("Reproduction number")

probs = calc_prob.prob_gathering(incid)

ax3 = fig.add_subplot(3, 1, 3, sharex=ax1)

ax3.step(probs.iloc[10:].index, probs.iloc[10:]*100., where="pre")
ax3.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5)
ax3.set_ylabel(("For a gathering of 10,\nprobability (%) "
                "that at least\n1 person has virus"))

locator = MonthLocator()
formatter = DateFormatter("%B")
ax3.xaxis.set_major_locator(locator)
ax3.xaxis.set_major_formatter(formatter)

fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.05)
fig.text(0, 0.08, (
                "The Donald Must Vacate Project\n"
                "Data: Virginia, D.C., and Maryland departments of health; "
                "Census Bureau\n"
                "Source code: https://github.com/kdpenner/donald_must_vacate"))

today = date.today()

fig.suptitle((
             "Pandemic statistics for the D.C.-NoVA-southern MD "
             "agglomeration, "+today.strftime("%Y-%m-%d")),
             x=0.7, y=0.92)

plt.savefig("dmv_summary_{0}.png".format(today.strftime("%Y%m%d")),
            bbox_inches="tight", dpi=300)

plt.close()
