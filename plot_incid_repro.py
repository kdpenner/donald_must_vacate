import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.dates import date2num, datestr2num, MonthLocator, DateFormatter
from matplotlib.text import Text
from datetime import date, timedelta
import calc_prob
from scipy.stats import binom
import string


class HandlerText:
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        handle_text = Text(x=x0, y=y0, text=orig_handle.get_text())
        handlebox.add_artist(handle_text)
        return handle_text


matplotlib.rc("font", **{"family": "sans-serif", "sans-serif": "Helvetica",
                         "weight": "bold", "size": 16})

bbox_locs = {1: (1.05, 0.5), 2: (1.05, -0.1), 3: (1.05, 0.2)}

incid = pd.read_csv("daily_incidence.csv")
incid["report_date"] = pd.to_datetime(incid["report_date"])
repro = pd.read_csv("repro_num.csv")

important_dates = {
        "Stay at home orders issued": ["2020-03-30", "2020-04-06"],
        "Memorial Day;\nphase 1 openings;\nGeorge Floyd protests":
        ["2020-05-25", "2020-06-06"],
        "Phase 2 openings": ["2020-06-12", "2020-06-22"],
        "NoVA phase 3 opening;\nIndependence Day":
        ["2020-07-01", "2020-07-08"],
        "John Lewis viewing": ["2020-07-27", "2020-08-03"],
        "Labor Day": ["2020-09-07", "2020-09-14"],
        "RBG viewing;\nACB Rose Garden event\nTrump's positive test":
        ["2020-09-23", "2020-10-02"],
        "Election day;\nBiden celebration;\nMAGA march":
        ["2020-11-03", "2020-11-14"],
        "Thanksgiving": ["2020-11-26", "2020-12-03"],
        "Christmas; New Year's": ["2020-12-25", "2020-01-01"],
        "Invasion by the\nbasket of deplorables": ["2021-01-06"]}

delta_incid = timedelta(days=7)
last_incid = incid["report_date"].max() - delta_incid
delta_repro = timedelta(days=17)
last_repro = incid["report_date"].max() - delta_repro

rt_offset = timedelta(days=5)

fig = plt.figure(figsize=(7, 15))

ax1 = fig.add_subplot(3, 1, 1)

ax1.step(incid["report_date"], incid["dmv_new_cases"], where="pre")
ax1.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5, label="Likely to change")
ax1.set_ylabel("Daily number of\nnew positive cases")
legax1 = ax1.legend(loc="lower left", bbox_to_anchor=bbox_locs[1])
for legax1patch in legax1.get_patches():
    legax1patch.set_alpha(None)

ax2 = fig.add_subplot(3, 1, 2, sharex=ax1)

ax2.step(incid["report_date"].iloc[10:]-rt_offset, repro["Median(R)"],
         where="pre")

errs = [repro["Median(R)"]-repro["Quantile.0.025(R)"],
        repro["Quantile.0.975(R)"]-repro["Median(R)"]]

ax2.errorbar(incid["report_date"].iloc[10:]-rt_offset,
             repro["Median(R)"], yerr=errs, fmt="none", ecolor="tab:blue",
             alpha=0.5)

colors = list(plt.get_cmap("tab20").colors[2:])
lightpink = colors[11]
lightpuke = colors[15]
lightgray = colors[13]

ax2.set_ylim([0.5, 1.5])

ax2.axvspan(last_repro, incid["report_date"].iloc[-1],
            facecolor="gold", label="Likely to change", alpha=0.5)

ax2.set_ylabel("Reproduction number")

probs = calc_prob.prob_gathering(incid)

ax3 = fig.add_subplot(3, 1, 3, sharex=ax1)

ax3.step(probs.iloc[10:].index, probs.iloc[10:], where="pre")
ax3.axvspan(last_incid, incid["report_date"].max(), facecolor="gold",
            alpha=0.5, label="Likely to change")


ax3.set_ylabel(("For a gathering of 10 random\npeople, probability "
                "that\n1 or more people has virus"))

locator = MonthLocator()
formatter = DateFormatter("%B")
ax3.xaxis.set_major_locator(locator)
ax3.xaxis.set_major_formatter(formatter)

xlim = ax3.get_xlim()[0]
end_patch = Rectangle(xy=(xlim, 0),
                      width=date2num(last_repro) - xlim,
                      height=1, facecolor=lightpuke,
                      alpha=0.5,
                      label="Pandemic will eventually end\nif sustained")
ax2.add_patch(end_patch)

forever_patch = Rectangle(xy=(xlim, 1),
                          width=date2num(last_repro) - xlim,
                          height=ax2.get_ylim()[1]-1, facecolor=lightpink,
                          alpha=0.5, label="Pandemic won't end\nif sustained")
ax2.add_patch(forever_patch)

handles, labels = ax2.get_legend_handles_labels()
handles = [handles[0]] + list(reversed(handles[1:]))
labels = [labels[0]] + list(reversed(labels[1:]))

for i, event in enumerate(important_dates.keys()):
    ann_letter = string.ascii_uppercase[i]
    date_low = important_dates[event][0]
    let = ax2.text(x=datestr2num(date_low), y=0.8, s=ann_letter, label=event)
    handles.append(let)
    labels.append(let.get_label())

legax2 = ax2.legend(handles, labels, loc="lower left",
                    bbox_to_anchor=bbox_locs[2], ncol=2,
                    handler_map={Text: HandlerText()})

for legax2patch in legax2.get_patches():
    legax2patch.set_alpha(None)

thresh7 = 1.-binom.cdf(7, 10, 0.5)
binom_patch7 = Rectangle(xy=(xlim, thresh7),
                         width=date2num(last_incid) - xlim,
                         height=ax3.get_ylim()[1]-thresh7, facecolor=lightgray,
                         alpha=0.5, label=(
                         "Riskier than flipping a coin\n10 times and getting\n"
                         "8 or more heads\n(includes darker shaded region)"))
ax3.add_patch(binom_patch7)

thresh6 = 1.-binom.cdf(6, 10, 0.5)
binom_patch6 = Rectangle(xy=(xlim, thresh6),
                         width=date2num(last_incid) - xlim,
                         height=ax3.get_ylim()[1]-thresh6, facecolor=lightgray,
                         alpha=1, label=(
                         "Riskier than flipping a coin\n10 times and getting\n"
                         "7 or more heads"))
ax3.add_patch(binom_patch6)

legax3 = ax3.legend(loc="lower left", bbox_to_anchor=bbox_locs[3], ncol=2)
legax3patches = legax3.get_patches()
legax3patches[0].set_alpha(None)

fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.05)
fig.text(0, 0.08, (
                "The Donald Must Vacate Project\n"
                "Data: Virginia, D.C., and Maryland departments of health; "
                "Census Bureau\n"
                "Source code: https://github.com/kdpenner/donald_must_vacate"))

today = date.today()

fig.suptitle((
             "Pandemic statistics for the\nD.C. + NoVA + MoCo + PG's County "
             "agglomeration, "+today.strftime("%Y-%m-%d")),
             x=1, y=0.92)

plt.savefig("dmv_summary_{0}.png".format(today.strftime("%Y%m%d")),
            bbox_inches="tight")

plt.close()
