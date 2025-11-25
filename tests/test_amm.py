"""Test AMM Implementations"""

import pytest
from src.amm.uniswap_v2 import UniswapV2AMM

def test_uniswap_v2_get_amount_out():
    """Test Uniswap V2 pricing formula"""
    amm = UniswapV2AMM(
        token0_reserve=100000,
        token1_reserve=200000,
        fee=0.003
    )

    amount_in = 1000
    amount_out = amm.get_amount_out(
        amount_in, 
        amm.reserve0, 
        amm.reserve1
    )

    # Expected: (1000 * 0.997 * 200000) / (100000 + 1000 * 0.997)
    expected = 1.974
    assert abs(amount_out - expected) < 0.01

def test_spot_price():
    """Test spot price calculation"""
    amm = UniswapV2AMM(100000, 200000)
    price = amm.get_spot_price()
    assert price == 2.0

def test_swap_updates_reserves():
    """Test that swaps update reserves correctly"""
    amm = UniswapV2AMM(100000, 200000)
    initial_k = amm.k

    amount_out = amm.swap(1000, 'x_to_y')

    assert amm.reserve0 == 101000
    assert amount_out > 0
    # K should remain approximately constant (within fee tolerance)
    new_k = amm.reserve0 * amm.reserve1
    assert abs(new_k - initial_k) / initial_k < 0.01
