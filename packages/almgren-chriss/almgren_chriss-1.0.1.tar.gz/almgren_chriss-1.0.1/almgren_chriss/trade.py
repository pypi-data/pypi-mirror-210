"""
This module provides functions for calculating the trading trajectory and list of trades in the Almgren-Chriss model.

Functions
---------
trade_trajectory
    Calculate the trading trajectory.
trade_list
    Calculate the list of trades.

Parameters
----------
lambda_ : float
    Risk tolerance (lambda)
tau : float
    Interval between trades
sigma : float
    Volatility
gamma : float
    Permanent impact slope
eta : float
    Temporary impact slope
X : float
    Total number of shares
T : float
    Trading duration

Returns
-------
numpy.ndarray
    The calculated values.
"""
import math

import numpy as np

from .decay_rate import kappa


__all__ = ['trade_trajectory', 'trade_list']


def trade_trajectory(lambda_: float, tau: float, sigma: float, gamma: float, eta: float,
                     X: float, T: float) -> np.ndarray:
    r"""
    Compute the trading trajectory in the Almgren-Chriss model.

    .. math:: x_j = \frac{\sinh(\kappa(T-t_j))}{\sinh(\kappa T)}X

    Parameters
    ----------
    lambda_ : float
        Risk tolerance
    tau : float
        Interval between trades
    sigma : float
        Volatility
    gamma : float
        Permanent impact slope
    eta : float
        Temporary impact slope
    X : float
        Total number of shares
    T : float
        Trading duration

    Returns
    -------
    np.ndarray
        The trading trajectory
    """
    t_j = np.arange(T / tau + 1) * tau
    kappa_ = kappa(lambda_, tau, sigma, gamma, eta)
    return (np.sinh((kappa_ * (T - t_j))) / math.sinh(kappa_ * T)) * X


def trade_list(lambda_: float, tau: float, sigma: float, gamma: float, eta: float,
               X: float, T: float) -> np.ndarray:
    r"""
    Compute the list of trades in the Almgren-Chriss model.

    .. math:: n_j = \frac{2\sinh(\frac{1}{2}\kappa\tau)}{\sinh(\kappa T)} \cosh\left(\kappa\left(T-t_{j-\frac{1}{2}} \right) \right)X

    Parameters
    ----------
    lambda_ : float
        Risk tolerance
    tau : float
        Interval between trades
    sigma : float
        Volatility
    gamma : float
        Permanent impact slope
    eta : float
        Temporary impact slope
    X : float
        Total number of shares
    T : float
        Trading duration

    Returns
    -------
    np.ndarray
        The list of trades
    """
    t_j = np.arange(1, T / tau + 1) * tau
    kappa_ = kappa(lambda_, tau, sigma, gamma, eta)
    return 2 * (math.sinh(kappa_ * tau / 2) / math.sinh(kappa_ * T)) * np.cosh(kappa_ * (T - (t_j - tau / 2))) * X
