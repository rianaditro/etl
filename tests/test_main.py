import unittest
import runpy
from unittest.mock import patch, MagicMock, AsyncMock
import pandas as pd
import asyncio # Import asyncio to reference it in patch

# Define a sample structure for the data returned by the mocked extractor
mock_extracted_data = [
    {'Title': 'Prod1', 'Price': '10', 'Rating': '4.0', 'Colors': 'R', 'Size': 'S', 'Gender': 'M', 'Timestamp': 'ts1'},
    {'Title': 'Prod2', 'Price': '20', 'Rating': '3.5', 'Colors': 'B', 'Size': 'M', 'Gender': 'F', 'Timestamp': 'ts2'}
]

# Define a sample structure for the data after transformation
mock_transformed_data = pd.DataFrame([
    {'Title': 'Prod1', 'Price': '10', 'Rating': 4.0, 'Colors': 'R', 'Size': 'S', 'Gender': 'M', 'Timestamp': 'ts1'},
]) # Assuming Prod2 might be filtered out or Rating converted


class TestMainScript(unittest.TestCase):

    @patch('main.WebExtractor')
    @patch('main.Transformer')
    @patch('main.asyncio.run')
    @patch('main.pandas.DataFrame') # Patch the DataFrame constructor in main's context
    def test_main_flow(self, mock_pd_dataframe, mock_asyncio_run, mock_transformer_class, mock_webextractor_class):
        # --- Arrange Mocks ---

        # 1. Mock WebExtractor instance and its get_all method
        mock_extractor_instance = MagicMock()
        # Configure get_all to be an async mock if needed, but asyncio.run is mocked anyway
        # We just need asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_extracted_data
        mock_webextractor_class.return_value = mock_extractor_instance

        # 2. Mock Transformer instance and its clean method
        mock_transformer_instance = MagicMock()
        mock_transformer_instance.clean.return_value = mock_transformed_data # Return the transformed DataFrame
        mock_transformer_class.return_value = mock_transformer_instance

        # 3. Mock pandas DataFrame instance returned by the constructor
        #    and its to_csv method
        mock_df_instance = MagicMock()
        mock_to_csv = MagicMock()
        mock_df_instance.to_csv = mock_to_csv
        # Make the DataFrame constructor return our *second* mock DataFrame instance
        # The first call to pd.DataFrame uses the extractor results
        # The second call (implicitly via transformer.clean) returns the transformed one
        # Let's refine: We patch the constructor, it gets called with extractor results.
        # Then transformer.clean is called on *that* df instance.
        # Then the *result* of clean (mock_transformed_data) has .to_csv called.
        # So, we need the DataFrame constructor mock to return something,
        # and then assert that to_csv is called on the result of transformer.clean

        # Let the constructor return a basic mock df for the first call
        mock_initial_df = MagicMock()
        mock_pd_dataframe.return_value = mock_initial_df

        # The result of transformer.clean is mock_transformed_data (which is already a DataFrame)
        # We need to patch the to_csv method *on this specific DataFrame object* if possible,
        # or more simply, patch it globally on the DataFrame class for the duration of the test.
        # Let's patch it globally for simplicity.

        with patch('pandas.DataFrame.to_csv') as mock_global_to_csv:

            # --- Act ---
            # Execute the main.py script as __main__
            # runpy executes the module in a separate namespace, but patches apply
            script_globals = runpy.run_module('main', run_name='__main__')

            # --- Assert ---
            # 1. Check WebExtractor initialization and get_all call (via asyncio.run)
            mock_webextractor_class.assert_called_once()
            mock_asyncio_run.assert_called_once()
            # Check the *argument* passed to asyncio.run, which should be the result of extractor.get_all(urls)
            # This is tricky as get_all is called inside run. Let's check the extractor instance method was prepared.
            # We can check if the extractor instance's get_all was accessed.
            # Better: Check the expected URLs were generated and used implicitly by asyncio.run's argument
            # For simplicity, we trust asyncio.run was called with the right coroutine.

            # 2. Check pandas DataFrame was initialized with extracted data
            mock_pd_dataframe.assert_called_once_with(mock_extracted_data)

            # 3. Check Transformer initialization and clean call
            mock_transformer_class.assert_called_once()
            mock_transformer_instance.clean.assert_called_once_with(mock_initial_df) # Called with the initial DF

            # 4. Check final DataFrame's to_csv call
            # The object `results` in main.py becomes `mock_transformed_data` after the clean call.
            # We assert that the globally patched to_csv was called on our transformed data object.
            # This assertion is tricky because mock_transformed_data is a real DataFrame.
            # The patch replaces the method on the *class*.
            mock_global_to_csv.assert_called_once_with("fashionstudio.csv", index=False)


if __name__ == '__main__':
    unittest.main()
