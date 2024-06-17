# File      DASHBOARD
# Authors   Matteo Naccarato 
#           Maurizio Meschi

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import numpy as np

import get_data

# LOOK IF NEW DATA IS AVAILABLE
get_data.get_data()

import frontend.drivers
import frontend.circuits
import backend.seasons as seasons
import backend.drivers as drivers
import backend.circuits as circuits
import backend.teams as teams
import backend.f1db_utils as f1db_utils

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# TABS STRUCTURE
tabs = ["seasons", "circuits", "drivers", "teams"]
STARTING_TAB = 0
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
        html.Span('F1', style={'color': 'red'}), 
        html.Span('-DATA', style={'color': 'white'}),
    ],className="text-center fw-bold m-0 pt-2"),
    #html.Hr(),
    html.Div([
        dcc.Tabs(id="tabs-graph", 
            value=tabs_children[STARTING_TAB].value, 
            children=tabs_children, 
            parent_className='custom-tabs', className='custom-tabs-container h-100',
            colors={
                "border": "transparent",
                "background": "rgb(33,37,41)"
            }),
        html.Div(id='tabs-content-graph')
    ], className="d-flex flex-column-reverse justify-content-between vh-98"),
], className="px-2 bg-dark vh-100")


## CALLBACKS
@callback(Output('tabs-content-graph', 'children'),
            Input('tabs-graph', 'value'))
def render_content(tab):
    match tab:
        
        # SEASONS
        case 'tab-0-seasons':
            return html.Div([
                html.Hr(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id="season_GP_graph", figure=seasons.createSeason_GP_Plot(), className="h-100"), width=6),
                    dbc.Col(dcc.Graph(id="season_Geo_graph", figure=seasons.createSeasonGeo(), className="h-100"), width=6)
                ], className="graph-section-seasons"),
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.Div(
                        seasons.crateDriverElement(),
                        id="range_div"
                    ),
                    dbc.Row(dbc.Col(dcc.Graph(id="season_graph", className="h-100")))
                ], className="graph-section-seasons")
            ], className="d-flex flex-column justify-content-between gap-2 container-fluid")
            
            
        # CIRCUITS
        case 'tab-1-circuits':
            return html.Div([
                html.Hr(className="mb-0"),
                dbc.Row([
                    dbc.Col(
                        dbc.Stack([
                            dcc.Graph(id="circuits-gp-held", className="h-100")
                    ], className="h-100"), width=6),
                    dbc.Col(dcc.Graph(id="circuits-quali-race-results", className="h-100"), width=6)
                ], className="graph-section-circuits"),
                html.Br(),
                dbc.Stack([
                    dbc.Row([
                        dbc.Col([
                            dbc.Col(html.Label("Min Value"), width=3),
                            dbc.Col(frontend.circuits.circuits_gp_held_min_value, width=9) 
                        ], className="d-flex justify-content-center", width=2),
                        dbc.Col(frontend.circuits.circuits_dropdown, width=4),
                        dbc.Col([
                            html.Label("Qualifying Position Range"),
                            frontend.circuits.quali_race_range
                        ], width=6),    
                    ], className="d-flex justify-content-center"),
                    dcc.Graph(id='circuits-qualifying', className="h-100")
                ], className="graph-section-circuits")
            ], className="container-fluid")
         
            
        # DRIVERS
        case 'tab-2-drivers':
            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='drivers-line', figure=frontend.drivers.drivers_figures['numDriversPerYear'], className="h-100"), width=6),
                    dbc.Col(dcc.Graph(id="drivers-world", figure=frontend.drivers.drivers_figures['worldSpread'], className="h-100"), width=6)
                ], className="graph-section-circuits"),
                html.Br(),
                dbc.Stack([
                    dbc.Row([
                        html.Div([
                            html.Div([
                                html.Label("Type of Graph"),
                                html.Label("Performance Type")
                            ], className="d-flex flex-column px-5"),
                            html.Div([
                                frontend.drivers.drivers_performance_type_graph_radio,
                                frontend.drivers.drivers_performance_type_radio
                            ], className="d-flex flex-column align-items-center"),
                            html.Div([
                                dbc.Col([
                                    html.Div([
                                        html.Label("==============", style={"color": "rgb(33,37,41)"}),
                                        html.Label("Min Value"),
                                        html.Label("==============", style={"color": "rgb(33,37,41)"})
                                    ]),
                                    frontend.drivers.drivers_performance_min_value 
                                ], id="drivers-min-value-id", width=12),
                                dbc.Col(frontend.drivers.drivers_performance_dropdown, width=12, style={"max-width":"100px;"})
                            ])
                        ], className="d-flex gap-4"),
                    ]),
                    dcc.Graph(id="drivers-performance", className="h-100"),
                    html.Br()
                ], className="graph-section-circuits")
            ], className="container-fluid")
            
         
        # TEAMS
        case 'tab-3-teams':
            return html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="entrants_teams_graph", figure=teams.creteNumTeamsEntrantsForYear(), className="h-100"), width=6),
                    dbc.Col(dcc.Graph(id="geo_teams_graph", figure=teams.createCostructorGeo(), className="h-100"), width=6)
                ], className="graph-section-circuits"),
                html.Br(),
                dbc.Stack([
                    dbc.Row([
                        html.Div([
                            html.Div([
                                html.Label("Type of Graph"),
                                html.Label("Performance Type")
                            ], className="d-flex flex-column px-5"),
                            html.Div([
                                teams.createRadioButtonGraph(),
                                teams.createRadioButton()
                            ], className="d-flex flex-column align-items-center"),
                            html.Div([
                                dbc.Col([
                                    html.Div([
                                        html.Label("==============", style={"color": "rgb(33,37,41)"}),
                                        html.Label("Min Value"),
                                        html.Label("==============", style={"color": "rgb(33,37,41)"})
                                    ]),
                                    teams.createSlider() 
                                ], id="teams-min-value-id", width=12),
                                dbc.Col(teams.createDropdown(), id='dropdown_col', width=12, style={"max-width":"50px;"})
                            ])
                        ], className="d-flex gap-4"),
                    ]),
                    dcc.Graph(id="teams_graph", figure=teams.createWinConstructorPlot(), className="h-100")
                ], className="graph-section-circuits")
            ], className="container-fluid")
        
        # DEFAULTS
        case _:
             return html.Div([])
        


