import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import numpy as np

import backend.season as season
import backend.drivers as drivers
import backend.circuits as circuits
import backend.f1db_utils as f1db_utils
import backend.teams as teams

# TODO chiamata a get-data.py (solo se passata più di una 5 giorni dall'ultima lettura OPPURE fare ogni lunedì se non già fatto lo stesso giorno)
# leggere da ./f1db-csv/


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)





# TODO => do useful structure like tabs = ["seasons": [array_of_graphs], "circuits": [array_of_graphs], ...]
# TODO => fare labels con dizionario e for figo
# ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
drivers_template = "plotly_dark" # TODO => put them in utils.py
transparent_bg = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)"
}
warning_empty_dataframe = {
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [{
            "text": "No matching data found",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 28}
        }]
    }
}

def getTitleObj(titleStr):
    return {
        "text": titleStr,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 18 }
    }


# Needed to handle hovertemplate properly
def format_driver_info(driver_info):
    max_display = 5 # TODO => make it as a const
    if len(driver_info) > max_display:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info[:max_display]]) + f'<br>and {len(driver_info) - max_display} more'
    else:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info])
    
# drivers.drivers_dfs["worldSpread"].sort_values(by="driverName", inplace=True)
driver_info = drivers.drivers_dfs["worldSpread"].groupby(['nationalityCountryId','year']).apply(
    lambda x: [{'driverName': row['driverName']} for idx, row in x.iterrows()]
).reset_index(name='driverInfo')

drivers.drivers_dfs["worldSpread"] = pd.merge(drivers.drivers_dfs["worldSpread"], driver_info, on=['nationalityCountryId','year'], how="left")
drivers.drivers_dfs["worldSpread"]['driverInfo'] = drivers.drivers_dfs["worldSpread"]['driverInfo'].apply(format_driver_info)

drivers.drivers_dfs["worldSpread"].sort_values(by="year", inplace=True)
# print(drivers.drivers_dfs["worldSpread"][drivers.drivers_dfs["worldSpread"]["alpha3Code"] == "GBR"].tail(10))




# DRIVERS STATIC FIGURES (TODO => maybe put them in frontend file)
drivers_figures = {
    "numDriversPerYear" : px.line(
        drivers.drivers_dfs["numDriversPerYear"],
        x = "year",
        y = ["officialDriver","testDriver"],
        markers = True,
        color_discrete_sequence=f1db_utils.custom_colors,
        labels = {
            "value": "Number of Drivers",
            "variable": "Driver Type",
            "year": "Year"
        },
        hover_data = {
            "variable": False,
            "year": False
        },
        template = drivers_template
    ).for_each_trace(lambda t: t.update(name = drivers.driver_type[t.name]))
    .update_layout(
        transparent_bg,
        title = getTitleObj("Number of Official Drivers and Test Drivers Over the Years"),
        hovermode = "x"
    ),
    "worldSpread": px.scatter_geo(
        drivers.drivers_dfs["worldSpread"], 
        locations = "alpha3Code", 
        color = "continentName",
        hover_name = "countryName", 
        size = "count_display",
        animation_frame = "year",
        projection = "natural earth",
        labels = {
            "continentName": "Continent",
            "year": "Year",
            "count_display": "Number of Drivers",
            "countryName": "Country",
            "count": "Number of Drivers",
            "driverInfo": "Drivers"
        },
        hover_data = {
            'countryName': True,
            'continentName': True,
            'count': True,
            'driverInfo': True,
            "alpha3Code": False,
            "year": False
        },
        category_orders = {
            # "continentName": ["Europe"]
        },
        template = drivers_template
    ).update_layout(
        transparent_bg,
        height=500,
        title = {
            "text": "Spread of Drivers' Nationalities Over the Years",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18 }
        },
    ).update_geos(
        bgcolor="rgba(0,0,0,0)",
        showland=True, 
        landcolor="rgb(200,212,227)",
        projection_type='orthographic',
        showcoastlines=True,
        resolution=50 # Slow but otherwise (110), smaller countries (e.g. Monaco) will not be displayed
    ), 
}
drivers_figures["worldSpread"].data[0].customdata = drivers.drivers_dfs["worldSpread"][["countryName", "continentName", "count"]].values.tolist()

