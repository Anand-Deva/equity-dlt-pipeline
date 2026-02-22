"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import os
import yfinance as yf
import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from dotenv import load_dotenv

@dlt.resource(name="sp500_prices"
        , write_disposition="append")
def sp500_data():
    ticker = yf.Ticker("^GSPC")
    df = ticker.history(period="max", interval="1d")
    df = df.reset_index()
    for row in df.to_dict(orient="records"):
        yield row

pipeline = dlt.pipeline(
        pipeline_name='yfinance_pipeline',
        dataset_name='stock_market_data',
        destination='postgres',
        refresh="drop_sources",
        progress="log",
    )


if __name__ == "__main__":
    load_dotenv()
    load_info = pipeline.run(sp500_data)
    print(load_info)
