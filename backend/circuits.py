import pandas as pd
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from collections import defaultdict

import backend.f1db_utils as f1db_utils


# DICT
dict = {
    "year": "Year",
    "timeMillis": "Lap Time Millis",
    "time": "Lap Time",
    "officialName": "GP Name",
    "driverName": "Driver",
    "qualifyingFormat": "Qualifying Format",
    "circuitName": "Circuit",
    "circuitId": "Circuit"
}



# FUNCTIONS
def getCircuits():
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.circuits}")
    df.rename(columns={"id": "circuitId", "name":"circuitName"}, inplace=True)
    df.drop(columns=df.columns.difference(["circuitId", "circuitName", "countryId"]), inplace=True)
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.rename(columns={"id": "countryId", "name":"countryName"}, inplace=True)
    df_countries.drop(columns=df_countries.columns.difference(["countryId", "countryName", "alpha3Code"]), inplace=True)
    df = pd.merge(df, df_countries, on="countryId", how="left")
    # print(df.head())
    return df


def get_qualifying_times(selected_circuits):
    print("==========================================")
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.qualifying_results}")
    
    df_races = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races}")
    df_races.rename(columns={"id": "raceId"}, inplace=True)
    df_races.drop(columns=df_races.columns.difference(["raceId", "circuitId", "grandPrixId", "officialName", "qualifyingFormat"]), inplace=True)
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    
    df_circuits = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.circuits}")
    df_circuits.rename(columns={"id": "circuitId", "name": "circuitName"}, inplace=True)
    df_circuits.drop(columns=df_circuits.columns.difference(["circuitId", "circuitName", "countryId"]), inplace=True)
    
    df = pd.merge(df, df_races, on="raceId", how="left")
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")
    df = pd.merge(df, df_circuits, on="circuitId", how="left")
    
    df = df[f1db_utils.get_p1_mask(df, f1db_utils.PerformanceType.POLE)]
    selected_circuits_mask = df["circuitId"].isin(selected_circuits)
    df = df[selected_circuits_mask]
    df["time"] = df["time"].fillna(df["q3"])
    df["timeMillis"] = df["timeMillis"].fillna(df["q3Millis"])
    df.reset_index(inplace=True)
    
    df.drop(columns=df.columns.difference(["year", "driverId", "driverName", "time", "timeMillis", "circuitId", "circuitName", "grandPrixId", "officialName", "qualifyingFormat"]), inplace=True)
    
    print(df.tail())
    return df
    
    
    

# UI
circuits_gp_held_min_value = dcc.Slider(
    id='circuits-gp-held-min-value-id',
    min=0,
    step=1,
    value=0,
    tooltip={"placement": "bottom", "always_visible": True}
) 

circuits_dropdown = dcc.Dropdown(
    id="circuits-dropdown",
    options=[{"label": f"{row["circuitName"]}, {row["countryName"]}", "value": row["circuitId"]} for row in getCircuits().to_dict(orient="records")], # TODO => put also flag image => FLAG Name, country
    placeholder="Select a Circuit",
    searchable=True,
    clearable=False,
    multi=True,
    maxHeight=200,
    value=["monza"]#,"monaco", "austria"]
)


circuits_dfs = {
    
}