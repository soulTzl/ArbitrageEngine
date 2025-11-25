"""Gas Cost Estimation for Transactions"""

class GasEstimator:
    """Estimates gas costs for different transaction types"""

    def __init__(self, web3_client=None):
        self.w3 = web3_client
        self.gas_prices = {
            'slow': 0,
            'standard': 0,
            'fast': 0
        }
        if web3_client:
            self.update_gas_prices()

    def update_gas_prices(self):
        """Fetch current gas prices from network"""
        if not self.w3:
            # Mock gas prices
            self.gas_prices = {
                'slow': 20e9,      # 20 gwei
                'standard': 30e9,  # 30 gwei
                'fast': 50e9       # 50 gwei
            }
            return

        current_price = self.w3.eth.gas_price
        self.gas_prices = {
            'slow': current_price * 0.8,
            'standard': current_price,
            'fast': current_price * 1.2
        }

    def estimate_swap_cost(self, swap_type='uniswap_v2', speed='standard'):
        """
        Estimate gas cost for a token swap.

        Typical gas usage:
        - Uniswap V2 swap: 100,000 - 150,000 gas
        - Uniswap V3 swap: 120,000 - 180,000 gas
        - Multi-hop swap: 150,000 - 250,000 gas
        """
        gas_units = {
            'uniswap_v2': 120000,
            'uniswap_v3': 150000,
            'curve': 200000,
            'multi_hop': 200000
        }

        gas_price = self.gas_prices[speed]
        estimated_gas = gas_units.get(swap_type, 150000)

        # Cost in wei
        cost_wei = gas_price * estimated_gas

        # Convert to ETH
        cost_eth = cost_wei / 1e18

        return {
            'gas_units': estimated_gas,
            'gas_price_gwei': gas_price / 1e9,
            'total_cost_eth': cost_eth,
            'total_cost_usd': cost_eth * 2000  # Assuming ETH = $2000
        }

    def estimate_arbitrage_cost(self, n_swaps=2, speed='fast'):
        """
        Estimate total gas cost for arbitrage execution.

        Includes:
        - Token approvals (if needed)
        - Multiple swaps
        - Safety margin
        """
        approval_gas = 50000
        swap_gas = 150000 * n_swaps
        total_gas = approval_gas + swap_gas

        gas_price = self.gas_prices[speed]
        cost_wei = gas_price * total_gas * 1.1  # 10% safety margin
        cost_eth = cost_wei / 1e18

        return {
            'total_gas': total_gas,
            'cost_eth': cost_eth,
            'cost_usd': cost_eth * 2000
        }
