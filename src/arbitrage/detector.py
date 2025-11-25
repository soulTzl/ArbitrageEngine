"""Arbitrage Opportunity Detection Engine"""

import numpy as np
from typing import List, Dict
from scipy.optimize import minimize_scalar

class ArbitrageDetector:
    """Detects arbitrage opportunities across multiple AMMs"""

    def __init__(self, amms, min_profit_threshold=0.01):
        self.amms = amms
        self.min_profit_threshold = min_profit_threshold
        self.opportunities = []

    def find_two_pool_arbitrage(self, token_pair):
        """
        Find arbitrage between two pools for the same token pair.

        Strategy:
        1. Compare prices across all pools
        2. Calculate potential profit for various trade sizes
        3. Account for gas costs and slippage
        4. Filter opportunities above minimum threshold
        """
        token0, token1 = token_pair
        pools = [amm for amm in self.amms if amm.has_pair(token0, token1)]

        opportunities = []

        for i in range(len(pools)):
            for j in range(i + 1, len(pools)):
                pool_a = pools[i]
                pool_b = pools[j]

                # Calculate price difference
                price_a = pool_a.get_spot_price()
                price_b = pool_b.get_spot_price()

                if abs(price_a - price_b) / min(price_a, price_b) < 0.001:
                    continue  # Price difference too small

                # Determine trade direction
                if price_a < price_b:
                    buy_pool = pool_a
                    sell_pool = pool_b
                else:
                    buy_pool = pool_b
                    sell_pool = pool_a

                # Find optimal trade size
                optimal_amount = self._optimize_trade_size(
                    buy_pool, sell_pool, token0, token1
                )

                if optimal_amount > 0:
                    profit = self._calculate_net_profit(
                        buy_pool, sell_pool, token0, token1, optimal_amount
                    )

                    if profit > self.min_profit_threshold:
                        opportunities.append({
                            'buy_pool': buy_pool.name,
                            'sell_pool': sell_pool.name,
                            'token_in': token0,
                            'token_out': token1,
                            'amount': optimal_amount,
                            'expected_profit': profit,
                            'timestamp': self._get_timestamp()
                        })

        return opportunities

    def _optimize_trade_size(self, buy_pool, sell_pool, token0, token1):
        """
        Find optimal trade size that maximizes profit.

        Uses scipy.optimize.minimize_scalar
        """
        def negative_profit(amount):
            # Simulate buy from pool A
            buy_pool_copy = buy_pool.copy()
            amount_out_buy = buy_pool_copy.get_amount_out(
                amount, buy_pool_copy.reserve0, buy_pool_copy.reserve1
            )

            # Simulate sell to pool B
            sell_pool_copy = sell_pool.copy()
            amount_out_sell = sell_pool_copy.get_amount_out(
                amount_out_buy, sell_pool_copy.reserve1, sell_pool_copy.reserve0
            )

            # Net profit (negative for minimization)
            profit = amount_out_sell - amount
            return -profit

        result = minimize_scalar(
            negative_profit,
            bounds=(0.01, 1000),
            method='bounded'
        )

        return result.x if -result.fun > 0 else 0

    def _calculate_net_profit(self, buy_pool, sell_pool, token0, token1, amount):
        """Calculate net profit after gas costs"""
        # Simulate trades
        buy_pool_copy = buy_pool.copy()
        sell_pool_copy = sell_pool.copy()

        amount_out_buy = buy_pool_copy.swap(amount, 'x_to_y')
        amount_out_sell = sell_pool_copy.swap(amount_out_buy, 'y_to_x')

        # Gross profit
        gross_profit = amount_out_sell - amount

        # Estimate gas costs (placeholder - implement real gas estimation)
        gas_cost = 0.001  # 0.001 ETH

        return gross_profit - gas_cost

    def _get_timestamp(self):
        """Get current timestamp"""
        import time
        return int(time.time())

    def find_triangular_arbitrage(self, tokens):
        """
        Find triangular arbitrage opportunities.

        Example: ETH -> USDC -> DAI -> ETH
        """
        token_a, token_b, token_c = tokens
        paths = []

        for amm in self.amms:
            if not (amm.has_pair(token_a, token_b) and 
                    amm.has_pair(token_b, token_c) and 
                    amm.has_pair(token_c, token_a)):
                continue

            # Test various starting amounts
            for start_amount in [0.1, 1, 10, 100]:
                # Create copy of AMM
                amm_copy = amm.copy()

                # Step 1: A -> B
                amount_b = amm_copy.swap(start_amount, 'a_to_b')

                # Step 2: B -> C
                amount_c = amm_copy.swap(amount_b, 'b_to_c')

                # Step 3: C -> A
                final_amount_a = amm_copy.swap(amount_c, 'c_to_a')

                profit = final_amount_a - start_amount
                profit_percentage = (profit / start_amount) * 100

                if profit_percentage > self.min_profit_threshold:
                    paths.append({
                        'path': [token_a, token_b, token_c, token_a],
                        'start_amount': start_amount,
                        'end_amount': final_amount_a,
                        'profit': profit,
                        'profit_percentage': profit_percentage,
                        'amm': amm.name
                    })

        return paths
