import numpy as np


def beta(asset_returns, market_returns):
    """
    Estimate beta of an asset relative to the market.

    Beta measures systematic risk: how much the asset moves
    relative to the market.

    Parameters:
    -----------
    asset_returns : array-like
        Return series of the asset
    market_returns : array-like
        Return series of the market index

    Returns:
    --------
    float
        Beta: Cov(r_i, r_m) / Var(r_m)
    """
    asset_returns = np.asarray(asset_returns)
    market_returns = np.asarray(market_returns)
    cov_matrix = np.cov(asset_returns, market_returns, ddof=1)
    return cov_matrix[0, 1] / cov_matrix[1, 1]


def capm_expected_return(risk_free_rate, asset_beta, market_return):
    """
    Calculate expected return of an asset under CAPM.

    CAPM: E[r_i] = r_f + beta_i * (E[r_m] - r_f)

    Parameters:
    -----------
    risk_free_rate : float
        Risk-free rate (e.g., 0.02 for 2%)
    asset_beta : float
        Beta of the asset
    market_return : float
        Expected market return

    Returns:
    --------
    float
        CAPM expected return
    """
    market_risk_premium = market_return - risk_free_rate
    return risk_free_rate + asset_beta * market_risk_premium
