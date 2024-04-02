import pandas as pd
import plotly.graph_objects as go
def get_weights_df(backtest):
    pos_df = backtest.data.copy()
    for col in pos_df.columns:
        pos_df[col] = backtest.strategy.children[col].__dict__["data"]["position"]*backtest.data[col]
    weights_df = pos_df.copy()
    dfall = pos_df.sum(axis=1)
    for col in weights_df.columns:
        weights_df[col] = pos_df[col]/dfall
    return weights_df

def get_holdings_df(backtest):
    pos_df = backtest.data.copy()
    for col in pos_df.columns:
        pos_df[col] = backtest.strategy.children[col].__dict__["data"]["position"]
    return pos_df

def get_transactions_dfdict(res):
    dfdict = {}
    for backtest in res.backtest_list:
        strat_name = backtest.strategy.name
        weights_df = backtest.__dict__["_sweights"]
        if weights_df is None:
            weights_df = get_weights_df(backtest)
        pos_df = get_holdings_df(backtest=backtest)
        dfw = pd.DataFrame(weights_df.stack().rename_axis(['Date', 'Security']))
        dfh = pd.DataFrame(pos_df.stack().rename_axis(['Date', 'Security']))
        dfw.columns = ["weights"]
        dfh.columns = ["Positions (With Notional 1e6)"]
        tr = backtest.strategy.get_transactions()
        dfp = backtest.strategy.prices.copy()
        
        dfp = dfp.reset_index().rename(columns={"index": "Date"})
        dfp.columns = ["Date", "pfolio_value"]
        dfc = tr.join(dfw).join(dfh).reset_index()
        dftrc = pd.merge(dfc,  dfp, on="Date")
        dftrc["asset_value"] = dftrc["weights"]*dftrc["pfolio_value"]
        dftrc = dftrc.set_index(["Date", "Security"]).drop(["quantity"], axis=1)
        dfdict[strat_name] = dftrc
    return dfdict


def plot_all_bt_results(res):
    fig = go.Figure()
    all_strategies = list(res.prices.columns)
    data = res.prices.reset_index().rename(columns = {"index": "Date"})
    for strategy in all_strategies:
       fig.add_trace(go.Scatter(x=data["Date"], y=data[strategy], mode='lines', name=strategy))
    fig.update_layout(
                        title= "Strategy performance",
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Value'),
                        showlegend=True
                    )
    return fig


def get_all_stats_df(res):
    prev_cols = list(res.stats.transpose().columns)
    dfstats = res.stats.transpose().reset_index()
    dfstats.columns = ["Investment"] + prev_cols
    return dfstats

def get_returns_heatmaps(res):
    heatmap_dict = {}
    for strategy in res.keys(): 
       data_df = res[strategy].__dict__["return_table"].round(2)
       heatmap_dict[strategy] = data_df
    return heatmap_dict 

