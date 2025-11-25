"""Backtesting Engine for Arbitrage Strategies"""

import numpy as np
import pandas as pd

class ArbitrageBacktester:
    """Backtests arbitrage strategies on historical data"""

    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.portfolio = {
            'cash': initial_capital,
            'holdings': {},
            'total_value': initial_capital
        }
        self.trades = []
        self.performance_metrics = {}

    def run_backtest(self, historical_data, strategy):
        """
        Execute backtest on historical price data.

        Args:
            historical_data: DataFrame with pool states over time
            strategy: ArbitrageDetector instance

        Returns:
            Performance metrics and trade log
        """
        portfolio_values = []

        # Group by timestamp
        for timestamp in historical_data['timestamp'].unique():
            current_state = historical_data[
                historical_data['timestamp'] == timestamp
            ]

            # Detect opportunities
            opportunities = strategy.find_two_pool_arbitrage(
                ('ETH', 'USDC')
            )

            # Execute most profitable opportunity
            if opportunities:
                best_opp = max(opportunities, key=lambda x: x['expected_profit'])
                self._execute_trade(best_opp, timestamp)

            # Track portfolio value
            current_value = self._calculate_portfolio_value()
            portfolio_values.append({
                'timestamp': timestamp,
                'value': current_value
            })

        # Calculate metrics
        self._calculate_performance_metrics(portfolio_values)

        return {
            'trades': self.trades,
            'metrics': self.performance_metrics,
            'portfolio_history': portfolio_values
        }

    def _execute_trade(self, opportunity, timestamp):
        """Simulate trade execution"""
        trade = {
            'timestamp': timestamp,
            'type': 'arbitrage',
            'buy_pool': opportunity['buy_pool'],
            'sell_pool': opportunity['sell_pool'],
            'amount': opportunity['amount'],
            'profit': opportunity['expected_profit']
        }

        self.trades.append(trade)
        self.portfolio['cash'] += opportunity['expected_profit']

    def _calculate_portfolio_value(self):
        """Calculate current portfolio value"""
        return self.portfolio['cash']

    def _calculate_performance_metrics(self, portfolio_history):
        """Calculate key performance metrics"""
        df = pd.DataFrame(portfolio_history)
        df['returns'] = df['value'].pct_change()

        # Total return
        total_return = (df['value'].iloc[-1] - self.initial_capital) / self.initial_capital

        # Sharpe ratio
        returns_mean = df['returns'].mean()
        returns_std = df['returns'].std()
        sharpe_ratio = (returns_mean / returns_std) * np.sqrt(365) if returns_std > 0 else 0

        # Maximum drawdown
        cumulative_returns = (1 + df['returns']).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # Win rate
        profitable_trades = sum(1 for t in self.trades if t['profit'] > 0)
        win_rate = profitable_trades / len(self.trades) if self.trades else 0

        # Average profit
        avg_profit = np.mean([t['profit'] for t in self.trades]) if self.trades else 0

        self.performance_metrics = {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'total_trades': len(self.trades)
        }
