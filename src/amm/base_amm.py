"""Base class for Automated Market Makers"""

from abc import ABC, abstractmethod

class BaseAMM(ABC):
    """Abstract base class for all AMM implementations"""

    def __init__(self, name, fee=0.003):
        self.name = name
        self.fee = fee

    @abstractmethod
    def get_amount_out(self, amount_in, reserve_in, reserve_out):
        """Calculate output amount for given input"""
        pass

    @abstractmethod
    def get_spot_price(self):
        """Get current spot price"""
        pass

    @abstractmethod
    def swap(self, amount_in, direction):
        """Execute a swap"""
        pass

    def has_pair(self, token0, token1):
        """Check if AMM has trading pair"""
        return True  # Implement based on actual pool data
