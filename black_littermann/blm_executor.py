import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pypfopt.black_litterman import BlackLittermanModel
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier
from market_data_load import MarketDataLoad

# tau, Sigma, pi, P, Q, Omega, posterior_returns, posterior_cov

def first_execute():
    history_filepath = "all_stocks_5yr_history.csv"
    weights_filepath = "market_weights.csv"
    bmark_filepath = "snp_historical.csv"
    
    market_data = MarketDataLoad(history_filepath, weights_filepath, bmark_filepath)
    cov_matrix = market_data.S
    # Sample P and Q for demonstration purposes
    P = np.array([[1, -1, 0, 0],    
                  [0, 1, -1, 0]])
    Q = np.array([0.05, 0.03])  # Views: Asset1 outperforms Asset2 by 5%, Asset2 outperforms Asset3 by 3%
    blm = BlackLittermanModel(cov_matrix,
        pi="market",
        absolute_views=None,
        Q=Q,
        P=P,
        market_caps=market_data.weights_df["MarketCap"]
    )
    # Get Omega from the model if needed    
    posterior_returns = blm.bl_returns()
    posterior_cov = blm.bl_cov()

    # Optimize portfolio based on posterior returns and covariance
    ef = EfficientFrontier(posterior_returns, posterior_cov, weight_bounds=(0.05, 0.4))
    # Add bounds or other constraints as needed
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=True)

    omega = blm.omega
    tau = blm.tau
    pi = blm.pi

    return cov_matrix, P, Q, omega, tau, pi, posterior_returns, posterior_cov, cleaned_weights, performance

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    cov_matrix, P, Q, omega, tau, pi, posterior_returns, posterior_cov, cleaned_weights, performance = first_execute()
    print("Optimized Weights:", cleaned_weights)