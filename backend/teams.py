# File      BACKEND | TEAMS
# Author    Maurizio Meschi

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

# Get constructors data
def getTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-constructors.csv')
    
    return df

# Get entrants constructors data for season
def getEntrantsTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-seasons-entrants-constructors.csv')
        
    return df

# Get countries data
def getGeoData():
    df1 = getTeamsData()
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df2 = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-countries.csv')

    return [df1,df2]

# Get seasons constructor standings data
def getExtraTeamData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-seasons-constructor-standings.csv')

    return df

# Get races data
def getRaceTeamsData():
    current_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_path)

    df = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-races-race-results.csv')
    df2 = pd.read_csv(directory_path + "/../f1db-csv/" + 'f1db-races.csv')

    return [df,df2]


# Create radio buttons to display WCCs, wins, podiums
def createRadioButton():
    return dbc.RadioItems(
                      options=[
                          {"label":"WCCs", "value":"win"}, 
                          {"label":"Wins", "value":"win race"},
                          {"label":"Podiums", "value":"podiums"}
                      ],
                      value="win",
                      inline=True,
                      id="radio-input-teams"
                )

# Create radio buttons to display absolute or Constructor's Trend
def createRadioButtonGraph():
    return dbc.RadioItems(
                      options=[
                          {"label":"Absolute", "value":"absolute"},
                          {"label":"Constructor's Trend", "value":"trend"}
                      ],
                      value="absolute",
                      inline=True,
                      id="radio-input-graph",
                )

# Create the dropdown to choose the Teams on which to view the information
def createDropdown(radio_value = 'win'):
    df = getTeamsData()
    if (radio_value == 'win'):
        df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
        df = df.loc[df['totalChampionshipWins'] > 0]
    elif (radio_value == 'win race'):
        df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
        df = df.loc[df['totalRaceWins'] > 0]
    else:
        df.sort_values(by='totalPodiums', ascending=False, inplace=True)
        df = df.loc[df['totalPodiums'] > 0]
        
    return dcc.Dropdown(
        id='dropdown',
        options=[{"label":row["fullName"], "value": row["id"]} for row in df.to_dict(orient="records")],
        value=df['id'].iloc[0],
        multi=True,
        style={'marginBottom': 10, 'marginTop': 2, 'text-align': 'center'}
    )

# Crate slider with default value
def createSlider():
    return dcc.Slider(
        id='teams-slider',
        min=0,
        max=32,
        step=1,
        value=1,
        marks={i: str(i) for i in range(32)},
    )

# Crate slider value
def updateSliderValue():
    SliderValue = {
        "win_max_slider": 0,
        "win_race_max_slider": -10,
        "podiums_max_slider": [-10,50]
    }
    df = getTeamsData()
    df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
    SliderValue['win_max_slider'] = df['totalChampionshipWins'].max()

    #df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    SliderValue['win_race_max_slider'] = df['totalRaceWins'].max()

    [df2, df3] = getRaceTeamsData()
    df2 =df2.loc[(df2['positionNumber'] == 1) | (df2['positionNumber'] == 2) | (df2['positionNumber'] == 3)].reset_index()
    df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
    
    df3 = df3[df3['id'].isin(df2['raceId'])]
    df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')
    df2 = df2['constructorId'].value_counts().reset_index()
    df2.columns = ['name', 'totalPodiums']
    SliderValue['podiums_max_slider'] = df2['totalPodiums'].max()
    return SliderValue


# Create the bar char to display WCCs
def createWinConstructorPlot(min_value = 1):
    df = getTeamsData()
    df.sort_values(by='totalChampionshipWins', ascending=False, inplace=True)
    # Set default value
    if (min_value is None):
        min_value = 1
    # Extract only the teams that have won x championships
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

# Create the bar char to display win races
def createRaceWinPlot(min_value = 0):
    df = getTeamsData()
    df.sort_values(by='totalRaceWins', ascending=False, inplace=True)
    # Set default value
    if (min_value is None):
        min_value = 1
        # Extract only the teams that have won x race
    df = df.loc[df['totalRaceWins'] >= min_value]
    
    fig = px.bar(df, x='fullName', y='totalRaceWins',
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map = f1db_utils.podium_colors,
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

# Create the bar char to display total podiums
def createTotalPodiumPlot(min_value = 1):
    [df2, df3] = getRaceTeamsData()
    # Get only the teams that finished first, second or third in the race
    df2 =df2.loc[(df2['positionNumber'] == 1) | (df2['positionNumber'] == 2) | (df2['positionNumber'] == 3)].reset_index()
    df2['RowNumber'] = df2.groupby('constructorId').cumcount() + 1
    df3 = df3[df3['id'].isin(df2['raceId'])]
    df2 = df2.merge(df3, left_on='raceId', right_on='id', how='left')
    df2 = df2['constructorId'].value_counts().reset_index()
    df2.columns = ['constructorId', 'totalPodiums']
    df2 = df2.loc[df2['totalPodiums']>= min_value]
    
    df_constructors_info = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.constructors}")
    df_constructors_info.rename(columns={"id":"constructorId"}, inplace=True)
    df_constructors_info.drop(columns=df_constructors_info.columns.difference(["constructorId", "fullName"]), inplace=True)
    df2 = pd.merge(df2, df_constructors_info, on="constructorId", how="left")
    
    # Create a bar chart
    fig = px.bar(df2, x='fullName', y='totalPodiums',
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df2),
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
    

