from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go

router = APIRouter()


@router.get('/viz/{statecode}')
async def viz(statecode: str,
              statecode2: Optional[str]=None,
              statecode3: Optional[str]=None):
    """
    Visualize state unemployment rate from [Federal Reserve Economic Data](https://fred.stlouisfed.org/) 📈

    ### Path Parameter
    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table)
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Query Parameters (Optional)
    `statecode2`: The state code for a state to compare to.
    `statecode3`: The state code for a third state to compare to.
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
    if statecode2 not in statecodes and statecode2:
        raise HTTPException(status_code=404,
                            detail=f'State code {statecode2} not found')
    if statecode3 not in statecodes and statecode3:
        raise HTTPException(status_code=404,
                            detail=f'State code {statecode3} not found')

    # Get the state's unemployment rate data from FRED
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={statecode}UR'
    df = pd.read_csv(url, parse_dates=['DATE'])

    # If there's a second statecode, make a df for it.
    if statecode2:
        url_2 = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={statecode2}UR'
        df_2 = pd.read_csv(url_2, parse_dates=['DATE'])
        df_2.columns = ['Date', 'Percent']

    # If there's a third statecode, make a df for it.
    if statecode3:
        url_3 = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={statecode3}UR'
        df_3 = pd.read_csv(url_3, parse_dates=['DATE'])
        df_3.columns = ['Date', 'Percent']

    # Get USA general unemployment rate data from FRED.
    us_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE'
    df_us = pd.read_csv(us_url, parse_dates=['DATE'])

    # Set column names for datasets.
    df.columns, df_us.columns = ['Date', 'Percent'], ['Date', 'Percent']

    # Restructure US to match state unemployment start dates.
    if not statecode2 and not statecode3:
        df_us = df_us[(df_us['Date'].dt.year >= min(df['Date'].dt.year)) &
                    (df_us['Date'].dt.month >= min(df['Date'].dt.month)) &
                    (df_us['Date'].dt.day >= min(df['Date'].dt.day))]
    if statecode2 and not statecode3:
        df_us = df_us[(df_us['Date'].dt.year >= min(df['Date'].dt.year)) &
                    (df_us['Date'].dt.year >= min(df_2['Date'].dt.year)) &
                    (df_us['Date'].dt.month >= min(df['Date'].dt.month)) &
                    (df_us['Date'].dt.month >= min(df_2['Date'].dt.month)) &
                    (df_us['Date'].dt.day >= min(df['Date'].dt.day)) &
                    (df_us['Date'].dt.day >= min(df_2['Date'].dt.day))]
    if statecode2 and statecode3:
        df_us = df_us[(df_us['Date'].dt.year >= min(df['Date'].dt.year)) &
                    (df_us['Date'].dt.year >= min(df_2['Date'].dt.year)) &
                    (df_us['Date'].dt.year >= min(df_3['Date'].dt.year)) &
                    (df_us['Date'].dt.month >= min(df['Date'].dt.month)) &
                    (df_us['Date'].dt.month >= min(df_2['Date'].dt.month)) &
                    (df_us['Date'].dt.month >= min(df_3['Date'].dt.month)) &
                    (df_us['Date'].dt.day >= min(df['Date'].dt.day)) &
                    (df_us['Date'].dt.day >= min(df_2['Date'].dt.day)) &
                    (df_us['Date'].dt.day >= min(df_3['Date'].dt.day))]        

    statename = statecodes[statecode]  # Fetch state name.

    if statecode2:
        state2 = statecodes[statecode2]
    if statecode3:
        state3 = statecodes[statecode3]

    five_yrs = datetime.now().year - 5

    # Styling
    style = dict()
    # United States
    us_5yrs = np.mean(df_us[(df_us['Date'].dt.year == five_yrs)]['Percent'])
    # State
    st_5yrs = np.mean(df[(df['Date'].dt.year == five_yrs)]['Percent'])
    if statecode2:
        # State 2 
        st2_5yrs = np.mean(df_2[(df_2['Date'].dt.year == five_yrs)]['Percent'])
    if statecode3:
        # State 3
        st3_5yrs = np.mean(df_3[(df_3['Date'].dt.year == five_yrs)]['Percent'])

    # CASE: Only one state entered.
    if statecode and not statecode2 and not statecode3:
        if st_5yrs > us_5yrs:
            style['title'] = f'{statename} Unemployment Rates Averaged Higher than the United States since {five_yrs}.'
            style['state1color'] = '#CC0000'  # Dark error red
            style['us_color'] = '#4BB543'  # Success Green
        elif st_5yrs < us_5yrs:
            style['title'] = f'{statename} Unemployment Rates Averaged Lower than the United States since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success Green
            style['us_color'] = '#CC0000'  # Dark error red
        elif st_5yrs == us_5yrs:
            style['title'] = f'{statename} Averaged the Same Unemployment as the United States since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success Green
            style['us_color'] = 'darkcyan'  # Dark cyan

    # CASE: Two states entered.
    if statecode and statecode2 and not statecode3:
        if st_5yrs > st2_5yrs:
            style['title'] = f'{statename} Averaged Higher Unemployment than {state2} since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success Green
            style['state2color'] = '#CC0000'  # Dark error red
            style['us_color'] = 'black'
        elif st_5yrs < st2_5yrs:
            style['title'] = f'{statename} Averaged Lower Unemployment than {state2} since {five_yrs}.'
            style['state1color'] = '#CC0000'  # Dark error red
            style['state2color'] = '#4BB543'  # Success Green
            style['us_color'] = 'black'
        elif st_5yrs == st2_5yrs:
            style['title'] = f'{statename} and {state2} Averaged the Same Unemployment since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success Green
            style['state2color'] = 'darkcyan'  # Dark Cyan
            style['us_color'] = 'black'

    # CASE: Three states entered (maximum)
    if statecode and statecode2 and statecode3:
        # Possible combinations:
        # 1 > 2 > 3
        # 1 > 3 > 2
        # 2 > 1 > 3
        # 2 > 3 > 1
        # 3 > 2 > 1
        # 3 > 1 > 2
        if (st_5yrs > st2_5yrs) and (st2_5yrs > st3_5yrs):
            style['title'] = f'{statename} Averaged Higher Unemployment than {state2} and {state3} since {five_yrs}.'
            style['state1color'] = '#CC0000'  # Dark error red
            style['state2color'] = 'darkcyan'  # Dark Cyan
            style['state3color'] = '#4BB543'  # Success green
            style['us_color'] = 'black'

        elif (st_5yrs > st3_5yrs) and (st3_5yrs > st2_5yrs):
            style['title'] = f'{statename} Averaged Higher Unemployment than {state2} and {state3} since {five_yrs}.'
            style['state1color'] = '#CC0000'  # Dark error red
            style['state2color'] = '#4BB543'  # Success green
            style['state3color'] = 'darkcyan'  # Dark cyan
            style['us_color'] = 'black'
    
        elif (st2_5yrs > st_5yrs) and (st_5yrs > st3_5yrs):
            style['title'] = f'{statename} Averaged Higher Unemployment than {state3}, but lower than {state2} since {five_yrs}.'
            style['state1color'] = 'darkcyan'  # Dark cyan
            style['state2color'] = '#CC0000'  # Dark error red
            style['state3color'] = '#4BB543'  # Success green
            style['us_color'] = 'black'

        elif (st2_5yrs > st3_5yrs) and (st3_5yrs > st_5yrs):
            style['title'] = f'{statename} Averaged Lower Unemployment than {state2} and {state3} since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success green
            style['state2color'] = '#CC0000'  # Dark error red
            style['state3color'] = 'darkcyan'  # Dark cyan
            style['us_color'] = 'black'

        elif (st3_5yrs > st2_5yrs) and (st2_5yrs > st_5yrs):
            style['title'] = f'{statename} Averaged Lower Unemployment than {state2} and {state3} since {five_yrs}.'
            style['state1color'] = '#4BB543'  # Success green
            style['state2color'] = 'darkcyan'  # Dark cyan
            style['state3color'] = '#CC0000'  # Dark error red
            style['us_color'] = 'black'

        elif (st3_5yrs > st_5yrs) and (st_5yrs > st2_5yrs):
            style['title'] = f'{statename} Averaged Lower Unemployment than {state3}, but higher than {state2} since {five_yrs}.'
            style['state1color'] = 'darkcyan'  # Dark cyan
            style['state2color'] = '#4BB543'  # Success green
            style['state3color'] = '#CC0000'  # Dark error red
            style['us_color'] = 'black'

    # Instantiate Plotly figure
    fig = go.Figure()
    # Add state to figure.
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Percent'],
                             name=statename,
                             line=dict(color=style.get('state1color'))))
    # Add US to figure.
    fig.add_trace(go.Scatter(x=df_us['Date'], y=df_us['Percent'],
                             name='United States',
                             line=dict(color=style.get('us_color'), dash='dash')))
    # Check if there's a second and third trace we need to add.
    if statecode2:
        fig.add_trace(go.Scatter(x=df_2['Date'], y=df_2['Percent'],
                                name=state2,
                                line=dict(color=style.get('state2color'))))
    if statecode3:
        fig.add_trace(go.Scatter(x=df_3['Date'], y=df_3['Percent'],
                                name=state3,
                                line=dict(color=style.get('state3color'))))
    # Title and axes.
    if statecode3:
        fig.update_layout(title_text=style.get('title'),
                          font=dict(size=10))
    else:
        fig.update_layout(title_text=style.get('title'))
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Percent Unemployed')

    # Return Plotly figure as JSON string.
    return fig.to_json()