from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import json
import os
import requests

router = APIRouter()

# Load API keys.
load_dotenv()
YELP_API = os.environ.get('YELP_API')
WS_API_KEY = os.environ.get('WS_API_KEY')


@router.get("/walkability/{city}_{statecode}")
async def walkability(city: str, statecode: str):
    """Determine how walkable an area is based upon the popular metric,
    [Walkscore](https://www.walkscore.com/professional/api.php),
    using the [Yelp Fusion API](https://www.yelp.com/developers/documentation/v3) to fetch addresses
    from the specified location.

    ### Path Parameters
    `city`: City of which to retrieve WalkScore.

    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Response
    JSON response of `city` and `walkability` (Walkscore calculation as a score out of 100)."""

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
                            detail=f"State '{statecode}' not found.")

    headers = {'Authorization': 'Bearer {}'.format(YELP_API)}
    params = {'location': f'{city}, {statecode}'}

    # Make request.
    req = requests.get('https://api.yelp.com/v3/businesses/search',
                       headers=headers, params=params)

    # Empty array to populate with walkscores.
    scores = []

    # Iterate through businesses, and make walkscore requests.
    for business in req.json()['businesses']:
        # Latitude / Longitude / Address needed for Walkscore API.
        lat = business['coordinates']['latitude']
        lon = business['coordinates']['longitude']
        address = business['location']['address1']
        
        # Query
        q = ("https://api.walkscore.com/score?format=json" +
             f"&address={address}&lat={lat}&lon={lon}" +
             f"&wsapikey={WS_API_KEY}")

        # Confirm Walkscore data has been returned and append if so.
        if requests.get(q).json().get('walkscore'):
            scores.append(requests.get(q).json().get('walkscore'))

    # Return average walkscore.
    walk = round(sum(scores) / len(scores), 2)
    return json.dumps({'city': f'{city}, {statecode}', 'walkability': walk})
