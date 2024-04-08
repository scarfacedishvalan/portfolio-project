from google.cloud import storage
import os
import pandas as pd
from source_etf_data import merge_asset_data
import time
import datetime

class PriceDataGC:
    project_name = "stone-goal-401904"
    bucket_name = "price-data-etf"
    folder = "price-data"
    ticker_mapping_path = f"gs://{bucket_name}/configs/ticker_mapping.csv"

    @classmethod
    def get_all_assets(cls, path=False):
        storage_client = storage.Client(project=cls.project_name)
        bucket = storage_client.get_bucket(cls.bucket_name)
        blobs = bucket.list_blobs()
        all_names = []        
        for blob in list(blobs):
            if cls.folder in blob.name:
                if path:
                    asset_name = blob.name
                else:
                    asset_name = blob.name.replace(cls.folder + "/", "").replace(".csv", "").replace("_NS", "")
                all_names.append(asset_name)
        return all_names
    
    @classmethod
    def read_all_data(cls, assets = None):
        all_paths = cls.get_all_assets(path=True)
        if assets:
            all_paths = [path for path in all_paths if any([asset in path for asset in assets])]
        all_df_dict = {}
        global_min_date = pd.to_datetime("2010-02-02")    
        global_max_date = pd.to_datetime("2050-02-02")            
        for path in all_paths:
            gs_path = f"gs://{cls.bucket_name}/{path}"
            df = pd.read_csv(gs_path)
            min_date = min(pd.to_datetime(df["Date"]))
            max_date = max(pd.to_datetime(df["Date"]))
            if min_date > global_min_date:
                global_min_date = min_date
            if max_date < global_max_date:
                global_max_date = max_date
            asset = path.replace(cls.folder + "/", "").replace(".csv", "").replace("_NS", "")
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

    @classmethod
    def update_gc_assets_data(cls, assets = None, log_local = False):
        all_df_dict, _, _ = cls.read_all_data(assets=assets)
        ticker_mapping_df = pd.read_csv(cls.ticker_mapping_path)
        ticker_mapping_df = ticker_mapping_df.set_index("asset")
        if log_local:
            f = open(r"C:\Python\data\logger_update_gc.txt" , "w")
            f.write("Logging at: " + str(datetime.datetime.now()) + "\n")

        for asset, df in all_df_dict.items():
            path = ticker_mapping_df["path"][asset]
            ticker = ticker_mapping_df["ticker"][asset]
            df_merged = merge_asset_data(asset_ticker=ticker, df_existing=df.reset_index()) 
            gs_path = f"gs://{cls.bucket_name}/{path}"           
            df_merged.to_csv(gs_path, index=False)
            print(f"Done for {asset}")
            if log_local:
                f.write(f"Done for {asset} \n")
        if log_local:
            f.close()
        
if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    all_assets = PriceDataGC.get_all_assets()
    # price_data = PriceDataGC.get_combined_price_data(assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"])
    # all_data_dict, _, _ = PriceDataGC.read_all_data(assets = ["NIFTYBEES"])
    # df_previous = all_data_dict["NIFTYBEES"]
    PriceDataGC.update_gc_assets_data()
    a=2