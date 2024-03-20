from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from json_recipe_handler import load_json_recipe, handle_recipe_dict
import json
from dash import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import calendar
from multiindex_table_create import multiindex_table

# Define the years and months

MAX_YR = 2014
MIN_YR = 2024
START_YR = 2007

        # if chosen_assets is not None:
        #     self.pricedata_obj._dfraw = pd.DataFrame(self.pricedata_obj._dfraw[chosen_assets])
        # self.rebalance_frequency = 365
        # self.rebalance_start_period = cov_period
        # self.initial_investment = 10000
        # self.cov_period = cov_period
        # self.bounds = bounds


TABLE_SETTINGS_DICT = {"stats_table": dict (   
    show_cols = ["Investment", 'total_return', 'cagr', 'max_drawdown', 'calmar', "daily_mean", "daily_vol", "daily_sharpe"],
    columns_data_config = {"cagr": {'specifier': '.2%'}, "max_drawdown": {'specifier': '.2%'}, "daily_mean": {'specifier': '.2%'}, 
                            "daily_vol": {'specifier': '.2%'}, "total_return": {'specifier': ',.2f'}, "calmar": {'specifier': ',.2f'},
                            "daily_sharpe": {'specifier': ',.2f'}}
                            )
    }

HEATMAPS_STYLE = {'width': '1000px', 'height': '800px'}
ALL_STATS_HEADING = html.H2("Backtest Stats", style={'textAlign': 'center'})
BT_STATS_HEADING = html.H3("Strategy Summary Stats", style={'textAlign': 'center'})
MONTHLY_RETURNS_HEADING = html.H3("Monthly Returns", style={'textAlign': 'center'})
TRANSACTIONS_HEADING = html.H3("Transaction Value Details", style={'textAlign': 'center'})

def generate_table(dataframe, idname, show_columns, columns_data_config, cellwidth = '150px'):
    hidden_cols = [col for col in dataframe.columns if col not in show_columns]
    columns = []
    for col in dataframe.columns:
        d = {'name': col, 'id': col}
        if col in columns_data_config:
            d.update({'type': 'numeric', 'format': columns_data_config.get(col, None)})
        columns.append(d)
    return dash_table.DataTable(
        id=idname,
        columns=columns,
        data=dataframe.to_dict('records'),
        style_table={'overflowX': 'auto'},  # Enable horizontal scrolling
        hidden_columns=hidden_cols,
        style_cell={'width': cellwidth},
        sort_action='native'
    )
def get_sample_dfs():
    sample_dfstats = pd.DataFrame({
        "Investment": ["Asset A", "Asset B", "Asset C"],
        "total_return": [0.15, 0.25, 0.12],
        "cagr": [0.1, 0.12, 0.08],
        "max_drawdown": [0.05, 0.06, 0.04],
        "calmar": [2.0, 2.1, 1.5],
        "daily_mean": [0.002, 0.003, 0.0015],
        "daily_vol": [0.01, 0.012, 0.009],
        "daily_sharpe": [0.2, 0.25, 0.17]
    })
    years = range(2010, 2023)
    months = range(1, 13)

    # Get full month names
    month_names = [calendar.month_name[month] for month in months] + ["YTD"]

    # Generate random returns between -1 and 1 for each month
    sample_returns_data = np.random.uniform(-1, 1, size=(len(years), len(month_names)))
    returns_df = pd.DataFrame(sample_returns_data, index=years, columns=month_names).round(2)
    sample_returns_data2 = np.random.uniform(-1, 1, size=(len(years), len(month_names)))
    returns_df2 = pd.DataFrame(sample_returns_data2, index=years, columns=month_names).round(2)
    sample_heatmap_dict = {"Strategy1": returns_df, "Strategy2": returns_df2}
    dates = pd.date_range('2024-01-01', periods=5)
    securities = ['AAPL', 'GOOGL', 'MSFT']
    num_rows = len(dates) * len(securities)

    # Create multiindex
    index = pd.MultiIndex.from_product([dates, securities], names=['Date', 'Security'])

    # Create dataframe
    data = {
        'price': np.random.uniform(100, 200, num_rows),
        'weights': np.random.uniform(0, 1, num_rows),
        'pfolio_value': np.random.uniform(10000, 20000, num_rows),
        'asset_value': np.random.uniform(5000, 10000, num_rows)
    }

    dftrc = pd.DataFrame(data, index=index).round(2)
    dftrc.index = dftrc.index.set_levels(dftrc.index.levels[0].strftime('%Y-%m-%d'), level=0)
    data2 = {
        'price': np.random.uniform(100, 200, num_rows),
        'weights': np.random.uniform(0, 1, num_rows),
        'pfolio_value': np.random.uniform(10000, 20000, num_rows),
        'asset_value': np.random.uniform(5000, 10000, num_rows)
    }
    dftrc2 = pd.DataFrame(data2, index=index).round(2)
    dftrc2.index = dftrc2.index.set_levels(dftrc2.index.levels[0].strftime('%Y-%m-%d'), level=0)
    dftrc_dict = {"Strategy1": dftrc, "Strategy2": dftrc2}
    return sample_dfstats, sample_heatmap_dict, dftrc_dict

