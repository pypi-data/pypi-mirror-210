import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

st.set_page_config(page_title="SPAI Demo", page_icon="🌍")


@st.cache_data(ttl=10)
def get_data():
    api_url = "http://localhost:8000/"
    analytics = requests.get(api_url).json()
    df = pd.DataFrame(analytics)
    return df


df = get_data()

# AWS Open Data Terrain Tiles
TERRAIN_IMAGE = (
    "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
)

# Define how to parse elevation tiles
ELEVATION_DECODER = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}

st.sidebar.markdown("### Dates")
selected_layers = [
    pdk.Layer(
        "TerrainLayer",
        texture=f"http://localhost:8001/NDVI_{date}.tif/{{z}}/{{x}}/{{y}}.png",
        elevation_decoder=ELEVATION_DECODER,
        elevation_data=TERRAIN_IMAGE,
    )
    for date in df.index
    if st.sidebar.checkbox(date, True)
]

if selected_layers:
    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": 41.4,
                "longitude": 2.17,
                "zoom": 9,
                "pitch": 60,
            },
            layers=selected_layers,
        )
    )
else:
    st.error("Please choose at least one layer above.")


st.title("Vegetation Analytics")

st.line_chart(df)
if st.checkbox("Show data"):
    st.write(df)
