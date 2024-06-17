# File      BACKEND | SEASONS
# Author    Maurizio Meschi

import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import os
from datetime import datetime
import backend.f1db_utils as f1db_utils
import frontend.drivers

labels_dict = {
    "year": "Year",
    "continentName": "Continent",
    "number_gps": "Count",
    "grand_prix_fullName": "GP Names",
    "driverName": "Driver"
}


# FUNCTIONS | GET DATA
def getSeasonData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    csv_file = ["f1db-seasons-driver-standings.csv",
                "f1db-races.csv",
                "f1db-grands-prix.csv",
                "f1db-countries.csv"]
    df_list = {}

    i=0
    for path in csv_file:
        df_list[i] = pd.read_csv(directory_path + "/../f1db-csv/" + path)
        i += 1
    
    return df_list

def getSeasonDrivingStanding():
    df_list = getSeasonData()
    driver_Data = df_list[0]
    driver_Data.drop(columns=["positionDisplayOrder", "positionText"], inplace=True)
    return driver_Data

def getSeasonGp():
    df_list = getSeasonData()
    gp_Data = df_list[1]
    gp_Data.drop(columns=["sprintRaceDate", "warmingUpDate", "warmingUpTime"], inplace=True)
    return gp_Data

def getGeoDataGp():
    df_list = getSeasonData()
    df1 = df_list[1].loc[:, ['year', 'grandPrixId']]
    df2 = df_list[2].loc[:, ['id', 'countryId']]
    df3 = df_list[3].loc[:, ['id', 'continentId', 'alpha3Code']]
    return [df1, df2, df3] 



# FUNCTIONS | PLOTS

# UP-LEFT GRAPH | Number of GP Over the Years
def createSeason_GP_Plot():
    data = getSeasonGp()
    gp_count_for_year = data['year'].value_counts()
    
    df_count = gp_count_for_year.reset_index()
    df_count.columns = ['year', 'value']
    df_count.sort_values(by="year", inplace=True)
    
    return px.line(df_count, 
        x = "year", 
        y = "value", 
        markers = True, 
        labels = labels_dict,
        color_discrete_sequence=f1db_utils.custom_colors,
        template = f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Number of GP Over the Years"),
        hovermode = "x",
        margin=f1db_utils.margin
    ).update_traces(
        hoverlabel=f1db_utils.getHoverlabel(),
        hovertemplate="<br>".join(["<b>%{y}</b><extra></extra>"])
    ).update_yaxes(title_text='Number of GP')
    

# UP-RIGHT GRAPH | Numbers of GP by Country
def createSeasonGeo():
    [df1, df2, df3] = getGeoDataGp()
    gp_count_for_year = df1['grandPrixId'].value_counts()

    df_count = gp_count_for_year.reset_index()
    df_count.columns = ['grandPrixId', 'value']

    # Create a new dataframe to store data of interest from different dfs
    df = pd.DataFrame(columns=['id', 'number_gps', 'continent', 'code'])
    
    # Storage country, alpha3Code and continent
    for index, value in df_count['grandPrixId'].items():
        countryId = df2.loc[df2['id'] == value, "countryId"].iloc[0]
        alpha3Code = df3.loc[df3['id'] == countryId, "alpha3Code"]
        continent = df3.loc[df3['id'] == countryId, "continentId"]
        if not alpha3Code.empty:
            if not continent.empty:
                alpha3Code = alpha3Code.iloc[0]
                continent = continent.iloc[0]
                # Add the row to the new df
                df = df._append({
                    'id': value, 
                    'number_gps': df_count.loc[df_count['grandPrixId'] == value, "value"].iloc[0], 
                    'continent': continent, 
                    'code': alpha3Code
                }, ignore_index=True)
            
    df['number_gps'] = df['number_gps'].astype(str).astype(int)
    
    df_grands_prix = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.grands_prix}")
    df_grands_prix.drop(columns=df_grands_prix.columns.difference(["id", "fullName"]), inplace=True)
    df_grands_prix.rename(columns={"fullName":"grand_prix_fullName"},inplace=True)
    
    df = pd.merge(df, df_grands_prix, on="id", how="left")
    df_grouped = df.groupby('code', as_index=False).agg({
        'id': lambda x: '<br> '.join(map(str, x)),
        'grand_prix_fullName': lambda x: '<br> '.join(map(str, x)),
        'number_gps': 'sum',
        'continent': 'first'
    })
        
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.drop(columns=df_countries.columns.difference(["alpha3Code", "name", "continent"]), inplace=True)
    df_countries.rename(columns={"name":"countryName", "alpha3Code": "code"}, inplace=True)
    
    df_continents = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.continents}")
    df_continents.drop(columns=df_continents.columns.difference(["id", "name"]), inplace=True)
    df_continents.rename(columns={"id":"continent","name":"continentName"},inplace=True)
    
    df_grouped = pd.merge(df_grouped, df_countries, on="code", how="left")
    df_grouped = pd.merge(df_grouped, df_continents, on="continent", how="left")
    
    # Create scatter plot geo
    return px.scatter_geo(df_grouped, 
        locations="code", 
        size="number_gps", 
        color='continentName',
        hover_name="countryName", 
        hover_data={
            "number_gps" : True, 
            "grand_prix_fullName": True,
            "id": False,
            "code" : False
        }, 
        labels=labels_dict,
        color_discrete_map = {
            'Africa': "rgb(99, 110, 250)", 
            'Antarctica': "rgb(239, 85, 59)", 
            'Asia': "rgb(0, 204, 150)", 
            "Europe": "rgb(247,1,0)",
            'Australia': "rgb(171, 99, 250)", 
            'North America': "rgb(25, 211, 243)", 
            'South America': "rgb(254, 203, 82)"
        },
        category_orders = f1db_utils.continents_order,
        template = f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Number of GP by Country"),
        margin=f1db_utils.margin_geo
    ).update_geos(f1db_utils.update_geos).update_traces(hoverlabel = f1db_utils.getHoverlabel(14))
    

