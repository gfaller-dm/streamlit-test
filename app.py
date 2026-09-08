import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.utils import *

# Load and check environment variable is set correctly
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."
APP_USER_AUTH = os.getenv('APP_USER_AUTH')
assert APP_USER_AUTH, "APP_USER_AUTH must be set in app.yaml."

# Query
sql_query = "select * from workspace.default.sports_federations_safeguarding_country limit 1000"

# Query the SQL data
if APP_USER_AUTH == "Y":

    print('User authentication is enabled. Querying with user access token.')

    # Extract user access token from the request headers
    user_token = st.context.headers.get('X-Forwarded-Access-Token')
    # Query the SQL data using the user token
    data = sql_query_with_user_token(sql_query, user_token=user_token)

else:
    print('User authentication is disabled. Querying with service principal credentials.')
    # In order to query with Service Principal credentials, comment the above line and uncomment the below line
    data = sql_query_with_service_principal(sql_query)

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
selected_federations = filter_columns[0].multiselect(
    "Federation", options=federation_options, key="selected_federations"
)
selected_sports = filter_columns[1].multiselect(
    "Sport", options=sport_options, key="selected_sports"
)

filtered_data = data
if selected_federations:
    filtered_data = filtered_data[filtered_data["Federation"].isin(selected_federations)]
if selected_sports:
    filtered_data = filtered_data[filtered_data["Sport"].isin(selected_sports)]

st.subheader("Safeguarding policies")
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
            hole=0.55,
            sort=False,
            texttemplate="%{label}<br>%{percent:.0%}",
            marker={"colors": ["#2E8B57", "#D95F59", "#9E9E9E"]},
        )
    )
    figure.update_layout(
        title=chart_titles[chart_column],
        showlegend=True,
        margin={"t": 55, "b": 10, "l": 10, "r": 10},
        height=320,
    )
    chart_event = column_layout.plotly_chart(
        figure,
        use_container_width=True,
        key=f"donut_{chart_column}",
        on_select="rerun",
        selection_mode=("points",),
    )
    donut_selections[chart_column] = {
        point["label"]
        for point in chart_event.get("selection", {}).get("points", [])
        if "label" in point
    }

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
)
st.plotly_chart(map_figure, use_container_width=True)



