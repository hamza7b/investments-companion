import os
import pandas as pd
import yfinance as yf


def download_and_save_prices(ticker, start_date, end_date, data_dir='../data'):
    """
    Download historical prices from Yahoo Finance and save to CSV.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol (e.g., 'UBS', 'APPLE')
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    data_dir : str
        Directory to save CSV file (default: ../data)
    
    Returns:
    --------
    prices : ndarray
        Flattened array of closing prices
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Download data
    print(f"Downloading {ticker} data from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    # Save to CSV
    filename = f"{data_dir}/{ticker}_{start_date}_{end_date}.csv"
    data.to_csv(filename)
    print(f"✓ Saved to {filename}")
    
    # Extract and flatten prices
    prices = data['Close'].values.flatten()
    return prices, filename


def load_prices_from_csv(filepath):
    """
    Load prices from CSV file.
    
    Parameters:
    -----------
    filepath : str
        Path to CSV file
    
    Returns:
    --------
    prices : ndarray
        Flattened array of closing prices
    """
    df = pd.read_csv(filepath, index_col=0)
    prices = df['Close'].values.flatten()
    print(f"✓ Loaded {len(prices)} prices from {filepath}")
    return prices
