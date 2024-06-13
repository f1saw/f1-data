import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import season


# chiamata a get-data.py (solo se passata più di una 5 giorni dall'ultima lettura)
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

app = Dash(__name__,suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


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
                #html.H3('Tab content 1'),
                season.createDropDown(),
                html.Hr(),
                html.Div(
                    #season.crateDriverElement([1950, 1955]),
                    id="range_div"
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(id="season_graph", figure=season.createSeasonGeo())
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
        
        # DEFAULTS
        case _:
             return html.Div([])
        
#Callback season
        
@callback(Output('range_div', 'children'),
              Input('dropdown', 'value'))
def update_graph(dropdown):
    if (dropdown == "Season Driver"):
        return season.crateDriverElement([1990, 1995])
    return
         
@callback(Output('dropdown_drivers', 'options'),
               Input('range-slider', 'value'))
def update_dropdown(slider_value):
        return season.updateDropDownDrivers(slider_value)


@callback(Output('season_graph', 'figure'),
              [Input('radio-input', 'value'),
               Input('dropdown', 'value'),
               Input('range-slider', 'value'),
               Input('dropdown_drivers', 'value')])
def update_graph(radio_value, dropdown_value, range_value, driver):
    if (dropdown_value == "Season Gran Prix"):
        return season.createSeason_GP_Plot()
    elif (dropdown_value == "Season Driver"):
        return season.createSeasonDriverPlot(radio_value, range_value, driver)  
    else:
        return season.createSeasonGeo() 

####   

        
if __name__ == '__main__':
    app.run(debug=True) # TODO => what does Debug=True do ??
