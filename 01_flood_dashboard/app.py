"""
Flood Data Visualisation Dashboard (Humanised)
---------------------------------------------
Explore rainfall and river discharge over time and see example
flood‑prone locations on a map. This is a teaching app: small, clear,
and easy to extend with your real data.
"""

from datetime import date
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Optional import: only used for the map. If not installed, the app still runs
try:
    import geopandas as gpd
    HAS_GPD = True
except Exception:
    HAS_GPD = False

# ------------------------------
# 1) Load simple demo datasets
# ------------------------------
df = pd.read_csv("data/rainfall_discharge.csv", parse_dates=["date"])

risk_points = None
if HAS_GPD:
    try:
        risk_points = gpd.read_file("data/flood_prone.geojson").to_crs(4326)
    except Exception:
        risk_points = None

# ------------------------------
# 2) Build the Dash application
# ------------------------------
app = Dash(__name__, title="Flood Data Dashboard")

app.layout = html.Div(
    [
        html.H1("🌊 Flood Data Dashboard", style={"textAlign": "center"}),

        html.Div(
            [
                html.Div(
                    [
                        html.Label("Choose variable to plot"),
                        dcc.Dropdown(
                            id="variable",
                            options=[
                                {"label": "Rainfall (mm)", "value": "rainfall_mm"},
                                {"label": "Discharge (m³/s)", "value": "discharge_cms"},
                            ],
                            value="rainfall_mm",
                            clearable=False,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Pick date range"),
                        dcc.DatePickerRange(
                            id="daterange",
                            start_date=df["date"].min().date(),
                            end_date=df["date"].max().date(),
                        ),
                    ]
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "1rem",
                "margin": "1rem 0",
            },
        ),

        dcc.Graph(id="timeseries"),

        html.H2("Flood‑prone locations (demo)"),
        html.P(
            "These are example points with a 'risk_score'. Replace with your real GIS data.",
            style={"marginTop": "-0.6rem", "color": "#555"},
        ),
        dcc.Graph(id="map"),
    ],
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "1rem"},
)

# ------------------------------
# 3) Define interactive callbacks
# ------------------------------
@app.callback(
    Output("timeseries", "figure"),
    Input("variable", "value"),
    Input("daterange", "start_date"),
    Input("daterange", "end_date"),
)
def update_timeseries(selected_variable: str, start_date: str, end_date: str):
    """Filter the time series by date and plot the chosen variable."""
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    filtered = df.loc[mask]

    title = "Rainfall (mm)" if selected_variable == "rainfall_mm" else "Discharge (m³/s)"
    fig = px.line(filtered, x="date", y=selected_variable, markers=True, title=title)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=title)
    return fig

@app.callback(Output("map", "figure"), Input("variable", "value"))
def update_map(_):
    """Show a simple point map if geopandas is available, otherwise a blank figure."""
    if risk_points is None or risk_points.empty:
        return px.scatter_mapbox(
            lat=[0.34], lon=[32.58], zoom=5, title="Install geopandas to show demo points"
        ).update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=40, b=0))

    fig = px.scatter_mapbox(
        risk_points,
        lat=risk_points.geometry.y,
        lon=risk_points.geometry.x,
        size="risk_score",
        hover_data=["name", "risk_score"],
        zoom=5,
        height=520,
        title="Demo flood‑prone locations",
    )
    fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=40, b=0))
    return fig

if __name__ == "__main__":
    # Run the app. Press CTRL+C to stop.
    app.run_server(debug=True)
