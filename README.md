# The Donald Must Vacate Project: Pandemic statistics for the DMV

Northern Virginia, D.C., and counties in southern Maryland compose a
metropolitan area that should not be considered as 3 independent jurisdictions.
Additionally, southwestern Virginia is culturally different, and distant, from
northern Virginia. Saying "cases in Virginia are rising" can mean that cases in
northern VA are flat while those in southwestern VA are rising. Here are
pandemic statistics relevant to the immediate and complete environment of the
DMV.

First is the daily number of new cases as a function of time for the combined
area.

Second is an estimate of the instantaneous reproduction number for SARS-CoV-2
as a function of time.

Third is a crude estimate of the probability that at least 1 person in a random
group of 10 is infected.

## Background information on the reproduction number

The reproduction number, R, is the average number of secondary infections
caused by exposure to a contagious person. "Instantaneous" refers to the
estimate calculated here; another estimate is of the cohort reproduction
number. From [Cori et al. (2013)][1]:

> The distinction between [cohort R] and [instantaneous R] is similar to the
> distinction between the actual life span of individuals born in 2013, which
> we can measure only retrospectively after all individuals have died (i.e., in
> a century), and life expectancy in 2013, estimated now by assuming that death
rates in the future will be similar to those in 2013.

To be clear, instantaneous R is like the latter.

R<sub>0</sub> is the reproduction number at time = 0, the time a virus is
introduced to a population. For SARS-CoV-2 in China, this event was (likely) in
November, 2019; in the U.S., this event was (likely) in January, 2020.
R<sub>0</sub> for SARS-CoV-2 is uncertain. Plausible values are between 2.0 and
4.0, according to the [CDC][2].

As the population takes countermeasures, such as physical distancing, wearing
of masks, and contact tracing, R at time > 0 differs from
R<sub>0</sub>---hopefully decreasing as time goes on. To end a pandemic before
most of the population contracts the virus, the contagious population must
infect fewer people than its current size. R must be < 1 for an extended period
of time.

## Background information on the probability estimate

An infected person is contagious for [10 days][3]. This number is uncertain to
a few days. The number of contagious people is [11 times][2] the number of
people who've tested positive. This number could be between 6 and 24.

Let's assume that for every 1 person who tests positive and isolates for 10
days, 10 other people are contagious and free to infect the population. If
1,000 people have tested positive in the past 10 days, 10,000 people are
roaming free.

If you go to a gathering of 10 random people, some of these people won't be
infected; the remainder may be. The probability shown in the bottom plot is the
probability that at least 1 person in the random group of 10 is infected. When
the probability is 1, at least 1 person is infected---there is no doubt. When
the probability is 0, no person is infected---there is no doubt.

Credit for this idea goes to [Chande et al. (2020)][3]. The model is very
simple and should be taken with many grains of salt.

## Data

Daily incidence data---number of new cases each day---are taken from 3 sources:
the departments of health of Virginia, D.C., and Maryland.

Included VDH health districts: Arlington, Fairfax, Alexandria, Loudoun, Prince
William. Included MD counties: Montgomery and Prince George's.

## Calculating R(t)

I use the [`EpiEstim`][4] package to estimate the instantaneous reproduction
number as a function of time from the incidence time series.

## Disclaimers

This product uses the Census Bureau Data API but is not endorsed or certified
by the Census Bureau.

[1]: <https://academic.oup.com/aje/article/178/9/1505/89262>

[2]: <https://www.cdc.gov/coronavirus/2019-ncov/hcp/planning-scenarios.html>

[3]: https://www.nature.com/articles/s41562-020-01000-9/

[4]: <https://cran.r-project.org/web/packages/EpiEstim/index.html>
