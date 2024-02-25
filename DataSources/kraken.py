"""Get financial data from Kraken API."""

import ccxt
from DataSources.IDataSource import IDataSource, exponential_backoff


class Kraken(IDataSource):
    """A source for financial data from Kraken API."""

    def __init__(self, key, secret):
        self.exchange = ccxt.kraken

    def get_securities(self):
        """Get a list of all securities available from the source."""
        return self.exchange.symbols

    def download_historical_data(self, tickers, period="1d"):
        """Downloads historical data for a list of tickers.

        Args:
            tickers (List[str]): A list of ticker symbols to download data for.
            period (str, optional): The period to download data for. Defaults to "1d".

        Returns:
            Dict[str, pd.DataFrame]: A dictionary of DataFrames containing the historical data for each ticker.
        """
        data = {}
        for ticker in set(tickers):
            data[ticker] = self.download_ticker_data(ticker, period)
        return data

    def download_ticker_data(self, ticker, period="1d"):
        """Downloads historical data for a single ticker with exponential backoff."""
        return exponential_backoff(5, 1, 0.1, self.exchange.fetch_ohlcv, ticker, period)