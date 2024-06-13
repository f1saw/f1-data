import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import os
from datetime import datetime

# selezione anni -> prendo piloti in quegli anni e si vede come variano nel tempo i piazzamenti finali
# numero di gp fatti
# mappa dei circuiti -> per ogni anno mostrare dove sono stati fatti i GP

def getSeasonData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    csv_file = ["f1db-seasons-driver-standings.csv",
                "f1db-races.csv",
                "f1db-grands-prix.csv",
                "f1db-countries.csv"]
    df_list = {}
    df_list["df_season_costurct"] = [], 
    df_list["df_season_gp"] = []


    i=0
    for path in csv_file:
        df_list[i] = pd.read_csv(directory_path + "/f1db-csv/" + path)
        #print(df_list[i])
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
    df3 = df_list[3].loc[:, ['id', 'alpha3Code']]
    return [df1, df2, df3]#pd.concat([df1, df2, df3], axis=1)


def createRadioButtonDriver():
    return dbc.RadioItems(
                      # Sono le 3 opzioni
                      options=[
                          {"label":"Position", "value":"positionNumber"}, # opzione boxplot
                          {"label":"Points", "value":"points"}
                      ],
                      # Impostiamo il valore di default
                      value="positionNumber",
                      # inline = True mette i 3 bottoni in linea invece che verticale
                      inline=True,
                      id="radio-input",
                      style={'marginBottom': 20, 'marginLeft': 7}
                )

def createRangeSlider():
    marks = {str(year): str(year) for year in range(1950, datetime.now().year + 1)}
    return dcc.RangeSlider(1950, 
                           datetime.now().year, 
                           1, 
                           value=[1990, 1995], 
                           marks=marks, 
                           id='range-slider'
                    )

def createDropDownDrivers(slider_value=[1990, 1995]):
    data = getSeasonDrivingStanding()
    data_in_range = data.loc[(data["year"] >= slider_value[0]) & (data["year"] <= slider_value[1])]
    data_in_range = data_in_range['driverId'].unique()
    
    return dcc.Dropdown(
    id='dropdown_drivers',
    options = [{'label': value, 'value': value} for value in data_in_range ],
    value=['ayrton-senna', 'alain-prost'],
    multi=True,
    style={'marginBottom': 10, 'marginTop': 20, 'text-align': 'center'}
    )

def updateDropDownDrivers(slider_value):
    data = getSeasonDrivingStanding()
    data_in_range = data.loc[(data["year"] >= slider_value[0]) & (data["year"] <= slider_value[1])]
    data_in_range = data_in_range['driverId'].unique()
    
    return [{'label': value, 'value': value} for value in data_in_range]

def crateDriverElement(slider_value):
    if (slider_value is None):
        slider_value = [1990, 1995]
    return html.Div([
                    createRadioButtonDriver(),
                    createRangeSlider(),
                    createDropDownDrivers(slider_value)
                ])


def createDropDown():
    return dcc.Dropdown(
    id='dropdown',
    options=[
        {'label': 'Season Map', 'value': 'Season Map'},
        {'label': 'Season Driver', 'value': 'Season Driver'},
        {'label': 'Season Gran Prix', 'value': 'Season Gran Prix'}
    ],
    value='Season Map',
    style={'marginBottom': 10, 'marginTop': 2, 'text-align': 'center'}
)

def figDesign(fig):
    transparent_bg = {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)"
    }

    fig.update_layout(
        transparent_bg,
        height=400,
        title = {
            "text": "Total number of GP contested in F1 history",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18 }
        })

def createSeasonDriverPlot(radio_button_value="positionNumber", slider_value=[1990, 1995], driver=['ayrton-senna', 'alain-prost']):
    data = getSeasonDrivingStanding()
   
    data_in_range = data.loc[(data["year"] >= slider_value[0]) & (data["year"] <= slider_value[1])]
    
    selected_drivers_mask = data_in_range["driverId"].isin(driver)
    data_in_range = data_in_range[selected_drivers_mask]
    
    fig = px.line(data_in_range, x="year", y=radio_button_value, title="Andamento piloti", color="driverId", height=400)
    fig.update_xaxes(dtick=1, tickmode='linear')
    #fig = px.scatter(data_in_range, x="year", y=radio_button_value, title="Andamento piloti", color="driverId")
    if (radio_button_value == "positionNumber"):
        fig.update_yaxes(autorange="reversed", title_text='Position')
    else:
        fig.update_yaxes(title_text='Points')
    figDesign(fig)

    return fig

def createSeason_GP_Plot():
    data = getSeasonGp()
    gp_count_for_year = data['year'].value_counts()
    
    #gp_count_for_year = pd.DataFrame(gp_count_for_year)
    df_count = gp_count_for_year.reset_index()

    df_count.columns = ['year', 'value']
    df_count.sort_values(by="year", inplace=True)
    
    fig = px.line(df_count, x="year", y="value", title="GP for year", height=400)
    fig.update_yaxes(title_text='#GP')

    figDesign(fig)

    return fig

def createSeasonGeo():
    [df1, df2, df3] = getGeoDataGp()
    gp_count_for_year = df1['grandPrixId'].value_counts()

    #gp_count_for_year = pd.DataFrame(gp_count_for_year)
    df_count = gp_count_for_year.reset_index()

    df_count.columns = ['grandPrixId', 'value']
    df = pd.DataFrame(columns=['id', 'count', 'code'])
    for index, value in df_count['grandPrixId'].items():
        
        countrieId = df2.loc[df2['id'] == value, "countryId"].iloc[0]
        
        alpha3Code = df3.loc[df3['id'] == countrieId, "alpha3Code"]
        if not alpha3Code.empty:
            alpha3Code = alpha3Code.iloc[0]
            df = df._append({'id': value, 'count': df_count.loc[df_count['grandPrixId'] == value, "value"].iloc[0], 'code': alpha3Code}, ignore_index=True)
        
    
    df['count'] = df['count'].astype(str).astype(int)


    fig = px.scatter_geo(df, locations=df["code"], size="count", hover_data={"id" : True}, height=400)
    figDesign(fig)

    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showland=True, landcolor="rgb(200,212,227)",
        resolution=110
    ),
    
    return fig
