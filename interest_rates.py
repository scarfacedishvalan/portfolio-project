import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from ir_helpers import render_model_inputs, model_config

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

from dash.dependencies import Input, Output

@app.callback(
    Output("model-params-container", "children"),
    Input("model-select", "value")
)
def update_model_inputs(model_name):
    return render_model_inputs(model_name)


app.layout = dbc.Container([
    dbc.Row([
        # Sidebar with controls
        dbc.Col([
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

            dbc.Label("Time Step (months)"),
            dbc.Input(id='timestep-input', type='number', step=1, value=1),

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

            html.H4("Rate Distribution Heatmap"),
            dcc.Graph(id='heatmap-graph', figure={}),

            html.H4("Summary Statistics"),
            dbc.Table(id='summary-table', bordered=True, striped=True, hover=True)
        ], width=9)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