# Create the bar char to display WCCs
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
        title=f1db_utils.getTitleObj("Number of Teams Over the Year"),
        margin=f1db_utils.margin
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

# Create the scatter geo to display the distribution of Teams Around the World
def createCostructorGeo():
    [df1, df2] = getGeoData()
  
    # Create a new dataframe to store data of interest from different dfs
    df = pd.DataFrame(columns=['Teams', 'Country', 'Continent','code'])

    # Storage country, alpha3Code and continent
    for index, value in df1['fullName'].items():
        countryId = df1["countryId"][index]
        alpha3Code = df2.loc[df2['id'] == countryId, "alpha3Code"]
        continent = df2.loc[df2['id'] == countryId, "continentId"]
        if not alpha3Code.empty:
            if not continent.empty:
                continent = continent.iloc[0]
                alpha3Code = alpha3Code.iloc[0]
                # Add the row to the new df
                df = df._append({'Teams': value, 
                                 'Country': countryId, 
                                 'Continent': continent, 
                                 'code': alpha3Code}, 
                                 ignore_index=True)
    
    df_count = df['Country'].value_counts().reset_index()
    df_count.columns = ['Country', 'count']
    
    def format_team_info(team_info):
        max_display = 15
        if len(team_info) > max_display:
            return '<br>'.join([f"{item['Teams']}" for item in team_info[:max_display]]) + f'<br><i>and {len(team_info) - max_display} more</i><extra></extra>'
        else:
            return '<br>'.join([f"{item['Teams']}" for item in team_info]) + '<extra></extra>'
    
    df_grouped = df.groupby(['Country']).apply(
        lambda x: [{'Teams': row['Teams']} for idx, row in x.iterrows()]
    ).reset_index(name='Teams')
    df_grouped["Teams"] = df_grouped["Teams"].apply(format_team_info)
    df_grouped = df_grouped.merge(df_count, on='Country', how='left')

    df_countries = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.countries}")
    df_countries.rename(columns={"id":"Country", "name":"countryName", "alpha3Code": "code"}, inplace=True)
    df_countries.drop(columns=df_countries.columns.difference(["Country", "countryName", "continentId", "code"]), inplace=True)
    df_grouped = pd.merge(df_grouped, df_countries, on="Country", how="left")
    
    df_continents = pd.read_csv(f"{f1db_utils.folder}/{f1db_utils.continents}")
    df_continents.rename(columns={"id":"continentId", "name":"continentName"}, inplace=True)
    df_continents.drop(columns=df_continents.columns.difference(["continentId", "continentName"]), inplace=True)
    df_grouped = pd.merge(df_grouped, df_continents, on="continentId", how="left")

    fig = px.scatter_geo(
        df_grouped, 
        locations='code', 
        color='continentName',
        size='count', 
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
        title = f1db_utils.getTitleObj("Distribution of Teams Around the World"),
        margin=f1db_utils.margin_geo
    ).update_traces(
        hoverlabel=f1db_utils.getHoverlabel(13)
    ).update_geos(f1db_utils.update_geos).update_geos(resolution=110)
    
    return fig

# Create graphs to visualize team trends
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
                color_discrete_map = {
                    "Scuderia Ferrari": f1db_utils.F1_RED,
                    "Red Bull Racing": "#6A76FC",
                    "McLaren Racing": "#FD8000",
                    "Mercedes AMG F1": "#00A09C",
                    "Aston Martin": "#00594F"
                },
                hover_data = {
                    "fullName": True
                }
            ).update_layout(hovermode="x", title=f1db_utils.getTitleObj("WCCs Trend"),margin=dict(b=60))
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
                color_discrete_map = {
                    "Scuderia Ferrari": f1db_utils.F1_RED,
                    "Red Bull Racing": "#6A76FC",
                    "McLaren Racing": "#FD8000",
                    "Mercedes AMG F1": "#00A09C",
                    "Aston Martin": "#00594F"
                },
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

            df2 = f1db_utils.order_df(df2, "constructorId", teamName)
            fig = px.line(df2, 
                x='date', 
                y='RowNumber', 
                color='fullName', 
                color_discrete_sequence=f1db_utils.custom_colors,
                markers=True,
                template=f1db_utils.template,
                labels=labels_dict,
                color_discrete_map = {
                    "Scuderia Ferrari": f1db_utils.F1_RED,
                    "Red Bull Racing": "#6A76FC",
                    "McLaren Racing": "#FD8000",
                    "Mercedes AMG F1": "#00A09C",
                    "Aston Martin": "#00594F"
                },
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