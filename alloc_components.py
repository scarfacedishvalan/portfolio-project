import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
from json_recipe_handler import load_json_recipe, handle_recipe_dict, recipe_details_to_df
from base_layout_components import get_recipe_table, get_stats_table, generate_table
from data_fetch import PriceData
import pandas as pd
import dash_pivottable
import plotly.express as px
import plotly.graph_objs as go
import dash_daq as daq
from portfolio_plots import PortfolioPlot, plot_multiple_btest_pfolios
from data_fetch import PriceData
import numpy as np
from read_from_gc import PriceDataGC

asset_dropdown_width = {"width": "100%"}
tooltip_styling={
        "always_visible": True,
        "placement": "bottom",
    }
prices_graph_style = {'height': '800px', 'border': '2px solid black'}
general_style = {
            'border': '2px solid black',  # Add a border
            'background-color': 'lightblue',  # Change background color to light blue,
            'padding': '20px'
        }
bt_dropdown_style = {"width": "100%"}
test_str = "ETF List: "
hr_style = {'borderWidth': "5vh", "width": "100%"}
SELECTED_ASSETS = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100"]


def get_slider_card(assetlist, values = None):
    slider_list = []
    if values is None:
        values = [100/len(assetlist)]*len(assetlist)
    for i, asset in enumerate(assetlist):
            header = html.H5(f"Allocation for {asset}", className="card-title")
            slider_list.append(header)
            sld =         dcc.Slider(
                id={"type": "weight-slider", "index": asset},
                # marks={i: f"{i}%" for i in range(0, 101, 10)},
                min=0,
                max=100,
                # step=5,
                value=values[i],
                included=False,
                tooltip=tooltip_styling
            )
            slider_list.append(sld)
    return slider_list, values

def data_load(selected_assets, assets_weights = None, show_assets_bool = False):
    if assets_weights is None:
        wt_arr = None
    else:
        wt_dict = {k: v for d in assets_weights for k, v in d.items()}
        wt_arr = np.array([wt_dict[asset] for asset in selected_assets])

    pricedata = PriceData(asset_list=selected_assets)
    pplot = PortfolioPlot(pricedata_obj=pricedata)
    fig, res = pplot.plot_value_data_df(plot_assets=show_assets_bool, weights=wt_arr)
    # Return the list of assets and weights to be stored
    # print(assets_weights)
    prev_cols = list(res.stats.transpose().columns)
    dfstats = res.stats.transpose().reset_index()
    dfstats.columns = ["Investment"] + prev_cols
    show_cols = ["Investment", 'total_return', 'cagr', 'max_drawdown', 'calmar', "daily_mean", "daily_vol", "daily_sharpe"]
    columns_data_config = {"cagr": {'specifier': '.2%'}, "max_drawdown": {'specifier': '.2%'}, "daily_mean": {'specifier': '.2%'}, 
                            "daily_vol": {'specifier': '.2%'}, "total_return": {'specifier': ',.2f'}, "calmar": {'specifier': ',.2f'},
                            "daily_sharpe": {'specifier': ',.2f'}}
    stat_table = generate_table(dfstats, idname="price_stats", show_columns=show_cols, columns_data_config=columns_data_config)
    
    return assets_weights, fig, stat_table

def plot_all_assets_raw_data(all_assets_dict = None, assets = None):
    fig = go.Figure()
    if all_assets_dict is None:
        all_assets_dict = PriceDataGC.read_all_raw_data()
    if assets is not None:
        all_assets_dict = {asset: df for asset, df in all_assets_dict.items() if asset in assets}
    data_dict = {}
    for asset, valuedata in all_assets_dict.items():
        # valuedata = df.reset_index()
        prev_cols = list(valuedata.columns)[1:]
        f = lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")    
        valuedata.columns = ["Date"] + prev_cols
        valuedata["Date"] = valuedata["Date"].apply(f)
        data_dict[asset] = valuedata.to_dict("records")
        fig.add_trace(go.Scatter(x=valuedata["Date"], y=valuedata["Close"], mode='lines', name=asset))
    fig.update_layout(
                        title= "Raw data: NIFTY ETF",
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Close Price'),
                        showlegend=True
                    )
    # fig.update_yaxes(type="log")
    return fig, data_dict


all_assets = list(PriceData()._dfraw.columns)
ticker_mapping_df = pd.read_csv('gs://price-data-etf/configs/ticker_mapping.csv')
name_dict = dict(zip(ticker_mapping_df["asset"].to_list(), ticker_mapping_df["name"].to_list()))
fig_raw, raw_data_dict = plot_all_assets_raw_data()

raw_data_dropdown = html.Div(children = [dcc.Dropdown(
    id="raw_data_dropdown",
    options=[{"label": name_dict[asset] + f" ({asset})", "value": asset} for asset in all_assets],
    value=SELECTED_ASSETS,  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
)], style=general_style)
asset_dropdown = html.Div(children = [dcc.Dropdown(
    id="asset_dropdown",
    options=[{"label": name_dict[asset] + f" ({asset})", "value": asset} for asset in all_assets],
    value=SELECTED_ASSETS,  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
)], style=general_style)

assets_weights, fig, stat_table = data_load(selected_assets=SELECTED_ASSETS)
update_section = html.Div(children = [
                 html.Br(),
                  dcc.Store(id="raw-data-store", data=raw_data_dict),
             dbc.Button("Update weights", id = "update-wts-button"),
             html.Br(),
             html.Div(id = "sum_value"),
             html.Br(),
            daq.BooleanSwitch(id="show-assets-boolean", on=False, color="red", label="Show Assets Data on Graph",),
            # html.Div(id = "sum_value"),
            html.Br(),
])
raw_graph = dcc.Loading(
                id="loading-raw",
                type="default",
                children=[
                    dcc.Graph(id="raw-data-graph", figure=fig_raw, style= prices_graph_style)
                ]
            )

pfolio_graph = dcc.Loading(
                id="loading-pfolio-alloc",
                type="default",
                children=[
                    dcc.Graph(id="prices-graph", figure=fig, style= prices_graph_style)
                ]
            )
slider_section  = [html.Br(), html.Div(id="slider_div", children=[assets_weights]), html.Br(), update_section]
stats_placeholder =  dcc.Loading(
                id="loading1b",
                type="default",
                children=[
                    html.Div(id = "tab1-graphs-placeholder", children = [stat_table])
                ]
            )

