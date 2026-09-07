import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.utils import *

# Load and check environment variable is set correctly
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."
APP_USER_AUTH = os.getenv('APP_USER_AUTH')
assert APP_USER_AUTH, "APP_USER_AUTH must be set in app.yaml."

# Query
sql_query = "select * from workspace.default.sports_federations_safeguarding limit 1000"

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

st.subheader("Safeguarding policies")
chart_columns = ["CodeofEthics", "CodeofConduct", "SpecialEntityDedicated"]
chart_titles = {
    "CodeofEthics": "Code of Ethics",
    "CodeofConduct": "Code of Conduct",
    "SpecialEntityDedicated": "Special Entity Dedicated",
}
chart_columns_layout = st.columns(3)

for chart_column, column_layout in zip(chart_columns, chart_columns_layout):
    values = data[chart_column].astype("string").str.strip().str.upper()
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
    column_layout.plotly_chart(figure, use_container_width=True)

st.dataframe(data=data, height=600, use_container_width=True, hide_index=True)



