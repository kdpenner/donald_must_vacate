import get_pop


def prob_gathering(incid):

    incid = incid.set_index("report_date")

    infectious_det = incid["dmv_new_cases"].rolling("10d").sum()

    ascertainment_bias = 11.

    infectious_asym = infectious_det * (ascertainment_bias - 1)

    total_pop = get_pop.dmv_pop()

    frac_asym = infectious_asym/total_pop

    prob_gt0_in10 = 1.-(1.-frac_asym)**10.

    return prob_gt0_in10


if __name__ == '__main__':

    prob_gathering()
