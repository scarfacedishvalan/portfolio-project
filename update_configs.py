from google.cloud import storage
import os
import pandas as pd
from read_from_gc import PriceDataGC

class ConfigGC:
    project_name = "stone-goal-401904"
    bucket_name = "price-data-etf"
    folder = "configs"

    @classmethod
    def get_config_yf(cls):
        df_config = pd.DataFrame(columns = ["asset","source","ticker", "path"])
        all_assets = PriceDataGC.get_all_assets()
        all_asset_paths = PriceDataGC.get_all_assets(path=True)
        all_tickers = [ticker + ".NS" for ticker in all_assets]
        df_config["asset"] = all_assets
        df_config["ticker"] = all_tickers
        df_config["path"] = all_asset_paths
        df_config["source"] = "yfinance"
        return df_config
    
    @classmethod
    def update_to_gc(cls):
        gs_path = f"gs://{cls.bucket_name}/{cls.folder}/ticker_mapping.csv"
        df_config = cls.get_config_yf()
        df_config.to_csv(gs_path, index=False)
        print("Ticker mapping config updated!")
    
if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    # df_config = ConfigGC.get_config_yf()
    # df_config.to_csv("")
    ConfigGC.update_to_gc()
    A=2

