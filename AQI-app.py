from dash import Dash, dcc, html, Output, Input
import pandas as pd
import plotly.express as px

# Load the county boundary coordinates
import json

with open("counties.json") as f:
    counties = json.load(f)

df = pd.read_csv("aqi_data.csv", dtype={"FIPS": str})

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="choropleth-map"),
        dcc.Slider(
            id="year-slider",
            min=df["Year"].min(),
            max=df["Year"].max(),
            value=df["Year"].min(),
            marks={str(year): str(year) for year in df["Year"].unique()},
            step=None,
        )
    ]
)


@app.callback(Output("choropleth-map", "figure"), [Input("year-slider", "value")])
def update_map(selected_year):
    filtered_df = df[df["Year"] == selected_year]

    fig = px.choropleth(
        filtered_df,
        geojson=counties,
        locations="FIPS",
        color="Median.AQI",
        color_continuous_scale="Magma",
        range_color=(0, 170),
        scope="usa",
        labels={"Median.AQI": "AQI Level"},
    )

    fig.update_layout(transition_duration=500)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run(debug=False)
