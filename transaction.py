"""transaction,py - A class to represent a single transaction for a single security."""
from datetime import datetime
from enum import Enum


class Action(Enum):
    BUY = 1
    SELL = 2


class Transaction:
    """A class to represent a single transaction for a single security."""

    def __init__(self, ticker, date, price, quantity, action=None, account=None):
        # TODO wire in account, will be used for double entry accounting
        self.ticker = ticker
        self.date = date
        self.price = price
        self.quantity = quantity
        self.amount = price * quantity
        if action:
            self.action = action
        else:
            self.action = Action.BUY if quantity > 0 else Action.SELL

    def __str__(self):
        return f"Transaction({self.ticker}, {self.date}, {self.price}, {self.quantity})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.date, self.price, self.quantity))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
