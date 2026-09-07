import os
import streamlit as st
import pandas as pd

from utils.utils import *

# Ensure environment variable is set correctly
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml."

# Extract user access token from the request headers
user_token = st.context.headers.get('X-Forwarded-Access-Token')


# Streamlit app
st.set_page_config(layout="wide")

st.header("Taxi fare distribution !!! :)")

col1, col2 = st.columns([3, 1])

# Query the SQL data with the user credentials
data = sql_query_with_user_token("SELECT * FROM samples.nyctaxi.trips LIMIT 5000", user_token=user_token)

# In order to query with Service Principal credentials, comment the above line and uncomment the below line
# data = sql_query_with_service_principal("SELECT * FROM samples.nyctaxi.trips LIMIT 5000")

with col1:
    st.scatter_chart(data=data, height=400, width=700, y="fare_amount", x="trip_distance")
with col2:
    st.subheader("Predict fare")
    pickup = st.text_input("From (zipcode)", value="10003")
    dropoff = st.text_input("To (zipcode)", value="11238")
    d = data[(data['pickup_zip'] == int(pickup)) & (data['dropoff_zip'] == int(dropoff))]
    st.write(f"# **${d['fare_amount'].mean() if len(d) > 0 else 99:.2f}**")

st.dataframe(data=data, height=600, use_container_width=True)



