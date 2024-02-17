import pandas as pd
import yfinance as yf
import click
from datetime import datetime
import time
from random import random
from talib import ATR
import prettytable


def download_ticker_data(ticker, period="1d", max_retries=5, base_delay=1, jitter=0.1):
    """Downloads historical data for a single ticker with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return yf.download(ticker, period=period, auto_adjust=True)
        except Exception as e:
            delay = (2 ** attempt + random() * jitter) * base_delay
            print(f"Error downloading {ticker}: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    print(f"Failed to download data for {ticker} after {max_retries} attempts.")
    return None


def download_historical_data(tickers, period="1d", max_retries=5, base_delay=1, jitter=0.1):
    """Downloads historical data for a list of tickers with exponential backoff."""
    data = {}
    for ticker in set(tickers):
        data[ticker] = download_ticker_data(ticker, period, max_retries, base_delay, jitter)
    return data


def calculate_atr_values(ohlcv_dict, period=14):
    """Calculates ATR and related values for each ticker in a dictionary of OHLCV data."""
    for ticker, ticker_data in ohlcv_dict.items():
        if ticker_data is not None and len(ticker_data) >= period:
            high = ticker_data['High']
            low = ticker_data['Low']
            close = ticker_data['Close']
            atr = ATR(high, low, close, timeperiod=period)
            ticker_data['ATR'] = atr
            ticker_data['Close_Minus_ATR_15'] = close - atr * 1.5
            ticker_data['Close_Plus_ATR_3'] = close + atr * 3
    return ohlcv_dict


def process_csv(csv_file):
    """Processes the portfolio CSV file and returns enriched data."""
    df = pd.read_csv(csv_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Timedelta'] = (datetime.now() - df['Date']).dt.days
    tickers = df['Ticker'].tolist()
    latest_data = download_historical_data(tickers, period="15d")
    latest_data = calculate_atr_values(latest_data, period=14)
    for ticker, ticker_data in latest_data.items():
        if ticker_data is not None:
            df.loc[df['Ticker'] == ticker, 'Latest Price'] = ticker_data.iloc[-1]['Close']
            df.loc[df['Ticker'] == ticker, 'ATR'] = ticker_data.iloc[-1]['ATR']
            df.loc[df['Ticker'] == ticker, 'Close_Minus_ATR_15'] = ticker_data.iloc[-1]['Close_Minus_ATR_15']
            df.loc[df['Ticker'] == ticker, 'Close_Plus_ATR_3'] = ticker_data.iloc[-1]['Close_Plus_ATR_3']
    df['Market Value'] = df['Quantity'] * df['Latest Price']
    df['Total Gain/Loss ($)'] = df['Market Value'] - df['Cost Basis']
    df['Total Gain/Loss (%)'] = (df['Market Value'] - df['Cost Basis']) / df['Cost Basis']
    df['ARR'] = (df['Total Gain/Loss (%)'] / df['Timedelta']) * 365
    df['% of Acct'] = df['Market Value'] / df['Market Value'].sum() * 100
    return df


@click.command()
@click.option('--file', type=click.Path(exists=True), prompt='Enter CSV file path:')
@click.option('--portfolio', type=str, default='')
def main(file, portfolio):
    """CLI interface for portfolio analysis."""
    df = process_csv(file)
    if portfolio:
        df = df[df['Tags'].str.contains(portfolio, na=False)]
    print(df.to_string())


if __name__ == '__main__':
    main()
