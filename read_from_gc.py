import os
import pandas as pd
from source_etf_data import merge_asset_data
import time
import datetime

class PriceDataGC:
    folder = "data/price_data"
    ticker_mapping_path = f"data/ticker_mapping.csv"

    @classmethod
    def read_config(cls):
        df = pd.read_csv(cls.ticker_mapping_path)
        return df

    @classmethod
    def get_all_assets(cls):
        df = cls.read_config()
        return list(set(df["asset"].to_list()))
    
    @classmethod
    def read_all_raw_data(cls):
        dfmap = cls.read_config()
        all_df_dict = {}
        for idx, row in dfmap.iterrows():
            gs_path = os.path.join(cls.folder, row["ticker"].replace(".", "_") + ".csv")
            df = pd.read_csv(gs_path)
            asset = row["asset"]
            all_df_dict[asset] = df
        return all_df_dict
        
    @classmethod
    def read_all_data(cls, assets = None):        
        dfmap = cls.read_config()
        if assets:
            dfmap = dfmap.loc[dfmap["asset"].isin(assets)]
        all_df_dict = {}
        global_min_date = pd.to_datetime("2010-02-02")    
        global_max_date = pd.to_datetime("2050-02-02")            
        for idx, row in dfmap.iterrows():
            gs_path = os.path.join(cls.folder, row["ticker"].replace(".", "_") + ".csv")
            df = pd.read_csv(gs_path)
            min_date = min(pd.to_datetime(df["Date"]))
            max_date = max(pd.to_datetime(df["Date"]))
            if min_date > global_min_date:
                global_min_date = min_date
            if max_date < global_max_date:
                global_max_date = max_date
            asset = row["asset"]
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
            all_df_dict[asset] = df
        return all_df_dict, global_min_date.strftime("%Y-%m-%d"), global_max_date.strftime("%Y-%m-%d")
    

    @classmethod
    def get_combined_price_data(cls, assets = None):
        all_df_dict, global_min_date, global_max_date = cls.read_all_data(assets = assets)
        dr  = pd.date_range(start=global_min_date, end=global_max_date, freq="B")
        price_data = pd.DataFrame(index = pd.Series(dr, name="Date"))
        for asset, df in all_df_dict.items():
            dft = df[["Close"]]
            dft.columns = [asset]
            price_data = price_data.join(dft).fillna(method="ffill").fillna(method = "bfill")
        return price_data




if __name__ == "__main__":
    # credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    # all_assets = PriceDataGC.get_all_assets()
    # price_data = PriceDataGC.get_combined_price_data(assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"])
    # all_data_dict, _, _ = PriceDataGC.read_all_data(assets = ["NIFTYBEES"])
    # df_previous = all_data_dict["NIFTYBEES"]
    # PriceDataGC.update_gc_assets_data()
    all_raw = PriceDataGC.read_all_raw_data()
    a=2