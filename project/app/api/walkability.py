from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.sql_query_function import fetch_query_records

import json
import os
import requests

router = APIRouter()


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

    statecode = statecode.upper()  # Ensure state code is uppercase.
    city = city.title()  # Capitalize first letter of city.

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
    if statecode not in codes:
        raise HTTPException(status_code=404,
                            detail=f"State '{statecode}' not found.")

    # Make query to database
    citystate = f'{city}, {statecode}'
    query = f"""SELECT walkscore FROM WALKABILITY WHERE city='{citystate}';"""
    data = fetch_query_records(query)

    # Return fetched data
    return json.dumps({'city': citystate, 'walkability': data[0][0]})
