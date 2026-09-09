from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.utils import *

# Load the dashboard data from the local CSV file.
data = read_csv_data(str(Path(__file__).with_name("test_data.csv")))

# Streamlit app
st.set_page_config(layout="wide")

st.header("Sports federations safeguarding")

all_federations = sorted(data["Federation"].dropna().unique().tolist())
all_sports = sorted(data["Sport"].dropna().unique().tolist())

selected_sports = [
    value for value in st.session_state.get("selected_sports", []) if value in all_sports
]
federation_source = data[data["Sport"].isin(selected_sports)] if selected_sports else data
federation_options = sorted(federation_source["Federation"].dropna().unique().tolist())
selected_federations = [
    value for value in st.session_state.get("selected_federations", [])
    if value in federation_options
]
st.session_state["selected_federations"] = selected_federations

sport_source = data[data["Federation"].isin(selected_federations)] if selected_federations else data
sport_options = sorted(sport_source["Sport"].dropna().unique().tolist())
selected_sports = [value for value in selected_sports if value in sport_options]
st.session_state["selected_sports"] = selected_sports
filter_columns = st.columns(2)
selected_sports = filter_columns[0].multiselect(
    "Sport", options=sport_options, key="selected_sports"
)
selected_federations = filter_columns[1].multiselect(
    "Federation", options=federation_options, key="selected_federations"
)

filtered_data = data
if selected_federations:
    filtered_data = filtered_data[filtered_data["Federation"].isin(selected_federations)]
if selected_sports:
    filtered_data = filtered_data[filtered_data["Sport"].isin(selected_sports)]

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        justify-content: center;
        font-size: 1.1rem;
    }
    [data-testid="stMetricValue"] {
        justify-content: center;
        font-size: 2.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

kpi_columns = st.columns(3)
kpi_columns[0].metric("Records", len(filtered_data))
kpi_columns[1].metric("Federations", filtered_data["Federation"].nunique())
kpi_columns[2].metric("Countries", filtered_data["Country"].nunique())


chart_columns = ["CodeofEthics", "CodeofConduct", "SpecialEntityDedicated"]
chart_titles = {
    "CodeofEthics": "Code of Ethics",
    "CodeofConduct": "Code of Conduct",
    "SpecialEntityDedicated": "Special Entity Dedicated",
}
chart_columns_layout = st.columns(3)
donut_selections = {}

for chart_column, column_layout in zip(chart_columns, chart_columns_layout):
    values = filtered_data[chart_column].astype("string").str.strip().str.upper()
    values = values.where(values.isin(["Y", "N"]), "Other").fillna("Other")
    counts = values.value_counts().reindex(["Y", "N", "Other"], fill_value=0)
    counts = counts[counts > 0]

    figure = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            customdata=counts.index,
            hole=0.55,
            sort=False,
            texttemplate="%{label}<br>%{percent:.0%}",
            hovertemplate="%{label}<br>%{value}<br>%{percent:.0%}<extra></extra>",
            selected={"marker": {"opacity": 1.0}},
            marker={"colors": ["#2E8B57", "#D95F59", "#9E9E9E"]},
        )
    )
    figure.update_layout(
        title=chart_titles[chart_column],
        showlegend=True,
        clickmode="event+select",
        margin={"t": 55, "b": 10, "l": 10, "r": 10},
        height=320,
    )

    chart_event = column_layout.plotly_chart(
        figure,
        use_container_width=True,
        key=f"donut_{chart_column}",
        on_select="rerun",
        selection_mode=("points",),
        config={"staticPlot": False, "displayModeBar": False},
    )

    donut_selections[chart_column] = selected_values_from_plotly_event(
        chart_event,
        counts.index,
    )

st.subheader("Federations by country")
map_data = filtered_data.copy()
for chart_column, selected_values in donut_selections.items():
    if selected_values:
        values = map_data[chart_column].astype("string").str.strip().str.upper()
        values = values.where(values.isin(["Y", "N"]), "Other").fillna("Other")
        map_data = map_data[values.isin(selected_values)]

country_counts = (
    map_data["Country"]
    .dropna()
    .astype("string")
    .value_counts()
    .rename_axis("Country")
    .reset_index(name="Federations")
)

map_figure = px.choropleth(
    country_counts,
    locations="Country",
    locationmode="country names",
    color="Federations",
    hover_name="Country",
    color_continuous_scale="Greens",
    projection="natural earth",
)
map_figure.update_layout(
    margin={"t": 10, "b": 0, "l": 0, "r": 0},
    height=520,
    showlegend=False,
    coloraxis_showscale=False,
)
st.plotly_chart(map_figure, use_container_width=True)

