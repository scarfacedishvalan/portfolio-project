import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from interest_rates.ir_helpers import render_model_inputs, model_config
from interest_rates.ir_callbacks import add_callbacks
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output

def create_ir_app():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    table_def =             dash_table.DataTable(
                    id = "summary-table",
                    data= pd.DataFrame(columns=["Statistic", "Value"]).to_dict("records"),
                    columns=[{'id': c, 'name': c} for c in ["Statistic", "Value"]],
                    style_table={'overflowX': 'auto'},
                    style_cell={'padding': '5px', 'textAlign': 'left'},
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'Statistic'},
                            'width': '60%',
                            'minWidth': '150px',
                            'maxWidth': '300px',
                            'whiteSpace': 'normal'
                        },
                        {
                            'if': {'column_id': 'Value'},
                            'width': '40%',
                            'minWidth': '80px',
                            'maxWidth': '150px',
                            'textAlign': 'right'
                        }
                    ],
                    style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
                    style_as_list_view=True                
                )

    app.layout = dbc.Container([
        dbc.Row([
            # Sidebar with controls
            dbc.Col([
                dcc.Store(id="simulation-store"),
                html.H4("Model Selection & Parameters"),
                dbc.Label("Select Interest Rate Model"),
                dcc.Dropdown(
                    id='model-select',
                    options=[
                        {'label': 'Vasicek', 'value': 'vasicek'},
                        {'label': 'CIR', 'value': 'cir'},
                        {'label': 'Hull-White', 'value': 'hw'}
                    ],
                    value='vasicek'
                ),

                html.Div(id='model-params-container'),

                html.Hr(),

                html.H4("Simulation Settings"),

                dbc.Label("Time Horizon (years)"),
                dbc.Input(id='horizon-input', type='number', step=1, value=5),

                dbc.Label("Number of Paths"),
                dbc.Input(id='paths-input', type='number', step=100, value=1000),

                dbc.Label("Time Steps (months)"),
                dbc.Input(id='timestep-input', type='number', step=1, value=60),
                dbc.Button("Run Simulation", id="run-simulation-btn", n_clicks=0),

                html.Hr(),

                html.H4("Macro Scenarios"),

                dcc.Dropdown(
                    id='scenario-select',
                    options=[
                        {'label': 'Baseline', 'value': 'baseline'},
                        {'label': 'High Inflation', 'value': 'inflation'},
                        {'label': 'Recession', 'value': 'recession'},
                        {'label': 'Soft Landing', 'value': 'soft'}
                    ],
                    value='baseline'
                )
            ], width=3),

            # Main display area
            dbc.Col([
                html.H4("Simulated Yield Curves"),
                dcc.Graph(id='yield-curve-graph', figure={}),

                dbc.Row([
                            dbc.Col([
                                dbc.Label("View cross-section at t:"),
                                dbc.Input(id="t-view", type="number", value=1.0),
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Bins:"),
                                dbc.Input(id="nbinsx-input", type="number", value=50, step = 10),
                            ], width=2),
                            dbc.Col([
                                html.Br(),
                                dbc.Button("Cross Section", id="cross-section-btn", color="primary"),
                            ], width=6),
                        ], className="my-2"),

                dcc.Graph(id='dist-graph', figure={}),

                html.H4("Summary Statistics"),
                # dbc.Table(id='summary-table', bordered=True, striped=True, hover=True)

                dbc.Row([
                            dbc.Col([table_def], width = 6)
                ])
            ], width=9)
        ])
    ], fluid=True)

    app = add_callbacks(app)
    return app

if __name__ == '__main__':
    app = create_ir_app()    
    app.run_server(debug=False)
