# File      FRONTEND | DRIVERS
# Author    Matteo Naccarato

import pandas as pd
import plotly.express as px
from dash import dcc
import dash_bootstrap_components as dbc

import backend.f1db_utils as f1db_utils
import backend.drivers as drivers

NOT_QUALIFIED = "NQ"

# ======Handle hovertemplate accurately======
MAX_ELEMENTS_TO_DISPLAY = 5
def format_race_driver_info(race_driver_info):
    max_display = MAX_ELEMENTS_TO_DISPLAY
    if len(race_driver_info) > max_display:
        return '<br>'.join([f"{item['officialName']} <i>({item['driverName']})</i>" for item in race_driver_info[:max_display]]) + f'<br><i>and {len(race_driver_info) - max_display} more</i>'
    else:
        return '<br>'.join([f"{item['officialName']} <i>({item['driverName']})</i>" for item in race_driver_info])

def format_driver_info(driver_info):
    max_display = MAX_ELEMENTS_TO_DISPLAY
    if len(driver_info) > max_display:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info[:max_display]]) + f'<br><i>and {len(driver_info) - max_display} more</i><extra></extra>'
    else:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info]) + '<extra></extra>'
    
# ===========================================
    
    
# DRIVERS' world figure update (formatting)
driver_info = drivers.dfs["worldSpread"].groupby(['nationalityCountryId','year']).apply(
    lambda x: [{'driverName': row['driverName']} for idx, row in x.iterrows()]
).reset_index(name='driverInfo')
drivers.dfs["worldSpread"] = pd.merge(drivers.dfs["worldSpread"], driver_info, on=['nationalityCountryId','year'], how="left")
drivers.dfs["worldSpread"]['driverInfo'] = drivers.dfs["worldSpread"]['driverInfo'].apply(format_driver_info)
drivers.dfs["worldSpread"].sort_values(by="year", inplace=True)

# ====================DRIVERs STATIC FIGURES'=======================
drivers_figures = {
    # UP-LEFT GRAPH (Number of Drivers)
    "numDriversPerYear" : px.line(
        drivers.dfs["numDriversPerYear"],
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
        template = f1db_utils.template
    ).for_each_trace(lambda t: t.update(name = drivers.driver_type[t.name]))
    .update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Number of Official Drivers and Test Drivers Over the Years"),
        hovermode = "x",
        margin=f1db_utils.margin
    ).update_traces(
        hoverlabel = f1db_utils.getHoverlabel(13),
        hovertemplate="<b>%{y}</b><extra></extra>"
    ),
    # UP-RIGHT GRAPH (Distribution of Drivers' Nationalities)
    "worldSpread": px.scatter_geo(
        drivers.dfs["worldSpread"], 
        locations = "alpha3Code", 
        color = "continentName",
        hover_name = "countryName", 
        size = "count_display",
        animation_frame = "year",
        projection = "natural earth",
        labels = drivers.labels_dict,
        hover_data = {
            'countryName': True,
            'continentName': True,
            'count': True,
            'driverInfo': True,
            "alpha3Code": False,
            "year": False
        },
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
        template = f1db_utils.template
    ).update_layout(
        f1db_utils.transparent_bg,
        margin=f1db_utils.margin_geo,
        title = f1db_utils.getTitleObj("Distribution of Drivers' Nationalities Over the Years"),
    ).update_geos(f1db_utils.update_geos)
}

CUSTOM_HOVERTEMPLATE = '<b>%{customdata[0]}</b>, %{customdata[1]}<br><br><b>%{customdata[2]}</b><br>%{customdata[3]}<extra></extra>'
drivers_figures["worldSpread"].update_traces(
    hoverlabel=f1db_utils.getHoverlabel(13),
    hovertemplate=CUSTOM_HOVERTEMPLATE
)
for frame in drivers_figures["worldSpread"].frames:
    for data in frame.data:
        data.hovertemplate = CUSTOM_HOVERTEMPLATE
        
# ===========================================       
        
        
# ===================UI========================    

drivers_performance_type_graph_radio = dbc.RadioItems(
    id="drivers-performance-type-graph-id",
    options=[
        {"label": "Absolute", "value": "absolute"},
        {"label": "Drivers' Trend", "value": "trend"}
    ],
    value="absolute",
    inline=True
)

drivers_performance_type_radio = dbc.RadioItems(
    id="radio-drivers-performance-type-id",
    options=[
        {"label": "WDCs", "value": f1db_utils.PerformanceType.WDCS.value},
        {"label": "Wins", "value": f1db_utils.PerformanceType.WINS.value},
        {"label": "Podiums", "value": f1db_utils.PerformanceType.PODIUMS.value},
        {"label": "Poles", "value": f1db_utils.PerformanceType.POLES.value}
    ],
    value=f1db_utils.PerformanceType.WDCS.value,
    inline=True
)

drivers_performance_min_value = dcc.Slider(
    id='drivers-performance-min-value-id',
    min=1,
    step=1,
    value=0,
    tooltip={"placement": "bottom", "always_visible": True}
) 

drivers_performance_dropdown = dcc.Dropdown(
    id="drivers-performance-dropdown",
    options=[{"label":row["driverName"], "value": row["driverId"]} for row in drivers.getDrivers(drivers.PERFORMANCE_TYPE_DEFAULT).to_dict(orient="records")],
    placeholder="Select a Driver",
    searchable=True,
    clearable=False,
    multi=True,
    maxHeight=200,
    value=["lewis-hamilton","max-verstappen","sebastian-vettel"]  # "michael-schumacher"] 
)    

drivers_color_map = {
    "Lewis Hamilton": "#D626FF",
    "Sebastian Vettel": "#F6F926",
    "Max Verstappen": "#6A76FC",
    "Charles Leclerc": f1db_utils.F1_RED,
    "Michael Schumacher": "rgb(228,26,28)",
    "Alain Prost": "#EB000F",
    "Ayrton Senna": "#00FD35",
    "Lando Norris": "#FD8000"
}

# ===========================================