import os
import requests
import json


def dmv_pop():

    census_key = os.environ.get("CENSUS_KEY")

    fips_codes = {"51": ["013", "059", "107", "153", "510", "600", "610",
                         "683", "685"],
                  "11": ["001"],
                  "24": ["031", "033"]}

    population = 0.

    for fips_state in fips_codes.keys():
        for fips_county in fips_codes[fips_state]:
            url_census = ("https://api.census.gov/data/2018/acs/acs5?get=NAME,"
                          "B01003_001E&for=county:"+fips_county+"&in="
                          "state:"+fips_state+"&key="+census_key)
            req_census = requests.get(url_census)
            json_census = json.loads(req_census.content)
            print("Adding population of "+json_census[1][0])
            population += float(json_census[1][1])

    return population


if __name__ == '__main__':

    dmv_pop()
