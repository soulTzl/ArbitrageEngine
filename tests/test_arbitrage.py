"""Test Arbitrage Detection"""

import pytest
from src.amm.uniswap_v2 import UniswapV2AMM
from src.arbitrage.detector import ArbitrageDetector

def test_detect_arbitrage_opportunity():
    """Test arbitrage detection between two pools"""
    # Pool A: cheaper
    pool_a = UniswapV2AMM(100000, 200000, name="Pool A")

    # Pool B: more expensive
    pool_b = UniswapV2AMM(100000, 210000, name="Pool B")

    detector = ArbitrageDetector([pool_a, pool_b], min_profit_threshold=0)
    opportunities = detector.find_two_pool_arbitrage(('ETH', 'USDC'))

    assert len(opportunities) > 0
    assert opportunities[0]['expected_profit'] > 0

def test_no_arbitrage_same_price():
    """Test that no arbitrage detected when prices are equal"""
    pool_a = UniswapV2AMM(100000, 200000)
    pool_b = UniswapV2AMM(100000, 200000)

    detector = ArbitrageDetector([pool_a, pool_b])
    opportunities = detector.find_two_pool_arbitrage(('ETH', 'USDC'))

    assert len(opportunities) == 0