def create_stats_container(dfstats=None, heatmap_dict=None, dftrc_dict = None, use_samples = False):
    if use_samples:
        dfstats, heatmap_dict, dftrc_dict = get_sample_dfs()
    datatable_rows = []
    row = dbc.Row([
            dbc.Col(BT_STATS_HEADING)
        ], style={'paddingBottom': '40px'})
    datatable_rows.append(row)
    stat_table = generate_table(dfstats, idname="bt_stats", show_columns=TABLE_SETTINGS_DICT["stats_table"]["show_cols"], 
                                columns_data_config=TABLE_SETTINGS_DICT["stats_table"]["columns_data_config"])
    row = dbc.Row([
            dbc.Col(stat_table)
        ], style={'paddingBottom': '20px'})
    datatable_rows.append(row)
    row = dbc.Row([
            dbc.Col(MONTHLY_RETURNS_HEADING)
        ], style={'paddingBottom': '40px'})
    datatable_rows.append(row)
    for strategy, data_df in heatmap_dict.items():
        # Create DataTable for each DataFrame
        data=data_df.values
        fig = px.imshow(data,
                        labels=dict(x="Year", y="Month", color="Returns"),
                        x=list(data_df.columns),
                        y=list(data_df.index),
                        text_auto=True,
                        color_continuous_scale='RdYlGn'
                    )
        fig.update_xaxes(side="top")
        # fig.update_layout(title={
        #                     'text': strategy,
        #                     'x': 0.5,  # Center the title horizontally
        #                     'y': 2,  # Adjust the gap between title and figure
        #                     'xanchor': 'center',  # Center the title horizontally
        #                     'yanchor': 'top',  # Anchor the title to the top of the figure
        #                      })
        graph = dcc.Graph(
                            id='heatmap-' + strategy,
                            figure=fig,
                            style=HEATMAPS_STYLE
                        )
        # Create a dbc.Row for each DataTable
        row = dbc.Row([
            dbc.Col(html.H5(strategy + " Monthly Returns"))
        ], style={'paddingBottom': '10px'})
        datatable_rows.append(row)
        row = dbc.Row([
            dbc.Col(graph)
        ], style={'paddingBottom': '20px'})
        datatable_rows.append(row)
    row = dbc.Row([
            dbc.Col(TRANSACTIONS_HEADING)
        ], style={'paddingBottom': '40px'})
    datatable_rows.append(row)
    for strategy, dftrc in dftrc_dict.items():
        dftrc = dftrc.round(2)
        try:
            dftrc.index = dftrc.index.set_levels(dftrc.index.levels[0].strftime('%Y-%m-%d'), level=0)
        except:
            pass
        row = dbc.Row([
            dbc.Col(html.H5(strategy + " Transaction Details"))
        ], style={'paddingBottom': '5px'})
        datatable_rows.append(row)
        html_table = multiindex_table(dftrc)
        row = dbc.Row([
                dbc.Col(html_table)
            ], style={'paddingBottom': '20px'})
        datatable_rows.append(row)
    # Create a dbc.Container to hold all the dbc.Rows
    container = dbc.Container([ALL_STATS_HEADING] + [html.Br()] + datatable_rows, fluid=True)
    return container

