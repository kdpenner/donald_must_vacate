import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, MonthLocator, DateFormatter

incid = pd.read_csv("daily_incidence.csv")
repro = pd.read_csv("repro_num.csv")

fig = plt.figure(figsize=(7,10))

ax1 = fig.add_subplot(2, 1, 1)

ax1.step(date2num(incid["report_date"]), incid["dmv_new_cases"], where="post")
ax1.set_ylabel("Number of new positive cases")

ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)

ax2.step(date2num(incid["report_date"].loc[repro.index]), repro["Median(R)"],
         where="pre")

errs = [repro["Median(R)"]-repro["Quantile.0.025(R)"],
        repro["Quantile.0.975(R)"]-repro["Median(R)"]]

ax2.errorbar(date2num(incid["report_date"].loc[repro.index]),
             repro["Median(R)"], yerr=errs, fmt="none", ecolor="lightgray")
ax2.axhspan(1, 1.5, facecolor="mediumpurple", alpha=0.5,
            label="average number of cases over following 7 days increases")
ax2.axhspan(0.5, 1, facecolor="navajowhite", alpha=0.5,
            label="average number of cases over following 7 days decreases")
ax2.legend(facecolor="white", framealpha=1)

ax2.set_ylim([0.5, 1.5])
ax2.set_ylabel("Instantaneous reproduction number")

locator = MonthLocator()
formatter = DateFormatter("%B")
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)

fig.autofmt_xdate()

plt.savefig("dmv_summary.png", bbox_inches="tight")

plt.show()
