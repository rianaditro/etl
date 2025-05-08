import pytest
from unittest.mock import AsyncMock, MagicMock

from bs4 import BeautifulSoup as bs

from utils.extract import WebExtractor


class TestWebExtractor:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.extractor = WebExtractor()
        self.url = "https://www.example.com"
        self.html = """
        <div id="collectionList">
            <div class="collection-card">
                <h3 class="product-title">Product Title</h3>
                <div class="price-container">Price</div>
                <p>Rating: ⭐ 4.8 / 5</p>
                <p>Colors: 5</p>
                <p>Size: M</p>
                <p>Gender: Men</p>
            </div>
        </div>
        """
        self.soup = bs(self.html, "html.parser")
        self.card = self.soup.find("div", {"class": "collection-card"})
        self.element = self.soup.find("p")
        self.result = self.extractor.parse(self.html)

    def test_clean_text(self):
        clean_text = self.extractor.clean_text(self.element)
        assert clean_text == "4.8"

    def test_get_data_card(self):
        data = self.extractor.get_data_card(self.card)
        assert data["Title"] == "Product Title"
        assert data["Price"] == "Price"
        assert data["Rating"] == "4.8"
        assert data["Colors"] == "5"
        assert data["Size"] == "M"
        assert data["Gender"] == "Men"

    def test_parse(self):
        result = self.extractor.parse(self.html)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch(self):        
        mock_response = MagicMock()
        mock_response.text = self.html
        mock_response.raise_for_status = MagicMock()

        self.extractor.session.get = AsyncMock(return_value=mock_response)
        self.extractor.parse = MagicMock(return_value=self.result)

        result = await self.extractor.fetch(self.url)
        
        self.extractor.session.get.assert_called_once_with(self.url, impersonate="firefox")
        self.extractor.parse.assert_called_once_with(self.html)
        
        assert result == self.result

    @pytest.mark.asyncio
    async def test_get_all(self):
        urls = [self.url]
        mock_response = MagicMock()
        mock_response.text = self.html
        mock_response.raise_for_status = MagicMock()

        self.extractor.session.get = AsyncMock(return_value=mock_response)
        self.extractor.parse = MagicMock(return_value=self.result)

        result = await self.extractor.get_all(urls)
        
        self.extractor.session.get.assert_called_once_with(self.url, impersonate="firefox")
        self.extractor.parse.assert_called_once_with(self.html)
        
        assert result == self.result