# =================1================= SEASONS by Maurizio Meschi
@callback([Output('dropdown_drivers', 'options'),
           Output('dropdown_drivers', 'value')],
               Input('range-slider', 'value'))
def update_dropdown(slider_value):
        return [seasons.updateDropDownDrivers(slider_value), ['ayrton-senna', 'alain-prost']]

@callback(Output('season_graph', 'figure'),
              [Input('radio-input', 'value'),
               Input('range-slider', 'value'),
               Input('dropdown_drivers', 'value'),
               Input('dropdown_drivers', 'options')])
def update_graph(radio_value, range_value, driver, option):
    if(driver == []):
        driver = [option[0]['value'], option[3]['value']]
    return seasons.createSeasonDriverPlot(radio_value, range_value, driver) 
 
# =================1================= 



# =================2================= CIRCUITS by Matteo Naccarato
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


# UP-LEFT GRAPH (GP Held)
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
            "countryName": True,
            "type": True
        },
        template = f1db_utils.template,
        color_discrete_sequence =[f1db_utils.podium_colors["count_position_2"]]
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Number of GP Held by Circuit"),
        hovermode = "x",
        margin=f1db_utils.margin
    ).update_traces(
        hoverlabel=f1db_utils.getHoverlabel(),
        hovertemplate="<b>%{y}</b>, %{customdata[1]}<br>Type: %{customdata[2]}<extra></extra>"
    ) if not df.empty else f1db_utils.warning_empty_dataframe
    
    return fig


# UP-RIGHT GRAPH (Qualifying vs Race)
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
    if len(circuitsId) != 1: return f1db_utils.warning_empty_dataframe

    # Update data to properly set the upper bound of the Qualifying Position slider 
    global circuits_vars
    df = circuits.get_quali_race(circuitsId)
    circuits_vars["quali_race_range_min"] = df["positionQualifying"].min()
    circuits_vars["quali_race_range_max"] = df["positionQualifying"].max()
    
    # Filter by Qualifying Position Range
    df = df[df['positionQualifying'].isin(list(range(int(qualiRange[0]), int(qualiRange[1])+1)))] 
    df.sort_values(by="raceId", inplace=True, ascending=False)

    # Compute frequency values    
    total_qualifying = df['positionQualifying'].value_counts().reset_index()
    total_qualifying.columns = ['positionQualifying', 'total']
    freq_df = df.groupby(['positionQualifying', 'positionRace']).size().reset_index(name='count')
    freq_df = pd.merge(freq_df, total_qualifying, on='positionQualifying')
    freq_df['count_per_total'] = freq_df['count'] / freq_df['total'] * 100
    
    # Customize hoverlabel info with offical GP name and Driver info who achieved the pole
    race_driver_info = df.groupby(['positionQualifying', 'positionRace']).apply(
        lambda x: [{'officialName': row['officialName'], 'driverName': row['driverName']} for idx, row in x.iterrows()]
    ).reset_index(name='raceDriverInfo')
    freq_df = pd.merge(freq_df, race_driver_info, on=['positionQualifying', 'positionRace'])
    freq_df['raceDriverInfo'] = freq_df['raceDriverInfo'].apply(frontend.drivers.format_race_driver_info)
    
    freq_df.reset_index(inplace=True)
    freq_df.drop(columns=["index"], inplace=True)
    
    # X-axis values
    tickvals = np.linspace(circuits_vars["quali_race_range_min"], circuits_vars["quali_race_range_max"], circuits_vars["quali_race_range_max"])
    ticktext = [val if val < (circuits_vars["quali_race_range_max"]) else frontend.drivers.NOT_QUALIFIED for val in tickvals]
                 
    fig = px.scatter(freq_df, 
        x = 'positionQualifying', 
        y = 'positionRace', 
        size = 'count',
        labels = circuits.labels_dict,
        template = f1db_utils.template,
        color_discrete_sequence=f1db_utils.custom_colors
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Qualifying Position vs Race Position"),
        xaxis = {
            'tickvals': tickvals, 
            'ticktext': ticktext  
        },
        margin=f1db_utils.margin
    ).update_traces(
        hovertemplate='Q: <b>%{x}</b><br>' + 
        'R: <b>%{y}</b><br>' + 
        'Count: <b>%{marker.size}</b> / %{customdata[0]} (<b>%{customdata[1]:.0f}%</b>)<br>' +
        '%{customdata[2]}',
        hoverlabel = f1db_utils.getHoverlabel(14)
    )
    fig.data[0].customdata = freq_df[['total', 'count_per_total', 'raceDriverInfo']].values
    
    return fig 


