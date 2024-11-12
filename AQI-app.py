from dash import Dash, dcc, html, Output, Input, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import dash_bootstrap_components as dbc
import numpy as np

# Load the county boundary coordinates
with open("counties.json") as f:
    counties = json.load(f)

# Load and preprocess the data
df = pd.read_csv("aqi_data.csv", dtype={"FIPS": str})

# Ensure 'Year' is integer
df["Year"] = df["Year"].astype(int)

# Precompute max count for histogram y-axis (fixed across years)
max_count = 0
bin_edges = np.linspace(0, 200, 41)  # 40 bins from 0 to 200
for year in df["Year"].unique():
    year_df = df[df["Year"] == year]
    counts, _ = np.histogram(year_df["Median.AQI"], bins=bin_edges)
    max_count = max(max_count, counts.max())

# Define a custom continuous color scale
custom_color_scale = [
    [0.0, "green"],  # AQI 0
    [0.25, "yellow"],  # AQI 50
    [0.50, "orange"],  # AQI 100
    [1.0, "maroon"],  # AQI 200
]


# Define a function to create the map figure with continuous color scale
def create_map_figure(selected_year):
    filtered_df = df[df["Year"] == selected_year]

    fig = px.choropleth(
        filtered_df,
        geojson=counties,
        locations="FIPS",
        color="Median.AQI",
        hover_data=["County", "Median.AQI"],
        color_continuous_scale=custom_color_scale,
        range_color=(0, 200),
        scope="usa",
        labels={"Median.AQI": "Median AQI"},
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        font=dict(family="Roboto, Arial", size=14),
        paper_bgcolor="#f8f9fa",  # Light grey background
        plot_bgcolor="#f8f9fa",  # Light grey background
        geo=dict(
            showlakes=True,
            lakecolor="LightBlue",
            showcountries=True,
            countrycolor="Black",
            coastlinecolor="Black",
            projection_scale=1,
            center=dict(lat=37.0902, lon=-95.7129),
        ),
        coloraxis_colorbar=dict(
            title="Median AQI",
            thicknessmode="pixels",
            thickness=15,
            lenmode="pixels",
            len=300,
            yanchor="middle",
            y=0.5,
            ticks="outside",
        ),
    )

    # Limit the view to the contiguous US
    fig.update_geos(
        lataxis_range=[23, 50],
        lonaxis_range=[-130, -65],
    )

    # Remove box/lasso select tools from the map
    fig.update_layout(dragmode=False)

    return fig


# Initial figure
initial_year = df["Year"].min()
map_fig = create_map_figure(initial_year)

# Configure the modebar buttons
map_config = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoomInGeo",
        "zoomOutGeo",
        "hoverClosestGeo",
        "select2d",
        "lasso2d",
    ],
    "scrollZoom": False,  # Disable scroll zooming
    "doubleClick": "reset",  # Reset on double click
}

line_hist_config = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d",
        "pan2d",
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "autoScale2d",
    ],
}

# Define the Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.NavbarBrand(
                                "Air Quality Index (AQI) in US Counties",
                                className="ml-2",
                            )
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="#",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink(
                                "Visit strickvax.com",
                                href="https://strickvax.com",
                                target="_blank",
                            )
                        ),
                    ],
                    className="ml-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4",
)

# Define the app layout
app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

app.layout = dbc.Container(
    [
        # Navbar at the top
        navbar,
        # Main Content: Map and Charts
        dbc.Row(
            [
                # Choropleth Map
                dbc.Col(
                    [
                        dcc.Graph(
                            id="choropleth-map",
                            figure=map_fig,
                            config=map_config,
                            style={"height": "80vh"},
                            className="dash-graph",
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=8,
                    xl=8,
                ),
                # Line Chart and Histogram
                dbc.Col(
                    [
                        dcc.Graph(
                            id="line-chart",
                            config=line_hist_config,
                            style={"height": "40vh"},
                            className="dash-graph",
                        ),
                        dcc.Graph(
                            id="histogram",
                            config=line_hist_config,
                            style={"height": "40vh"},
                            className="dash-graph",
                        ),
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=4,
                    xl=4,
                ),
            ]
        ),
        # Year Slider
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Slider(
                            id="year-slider",
                            min=df["Year"].min(),
                            max=df["Year"].max(),
                            value=initial_year,
                            marks={
                                str(year): str(year) for year in df["Year"].unique()
                            },  # String keys
                            step=None,  # Ensure it only steps through the years in the dataset
                            tooltip={"placement": "bottom", "always_visible": True},
                        )
                    ],
                    width=12,
                )
            ],
            className="my-4",
        ),
    ],
    fluid=True,
    style={"backgroundColor": "#f8f9fa"},
)  # Set background color


# Callback to update the map and histogram based on the selected year
@app.callback(
    [Output("choropleth-map", "figure"), Output("histogram", "figure")],
    [Input("year-slider", "value")],
)
def update_map(selected_year):
    map_fig = create_map_figure(selected_year)

    # Create histogram of AQI levels for all years, highlighting the selected year
    hist_fig = go.Figure()

    years = sorted(df["Year"].unique())
    for year in years:
        opacity = 0.1 if year != selected_year else 0.8
        filtered_df = df[df["Year"] == year]
        hist_fig.add_trace(
            go.Histogram(
                x=filtered_df["Median.AQI"],
                xbins=dict(start=0, end=200, size=5),
                name=str(year),
                opacity=opacity,
                marker=dict(color="blue" if year == selected_year else "grey"),
                showlegend=False,
            )
        )

    hist_fig.update_layout(
        barmode="overlay",
        title="AQI Distribution Across Years",
        title_x=0.5,
        margin={"r": 20, "t": 50, "l": 20, "b": 50},
        font=dict(family="Roboto, Arial", size=12),
        xaxis_title="Median AQI",
        yaxis_title="Count",
    )
    hist_fig.update_xaxes(range=[0, 200])
    hist_fig.update_yaxes(automargin=True)

    return map_fig, hist_fig


# Callback to update the line chart when a county is clicked
@app.callback(Output("line-chart", "figure"), [Input("choropleth-map", "clickData")])
def update_line_chart(clickData):
    if clickData is None:
        # Display a placeholder figure
        fig = go.Figure()
        fig.update_layout(
            title="Click on a county to see AQI over time",
            title_x=0.5,
            font=dict(family="Roboto, Arial", size=12),
            margin={"r": 20, "t": 50, "l": 20, "b": 50},
            xaxis_title="Year",
            yaxis_title="Median AQI",
            plot_bgcolor="#f8f9fa",
        )
        return fig
    else:
        fips = clickData["points"][0]["location"]
        county_df = df[df["FIPS"] == fips]

        if county_df.empty:
            return no_update

        county_name = (
            county_df["County"].iloc[0] if "County" in county_df.columns else fips
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=county_df["Year"],
                y=county_df["Median.AQI"],
                mode="lines+markers",
                marker=dict(
                    color=county_df["Median.AQI"],
                    colorscale=custom_color_scale,
                    cmin=0,
                    cmax=200,
                    showscale=False,  # Removed the colorbar
                ),
                line=dict(color="black"),
            )
        )

        fig.update_layout(
            title=f"AQI Over Time for {county_name}",
            title_x=0.5,
            font=dict(family="Roboto, Arial", size=12),
            margin={"r": 20, "t": 50, "l": 20, "b": 50},
            xaxis=dict(dtick=1, title="Year"),
            yaxis=dict(title="Median AQI", automargin=True),
        )

        return fig


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=False)
