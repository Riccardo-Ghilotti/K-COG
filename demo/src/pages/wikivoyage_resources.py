import streamlit as st
from streamlit_theme import st_theme
import pydeck
import pandas as pd
import json
import streamlit.components.v1 as components
st.title("Wikivoyage Corpus Map")
st.write("""This page displays a map showing cities that are either capitals or have at least 500,000 inhabitants. These locations were selected to build the reference corpus and ontology.

By clicking on a city on the map, you are redirected to its corresponding Wikivoyage page, which represents the source corpus used as the starting point of the project.
         """)

with open("./demo/resources/wikivoyage_cities.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

cities = pd.DataFrame(cities).T.reset_index(names="city")

cities["lat"] = cities["lat"].astype(float)
cities["lon"] = cities["lon"].astype(float)

point_layer = pydeck.Layer(
    "ScatterplotLayer",
    data=cities,
    id="cities",
    get_position=["lon", "lat"],
    get_color="[255, 75, 75]",
    pickable=True,
    auto_highlight=True,
    get_radius=9000,
)

view_state = pydeck.ViewState(
    latitude=52, longitude=10, controller=True, zoom=3, pitch=30
)

theme = st_theme()
map_style = "light"
if theme and theme["base"] == "dark":
    map_style = "dark"

chart = pydeck.Deck(
    point_layer,
    initial_view_state=view_state,
    tooltip={"text": "{city}\n{link}"},  
    map_style=map_style
)

event = st.pydeck_chart(chart, on_select="rerun", selection_mode="multi-object")

selected = event.selection.get("objects", {}).get("cities", [])

if selected:
    for obj in selected:
        url = obj.get("link")
        if url:
            components.html(
                f"<script>window.parent.open('{url}', '_blank');</script>",
                height=0,
            )