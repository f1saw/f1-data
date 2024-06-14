import pandas as pd
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from collections import defaultdict

import backend.f1db_utils as f1db_utils


# LABELS DICT
labels_dict = {
    "year": "Year",
    "timeMillis": "Lap Time Millis",
    "time": "Lap Time",
    "officialName": "GP Name",
    "driverName": "Driver",
    "qualifyingFormat": "Qualifying Format",
    "circuitName": "Circuit",
    "circuitId": "Circuit",
    "totalRacesHeld": "Races Held",
    "name": "Circuit Name",
    "fullName": "Circuit Name",
    "type": "Circuit Type",
    "countryName": "Country",
    "positionQualifying": "Qualifying",
    "positionRace": "Race"
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


# UP-LEFT GRAPH
def get_gp_held(minValue):
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.circuits}")
    df.sort_values(by=["totalRacesHeld", "name"], ascending=False, inplace=True)
    
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.rename(columns={"id": "countryId", "name":"countryName"}, inplace=True)
    df_countries.drop(columns=df_countries.columns.difference(["countryId", "countryName", "alpha3Code"]), inplace=True)
    df = pd.merge(df, df_countries, on="countryId", how="left")
    
    df = df[df["totalRacesHeld"] >= minValue]
    df.reset_index(inplace=True)
    df.drop(columns=["index"], inplace=True)
    
    #print(df.head())
    return df


# UP-RIGHT GRAPH
def get_quali_race(selected_circuits):
    # print("==========================================")
    if len(selected_circuits) != 1: f1db_utils.warning_empty_dataframe # TODO => empty or TOO MANY CIRCUITS, ONLY ONE ALLOWED FOR THIS GRAPH
    
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.qualifying_results}")
    df.rename(columns={"positionText":"positionQualifying"}, inplace=True)
    df.drop(columns=df.columns.difference(["raceId","positionQualifying","driverId"]), inplace=True)
    
    df_races_results = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races_results}")
    df_races_results.rename(columns={"id": "raceId", "positionText": "positionRace"}, inplace=True)
    df_races_results.drop(columns=df_races_results.columns.difference(["raceId", "positionRace", "driverId"]), inplace=True)
    
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    # print(df_races_results.head())
    
    df_races = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races}")
    df_races.rename(columns={"id":"raceId"}, inplace=True)
    df_races.drop(columns=df_races.columns.difference(["raceId", "circuitId", "officialName"]), inplace=True)
    df_races_circuits = pd.merge(df_races_results, df_races, on="raceId", how="left")
    selected_circuits_mask = df_races_circuits["circuitId"].isin(selected_circuits)
    df_races_circuits = df_races_circuits[selected_circuits_mask]
    # print(df_races_circuits.head(10))
    
    df = pd.merge(df, df_races_circuits, on=["raceId","driverId"], how="right")
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")
    # df.drop(columns=["driverId"], inplace=True)
    # df['positionQualifying'] = df['positionQualifying'].replace({'DNF': -1, 'DNS': -2, "DSQ": -3, "DNQ": -4, "NC": -5, "DNPQ": -6, "EX": -7}) # TODO => fare conversione in file a parte
    
    
    # print(df.tail())



    df['positionRace'] = df['positionRace'].replace({'DNF': -1, 'DNS': -2, "DSQ": -3, "DNQ": -4, "NC": -5, "DNPQ": -6, "EX": -7}) # TODO => fare conversione in file a parte
    # df['positionRace'] = df['positionRace'].replace({'DNF': f1db_utils.INFINITE_RESULT, 'DNS': f1db_utils.INFINITE_RESULT, "DSQ": f1db_utils.INFINITE_RESULT, "DNQ": f1db_utils.INFINITE_RESULT, "NC": f1db_utils.INFINITE_RESULT, "DNPQ": f1db_utils.INFINITE_RESULT, "EX": f1db_utils.INFINITE_RESULT}) # TODO => fare conversione in file a parte
    df['positionRace'] = pd.to_numeric(df['positionRace'], errors='coerce')
    df["positionRace"] = df["positionRace"].fillna(-10)
    df['positionRace'] = df['positionRace'].astype(int)
    df = df[df["positionRace"] > 0]
    
    
    

    df['positionQualifying'] = df['positionQualifying'].replace({'DNF': f1db_utils.INFINITE_RESULT, 'DNS': f1db_utils.INFINITE_RESULT, "DSQ": f1db_utils.INFINITE_RESULT, "DNQ": f1db_utils.INFINITE_RESULT, "NC": f1db_utils.INFINITE_RESULT, "DNPQ": f1db_utils.INFINITE_RESULT, "EX": f1db_utils.INFINITE_RESULT}) # TODO => fare conversione in file a parte
    df["positionQualifying"] = df["positionQualifying"].fillna(f1db_utils.INFINITE_RESULT)
    df['positionQualifying'] = df['positionQualifying'].astype(int)
    # print(df.sort_values(by="positionQualifying", ascending=False).head())
    max_quali_value = df[df["positionQualifying"] != f1db_utils.INFINITE_RESULT]["positionQualifying"].max()
    
    
    df["positionQualifying"] = df["positionQualifying"].replace(f1db_utils.INFINITE_RESULT, max_quali_value+1)
    # print(df.sort_values(by="positionQualifying", ascending=False).head())
    
    

    # df['positionQualifying'] = df['positionQualifying'].replace({'DNF': f1db_utils.INFINITE_RESULT, 'DNS': f1db_utils.INFINITE_RESULT, "DSQ": f1db_utils.INFINITE_RESULT, "DNQ": f1db_utils.INFINITE_RESULT, "NC": f1db_utils.INFINITE_RESULT, "DNPQ": f1db_utils.INFINITE_RESULT, "EX": f1db_utils.INFINITE_RESULT}) # TODO => fare conversione in file a parte
    # df['positionQualifying'] = pd.to_numeric(df['positionQualifying'], errors='coerce')
    #df["positionQualifying"] = df["positionQualifying"].fillna(f1db_utils.INFINITE_RESULT)
    #df['positionQualifying'] = df['positionQualifying'].astype(int)
    # print(df[df['positionQualifying'].isna()])
    
    
    
    
    
    
    
    # df['positionQualifying'] = df['positionQualifying'].astype(int)
    #print(f"AA - {df["positionQualifying"].max()}")
    # m = int(df["positionQualifying"].max())
    
    
    # print(df.sort_values(by="positionQualifying", ascending=False).head(20))
    
    # df = df[df['positionQualifying'].isin(list(range(int(qualiRange[0]), int(qualiRange[1]))))] # df["positionQualifying"].max()
    
    
    
    
    
    
    
    
    # DROP useless data (negative values)
    df = df[df["positionQualifying"] > 0]
    
    
    
    # df.sort_values(by="positionQualifying", inplace=True)
    # df.reset_index(inplace=True)
    # df.drop(columns=["index"], inplace=True)
    # print(df.head())
    # df_races
    
    
    
    return df
    
    
# BOTTOM GRAPH
def get_qualifying_times(selected_circuits):
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
    
    # print(df.tail())
    return df
    
    

    
    

# UI
circuits_gp_held_min_value = dcc.Slider(
    id='circuits-gp-held-min-value-id',
    min=0,
    step=1,
    value=0,
    tooltip={"placement": "bottom", "always_visible": True}
) 

quali_race_range = dcc.RangeSlider(
    id='circuits-quali-race-range-id',
    min=0, 
    max=20, 
    step=1, 
    value=[-f1db_utils.INFINITE_RESULT, f1db_utils.INFINITE_RESULT],
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
    # value=["interlagos"]
)


circuits_dfs = {
    
}