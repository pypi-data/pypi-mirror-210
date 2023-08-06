# yfinance Package with Wide-Form Data Support and Data Export

`yfinance-extended` extends `yfinance` package by Ran Aroussi and make it easier to:
1. Retrieve multiple-ticker intraday price data in a wide-form `pandas` dataframe;
2. Read options data for all available expiration dates;
3. Retrieve top-of-the-book bid-ask prices and sizes; and,
4. Store data in the parquet format with the following structure:
```
./saved_data
├── AAPL
│   ├── AAPL-2023-04-24.parquet
│   ├── AAPL-2023-04-25.parquet
│   ├── AAPL-2023-04-26.parquet
│   ├── AAPL-2023-04-27.parquet
│   └── AAPL-2023-04-28.parquet
└── TSM
    └── TSM-2023-04-24.parquet
    └── TSM-2023-04-25.parquet
    └── TSM-2023-04-26.parquet
    └── TSM-2023-04-27.parquet
    └── TSM-2023-04-28.parquet
```

## Sample Usage
### Get Historical Data
Getting past five days of minute-by-minute prices of Apple, Inc., including pre-/post-market data.
```python
import yfinance-extended as yfe

loader = yfe.YahooBatchLoader()

price_df = get_historical_prices("AAPL", period="5d", interval="1m", prepost=True)
prices_df = get_historical_prices(["AAPL", "GOOGL"], period="5d", interval="1m", prepost=True)
```

### Read all Available Options Information
```python
options_df = loader.options_data("AAPL")
```

### Get Top-of-the-Book Data
```python
live_prices_df = loader.get_prices("AAPL")
live_prices_df = loader.get_prices(["AAPL", "GOOGL"])
```

### Save to and Read Data from Parquet Files
Save files:
```python
prices_df = get_historical_prices(["AAPL", "GOOGL"], period="5d", interval="1m", prepost=True)
yfe.to_parquet(prices_df, root_dir="./data")
```
Read files:
```python
prices_df = yfe.read_parquet(root_dir="./data")
```
Alternatively, if you wish to save all data into one file:
```python
# Write to one file
yfe.to_parquet(prices_df, filepath="./data/datafile.parquet")

# Read from the file
prices_df = yfe.read_parquet(filepath="./data/datafile.parquet")
```