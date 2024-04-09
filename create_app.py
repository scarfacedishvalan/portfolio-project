from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
from base_layout_components import metas, app_title
from allocation_layout import overall_layout
from callbacks import get_all_callbacks
import flask

def create_app():
    app = Dash(
        __name__,
        # external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME],
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=metas,
        title=app_title,
    )

    app.layout = overall_layout

    @app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open


    app = get_all_callbacks(app)
    return app

if __name__ == "__main__":
    import os
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    # app = create_app()
    app.run_server(debug=True)