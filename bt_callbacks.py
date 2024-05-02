from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from allocation_layout import get_slider_card
import dash
from portfolio_plots import PortfolioPlot, plot_multiple_btest_pfolios
from data_fetch import PriceData
import numpy as np
import dash_bootstrap_components as dbc
from base_layout_components import generate_table
import btest_helpers as bth
import json
import json_recipe_handler as jrh
from base_layout_components import create_stats_container, get_recipe_table
import bt_components as btc
import pandas as pd

def get_bt_callbacks(app):

    @app.callback(
    [Output('recipe-store', 'data'), Output('recipe-validation-message', "children"), Output("recipe-table-placeholder", "children")],
    [Input('validate-recipe-button', 'n_clicks')],
    [State('json-recipe-input', 'value')]
    )
    def store_json(n_clicks, json_string):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "validate-recipe-button" in changed_id:            
            try:
                recipe = json.loads(json_string)            
                # print(recipe)
                recipe_dict = jrh.handle_recipe_dict(recipe)
                all_strat = jrh.get_all_strategies(recipe_dict)
                recipe_table = get_recipe_table(recipe_dict = recipe_dict)
                # print(recipe_dict)
                return [recipe, "", recipe_table]
            except Exception as e:
                return [{}, f"{type(e)} loading recipe: " + str(e), no_update]
        else:
            return [no_update, no_update, no_update]    
    
    @app.callback(
        [Output('bt-graph', 'figure'), Output("bt_stats", "data"), Output("bt-pivot-loading", "children"), Output("bt-metrics-store", "data"),
         Output("bt-plot-data", "data")],
        Input('bt-run-button', 'n_clicks'),
        Input('asset_dropdown_bt', 'value'),
        Input('recipe-store', 'data')
    )
    def plot_bt_results(n, asset_list, recipe):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "bt-run-button" in changed_id:
            if asset_list is None or not recipe:
                return [no_update, no_update, no_update, no_update, no_update]
            fig, datap, trdict, metrics_dict, dfstats = btc.load_bt_graph(asset_list=asset_list, recipe=recipe)
            trdata = pd.concat([df for key, df in trdict.items()], ignore_index=True)
            pivot_table = btc.get_pivot_table(trdict=trdict)
            return [fig, dfstats.to_dict("records"), pivot_table, metrics_dict, datap.to_dict("records")]
        else:
            return [no_update, no_update, no_update, no_update, no_update]


    @app.callback(
        Output("download-bt", "data"),
        [Input("btn-download-bt", "n_clicks"), Input("bt-plot-data", "data") ],
        prevent_initial_call=True,
    )
    def downloader(n_clicks, datap_dict):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "btn-download-bt" in changed_id:
            df = pd.DataFrame(datap_dict)
            return dcc.send_data_frame(df.to_csv, "figure_bt_raw.csv")
        else:
            return no_update

    @app.callback(
        [Output('bt-strategy-select', 'options'),
        Output('bt-strategy-select', 'value')],
        [Input("bt-metrics-store", "data")]
    )
    def update_dropdown(metrics_data):
        if not metrics_data:
            return [[], None]
        else:
            all_strategies = list(metrics_data["mreturns"].keys())
            return [all_strategies, all_strategies[0]]

    @app.callback(
        Output('bt-metric-loading', 'children'),
        [Input('metric-select', 'value'),
         Input('bt-strategy-select', 'value'),
        Input("bt-metrics-store", "data")]
    )
    def update_dropdown(metric, strategy, metrics_data):
        if not metrics_data:
            return no_update
        else:
            if metric == "Monthly Returns":
                mdata = metrics_data["mreturns"]
                figure = btc.get_heatmap(mdata, strategy)
            else:
                drawdowns = metrics_data["drawdowns"]
                figure = btc.get_drawdown_graph(drawdowns, strategy)
            return figure

    @app.callback(
        Output("collapse", "is_open"),
        [Input("collapse-button", "n_clicks")],
        [State("collapse", "is_open")],
        )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    return app