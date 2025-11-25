"""Uniswap V2 Constant Product Market Maker Implementation"""

from .base_amm import BaseAMM

class UniswapV2AMM(BaseAMM):
    """
    Uniswap V2 AMM using constant product formula: x * y = k
    """

    def __init__(self, token0_reserve, token1_reserve, fee=0.003, name="Uniswap V2"):
        super().__init__(name, fee)
        self.reserve0 = token0_reserve
        self.reserve1 = token1_reserve
        self.k = token0_reserve * token1_reserve

    def get_amount_out(self, amount_in, reserve_in, reserve_out):
        """
        Calculate output amount using Uniswap V2 formula.

        Formula:
        amount_out = (amount_in * (1 - fee) * reserve_out) / 
                     (reserve_in + amount_in * (1 - fee))
        """
        if amount_in <= 0:
            return 0

        amount_in_with_fee = amount_in * (1 - self.fee)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee

        return numerator / denominator

    def get_spot_price(self):
        """Calculate current spot price (token1 / token0)"""
        return self.reserve1 / self.reserve0

    def swap(self, amount_in, direction):
        """
        Execute a swap and update reserves.

        Args:
            amount_in: Input token amount
            direction: 'x_to_y' or 'y_to_x'

        Returns:
            Output token amount
        """
        if direction == 'x_to_y':
            amount_out = self.get_amount_out(amount_in, self.reserve0, self.reserve1)
            self.reserve0 += amount_in
            self.reserve1 -= amount_out
        else:  # y_to_x
            amount_out = self.get_amount_out(amount_in, self.reserve1, self.reserve0)
            self.reserve1 += amount_in
            self.reserve0 -= amount_out

        return amount_out

    def calculate_slippage(self, amount_in):
        """
        Calculate price slippage for a trade.

        Slippage = (effective_price - spot_price) / spot_price
        """
        spot_price = self.get_spot_price()
        amount_out = self.get_amount_out(amount_in, self.reserve0, self.reserve1)
        effective_price = amount_out / amount_in if amount_in > 0 else 0

        slippage = (effective_price - spot_price) / spot_price if spot_price > 0 else 0
        return slippage

    def copy(self):
        """Create a copy of the AMM state"""
        return UniswapV2AMM(self.reserve0, self.reserve1, self.fee, self.name)
