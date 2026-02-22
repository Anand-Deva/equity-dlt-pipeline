#!/bin/bash
set -e
python stockdata_pipeline.py
python yfinance_pipeline.py
