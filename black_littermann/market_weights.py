import yfinance as yf
import pandas as pd
import requests
import pandas as pd
import datetime
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage

def get_market_weights(tickers):
    """
    Given a list of stock tickers, return a DataFrame of their 
    market capitalizations and market-cap-based weights.
    
    Parameters
    ----------
    tickers : list of str
        List of stock tickers (e.g. ['AAPL', 'MSFT', 'GOOGL'])
    
    Returns
    -------
    pd.DataFrame
        Columns: ['Ticker', 'MarketCap', 'Weight']
        Sorted by descending market cap.
    """
    data = []
    
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            mcap = info.get("marketCap", None)
            if mcap is not None:
                data.append((t, mcap))
        except Exception as e:
            print(f"Warning: could not fetch data for {t}: {e}")

    if not data:
        raise ValueError("No valid market capitalization data retrieved.")

    df = pd.DataFrame(data, columns=["Ticker", "MarketCap"])
    df["Weight"] = df["MarketCap"] / df["MarketCap"].sum()
    df.sort_values("MarketCap", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df


def get_market_weights_fmp(tickers, apikey):
    """
    Given a list of stock tickers (matching the API’s format),
    fetch market capitalizations from FinancialModelingPrep,
    then compute normalized weights.
    """
    data = []
    for t in tickers:
        url = f"https://financialmodelingprep.com/stable/profile?symbol={t}&apikey={apikey}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Warning: API error for {t}: status {resp.status_code}")
            continue
        j = resp.json()
        if not j:
            print(f"Warning: empty data for {t}")
            continue
        # Example JSON: [ { "symbol": "AAPL", "price": ..., "mktCap": 2220000000000, ... } ]
        mcap = j[0].get("marketCap", None)
        if mcap is None:
            print(f"Warning: no mktCap for {t}")
            continue
        data.append((t, mcap))
    if not data:
        raise ValueError("No valid market cap data retrieved.")
    df = pd.DataFrame(data, columns=["Ticker", "MarketCap"])
    df["Weight"] = df["MarketCap"] / df["MarketCap"].sum()
    df.sort_values("MarketCap", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# Stocks history
# financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted?symbol=AAPL&from=2025-10-14&to=2025-10-22&apikey=T0QzKnHiapi0XOqY3yfxJX0vfANC9JsA

def get_stocks_history_fmp(ticker, from_date, to_date, apikey):
    """
    Fetch historical stock data from FinancialModelingPrep API.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL')
    from_date : str
        Start date in 'YYYY-MM-DD' format
    to_date : str
        End date in 'YYYY-MM-DD' format
    apikey : str
        API key for FinancialModelingPrep
    
    Returns
    -------
    pd.DataFrame
        DataFrame with historical stock data.
    """
    url = f"https://financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted?symbol={ticker}&from={from_date}&to={to_date}&apikey={apikey}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError(f"API error for {ticker}: status {resp.status_code}")
    j = resp.json()
    if not j:
        raise ValueError(f"No data returned for {ticker}")
    df = pd.DataFrame(j)
    return df

# Get 5 year history of a list of tickers
def get_multiple_stocks_history_fmp(tickers, apikey):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=5*365)).strftime('%Y-%m-%d')
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    all_data = {}
    for ticker in tickers:
        df = get_stocks_history_fmp(ticker, start_date, end_date, apikey)
        df.to_csv(f"{ticker}_5yr_history.csv", index=False)
        all_data[ticker] = df
    return all_data

def load_stocks_data_from_csv(filepath):
    dfall_history = pd.read_csv(filepath, index_col=0, parse_dates=True, date_format='%Y-%m-%d')
    return dfall_history

def load_market_weights_from_csv(filepath):
    weights_df = pd.read_csv(filepath)
    return weights_df


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    apikey = "T0QzKnHiapi0XOqY3yfxJX0vfANC9JsA"
    # weights_df = get_market_weights_fmp(tickers, apikey)
    df_history = get_stocks_history_fmp("SPGI", "2025-10-14", "2025-10-26", apikey)
    # all_data = get_multiple_stocks_history_fmp(tickers, apikey)
    
    # all_dates = pd.date_range(start=(datetime.datetime.now() - datetime.timedelta(days=5*365)).strftime('%Y-%m-%d'), end=datetime.datetime.now().strftime('%Y-%m-%d'))
    # dfall_history = pd.DataFrame(index=all_dates)
    # for ticker, df in all_data.items():
    #     df['date'] = pd.to_datetime(df['date'])
    #     df.set_index('date', inplace=True)
    #     dfall_history[ticker] = df['adjClose']


    # dfall_history.dropna(inplace=True)
    # dfall_history.to_csv("all_stocks_5yr_history.csv")
    # weights_df.to_csv("market_weights.csv", index=False)

    dfall_history = pd.read_csv("all_stocks_5yr_history.csv", index_col=0, parse_dates=True, date_format='%Y-%m-%d')
    weights_df = pd.read_csv("market_weights.csv")

    mu = mean_historical_return(dfall_history)
    S = CovarianceShrinkage(dfall_history).ledoit_wolf()
    print(weights_df)
