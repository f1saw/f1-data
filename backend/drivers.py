import pandas as pd

# find good way to make this var reusable
folder = 'f1db-csv'
drivers_csv = 'drivers.csv'
seasons_entrants_drivers = 'f1db-seasons-entrants-drivers.csv'
drivers_info = 'f1db-drivers.csv'
countries = 'f1db-countries.csv'

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
    # return pd.merge(df_by_year, df_test_drivers_by_year, on="year", how="outer")
    return df_by_year


def getWorldSpread():
    df_drivers_entrants = pd.read_csv(f"{folder}/{seasons_entrants_drivers}")
    df_drivers_info = pd.read_csv(f"{folder}/{drivers_info}")
    df_countries = pd.read_csv(f"{folder}/{countries}")
    
    df_drivers_entrants.drop(columns=df_drivers_entrants.columns.difference(["year","driverId"]), inplace=True)
    #print(df_drivers_entrants.tail())
    
    
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","countryOfBirthCountryId"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId"}, inplace=True)
    #print(df_drivers_info.tail())
    
    df_countries.drop(columns=df_countries.columns.difference(["id", "alpha3Code", "name", "continentId"]), inplace=True)
    df_countries.rename(columns={"id":"countryOfBirthCountryId"}, inplace=True)
    #print(df_countries.tail())
    
    df_merged = pd.merge(df_drivers_entrants, df_drivers_info, on="driverId", how="left")
    df_merged = pd.merge(df_merged, df_countries, on="countryOfBirthCountryId", how="left")
    df_merged["count"] = df_merged.groupby(["year","alpha3Code"])["driverId"].transform("count")
    df_merged["count_display"] = df_merged["count"]
    df_merged.drop(columns=["driverId"], inplace=True)
    

    print(df_merged.tail())
    
    return df_merged