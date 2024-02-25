from typing import List, ContextManager, Dict, Iterable
import pandas as pd
from PortfolioSources.IPortfolioSource import IPortfolioSource
from position import Position
from transaction import Transaction


class CsvPortfolioSource(IPortfolioSource, ContextManager):
    """Portfolio data from a CSV file."""

    def __init__(self, file_path, versioning=True, versioning_template="{file_path}.{timestamp}"):
        self.file_path = file_path
        self.positions: Dict[str, Position] = {}
        self._positions: pd.DataFrame = None
        self._old_positions: pd.DataFrame = None
        self.versioning: bool = versioning
        self.versioning_template: str = versioning_template

    def __enter__(self):
        print(f"Opening {self.file_path}...")
        self._positions = pd.read_csv(self.file_path)
        self._old_positions = self._positions.copy()

        self.positions = self._read_positions()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._positions = self._write_positions()

        # If there are no changes, don't write the file.
        if len(self._positions) == len(self._old_positions):
            if self._positions.equals(self._old_positions):
                return

        # Handle versioning
        if self.versioning:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
            new_file_path = self.versioning_template.format(file_path=self.file_path, timestamp=timestamp)
            self._positions.to_csv(new_file_path, index=False)
        else:
            self._positions.to_csv(self.file_path, index=False)

    def _read_positions(self) -> Dict[str, Position]:
        """Read positions in from the underlying dataframe."""
        for index, row in self._positions.iterrows():
            # print(row)
            ticker = row['Ticker']
            if ticker not in self.positions:
                # print(f"Creating position for {ticker}, {row['Date']}, {row['Action']}, {row['Price']}, {row['Quantity']}")
                position = Position(ticker)
                position.add_transaction(Transaction(row['Ticker'], pd.to_datetime(row["Date"]), row["Price"], row["Quantity"]))
                self.positions[ticker] = position
            else:
                # print(f"Adding transaction to position for {ticker}, {row['Date']}, {row['Action']}, {row['Price']}, {row['Quantity']}")
                self.positions[ticker].add_transaction(Transaction(row['Ticker'], pd.to_datetime(row["Date"]), row["Price"], row["Quantity"]))

        return self.positions

    def _write_positions(self) -> pd.DataFrame:
        """Write position objects into the underlying dataframe."""
        data = []
        for ticker, position in self.positions.items():
            for transaction in position.transactions:
                data.append([position.ticker, transaction.date, transaction.price, transaction.quantity])

        return pd.DataFrame(data, columns=["Ticker", "Date", "Price", "Quantity"])

    def get_position(self, ticker) -> Position:
        if ticker in self.positions:
            return self.positions[ticker]

    def get_positions(self) -> Iterable[Position]:
        for ticker, position in self.positions.items():
            yield position

    def add_position(self, position):
        if position.ticker in self.positions:
            self.positions[position.ticker].merge_position(position)
        else:
            self.positions[position.ticker] = position

    def modify_position(self, position):
        old_position = self.get_position(position.ticker)
        if old_position:
            self.delete_position(old_position)
            self.add_position(position)

    def delete_position(self, position):
        self.positions.pop(position.ticker)