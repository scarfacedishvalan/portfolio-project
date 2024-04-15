import pandas as pd
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay

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
        dftrc = dftrc.drop(["quantity"], axis=1)
        dftrc["strategy"] = strat_name
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
    dfstats.columns = ["Strategy"] + prev_cols
    return dfstats

def convert_to_timeseries(df):
    # Create an empty list to store data for each day
    daily_data = []

    # Iterate over each row in the original dataframe
    for _, row in df.iterrows():
        # Extract drawdown period start and end dates
        start_date = row['Start']
        end_date = row['End']
        
        # Create a date range for the drawdown period
        date_range = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # For each date in the drawdown period, add a tuple of (date, drawdown value) to the list
        for date in date_range:
            daily_data.append((date, row['drawdown']))
    
    # Convert the list of tuples to a dataframe
    timeseries_df = pd.DataFrame(daily_data, columns=['Date', 'drawdown'])
    
    # Set the date column as the index
    timeseries_df.set_index('Date', inplace=True)
    
    # Fill missing values with 0
    start_date = timeseries_df.index.min()-  BDay(1)
    end_date = timeseries_df.index.max() +  BDay(1)
    timeseries_df = timeseries_df.reindex(pd.date_range(start=start_date , end= end_date, freq='B'), fill_value=0)
    f = lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
    timeseries_df = timeseries_df.reset_index()
    timeseries_df.columns = ["Date", "drawdown"]
    timeseries_df["Date"] = timeseries_df["Date"].apply(f)
    return timeseries_df

def get_returns_heatmaps(res):
    heatmap_dict = {}
    for strategy in res.keys(): 
       data_df = res[strategy].__dict__["return_table"].round(2)
       data_df = data_df.reset_index().rename(columns = {"index": "Date"})
       heatmap_dict[strategy] = data_df.to_dict("records")
    return heatmap_dict 

def get_drawdown_dict(res):
    drawdown_dict = {}
    for strategy in res.keys(): 
       data_df = res[strategy].__dict__["drawdown_details"].round(2)
       f = lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
       data_df["Start"] = data_df["Start"].apply(f)
       data_df["End"] = data_df["End"].apply(f)
       drawdown_ts = convert_to_timeseries(data_df)
       drawdown_dict[strategy] = drawdown_ts.to_dict("records")
    return drawdown_dict