CUSTOM_HOVERTEMPLATE = '<b>%{customdata[0]}</b>, %{customdata[1]}<br><br><b>%{customdata[2]}</b><br>%{customdata[3]}'
drivers_figures["worldSpread"].update_traces(hovertemplate=CUSTOM_HOVERTEMPLATE)
for frame in drivers_figures["worldSpread"].frames:
    for data in frame.data:
        data.hovertemplate = CUSTOM_HOVERTEMPLATE
        


# TABS STRUCTURE
tabs = ["seasons", "circuits", "drivers", "teams"]
tabs_children = []
for idx, tab in enumerate(tabs):
    tabs_children.append(dcc.Tab(
        label = tab.upper(),
        value = f"tab-{idx}-{tab}",
        className = "custom-tab",
        selected_className = "custom-tab--selected"
    ))


# LAYOUT BUILDER

app.layout = html.Div([
    html.H1([
        html.Span('F', style={'color': 'red'}),
        html.Span('1-DATA', style={'color': 'white'}),
        #html.Span('A', style={'color': 'red'}),
    ],className="text-center fw-bold m-3"),
    html.Div([
        dcc.Tabs(id="tabs-graph", 
            value=tabs_children[2].value, 
            children=tabs_children, 
            parent_className='custom-tabs', className='pt-5 custom-tabs-container',
            colors={
                "border": "transparent",
                "primary": "orange",
                "background": "rgb(33,37,41)"
            }),
        html.Div(id='tabs-content-graph')
    ], className="d-flex flex-column-reverse justify-content-between"),
], className="p-2 bg-dark vh-100") # overflow-hidden


## CALLBACKS
@callback(Output('tabs-content-graph', 'children'),
            Input('tabs-graph', 'value'))
def render_content(tab):
    match tab:
        # SEASONS
        case 'tab-0-seasons':
            return html.Div([
                #html.H3('Tab content 1'),
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(id="season_GP_graph", figure=season.createSeason_GP_Plot())
                    ),
                    dbc.Col(
                        dcc.Graph(id="season_Geo_graph", figure=season.createSeasonGeo())
                    )
                ]),
                html.Div(
                    season.crateDriverElement([1950, 1955]),
                    id="range_div"
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(id="season_graph") #figure=season.createSeasonDriverPlot())
                    )
                )
            ], className="d-flex flex-column justify-content-between gap-2")
            
        # CIRCUITS
        case 'tab-1-circuits':
            return html.Div([
                dbc.Row([
                    dbc.Col(
                        dbc.Stack([
                            dbc.Row([
                                dbc.Col(html.Label("Min Value"), width=2),
                                dbc.Col(circuits.circuits_gp_held_min_value, width=7) 
                            ], className="d-flex justify-content-center"),
                            dcc.Graph(id="circuits-gp-held")
                        ]), width=6
                    ), dbc.Col(
                        dbc.Stack([ 
                            dbc.Row([
                                html.Label("Qualifying Position Range"),
                                circuits.quali_race_range
                            ]),
                            dcc.Graph(id="circuits-quali-race-results")
                        ]), width=6)
                ]),
                html.Br(),
                dbc.Stack([
                    dbc.Row([dbc.Col(circuits.circuits_dropdown, width=3)], className="d-flex justify-content-center"),
                    dcc.Graph(id='circuits-qualifying', figure=drivers_figures['numDriversPerYear'])
                ])
            ])
            
            
            
            
            
            
        # DRIVERS
        case 'tab-2-drivers':
            return html.Div([
                # html.H3('Tab content 2'),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='drivers-line', figure=drivers_figures['numDriversPerYear']), width=6),
                    dbc.Col(dcc.Graph(id="drivers-world", figure=drivers_figures['worldSpread']), width=6)
                ]),
                dbc.Stack([
                    dbc.Row([
                        dbc.Col([
                            dbc.Stack([
                                html.Label("Type of Graph"),
                                drivers.drivers_performance_type_graph_radio
                            ], direction="horizontal", gap=3),
                            dbc.Stack([
                                html.Label("Performance Type"),
                                drivers.drivers_performance_type_radio
                            ], direction="horizontal", gap=3),
                        ], width=4),
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(html.Label("Min Value"), width=2),
                                dbc.Col(drivers.drivers_performance_min_value, width=7) 
                            ], id="drivers-min-value-id"),
                            dbc.Col(drivers.drivers_performance_dropdown, width=9)
                        ], width=4)
                    ]),
                    dcc.Graph(id="drivers-performance")
                ])
            ])
            
            
            
        # TEAMS
        case 'tab-3-teams':
            return html.Div([
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(id="entrants_teams_graph", figure=teams.creteNumTeamsEntrantsForYear())
                    ),
                    dbc.Col(
                        dcc.Graph(id="geo_teams_graph", figure=teams.createCostructorGeo())
                    )
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                    dbc.Stack([
                                html.Label("Type of Graph"),
                                teams.createRadioButtonGraph()
                            ], direction="horizontal", gap=3),
                    width=3),
                    dbc.Col(
                        teams.createDropdown(),
                        width=6,
                        id = "dropdown_col"
                    ),
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Stack([
                                html.Label("Performance Type"),
                                teams.createRadioButton(),
                        ], direction="horizontal", gap=3),
                        width=3),
                    dbc.Col(
                        teams.createSlider()
                         #style={'marginRight': 30}
                    )
                ],style={'marginRight': 38, 'marginLeft': 42}),
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(id="teams_graph", figure=teams.createWinConstructorPlot())
                    )
                )
            ], className="container-fluid")
        
        # DEFAULTS
        case _:
             return html.Div([])
        


