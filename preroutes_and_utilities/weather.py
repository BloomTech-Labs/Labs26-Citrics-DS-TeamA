import os
from dotenv import load_dotenv
import sys
from wwo_hist import retrieve_hist_data
import urllib.request

frequency = 6
start_date = "01-Jan-2009"
end_date = '31-AUG-2020'

load_dotenv()

DATA_PATH = os.path.join("data", "weather")
os.chdir(DATA_PATH)

WEATHER_KEY = os.environ.get("WEATHER_KEY")

# Consult lexicon in data/weather directory before proceeding.
locations = [str(code) for code in sys.argv[1:]]

if len(sys.argv[1:]) > 3:
    sure = input(
        "You have entered more than three zip codes, are you certain you'd like to proceed? y/n: "
    )
    if sure.lower() == "n" or sure.lower() == "no":
        sys.exit()

count = 0
for code in locations:
    if len(code) != 5:
        count += 1

if count > 0:
    raise ValueError(
        f"Not a valid zip code; locations array contains value with len < 5"
        )
    sys.exit(5)

f = open("lexicon.txt", "a")
for code in locations:
    input_ = input(f"{code} : location ")
    f.write(f"\n{code} : {input_}")

hist_weather_data = retrieve_hist_data(WEATHER_KEY,
                                       location_list=locations,
                                       start_date=start_date,
                                       end_date=end_date,
                                       frequency=frequency,
                                       location_label=False,
                                       export_csv=True,
                                       store_df=True)
