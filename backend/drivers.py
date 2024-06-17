# File      BACKEND | DRIVERS
# Author    Matteo Naccarato

import pandas as pd
from collections import defaultdict

import backend.f1db_utils as f1db_utils


MIN_VALUE_DEFAULT = 0
COL_TO_APPLY_MIN_DEFAULT = "count_position_1"
PERFORMANCE_TYPE_DEFAULT = f1db_utils.PerformanceType.WDCS.value


# LABELS DICT
labels_dict = {
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
    "date": "Date",
    "continentName": "Continent",
    "count_display": "Number of Drivers",
    "countryName": "Country",
    "count": "Number of Drivers",
    "driverInfo": "Drivers"
}

performanceType2file = {
    f1db_utils.PerformanceType.WDCS.value: f1db_utils.seasons_driver_standings,
    f1db_utils.PerformanceType.WINS.value: f1db_utils.races_results,
    f1db_utils.PerformanceType.PODIUMS.value: f1db_utils.races_results,
    f1db_utils.PerformanceType.POLES.value: f1db_utils.qualifying_results
}

performanceType2TimeAxis = {
    "wdcs": "year",
    "wins": "date",
    "podiums": "date",
    "poles": "date"
}

driver_type = {
    "officialDriver": "Official Driver",
    "testDriver": "Test Driver"
}


# @returns -> proper dataframe mask based on {performanceType}
def performanceType2Mask(df, performanceType):
    match performanceType:
        case f1db_utils.PerformanceType.WDCS.value | f1db_utils.PerformanceType.WINS.value | f1db_utils.PerformanceType.POLES.value: 
            return f1db_utils.get_p1_mask(df, performanceType)
        case f1db_utils.PerformanceType.PODIUMS.value:
            return (df["positionNumber"] <= 3.0) 


# @returns -> drivers dataframe. 
#               {filterFlag} is used to return drivers who achieved at least one positive result in performance (e.g. WDCs, Wins, ...)
def getDrivers(filterFlag = None):
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df.drop(columns=df.columns.difference(["driverId", "driverName"]), inplace=True)
    
    if filterFlag is not None: # e.g. WDCs => return only drivers who have won at least one WDCs
        df = getTrendPerformance(df["driverId"].to_numpy(), filterFlag)
        df = df.drop_duplicates(subset=['driverId', 'driverName'])
        df = df.sort_values(by="driverName")
    
    return df
    
    
# @returns -> dataframe with number of official and test drivers over the years
def getNumDriversPerYear():
    df = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.seasons_entrants_drivers}")
    df.drop(columns=["entrantId","constructorId","engineManufacturerId","rounds","roundsText"], inplace=True)
    no_test_driver_mask = df["testDriver"] == False
    df_by_year = df[no_test_driver_mask].groupby(by=["year"]).count()
    df_by_year.rename(columns={"driverId":"officialDriver"}, inplace=True)
    df_by_year.drop(columns=["testDriver"], inplace=True)
    df_by_year = df_by_year.reset_index()
    
    df_test_drivers_by_year = df[~no_test_driver_mask].groupby(by=["year"]).count()
    df_test_drivers_by_year = df_test_drivers_by_year.reset_index()
    df_test_drivers_by_year.drop(columns=["driverId"], inplace=True)
    
    return pd.merge(df_by_year, df_test_drivers_by_year, on="year", how="outer")


# @returns -> dataframe with drivers evolution by country and over the years
def getWorldSpread():
    df_drivers_entrants = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.seasons_entrants_drivers}")
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_continents = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.continents}")
    
    df_drivers_entrants.drop(columns=df_drivers_entrants.columns.difference(["year","driverId"]), inplace=True)
    
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","name","nationalityCountryId"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId", "name": "driverName"}, inplace=True)
        
    df_countries.drop(columns=df_countries.columns.difference(["id", "alpha3Code", "name", "continentId"]), inplace=True)
    df_countries.rename(columns={"id":"nationalityCountryId", "name":"countryName"}, inplace=True)
        
    df_continents.drop(columns=df_continents.columns.difference(["id", "name"]), inplace=True)
    df_continents.rename(columns={"id":"continentId","name":"continentName"},inplace=True)
   
    df_merged = pd.merge(df_drivers_entrants, df_drivers_info, on="driverId", how="left")
    df_merged = pd.merge(df_merged, df_countries, on="nationalityCountryId", how="left")
    df_merged = pd.merge(df_merged, df_continents, on="continentId", how="left")
    df_merged = df_merged.drop_duplicates(subset=['driverId', 'year'])
    df_merged["count"] = df_merged.groupby(["year","alpha3Code"])["driverId"].transform("count")
    df_merged["count_display"] = df_merged["count"]
    
    return df_merged