# =================1================= SEASONS
@callback(Output('dropdown_drivers', 'options'),
               Input('range-slider', 'value'))
def update_dropdown(slider_value):
        return season.updateDropDownDrivers(slider_value)



@callback(Output('season_graph', 'figure'),
              [Input('radio-input', 'value'),
               Input('range-slider', 'value'),
               Input('dropdown_drivers', 'value'),
               Input('dropdown_drivers', 'options')])
def update_graph(radio_value, range_value, driver, option):
    print(option[0]['value'])
    if(driver == []):
        driver = [option[0]['value'], option[3]['value']]
    return season.createSeasonDriverPlot(radio_value, range_value, driver) 
 
#### 
# 
#  CALLBACK TEAMS
#   
@callback(Output('teams_graph', 'figure'),
             [Input('radio-input-teams', 'value'),
              Input('teams-slider', 'value'),
              Input('radio-input-graph', 'value'),
              Input('dropdown', 'value')])
def update_teams_graph(radio_value, slider_value, radio_graph_value, dropdown_value):
    if (radio_graph_value == 'trend'):
        return teams.createConstructorTrend(radio_value, dropdown_value)
    else:
        if (radio_value == 'win'):
            return teams.createWinConstructorPlot(slider_value)
        #elif(radio_value == "best race"):
        #   return teams.createRaceConstructPlot(slider_value)
        elif(radio_value == "win race"):
            return teams.createRaceWinPlot(slider_value)
        else:
            return teams.createTotalPodiumPlot(slider_value)

# TODO -> prendere dinamicamente i valori 16, 32 etc
@app.callback(
    [Output('teams-slider', 'max'),
     Output('teams-slider', 'min'),
     Output('teams-slider', 'marks'),
     Output('teams-slider', 'value')],
        Input('radio-input-teams', 'value'))
def update_teams_slider(radio_input):
    value = teams.updateSliderValue()
    if (radio_input == "win"):
        return value['win_max_slider'], 1, {0:"1", str(value['win_max_slider']):str(value['win_max_slider'])}, 1
    elif(radio_input == "win race"):
        return value['win_race_max_slider'], 1, {0:"1", str(value['win_race_max_slider']):str(value['win_race_max_slider'])}, 1
    else:
        return value['podiums_max_slider'], 1, {0:"1", str(value['podiums_max_slider']):str(value['podiums_max_slider'])}, 1


@callback(Output('dropdown_col', 'children'),
             [Input('teams-slider', 'value'),
              Input('radio-input-teams', 'value')])
def update_option_dropdown(slider_value, radio_value):
    return teams.createDropdown(slider_value, radio_value)

# =================1================= 






# =================2================= CIRCUITS
circuits_vars = {
    "gp_held_max": 1,
    "quali_race_range_min": -10,
    "quali_race_range": [-10,50],
    "quali_race_range_max": 50,
}
@app.callback(
    [Output("circuits-gp-held-min-value-id", "max"),
    Output("circuits-gp-held-min-value-id", "marks")],
    Input("circuits-gp-held", "figure"))
