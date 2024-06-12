import sys
import os
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from drivers import *


# chiamata a get-data.py (solo se passata più di una 5 giorni dall'ultima lettura OPPURE fare ogni lunedì se non già fatto lo stesso giorno)
# leggere da ./f1db-csv/

#### DATI OTTENUTI


#### CREAZIONE DASHBOARD

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


radio_drivers_performance = dbc.RadioItems(
    id="radio-drivers-performance-id",
    options=[
        {"label": "Absolute", "value": "absolute"},
        {"label": "Driver's Trend", "value": "trend"}
    ],
    value="absolute",
    inline=True
)

drivers_performance_type_radio = dbc.RadioItems(
    id="radio-drivers-performance-type-id",
    options=[
        {"label": "WDCs", "value": "wdcs"},
        {"label": "Wins", "value": "wins"},
        {"label": "Podiums", "value": "podiums"},
        {"label": "Poles", "value": "poles"}
    ],
    value="wdcs",
    inline=True
)

drivers_performance_min_value = dcc.Slider(
    id='drivers-performance-min-value-id',
    min=0,
    max=100,  # Un valore molto grande per simulare l'infinito
    step=1,
    value=0,
    marks={0: '0', 100: '∞'},
    tooltip={"placement": "bottom", "always_visible": True}
) 

drivers_performance_dropdown = dcc.Dropdown(
    id="drivers-performance-dropdown",
    options=[{"label":row["driverName"], "value": row["driverId"]} for row in Drivers.getDrivers().to_dict(orient="records")],
    placeholder="Select a Driver",
    searchable=True,
    clearable=False,
    multi=True,
    maxHeight=200
)


# TODO => do useful structure like tabs = ["seasons": [array_of_graphs], "circuits": [array_of_graphs], ...]
# TODO => fare labels con dizionario e for figo
# ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
drivers_template = "plotly_dark"
transparent_bg = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)"
}
drivers_dfs = {
    "numDriversPerYear": Drivers.getNumDriversPerYear(),
    "worldSpread": Drivers.getWorldSpread(),
    "absolutePerformance": Drivers.getAbsolutePerformance(Drivers.PERFORMANCE_TYPE_DEFAULT, Drivers.MIN_VALUE_DEFAULT, Drivers.COL_TO_APPLY_MIN_DEFAULT)
}

driver_type = {
    "officialDriver": "Official Driver",
    "testDriver": "Test Driver"
}


# STATIC FIGURES
drivers_figures = {
    "numDriversPerYear" : px.line(
        drivers_dfs["numDriversPerYear"],
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
    ).for_each_trace(lambda t: t.update(name = driver_type[t.name]))
    .update_layout(
        transparent_bg,
        title = {
            "text": "Number of Official Drivers and Test Drivers Over the Years",
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18 }
        },
        hovermode = "x"
    ),
    "worldSpread": px.scatter_geo(
        drivers_dfs["worldSpread"], 
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
], className="p-2 bg-dark vh-100 overflow-hidden")


## CALLBACKS
@callback(Output('tabs-content-graph', 'children'),
            Input('tabs-graph', 'value'))
def render_content(tab):
    match tab:
        # SEASONS
        case 'tab-0-seasons':
            return html.Div([
                html.H3('Tab content 1'),
                dcc.Graph(
                    figure={
                        'data': [{
                            'x': [1, 2, 3],
                            'y': [3, 1, 2],
                            'type': 'bar'
                        }]
                    }
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
                    dbc.Col(
                        dcc.Graph(id='drivers-line', figure=drivers_figures['numDriversPerYear']),
                        width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id="drivers-world", figure=drivers_figures['worldSpread']),
                        width=6
                    )
                ]),
                dbc.Stack([
                    dbc.Row([
                        dbc.Col([
                            dbc.Stack([
                                html.Label("Type of Graph:"),
                                radio_drivers_performance
                            ], direction="horizontal", gap=3),
                            dbc.Stack([
                                html.Label("Performance Type"),
                                drivers_performance_type_radio
                            ], direction="horizontal", gap=3),
                        ], width=4),
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(
                                    html.Label("Min Value"),
                                    width=2
                                ),
                                dbc.Col(
                                    drivers_performance_min_value,
                                    width=7
                                ) 
                            ]),
                            dbc.Col(
                                drivers_performance_dropdown,
                                width=9
                            )
                        ], width=4)
                    ]),
                    dcc.Graph(id="drivers-performance")
                ])
                
                
            ])
        
        # DEFAULTS
        case _:
             return html.Div([])
         

drivers_dict = {
    "driverId": "Driver",
    "driverName": "Driver",
    "count_position_1": "Wins",
    "count_position_2": "2°",
    "count_position_3": "3°",
    "count_podiums": "Podiums",
    "variable": "Position",
    "value": "Number of Podiums",
    "wdcs": "WDCs",
    "wins": "Wins",
    "poles": "Poles",
    "podiums": "Podiums"
}

@app.callback(
    Output("drivers-performance", "figure"),
    [Input("radio-drivers-performance-id", "value"),
     Input("radio-drivers-performance-type-id", "value"),
     Input("drivers-performance-min-value-id", "value"),
     Input("drivers-performance-dropdown", "value")]
)
def update_drivers_performance(graph_type, performance_type, min_value, selected_driver):
    print(f"{graph_type} {performance_type}")
    df = []
    
    if (graph_type == "absolute"):
        if (performance_type == Drivers.PERFORMANCE_TYPE_DEFAULT and min_value == Drivers.MIN_VALUE_DEFAULT):
            df = drivers_dfs["absolutePerformance"] # standard values, use the one already computed
        else:
            df = Drivers.getAbsolutePerformance(
                performance_type, 
                min_value, 
                "count_podiums" if performance_type == "podiums" else "count_position_1"
            )
            
        title = f"Most F1 {drivers_dict[performance_type]}"
        match performance_type:
            case "wdcs" | "wins" | "poles":
                # Keep only 1st place results, already done with poles
                if performance_type != "poles":
                    df = df[df["count_position_1"] != 0] 
                df.sort_values(by=["count_position_1"], ascending=False, inplace=True)         
                y = "count_position_1"
                drivers_dict["count_position_1"] = f"Number of {drivers_dict[performance_type]}"
                
            case "podiums":
                df.sort_values(by=["count_podiums"], ascending=False, inplace=True)
                y = ["count_position_1", "count_position_2", "count_position_3"] # with proper colors (gold, silver, bronze)
                drivers_dict["count_position_1"] = "1°"
        
        
        x = "driverName"
        colors = {
            "count_position_1": "gold",
            "count_position_2": "silver",
            "count_position_3": "peru"
        }
        fig = px.bar(df, 
            x = x, 
            y = y,
            labels = drivers_dict,
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
            lambda t: t.update(name = drivers_dict[t.name]) if t.name in drivers_dict else None
        )
        
        if performance_type == "podiums":
            return fig.update_traces(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                ),
                # customdata = ["1°", "2°", "3°"],
                hovertemplate="<b>%{y}<br>" + # TODO => try to do like 1°:#1, 2°:#2, ...
                        "<extra></extra>"
            )
        else:
            return fig.update_traces(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                ),
                # customdata = ["1°", "2°", "3°"],
                hovertemplate="<b>%{y}<br>" + # TODO => try to do like 1°:#1, 2°:#2, ...
                        "<extra></extra>",
                showlegend=True,
                name= "1°"
            )

    elif selected_driver is not None:
        # TODO
        df = Drivers.getTrendPerformance(selected_driver, performance_type)
        

    
         
if __name__ == '__main__':
    app.run(debug=True) # TODO => what does Debug=True do ??
