from pathlib import Path

import pandas as pd

from utils.utils import read_csv_data


def test_read_csv_data_reads_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"Federation": ["F1", "F2"], "Sport": ["Football", "Tennis"]}).to_csv(
        csv_path,
        index=False,
    )

    result = read_csv_data(str(csv_path))

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert result["Federation"].tolist() == ["F1", "F2"]
