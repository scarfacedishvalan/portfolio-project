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

app = Dash(__name__)

app.layout = html.Div([
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),

    # dcc.Link('Navigate to "/"', href='/'),
    # html.Br(),
    # dcc.Link('Navigate to "/page-2"', href='/page-2'),

    # content will be rendered in this element
    html.Div(id='page-content', children = overall_bt_layout)
])


@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/assetalloc":
        return overall_pricing_layout
    else:
        return overall_bt_layout


if __name__ == '__main__':
    app.run(debug=True)