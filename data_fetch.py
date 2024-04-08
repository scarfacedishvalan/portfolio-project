import pandas as pd
import xlwings as xw

import numpy as np
from numpy import *
import os
from numpy.linalg import multi_dot
import yfinance as yf
import plotly.graph_objects as go
from read_from_gc import PriceDataGC

RAW_PRICE_DATAPATH = "price_data.xlsx"
if os.path.exists(r"C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"):
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

class PriceData:
    def __init__(self, df = None, periods = 365, asset_list = None):
        self.asset_list = asset_list
        if df is None:
            self._data_src = RAW_PRICE_DATAPATH
            self._datecol = "Date"
            self._dfraw = self.read_prices()
        else:
            self._dfraw = df
        self._periods = periods
        self._returnsdf = self.get_returns()
        if asset_list:
            self._dfraw = pd.DataFrame(self._dfraw[asset_list])
            self._returnsdf = self.get_returns()
            
    def read_prices(self):
        # df = pd.read_excel(self._data_src)
        # df[self._datecol] = pd.to_datetime(df[self._datecol])
        # df = df.set_index(self._datecol)
        price_df = PriceDataGC.get_combined_price_data(assets=self.asset_list)
        return price_df

    def get_assets(self):
        return list(set(self._dfraw.columns))
    
    def get_returns(self):
        return self._dfraw.astype("float").pct_change(periods=int(self._periods)).fillna(0)
        
    def get_time_period(self):
        length = pd.to_datetime(list(self._dfraw.index)[-1])- pd.to_datetime(list(self._dfraw.index)[0])
        length = length.days/365
        return length
    
    def get_summary_returns(self):
        length = self.get_time_period()
        returns = np.log((self._dfraw.iloc[-1]/self._dfraw.iloc[0]).values)/length
        dflist = [dict(asset = asset, returns = returns) for asset, returns in zip(self.get_assets(), returns)]
        df = pd.DataFrame(dflist)
        df = df.sort_values("returns", ascending=False)
        return df
    
    # def get_asset_metrics(self):
    #     asset_dict = {}
    #     for asset in self._dfraw.columns:
            
    
if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    pricedata = PriceData(asset_list=["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"])
    # df = pricedata.get_summary_returns()
    a=2
