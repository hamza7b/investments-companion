import numpy as np


def portfolio_return(weights, expected_returns):
    """
    Calculate expected return of a portfolio.

    Parameters:
    -----------
    weights : array-like
        Asset weights (must sum to 1)
    expected_returns : array-like
        Expected return of each asset

    Returns:
    --------
    float
        Portfolio expected return: sum(w_i * mu_i)
    """
    weights = np.asarray(weights)
    expected_returns = np.asarray(expected_returns)
    return np.dot(weights, expected_returns)


def portfolio_variance(weights, cov_matrix):
    """
    Calculate portfolio variance using the quadratic form w^T * Sigma * w.

    Parameters:
    -----------
    weights : array-like
        Asset weights (must sum to 1)
    cov_matrix : array-like
        Covariance matrix of asset returns (n x n)

    Returns:
    --------
    float
        Portfolio variance
    """
    weights = np.asarray(weights)
    cov_matrix = np.asarray(cov_matrix)
    return weights @ cov_matrix @ weights


def covariance_matrix(returns_matrix):
    """
    Calculate the covariance matrix from a matrix of asset returns.

    Parameters:
    -----------
    returns_matrix : array-like
        Matrix of returns with shape (n_assets, n_periods)

    Returns:
    --------
    ndarray
        Covariance matrix of shape (n_assets, n_assets)
    """
    returns_matrix = np.asarray(returns_matrix)
    return np.cov(returns_matrix, ddof=1)