start_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Initial Amount "),
        dbc.Input(
            id="initial_investment",
            placeholder="Min 10",
            type="text",
            min=10,
            value=100000,
        ),
    ],
    className="mb-3",
)

rebalance_frequency = dbc.InputGroup(
    [
        dbc.InputGroupText("Rebalance frequency"),
        dbc.Input(
            id="rebal_freq",
            placeholder="Min 7",
            type="text",
            value="365",
        ),
    ],
    className="mb-3",
)

cov_period = dbc.InputGroup(
    [
        dbc.InputGroupText("Covariance period"),
        dbc.Input(
            id="cov_period",
            placeholder="Min 365",
            type="text",
            value=str(365*3),
        ),
    ],
    className="mb-3",
)

target_return = dbc.InputGroup(
    [
        dbc.InputGroupText("Target Return"),
        dbc.Input(
            id="target_return",
            type="text",
            value="0.1",
        ),
    ],
    className="mb-3",
)

recipe_json = load_json_recipe("recipe.json")
json_str = json.dumps(recipe_json, indent=4)

recipe_component = html.Div([
    html.H3("Strategy Recipe"),
    dcc.Textarea(id='json-recipe-input', value=json_str, style={'width': '100%', 'height': '300px'}),
    html.Button('Validate Recipe', id='validate-recipe-button', n_clicks=0),
    html.Div(id='recipe-validation-message'),
    dcc.Store(id='recipe-store', data=handle_recipe_dict(recipe_json))
])


collapsible_inputs_bt = dbc.Container(
    [
        # dbc.Row(
        #     dbc.Col(
        #         html.H2("Collapsible Input Settings", className="text-center mb-4"),
        #     )
        # ),
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
start_year = dbc.InputGroup(
    [
        dbc.InputGroupText("Start Year"),
        dbc.Input(
            id="start_yr",
            placeholder=f"min {MIN_YR}   max {MAX_YR}",
            type="number",
            min=MIN_YR,
            max=MAX_YR,
            value=START_YR,
        ),
    ],
    className="mb-3",
)
number_of_years = dbc.InputGroup(
    [
        dbc.InputGroupText("Number of Years:"),
        dbc.Input(
            id="planning_time",
            placeholder="# yrs",
            type="number",
            min=1,
            value=MAX_YR - START_YR + 1,
        ),
    ],
    className="mb-3",
)
end_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Ending Amount"),
        dbc.Input(id="ending_amount", disabled=True, className="text-black"),
    ],
    className="mb-3",
)
rate_of_return = dbc.InputGroup(
    [
        dbc.InputGroupText(
            "Rate of Return(CAGR)",
            id="tooltip_target",
            className="text-decoration-underline",
        ),
        dbc.Input(id="cagr", disabled=True, className="text-black"),
        # dbc.Tooltip(cagr_text, target="tooltip_target"),
    ],
    className="mb-3",
)


footer = html.Div(
    [
        dcc.Markdown(
            """
             This information is intended solely as general information for educational
            and entertainment purposes only and is not a substitute for professional advice and
            services from qualified financial services providers familiar with your financial
            situation.            
            """
        ),

    ],
    className="p-2 mt-5 bg-primary text-white small",
)


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
