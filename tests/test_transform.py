import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from utils.transform import Transformer

class TestTransformer(unittest.TestCase):

    def setUp(self):
        self.transformer = Transformer()
        self.sample_data = {
            'Title': ['Product A', 'Product B', 'Unknown Product', 'Product C'],
            'Price': ['100', '200', '300', 'Price Unavailable'],
            'Rating': ['4.5', '3.0', 'Invalid Rating', '5.0'],
            'Colors': ['Red', 'Blue', 'Green', 'Black'],
            'Size': ['S', 'M', 'L', 'XL'],
            'Gender': ['Male', 'Female', 'Unisex', 'Male']
        }
        self.df = pd.DataFrame(self.sample_data)

        self.expected_clean_data_after_remove_dirty = {
            'Title': ['Product A', 'Product B'],
            'Price': ['100', '200'],
            'Rating': ['4.5', '3.0'],
            'Colors': ['Red', 'Blue'],
            'Size': ['S', 'M'],
            'Gender': ['Male', 'Female']
        }
        self.expected_df_after_remove_dirty = pd.DataFrame(self.expected_clean_data_after_remove_dirty)


    def test_remove_dirty(self):
        cleaned_df = self.transformer.remove_dirty(self.df.copy()) # Use copy to avoid modifying original df
        # Convert expected df columns to match the potential types after loading
        expected_df = self.expected_df_after_remove_dirty.astype(cleaned_df.dtypes)
        assert_frame_equal(cleaned_df, expected_df)

    def test_remove_dirty_no_matching_columns(self):
        # Test case where a column in dirty_patterns doesn't exist in df
        data_missing_col = {
             'Title': ['Product A', 'Product B', 'Unknown Product'],
             'Price': ['100', '200', 'Price Unavailable'],
             # 'Rating' column is missing
        }
        df_missing_col = pd.DataFrame(data_missing_col)
        expected_data = {
            'Title': ['Product A', 'Product B'],
            'Price': ['100', '200'],
        }
        expected_df = pd.DataFrame(expected_data)

        cleaned_df = self.transformer.remove_dirty(df_missing_col.copy())
        expected_df = expected_df.astype(cleaned_df.dtypes)
        assert_frame_equal(cleaned_df, expected_df)


    def test_convert_type(self):
        # Test successful conversion
        df_to_convert = self.expected_df_after_remove_dirty.copy()
        converted_df = self.transformer.convert_type(df_to_convert)
        self.assertTrue(pd.api.types.is_numeric_dtype(converted_df['Rating']))
        self.assertEqual(converted_df['Rating'].tolist(), [4.5, 3.0])

        # Test with non-numeric data (should ideally handle gracefully, but current code prints error)
        df_non_numeric = pd.DataFrame({'Rating': ['4.5', 'Not a number', '3.0']})
        # We expect the conversion to fail for 'Not a number' and potentially raise or coerce to NaN
        # Based on pd.to_numeric default behavior (errors='raise'), it should raise ValueError
        # The try-except block in the code catches this and prints.
        # Let's test that the column remains object type after the failed attempt.
        converted_df_error = self.transformer.convert_type(df_non_numeric.copy())
        # Check if the column type is still object or if conversion partially happened
        # Since the error is caught, the original df is returned.
        self.assertTrue(pd.api.types.is_object_dtype(converted_df_error['Rating']))


    def test_clean(self):
        cleaned_df = self.transformer.clean(self.df.copy())

        # Expected result after both remove_dirty and convert_type
        expected_data_final = {
            'Title': ['Product A', 'Product B'],
            'Price': ['100', '200'],
            'Rating': [4.5, 3.0], # Numeric type
            'Colors': ['Red', 'Blue'],
            'Size': ['S', 'M'],
            'Gender': ['Male', 'Female']
        }
        expected_df_final = pd.DataFrame(expected_data_final)

        # Ensure dtypes match before comparison
        expected_df_final = expected_df_final.astype(cleaned_df.dtypes)

        assert_frame_equal(cleaned_df, expected_df_final)

if __name__ == '__main__':
    unittest.main()
