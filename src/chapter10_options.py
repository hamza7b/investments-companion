import numpy as np
from scipy.stats import norm


def _d1(S, K, T, r, sigma):
    """
    Calculate d1 term used in the Black-Scholes formula.

    d1 = [ln(S/K) + (r + sigma^2/2) * T] / (sigma * sqrt(T))
    """
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def _d2(S, K, T, r, sigma):
    """
    Calculate d2 term used in the Black-Scholes formula.

    d2 = d1 - sigma * sqrt(T)
    """
    return _d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


def black_scholes_call(S, K, T, r, sigma):
    """
    Price a European call option using the Black-Scholes formula.

    C = S * N(d1) - K * e^(-rT) * N(d2)

    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annualized, e.g., 0.05 for 5%)
    sigma : float
        Volatility of the underlying asset (annualized, e.g., 0.20 for 20%)

    Returns:
    --------
    float
        Call option price
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def black_scholes_put(S, K, T, r, sigma):
    """
    Price a European put option using the Black-Scholes formula.

    P = K * e^(-rT) * N(-d2) - S * N(-d1)

    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annualized, e.g., 0.05 for 5%)
    sigma : float
        Volatility of the underlying asset (annualized, e.g., 0.20 for 20%)

    Returns:
    --------
    float
        Put option price
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
