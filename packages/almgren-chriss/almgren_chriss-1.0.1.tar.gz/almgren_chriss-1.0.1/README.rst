almgren-chriss
==============

This package provides functions for implementing the Almgren-Chriss model for optimal execution of portfolio transactions.

What is the Almgren-Chriss Model?
---------------------------------

The Almgren-Chriss model is a mathematical model used in financial markets to determine the optimal way to execute large
orders. The model takes into account various factors such as the risk tolerance of the trader, the volatility of the
market, and the impact of the trade on the market price. The goal of the model is to minimize the expected cost of the
trade while taking into account the risk of price fluctuations.

Functions in the Package
------------------------

The package provides the following functions:

- `cost_expectation`: Calculate the expected cost of trading.
- `cost_variance`: Calculate the variance of the cost of trading.
- `decay_rate`: Calculate the trade decay rate.
- `trade_trajectory`: Calculate the trading trajectory.
- `trade_list`: Calculate the list of trades.

Each function takes various parameters including risk tolerance, interval between trades, volatility, permanent impact
slope, temporary impact slope, total number of shares, and trading duration.

Example
-------

Here is an example of how to use the functions in the package:

.. code-block:: python

   from almgren_chriss import trade_trajectory, trade_list, cost_expectation, cost_variance


   lambda_ = 2e-6
   tau = 1
   sigma = 0.95
   gamma = 2.5e-7
   eta = 2.5e-6
   epsilon = 0.0625
   X = 1e06
   T = 5

>>> trade_trajectory(lambda_, tau, sigma, gamma, eta, X, T)
array([1000000.0, 428598.84574702, 182932.81426177, 76295.72161546, 27643.37739691, 0.0])

.. image:: assets/trade_trajectory.png

>>> trade_list(lambda_, tau, sigma, gamma, eta, X, T)
array([571401.15425298, 245666.03148525, 106637.09264631, 48652.34421856, 27643.37739691])

.. image:: assets/trade_list.png

>>> cost_expectation(lambda_, tau, sigma, gamma, eta, epsilon, X, T)
1140715.1670497851

>>> import math
>>> math.sqrt(cost_variance(lambda_, tau, sigma, gamma, eta, X, T))
449367.65254135116