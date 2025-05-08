"""
page 1 - 50
Data yang diambil, meliputi hal berikut.

    Title.
    Price. * 16000
    Rating. --> float
    Colors. --> angka
    Size. replace  Size:
    Gender. replace Gender
    Timestamp

dirty_patterns = {
    "Title": ["Unknown Product"],
    "Rating": ["Invalid Rating / 5", "Not Rated"],
    "Price": ["Price Unavailable", None],
    }
    
export as CSV, Google Sheets, PostgreSQL
test coverage 80-90%
"""
import asyncio
import pandas
from utils.extract import WebExtractor
from utils.transform import Transformer
from utils.load import export_to_csv



if __name__ == "__main__":
    try:
        extractor = WebExtractor()
        transformer = Transformer()

        main_url = "https://fashion-studio.dicoding.dev"

        urls = [f"{main_url}/page{i}" for i in range(2, 51)]
        urls.append(main_url)
        
        results = asyncio.run(extractor.get_all(urls))

        df = pandas.DataFrame(results)
        results = transformer.clean(df)

        export_to_csv(results, "products.csv")
    except Exception as e:
        raise e