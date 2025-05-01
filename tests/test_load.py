import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.load import export_to_csv

class TestLoad(unittest.TestCase):

    @patch('utils.load.pandas.DataFrame') # Patch DataFrame constructor
    @patch('pandas.DataFrame.to_csv')    # Patch to_csv method on the instance
    def test_export_to_csv(self, mock_to_csv, mock_dataframe_constructor):
        # Arrange
        sample_data = [
            {'col1': 1, 'col2': 'a'},
            {'col1': 2, 'col2': 'b'}
        ]
        filename = "test_output.csv"

        # Create a mock DataFrame instance to be returned by the constructor
        mock_df_instance = MagicMock()
        mock_dataframe_constructor.return_value = mock_df_instance
        # Assign the mock_to_csv to the to_csv attribute of the mock instance
        mock_df_instance.to_csv = mock_to_csv

        # Act
        export_to_csv(sample_data, filename)

        # Assert
        # 1. Check if DataFrame was called with the correct data
        mock_dataframe_constructor.assert_called_once_with(sample_data)

        # 2. Check if to_csv was called on the DataFrame instance with the correct arguments
        mock_to_csv.assert_called_once_with(filename, index=False)

if __name__ == '__main__':
    unittest.main()
