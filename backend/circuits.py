# File      BACKEND | CIRCUITS
# Author    Matteo Naccarato

import pandas as pd

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
    "totalRacesHeld": "GP Held",
    "name": "Circuit Name",
    "fullName": "Circuit Name",
    "type": "Circuit Type",
    "countryName": "Country",
    "positionQualifying": "Qualifying",
    "positionRace": "Race"
}

not_a_number_replace = {
    'DNF': f1db_utils.INFINITE_RESULT, 
    'DNS': f1db_utils.INFINITE_RESULT, 
    "DSQ": f1db_utils.INFINITE_RESULT, 
    "DNQ": f1db_utils.INFINITE_RESULT, 
    "NC": f1db_utils.INFINITE_RESULT, 
    "DNPQ": f1db_utils.INFINITE_RESULT, 
    "EX": f1db_utils.INFINITE_RESULT
}


# FUNCTIONS
# @returns -> circuits dataframe with countries information
def getCircuits():
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.circuits}")
    df.rename(columns={"id": "circuitId", "name":"circuitName"}, inplace=True)
    df.drop(columns=df.columns.difference(["circuitId", "circuitName", "countryId"]), inplace=True)
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.rename(columns={"id": "countryId", "name":"countryName"}, inplace=True)
    df_countries.drop(columns=df_countries.columns.difference(["countryId", "countryName", "alpha3Code"]), inplace=True)
    df = pd.merge(df, df_countries, on="countryId", how="left")
    
    return df


# UP-LEFT GRAPH (GP Held)
# @returns -> circuits dataframe which held more races than {minValue}
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
    
    return df


# UP-RIGHT GRAPH (Qualifying vs Race)
# @returns -> dataframe of selected circuits (only 1 circuit is accepted due to graphical visualization) 
#               and information about qualifying position and race result of each driver who competed on that circuit
def get_quali_race(selected_circuits):
    if len(selected_circuits) != 1: f1db_utils.warning_empty_dataframe
    
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.qualifying_results}")
    df.rename(columns={"positionText":"positionQualifying"}, inplace=True)
    df.drop(columns=df.columns.difference(["raceId","positionQualifying","driverId"]), inplace=True)
    
    df_races_results = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races_results}")
    df_races_results.rename(columns={"id": "raceId", "positionText": "positionRace"}, inplace=True)
    df_races_results.drop(columns=df_races_results.columns.difference(["raceId", "positionRace", "driverId"]), inplace=True)
    
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    
    df_races = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races}")
    df_races.rename(columns={"id":"raceId"}, inplace=True)
    df_races.drop(columns=df_races.columns.difference(["raceId", "circuitId", "officialName"]), inplace=True)
    df_races_circuits = pd.merge(df_races_results, df_races, on="raceId", how="left")
    selected_circuits_mask = df_races_circuits["circuitId"].isin(selected_circuits)
    df_races_circuits = df_races_circuits[selected_circuits_mask]
    
    df = pd.merge(df, df_races_circuits, on=["raceId","driverId"], how="right")
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")

    df['positionRace'] = df['positionRace'].replace(not_a_number_replace) 
    df['positionRace'] = pd.to_numeric(df['positionRace'], errors='coerce')
    df["positionRace"] = df["positionRace"].fillna(f1db_utils.QUALI_FILL_NA)
    df['positionRace'] = df['positionRace'].astype(int)
    df = df[(df["positionRace"] > 0) & (df["positionRace"] < f1db_utils.INFINITE_RESULT - 1)]

    df['positionQualifying'] = df['positionQualifying'].replace(not_a_number_replace) 
    df["positionQualifying"] = df["positionQualifying"].fillna(f1db_utils.INFINITE_RESULT)
    df['positionQualifying'] = df['positionQualifying'].astype(int)
    max_quali_value = df[df["positionQualifying"] != f1db_utils.INFINITE_RESULT]["positionQualifying"].max()
    # Replace qualifying NaN (previously replaced with INFINITE) with max real qualifying result + 1
    df["positionQualifying"] = df["positionQualifying"].replace(f1db_utils.INFINITE_RESULT, max_quali_value + 1)
    df = df[df["positionQualifying"] > 0]
    
    return df
    
    
# BOTTOM GRAPH (Pole Lap Time)
# @returns -> dataframe of selected circuits with pole lap time progress over the years
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
    
    # Filter by Pole and Selected Circuits
    df = df[f1db_utils.get_p1_mask(df, f1db_utils.PerformanceType.POLES.value)]
    selected_circuits_mask = df["circuitId"].isin(selected_circuits)
    df = df[selected_circuits_mask]
    # Merge different types of Qualifying format ({time} and {q3})
    df["time"] = df["time"].fillna(df["q3"])
    df["timeMillis"] = df["timeMillis"].fillna(df["q3Millis"])
    
    df.reset_index(inplace=True)
    df.drop(columns=df.columns.difference(["year", "driverId", "driverName", "time", "timeMillis", "circuitId", "circuitName", "grandPrixId", "officialName", "qualifyingFormat"]), inplace=True)
    
    return df