# File      FRONTEND | CIRCUITS
# Author    Matteo Naccarato

from dash import dcc

import backend.f1db_utils as f1db_utils
import backend.circuits as circuits


# ===================UI========================   

circuits_gp_held_min_value = dcc.Slider(
    id='circuits-gp-held-min-value-id',
    min=1,
    step=1,
    value=0,
    tooltip={"placement": "bottom", "always_visible": True}
) 

quali_race_range = dcc.RangeSlider(
    id='circuits-quali-race-range-id',
    min=0, 
    max=20, 
    step=1, 
    value=[-f1db_utils.INFINITE_RESULT, f1db_utils.INFINITE_RESULT],
    tooltip={"placement": "bottom", "always_visible": True}
) 

circuits_dropdown = dcc.Dropdown(
    id="circuits-dropdown",
    options=[{"label": f'{row["circuitName"]}, {row["countryName"]}', "value": row["circuitId"]} for row in circuits.getCircuits().to_dict(orient="records")],
    placeholder="Select a Circuit",
    searchable=True,
    clearable=False,
    multi=True,
    maxHeight=200,
    value=["monza"]#,"monaco", "austria"]
    # value=["interlagos"]
)

# ===========================================