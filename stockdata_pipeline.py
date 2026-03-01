import os
import dlt
import logging
from dotenv import load_dotenv
from dlt.sources.rest_api import rest_api_resources

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dlt.source
def stockdata_source(api_token: str, symbols: list):
    # Consolidated configuration: One resource, multiple symbols in one table
    config = {
        "client": {
            "base_url": "https://api.stockdata.org/v1/data/",
        },
        "resources": [
            {
                "name": f"eod_{symbol.lower()}",
                "write_disposition": "merge", # Merge strategie
                "primary_key": ["volume", "date"],
                "endpoint": {
                    "path": "eod",
                    "params": {
                        "symbols": symbol,
                        "api_token": api_token,
                        "limit": 100, 
                    },
                    "data_selector": "data",
                    "paginator": {
                        "type": "json_link",
                        "next_url_path": "meta.next_page_url" # Verify this path in actual JSON response
                    }
                },
            }
            for symbol in ["AAPL", "TSLA", "MSFT"]
        ],
    }
    yield from rest_api_resources(config)

def load_data():
    api_token = os.getenv("stockdata_token")
    symbols = ["AAPL", "TSLA", "MSFT"]
    
    pipeline = dlt.pipeline(
        pipeline_name="stock_ingestion",
        destination="bigquery",
        staging="filesystem",
        dataset_name="market_data"
    )

    try:
        info = pipeline.run(stockdata_source(api_token,symbols))
        info.raise_on_failed_jobs()
        logger.info("Pipeline ran successfully.")
        
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    load_dotenv()
    load_data()
