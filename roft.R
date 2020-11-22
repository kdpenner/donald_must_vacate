library(EpiEstim)
library(distcrete)
library(ggplot2)

t <- read.table("daily_incidence.csv", header=TRUE, sep=",")
t <- na.omit(t)

names(t)[names(t) == "report_date"] <- "dates"
t$dates <- as.Date(t$dates)
names(t)[names(t) == "dmv_new_cases"] <- "I"

ndays <- NROW(t$I)
t_start <- seq(2, ndays - 9)
t_end <- t_start + 9

si <- distcrete("gamma", 1, anchor=0, w=1, shape=1.38, rate=0.24)
x <- seq(0, 100)
si_discrete <- si$d(x)

config <- make_config(list(si_distr=si_discrete,
                           t_start=t_start, t_end=t_end))

roft <- estimate_R(t, method="non_parametric_si", config=config)

plot(roft, legend=FALSE)

write.csv(roft$R, "repro_num.csv", row.names=FALSE)