# @returns -> drivers dataframe with their absolute count of performance achievements (WDCs, Wins, Podiums, Poles)
def getAbsolutePerformance(performanceType, minValue, colToApplyMin):
    df = pd.read_csv(f"{f1db_utils.folder}/{performanceType2file[performanceType]}")
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    df.drop(columns=df.columns.difference(["positionNumber","driverId","year"]), inplace=True)
    
    match performanceType:
        # 1st, 2nd, 3rd places only
        case f1db_utils.PerformanceType.PODIUMS.value:
            podium_mask = (df["positionNumber"] == 1) | (df["positionNumber"] == 2) | (df["positionNumber"] == 3)
            df = df[podium_mask]
            for place in [1,2,3]:
                df[f'count_position_{place}'] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x == place*1.0).sum()) # count P1,P2,P3
            df["count_podiums"] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x <= 3.0).sum()) # count podiums
            df.sort_values(by=["count_position_1"], inplace=True, ascending=False)
            df.drop_duplicates(subset=["driverId","count_position_1","count_position_2","count_position_2"], inplace=True)
            
        # 1st place only
        case f1db_utils.PerformanceType.WINS.value | f1db_utils.PerformanceType.WDCS.value | f1db_utils.PerformanceType.POLES.value:
            df = df[f1db_utils.get_p1_mask(df, performanceType)]
            for place in [1]:
                df[f'count_position_{place}'] = df.groupby('driverId')['positionNumber'].transform(lambda x: (x == place*1.0).sum()) # count P1
            df.sort_values(by=["count_position_1"], inplace=True, ascending=False)
            df.drop_duplicates(subset=["driverId","count_position_1"], inplace=True)
       
    df.drop(columns=["year"], inplace=True)
    df = df[df[colToApplyMin] >= minValue]
    df.reset_index(inplace=True)
    df.drop(columns=["positionNumber","index"], inplace=True)
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")

    return df


# Progressive counter following the years
# e.g. a driver who won WDCs in 2008,2010 will be
#       2008 | 1
#       2009 | 1
#       2010 | 2
#       2011 | 2
counter = defaultdict(int)
def count_p1(row):
    global counter
    if row["positionNumber"] == 1.0:
        counter[row["driverId"]] += 1
    return counter[row["driverId"]]

# Progressive counter like the one above
def count_podiums(row):
    global counter
    if row["positionNumber"] <= 3.0:
        counter[row["driverId"]] += 1
    return counter[row["driverId"]] 


# @returns -> drivers dataframe (filtered by {selected_drivers}) with their trend count of performance achievements (WDCs, Wins, Podiums, Poles)
def getTrendPerformance(selected_drivers, performanceType):
    df = pd.read_csv(f"{f1db_utils.folder}/{performanceType2file[performanceType]}")
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["driverId", "driverName"]), inplace=True)
    
    # Drivers filter by {selected_drivers}
    selected_drivers_mask = df["driverId"].isin(selected_drivers) 
    df = df[selected_drivers_mask]
    if performanceType == f1db_utils.PerformanceType.WDCS.value: 
        df = df[f1db_utils.currentSeasonCheckMask(df, performanceType)]
    else:
        df = df[performanceType2Mask(df, performanceType)] # show the marker only when the driver achieved the result 
        
    df.reset_index(inplace=True)
    match performanceType:
        case f1db_utils.PerformanceType.WDCS.value:
            df.drop(columns=["index","positionDisplayOrder","positionText","points"], inplace=True)
        
        # Get races info
        case f1db_utils.PerformanceType.WINS.value | f1db_utils.PerformanceType.PODIUMS.value | f1db_utils.PerformanceType.POLES.value:
            df.drop(columns=df.columns.difference(["raceId","driverId","positionNumber"]), inplace=True)
            df_races = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.races}")
            df_races.rename(columns={"id":"raceId"}, inplace=True)
            df_races.drop(columns=df_races.columns.difference(["raceId","date","grandPrixId","officialName","circuitId"]), inplace=True)
            df = pd.merge(df, df_races, on="raceId", how="left")
    
    # Progressive counter of drivers' achievements        
    for driver_id in selected_drivers:
        counter[driver_id] = 0
    df["progressiveCounter"] = df.apply(count_p1 if performanceType != f1db_utils.PerformanceType.PODIUMS.value else count_podiums, axis=1)
    df = pd.merge(df, df_drivers_info, on="driverId", how="left")
    
    return df


# Default Drivers DataFrames
dfs = {
    "numDriversPerYear": getNumDriversPerYear(),
    "worldSpread": getWorldSpread(),
    "absolutePerformance": getAbsolutePerformance(PERFORMANCE_TYPE_DEFAULT, MIN_VALUE_DEFAULT, COL_TO_APPLY_MIN_DEFAULT)
}