# The Donald Must Vacate Project: Pandemic statistics for the DMV

Northern Virginia, D.C., and counties in southern Maryland compose a
metropolitan area that should not be considered as 3 independent jurisdictions.
Additionally, southwestern Virginia is culturally different, and distant, from
northern Virginia. Saying ``cases in Virginia are rising`` can mean that cases
in northern VA are flat while those in southwestern VA are rising. The first
goal of this project is to present statistics relevant to my decision-making,
which means statistics of my immediate environment.

The second goal of this project is to estimate the reproduction number as a
function of time. The reproduction number is the number of people infected by a
contagious person.

## Data

Daily incidence data---number of new cases each day---are taken from 3 sources:
the departments of health of Virginia, D.C., and Maryland.

Included VDH health districts: Arlington, Fairfax, Alexandria, Loudoun, Prince
William. Included MD counties: Montgomery and Prince George's.

## Calculating R(t)

I use the `EpiEstim` package to estimate the reproduction number as a function
of time from the incidence time series.

`EpiEstim` is introduced here:

<https://academic.oup.com/aje/article/178/9/1505/89262>

Parameters of the serial interval distribution are in:

<https://github.com/kdpenner/donald_must_vacate/blob/main/roft.R>
