from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px

# Load the county boundary coordinates
import json

with open("counties.json") as f:
    counties = json.load(f)

df = pd.read_csv("aqi_data.csv", dtype={"FIPS": str})

fig = px.choropleth(
    df,
    geojson=counties,
    locations="FIPS",
    color="Median.AQI",
    color_continuous_scale="Magma",
    range_color=(0, 170),
    scope="usa",
    labels={"Median.AQI": "AQI Level"},
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor="LightSteelBlue",
)

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Slider(
            id="year-slider",
            min=1980,
            max=2023,
            value=2023,
            marks={str(year): str(year) for year in df["Year"]},
            step=None,
        ),
        dcc.Graph(figure=fig),
    ]
)

if __name__ == "__main__":
    app.run(debug=False)
