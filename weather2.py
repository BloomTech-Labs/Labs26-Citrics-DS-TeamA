import os
from dotenv import load_dotenv
from wwo_hist import retrieve_hist_data
import urllib.request

DATA_PATH = os.path.join("data")
os.chdir(DATA_PATH)

frequency = 6
start_date = "01-JAN-2009"
end_date = '03-SEP-2020'

load_dotenv()

WEATHER_KEY = os.environ.get("WEATHER_KEY")

print(WEATHER_KEY)

# Location Lexicon
# ----------------
# Based on zip code of given city's city hall
# "10007" : New York City (Manhattan)
# "94102" : San Francisco
# "90012" : Los Angeles
# "30303" : Atlanta
# "21401" : Annapolis, MD
# "32301" : Tallahassee, FL

locations = ["30303", "21401", "32301"]

hist_weather_data = retrieve_hist_data(WEATHER_KEY,
                                       location_list=locations,
                                       start_date=start_date,
                                       end_date=end_date,
                                       frequency=frequency,
                                       location_label=False, 
                                       export_csv=True,
                                       store_df=True) 