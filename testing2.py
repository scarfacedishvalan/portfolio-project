import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from texts import get_text_content
from bt_layout import ALL_CARDS_DICT, HEADINGS_DICT
from base_layout_components import metas, app_title
from bt_callbacks import get_bt_callbacks
from bt_layout import overall_bt_layout
from pricing_layout import overall_pricing_layout
from pricing_callbacks import get_pricing_callbacks


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX],
                meta_tags=metas,
                title=app_title)


# App layout
app.layout = html.Div([
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children = overall_bt_layout)
])


@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/assetalloc":
        return overall_pricing_layout
    else:
        return overall_bt_layout
app = get_pricing_callbacks(app)
app = get_bt_callbacks(app)

# app = get_bt_callbacks(app)

if __name__ == "__main__":
    import os
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    app.run_server(debug=False)