# BOTTOM GRAPH
def createSeasonDriverPlot(radio_button_value="positionNumber", slider_value=[1985, 1995], driver=['']):
    data = getSeasonDrivingStanding()
    
    # If there is only one element, transform it into a list
    # (.isin() only accepts a list)
    if isinstance(driver, str):
        driver = [driver]
   
   # Range in which to display the data
    data_in_range = data.loc[(data["year"] >= slider_value[0]) & (data["year"] <= slider_value[1])]
    
    selected_drivers_mask = data_in_range["driverId"].isin(driver)
    data_in_range = data_in_range[selected_drivers_mask]
    
    data_in_range = f1db_utils.order_df(data_in_range, "driverId", driver)
    
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","name"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId", "name": "driverName"}, inplace=True)
    data_in_range = pd.merge(data_in_range, df_drivers_info, on="driverId", how="left")
    
    title = "Positions" if radio_button_value == "positionNumber" else "Points"
    # Create the line chart
    fig = px.line(data_in_range, 
        x="year", 
        y=radio_button_value,  
        color="driverName", 
        labels = labels_dict,
        color_discrete_sequence=f1db_utils.custom_colors,
        color_discrete_map = frontend.drivers.drivers_color_map,
        template = f1db_utils.template,
        hover_data = { "driverName": True }
    ).update_layout(
        f1db_utils.transparent_bg,
        hovermode = "x",
        title = f1db_utils.getTitleObj(f"Drivers' {title} in WDCs"),
        margin=f1db_utils.margin
    )
    fig.update_xaxes(dtick=1, tickmode='linear')
    if (radio_button_value == "positionNumber"):
        fig.update_traces(
            hoverlabel = f1db_utils.getHoverlabel(),
            hovertemplate="<br>".join(["%{customdata} <b>(%{y})</b><extra></extra>"])
        )
        fig.update_yaxes(autorange="reversed", title_text='WDC Position')
    else:
        fig.update_traces(
            hoverlabel = f1db_utils.getHoverlabel(),
            hovertemplate="<br>".join(["Points: <b>%{y}</b><extra></extra>"])
        )
        fig.update_yaxes(title_text='WDC Points')
    
    return fig


    

# HTML Elements
def createRadioButtonDriver():
    return dbc.RadioItems(
            # Sono le 3 opzioni
            options=[
                {"label":"Position", "value":"positionNumber"},
                {"label":"Points", "value":"points"}
            ],
            value="positionNumber",
            id="radio-input",
            className="d-flex flex-column justify-content-start"
    )

# Create the slider
def createRangeSlider():
    dict1 = {str(year): str(year) for year in range(1950, datetime.now().year + 1, 10)}
    dict2 = {str(datetime.now().year) : str(datetime.now().year)}
    marks =  {**dict1, **dict2}
    return dcc.RangeSlider(
        1950, 
        datetime.now().year, 
        10, 
        value=[1985, 1995], 
        marks=marks, 
        id='range-slider',
    )

# Create dropdown
def createDropDownDrivers(slider_value=[1985, 1995]):
    data = getSeasonDrivingStanding()

    data_in_range = data.loc[(data["year"] >= slider_value[0]) & (data["year"] <= slider_value[1])]
    data_in_range = data_in_range['driverId'].unique()
    
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","name"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId", "name": "driverName"}, inplace=True)
    
    selected_drivers_mask = df_drivers_info["driverId"].isin(data_in_range) 
    df_drivers_info = df_drivers_info[selected_drivers_mask]
    
    return dcc.Dropdown(
        id='dropdown_drivers',
        options = [{"label":row["driverName"], "value": row["driverId"]} for row in df_drivers_info.to_dict(orient="records") ],
        multi=True,
        placeholder="Select a Driver",
        value=['ayrton-senna', 'alain-prost']
    )

# Update dropdown
def updateDropDownDrivers(slider_value): 
    df_seasons_drivers_standings = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.seasons_driver_standings}")
    df_seasons_drivers_standings.drop(columns=df_seasons_drivers_standings.columns.difference(["year","driverId"]), inplace=True)
    data = df_seasons_drivers_standings.loc[
        (df_seasons_drivers_standings["year"] >= slider_value[0]) 
        & (df_seasons_drivers_standings["year"] <= slider_value[1])
    ]
        
    df_drivers_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.drivers_info}")
    df_drivers_info.drop(columns=df_drivers_info.columns.difference(["id","name"]), inplace=True)
    df_drivers_info.rename(columns={"id":"driverId", "name": "driverName"}, inplace=True)
    
    data = pd.merge(data, df_drivers_info, on="driverId", how="left")
    
    return [{"label":row["driverName"], "value": row["driverId"]} for row in data.to_dict(orient="records")]
    

def crateDriverElement(slider_value = [1985, 1995]):
    if (slider_value is None):
        slider_value = [1985, 1995]
    return dbc.Row([
        dbc.Col(createRangeSlider(), width=7),
        dbc.Col(createDropDownDrivers(slider_value), width=4),
        dbc.Col(createRadioButtonDriver(), width=1)
    ], style={'marginTop': 0}),
    