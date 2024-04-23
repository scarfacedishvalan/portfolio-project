from bt_components import load_bt_grpah
from json_recipe_handler import load_json_recipe, handle_recipe_dict, recipe_details_to_df
import constants as cts
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update

def get_bt_graph():
    recipe_json = load_json_recipe("recipe.json")
    recipe = handle_recipe_dict(recipe_json)
    asset_list = cts.SELECTED_ASSETS
    figbt, trdict, metrics_dict, dfstats = load_bt_grpah(asset_list=asset_list, recipe=recipe, cache=True)
    graph =  dcc.Graph(id="bt-graph", figure = figbt)
    return graph