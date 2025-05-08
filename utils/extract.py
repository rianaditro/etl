import asyncio
import re
import datetime

from curl_cffi import AsyncSession
from bs4 import BeautifulSoup



class WebExtractor:
    def __init__(self):
        self.session = AsyncSession()
    
    async def fetch(self, url: str) -> list:
        """
        Fetches the URL and extracts the data from the HTML response.
        """
        print(f"Fetching URL: {url}")

        try:
            response = await self.session.get(url, impersonate="firefox")
            response.raise_for_status()
            html = response.text
            result = self.parse(html)
        except Exception as e:
            print(f"Failed to fetch URL: {url}. Error: {e}")
            return []
        
        print(f"Total result: {len(result)}")
        return result
    
    async def get_all(self, urls: list) -> list:
        """
        Fetches all the URLs and returns the results in a single list.
        """
        print(f"Starting to fetch {len(urls)} URLs...")
        tasks = [self.fetch(url) for url in urls]
        result = await asyncio.gather(*tasks)
        result = [item for sublist in result for item in sublist]
        print(f"Finished fetching URLs. Total results collected: {len(result)}")
        return result
    
    def clean_text(self, element: BeautifulSoup) -> str:
        """
        Extracts the text from the provided HTML element and removes any
        unwanted strings.
        """
        if element is None:
            return ""

        text = element.get_text(strip=True)
        removes = ["$", "Rating: ", "⭐ ", " / 5", "Colors: ", " Colors", "Size: ", "Gender: "]
        pattern = '|'.join(map(re.escape, removes)) 
        
        return re.sub(pattern, '', text)
        
    def get_data_card(self, card_element: BeautifulSoup) -> dict:
        """
        Extracts the data from a collection card element.
        """

        title = card_element.find("h3", {"class": "product-title"})
        price = card_element.find("div", {"class": "price-container"})
        
        details = card_element.find_all("p")
        # Get only 4 last element
        if len(details) > 4:
            details = details[1:]
        
        # Collect data
        try:
            data = {
                "Title": title,
                "Price": price,
                "Rating": details[0],
                "Colors": details[1],
                "Size": details[2],
                "Gender": details[3],
                }
            
            # Clean data
            for key, value in data.items():
                data[key] = self.clean_text(value)

            # Add timestamp
            data["Timestamp"] = datetime.datetime.now()

            # Convert to rupiah
            data["Price"] = int(data["Price"]) * 16000

        except Exception as e:
            print(f"Failed to extract data from card. Error: {e}")
            print(title, price, details, data)
            return {}
        
        return data

    def parse(self, html: str) -> list:
        """
        Extracts the data from the HTML string.
        """
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            collection_list = soup.find("div", {"id": "collectionList"})
            if not collection_list:
                raise ValueError("Collection list not found in HTML")
            
            collection_cards = collection_list.find_all("div", {"class": "collection-card"})
            if not collection_cards:
                raise ValueError("No collection cards found in collection list")

            for card in collection_cards:
                data = self.get_data_card(card)
                results.append(data)
        except Exception as e:
            print(f"Error parsing HTML: {e}")

        return results
        
