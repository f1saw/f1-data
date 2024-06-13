import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import season
import backend.drivers as drivers



# chiamata a get-data.py (solo se passata più di una 5 giorni dall'ultima lettura OPPURE fare ogni lunedì se non già fatto lo stesso giorno)
# leggere da ./f1db-csv/

# SEASON DATA
"""
df_season_list = season.getSeasonData()

df_season_list["df_season_costurct"] = df_season_list[0]
df_season_list["df_season_driver"] = df_season_list[1]
df_season_list["df_season_entrants_constructors"] = df_season_list[2]
df_season_list["df_season_entrants_drivers"] = df_season_list[3]
df_season_list["df_season_entrants_tyre"] = df_season_list[4]
df_season_list["sdf_season_entrants"] = df_season_list[5]
"""

#### DATI OTTENUTI


#### CREAZIONE DASHBOARD

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


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



# STATIC FIGURES
drivers_figures = {
    "numDriversPerYear" : px.line(
        drivers.drivers_dfs["numDriversPerYear"],
        x = "year",
        y = ["officialDriver","testDriver"],
        markers = True,
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
            "count_display": "Number of Drivers"
        },
        hover_data = {
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
            "text": "Spread of Drivers Nationalities Over the Years",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18 }
        },
    ).update_geos(
        bgcolor="rgba(0,0,0,0)",
        showland=True, landcolor="rgb(200,212,227)",
        resolution=110
    ),

    
}
# my_fig.add_scatter(x=drivers_dfs["numDriversPerYear"]["year"], y=drivers_dfs["numDriversPerYear"]["testDriver"])



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
    html.H1('F1-DATA', className="text-center fw-bold m-3"),
    html.Div([
        dcc.Tabs(id="tabs-graph", 
            value=tabs_children[0].value, 
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
                        dcc.Graph(id="season_graph", figure=season.createSeason_GP_Plot())
                    ),
                    dbc.Col(
                        dcc.Graph(id="season_graph", figure=season.createSeasonGeo())
                    )
                ]),
                html.Div(
                    season.crateDriverElement([1950, 1955]),
                    id="range_div"
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(id="season_graph", figure=season.createSeasonDriverPlot())
                    )
                )
            ], className="d-flex flex-column justify-content-between gap-2")
            
        # CIRCUITS
        case 'tab-1-circuits':
            return html.Div([
                html.H3('Tab content 2'),
                dcc.Graph(
                    id='graph-2-tabs-dcc',
                    figure={
                        'data': [{
                            'x': [1, 2, 3],
                            'y': [5, 10, 6],
                            'type': 'bar'
                        }]
                    }
                )
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
                            ]),
                            dbc.Col(drivers.drivers_performance_dropdown, width=9)
                        ], width=4)
                    ]),
                    dcc.Graph(id="drivers-performance")
                ])
            ])
        
        # DEFAULTS
        case _:
             return html.Div([])
        
#Callback season
         
@callback(Output('dropdown_drivers', 'options'),
               Input('range-slider', 'value'))
def update_dropdown(slider_value):
        print(slider_value)
        return season.updateDropDownDrivers(slider_value)

@callback(Output('season_graph', 'figure'),
              [Input('radio-input', 'value'),
               Input('range-slider', 'value'),
               Input('dropdown_drivers', 'value')])
def update_graph(radio_value, range_value, driver):
    if (driver!=[]):
        return season.createSeasonDriverPlot(radio_value, range_value, driver) 
    return season.createSeasonDriverPlot(radio_value, range_value)   
 

####   


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
                "count_podiums" if performance_type == "podiums" else "count_position_1"
            )
            
        title = f"Most F1 {drivers.drivers_dict[performance_type]}"
        match performance_type:
            case "wdcs" | "wins" | "poles":
                # Keep only 1st place results, already done with poles
                if performance_type != "poles":
                    df = df[df["count_position_1"] != 0] 
                df.sort_values(by=["count_position_1"], ascending=False, inplace=True)         
                y = "count_position_1"
                drivers.drivers_dict["count_position_1"] = f"Number of {drivers.drivers_dict[performance_type]}"
                max_val = df[y].max()
                
            case "podiums":
                df.sort_values(by=["count_podiums"], ascending=False, inplace=True)
                y = ["count_position_1", "count_position_2", "count_position_3"] # with proper colors (gold, silver, bronze)
                drivers.drivers_dict["count_position_1"] = "1°"
                max_val = df["count_podiums"].max()
        
        
        x = "driverName"
        colors = {
            "count_position_1": "gold",
            "count_position_2": "silver",
            "count_position_3": "peru"
        }
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
                color_discrete_sequence =[colors["count_position_1"]]*len(df),
                color_discrete_map=colors,
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
                ), max_val, {0: "0", str(max_val): str(max_val)}]
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
                ), max_val, {0: "0", str(max_val): str(max_val)}]
        else:
            return [warning_empty_dataframe, max_val, {0: "0", str(max_val): str(max_val)}]


    elif selected_driver is not None: # Performance Trend
        df = drivers.getTrendPerformance(selected_driver, performance_type)
        drivers.drivers_dict["progressiveCounter"] = f"{drivers.drivers_dict[performance_type]} Trend"
        
        hover_data = {
            drivers.performanceType2TimeAxis[performance_type]: False
        }
        if performance_type != "wdcs":
            hover_data["officialName"] = True
        
        return [px.line(
            df,
            x = drivers.performanceType2TimeAxis[performance_type], 
            y = "progressiveCounter", 
            color = "driverName",
            markers = True,
            labels = drivers.drivers_dict,
            hover_data = hover_data,
            template = drivers_template
        ).update_layout(
            transparent_bg,
            yaxis = dict(tickmode="linear", dtick=1) if df["progressiveCounter"].max() < 10 else {},
            title = getTitleObj(f"{drivers.drivers_dict[performance_type]} Trend"),
            hovermode = "x"
        ) if not df.empty else warning_empty_dataframe, max_val, {0: "0", str(max_val): str(max_val)}]

    else:
        return [warning_empty_dataframe, max_val, {0: "0", str(max_val): str(max_val)}]
    
      
if __name__ == '__main__':
    app.run(debug=True) # TODO => what does Debug=True do ??
