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
import re
import itertools
import pickle
# from algo_optimiser import MPTOptimiser

def generate_value_dict(data):
    variations = []
    count = 1
    value_dict = {}
    for i, optimiser in enumerate(data["optimiser"], start=1):
        optimiser_copy = optimiser.copy()
        
        args = optimiser_copy["args"]
        if args == {}:
            value_dict[optimiser["name"]] = {}
            continue
        list_bool = False
        for key, value in args.items():

            if optimiser["name"] not in value_dict.keys():
                    value_dict[optimiser["name"]] = {}
            if isinstance(value, list):                 
                value_dict[optimiser["name"]][key] = value
                list_bool = True
        if not list_bool:
            value_dict[optimiser["name"]][key] = [value]
                
    return value_dict

def get_all_combinations(value_dict):
    all_values_list = []
    optim_list = []
    args_list = []
    for optimiser_name, args in value_dict.items() :    
        for arg, values in args.items():
            optim_list.append([optimiser_name]*len(values))
            args_list.append([arg]*len(values))
            all_values_list.append(values)
    all_comb_values = list(itertools.product(*all_values_list))
    all_comb_optims = list(itertools.product(*optim_list))
    all_comb_args = list(itertools.product(*args_list))
    new_values_dict_list = []
    for i, value_comb in enumerate(all_comb_values):
        new_value_dict = copy.deepcopy(value_dict)
        for j, value in enumerate(value_comb):        
            new_value_dict[all_comb_optims[i][j]][all_comb_args[i][j]] = value
        new_values_dict_list.append(new_value_dict)
    return new_values_dict_list

def get_all_comb_variations(data):
    value_dict = generate_value_dict(data)
    new_values_dict_list = get_all_combinations(value_dict)
    optim_dict_list = []
    for arg_dict in new_values_dict_list:
        new_optim_dict = copy.deepcopy(data)
        for i, opt_args in enumerate(new_optim_dict["optimiser"]):
            opt_name = opt_args["name"]
            opt_args["args"].update(arg_dict[opt_name])
        optim_dict_list.append(new_optim_dict)
    return optim_dict_list

def iso8601_to_pandas_offset(duration):
    if isinstance(duration, pd.DateOffset):
        return duration
    # Regular expression pattern to match ISO 8601 duration format with only days, months, and years
    pattern = re.compile(r'^P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?$')
    
    # Match the duration string with the pattern
    match = pattern.match(duration)
    if match:
        # Extract years, months, and days from the match
        years = int(match.group('years') or 0)
        months = int(match.group('months') or 0)
        days = int(match.group('days') or 0)
        
        # Convert years, months, and days to pandas offset
        offset = pd.DateOffset(years=years, months=months, days=days)
        return offset
    else:
        raise ValueError("Invalid ISO 8601 duration format")

def handle_bounds(input_data):
    if isinstance(input_data, dict):
        return input_data
    if isinstance(input_data, tuple):
        if all(isinstance(item, tuple) for item in input_data):
            return input_data
    elif isinstance(input_data, list):
        if all(isinstance(item, tuple) for item in input_data):
            return tuple(input_data)
        elif all(isinstance(item, list) for item in input_data):
            return tuple(tuple(inner) for inner in input_data)
    return None

def handle_arguments(args):
    for key, value in args.items():
        if key == "lookback" or key == "lag":
            args[key] = iso8601_to_pandas_offset(value)
        if key == "bounds":
            args[key] = handle_bounds(value)
    return args

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
        if isinstance(strategy_dict["optimiser"], dict):
            all_optimisers = [strategy_dict["optimiser"]]
        elif isinstance(strategy_dict["optimiser"], list):
            all_optimisers = strategy_dict["optimiser"]
        else:
            raise TypeError("Invalid optimiser type")
        for optimiser in all_optimisers:
            optval = optimiser["name"]
            arguments = optimiser["args"]
            arguments = handle_arguments(arguments)
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
        strategy_dict = copy.deepcopy(recipe_dict[strategy_name])
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

def convert_optimisers_to_list(recipe):
    new_recipe = copy.deepcopy(recipe)
    
    for strategy, recipe_dict in recipe.items():    
        if "optimiser" in recipe_dict.keys():
            if isinstance(recipe_dict["optimiser"], dict):
                all_optimisers = [recipe_dict["optimiser"]]
            elif isinstance(recipe_dict["optimiser"], list):
                all_optimisers = recipe_dict["optimiser"]
            new_recipe["optimiser"] = all_optimisers
    return new_recipe

def handle_recipe_dict(recipe):
    new_recipe = {}    
    for strategy, recipe_dict in recipe.items():        
        opt_args_tracker = {}
        if "optimiser" in recipe_dict.keys():
            opt_details = copy.deepcopy(recipe_dict["optimiser"])
            if not isinstance(opt_details, list):
                opt_details = [opt_details]
            data = dict(optimiser = opt_details)
            all_comb_strategies = get_all_comb_variations(data)
            for i, optimiser_dict in enumerate(all_comb_strategies):
                new_strat_name = f"{strategy}.{i+1}" if len(all_comb_strategies) != 1 else strategy
                new_recipe[new_strat_name] = copy.deepcopy(recipe_dict)
                new_recipe[new_strat_name].update(optimiser_dict)
        else:
            new_recipe[strategy] = copy.deepcopy(recipe_dict)
    return new_recipe
    
def strategy_runner(data, recipe):
    recipe_dict = handle_recipe_dict(recipe)
    all_strategies = get_all_strategies(recipe_dict=recipe_dict)
    results = run_all_strategies(data, all_strategies)
    return results

def recipe_details_to_df(data):
    data_list = []
    for key, value in data.items():
        for optimiser in value["optimiser"]:
            temp_dict = {
                "Strategy_Name": key,
                "Rebalance_Frequency": value["rebalance_freq"],
                "Optimiser_Name": optimiser["name"],
                "Optimiser_arguments": json.dumps(optimiser["args"], indent = 4)
            }
            data_list.append(temp_dict)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data_list)
    return df


if __name__ == "__main__":
    # Load JSON recipe
    import btest_helpers as bth
    recipe = load_json_recipe("recipe.json")

    # recipe_dict = handle_recipe_dict(recipe)
    # all_strat = get_all_strategies(recipe_dict)
    pricedata = PriceData()
    chosen_assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"]
    bnds = ((0.1, 1), (0.05, 1), (0.05, 0.5), (0.05, 0.5), (0.1, 0.5), (0.05, 1))
    # pbtest = PortfolioBtest(pricedata, chosen_assets=chosen_assets, bounds=bnds)

    # df_shares_opt_all = pbtest.get_backtest_data(target_returns=0.1)

    # data = bt.get('spy,agg', start='2010-01-01')
    data = pricedata._dfraw[chosen_assets]
    res = strategy_runner(data=data, recipe=recipe)
    # with open(r"bt_results.pickle", "wb") as output_file:
        # pickle.dump(res, output_file)
    # # dfr = recipe_details_to_df(handle_recipe_dict(recipe))
    # res_loaded = pickle.load(open("bt_results.pickle", "rb"))
    trdict = bth.get_transactions_dfdict(res)
    # dfstats = bth.get_all_stats_df(res)
    # heatmap_dict = bth.get_returns_heatmaps(res)
    # Run strategies
    # "bounds": [[0.05,1], [0.05,1],[0.05,1],[0.05,1],[0.05,1],[0.05,1]],
    # new_recipe = handle_recipe_dict(recipe)
    b=2
