"""
This module provides functions for calculating the expected cost and variance of the cost of trading in the
Almgren-Chriss model.

Functions
----------
cost_expectation
    Calculate the expected cost of trading.
cost_variance
    Calculate the variance of the cost of trading.

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
epsilon : float
    Temporary impact intercept
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

from .decay_rate import kappa, tilde_tau


__all__ = ['cost_expectation', 'cost_variance']


def cost_expectation(lambda_: float, tau: float, sigma: float, gamma: float, eta: float, epsilon: float,
                     X: float, T: float) -> np.ndarray:
    r"""
    Compute the expected cost of trading in the Almgren-Chriss model.

    .. math:: E(X) = \frac{1}{2}\gamma X^2+\epsilon X+\tilde{\eta}X^2\frac{\tanh(\frac{1}{2}\kappa\tau)\big(\tau\sinh(2\kappa T) + 2T\sinh(\kappa\tau) \big)}{2\tau^2\sinh^2(\kappa T)}

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
        The expected cost of trading
    """
    kappa_ = kappa(lambda_, tau, sigma, gamma, eta)
    a = math.tanh(kappa_ * tau / 2) * (tau * math.sinh(2 * kappa_ * T) + 2 * T * math.sinh(kappa_ * tau))
    b = 2 * tau ** 2 * math.sinh(kappa_ * T) ** 2
    return ((gamma * X ** 2) / 2
            + epsilon * X
            + tilde_tau(lambda_, tau, sigma, gamma, eta) * X ** 2 * (a / b))


def cost_variance(lambda_: float, tau: float, sigma: float, gamma: float, eta: float,
                  X: float, T: float) -> np.ndarray:
    r"""
    Compute the variance of the cost of trading in the Almgren-Chriss model.

    .. math:: V(X) = \frac{1}{2}\sigma^2X^2\frac{\tau\sinh(\kappa T) \cosh(\kappa(T-\tau))-T\sinh(\kappa\tau)}{\sinh^2(\kappa T)\sinh(\kappa\tau)}

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
        The variance of the cost of trading
    """
    kappa_ = kappa(lambda_, tau, sigma, gamma, eta)
    a = tau * math.sinh(kappa_ * T) * math.cosh(kappa_ * (T - tau)) - T * math.sinh(kappa_ * tau)
    b = math.sinh(kappa_ * T) ** 2 * math.sinh(kappa_ * tau)
    return (sigma ** 2 * X ** 2 / 2) * (a / b)
