import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from utils.extract import WebExtractor
import asyncio
import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests


# Mock response object for curl_cffi
class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self._status_code = status_code

    def raise_for_status(self):
        if self._status_code >= 400:
            raise requests.errors.CurlError(f"HTTP status code {self._status_code}")

    @property
    def status_code(self):
        return self._status_code


class TestWebExtractorAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # We patch the session *within* the extractor instance for these tests
        self.extractor = WebExtractor()
        self.mock_session = AsyncMock()
        self.extractor.session = self.mock_session # Replace the real session with the mock

        # Mock datetime for consistent timestamps
        self.mock_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
        self.datetime_patcher = patch('utils.extract.datetime')
        self.mock_datetime = self.datetime_patcher.start()
        self.mock_datetime.datetime.now.return_value = self.mock_now

    async def asyncTearDown(self):
        self.datetime_patcher.stop()
        # Ensure the session is closed if it was ever awaited (good practice)
        if self.mock_session.close.called:
             await self.extractor.session.close()

    # --- Keep existing synchronous tests ---
    def test_clean_text(self):
        # Need a separate extractor instance as setUp is now asyncSetUp
        sync_extractor = WebExtractor()
        sample_element = """
        <p style="
            font-size: 14px;
            color: #777;">
            Rating: ⭐ 3.9 / 5
        </p>
        """
        soup = BeautifulSoup(sample_element, "html.parser")
        text = sync_extractor.clean_text(soup) # Use sync_extractor
        self.assertEqual(text, "3.9")

        # Test with other patterns
        price_element = '<div class="price-container">$ 100</div>'
        soup_price = BeautifulSoup(price_element, "html.parser")
        text_price = sync_extractor.clean_text(soup_price) # Use sync_extractor
        self.assertEqual(text_price, "100")

        colors_element = '<p>Colors: Red, Blue</p>'
        soup_colors = BeautifulSoup(colors_element, "html.parser")
        text_colors = sync_extractor.clean_text(soup_colors) # Use sync_extractor
        self.assertEqual(text_colors, "Red, Blue")

        # Test with None element
        text_none = sync_extractor.clean_text(None) # Use sync_extractor
        self.assertEqual(text_none, "")

    def test_get_data_card(self):
        # Use the mock_now from asyncSetUp for consistency
        sync_extractor = WebExtractor() # Need a separate instance
        with patch('utils.extract.datetime') as mock_datetime: # Still need to patch here for this sync test
            mock_datetime.datetime.now.return_value = self.mock_now

            sample_card_html = """
            <div class="collection-card">
                <h3 class="product-title">Cool T-Shirt</h3>
                <div class="price-container">$ 25</div>
                <p>Rating: ⭐ 4.5 / 5</p>
                <p>Colors: Black, White</p>
                <p>Size: M, L</p>
                <p>Gender: Unisex</p>
            </div>
            """
            soup = BeautifulSoup(sample_card_html, "html.parser")
            card_element = soup.find("div", {"class": "collection-card"})
            data = sync_extractor.get_data_card(card_element) # Use sync_extractor

            expected_data = {
                "Title": "Cool T-Shirt",
                "Price": "25",
                "Rating": "4.5",
                "Colors": "Black, White",
                "Size": "M, L",
                "Gender": "Unisex",
                "Timestamp": self.mock_now # Use mock_now from setup
            }
            self.assertEqual(data, expected_data)

    def test_get_data_card_missing_elements(self):
        sync_extractor = WebExtractor() # Need a separate instance
        with patch('utils.extract.datetime') as mock_datetime: # Still need to patch here
            mock_datetime.datetime.now.return_value = self.mock_now
            sample_card_html_missing = """
            <div class="collection-card">
                <h3 class="product-title">Basic Shirt</h3>
                <div class="price-container">$ 15</div>
                <!-- Missing Rating, Colors, Size, Gender -->
            </div>
            """
            soup = BeautifulSoup(sample_card_html_missing, "html.parser")
            card_element = soup.find("div", {"class": "collection-card"})
            data = sync_extractor.get_data_card(card_element) # Use sync_extractor
            self.assertEqual(data, {}) # Expecting empty dict due to exception handling

    def test_parse(self):
        sync_extractor = WebExtractor() # Need a separate instance
        with patch('utils.extract.datetime') as mock_datetime: # Still need to patch here
            mock_datetime.datetime.now.return_value = self.mock_now
            sample_html = """
            <html><body>
            <div id="collectionList">
                <div class="collection-card">
                    <h3 class="product-title">Product 1</h3>
                    <div class="price-container">$ 10</div>
                    <p>Rating: ⭐ 4.0 / 5</p>
                    <p>Colors: Red</p>
                    <p>Size: S</p>
                    <p>Gender: Male</p>
                </div>
                <div class="collection-card">
                    <h3 class="product-title">Product 2</h3>
                    <div class="price-container">$ 20</div>
                    <p>Rating: ⭐ 3.5 / 5</p>
                    <p>Colors: Blue</p>
                    <p>Size: M</p>
                    <p>Gender: Female</p>
                </div>
            </div>
            </body></html>
            """
            results = sync_extractor.parse(sample_html) # Use sync_extractor
            expected_results = [
                {
                    "Title": "Product 1", "Price": "10", "Rating": "4.0",
                    "Colors": "Red", "Size": "S", "Gender": "Male", "Timestamp": self.mock_now
                },
                {
                    "Title": "Product 2", "Price": "20", "Rating": "3.5",
                    "Colors": "Blue", "Size": "M", "Gender": "Female", "Timestamp": self.mock_now
                }
            ]
            self.assertEqual(results, expected_results)

    def test_parse_no_list(self):
        sync_extractor = WebExtractor() # Need a separate instance
        sample_html_no_list = "<html><body><p>No list here</p></body></html>"
        results = sync_extractor.parse(sample_html_no_list) # Use sync_extractor
        self.assertEqual(results, []) # Expect empty list due to exception

    def test_parse_no_cards(self):
        sync_extractor = WebExtractor() # Need a separate instance
        sample_html_no_cards = """
        <html><body>
        <div id="collectionList">
            <p>No cards inside the list</p>
        </div>
        </body></html>
        """
        results = sync_extractor.parse(sample_html_no_cards) # Use sync_extractor
        self.assertEqual(results, []) # Expect empty list due to exception

    # --- Async tests ---
    async def test_fetch_success(self):
        test_url = "http://example.com/page1"
        mock_html = """
        <html><body><div id="collectionList">
            <div class="collection-card">
                <h3 class="product-title">Async Product</h3>
                <div class="price-container">$ 50</div> <p>Rating: ⭐ 5.0 / 5</p> <p>Colors: Green</p> <p>Size: L</p> <p>Gender: Any</p>
            </div>
        </div></body></html>
        """
        # Configure the mock session's get method to return a mock response
        self.mock_session.get.return_value = MockResponse(text=mock_html, status_code=200)

        result = await self.extractor.fetch(test_url)

        # Assertions
        self.mock_session.get.assert_awaited_once_with(test_url, impersonate="firefox")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {
            "Title": "Async Product", "Price": "50", "Rating": "5.0",
            "Colors": "Green", "Size": "L", "Gender": "Any", "Timestamp": self.mock_now
        })

    async def test_fetch_http_error(self):
        test_url = "http://example.com/notfound"
        # Configure the mock session's get method to return an error status
        self.mock_session.get.return_value = MockResponse(text="Not Found", status_code=404)

        result = await self.extractor.fetch(test_url)

        # Assertions
        self.mock_session.get.assert_awaited_once_with(test_url, impersonate="firefox")
        self.assertEqual(result, []) # Expect empty list on error

    async def test_fetch_request_exception(self):
        test_url = "http://example.com/error"
        # Configure the mock session's get method to raise an exception
        self.mock_session.get.side_effect = requests.errors.CurlError("Network error")

        result = await self.extractor.fetch(test_url)

        # Assertions
        self.mock_session.get.assert_awaited_once_with(test_url, impersonate="firefox")
        self.assertEqual(result, []) # Expect empty list on exception

    async def test_get_all(self):
        urls = ["http://example.com/1", "http://example.com/2"]
        # Mock the fetch method directly for this test
        with patch.object(self.extractor, 'fetch', new_callable=AsyncMock) as mock_fetch:
            # Define return values for consecutive calls to fetch
            mock_fetch.side_effect = [
                [{"Title": "Product 1", "Price": "10", "Timestamp": self.mock_now}], # Result for url1
                [{"Title": "Product 2", "Price": "20", "Timestamp": self.mock_now}]  # Result for url2
            ]

            results = await self.extractor.get_all(urls)

            # Assertions
            self.assertEqual(mock_fetch.call_count, 2)
            mock_fetch.assert_any_await(urls[0])
            mock_fetch.assert_any_await(urls[1])
            self.assertEqual(len(results), 2)
            self.assertEqual(results, [
                {"Title": "Product 1", "Price": "10", "Timestamp": self.mock_now},
                {"Title": "Product 2", "Price": "20", "Timestamp": self.mock_now}
            ])

    async def test_get_all_with_empty_results(self):
        urls = ["http://example.com/empty", "http://example.com/valid"]
        with patch.object(self.extractor, 'fetch', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [
                [], # Empty result for first URL
                [{"Title": "Valid Product", "Price": "30", "Timestamp": self.mock_now}]
            ]

            results = await self.extractor.get_all(urls)

            self.assertEqual(mock_fetch.call_count, 2)
            self.assertEqual(len(results), 1)
            self.assertEqual(results, [{"Title": "Valid Product", "Price": "30", "Timestamp": self.mock_now}])


if __name__ == "__main__":
    unittest.main()
