from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
from base_layout_components import metas, app_title
from bt_callbacks import get_bt_callbacks
from bt_layout import overall_bt_layout
from pricing_layout import overall_pricing_layout
from pricing_callbacks import get_pricing_callbacks

def create_app():
    app = Dash(
        __name__,
        # external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME],
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=metas,
        title=app_title,
    )

    app.layout = html.Div([
        # represents the browser address bar and doesn't render anything
        html.H1("Optimal Strategies for Portfolio Allocation", style={'textAlign': 'center'}),
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
    return app

if __name__ == "__main__":
    import os
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    app = create_app()
    app.run_server(debug=False)