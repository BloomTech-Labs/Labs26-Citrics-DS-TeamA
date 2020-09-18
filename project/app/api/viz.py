from datetime import datetime
from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd
import plotly.graph_objects as go

router = APIRouter()


@router.get('/viz/{statecode}')
async def viz(statecode: str):
    """
    Visualize state unemployment rate from [Federal Reserve Economic Data](https://fred.stlouisfed.org/) 📈

    ### Path Parameter
    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Response
    JSON string to render with [react-plotly.js](https://plotly.com/javascript/react/)
    """

    # Validate the state code
    statecodes = {
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
    statecode = statecode.upper()
    if statecode not in statecodes:
        raise HTTPException(status_code=404,
                            detail=f'State code {statecode} not found')

    # Get the state's unemployment rate data from FRED
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={statecode}UR'
    df = pd.read_csv(url, parse_dates=['DATE'])

    # Get USA general unemployment rate data from FRED.
    us_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE'
    df_us = pd.read_csv(us_url, parse_dates=['DATE'])

    # Set column names for both datasets.
    df.columns, df_us.columns = ['Date', 'Percent'], ['Date', 'Percent']

    # Restructure US to match state unemployment start dates.
    df_us = df_us[(df_us['Date'].dt.year >= min(df['Date'].dt.year)) &
                  (df_us['Date'].dt.month >= min(df['Date'].dt.month)) &
                  (df_us['Date'].dt.day >= min(df['Date'].dt.day))]

    statename = statecodes[statecode]  # Fetch state name.

    five_yrs = datetime.now().year - 5

    # Styling
    style = dict()
    st_5yrs = np.mean(df[(df['Date'].dt.year == five_yrs)]['Percent'])
    us_5yrs = np.mean(df_us[(df_us['Date'].dt.year == five_yrs)]['Percent'])
    # If the state unemployment rate (last 5 years) is less than US avg...
    if st_5yrs < us_5yrs:
        style['state'] = '#39ED11'
        style['USA'] = 'crimson'
        style['us_size'] = 2.85
        style['state_size'] = 2.5
        title = (f'{statename} averaged lower unemployment than the US ' +
                 f'since {five_yrs}.')
        style['title'] = title
    # If greater than...
    elif st_5yrs > us_5yrs:
        style['USA'] = '#39ED11'
        style['state'] = 'crimson'
        style['us_size'] = 2.8
        style['state_size'] = 4.5
        title = (f'{statename} averaged higher unemployment than the US ' +
                 f'since {five_yrs}.')
        style['title'] = title
    # If equal to...
    elif st_5yrs == us_5yrs:
        style['USA'] = '#39ED11'
        style['state'] = '#39ED11'
        style['us_size'] = 2.5
        style['state_size'] = 2.5
        title = f'{statename} had the same unemployment as the US since {five_yrs}'
        style['title'] = title
    # Instantiate Plotly figure
    fig = go.Figure()
    # Add state to figure.
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Percent'],
                             name=statename,
                             line=dict(width=style.get('state_size'),
                             dash='dot', color=style.get('state'))))
    # Add US to figure.
    fig.add_trace(go.Scatter(x=df_us['Date'], y=df_us['Percent'],
                             name='United States',
                             line=dict(width=style.get('us_size'),
                             color=style.get('USA'))))
    # Title and axes.
    fig.update_layout(title_text=style.get('title'))
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Percent Unemployed')

    # Return Plotly figure as JSON string.
    return fig.to_json()
