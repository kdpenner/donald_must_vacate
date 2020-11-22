import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.dates import date2num, datestr2num, MonthLocator, DateFormatter
from datetime import date, timedelta
import calc_prob
from scipy.stats import binom


matplotlib.rc("font", **{"family": "sans-serif", "sans-serif": "Helvetica",
                         "weight": "bold", "size": 16})

incid = pd.read_csv("daily_incidence.csv")
incid["report_date"] = pd.to_datetime(incid["report_date"])
repro = pd.read_csv("repro_num.csv")

important_dates = {
        "Stay at home orders issued": ["2020-03-30", "2020-04-06"],
        "Memorial Day;\nphase 1 openings;\nfirst George Floyd protest":
        ["2020-05-25", "2020-06-01"],
        "Phase 2 openings": ["2020-06-12", "2020-06-22"],
        "NoVA phase 3 opening;\nIndependence Day":
        ["2020-07-01", "2020-07-08"],
        "John Lewis viewing": ["2020-07-27", "2020-08-03"],
        "Labor Day": ["2020-09-07", "2020-09-14"],
        "RBG viewing;\nACB Rose Garden event": ["2020-09-23", "2020-09-30"],
        "Trump's positive test": ["2020-10-02", "2020-10-09"]}

delta_incid = timedelta(days=7)
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

for i, event in enumerate(important_dates.keys()):
    date_low = important_dates[event][0]
    date_high = important_dates[event][1]
    pR = Rectangle(xy=(datestr2num(date_low), 0.8),
                   width=datestr2num(date_high) - datestr2num(date_low),
                   height=0.1, label=event, facecolor=colors[i], zorder=10)
    ax2.add_patch(pR)

lim_transform2 = ax2.transData + ax2.transAxes.inverted()

ax2.axvspan(last_repro, incid["report_date"].loc[repro.index].max(),
            facecolor="gold", label="Likely to change", alpha=0.5)
ax2.axhspan(1, 1.5,
            xmax=lim_transform2.transform((date2num(last_repro), 0))[0],
            facecolor=colors[11], alpha=0.5,
            label="Pandemic won't end\nif sustained")
ax2.axhspan(0.5, 1,
            xmax=lim_transform2.transform((date2num(last_repro), 0))[0],
            facecolor=colors[15], alpha=0.5,
            label="Pandemic will eventually end\nif sustained")

ax2.set_ylim([0.5, 1.5])
ax2.set_ylabel("Reproduction number")

probs = calc_prob.prob_gathering(incid)

ax3 = fig.add_subplot(3, 1, 3, sharex=ax1)

ax3.step(probs.iloc[10:].index, probs.iloc[10:], where="pre")
ax3.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5)

thresh = 1.-binom.cdf(6, 10, 0.5)
thresh_patch = Rectangle(xy=(0, thresh), width=date2num(last_incid),
                         height=ax3.get_ylim()[1]-thresh, facecolor=colors[13],
                         alpha=0.5, label=(
                         "Riskier than flipping a coin\n10 times and getting\n"
                         "7 or more heads"))
ax3.add_patch(thresh_patch)

ax3.set_ylabel(("For a gathering of 10,\nprobability "
                "that 1 or more\npeople has virus"))

locator = MonthLocator()
formatter = DateFormatter("%B")
ax3.xaxis.set_major_locator(locator)
ax3.xaxis.set_major_formatter(formatter)

handles = []
labels = []

for ax in [ax1, ax2, ax3]:
    handlest, labelst = ax.get_legend_handles_labels()
    handles += handlest
    labels += labelst

handles = [handles[-4]] + handles[-3:-1] + handles[:-4] + [handles[-1]]
labels = [labels[-4]] + labels[-3:-1] + labels[:-4] + [labels[-1]]

leg = fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.9, 0.33))
leg_patches = leg.get_patches()
for leg_patch in leg_patches:
    leg_patch.set_alpha(None)

fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.05)
fig.text(0, 0.08, (
                "The Donald Must Vacate Project\n"
                "Data: Virginia, D.C., and Maryland departments of health; "
                "Census Bureau\n"
                "Source code: https://github.com/kdpenner/donald_must_vacate"))

today = date.today()

fig.suptitle((
             "Pandemic statistics for the\nD.C. + NoVA + MoCo + PG's county "
             "agglomeration, "+today.strftime("%Y-%m-%d")),
             x=0.7, y=0.92)

plt.savefig("dmv_summary_{0}.png".format(today.strftime("%Y%m%d")),
            bbox_inches="tight")

plt.close()
