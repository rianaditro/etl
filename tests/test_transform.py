import pytest
import pandas as pd

from utils.transform import Transformer



class TestTransformer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.transformer = Transformer()
        self.df = pd.DataFrame({
            "Title": ["Product 1", "Product 2", "Unknown Product"],
            "Price": ["10", "Price Unavailable", "20"],
            "Rating": ["4.8", "5", "Not Rated"],
            "Colors": ["5", "6", "7"],
            "Size": ["M", "L", "S"],
            "Gender": ["Men", "Women", "Unisex"],
        })
    
    def test_remove_dirty(self):
        result = self.transformer.remove_dirty(self.df)
        expected = pd.DataFrame({
            "Title": ["Product 1"],
            "Price": ["10"],
            "Rating": ["4.8"],
            "Colors": ["5"],
            "Size": ["M"],
            "Gender": ["Men"]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_convert_type(self):
        df = self.transformer.remove_dirty(self.df)
        result = self.transformer.convert_type(df)
        expected = pd.DataFrame({
            "Title": ["Product 1"],
            "Price": ["10"],
            "Rating": [4.8],
            "Colors": ["5"],
            "Size": ["M"],
            "Gender": ["Men"]
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_convert_type_failed(self):
        with pytest.raises(ValueError):
            self.transformer.convert_type(self.df)
    
    def test_clean(self):
        result = self.transformer.clean(self.df)
        expected = pd.DataFrame({
            "Title": ["Product 1"],
            "Price": ["10"],
            "Rating": [4.8],
            "Colors": ["5"],
            "Size": ["M"],
            "Gender": ["Men"]
        })
        pd.testing.assert_frame_equal(result, expected)