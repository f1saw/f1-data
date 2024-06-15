# File      BACKEND | TEAMS
# Authors   Maurizio Meschi

import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import os
from datetime import datetime
import backend.f1db_utils as f1db_utils

labels_dict = {
    "fullName": "Constructor",
    "continentName": "Continent"
}

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
                          {"label":"WCCs", "value":"win"}, # opzione boxplot
                          #{"label":"Best Race Result", "value":"best race"},
                          {"label":"Wins", "value":"win race"},
                          {"label":"Podiums", "value":"podiums"}
                      ],
                      # Impostiamo il valore di default
                      value="win",
                      # inline = True mette i 3 bottoni in linea invece che verticale
                      inline=True,
                      id="radio-input-teams"
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
        # options = [{'label': value, 'value': value} for index,value in df['fullName'].items() ],
        options=[{"label":row["fullName"], "value": row["id"]} for row in df.to_dict(orient="records")],
        value=df['id'].iloc[0],
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

def updateSliderValue():
    SliderValue = {
        "win_max_slider": 0,
        "win_race_max_slider": -10,
        "podiums_max_slider": [-10,50]
    }
    df = getTeamsData()
    df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
    SliderValue['win_max_slider'] = df['totalChampionshipWins'].max()

    df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    SliderValue['win_race_max_slider'] = df['totalRaceWins'].max()

    df = getTeamsData()
    df.sort_values(by='totalPodiums', ascending=False, inplace=True)
    SliderValue['podiums_max_slider'] = df['totalPodiums'].max()
    return SliderValue


def createWinConstructorPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalChampionshipWins'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalChampionshipWins', 
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map=f1db_utils.podium_colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},
                template=f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        hovermode="x"
    )
    fig.update_yaxes(title_text='Number of WCCs')
    fig.update_xaxes(title_text='Team')
    fig.update_traces(
        hoverlabel=f1db_utils.getHoverlabel(),
        hovertemplate="<br>".join([           
            "<b>%{y}</b><extra></extra>",
        ])
    )
    return fig


def createRaceWinPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalRaceWins'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalRaceWins',
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map=f1db_utils.podium_colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},
                template=f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        hovermode="x"
    )
    fig.update_yaxes(title_text='Number of Wins')
    fig.update_xaxes(title_text='Team')
    fig.update_traces(
        hoverlabel=f1db_utils.getHoverlabel(),
        hovertemplate="<br>".join([           
            "<b>%{y}</b><extra></extra>",
        ])
    )
    return fig

def createTotalPodiumPlot(min_value = 1):
    df = getTeamsData()
    df.sort_values(by='totalPodiums', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    # print(min_value)
    df = df.loc[df['totalPodiums'] >= min_value]
    fig = px.bar(df, x='fullName', y='totalPodiums',
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map=f1db_utils.podium_colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},
                template=f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        hovermode="x"
    )
    fig.update_yaxes(title_text='Number of Podiums')
    fig.update_xaxes(title_text='Team')
    fig.update_traces(
        hoverlabel=f1db_utils.getHoverlabel(),
        hovertemplate="<br>".join([           
            "<b>%{y}</b><extra></extra>",
        ])
    )
    return fig
    

def creteNumTeamsEntrantsForYear():
    df = getEntrantsTeamsData()
    df = df['year'].value_counts().reset_index()
    df.columns = ['year', 'value']
    df.sort_values(by="year", inplace=True)  
    # print(df) 
    fig = px.line(df, 
                  x="year",
                  y="value", 
                  markers = True, 
                  color_discrete_sequence=f1db_utils.custom_colors,
                  template = f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        hovermode="x", 
        title=f1db_utils.getTitleObj("Number of Teams Over the Year")
    )
    fig.update_yaxes(title_text='Number of Teams')
    fig.update_xaxes(title_text='Year')
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{y}</b><extra></extra>",
        ]),
        hoverlabel = f1db_utils.getHoverlabel(13)
    )


    return fig

