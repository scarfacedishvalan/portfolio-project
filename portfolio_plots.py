from portfolio_optimizer import PortfolioOptimizer
from data_fetch import PriceData
import plotly.graph_objects as go
from portfolio_backtest import PortfolioBtest
import numpy as np
import bt

class PortfolioPlot:
    def __init__(self, pricedata_obj=None, **kwargs):
        if pricedata_obj is None:
            pricedata_obj = PriceData()
        self.pricedata_obj = pricedata_obj
        self.portoptim_obj = PortfolioOptimizer(pricedata_obj)
        self.pbtest_obj = PortfolioBtest(pricedata_obj, **kwargs)
    
    def plot_all_assets(self, fig=None, title = "Assets Data Over Time"):
        price_data = self.pricedata_obj._dfraw
        if fig is None:
            fig = go.Figure()
        dates = list(price_data.index)
        for asset in price_data.columns:
            fig.add_trace(go.Scatter(x=dates, y=price_data[asset].to_list(), mode='lines', name=asset))
        fig.update_layout(
                            title= title,
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Value'),
                            showlegend=True
                        )
        return fig

    def plot_value_data_df(self, fig=None, title = "Value data over time", plot_assets = True, weights=None):
        res = self.pbtest_obj.get_buy_and_hold_results(weights=weights)
        asset_cols = list(res.prices.columns)[1:]
        # value_data_df = self.pbtest_obj.get_value_data_df()
        # prev_cols = list(value_data_df.columns)
        # value_data_df = value_data_df.reset_index()
        # value_data_df.columns = ["Date"] + prev_cols
        if fig is None:
            fig = go.Figure()
        if weights is None:
            numofasset = len(asset_cols)
            weights = np.array(numofasset*[1./numofasset])
        portfolio_value_dr = res.prices.iloc[:, [0]].reset_index()
        portfolio_value_dr.columns = ["Date", "Value"] 
        fig.add_trace(go.Scatter(x=portfolio_value_dr["Date"], y=portfolio_value_dr["Value"], mode='lines', name="Initially weighted Portfolio Value"))
        # portfolio_value_ir = self.portoptim_obj.get_prices_evolution(weights=weights).sum(axis = 1)
        # fig.add_trace(go.Scatter(x=dates, y=portfolio_value_ir.values, mode='lines', name="Initially weighted Portfolio Value"))
        if plot_assets:
            valuedata = res.prices.reset_index()
            prev_cols = list(valuedata.columns)[1:]
            valuedata.columns = ["Date"] + prev_cols
            for asset in asset_cols:
                fig.add_trace(go.Scatter(x=valuedata["Date"], y=valuedata[asset], mode='lines', name=asset))
        fig.update_layout(
                            title= title,
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Value'),
                            showlegend=True
                        )
        return fig, res
    
    def plot_backtested_portfolio(self, target_returns, optimiser_func = "sr", plot_assets=False, fig=None):
        df_btest = self.pbtest_obj.get_backtest_data(target_returns=target_returns, optimiser_func = optimiser_func)
        if fig is None:
            fig = go.Figure()
        dates = list(df_btest.index)
        lookback = str(int(self.pbtest_obj.cov_period/365)) + "y"
        rebalance = str(int(self.pbtest_obj.rebalance_frequency)) + "rb"
        tag = f"bt_{optimiser_func}_{str(np.round(target_returns, 2))}_{lookback}_{rebalance}"
        fig.add_trace(go.Scatter(x=dates, y=df_btest["pfolio_value"].values, mode='lines', name=tag))
        # portfolio_value_ir = self.portoptim_obj.get_prices_evolution(weights=weights).sum(axis = 1)
        # fig.add_trace(go.Scatter(x=dates, y=portfolio_value_ir.values, mode='lines', name="Initially weighted Portfolio Value"))
        if plot_assets:
            asset_cols = self.pricedata_obj._dfraw.columns
            for asset in asset_cols:
                fig.add_trace(go.Scatter(x=dates, y=df_btest[asset].to_list(), mode='lines', name=asset))
        
        fig.update_layout(title = "Backtested portfolio with rebalancing",
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Value'),
                            showlegend=True,
                               legend=dict(
                            font=dict(
                                family="Arial",
                                size=18,
                                color="black"
                            ))
                        )
        return fig
def handle_arguments(arg):
    argstr = str(arg)
    return [float(arg1) for arg1 in argstr.split("_")] 

def plot_multiple_btest_pfolios(asset_list, init_amounts, target_returns, cov_periods, bounds = None, rebal_freq = 365, returns_period=None):
    init_amounts_list = handle_arguments(init_amounts)
    target_returns_list = handle_arguments(target_returns)
    cov_periods_list  = handle_arguments(cov_periods)
    rebal_freq_list = handle_arguments(rebal_freq)
    
    fig = None
    for init_amount in init_amounts_list:
        for rebal_freq in rebal_freq_list:
            for target_return in target_returns_list:
                for cov_period in cov_periods_list:
                    if returns_period is None:
                        returns_period = rebal_freq
                    pricedata = PriceData(periods = returns_period)
                    pplot = PortfolioPlot(pricedata_obj=pricedata, chosen_assets = asset_list, rebal_freq = rebal_freq, cov_period = cov_period, bounds=bounds, initial_investment=init_amount)
                    fig = pplot.plot_backtested_portfolio(target_returns= target_return, optimiser_func = "sr", plot_assets=False, fig=fig)
    return fig

if __name__ == "__main__":
    weights = np.array([1/6,	0,	1/6,	0,	0,	0,	1/6,	1/6,	1/6,	1/6, 0, 0])
    pplot = PortfolioPlot()
    fig = pplot.plot_value_data_df(weights=weights)
    b=2