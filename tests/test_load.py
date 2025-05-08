import pytest
import os
import pandas as pd

from utils.load import export_to_csv

data = [
        {"Title": "Product 1", "Price": 10, "Rating": 4.8, "Colors": 5, "Size": "M", "Gender": "Men"},
        {"Title": "Product 2", "Price": 20, "Rating": 5, "Colors": 6, "Size": "L", "Gender": "Women"},
    ]       
filename = "test.csv"

def test_export_to_csv():
    export_to_csv(data, filename)
    df = pd.read_csv(filename)
    pd.testing.assert_frame_equal(df, pd.DataFrame(data))

    os.remove(filename)

def test_export_to_csv_failed():
    with pytest.raises(ValueError):
        export_to_csv("data", filename)