def createCostructorGeo():
    [df1, df2] = getGeoData()
    # print(df2)

    df = pd.DataFrame(columns=['Teams', 'Country', 'Continent','code'])
    for index, value in df1['fullName'].items():
        
        countryId = df1["countryId"][index]
        
        alpha3Code = df2.loc[df2['id'] == countryId, "alpha3Code"]
        continent = df2.loc[df2['id'] == countryId, "continentId"]
        if not alpha3Code.empty:
            if not continent.empty:
                continent = continent.iloc[0]
                alpha3Code = alpha3Code.iloc[0]
                df = df._append({'Teams': value, 'Country':countryId, 'Continent': continent, 'code': alpha3Code}, ignore_index=True)

    df_grouped = df.groupby(['code', 'Country']).agg({'Continent': 'first','Teams': lambda x: '<br> '.join(map(str, x))}).reset_index()
    
    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.rename(columns={"id":"Country", "name":"countryName"}, inplace=True)
    df_countries.drop(columns=df_countries.columns.difference(["Country", "countryName", "continentId"]), inplace=True)
    df_grouped = pd.merge(df_grouped, df_countries, on="Country", how="left")
    
    df_continents = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.continents}")
    df_continents.rename(columns={"id":"continentId", "name":"continentName"}, inplace=True)
    df_continents.drop(columns=df_continents.columns.difference(["continentId", "continentName"]), inplace=True)
    df_grouped = pd.merge(df_grouped, df_continents, on="continentId", how="left")
    # print(df_grouped.head())

    # Creare il plot
    # TODO => manca la size in funzione della quantità di teams in quella nazione
    fig = px.scatter_geo(
        df_grouped, 
        locations='code', 
        color='continentName', 
        labels=labels_dict,
        hover_name='countryName', 
        hover_data={'Teams': True, 'code': False}, 
        template = f1db_utils.template,
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
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Spread of Teams Around the World"),
    ).update_traces(
        hoverlabel=f1db_utils.getHoverlabel(13)
    ).update_geos(f1db_utils.update_geos).update_geos(resolution=110)
    
    return fig

def createConstructorTrend(graph_info, teamName):
    if not teamName: return f1db_utils.warning_empty_dataframe
    
    df = getTeamsData()
    if isinstance(teamName, str):
        teamName = [teamName]
    df = df.loc[df['id'].isin(teamName)]
    
    match graph_info:
        case 'win':
            df2 = getExtraTeamData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[df2['positionNumber'] == 1].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            
            df.rename(columns={"id":"constructorId"}, inplace=True)
            df2 = pd.merge(df2, df, on="constructorId", how="left")
            
            df2 = f1db_utils.order_df(df2, "constructorId", teamName)
            fig = px.line(df2, 
                x='year', 
                y='RowNumber', 
                color='fullName', 
                color_discrete_sequence=f1db_utils.custom_colors, 
                markers=True,
                template=f1db_utils.template,
                labels=labels_dict,
                hover_data = {
                    "fullName": True
                }
            ).update_layout(hovermode="x", title=f1db_utils.getTitleObj("WCCs Trend"))
            fig.update_yaxes(title_text='Number of WCCs')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                hovertemplate="<br>".join([
                    "<b>%{customdata}</b> (<b>%{y})</b><extra></extra>",
                ]),
                hoverlabel = f1db_utils.getHoverlabel(13)
             )

        case 'win race':
            [df2, df3] = getRaceTeamsData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[df2['positionNumber'] == 1].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            
            df.rename(columns={"id":"constructorId"}, inplace=True)
            df2 = pd.merge(df2, df, on="constructorId", how="left")
            
            df3 = df3[df3['id'].isin(df2['raceId'])]
            df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')
            df2 = f1db_utils.order_df(df2, "constructorId", teamName)
            fig = px.line(df2, 
                x='date', 
                y='RowNumber', 
                color='fullName', 
                color_discrete_sequence=f1db_utils.custom_colors,
                markers=True,
                template=f1db_utils.template,
                labels=labels_dict,
                hover_data = {
                    "fullName": True
                }).update_layout(hovermode="x", title=f1db_utils.getTitleObj("Wins Trend"))
            fig.update_yaxes(title_text='Number of Wins')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                hovertemplate="<br>".join([
                    "<b>%{customdata}</b> (<b>%{y})</b><extra></extra>",
                ]),
                hoverlabel = f1db_utils.getHoverlabel(13)
             )
        
        case 'podiums':
            [df2, df3] = getRaceTeamsData()
            df2 = df2[df2['constructorId'].isin(df['id'])]
            df2 =df2.loc[(df2['positionNumber'] == 1) | (df2['positionNumber'] == 2) | (df2['positionNumber'] == 3)].reset_index()
            df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
            
            df.rename(columns={"id":"constructorId"}, inplace=True)
            df2 = pd.merge(df2, df, on="constructorId", how="left")
            
            df3 = df3[df3['id'].isin(df2['raceId'])]
            df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')

            #print(df2)
            df2 = f1db_utils.order_df(df2, "constructorId", teamName)
            fig = px.line(df2, 
                x='date', 
                y='RowNumber', 
                color='fullName', 
                color_discrete_sequence=f1db_utils.custom_colors,
                markers=True,
                template=f1db_utils.template,
                labels=labels_dict,
                hover_data = {
                    "fullName": True
                }).update_layout(hovermode="x", title=f1db_utils.getTitleObj("Podiums Trend"))
            fig.update_yaxes(title_text='Number of Podiums')
            fig.update_xaxes(title_text='Year')
            fig.update_traces(
                hovertemplate="<br>".join([
                    "<b>%{customdata}</b> (<b>%{y})</b><extra></extra>",
                ]),
                hoverlabel = f1db_utils.getHoverlabel(13)
             )

    fig.update_layout(
        f1db_utils.transparent_bg
    )
    return fig

"""
df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    if (min_value is None):
        min_value = 1
    df = df.loc[df['totalRaceWins'] >= min_value]
"""