# BOTTOM GRAPH (Pole Lap Time)
@app.callback(
    Output("circuits-qualifying", "figure"),
     Input("circuits-dropdown", "value")
)
def circuits_update_qualifying(circuitsIds):
    if not circuitsIds: 
        return f1db_utils.warning_empty_dataframe
    
    df = circuits.get_qualifying_times(circuitsIds)
    df = f1db_utils.order_df(df, "circuitId", circuitsIds)
    
    # Y-axis values
    tickvals = np.logspace(np.log10(df['timeMillis'].min()), np.log10(df['timeMillis'].max()), num=5, base=10)
    ticktext = [f1db_utils.ms_to_time(val) for val in tickvals]
    return px.line(
        df,
        x = "year",
        y = "timeMillis", # Pole Lap Time
        color = "circuitName",
        markers = True,
        labels = circuits.labels_dict,
        hover_data = {
            "year": False,
            "timeMillis": False,
            "circuitName": True,
            "time": True,
            "driverName": True,
            "qualifyingFormat": True
        },
        color_discrete_sequence=f1db_utils.custom_colors,
        template = f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Pole Lap Time Over the Years"),
        hovermode = "x",
        yaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            tickmode='array',
            title="Lap Time"
        ),
        margin=f1db_utils.margin
    ).update_traces(
            hoverlabel = f1db_utils.getHoverlabel(14),
            hovertemplate="<br>".join(["<b>%{customdata[0]}</b> (%{x})<br><b>%{customdata[1]}</b>, <i>%{customdata[2]}</i><br>%{customdata[3]}<extra></extra>"])
    ) if not df.empty else f1db_utils.warning_empty_dataframe

# =================2=================




# =================3================= DRIVERS by Matteo Naccarato
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


