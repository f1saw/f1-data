from datetime import datetime
from enum import Enum
import pandas as pd
import plotly.express as px

folder = 'f1db-csv'

continents = 'f1db-continents.csv'
countries = 'f1db-countries.csv'
circuits = 'f1db-circuits.csv'
drivers_info = 'f1db-drivers.csv'
grands_prix = "f1db-grands-prix.csv"
qualifying_results = 'f1db-races-qualifying-results.csv'
races_results = "f1db-races-race-results.csv"
races = "f1db-races.csv"
seasons_driver_standings = "f1db-seasons-driver-standings.csv"
seasons_entrants_drivers = 'f1db-seasons-entrants-drivers.csv'

MONTH_END_SEASON = 12
INFINITE_RESULT = 100
MAX_QUALI = 30
F1_RED = "rgb(247,1,0)"


class PerformanceType(Enum):
    WDCS = "wdcs"
    WINS = "wins"
    PODIUMS = "podiums"
    POLES = "poles"
    
    
# ===============COLORS=====================
custom_colors = px.colors.qualitative.Light24.copy()
custom_colors[0] = F1_RED

podium_colors = {
    "count_position_1": "gold",
    "count_position_2": "silver",
    "count_position_3": "peru"
}

transparent_bg = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)"
}

# ===========================================


    

# ==================FIGURES==================

template = "plotly_dark"
    
warning_empty_dataframe = {
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [{
            "text": "No matching data found",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 28}
        }]
    }
}

def getTitleObj(titleStr):
    return {
        "text": titleStr,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 18 }
    }

continents_order = {
    "continentId": ['africa', 'antarctica', 'asia', 'australia', 'europe', 'north-america', 'south-america'],
    "continentName": ['Africa', 'Antarctica', 'Asia', 'Australia', 'Europe', 'North America', 'South America']
}

# ===========================================






# ==================FUNCTIONS==================

# Function to subset and order a pandas dataframe for a long format
# It does NOT change colors when adding new elements to a graph
def order_df(df_input, order_by, order):
    df_output=pd.DataFrame()
    for var in order:    
        df_append=df_input[df_input[order_by]==var].copy()
        df_output = pd.concat([df_output, df_append])
    return(df_output)


def currentSeasonCheckMask(df, performanceType):
    return (df["year"] < datetime.now().year) | (datetime.now().month >= MONTH_END_SEASON) if performanceType == PerformanceType.WDCS else True

def get_p1_mask(df, performanceType):
    # If "WDCS" , current year must not count as won world driver championship, to take into account the data:
    #  - "year" must be before current year (e.g. 2024)
    #       (e.g. 1975 < 2024 | OK)
    #       (e.g. 2024 < 2024 | NOT OK, season still running)
    # OR - current month must be at the end of the season (e.g. in decemeber)
    #       (e.g. season 2024 , current date Dec 2024 | OK, same year but season is over)
    return (df["positionNumber"] == 1.0) & currentSeasonCheckMask(df, performanceType)

# Funzione per convertire millisecondi in "minutes:seconds:milliseconds"
def ms_to_time(ms):
    minutes = int(ms // 60000)
    seconds = int((ms % 60000) // 1000)
    milliseconds = int(ms % 1000)
    return f"{minutes}:{seconds:02}:{milliseconds:03}"

# ===========================================


# ==================DRIVERS==================


# ===========================================