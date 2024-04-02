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

def get_all_callbacks(app):

    @app.callback(
    Output("slider_div", "children"),
    Input("asset_dropdown", "value")
    )
    def update_slider_div(selected_assets):
        if selected_assets is None or not selected_assets:
            return no_update
        sliders, values = get_slider_card(selected_assets)
        return sliders

    @app.callback(
        Output("weights-sum", "data"),  # Update the HTML div containing sliders
        Input({"type": "weight-slider", "index": ALL}, "value"),  # State to capture all slider values
    )
    def update_sliders(current_values):
        # Calculate the current sum of slider values
        # print(current_values)
        current_sum = sum(current_values)

        # # Calculate the adjustment factor
        # adjustment_factor = 100 / current_sum if current_sum != 0 else 0

        # # Adjust each slider value based on the factor
        # adjusted_values = [value * adjustment_factor for value in current_values]

        # # Update the sliders with the adjusted values
        # sliders = get_slider_card(selected_assets, adjusted_values)

        return current_sum

    @app.callback(
        Output("sum_value", "children"),
        Input("weights-sum", "data"),
    )
    def update_slider_div(current_sum):
        if not current_sum:
            return ""
        if abs(current_sum - 100) > 1e-4:
            return f"Total sum is not 100, readjust!"
        else:
            return ""
        
    @app.callback(
    [Output("store-assets-weights", "data"),Output("prices-graph", "figure"), Output("tab1-graphs-placeholder", "children")],  # Update the store data
    Input("update-wts-button", "n_clicks"),
    Input("show-assets-boolean", "on"),
    Input("asset_dropdown", "value"),  # Listen for changes in selected assets
    Input({"type": "weight-slider", "index": ALL}, "value")  # State to capture all slider values
    )
    def update_store_assets_weights(n, show_assets_bool, selected_assets, current_values):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "update-wts-button" in changed_id:
            # Combine selected assets and corresponding weights
            assets_weights = [{asset: weight/100} for asset, weight in zip(selected_assets, current_values)]
            if abs(sum(current_values) - 100) < 1e-4:
                pricedata = PriceData(asset_list=selected_assets)
                pplot = PortfolioPlot(pricedata_obj=pricedata)
                wt_dict = {k: v for d in assets_weights for k, v in d.items()}
                wt_arr = np.array([wt_dict[asset] for asset in selected_assets])
                fig, res = pplot.plot_value_data_df(plot_assets=show_assets_bool, weights=wt_arr)
                # Return the list of assets and weights to be stored
                print(assets_weights)
                prev_cols = list(res.stats.transpose().columns)
                dfstats = res.stats.transpose().reset_index()
                dfstats.columns = ["Investment"] + prev_cols
                show_cols = ["Investment", 'total_return', 'cagr', 'max_drawdown', 'calmar', "daily_mean", "daily_vol", "daily_sharpe"]
                columns_data_config = {"cagr": {'specifier': '.2%'}, "max_drawdown": {'specifier': '.2%'}, "daily_mean": {'specifier': '.2%'}, 
                                       "daily_vol": {'specifier': '.2%'}, "total_return": {'specifier': ',.2f'}, "calmar": {'specifier': ',.2f'},
                                        "daily_sharpe": {'specifier': ',.2f'}}
                stat_table = generate_table(dfstats, idname="price_stats", show_columns=show_cols, columns_data_config=columns_data_config)
                return [assets_weights, fig, stat_table]
            else:
                return [no_update, no_update, no_update]
        else:
            return [no_update, no_update, no_update]

    @app.callback(
    [Output('recipe-store', 'data'), Output('recipe-validation-message', "children"), Output("recipe-table-placeholder", "children")],
    [Input('validate-recipe-button', 'n_clicks')],
    [State('json-recipe-input', 'value')]
    )
    def store_json(n_clicks, json_string):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "validate-recipe-button" in changed_id:
            recipe = json.loads(json_string)            
            print(recipe)
            try:
                recipe_dict = jrh.handle_recipe_dict(recipe)
                all_strat = jrh.get_all_strategies(recipe_dict)
                recipe_table = get_recipe_table(recipe_dict = recipe_dict)
                print(recipe_dict)
                return [recipe, "", recipe_table]
            except Exception as e:
                return [{}, "Error loading recipe: " + str(e), no_update]
        else:
            return [{}, no_update, no_update]
    # @app.callback(
    #     Output('asset-bounds-container', 'children'),
    #     Input('add-button', 'n_clicks'),
    #     Input('asset-dropdown-bt-setting', 'value'),
    #     Input('asset-bounds-container', 'children')
    # )
    # def add_asset_bounds(n_clicks, selected_asset, existing_bounds):
    #     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
    #     if "add-button" in changed_id:
    #         if selected_asset is None:
    #             return no_update
    #         new_row =  [dbc.Row([
    #             dbc.Col(html.Label(f"Bounds for {selected_asset}")),
    #             dbc.Col(dcc.Input(
    #                 id={'type': 'min-input', 'asset': selected_asset},
    #                 type='number',
    #                 value = 0,
    #                 placeholder='Minimum Allocation'
    #             )),
    #             dbc.Col(dcc.Input(
    #                 id={'type': 'max-input', 'asset': selected_asset},
    #                 type='number',
    #                 value = 1,
    #                 placeholder='Maximum Allocation'
    #             )),
    #         ]), html.Br()]
    #         all_rows = existing_bounds + new_row
    #         return all_rows
    #     else:
    #         return no_update
        
    # @app.callback(
    # Output('bounds-store', 'data'),
    # Input('validate-button', 'n_clicks'),
    # Input("initial_investment", "value"),
    # Input("rebal_freq", "value"),
    # Input("cov_period", "value"),
    # Input("target_return", "value"),
    # State('asset-bounds-container', 'children'),
    # prevent_initial_call=True
    # )
    # def validate_bounds(n_clicks, initial_investment, rebal_freq, cov_period, target_return, asset_settings):
    #     bounds_dict = {}
    #     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
    #     if "validate-button" in changed_id:
    #         for row in asset_settings:
    #             try:
    #                 for setting in row.get("props").get("children"):
    #                     try:
    #                         typestr = setting.get("props").get("children").get("props").get("id").get("type")
    #                     except:
    #                         continue
    #                     if typestr == "min-input" or typestr == "max-input":
    #                         asset = setting["props"]["children"].get("props").get("id").get("asset")
    #                         if asset not in bounds_dict.keys():
    #                             bounds_dict[asset] = {}
    #                         bounds_dict[asset][typestr] = setting.get("props").get("children").get("props").get("value")
    #             except:
    #                 continue
    #         for asset in bounds_dict.keys(): 
    #             # Validate bounds
    #             try:
    #                 min_bound = float(bounds_dict[asset]["min-input"])
    #                 max_bound = float(bounds_dict[asset]["max-input"])
                    
    #                 if 0 <= min_bound <= 1 and 0 <= max_bound <= 1 and min_bound <= max_bound:
    #                     bounds_dict[asset] = (min_bound, max_bound)
    #                 else:
    #                     print(f"Invalid bounds for {asset}")
    #             except ValueError:
    #                 print(f"Invalid bounds for {asset}")

    #         print(bounds_dict)
    #         overall_settings = dict(initial_investment=initial_investment, rebal_freq=rebal_freq, cov_period=cov_period, target_return = target_return, bounds = bounds_dict)
    #         return overall_settings
    #     else:
    #         return {}
    
    
    @app.callback(
        [Output('bt-graph', 'figure'), Output("bt_stats_container", "children")],
        Input('bt-run-button', 'n_clicks'),
        Input('asset_dropdown_bt', 'value'),
        Input('recipe-store', 'data')
    )
    def plot_bt_results(n, asset_list, recipe):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #To determine if n_clicks is changed. 
        if "bt-run-button" in changed_id:
            if asset_list is None or not recipe:
                return [no_update, no_update]
            pricedata = PriceData(asset_list=asset_list)
            data = pricedata._dfraw
            res = jrh.strategy_runner(data, recipe)
            fig = bth.plot_all_bt_results(res)
            trdict = bth.get_transactions_dfdict(res)
            dfstats = bth.get_all_stats_df(res)
            heatmap_dict = bth.get_returns_heatmaps(res)
            try:
                statcontainer = create_stats_container(dfstats=dfstats, heatmap_dict=heatmap_dict, dftrc_dict = trdict, use_samples = False)
            except Exception as e:
                print(str(e))
                statcontainer = []
            return [fig, statcontainer]
        else:
            return [no_update, no_update]

    return app