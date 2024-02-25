"""ISource.py - ABC for sources to implement.

A source is a class that provides up-to-date financial data. This could be a
web API, a local database, or a CSV file. The source is responsible for
downloading and parsing the data into a format that can be used by the
portfolio tracker.
"""
import time
from abc import ABC, abstractmethod
from random import random


def exponential_backoff(max_retries, base_delay, jitter, func, *args, **kwargs):
    """Exponential backoff for a function that returns a value or None."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            delay = (2 ** attempt + random() * jitter) * base_delay
            print(f"Error: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    print(f"Failed after {max_retries} attempts.")
    return None


class IDataSource(ABC):
    """Abstract base class for sources to implement."""

    @abstractmethod
    def download_historical_data(self, tickers, period="1d"):
        """Downloads historical data for a list of tickers.

        Args:
            tickers (List[str]): A list of ticker symbols to download data for.
            period (str, optional): The period to download data for. Defaults to "1d".

        Returns:
            Dict[str, pd.DataFrame]: A dictionary of DataFrames containing the historical data for each ticker.
        """

    @abstractmethod
    def get_latest_price(self, ticker):
        """Gets the latest price for a single ticker.

        Args:
            ticker (str): The ticker symbol to get the latest price for.

        Returns:
            float: The latest price for the ticker.
        """

    @abstractmethod
    def get_securities(self):
        """Get a list of all securities available from the source.

        Returns:
            List[str]: A list of all available securities.
        """
