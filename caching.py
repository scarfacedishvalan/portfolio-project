from google.cloud import storage
import os
import pandas as pd
from source_etf_data import merge_asset_data
import time
import datetime
from json_recipe_handler import load_json_recipe, handle_recipe_dict, recipe_details_to_df
import constants as cts
import btest_helpers as bth
import json
import json_recipe_handler as jrh
from data_fetch import PriceData

class CachingBTGC():
    project_name = "stone-goal-401904"
    bucket_name = "price-data-etf"
    bt_cache_path = "configs/all_bt_cache.json"
    selected_assets = cts.SELECTED_ASSETS

    @staticmethod
    def convert_datetime(timeseries_df, colname = "Date"):
        f = lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
        timeseries_df[colname] = timeseries_df[colname].apply(f)
        return timeseries_df
    
    @classmethod
    def generate_overall_dict(cls):
        recipe_json = load_json_recipe("recipe.json")
        recipe = handle_recipe_dict(recipe_json)
        asset_list = cls.selected_assets
        pricedata = PriceData(asset_list=asset_list)
        data = pricedata._dfraw
        res = jrh.strategy_runner(data, recipe)
        fig = bth.plot_all_bt_results(res)
        trdict = bth.get_transactions_dfdict(res)
        heatmap_dict = bth.get_returns_heatmaps(res)
        drawdown_dict = bth.get_drawdown_dict(res)
        dfstats = bth.get_all_stats_df(res)
        dfstats = cls.convert_datetime(dfstats, colname="start")
        dfstats = cls.convert_datetime(dfstats, colname="end")
        trdata = {key: cls.convert_datetime(df).to_dict("records") for key, df in trdict.items()}
        data_plot = res.prices.reset_index().rename(columns = {"index": "Date"})
        data_plot = cls.convert_datetime(data_plot)
        metrics_dict = {"mreturns": heatmap_dict, "drawdowns": drawdown_dict}
        overall_dict = {}
        overall_dict["data_plot"] = data_plot.to_dict("records")
        overall_dict["transactions"] = trdata
        overall_dict["metrics_dict"] = metrics_dict
        overall_dict["dfstats"] = dfstats.to_dict("records")
        return overall_dict
    
    @classmethod
    def dump_to_json(cls, path = None):
        data = cls.generate_overall_dict()
        storage_client = storage.Client()
        ## instance of a bucket in your google cloud storage
        bucket = storage_client.get_bucket(cls.bucket_name)
        
        ## if you want to create a new file 
        blob = bucket.blob(cls.bt_cache_path)

        ## uploading data using upload_from_string method
        ## json.dumps() serializes a dictionary object as string
        blob.upload_from_string(json.dumps(data))

    @classmethod
    def read_from_cloud(cls, path = None):
        storage_client = storage.Client()
        ## instance of a bucket in your google cloud storage
        bucket = storage_client.get_bucket(cls.bucket_name)
        
        ## if you want to create a new file 
        blob = bucket.blob(cls.bt_cache_path)

        ## uploading data using upload_from_string method
        ## json.dumps() serializes a dictionary object as string
        data = json.loads(blob.download_as_string())
        return data


if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    CachingBTGC.dump_to_json()
    data = CachingBTGC.read_from_cloud()
    a=2