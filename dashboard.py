import sys
import os
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from drivers import *


# chiamata a get-data.py (solo se passata più di una 5 giorni dall'ultima lettura)
# leggere da ./f1db-csv/

#### DATI OTTENUTI


#### CREAZIONE DASHBOARD

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



# TODO => do useful structure like tabs = ["seasons": [array_of_graphs], "circuits": [array_of_graphs], ...]
# TODO => fare labels con dizionario e for figo
# ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
drivers_template = "plotly_dark"
transparent_bg = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)"
}
drivers_dfs = {
    "numDriversPerYear": getNumDriversPerYear(),
    "worldSpread": getWorldSpread()
}

driver_type = {
    "officialDriver": "Official Driver",
    "testDriver": "Test Driver"
}
"""continent_names = {
    "europe": "Europe",
    "north-america": "North America",
    "australia": "Australia",
    "africa": "Africa",
    "antarctica": "Antarctica"
}"""
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
    )
    
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
], className="p-2 bg-dark vh-100")

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
                html.H3('Tab content 2'),
                dcc.Graph(id='line', figure=drivers_figures['numDriversPerYear']),
                
                dcc.Graph(id="world", figure=drivers_figures['worldSpread'])
                
            ])
        
        # DEFAULTS
        case _:
             return html.Div([])
         
xaxis_feature_dropdown = dcc.Dropdown(
    id='xaxis-feature',
    # options=[{'label': "dizionario_nomi[col]", 'value': col} for col in df_penguins.columns],
    options="culmen_length_mm",
    value='culmen_length_mm'  # Valore predefinito
)

"""
@app.callback(Output('line','figure'), Input('xaxis_feature_dropdown', 'value'))
def update_line(x):
    fig = px.line(
        drivers_dfs["numDriversPerYear"],
        x = "year",
        y = "officialDriver"
    )
    return fig """
    
         
if __name__ == '__main__':
    app.run(debug=True) # TODO => what does Debug=True do ??
