from datetime import datetime
from typing import List, Dict

from multimethod import multimethod
from pandas import Timedelta

from DataSources import IDataSource
from position import Position


class Portfolio:
    """A collection of positions segregated by security. In most cases this means a stock ticker."""

    def __init__(self, data_sources: List[IDataSource] = None, positions: List[Position] = None):
        self._gain_loss_date = None
        self._gain_loss = None
        self._cost_basis_date = None
        self._cost_basis = None
        self._last_price_update = None
        self.positions = {}
        self.append(positions or {})
        self._data_sources = data_sources

        # Get latest prices from sources for all positions and cache for 24 hours.
        self.get_latest_prices()

    def append(self, positions: Dict[str, Position]):
        """Add a list of positions to the portfolio."""
        for ticker, position in positions.items():
            print(f"Adding position {position} to portfolio...")
            if position.ticker in self.positions:
                print(f"Position {position} already exists in portfolio. Merging...")
                self.positions[position.ticker].merge_position(position.transactions)
            else:
                print(f"Position {position} does not exist in portfolio. Adding...")
                self.positions[position.ticker] = position

    def get_value(self):
        """Get the total value of the portfolio."""
        total = 0
        for ticker, position in self.positions.items():
            total += position.get_value()
        return total

    def get_latest_prices(self, cache_time=Timedelta(24 * 60 * 60)):
        """Get the latest prices for all positions."""
        if self._last_price_update and datetime.now() < self._last_price_update + cache_time:
            return

        for ticker, position in self.positions.items():
            for source in self._data_sources:
                # try each source until we get a price
                try:
                    market_value = source.download_ticker_data(position.ticker)
                    self.positions[position.ticker].market_value = market_value['Close'].iloc[-1]
                    break
                except Exception as e:
                    raise e

        self._last_price_update = datetime.now()

    def cost_basis(self):
        """Get the cost basis of the portfolio."""
        # Cache the cost basis for 24 hours.
        if self._cost_basis_date and datetime.now() < self._cost_basis_date + Timedelta(24 * 60 * 60):
            return self._cost_basis

        self._cost_basis_date = datetime.now()

        total = 0
        for ticker, position in self.positions.items():
            total += position.get_cost_basis()

        self._cost_basis = total

        return total

    def gain_loss(self):
        """Get the gain or loss of the portfolio."""
        # Update prices and cost basis if stale.
        if (self._gain_loss is None or
                self._last_price_update and datetime.now() > self._last_price_update + Timedelta(24 * 60 * 60)):
            self.get_latest_prices()
            self.cost_basis()
            self._gain_loss = self.get_value() - self.cost_basis()
            self._gain_loss_date = datetime.now()

        return self._gain_loss

    def gain_loss_percent(self):
        """Get the gain or loss of the portfolio as a percentage."""
        # Update prices and cost basis if stale.
        if self._last_price_update and datetime.now() > self._last_price_update + Timedelta(24 * 60 * 60):
            self._gain_loss = self.get_value() - self.cost_basis()

        return self._gain_loss / self._cost_basis

    def average_time_held(self):
        """Get the average time held of the portfolio."""
        total = Timedelta(0)
        for ticker, position in self.positions.items():
            total += position.get_time_held()
        return total / len(self.positions)

    def get_annualized_return(self):
        """Get the annualized rate of return of the portfolio."""
        return self.gain_loss_percent() / self.average_time_held().days * 365
