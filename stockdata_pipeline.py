"""Template for building a `dlt` pipeline to ingest data from a REST API."""

import os
import dotenv
import dlt
from dlt.sources.rest_api import rest_api_resources


@dlt.source
def stockdata_source(api_token: str):
    # Base configuration for the API client
    config = {
        "client": {
            "base_url": "https://api.stockdata.org/v1/data/",
        },
        "resources": [
            {
                "name": f"eod_{symbol.lower()}",
                "endpoint": {
                    "path": "eod",
                    "params": {
                        "symbols": symbol,
                        "api_token": api_token,
                },
                    "data_selector": "data"
                },
            }
            for symbol in ["AAPL", "TSLA", "MSFT"] # Loop here to create 3 resources
        ],
    }
    yield from rest_api_resources(config)


if __name__ == "__main__":
    dotenv.load_dotenv()
    api_token = os.getenv("stockdata_token")

    eod_pipeline = dlt.pipeline(
        pipeline_name="stockdata_pipeline_postgres",
        destination="postgres", 
        dataset_name="stock_market_data"
    )

    load_info = eod_pipeline.run(stockdata_source(api_token= api_token))
    print(load_info)