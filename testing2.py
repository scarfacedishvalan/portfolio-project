import interest_rates.holee_page as holee_page
from interest_rates.yield_curve_layout import yield_curve_ns_layout, add_yield_callbacks
from interest_rates.holee_calib_layout import holee_calib_layout
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from interest_rates.holee_page import add_collapse_callbacks
from dash_extensions import Lottie

# --- Initialize the app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,)

# --- Tab content definitions
tab1_content = holee_page.holee_notes_layout()

tab2_content = yield_curve_ns_layout()

tab3_content = holee_calib_layout()

lottie_layout =     Lottie(
        options=dict(loop=True, autoplay=True),
        width="25%",
        height="25%",
        # url="https://assets1.lottiefiles.com/packages/lf20_jcikwtux.json"
        url="/assets/flowchart4.json"
    )
# --- Layout with side-by-side tabs
app.layout = dbc.Container(
    [
        html.H1("Interest Rate Models: Ho and Lee", className="my-4",  style={"textAlign": "center"}),
        html.Div([lottie_layout]),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Tabs(
                        id="side-tabs",
                        value="tab-1",
                        children=[
                            dcc.Tab(label="Ho & Lee Framework", value="tab-1", children=[tab1_content]),
                            dcc.Tab(label="Yield Curve Fitting", value="tab-2", children=[tab2_content]),
                            dcc.Tab(label="Ho & Lee Calibration", value="tab-3", children=[tab3_content]),
                        ],
                        style={"height": "100%"}
                    ),
                    width=12
                )
            ]
        ),
    ],
    fluid=True
)

app = holee_page.add_collapse_callbacks(app)
app = add_yield_callbacks(app)
# app = add_collapse_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)