# BOTTOM GRAPH (Drivers' WDCs / Wins / Podiums / Poles)
@app.callback(
    [Output("drivers-performance", "figure"),
     Output("drivers-performance-min-value-id", "max"),
     Output("drivers-performance-min-value-id", "marks")],
    [Input("drivers-performance-type-graph-id", "value"),
     Input("radio-drivers-performance-type-id", "value"),
     Input("drivers-performance-min-value-id", "value"),
     Input("drivers-performance-dropdown", "value")]
)
def update_drivers_performance(graph_type, performance_type, min_value, selected_drivers):
    df = []
    hover_data = {}
    max_val = 0
    if (graph_type == "absolute"):
        if (performance_type == drivers.PERFORMANCE_TYPE_DEFAULT and min_value == drivers.MIN_VALUE_DEFAULT):
            df = drivers.dfs["absolutePerformance"] # standard values, use the one already computed
        else:
            df = drivers.getAbsolutePerformance(
                performance_type, 
                min_value, 
                "count_podiums" if performance_type == f1db_utils.PerformanceType.PODIUMS.value else "count_position_1"
            )
        
        title = f"Most F1 {drivers.labels_dict[performance_type]}"
        match performance_type:
            case f1db_utils.PerformanceType.WDCS.value | f1db_utils.PerformanceType.WINS.value | f1db_utils.PerformanceType.POLES.value:
                df.sort_values(by=["count_position_1"], ascending=False, inplace=True)         
                y = "count_position_1"
                drivers.labels_dict["count_position_1"] = f"Number of {drivers.labels_dict[performance_type]}"
                max_val = df[y].max()
                
            case f1db_utils.PerformanceType.PODIUMS.value:
                df.sort_values(by=["count_podiums"], ascending=False, inplace=True)
                y = ["count_position_1", "count_position_2", "count_position_3"] 
                drivers.labels_dict["count_position_1"] = "1°"
                max_val = df["count_podiums"].max()
                hover_data = { "count_podiums": True }
        
        x = "driverName"
        if min_value <= max_val:
            fig = px.bar(df, 
                x = x, 
                y = y,
                labels = drivers.labels_dict,
                hover_data = hover_data,
                template = f1db_utils.template,
                color_discrete_sequence =[f1db_utils.podium_colors["count_position_1"]]*len(df),
                color_discrete_map=f1db_utils.podium_colors,
                category_orders = {"y": ["count_position_1", "count_position_2", "count_position_3"]},
            ).update_layout(
                f1db_utils.transparent_bg,
                title = f1db_utils.getTitleObj(title),
                hovermode="x",
                showlegend=True,
                margin=dict(t=20, b=20)
            ).for_each_trace(
                lambda t: t.update(name = drivers.labels_dict[t.name]) if t.name in drivers.labels_dict else None
            )
        
            if performance_type == f1db_utils.PerformanceType.PODIUMS.value:
                fig.update_traces(
                    hoverlabel = f1db_utils.getHoverlabel(),
                    hovertemplate="<b>%{y} / %{customdata[0]}</b><extra></extra>"
                )
                fig.data[0].customdata = df[["count_podiums"]].values.tolist()
                
                return [fig, max_val, {1: "1", str(max_val): str(max_val)}]
                
            else: # wdcs, wins, poles
                return [fig.update_traces(
                    hoverlabel=f1db_utils.getHoverlabel(),
                    hovertemplate="<b>%{y}<br><extra></extra>",
                    showlegend=True,
                    name= "1°"
                ), max_val, {1: "1", str(max_val): str(max_val)}]
        else:
            return [f1db_utils.warning_empty_dataframe, max_val, {1: "1", str(max_val): str(max_val)}]


    elif selected_drivers is not None: # Performance Trend
        df = drivers.getTrendPerformance(selected_drivers, performance_type)
        drivers.labels_dict["progressiveCounter"] = f"Number of {drivers.labels_dict[performance_type]}"
        
        hover_data = {
            "driverName": True,
            drivers.performanceType2TimeAxis[performance_type]: False
        }
        if performance_type != f1db_utils.PerformanceType.WDCS.value:
            hover_data["officialName"] = True
        
        df = f1db_utils.order_df(df, "driverId", selected_drivers)
        
        show_gp_name = "%{customdata[1]}" if performance_type != f1db_utils.PerformanceType.WDCS.value else ""
        return [
            px.line(
                df,
                x = drivers.performanceType2TimeAxis[performance_type], 
                y = "progressiveCounter", 
                color = "driverName",
                markers = True,
                labels = drivers.labels_dict,
                hover_data = hover_data,
                color_discrete_sequence=f1db_utils.custom_colors,
                color_discrete_map = frontend.drivers.drivers_color_map,
                template = f1db_utils.template
            ).update_layout(
                f1db_utils.transparent_bg,
                yaxis = dict(tickmode="linear", dtick=1) if df["progressiveCounter"].max() < 10 else {},
                title = f1db_utils.getTitleObj(f"{drivers.labels_dict[performance_type]} Trend"),
                hovermode = "x",
                margin=f1db_utils.margin
            ).update_traces(
                hoverlabel = f1db_utils.getHoverlabel(13),
                hovertemplate="<br>".join(["<b>%{customdata[0]}</b> (<b>%{y}</b>)<br>" + show_gp_name + "<extra></extra>"])
            ) if not df.empty else f1db_utils.warning_empty_dataframe, 
            max_val, 
            { 1: "1", str(max_val): str(max_val) }
        ]

    else:
        return [f1db_utils.warning_empty_dataframe, max_val, {1: "1", str(max_val): str(max_val)}]
    
# =================3================= 


# =================4================= TEAMS by Maurizio Meschi 
@app.callback(
    [Output('dropdown', 'style'),
     Output('teams-min-value-id', 'style')],
    Input('radio-input-graph', 'value')
)
def toggle_teams_dropdown(selected_value):
    if selected_value == "absolute":
        return [{'display': 'none'},None]
    else:
        return [None,{'display': 'none'}]
    
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
        elif(radio_value == "win race"):
            return teams.createRaceWinPlot(slider_value)
        else:
            return teams.createTotalPodiumPlot(slider_value)
        

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
              Input('radio-input-teams', 'value'))
def update_option_dropdown(radio_value):
    return teams.createDropdown(radio_value)

# =================4================= 

      
if __name__ == '__main__':
    app.run(debug=True) 