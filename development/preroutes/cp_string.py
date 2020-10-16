city = "north salt lake"
state = "ut"

columns = [
    "city",
    "state",
    "popestimate2010",
    "popestimate2011",
    "popestimate2012",
    "popestimate2013",
    "popestimate2014",
    "popestimate2015",
    "popestimate2016",
    "popestimate2017",
    "popestimate2018",
    "popestimate2019"
]

retrieve_records = f"""
SELECT
"""

for i in range(len(columns) - 1):
    retrieve_records += f"    {columns[i]},\n"

retrieve_records += f"    {columns[-1]}"
retrieve_records += f"""
FROM census
WHERE "city"='{city.title()} city' and "state"='{state.upper()}'
"""

if __name__ == "__main__":
    print(retrieve_records)