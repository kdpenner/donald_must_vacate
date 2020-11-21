library(EpiEstim)
library(ggplot2)

t <- read.table("daily_incidence.csv", header=TRUE, sep=",")
t <- na.omit(t)

names(t)[names(t) == "report_date"] <- "dates"
t$dates <- as.Date(t$dates)
names(t)[names(t) == "dmv_new_cases"] <- "I"

ndays <- NROW(t$I)
t_start <- seq(2, ndays - 9)
t_end <- t_start + 9

config <- make_config(list(mean_si=6, std_mean_si=1,
                           min_mean_si=1, max_mean_si=9,
                           std_si=2, std_std_si=0.5,
                           min_std_si=0.5, max_std_si=2.5,
                           t_start=t_start, t_end=t_end))

roft <- estimate_R(t, method="uncertain_si", config=config)

plot(roft, legend=FALSE)

write.csv(roft$R, "repro_num.csv", row.names=FALSE)
