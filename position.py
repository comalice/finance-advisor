"""position.py - A class to represent a position in a portfolio.

A position is a collection of transactions for a single security.
"""
from datetime import datetime
from enum import Enum
from typing import List
from transaction import Transaction, Action


class Status(Enum):
    OPEN = 1
    CLOSED = 2


class Position:
    """A class to represent a position in a portfolio."""

    def __init__(self, ticker, transactions: List[Transaction] = None, market_value=None):
        self.status = None
        self.ticker = ticker
        # a transaction consists of a date, a price, and a quantity
        # buy/sell is denoted by the sign of the quantity; buy is positive, sell is negative
        if transactions:
            self.transactions = transactions
        else:
            self.transactions = []

        self.market_value = market_value
        self.set_status()  # Call set_status to initialize

    def set_status(self):
        """Updates the status and quantity based on the transactions."""
        total_quantity = sum(transaction.quantity for transaction in self.transactions)
        self.status = Status.OPEN if total_quantity > 0 else Status.CLOSED

    def add_transaction(self, transaction):
        """Add a transaction to the position."""
        # print(f"Adding transaction {transaction} to position {self}")
        self.transactions.append(transaction)
        self.set_status()  # Update status after adding transaction

    def merge_position(self, position):
        """Merge a position into this position."""
        self.transactions.extend(position.transactions)
        self.set_status()  # Update status after merging

    def get_quantity(self):
        """Get the quantity of securities held in the position."""
        return sum(transaction.quantity for transaction in self.transactions)

    def get_value(self):
        """Get the value of the position."""
        if self.get_status() == Status.CLOSED:
            # If the position is closed, the value is 0
            return 0

        if self.market_value is not None:
            return self.get_quantity() * self.market_value

    def get_value_at_price(self, price):
        """Get the value of the position at a given price."""
        return self.get_quantity() * price

    def get_time_held(self, date=None):
        """Get the time held for the position."""
        if self.get_status() == Status.CLOSED:
            # Ensure the transactions are sorted by date
            sorted_transactions = sorted(self.transactions, key=lambda txn: txn.date)
            return sorted_transactions[-1].date - sorted_transactions[0].date

        if not date:
            date = datetime.now()

        return date - self.transactions[0].date

    def get_cost_basis(self):
        """Get the cost basis of the position."""
        cost_basis = 0
        for transaction in self.transactions:
            # We expect credits to be positive quantities or prices, and debits to be negative quantities or prices.
            cost_basis = cost_basis + transaction.price * transaction.quantity
        return cost_basis

    def get_return(self):
        """Get return of the position."""
        if self.get_status() == Status.CLOSED:
            # If the position is closed, the return is whatever is left in the cost basis.
            return self.get_cost_basis()

        return self.get_value() - self.get_cost_basis()

    def get_return_percent(self):
        """Get return of the position in %."""
        if self.get_status() == Status.CLOSED:
            # If the position is closed, the return percent is cost_basis divided by all the buy transactions.
            return self.get_cost_basis() / sum([txn.amount for txn in self.transactions if txn.action == Action.BUY])
        return self.get_return() / self.get_cost_basis()

    def get_annualized_return(self):
        """Get the annualized return of the position."""
        return self.get_return_percent() / self.get_time_held().days * 365

    def get_status(self):
        """Get the status of the position."""
        return self.status

    def __str__(self):
        return f"Position(ticker={self.ticker}\n\ttransactions={self.transactions}\n\tmarket_value={self.market_value})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.ticker)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
