import pandas as pd
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier

class MarketDataLoad:
    
    def __init__(self, history_filepath, weights_filepath, bmark_filepath, tickers=None):
        self.dfall_history = self.load_stocks_data_from_csv(history_filepath, tickers)
        self.bmark_history = self.load_bmark_history_from_csv(bmark_filepath)
        self.normalise_date_indexes()
        self.weights_df = self.load_market_weights_from_csv(weights_filepath)
        self.mu = self.get_mean_historical_return(self.dfall_history)
        self.S = self.get_covariance_matrix(self.dfall_history)
        
    @staticmethod
    def load_stocks_data_from_csv(filepath, tickers=None):
        dfall_history = pd.read_csv(filepath, index_col=0, parse_dates=True, date_format='%Y-%m-%d')
        if tickers:
            dfall_history = pd.DataFrame(dfall_history[tickers])
        return dfall_history

    @staticmethod
    def load_market_weights_from_csv(filepath):
        weights_df = pd.read_csv(filepath)
        weights_df = weights_df.set_index('Ticker')
        return weights_df
    
    @staticmethod
    def load_bmark_history_from_csv(filepath):
        bmark_history = pd.read_csv(filepath, index_col=0, parse_dates=True, date_format='%Y-%m-%d')
        return bmark_history
    
    @staticmethod
    def get_mean_historical_return(dfall_history):
        return mean_historical_return(dfall_history)

    @staticmethod
    def get_covariance_matrix(dfall_history):
        return CovarianceShrinkage(dfall_history).ledoit_wolf()    
    
    def normalise_date_indexes(self):
        common_dates = self.dfall_history.index.intersection(self.bmark_history.index)
        self.dfall_history = self.dfall_history.loc[common_dates]
        self.bmark_history = self.bmark_history.loc[common_dates]


class EfficientFrontierData:
    
    def __init__(self, mu, S, frontier_params: dict=None):
        self.mu = mu
        self.S = S
        self.frontier_params = frontier_params if frontier_params else {}
        
    def create_efficient_frontier(self):
        return EfficientFrontier(self.mu, self.S, **self.frontier_params)
    
    def optimize_portfolio(self, method='max_sharpe', **kwargs):
        ef = self.create_efficient_frontier()
        if method == 'max_sharpe':
            weights = ef.max_sharpe(**kwargs)
        elif method == 'min_volatility':
            weights = ef.min_volatility(**kwargs)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")
        return ef.clean_weights(), ef.portfolio_performance(verbose=True)  # returns cleaned weights and performance metrics
    

if __name__ == "__main__":
    history_filepath = "all_stocks_5yr_history.csv"
    weights_filepath = "market_weights.csv"
    bmark_filepath = "snp_historical.csv"

    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    market_data = MarketDataLoad(history_filepath, weights_filepath, bmark_filepath, tickers)
    
    ef_data = EfficientFrontierData(market_data.mu, market_data.S)
    clean_weights, performance = ef_data.optimize_portfolio(method='max_sharpe')
    
    print("Optimized Weights:", clean_weights)
    print("Portfolio Performance:", performance)