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
    # extractor = WebExtractor()
    # urls = [f"https://fashion-studio.dicoding.dev/page{i}" for i in range(10, 14)]
    # results = asyncio.run(extractor.get_all(urls))
    # print(results)
    # print(len(results))

    # df = pandas.DataFrame(results)
    # transformer = Transformer()
    # results = transformer.clean(df)

    # results.to_csv("fashionstudio.csv", index=False)
    from tests.test_extract import TestWebExtractorAsync

    TestWebExtractorAsync().test_get_all()