def circuits_update_slider_marks(figure):
    return [circuits_vars["gp_held_max"], {1:"1", str(circuits_vars["gp_held_max"]):str(circuits_vars["gp_held_max"])}]


# UP-LEFT GRAPH
@app.callback(
    Output("circuits-gp-held", "figure"),
    Input("circuits-gp-held-min-value-id", "value")
)
def circuits_update_gp_held(min_value):
    global circuits_vars
    df = circuits.get_gp_held(min_value)
    circuits_vars["gp_held_max"] = df["totalRacesHeld"].max()
    fig = px.bar(
        df,
        x = "name",
        y = "totalRacesHeld",
        labels = circuits.labels_dict,
        hover_data = {
            "name": False,
            "fullName": False,
            "type": True,
            "countryName": True
        },
        template = drivers_template,
        color_discrete_sequence =[f1db_utils.podium_colors["count_position_2"]]
    ).update_layout(
        transparent_bg,
        title = getTitleObj("Number GP Helds by Circuits"),
        hovermode = "x"
    ) if not df.empty else warning_empty_dataframe
    
    
    return fig




# BOTTOM GRAPH
@app.callback(
    Output("circuits-qualifying", "figure"),
     Input("circuits-dropdown", "value")
)
def circuits_update_qualifying(circuitsIds):
    if not circuitsIds: 
        return warning_empty_dataframe
    
    df = circuits.get_qualifying_times(circuitsIds)

    # Generare i tickvals automaticamente
    tickvals = np.logspace(np.log10(df['timeMillis'].min()), np.log10(df['timeMillis'].max()), num=7, base=10)
    ticktext = [f1db_utils.ms_to_time(val) for val in tickvals]
    
    return px.line(
        df,
        x = "year",
        y = "timeMillis", # pole,
        color = "circuitName",
        markers = True,
        labels = circuits.labels_dict,
        hover_data = {
            "year": False,
            "timeMillis": False,
            "time": True,
            #"officialName": True,
            "qualifyingFormat": True,
            "driverName": True
        },
        color_discrete_sequence=f1db_utils.custom_colors,
        template = drivers_template,
        # TODO per provare a evitare che i colori dei circuiti cambino quando se ne selezionano altri category_orders=
    ).update_layout(
        transparent_bg,
        title = getTitleObj("Pole Lap Time Over the Years"),
        hovermode = "x",
        yaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            tickmode='array',
            title="Lap Time"
        )
    ) if not df.empty else warning_empty_dataframe
    #.for_each_trace(lambda t: t.update(name = drivers.driver_type[t.name])


# UP-RIGHT GRAPH
@app.callback(
    [Output("circuits-quali-race-range-id", "min"),
    Output("circuits-quali-race-range-id", "max")],
    Input("circuits-quali-race-results", "figure")
)
def circuits_update_quali_race(figure):
    return [
        circuits_vars["quali_race_range_min"],
        circuits_vars["quali_race_range_max"]
    ]
    
