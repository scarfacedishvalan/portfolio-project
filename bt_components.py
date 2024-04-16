import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
from json_recipe_handler import load_json_recipe, handle_recipe_dict, recipe_details_to_df
from base_layout_components import get_recipe_table,  generate_table
from data_fetch import PriceData
import pandas as pd
import dash_pivottable
import plotly.express as px
import plotly.graph_objs as go
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
import random
import constants as cts
from caching import CachingBTGC

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
recipe_json = load_json_recipe("recipe.json")
json_str = json.dumps(recipe_json, indent=4)
TABLE_SETTINGS_DICT = {"stats_table": dict (   
    show_cols = ["Strategy", 'total_return', 'cagr', 'max_drawdown', 'calmar', "yearly_mean", "yearly_vol", "yearly_sharpe"],
    columns_data_config = {"cagr": {'specifier': '.2%'}, "max_drawdown": {'specifier': '.2%'}, "daily_mean": {'specifier': '.2%'}, 
                            "daily_vol": {'specifier': '.2%'}, "total_return": {'specifier': ',.2f'}, "calmar": {'specifier': ',.2f'},
                            "daily_sharpe": {'specifier': ',.2f'}, 
                            "yearly_vol": {'specifier': '.2%'},
                            "yearly_sharpe": {'specifier': ',.2f'},
                            "yearly_mean": {'specifier': '.2%'}}
                            )
    }

HEATMAPS_STYLE = {
                # 'width': '1000px', 
                  'height': '800px'}
SELECTED_ASSETS = cts.SELECTED_ASSETS

def get_stats_table(dfstats):
    stat_table = generate_table(dfstats, idname="bt_stats", show_columns=TABLE_SETTINGS_DICT["stats_table"]["show_cols"], 
                                columns_data_config=TABLE_SETTINGS_DICT["stats_table"]["columns_data_config"])
    return dcc.Loading(
    id="bt-statstable-loading",
    type="default",
    children=[
        stat_table,
    ]
    )

def get_pivot_table(trdict):
    all_strats = list(trdict.keys())
    first_strat = all_strats[0]
    if len(all_strats) > 1:
        first_only = {key: False for key in all_strats if key != first_strat}
    else:
        first_only = {first_strat: True}
    trdata = pd.concat([df for key, df in trdict.items()], ignore_index=True)
    rn = random.randint(1, 2000)
    pivot_table =  dash_pivottable.PivotTable(
            id=f'pivot-transactions-{rn}',
            data=trdata.to_dict("records"),
            cols=['Date'],
            colOrder="key_a_to_z",
            rows=['Security', "strategy"],
            rendererName="Stacked Column Chart",
            aggregatorName="First",
            vals=["weights"],
            valueFilter={'strategy': first_only}
        )
    return pivot_table

def load_bt_grpah(asset_list, recipe, cache = False):
    if cache:
        overall_dict = CachingBTGC.read_from_cloud()
        data_plot = pd.DataFrame(overall_dict["data_plot"])
        trdata = overall_dict["transactions"] 
        trdict = {key: pd.DataFrame(df) for key, df in trdata.items()}
        metrics_dict = overall_dict["metrics_dict"] 
        dfstats = pd.DataFrame(overall_dict["dfstats"])
        fig = bth.plot_all_bt_results(data_plot)
    else:
        pricedata = PriceData(asset_list=asset_list)
        data = pricedata._dfraw
        res = jrh.strategy_runner(data, recipe)
        fig = bth.plot_all_bt_results(res)
        trdict = bth.get_transactions_dfdict(res)
        # trdata = pd.concat([df for key, df in trdict.items()], ignore_index=True)
        pivot_table = get_pivot_table(trdict=trdict)
        heatmap_dict = bth.get_returns_heatmaps(res)
        drawdown_dict = bth.get_drawdown_dict(res)
        dfstats = bth.get_all_stats_df(res)
        metrics_dict = {"mreturns": heatmap_dict, "drawdowns": drawdown_dict}
    return fig, trdict, metrics_dict, dfstats


recipe = handle_recipe_dict(recipe_json)
asset_list = SELECTED_ASSETS
figbt, trdict, metrics_dict, dfstats = load_bt_grpah(asset_list=asset_list, recipe=recipe, cache=True)
pivot_table = get_pivot_table(trdict=trdict)
all_strategies = list(metrics_dict["mreturns"].keys())
pivot_row = dcc.Loading(
    id="bt-pivot-loading",
    type="default",
    children=[
        pivot_table,
    ]
    )

