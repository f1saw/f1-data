import pandas as pd
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from collections import defaultdict

# TODO => find good way to make this var reusable => put it into get-data.py
folder = 'f1db-csv'
drivers_csv = 'drivers.csv'
seasons_entrants_drivers = 'f1db-seasons-entrants-drivers.csv'
drivers_info = 'f1db-drivers.csv'
countries = 'f1db-countries.csv'
continents = 'f1db-continents.csv'
races_results = "f1db-races-race-results.csv"
races = "f1db-races.csv"
qualifying_results = 'f1db-races-qualifying-results.csv'
seasons_driver_standings = "f1db-seasons-driver-standings.csv"
grands_prix = "f1db-grands-prix.csv"


MIN_VALUE_DEFAULT = 0
COL_TO_APPLY_MIN_DEFAULT = "count_position_1"
PERFORMANCE_TYPE_DEFAULT = "wdcs"
MONTH_END_SEASON = 12

# TODO => wins, podiums, poles as ENUM

# DICT
drivers_dict = {
    "driverId": "Driver",
    "driverName": "Driver",
    "count_position_1": "Wins",
    "count_position_2": "2°",
    "count_position_3": "3°",
    "count_podiums": "Podiums",
    "variable": "Position",
    "value": "Number of Podiums",
    "wdcs": "WDCs",
    "wins": "Wins",
    "poles": "Poles",
    "podiums": "Podiums",
    "year": "Year",
    "officialName": "GP",
    "date": "Date"
}

performanceType2file = {
    "wdcs": seasons_driver_standings,
    "wins": races_results,
    "podiums": races_results,
    "poles": qualifying_results
}

performanceType2TimeAxis = {
    "wdcs": "year",
    "wins": "date",
    "podiums": "date",
    "poles": "date"
}


def currentSeasonCheckMask(df, performanceType):
    return (df["year"] < datetime.now().year) | (datetime.now().month >= MONTH_END_SEASON) if performanceType == "wdcs" else True

# FUNCTIONS
def get_p1_mask(df, performanceType):
    # If "WDCS" , current year must not count as won world driver championship, to take into account the data:
    #  - "year" must be before current year (e.g. 2024)
    #       (e.g. 1975 < 2024 | OK)
    #       (e.g. 2024 < 2024 | NOT OK, season still running)
    # OR - current month must be at the end of the season (e.g. in decemeber)
    #       (e.g. season 2024 , current date Dec 2024 | OK, same year but season is over)
    return (df["positionNumber"] == 1.0) & currentSeasonCheckMask(df, performanceType)
    
    
def performanceType2Mask(df, performanceType):
    match performanceType:
        case "wins" | "wdcs" | "poles": 
            return get_p1_mask(df, performanceType)
        case "podiums":
            return (df["positionNumber"] <= 3.0) 


def getDrivers():
    df = pd.read_csv(f"{folder}/{drivers_info}")
    df.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df.drop(columns=df.columns.difference(["driverId", "driverName"]), inplace=True) # TODO => al più nazionalità
    # print(df.head())
    return df
    

def getNumDriversPerYear():
    df = pd.read_csv(f"{folder}/{seasons_entrants_drivers}")
    df.drop(columns=["entrantId","constructorId","engineManufacturerId","rounds","roundsText"], inplace=True)
    no_test_driver_mask = df["testDriver"] == False
    df_by_year = df[no_test_driver_mask].groupby(by=["year"]).count()
    df_by_year.rename(columns={"driverId":"officialDriver"}, inplace=True)
    df_by_year.drop(columns=["testDriver"], inplace=True)
    df_by_year = df_by_year.reset_index()
    
    df_test_drivers_by_year = df[~no_test_driver_mask].groupby(by=["year"]).count()
    df_test_drivers_by_year = df_test_drivers_by_year.reset_index()
    df_test_drivers_by_year.drop(columns=["driverId"], inplace=True)
    
    # print(df_by_year.tail())
    # print(df_test_drivers_by_year.tail())
    #print(pd.merge(df_by_year, df_test_drivers_by_year, on="year", how="outer"))
    return pd.merge(df_by_year, df_test_drivers_by_year, on="year", how="outer")
    #return df_by_year



def getWorldSpread():
    # TODO => fare tramite for
    df_drivers_entrants = pd.read_csv(f"{folder}/{seasons_entrants_drivers}")
    df_drivers_info = pd.read_csv(f"{folder}/{drivers_info}")
    df_countries = pd.read_csv(f"{folder}/{countries}")
    df_continents = pd.read_csv(f"{folder}/{continents}")
    
    df_drivers_entrants.drop(columns=df_drivers_entrants.columns.difference(["year","driverId"]), inplace=True)
    #print(df_drivers_entrants.tail())
    
    
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","countryOfBirthCountryId"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId"}, inplace=True)
    #print(df_drivers_info.tail())
    
    df_countries.drop(columns=df_countries.columns.difference(["id", "alpha3Code", "name", "continentId"]), inplace=True)
    df_countries.rename(columns={"id":"countryOfBirthCountryId", "name":"countryName"}, inplace=True)
    # print(df_countries.tail())
    
    df_continents.drop(columns=df_continents.columns.difference(["id", "name"]), inplace=True)
    df_continents.rename(columns={"id":"continentId","name":"continentName"},inplace=True)
    # print(df_continents.tail())
    
    df_merged = pd.merge(df_drivers_entrants, df_drivers_info, on="driverId", how="left")
    df_merged = pd.merge(df_merged, df_countries, on="countryOfBirthCountryId", how="left")
    df_merged = pd.merge(df_merged, df_continents, on="continentId", how="left")
    df_merged["count"] = df_merged.groupby(["year","alpha3Code"])["driverId"].transform("count")
    df_merged["count_display"] = df_merged["count"]
    df_merged.drop(columns=["driverId"], inplace=True)
    

    # print(df_merged.tail())
    
    return df_merged



