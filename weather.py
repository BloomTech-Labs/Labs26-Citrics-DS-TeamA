import os
from wwo_hist import retrieve_hist_data

DATA_PATH = os.path.join("data")
os.chdir(DATA_PATH)

frequency = 6
start_date = "01-JAN-2009"
end_date = '03-SEP-2020'
WEATHER_KEY = os.getenv("WEATHER_KEY")

locations = ["new_york", "san_francisco", "los_angeles"]

hist_weather_data = retrieve_hist_data(WEATHER_KEY,
                                       locations,
                                       start_date,
                                       end_date,
                                       frequency,
                                       location_label=False, 
                                       export_csv=True, 
                                       store_df=True) 