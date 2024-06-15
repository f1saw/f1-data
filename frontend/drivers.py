import pandas as pd
import plotly.express as px

import backend.f1db_utils as f1db_utils
import backend.drivers as drivers

# TODO => put them in f1db_utils
# Needed to handle hovertemplate properly
def format_driver_info(driver_info):
    max_display = 5 # TODO => make it as a const
    if len(driver_info) > max_display:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info[:max_display]]) + f'<br>and {len(driver_info) - max_display} more<extra></extra>'
    else:
        return '<br>'.join([f"{item['driverName']}" for item in driver_info]) + '<extra></extra>'
    
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
        template = f1db_utils.template
    ).for_each_trace(lambda t: t.update(name = drivers.driver_type[t.name]))
    .update_layout(
        f1db_utils.transparent_bg,
        title = f1db_utils.getTitleObj("Number of Official Drivers and Test Drivers Over the Years"),
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
        height=500,
        title = f1db_utils.getTitleObj("Spread of Drivers' Nationalities Over the Years"),
    ).update_geos(f1db_utils.update_geos)
}
#drivers_figures["worldSpread"].data[0].customdata = drivers.drivers_dfs["worldSpread"][["countryName", "continentName", "count"]].values.tolist()

CUSTOM_HOVERTEMPLATE = '<b>%{customdata[0]}</b>, %{customdata[1]}<br><br><b>%{customdata[2]}</b><br>%{customdata[3]}<extra></extra>'
drivers_figures["worldSpread"].update_traces(hovertemplate=CUSTOM_HOVERTEMPLATE)
for frame in drivers_figures["worldSpread"].frames:
    for data in frame.data:
        data.hovertemplate = CUSTOM_HOVERTEMPLATE