def getAbsolutePerformance(performanceType, minValue, colToApplyMin):
    #print("======================================")
    df = pd.read_csv(f"{folder}/{performanceType2file[performanceType]}")
    df_drivers_info = pd.read_csv(f"{folder}/{drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    df.drop(columns=df.columns.difference(["positionNumber","driverId","year"]), inplace=True)
    
    #print(performanceType.upper())
    match performanceType:
        case "wins" | "podiums":
            podium_mask = (df["positionNumber"] == 1) | (df["positionNumber"] == 2) | (df["positionNumber"] == 3)
            df = df[podium_mask]
            for place in [1,2,3]:
                df[f'count_position_{place}'] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x == place*1.0).sum())
            df["count_podiums"] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x <= 3.0).sum())
            df.sort_values(by=["count_position_1"], inplace=True, ascending=False)
            df.drop_duplicates(subset=["driverId","count_position_1","count_position_2","count_position_2"], inplace=True)
        
        case "wdcs" | "poles":
            df = df[get_p1_mask(df, performanceType)]
            for place in [1]:
                df[f'count_position_{place}'] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x == place*1.0).sum())
            df.sort_values(by=["count_position_1"], inplace=True, ascending=False)
            df.drop_duplicates(subset=["driverId","count_position_1"], inplace=True)
            #print(df.head())
        
        
    df.drop(columns=["year"], inplace=True)
    df = df[df[colToApplyMin] >= minValue]
    df.reset_index(inplace=True)
    df.drop(columns=["positionNumber","index"], inplace=True)
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")
        
    
    #print(df.head())
    return df


# Inizializza il contatore
counter = defaultdict(int)

# Funzione per aggiornare il contatore
def count_p1(row):
    global counter
    if row["positionNumber"] == 1.0:
        counter[row["driverId"]] += 1
    return counter[row["driverId"]]

def count_podiums(row):
    global counter
    if row["positionNumber"] <= 3.0:
        counter[row["driverId"]] += 1
    return counter[row["driverId"]] 

def getTrendPerformance(selected_drivers, performanceType):
    # print("======================================")
    # print(f"{selected_drivers} - {performanceType}")
    df = pd.read_csv(f"{folder}/{performanceType2file[performanceType]}")
    df_drivers_info = pd.read_csv(f"{folder}/{drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    
    selected_drivers_mask = df["driverId"].isin(selected_drivers) 
    df = df[selected_drivers_mask]
    df = df[performanceType2Mask(df, performanceType)]
    
    # Get years when selected drivers have raced
    """"driversRacingYears = df.groupby("driverId").apply(
        lambda x: x[['year', 'positionNumber']].to_dict('records')
    ).to_dict()
    print(driversRacingYears)"""
    
    
    #df = df[get_p1_mask(df, performanceType)]
    df.reset_index(inplace=True)
    match performanceType:
        case "wdcs":
            df.drop(columns=["index","positionDisplayOrder","positionText","points"], inplace=True)
        
        case "wins" | "podiums" | "poles":
            df.drop(columns=df.columns.difference(["raceId","driverId","positionNumber"]), inplace=True)
            df_races = pd.read_csv(f"{folder}/{races}")
            df_races.rename(columns={"id":"raceId"}, inplace=True)
            df_races.drop(columns=df_races.columns.difference(["raceId","date","grandPrixId","officialName","circuitId"]), inplace=True)
            df = pd.merge(df, df_races, on="raceId", how="left")
            
            
            
         
    for driver_id in selected_drivers:
        counter[driver_id] = 0
    df["progressiveCounter"] = df.apply(count_p1 if performanceType != "podiums" else count_podiums, axis=1)
    
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")
    # print(df.head())
    return df





# UI
drivers_performance_type_graph_radio = dbc.RadioItems(
    id="drivers-performance-type-graph-id",
    options=[
        {"label": "Absolute", "value": "absolute"},
        {"label": "Driver's Trend", "value": "trend"}
    ],
    value="absolute",
    inline=True
)

drivers_performance_type_radio = dbc.RadioItems(
    id="radio-drivers-performance-type-id",
    options=[
        {"label": "WDCs", "value": "wdcs"},
        {"label": "Wins", "value": "wins"},
        {"label": "Podiums", "value": "podiums"},
        {"label": "Poles", "value": "poles"}
    ],
    value="wdcs",
    inline=True
)

drivers_performance_min_value = dcc.Slider(
    id='drivers-performance-min-value-id',
    min=0,
    # max=100,  # Un valore molto grande per simulare l'infinito
    step=1,
    value=0,
    # marks={0: "0", 100: "100"},
    tooltip={"placement": "bottom", "always_visible": True}
) 

drivers_performance_dropdown = dcc.Dropdown(
    id="drivers-performance-dropdown",
    options=[{"label":row["driverName"], "value": row["driverId"]} for row in getDrivers().to_dict(orient="records")],
    placeholder="Select a Driver",
    searchable=True,
    clearable=False,
    multi=True,
    maxHeight=200,
    # value=["lewis-hamilton","max-verstappen"]
)

drivers_dfs = {
    "numDriversPerYear": getNumDriversPerYear(),
    "worldSpread": getWorldSpread(),
    "absolutePerformance": getAbsolutePerformance(PERFORMANCE_TYPE_DEFAULT, MIN_VALUE_DEFAULT, COL_TO_APPLY_MIN_DEFAULT)
}

driver_type = {
    "officialDriver": "Official Driver",
    "testDriver": "Test Driver"
}