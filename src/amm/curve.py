"""Curve Finance StableSwap Implementation"""

from .base_amm import BaseAMM
import numpy as np

class CurveAMM(BaseAMM):
    """
    Curve StableSwap formula for low-slippage stablecoin swaps.

    Formula: A * n^n * sum(x_i) + D = A * D * n^n + D^(n+1) / (n^n * prod(x_i))
    """

    def __init__(self, reserves, amplification_coef=100, fee=0.0004, name="Curve"):
        super().__init__(name, fee)
        self.reserves = list(reserves)
        self.A = amplification_coef
        self.n = len(reserves)

    def get_D(self):
        """Calculate invariant D using Newton's method"""
        n = self.n
        S = sum(self.reserves)
        D = S
        Ann = self.A * (n ** n)

        for _ in range(255):
            D_P = D
            for reserve in self.reserves:
                D_P = D_P * D / (n * reserve)

            D_prev = D
            D = (Ann * S + D_P * n) * D / ((Ann - 1) * D + (n + 1) * D_P)

            if abs(D - D_prev) < 1:
                break

        return D

    def get_y(self, i, j, x):
        """
        Calculate output amount for token j given input x for token i.
        Solves the StableSwap invariant equation for y.
        """
        n = self.n
        D = self.get_D()
        Ann = self.A * (n ** n)
        c = D
        S_ = 0

        for k in range(n):
            if k == i:
                _x = x
            elif k == j:
                continue
            else:
                _x = self.reserves[k]
            S_ += _x
            c = c * D / (n * _x)

        c = c * D / (n * Ann)
        b = S_ + D / Ann
        y = D

        for _ in range(255):
            y_prev = y
            y = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) < 1:
                break

        return y

    def get_amount_out(self, amount_in, i=0, j=1):
        """Calculate output amount with fee"""
        x = self.reserves[i] + amount_in
        y = self.get_y(i, j, x)
        dy = self.reserves[j] - y
        return dy * (1 - self.fee)

    def get_spot_price(self):
        """Calculate spot price (reserve1 / reserve0)"""
        return self.reserves[1] / self.reserves[0]

    def swap(self, amount_in, direction):
        """Execute swap and update reserves"""
        if direction == 'x_to_y':
            amount_out = self.get_amount_out(amount_in, 0, 1)
            self.reserves[0] += amount_in
            self.reserves[1] -= amount_out
        else:
            amount_out = self.get_amount_out(amount_in, 1, 0)
            self.reserves[1] += amount_in
            self.reserves[0] -= amount_out

        return amount_out
