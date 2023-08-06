"""
This module provides functions for calculating the trade decay rate in the Almgren-Chriss model.

Functions
---------
tilde_kappa_squared
    Calculate the square of the adjusted trade decay rate.
tilde_tau
    Calculate the adjusted interval between trades.
kappa
    Calculate the trade decay rate.

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

Returns
-------
float
    The calculated value.
"""
import math


__all__ = ['tilde_kappa_squared', 'tilde_tau', 'kappa']


def tilde_kappa_squared(lambda_: float, tau: float, sigma: float, gamma: float, eta: float) -> float:
    r"""
    Compute the square of the adjusted trade decay rate in the Almgren-Chriss model.

    .. math:: \tilde{\kappa}^2 = \frac{\lambda \sigma^2}{\eta \left( 1 - \frac{\gamma \tau}{2 \eta} \right)}

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

    Returns
    -------
    float
        The square of the adjusted trade decay rate
    """
    return (lambda_ * sigma ** 2) / (eta * (1 - (gamma * tau) / (2 * eta)))


def tilde_tau(lambda_: float, tau: float, sigma: float, gamma: float, eta: float) -> float:
    r"""
    Compute the adjusted interval between trades in the Almgren-Chriss model.

    .. math:: \tilde{\eta} = \frac{\lambda \sigma^2}{\tilde{\kappa}^2}

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

    Returns
    -------
    float
        The adjusted interval between trades
    """
    return (lambda_ * sigma ** 2) / tilde_kappa_squared(lambda_, tau, sigma, gamma, eta)


def kappa(lambda_: float, tau: float, sigma: float, gamma: float, eta: float) -> float:
    r"""
    Compute the trade decay rate in the Almgren-Chriss model.

    .. math:: \kappa = \frac{\cosh^{-1}\left( \frac{\tau^2}{2} \tilde{\kappa}^2 + 1 \right)}{\tau}

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

    Returns
    -------
    float
        The trade decay rate
    """
    return math.acosh((tau ** 2 / 2) * tilde_kappa_squared(lambda_, tau, sigma, gamma, eta) + 1) / tau
