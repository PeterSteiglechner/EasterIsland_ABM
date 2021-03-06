n_fix = "low"
c_req_pp = 6.79 if n_fix == "low" else 1.95  # TODO
# "low": 1/[(1.46 Tons/ha/year) * 0.1 (ha/gardens) * (2809 kcal/day / (Tons/year)  / (2785 kcal/day/person)]
#       1/[1.46 * 0.1 * 2809 * 2785] * [tons * ha * kcal * year * day * person / (ha year gardens day year kcal)]
#       1/[1.46 * 0.1 * 2809 * 2785] * [1/ (tons * ha * kcal * year * day * person / (ha year gardens day Tons kcal))]
#       6.79 [1/ * (person / gardens)]
#       6.79 gardens/person
# "high": 1/(5.09 * 0.1 * 2809/2785) [gardens/person]
#       1.95 gardens/person

params_sensitivity = {
    "t_req_pp": 10,
    "c_req_pp": c_req_pp,
    "time_arrival": 1200,
    "max_p_growth_rate": 1.03,  # Bahn and Flenley 2017

    "map_tree_pattern_condition":
        {
            #"name": "Uniform",  # "Mosaic"
            "max_el": 450,
            "max_sl": 10,
            "tree_decrease_lake_distance": 0  # "Uniform"=0, "Mosaic"=1
        },
    "droughts_rano_raraku": [[800, 1200], [1570, 1720]],

}
