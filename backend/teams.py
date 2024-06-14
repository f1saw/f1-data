import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import os
from datetime import datetime
import utility.utility as utility
import backend.f1db_utils as f1db_utils

def getTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df_list = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-constructors.csv')
    #print(df_list)
    
    return df_list

def getEntrantsTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df_list = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-seasons-entrants-constructors.csv')
    #print(df_list)
    
    return df_list

def getGeoData():
    df1 = getTeamsData()
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df2 = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-countries.csv')

    return [df1,df2]

def getExtraTeamData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-seasons-constructor-standings.csv')
    
    return df

def getRaceTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-races-constructor-standings.csv')
    df2 = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-races.csv')

    return [df,df2]


def createRadioButton():
    return dbc.RadioItems(
                      # Sono le 3 opzioni
                      options=[
                          {"label":"Total Win", "value":"win"}, # opzione boxplot
                          #{"label":"Best Race Result", "value":"best race"},
                          {"label":"Num Win Race", "value":"win race"},
                          {"label":"Num Podiums", "value":"podiums"}
                      ],
                      # Impostiamo il valore di default
                      value="win",
                      # inline = True mette i 3 bottoni in linea invece che verticale
                      inline=True,
                      id="radio-input-teams",
                      style={'marginBottom': 20, 'marginLeft': 7}
                )

def createRadioButtonGraph():
    return dbc.RadioItems(
                      # Sono le 3 opzioni
                      options=[
                          {"label":"Absolute", "value":"absolute"}, # opzione boxplot
                          #{"label":"Best Race Result", "value":"best race"},
                          {"label":"Constructor's Trend", "value":"trend"}
                      ],
                      # Impostiamo il valore di default
                      value="absolute",
                      # inline = True mette i 3 bottoni in linea invece che verticale
                      inline=True,
                      id="radio-input-graph",
                      style={'marginBottom': 20, 'marginLeft': 7}
                )

def createDropdown(min_value = 1, radio_value = 'win'):
    df = getTeamsData()
    if (min_value is None):
        min_value = 1
    if (radio_value == 'win'):
        df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
        df = df.loc[df['totalChampionshipWins'] >= min_value]
    elif (radio_value == 'win race'):
        df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
        df = df.loc[df['totalRaceWins'] >= min_value]
    else:
        df.sort_values(by='totalPodiums', ascending=False, inplace=True)
        df = df.loc[df['totalPodiums'] >= min_value]
    return dcc.Dropdown(
    id='dropdown',
    options = [{'label': value, 'value': value} for index,value in df['fullName'].items() ],
    value=df['fullName'].iloc[0],
    multi=True,
    style={'marginBottom': 10, 'marginTop': 2, 'text-align': 'center'}
    )

def createSlider():
    return dcc.Slider(
        id='teams-slider',
        min=0,
        max=32,
        step=1,
        value=1,
        marks={i: str(i) for i in range(32)},
    )


def createWinConstructorPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalChampionshipWins'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalChampionshipWins', 
                color_discrete_sequence =[utility.colors["count_position_1"]]*len(df),
                color_discrete_map=utility.colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},)
    utility.figDesign(fig, "Total Championship Wins")
    fig.update_yaxes(title_text='Total Championship Wins')
    fig.update_xaxes(title_text='Team Name')
    fig.update_traces(
        hovertemplate="<br>".join([
            "Team Name: %{x}",
            "Total Championship Wins: %{y}",
        ])
    )
    return fig

def createRaceConstructPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='bestRaceResult', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['bestRaceResult'] <= min_value]
    fig = px.bar(df, x='fullName', y='bestRaceResult',
                color_discrete_sequence =[utility.colors["count_position_1"]]*len(df),
                color_discrete_map=utility.colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},)
    utility.figDesign(fig, "Best Race Result")
    return fig

def createRaceWinPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalRaceWins'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalRaceWins',
                color_discrete_sequence =[utility.colors["count_position_1"]]*len(df),
                color_discrete_map=utility.colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},)
    utility.figDesign(fig, "Total Race Win")
    fig.update_yaxes(title_text='Total Race Win')
    fig.update_xaxes(title_text='Team Name')
    fig.update_traces(
        hovertemplate="<br>".join([
            "Team Name: %{x}",
            "Total Race Win: %{y}",
        ])
    )
    return fig