@app.callback(
    Output("circuits-quali-race-results", "figure"),
    [Input("circuits-dropdown", "value"),
     Input("circuits-quali-race-range-id", "value")]
)
def circuits_update_quali_race(circuitsId, qualiRange):
    if len(circuitsId) == 0: return f1db_utils.warning_empty_dataframe
    # partendo dalle prime 2 file (quattro posizioni o tre) => dove vai a finire
    global circuits_vars
    df = circuits.get_quali_race(circuitsId)
    circuits_vars["quali_race_range_min"] = df["positionQualifying"].min()
    circuits_vars["quali_race_range_max"] = df["positionQualifying"].max()
    
    
    
    # Filter by Qualifying Position Range
    df = df[df['positionQualifying'].isin(list(range(int(qualiRange[0]), int(qualiRange[1])+1)))] 
    df.sort_values(by="raceId", inplace=True, ascending=False)
    
    total_qualifying = df['positionQualifying'].value_counts().reset_index()
    total_qualifying.columns = ['positionQualifying', 'total']

    freq_df = df.groupby(['positionQualifying', 'positionRace']).size().reset_index(name='count')
    freq_df = pd.merge(freq_df, total_qualifying, on='positionQualifying')


    # Needed to handle hovertemplate properly
    def format_race_driver_info(race_driver_info):
        max_display = 5 # TODO => make it as a const
        if len(race_driver_info) > max_display:
            return '<br>'.join([f"{item['officialName']} ({item['driverName']})" for item in race_driver_info[:max_display]]) + f'<br>and {len(race_driver_info) - max_display} more'
        else:
            return '<br>'.join([f"{item['officialName']} ({item['driverName']})" for item in race_driver_info])
        
    race_driver_info = df.groupby(['positionQualifying', 'positionRace']).apply(
        lambda x: [{'officialName': row['officialName'], 'driverName': row['driverName']} for idx, row in x.iterrows()]
    ).reset_index(name='raceDriverInfo')
    freq_df = pd.merge(freq_df, race_driver_info, on=['positionQualifying', 'positionRace'])
    freq_df['raceDriverInfo'] = freq_df['raceDriverInfo'].apply(format_race_driver_info)
    freq_df['count_per_total'] = freq_df['count'] / freq_df['total'] * 100
    
    freq_df.reset_index(inplace=True)
    freq_df.drop(columns=["index"], inplace=True)
    
    tickvals = np.linspace(circuits_vars["quali_race_range_min"], circuits_vars["quali_race_range_max"], circuits_vars["quali_race_range_max"])
    ticktext = [val if val < (circuits_vars["quali_race_range_max"]) else "NQ" for val in tickvals]
                 
    fig = px.scatter(freq_df, 
        x = 'positionQualifying', 
        y = 'positionRace', 
        size = 'count',
        labels = circuits.labels_dict,
        template = drivers_template,
        color_discrete_sequence=f1db_utils.custom_colors
    ).update_layout(
        transparent_bg,
        title = getTitleObj("Qualifying Position vs Race Position"),
        xaxis = {
            'tickvals': tickvals, 
            'ticktext': ticktext  
        }
    ).update_traces(
        hovertemplate='Q: <b>%{x}</b><br>' + 
        'R: <b>%{y}</b><br>' + 
        'Count: <b>%{marker.size}</b> / %{customdata[0]} (<b>%{customdata[1]:.0f}%</b>)<br>' +
        '%{customdata[2]}'
    )
    fig.data[0].customdata = freq_df[['total', 'count_per_total', 'raceDriverInfo']].values
    
    return fig if len(circuitsId) == 1 else warning_empty_dataframe # TODO => empty or TOO MANY CIRCUITS, ONLY ONE ALLOWED FOR THIS GRAPH

# =================2=================





# =================3================= DRIVERS
# IF "absolute" graph => HIDE drivers dropdown | SHOW min value slider
# IF "trend"    graph => SHOW drivers dropdown | HIDE min value slider
@app.callback(
    [Output('drivers-performance-dropdown', 'style'),
     Output('drivers-min-value-id', 'style')],
    Input('drivers-performance-type-graph-id', 'value')
)
def toggle_dropdown(selected_value):
    if selected_value == "absolute":
        return [{'display': 'none'},None]
    else:
        return [None,{'display': 'none'}]
    
    
# Update Drivers Dropdown
@app.callback(
    Output("drivers-performance-dropdown", "options"),
    Input("radio-drivers-performance-type-id", "value"),
)
def update_drivers_dropdown(performance_type):    
    return [
        {"label":row["driverName"], "value": row["driverId"]} for row in drivers.getDrivers(performance_type).to_dict(orient="records")
    ]


