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
    local_cache_path = "data/all_bt_cache.json"  # Local path for caching
    selected_assets = cts.SELECTED_ASSETS

    @staticmethod
    def convert_datetime(timeseries_df, colname="Date"):
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
        print("Strategy Runs Complete")
        fig, data = bth.plot_all_bt_results(res)
        trdict = bth.get_transactions_dfdict(res)
        print("Transactions dict complete")
        heatmap_dict = bth.get_returns_heatmaps(res)
        drawdown_dict = bth.get_drawdown_dict(res)
        dfstats = bth.get_all_stats_df(res)
        dfstats = cls.convert_datetime(dfstats, colname="start")
        dfstats = cls.convert_datetime(dfstats, colname="end")
        trdata = {key: cls.convert_datetime(df).to_dict("records") for key, df in trdict.items()}
        data_plot = res.prices.reset_index().rename(columns={"index": "Date"})
        data_plot = cls.convert_datetime(data_plot)
        metrics_dict = {"mreturns": heatmap_dict, "drawdowns": drawdown_dict}
        overall_dict = {
            "data_plot": data_plot.to_dict("records"),
            "transactions": trdata,
            "metrics_dict": metrics_dict,
            "dfstats": dfstats.to_dict("records"),
        }
        print("Overall dict generated")
        return overall_dict

    @classmethod
    def dump_to_json(cls):
        data = cls.generate_overall_dict()

        # Save to local path
        with open(cls.local_cache_path, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def read_from_local(cls, path=None):
        if path is None:
            path = cls.local_cache_path
        with open(path, "r") as f:
            data = json.load(f)
        return data


if __name__ == "__main__":
    CachingBTGC().read_from_local()
    a=2