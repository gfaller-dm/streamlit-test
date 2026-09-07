# General Notes

python version: 3.11

## Sync Databricks

- Download the app files to your computer:  
`databricks workspace export-dir /Workspace/Users/gerhard@gerhardfaller.de/databricks_apps/streamlit-test_2026_09_03-14_31/streamlit-data-app-obo-user .`

- Sync your changes:  
`databricks sync --watch . /Workspace/Users/gerhard@gerhardfaller.de/databricks_apps/streamlit-test_2026_09_03-14_31/streamlit-data-app-obo-user`

- Deploy to Databricks Apps:  
`databricks apps deploy streamlit-test --source-code-path /Workspace/Users/gerhard@gerhardfaller.de/databricks_apps/streamlit-test_2026_09_03-14_31/streamlit-data-app-obo-user`


## Start Streamlit

`streamlit run app.py`

