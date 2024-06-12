import pandas as pd
from datetime import datetime

# TODO => find good way to make this var reusable => put it into get-data.py
folder = 'f1db-csv'
drivers_csv = 'drivers.csv'
seasons_entrants_drivers = 'f1db-seasons-entrants-drivers.csv'
drivers_info = 'f1db-drivers.csv'
countries = 'f1db-countries.csv'
continents = 'f1db-continents.csv'
races_results = "f1db-races-race-results.csv"
qualifying_results = 'f1db-races-qualifying-results.csv'
seasons_driver_standings = "f1db-seasons-driver-standings.csv"

class Drivers:
    MIN_VALUE_DEFAULT = 0
    COL_TO_APPLY_MIN_DEFAULT = "count_position_1"
    PERFORMANCE_TYPE_DEFAULT = "wdcs"
    MONTH_END_SEASON = 12
    
    @staticmethod
    def getDrivers():
        df = pd.read_csv(f"{folder}/{drivers_info}")
        df.rename(columns={"id":"driverId", "name":"driverName"}, inplace=True)
        df.drop(columns=df.columns.difference(["driverId", "driverName"]), inplace=True) # TODO => al più nazionalità
        # print(df.head())
        return df
        
    @staticmethod
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


    @staticmethod
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
    
    
    @staticmethod
    def getAbsolutePerformance(performanceType, minValue, colToApplyMin):
        #print("======================================")
        performanceType2file = {
            "wdcs": seasons_driver_standings,
            "wins": races_results,
            "podiums": races_results,
            "poles": qualifying_results
        }
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
                # If "WDCS" , current year must not count as won world driver championship, to take into account the data:
                #  - "year" must be before current year (e.g. 2024)
                #       (e.g. 1975 < 2024 | OK)
                #       (e.g. 2024 < 2024 | NOT OK, season still running)
                # OR - current month must be at the end of the season (e.g. in decemeber)
                #       (e.g. season 2024 , current date Dec 2024 | OK, same year but season is over)
                p1_mask = (df["positionNumber"] == 1) & ((df["year"] < datetime.now().year) | (datetime.now().month >= Drivers.MONTH_END_SEASON) if performanceType == "wdcs" else True)
                df = df[p1_mask]
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
    
    
    @staticmethod
    def getTrendPerformance(selected_driver, performance_type):
        # TODO
        print("======================================")
        print(f"{selected_driver} - {performance_type}")
        return []