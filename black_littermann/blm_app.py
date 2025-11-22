# app.py
import os
import numpy as np
import pandas as pd

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier
from market_data_load import MarketDataLoad
from blm_executor import first_execute
from blm_calculations import build_latex_sections, make_collapsible

# ---------------------------
# App layout (UI only)
# ---------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# default tickers as requested
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]

# initialize sample market data (so UI shows something)
history_filepath = "all_stocks_5yr_history.csv"
weights_filepath = "market_weights.csv"
bmark_filepath = "snp_historical.csv"
market_data = MarketDataLoad(history_filepath, weights_filepath, bmark_filepath, tickers=DEFAULT_TICKERS)

cov_matrix, P, Q, omega, tau, pi, posterior_returns, posterior_cov, cleaned_weights, performance = first_execute()
latex_layout = build_latex_sections(tau, cov_matrix.values, pi, P, Q, omega, posterior_returns, posterior_cov.values)
app, collapsible_layout = make_collapsible(app, latex_layout, title="Show/Hide Black–Litterman Computation Steps")

# sample P and Q for initial display (as in your snippet)
P_sample = np.array([[1, -1, 0, 0],
                     [0, 1, -1, 0]])
Q_sample = np.array([0.05, 0.03])

# helper functions to format data tables
def df_to_table(df, id, max_rows=10):
    if isinstance(df, pd.Series):
        df = df.reset_index()
        df.columns = ["asset", "value"]
    return dash_table.DataTable(
        id=id,
        columns=[{"name": c, "id": c} for c in df.columns],
        data=df.head(max_rows).to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px"},
    )

def matrix_to_table(mat, row_names=None, col_names=None, id=""):
    arr = np.asarray(mat)
    nr, nc = arr.shape
    rows = []
    for i in range(nr):
        row = {}
        for j in range(nc):
            header = col_names[j] if col_names is not None else f"c{j}"
            row[header] = float(np.round(arr[i, j], 6))
        if row_names is not None:
            row["row"] = row_names[i]
        rows.append(row)
    cols = [{"name": "row", "id": "row"}] if row_names is not None else []
    for j in range(nc):
        header = col_names[j] if col_names is not None else f"c{j}"
        cols.append({"name": header, "id": header})
    return dash_table.DataTable(
        id=id,
        columns=cols,
        data=rows,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px"},
    )

# Controls column (left)
controls = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Black-Litterman Explorer", className="card-title"),
                html.P("Select tickers and add textual views. Use 'Add view' to register a view (no callbacks yet)."),
                dbc.Label("Tickers"),
                dcc.Dropdown(
                    id="ticker-select",
                    options=[{"label": t, "value": t} for t in DEFAULT_TICKERS],
                    value=DEFAULT_TICKERS,
                    multi=True,
                    placeholder="Select tickers..."
                ),
                html.Hr(),
                dbc.Label("Investor view (text)"),
                dcc.Textarea(
                    id="view-text",
                    placeholder="e.g. AAPL outperforms MSFT by 5%\nGOOGL outperforms AMZN by 2%",
                    style={"width": "100%", "height": 120},
                ),
                html.Div(className="mt-2", children=[
                    dbc.Button("Add view", id="add-view-btn", color="primary", className="me-2"),
                    dbc.Button("Optimize (BL + Opt)", id="optimize-btn", color="success"),
                ]),
                html.Small("Note: buttons have no callbacks yet — backend will parse text → P/Q and run BL & optimizer.", className="d-block mt-2 text-muted")
            ]
        )
    ],
    className="mb-3"
)

# Left Column: controls + market data preview
left_col = dbc.Col(
    [
        controls,
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Market Data (preview)"),
                    html.Div(df_to_table(market_data.S.reset_index().rename(columns={"index":"asset"}), id="market-cov-table")),
                    html.Br(),
                    html.H6("Market Weights"),
                    html.Div(df_to_table(market_data.weights_df, id="market-weights-table"))
                ]
            )
        )
    ],
    md=4,
)

# Right Column: P, Q, Results
right_col = dbc.Col(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("P matrix (current)"),
                                html.Div(matrix_to_table(P_sample, row_names=[f"view{i+1}" for i in range(P_sample.shape[0])],
                                                       col_names=DEFAULT_TICKERS, id="P-table"))
                            ]
                        )
                    ),
                    md=12
                )
            ],
            className="mb-3"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Q vector (current)"),
                                dash_table.DataTable(
                                    id="Q-table",
                                    columns=[{"name": "view", "id": "view"}, {"name": "Q", "id": "Q"}],
                                    data=[{"view": f"view{i+1}", "Q": float(Q_sample[i])} for i in range(len(Q_sample))],
                                    style_cell={"textAlign": "left", "padding": "6px"}
                                )
                            ]
                        )
                    ),
                    md=12
                )
            ],
            className="mb-3"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Optimized Weights"),
                                dash_table.DataTable(
                                    id="weights-table",
                                    columns=[{"name": "asset", "id": "asset"}, {"name": "weight", "id": "weight"}],
                                    data=[{"asset": t, "weight": 0.0} for t in DEFAULT_TICKERS],
                                    style_cell={"textAlign": "left", "padding": "6px"},
                                ),
                                html.Div(id="weights-note", className="text-muted mt-2", children="Weights will appear here after optimization.")
                            ]
                        )
                    ),
                    md=12
                )
            ],
            className="mb-3"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Portfolio Performance (summary)"),
                                dash_table.DataTable(
                                    id="performance-table",
                                    columns=[{"name": "metric", "id": "metric"}, {"name": "value", "id": "value"}],
                                    data=[{"metric": "Expected annual return", "value": ""}, {"metric": "Annual volatility", "value": ""}, {"metric": "Sharpe", "value": ""}],
                                    style_cell={"textAlign": "left", "padding": "6px"},
                                ),
                                html.Div(className="text-muted mt-2", children="Performance summary will populate after optimization.")
                            ]
                        )
                    ),
                    md=12
                )
            ]
        )
    ],
    md=8,
)

# Footer / hints
footer = dbc.Row(
    dbc.Col(
        dbc.Alert(
            [
                html.P("Implementation notes:", className="mb-1"),
                html.Ul(
                    [
                        html.Li("Parse the textual views (textarea) into P and Q in a backend routine and store them in app state."),
                        html.Li("Add callbacks: Add-view -> update P and Q tables; Optimize -> run BL + Efficient Frontier and update weights & performance tables."),
                        html.Li("Use proper BL implementation (e.g. PyPortfolioOpt BlackLittermanModel) and your MarketDataLoad class."),
                    ]
                )
            ],
            color="info"
        ),
        width=12
    ),
    className="mt-3"
)

app.layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(dbc.Col(html.H3("Black-Litterman UI (view only, no callbacks)"))),
        html.Hr(),
        dbc.Row([left_col, right_col]),
        # footer,
        collapsible_layout,
        html.Br(),
        html.Div("App created as a UI scaffold. Replace placeholder classes with real implementations and add callbacks.", className="text-muted small"),
    ],
    fluid=True
)

# Run server
if __name__ == "__main__":
    app.run_server(debug=True)
