"""An ABC for portfolio sources to implement."""

from abc import ABC, abstractmethod
from typing import List

from position import Position


class IPortfolioSource(ABC):
    """Abstract base class for portfolio sources to implement."""

    # methods for adding, modifying, and deleting positions in portfolios
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get the positions in the portfolio."""
        pass

    @abstractmethod
    def add_position(self, entry):
        """Adds a position to the portfolio."""
        pass

    @abstractmethod
    def modify_position(self, entry):
        """Modifies a position in the portfolio."""
        pass

    @abstractmethod
    def delete_position(self, entry):
        """Deletes a position from the portfolio."""
        pass
