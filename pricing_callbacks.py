from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from allocation_layout import get_slider_card
import dash
from portfolio_plots import PortfolioPlot, plot_multiple_btest_pfolios
from data_fetch import PriceData
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from base_layout_components import generate_table
from alloc_components import data_load, plot_all_assets_raw_data
import json

def get_pricing_callbacks(app):

    @app.callback(
    Output("raw-data-graph", "figure"),
    [Input("raw_data_dropdown", "value"), Input("raw-data-store", "data")]
    )
    def update_raw_data(selected_assets, raw_data_dict):
        if selected_assets is None:
            return no_update
        all_assets_dict = {asset: pd.DataFrame(df) for asset, df in raw_data_dict.items()}
        fig, data_dict = plot_all_assets_raw_data(all_assets_dict=all_assets_dict, assets=selected_assets)
        return fig    

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
                assets_weights, fig, stat_table = data_load(selected_assets=selected_assets, assets_weights = assets_weights, show_assets_bool = show_assets_bool)
                return [assets_weights, fig, stat_table]
            else:
                return [no_update, no_update, no_update]
        else:
            return [no_update, no_update, no_update]
        
    return app