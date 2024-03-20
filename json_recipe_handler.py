import bt
import pandas as pd
from algo_optimiser import MPTOptimiser
STRATEGY_NAME_MAP = {"MPTOptimiser": MPTOptimiser}
import copy
import bt
import importlib
import json
from data_fetch import PriceData
from portfolio_backtest import PortfolioBtest
from portfolio_optimizer import PortfolioOptimizer
# from algo_optimiser import MPTOptimiser

def expand_lists_in_dict(input_dict):
    result = [{}]
    for key, value in input_dict.items():
        if key == "bounds":
            continue
        if isinstance(value, list):
            new_result = []
            for item in value:
                for res in result:
                    new_res = res.copy()
                    new_res[key] = item
                    new_result.append(new_res)
            result = new_result
        else:
            for res in result:
                res[key] = value
    return result

def get_bt_function(key_name):
    if key_name in STRATEGY_NAME_MAP.keys():
        return STRATEGY_NAME_MAP[key_name]
    module_name = "bt.algos"
    try:
        module = importlib.import_module(module_name)
        return getattr(module, key_name)
    except AttributeError:
        return None
    except ImportError:
        return None
    

def create_strategy(strategy_dict):
    strategy_order = []
    if "rebalance_freq" in strategy_dict.keys():
        rebalance_func = get_bt_function(strategy_dict["rebalance_freq"])
        strategy_order.append(rebalance_func())
    if "select" in strategy_dict.keys():
        if strategy_dict["select"].lower() == "all":
            strategy_order.append(bt.algos.SelectAll())
        else:
            selection = strategy_dict["select"].split(",")
            strategy_order.append(bt.algos.SelectThese(selection))
    if "RunAfterDate" in strategy_dict.keys():
        strategy_order.append(bt.algos.RunAfterDate(strategy_dict["RunAfterDate"]))
    if "optimiser" in strategy_dict.keys():
        optval = strategy_dict["optimiser"]["name"]
        arguments = strategy_dict["optimiser"]["args"]
        optfunc = get_bt_function(optval)
        opt = optfunc(**arguments)
        strategy_order.append(opt)
    if "rebalance" in strategy_dict.keys():
        if strategy_dict["rebalance"]:        
            strategy_order.append(bt.algos.Rebalance())
    return strategy_order


def get_all_strategies(recipe_dict):
    all_strategies = {}
    for strategy_name in recipe_dict.keys():
        strategy_dict = recipe_dict[strategy_name]
        strategy_order = create_strategy(strategy_dict=strategy_dict)
        all_strategies[strategy_name] = bt.Strategy(strategy_name, strategy_order)
    return all_strategies

def run_all_strategies(data, all_strategies):
    btlist = []
    for strategy_name, strategy in all_strategies.items():
        test = bt.Backtest(strategy, data)
        btlist.append(test)
    results = bt.run(*btlist)
    return results

def load_json_recipe(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def handle_recipe_dict(recipe):
    new_recipe = {}
    for strategy, recipe_dict in recipe.items():
        if "optimiser" in recipe_dict.keys():
            input_dict = recipe_dict["optimiser"]["args"]
            input_dict_list = expand_lists_in_dict(input_dict)
            if len(input_dict_list) == 1:
                new_recipe[strategy] = recipe_dict
            else:
                for i, input in enumerate(input_dict_list):
                    new_strategy_name = strategy + f".{i+1}"
                    new_recipe[new_strategy_name] = copy.deepcopy(recipe[strategy])
                    new_recipe[new_strategy_name]["optimiser"]["args"] = copy.deepcopy(input)
        else:
            new_recipe[strategy] = recipe_dict
    return new_recipe
    
def strategy_runner(data, recipe):
    recipe_dict = handle_recipe_dict(recipe)
    all_strategies = get_all_strategies(recipe_dict=recipe_dict)
    results = run_all_strategies(data, all_strategies)
    return results


if __name__ == "__main__":
    # Load JSON recipe
    import btest_helpers as bth
    recipe = load_json_recipe("recipe.json")
    pricedata = PriceData()
    chosen_assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"]
    bnds = ((0.1, 1), (0.05, 1), (0.05, 0.5), (0.05, 0.5), (0.1, 0.5), (0.05, 1))
    # pbtest = PortfolioBtest(pricedata, chosen_assets=chosen_assets, bounds=bnds)

    # df_shares_opt_all = pbtest.get_backtest_data(target_returns=0.1)

    # data = bt.get('spy,agg', start='2010-01-01')
    data = pricedata._dfraw[chosen_assets]
    res = strategy_runner(data=data, recipe=recipe)
    # trdict = bth.get_transactions_dfdict(res)
    # dfstats = bth.get_all_stats_df(res)
    # heatmap_dict = bth.get_returns_heatmaps(res)
    # Run strategies
    # "bounds": [[0.05,1], [0.05,1],[0.05,1],[0.05,1],[0.05,1],[0.05,1]],
    # new_recipe = handle_recipe_dict(recipe)
    b=2
