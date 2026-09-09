# Utils for my app

import pandas as pd


def read_csv_data(csv_path: str) -> pd.DataFrame:
    """Read a CSV file into a pandas DataFrame."""
    return pd.read_csv(csv_path)

