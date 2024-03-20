from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import about
from base_layout_components import start_amount, start_year, number_of_years, end_amount, rate_of_return, footer, collapsible_inputs_bt, create_stats_container
from data_fetch import PriceData
import dash_daq as daq

app_description = """
How does asset allocation affect portfolio performance?   Select the percentage of stocks, bonds and cash
 in a portfolio and see annual returns over any time period from 1928 to 2021.
"""
app_title = "Asset Allocation Visualizer"
app_image = "https://www.wealthdashboard.app/assets/app.png"

metas = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    {"property": "twitter:card", "content": "summary_large_image"},
    {"property": "twitter:url", "content": "https://www.wealthdashboard.app/"},
    {"property": "twitter:title", "content": app_title},
    {"property": "twitter:description", "content": app_description},
    {"property": "twitter:image", "content": app_image},
    {"property": "og:title", "content": app_title},
    {"property": "og:type", "content": "website"},
    {"property": "og:description", "content": app_description},
    {"property": "og:image", "content": app_image},
]

asset_allocation_text = dcc.Markdown(
    """
> **Asset allocation** is one of the main factors that drive portfolio risk and returns.   Play with the app and see for yourself!

> Change the allocation to cash, bonds and stocks on the sliders and see how your portfolio performs over time in the graph.
  Try entering different time periods and dollar amounts too.
"""
)

backtesting_text =  dcc.Markdown(
    """
> **Backtesting** portfolios is an intricate play of parameters.

> Change the selected assets, bounds, rebalance frequency and other parameters to check what happens.
"""
)

####Styling

asset_dropdown_width = {"width": "80%"}
tooltip_styling={
        "always_visible": True,
        "placement": "bottom",
    }
prices_graph_style = {'height': '800px', 'width': '2000px'}



asset_allocation_card = dbc.Card(asset_allocation_text, className="mt-2")

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

all_assets = list(PriceData()._dfraw.columns)
asset_dropdown = dcc.Dropdown(
    id="asset_dropdown",
    options=[{"label": asset, "value": asset} for asset in all_assets],
    value=["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100"],  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
)

asset_dropdown_bt = dcc.Dropdown(
    id="asset_dropdown_bt",
    options=[{"label": asset, "value": asset} for asset in all_assets],
    value=["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100"],  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
)

slider_card = html.Div(
     children = [
    asset_dropdown, 
    html.Br(),
    # get_slider_card(["MOM100", "NIFTYBEES"]),
    html.Div(id="slider_div", children=[]),] 
    # body=True,
    # className="mt-4",
)

input_groups = html.Div(
    [start_amount, start_year, number_of_years, end_amount, rate_of_return],
    className="mt-4 p-4",
)


bounds_add_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='asset-dropdown-bt-setting',
                        options=[{"label": asset, "value": asset} for asset in all_assets],
                        value=None,
                        placeholder="Select Asset"
                    )
                ),
                dbc.Col(
                   dbc.Button('Add Asset bounds', id='add-button', n_clicks=0)
                ),
                dbc.Col(
                   dbc.Button('Validate all settings', id='validate-button', n_clicks=0),
                ),
            ],
            className="mb-3",
        ),
    ],
    fluid=True,
)

run_bt_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([])
                ),
                dbc.Col(
                   dbc.Button('Run backtest', id='bt-run-button', n_clicks=0)
                ),
            ],
            className="mb-3",
        ),
    ],
    fluid=True,
)
bt_layout = html.Div(children=[
     backtesting_text,
     html.Div(children = [collapsible_inputs_bt]),
     html.Br(),
     html.Br(),
     html.Br(),
     html.Br(),
     html.H5("Choose assets for backtesting"),
     html.Br(),
     asset_dropdown_bt,
     html.Br(),
     html.Br(),
#      html.H5("Choose bounds"),
#      html.Br(),
#    bounds_add_row,
#     html.Br(),
#     # dbc.Button('Add Asset bounds', id='add-button', n_clicks=0),
#     html.Br(),
#     html.Div(id='asset-bounds-container', children = []),
#         html.Br(),
    
#     dcc.Store(id='bounds-store', data={}),
    html.Br(),
    run_bt_row,
    html.Br(),
    dcc.Graph(id="bt-graph", style= prices_graph_style),
         html.Br(),
     html.Br(),
     html.H5("Portfolio Statistics"),
    html.Br(),
     html.Br(),
    html.Div(id = "bt_stats_container", children = [create_stats_container(use_samples=True)])
])


tabs = dbc.Tabs(
    [
        # dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
        dbc.Tab(
            [asset_allocation_text, slider_card, 
             html.Br(),
             dbc.Button("Update weights", id = "update-wts-button"),
             html.Br(),
             html.Div(id = "sum_value"),
             html.Br(),
            #   dcc.Checkbox(
            #         id='toggle-show-assets',
            #         label='Show assets data on graph',
            #         value=False,  # Initial value
            #         style={'margin-bottom': '10px'}
            #     ),
            daq.BooleanSwitch(id="show-assets-boolean", on=False, color="red", label="Show Assets Data on Graph",),
            # html.Div(id = "sum_value"),
            html.Br(),
            #  input_groups, time_period_card
            dcc.Graph(id="prices-graph", style= prices_graph_style),
            html.Br(),
            html.Br(),
            html.H5("Portfolio Stats"),
            html.Div(id = "tab1-graphs-placeholder", children = [])
             ],
            tab_id="tab-2",
            label="Asset Allocation Analysis",
            className="pb-4",
        ),
        # dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"),
        dbc.Tab(
            [
             bt_layout, 
                        html.Hr(),
                        html.Div(id="summary_table"),    
             ],
            tab_id="tab-3",
            label="Backtesting",
            className="pb-4",
        ),
    ],
    
    id="tabs",
    active_tab="tab-2",
    className="mt-2",
)


overall_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Asset Allocation Visualizer",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            [
                dcc.Store(id='weights-sum'),
                dcc.Store(id="store-assets-weights", data=[]),
                dcc.Store(id="weights-correct-bool", data=False),
                tabs,
                # dbc.Col(
                #     [
                #         # dcc.Graph(id="allocation_pie_chart", className="mb-2"),
                #         # dcc.Graph(id="returns_chart", className="pb-4"),
                #         bt_layout, 
                #         html.Hr(),
                #         html.Div(id="summary_table"),
                #     ],
                #     # width=12,
                #     # lg=7,
                #     className="p-4",
                # ),
            ],
            className="my-4",
        ),
        dbc.Row(dbc.Col(footer)),
        # dbc.Row(dbc.Col(about.card, width="auto"), justify="center")
    ],
    fluid=True,
)
