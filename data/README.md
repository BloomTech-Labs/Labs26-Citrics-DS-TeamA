# Data Sourcing

## Limitations of Current Deployment

It should be noted that the bulk of the data actually used in the project has been taken from datasets in the form of static *.csv* files. The API is, therefore, outdated. In order to update this, the **Labs 28 DS Team** will need to discover a way using APIs to periodically update these data. In some cases, as with the [**Bureau of Labor Statistics**](https://www.bls.gov/developers/) and [**Census**](https://www.census.gov/data/developers.html) data, the datasets used herein are periodically updated and accessible via their respective APIs.

With dynamic data, however, we introduce greater complexity, especially with regard to **time series** modeling. One approach would be to treat each table or column in **PostgreSQL** database as a something of a *queue* or *ring-buffer*; wherein old information is periodically discarded and new information is periodically inserted into the appropriate tables, ensuring *up-to-date predictions*, rather than stale ones based on old data.

# Data Dictionary

## PostgreSQL Database

### bls_jobs

city: str <- City name
state: str <- Two-letter state name abbreviation 
occ_title: str
jobs_1000: float
loc_quotient: float
hourly_wage: float
annual_wage: int

### census

city: str <- City name
state: str <- Two-letter state name abbreviation 
census2010pop: int
estmatesbase2010: int
popestimate2010: int
popestimate2011: int
popestimate2012: int
popestimate2013: int
popestimate2014: int
popestimate2015: int
popestimate2016: int
popestimate2017: int
popestimate2018: int
popestimate2019: int

### census_pred

census_pred
year: int <- Calendar year
city: str <- City name
state: str <- Two-letter state name abbreviation 
population: int <- Predicted population of city for given year

### climate_zone

zip: int <- Zipcode
city: str <- City name
state: str <- Two-letter state name abbreviation 
latitude: float <- Latitude of given zipcode
longitude: float <- Longitude of given zipcode
timezone: str <- Timezone in long format of given zipcode, *ex: CENTRAL STANDARD TIME* 
dst: int <- Binary integer value with 1 indicating that the locality practices Daylight Savings time and 0 indicating that it does not
climatezone: str <- Köppen climate classification expressed in layman's terms, *ex: Humid subtropical, no dry season*


### feelslikec

month: timestamp <- Datetime object for month of given prediction
city: str <- City name
state: str <- Two-letter state name abbreviation 
mean: float <- Predicted average monthly temperature in degrees Celsius


### feelslikef

month: timestamp <- Datetime object for month of given prediction
city: str <- City name
state: str <- Two-letter state name abbreviation 
mean: float <- Predicted average monthly temperature in degrees Fahrenheit

### historic_weather
date_time: timestamp <- Datetime object for observation taken at each six-hour interval
location: int <- Zipcode
city: str <- City name
state: str <- Two-letter state name abbreviation 
tempc: int <- Temperature in Degrees Celsius
feelslikec: int <- Temperature in Degrees Celsius adjusted for Dew Point and Wind Chill
precipmm: float <- Precipitation in milimeters
totalsnow_cm : int <- Total Snow in centimeters
humidity: int <- Humidity percentage
pressure: int <- Barometric pressure in milibars

### points_of_interest

city: str
point_1: str
point_1_address: str
point_2: str
point_2_address: str
point_3: str
point_3_address: str
point_4: str
point_4_address: str
point_5: str
point_5_address: str

### rental

month: timestamp <- Datetime object for month of historic rental price observation
city: str <- City name
state: str <- Two-letter state name abbreviation 
studio: int <- Studio apartment price for given location in a given month.
onebr: int <- One Bedroom apartment price for given location in a given month.
twobr: int <- Two Bedroom apartment price for given location in a given month.
fourbr: int <- Three Bedroom apartment price for given location in a given month.
fivebr: int <- Four Bedroom apartment price for given location in a given month.

### rental_pred

year: str <- Calendar year
city: str <- City name
state: str <- Two-letter state name abbreviation 
studio: int <- Studio apartment price for given location in a given year.
onebr: int <- Predicted One Bedroom apartment price for given location in a given year.
twobr: int <- Predicted Two Bedroom apartment price for given location in a given year.
fourbr: int <- Predicted Three Bedroom apartment price for given location in a given year.
fivebr: int <- Predicted Four Bedroom apartment price for given location in a given year.

### rental_prices

Location: str <- City name and two-letter state name abbreviation, *ex: New York,NY*
Location_Type: str <- Locale designation *ex: City*
State: str <- Two-letter state name abbreviation
Bedroom_Size: str <- Bedroom size, categories: **Studio**, **1br**, **2br**, **3br**, **4br** 
Price_YYYY_MM: int
from 2018_01 to 2020_08

### rp_clean

city: str <- City name
state: str <- Two-letter state name abbreviation 
bedroom_size: str <- Bedroom size, categories: **Studio**, **1br**, **2br**, **3br**, **4br** 
price_YYYY_MM: int <- Historical rental price observation for year, YYYY, and month, MM
from 2018_01 to 2020_08

### walkability

city: str <- City name and two-letter state name abbreviation, *ex: Abilene,TX*
walkscore: float