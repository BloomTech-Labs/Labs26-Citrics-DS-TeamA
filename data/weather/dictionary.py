import os
import json

# Converting lexicon to dictionary and displaying and json object

lexicon = open(os.path.join("data", "weather", "lexicon.txt"), "r")

list_ = []
for line in lexicon:
    stripped_line = line.strip()
    line_list = stripped_line.split()
    list_.append(line_list)

zipcodes = [list_[i][0] for i in range(len(list_))]
cities = [" ".join(list_[i][2:]) for i in range(len(list_))]

by_zip = {}

for i in range(len(zipcodes)):
    by_zip[zipcodes[i]] = cities[i]

by_city= {}

for i in range(len(zipcodes)):
    by_city[cities[i]] = zipcodes[i]

by_zip_tup = sorted(list(by_zip.items()), key=lambda x:x[0])
by_city_tup = sorted(list(by_city.items()), key=lambda x:x[0])
by_state_tup = sorted(list(by_city.items()), key=lambda x:x[0][-2:])

by_zip = {key:val for (key, val) in by_zip_tup}
by_city = {key:val for (key, val) in by_city_tup}
by_state = {key:val for (key, val) in by_state_tup}

by_zip_json = json.dumps(by_zip, indent=2)
by_city_json = json.dumps(by_city, indent=2)
by_state_json = json.dumps(by_state, indent=2)

# Measuring length of .csv data

csv_files = [file for file in os.listdir(os.path.join("data", "weather")) if file[-3:]  == "csv"]

if __name__ == "__main__":
    print(f"No. of entries: {len(by_zip)}")
    print("")

    print("By Zipcode")
    print("----------")
    print(by_zip_json)
    print("")

    print("By City")
    print("-------")
    print(by_city_json)
    print("")

    print("By State")
    print("--------")
    print(by_state_json)
    print("")

    print(csv_files)