# BOTTOM GRAPH
@app.callback(
    [Output("drivers-performance", "figure"),
     Output("drivers-performance-min-value-id", "max"),
     Output("drivers-performance-min-value-id", "marks")],
    [Input("drivers-performance-type-graph-id", "value"),
     Input("radio-drivers-performance-type-id", "value"),
     Input("drivers-performance-min-value-id", "value"),
     Input("drivers-performance-dropdown", "value")]
)
def update_drivers_performance(graph_type, performance_type, min_value, selected_driver):
    # print(f"{graph_type} {performance_type}")
    df = []
    
    max_val = 0
    if (graph_type == "absolute"):
        if (performance_type == drivers.PERFORMANCE_TYPE_DEFAULT and min_value == drivers.MIN_VALUE_DEFAULT):
            df = drivers.drivers_dfs["absolutePerformance"] # standard values, use the one already computed
        else:
            df = drivers.getAbsolutePerformance(
                performance_type, 
                min_value, 
                "count_podiums" if performance_type == f1db_utils.PerformanceType.PODIUMS.value else "count_position_1"
            )
            
        title = f"Most F1 {drivers.drivers_dict[performance_type]}"
        match performance_type:
            case f1db_utils.PerformanceType.WDCS.value | f1db_utils.PerformanceType.WINS.value | f1db_utils.PerformanceType.POLES.value:
                # Keep only 1st place results, already done with poles
                if performance_type != f1db_utils.PerformanceType.POLES.value:
                    df = df[df["count_position_1"] != 0] 
                df.sort_values(by=["count_position_1"], ascending=False, inplace=True)         
                y = "count_position_1"
                drivers.drivers_dict["count_position_1"] = f"Number of {drivers.drivers_dict[performance_type]}"
                max_val = df[y].max()
                
            case f1db_utils.PerformanceType.PODIUMS.value:
                df.sort_values(by=["count_podiums"], ascending=False, inplace=True)
                y = ["count_position_1", "count_position_2", "count_position_3"] # with proper colors (gold, silver, bronze)
                drivers.drivers_dict["count_position_1"] = "1°"
                max_val = df["count_podiums"].max()
        
        
        x = "driverName"
        # print(f"{min_value} {max_val}")
        if min_value <= max_val:
            fig = px.bar(df, 
                x = x, 
                y = y,
                labels = drivers.drivers_dict,
                hover_data = {
                    # y: drivers_dict[y]
                    x: False
                },
                template = drivers_template,
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map=f1db_utils.podium_colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},
            ).update_layout(
                transparent_bg,
                title = {
                    "text": title,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 18 }
                },
                hovermode="x",
                showlegend=True
            ).for_each_trace(
                lambda t: t.update(name = drivers.drivers_dict[t.name]) if t.name in drivers.drivers_dict else None
            )
        
            if performance_type == "podiums":
                return [fig.update_traces(
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                    ),
                    # customdata = ["1°", "2°", "3°"],
                    hovertemplate="<b>%{y}<br>" + # TODO => try to do like 1°:#1, 2°:#2, ...
                            "<extra></extra>"
                ), max_val, {1: "1", str(max_val): str(max_val)}]
            else:
                return [fig.update_traces(
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16,
                    ),
                    # customdata = ["1°", "2°", "3°"],
                    hovertemplate="<b>%{y}<br>" + # TODO => try to do like 1°:#1, 2°:#2, ...
                            "<extra></extra>",
                    showlegend=True,
                    name= "1°"
                ), max_val, {1: "1", str(max_val): str(max_val)}]
        else:
            return [warning_empty_dataframe, max_val, {1: "1", str(max_val): str(max_val)}]


    elif selected_driver is not None: # Performance Trend
        df = drivers.getTrendPerformance(selected_driver, performance_type)
        drivers.drivers_dict["progressiveCounter"] = f"{drivers.drivers_dict[performance_type]} Trend"
        
        hover_data = {
            drivers.performanceType2TimeAxis[performance_type]: False
        }
        if performance_type != f1db_utils.PerformanceType.WDCS.value:
            hover_data["officialName"] = True
        
        return [px.line(
            df,
            x = drivers.performanceType2TimeAxis[performance_type], 
            y = "progressiveCounter", 
            color = "driverName",
            markers = True,
            labels = drivers.drivers_dict,
            hover_data = hover_data,
            color_discrete_sequence=f1db_utils.custom_colors,
            template = drivers_template
        ).update_layout(
            transparent_bg,
            yaxis = dict(tickmode="linear", dtick=1) if df["progressiveCounter"].max() < 10 else {},
            title = getTitleObj(f"{drivers.drivers_dict[performance_type]} Trend"),
            hovermode = "x"
        ) if not df.empty else warning_empty_dataframe, max_val, {1: "1", str(max_val): str(max_val)}]

    else:
        return [warning_empty_dataframe, max_val, {1: "1", str(max_val): str(max_val)}]
    
# =================3================= 






      
if __name__ == '__main__':
    app.run(debug=True) # TODO => what does Debug=True do ??
