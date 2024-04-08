from pathlib import Path
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
from base_layout_components import metas, app_title
from allocation_layout import overall_layout
from callbacks import get_all_callbacks
import dash
from dash import html
import flask
import dash_bootstrap_components as dbc

HERE = Path(__file__).parent

app = dash.Dash()

# app.layout = html.A(dbc.Button("report"), href="/about", target="_blank")
app.layout = html.Div([
    html.A(dbc.Button("report"), href="/about", target="_blank"),
    html.Div(id='page-content', children=[overall_layout]),
])

app = get_all_callbacks(app)

@app.server.route("/about")
def get_report():
    return flask.send_from_directory(HERE, "about-us.html")


if __name__ == "__main__":
    app.run_server(debug=True)