recipe_component = html.Div([
    html.H3("Strategy Recipe"),
    dcc.Textarea(id='json-recipe-input', value=json_str, style={'width': '100%', 'height': '800px'}),
    dbc.Button('Validate Recipe', id='validate-recipe-button', n_clicks=0),
    html.Br(),
    html.Div(id='recipe-validation-message'),
    dcc.Store(id='recipe-store', data=handle_recipe_dict(recipe_json)),
    dcc.Store(id='bt-metrics-store', data={})
])
recipe_table = dcc.Loading(
    id="loading5",
    type="default",
    children=[
     html.Div(id = "recipe-table-placeholder", children = [ get_recipe_table()], style=general_style),
    ]
    )
all_assets = list(PriceData()._dfraw.columns)
ticker_mapping_df = pd.read_csv('gs://price-data-etf/configs/ticker_mapping.csv')
name_dict = dict(zip(ticker_mapping_df["asset"].to_list(), ticker_mapping_df["name"].to_list()))
asset_dropdown_bt = html.Div(children = [dcc.Dropdown(
    id="asset_dropdown_bt",
    options=[{"label": name_dict[asset] + f" ({asset})", "value": asset} for asset in all_assets],
    value=SELECTED_ASSETS,  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
    )], style=bt_dropdown_style)

bt_button =  dbc.Button('Run backtest', id='bt-run-button', n_clicks=0)
graph =     dcc.Loading(
    id="bt-graph-loading",
    type="default",
    children=[
        dcc.Graph(id="bt-graph", style= prices_graph_style, figure = figbt),
    ]
    )
# trdata = pd.read_csv("transactions_dict.csv")
# all_strats = list(set(trdata["strategy"]))
# first_strat = all_strats[0]
# if len(all_strats) > 1:
#     first_only = {key: False for key in all_strats if key != first_strat}
# else:
#     first_only = {first_strat: True}

# pivot_table =  dash_pivottable.PivotTable(
#         id='pivot-transactions',
#         data=trdata.to_dict("records"),
#         cols=['Date'],
#         colOrder="key_a_to_z",
#         rows=['Security', "strategy"],
#         rendererName="Stacked Column Chart",
#         aggregatorName="First",
#         vals=["weights"],
#         valueFilter={'strategy': first_only}
#     )




run_bt_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([asset_dropdown_bt], style = {"width": "2500px"}), width = 9 
                ),
                dbc.Col(
                   dbc.Button('Run backtest', id='bt-run-button', n_clicks=0), width = 3
                ),
            ],
            className="mt-3",
        ),
    ],
    fluid=True,
)

collapsible_inputs_bt = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Button(
                                "Backtesting Recipe",
                                id="collapse-button",
                                color="link",
                                
                            )
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    # dbc.Row(start_amount),
                                    # dbc.Row(rebalance_frequency),
                                    # dbc.Row(cov_period ),
                                    # dbc.Row(target_return ),
                                    recipe_component
                                ]
                            ),
                            id="collapse",
                        ),
                    ]
                ),
            )
        ),
    ],
    fluid=True,
)

# dfstats = pd.read_csv("allstats.csv")
stats_table = get_stats_table(dfstats)

def get_heatmap(heatmap_dict, strategy):
        data_df = pd.DataFrame(heatmap_dict[strategy]).set_index("Date")
        data=data_df.values
        fig = px.imshow(data,
                        labels=dict(x="Month", y="Year", color="Returns"),
                        x=list(data_df.columns),
                        y=list(data_df.index),
                        text_auto=True,
                        color_continuous_scale='RdYlGn'
                    )
        fig.update_xaxes(side="top")
        graph = dcc.Graph(
                            id='heatmap-' + strategy,
                            figure=fig,
                            style=HEATMAPS_STYLE
                        )
        return graph

def get_drawdown_graph(drawdown_dict, strategy):
    data_df = pd.DataFrame(drawdown_dict[strategy])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_df["Date"], y=data_df['drawdown'], mode='lines', name='Drawdowns'))
        
        # Update layout
    fig.update_layout(title=f'Drawdowns-{strategy}',
                    xaxis_title='Date',
                    yaxis_title='Drawdown Value',
                    )
    graph = dcc.Graph(
                            id='drawdown-' + strategy,
                            figure=fig,
                            style=HEATMAPS_STYLE
                        )
    return graph

metric_options = [{'label': 'Monthly Returns', 'value': 'Monthly Returns'},
                  {'label': 'Drawdowns', 'value': 'Drawdowns'},
                    ]
metric_select_drowpdown = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='bt-strategy-select',
                options=all_strategies,
                value = all_strategies[1]
            ),
            width=4),
        dbc.Col(
            dcc.Dropdown(
                id='metric-select',
                options=metric_options,
                value="Monthly Returns"
            ),
            width=4
        ),
    ])
])

mdata = metrics_dict["mreturns"]
heatmap = get_heatmap(mdata,  all_strategies[1])
metric_select_graph = dcc.Loading(
    id="bt-metric-loading",
    type="default",
    children=[
        heatmap,
    ]
    )
# run_bt_r