import pandas as pd
import numpy as np
import os
import yfinance as yf


def merge_asset_data(asset_ticker, df_existing = None):
    period = "1y" if df_existing is not None else "10y"
    ticker = yf.Ticker(asset_ticker)
    df = ticker.history(period = period)
    df = df.reset_index()
    df["Date"] = df["Date"].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d"))
    if df_existing is not None:
        df_existing["Date"] = df_existing["Date"].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d"))
        dfall = pd.concat([df_existing, df], ignore_index = True)
        dfall = dfall.drop_duplicates("Date", ignore_index=True)
    else:
        dfall = df.copy()
    return dfall