def createTotalPodiumPlot(min_value = 1):
    df = getTeamsData()
    df.sort_values(by='totalPodiums', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    print(min_value)
    df = df.loc[df['totalPodiums'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalPodiums',
                color_discrete_sequence =[utility.colors["count_position_1"]]*len(df),
                color_discrete_map=utility.colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},)
    utility.figDesign(fig, "Total podiums for costructor")
    fig.update_yaxes(title_text='Total podiums')
    fig.update_xaxes(title_text='Team Name')
    fig.update_traces(
        hovertemplate="<br>".join([
            "Team Name: %{x}",
            "Total podiums: %{y}",
        ])
    )
    return fig
    

def creteNumTeamsEntrantsForYear():
    df = getEntrantsTeamsData()
    df = df['year'].value_counts().reset_index()
    df.columns = ['year', 'value']
    df.sort_values(by="year", inplace=True)  
    print(df) 
    fig = px.line(df, 
                  x="year",
                  y="value", 
                  title="GP for year", 
                  markers = True, 
                  color_discrete_sequence=f1db_utils.custom_colors,
                  height=400)
    fig.update_yaxes(title_text='#Constructor')
    fig.update_xaxes(title_text='Team Name')
    fig.update_traces(
        hovertemplate="<br>".join([
            "Year: %{x}",
            "Num of Teams: %{y}",
        ])
    )

    utility.figDesign(fig, "Total teams for year")

    return fig

def createCostructorGeo():
    [df1, df2] = getGeoData()
    print(df2)

    df = pd.DataFrame(columns=['Teams', 'Country', 'Continent','code'])
    for index, value in df1['fullName'].items():
        
        countrieId = df1["countryId"][index]
        
        alpha3Code = df2.loc[df2['id'] == countrieId, "alpha3Code"]
        continent = df2.loc[df2['id'] == countrieId, "continentId"]
        if not alpha3Code.empty:
            if not continent.empty:
                continent = continent.iloc[0]
                alpha3Code = alpha3Code.iloc[0]
                df = df._append({'Teams': value, 'Country':countrieId, 'Continent': continent, 'code': alpha3Code}, ignore_index=True)

    df_grouped = df.groupby(['code', 'Country']).agg({'Continent': 'first','Teams': lambda x: '<br> '.join(map(str, x))}).reset_index()
    print(df_grouped)

    # Creare il plot
    fig = px.scatter_geo(df_grouped, locations='code', color='Continent', hover_name='Country', hover_data={'Teams': True, 'code': False}, height=400)

    utility.figDesign(fig, "Constructor Position")

    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showland=True, 
        landcolor="rgb(200,212,227)",
        projection_type='orthographic',
        showcoastlines=True,
        resolution=110
    ),
    
    return fig

def createConstructorTrend(graph_info, teamName):
    df = getTeamsData()
    if isinstance(teamName, str):
        teamName = [teamName]
    df = df.loc[df['fullName'].isin(teamName)]
    match graph_info:
        case 'win':
            df2 = getExtraTeamData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[df2['positionNumber'] == 1].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            fig = px.line(df2, 
                          x='year', 
                          y='RowNumber', 
                          color='constructorId', 
                          color_discrete_sequence=f1db_utils.custom_colors, 
                          markers=True)
            fig.update_yaxes(title_text='# Championship Win')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                 hovertemplate="<br>".join([
                    "Date: %{x}",
                    "Total Championship Win: %{y}",
                ])
             )

        case 'win race':
            [df2, df3] = getRaceTeamsData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[df2['positionNumber'] == 1].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            df3 = df3[df3['id'].isin(df2['raceId'])]
            df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')
            fig = px.line(df2, 
                          x='date', 
                          y='RowNumber', 
                          color='constructorId', 
                          color_discrete_sequence=f1db_utils.custom_colors,
                          markers=True)
            fig.update_yaxes(title_text='# Race Win')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                 hovertemplate="<br>".join([
                    "Date: %{x}",
                    "Total Race Win: %{y}",
                ])
             )
        
        case 'podiums':
            [df2, df3] = getRaceTeamsData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[(df2['positionNumber'] == 1) | (df2['positionNumber'] == 2) | (df2['positionNumber'] == 3)].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            df3 = df3[df3['id'].isin(df2['raceId'])]
            df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')
            print(df2)
            fig = px.line(df2, 
                          x='date', 
                          y='RowNumber', 
                          color='constructorId', 
                          color_discrete_sequence=f1db_utils.custom_colors,
                          markers=True)
            fig.update_yaxes(title_text='# Podiums')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                 hovertemplate="<br>".join([
                    "Date: %{x}",
                    "Total Podiums: %{y}",
                ])
             )
    
   
    utility.figDesign(fig, f'{teamName} Trend')
    return fig

"""
df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalRaceWins'] >= min_value]
"""