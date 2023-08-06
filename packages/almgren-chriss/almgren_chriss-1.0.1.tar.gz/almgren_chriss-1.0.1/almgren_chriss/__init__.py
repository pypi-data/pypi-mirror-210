"""
This package provides functions for implementing the Almgren-Chriss model for optimal execution of portfolio
transactions.

Modules
-------
cost
    Provides functions for calculating the expected cost and variance of the cost of trading.
decay_rate
    Provides functions for calculating the trade decay rate.
trade
    Provides functions for calculating the trading trajectory and the list of trades.

Functions
---------
cost_expectation
    Calculate the expected cost of trading.
cost_variance
    Calculate the variance of the cost of trading.
decay_rate
    Calculate the trade decay rate.
trade_trajectory
    Calculate the trading trajectory.
trade_list
    Calculate the list of trades.

Each function takes various parameters including risk tolerance, interval between trades, volatility, permanent impact
slope, temporary impact slope, total number of shares, and trading duration. Please refer to the individual function
documentation for more details on the parameters and return values.
"""
from .cost import cost_expectation, cost_variance
from .decay_rate import kappa as decay_rate
from .trade import trade_trajectory, trade_list
