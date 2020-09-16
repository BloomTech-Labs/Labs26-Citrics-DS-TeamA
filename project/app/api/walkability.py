from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import os
import json
import requests

router = APIRouter()

# Load API keys.
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
WS_API_KEY = os.environ.get('WS_API_KEY')


@router.get("/walkability/{city}_{statecode}")
async def walkability(city: str, statecode: str):
    """Determine how walkable an area is based upon the popular metric,
    [WalkScore](https://www.walkscore.com/professional/api.php),
    using a variety of features available from Google's APIs, including:

    - [Place Autocomplete](https://developers.google.com/places/web-service/autocomplete)
    - [Place Search](https://developers.google.com/places/web-service/search)
    - [Place Details](https://developers.google.com/places/web-service/details)

    Due to limits on the number of results fetched from Google Place Autocomplete, uses a variety of formatted searches to gain the best
    possible generalization of a city's WalkScore.

    ### Path Parameters
    `city`: City of which to retrieve WalkScore.

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Response
    JSON response of `city` and `walkability` (WalkScore calculation as a score out of 100)."""

    codes = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
        'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida',
        'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
        'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky',
        'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
        'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
        'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
        'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
        'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
        }

    statecode = statecode.upper()  # Ensure state code is uppercase.
    city = city.title()  # Capitalize first letter of city.

    if statecode not in codes:
        raise HTTPException(status_code=404,
                            detail=f'State code {code} not found.')

    # Variety of string formats (only 5 results from Google autocomplete API).
    strs = [f"{city}, {statecode}",
            f"{city}, {codes.get(statecode)}",
            f"{city}, {statecode}, United States",
            f"{city}, {codes.get(statecode)}, United States",
            f"{city}, {statecode}, United States of America",
            f"{city}, {codes.get(statecode)}, United States of America"]

    place_ids = []  # Empty array to populate.

    # Iterate through the strings.
    for input_string in strs:
        # Make query to Google Autocomplete.
        q = ('https://maps.googleapis.com/maps/api/place/autocomplete/' +
             f'json?input={input_string}&key={GOOGLE_API_KEY}')
        # Fetch the places from our results.
        places = requests.get(q).json()['predictions']
        places = [dict(p)['description'].split(',')[0] for p in places]

        # Append place IDs to list if doesn't already exist.
        for place in places:
            q = ('https://maps.googleapis.com/maps/api/' +
                 'place/findplacefromtext/' +
                 f'json?input={place}&inputtype=textquery' +
                 f'&key={GOOGLE_API_KEY}')
            query = requests.get(q).json()['candidates']

            # Some results are returning as lists. Let's deal with that.
            if isinstance(query, list):
                place_ids.append([x.get('place_id') for x in
                                  query if x.get('place_id') not in place_ids])
            else:
                if query.get('place_id') not in place_ids:
                    place_ids.append(query.get('place_id'))

    # Fetch addresses from place IDs.
    addresses = []
    for place in place_ids:
        if place:
            q = ('https://maps.googleapis.com/maps/api/place/details/' +
                 f'json?place_id={place[0]}&key={GOOGLE_API_KEY}')
            addresses.append(requests.get(q).json())

    # From this, fetch data from walkscore API.
    scores = []
    for address in addresses:
        lat_lon = address['result']['geometry']['location']
        q = ("https://api.walkscore.com/score?format=json" +
             f"&address={address['result']['formatted_address']}" +
             f"&lat={lat_lon['lat']}&lon={lat_lon['lng']}" +
             f"&wsapikey={WS_API_KEY}")
        scores.append(requests.get(q).json())

    # Get just the walkscores.
    scores = [s.get('walkscore') for s in scores if s.get('walkscore')]

    # Return average walkscore.
    average_score = sum(scores) / len(scores)
    walk = round(average_score, 2)
    return json.dumps({'city': f'{city}, {statecode}', 'walkability': walk})
