import numpy as np


def simple_return(prices):
    """
    Calculate simple returns from a price series.
    
    Parameters:
    -----------
    prices : array-like
        Price series (1D array or list)
    
    Returns:
    --------
    returns : ndarray
        Simple returns: (P_t - P_{t-1}) / P_{t-1}
    """
    prices = np.asarray(prices)
    return (prices[1:] / prices[:-1]) - 1

# Alternative return measyure: log returns, 
# which are often used in finance for their properties (e.g., time-additivity).
def log_return(prices):
    """
    Calculate log returns from a price series.
    
    Parameters:
    -----------
    prices : array-like
        Price series (1D array or list)
    
    Returns:
    --------
    returns : ndarray
        Log returns: ln(P_t / P_{t-1})
    """
    prices = np.asarray(prices)
    return np.log(prices[1:] / prices[:-1])


def expected_return(returns):
    """
    Calculate expected return (mean return).
    
    Parameters:
    -----------
    returns : array-like
        Series of returns
    
    Returns:
    --------
    expected_return : float
        Mean return
    """
    return np.mean(returns)


def volatility(returns):
    """
    Calculate volatility (standard deviation of returns).
    
    Parameters:
    -----------
    returns : array-like
        Series of returns
    
    Returns:
    --------
    volatility : float
        Standard deviation of returns
    """
    return np.std(returns, ddof=1)

