# app.py
import json
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from interest_rates.holee_content import content_data

# --- Configure which sections are collapsible (True) vs always open (False)
collapsible_config = {
    "1. Introduction": False,
    "2. Bond Pricing Equation (BPE) Setup": True,
    "3. No-Arbitrage Interpretation": False,
    "4. Calibration Problem": True,
    "5. Calibration Setup": True,
    "6. Solving the Integral Equation": True,
    "7. Final Calibration Formula": False,
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                external_scripts=[
                                    # Load MathJax from CDN
                                    "https://polyfill.io/v3/polyfill.min.js?features=es6",
                                    "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
                                ])


def make_sections():
    sections = []
    collapsible_idx = 0

    for title, text in content_data.items():
        is_collapsible = collapsible_config.get(title, False)

        body = dbc.CardBody(
            dcc.Markdown(text, dangerously_allow_html=True)
        )

        if is_collapsible:
            sections.append(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H2(
                                dbc.Button(
                                    title,
                                    color="link",
                                    id={"type": "toggle-btn", "index": collapsible_idx},
                                    n_clicks=0,
                                )
                            )
                        ),
                        dbc.Collapse(
                            body,
                            id={"type": "collapse", "index": collapsible_idx},
                            is_open=False,
                        ),
                    ],
                    # className="mb-3",
                )
            )
            collapsible_idx += 1
        else:
            sections.append(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4(title)),
                        body
                    ],
                    # className="mb-3",
                )
            )
    return sections



app.layout = dbc.Container(
    [
        html.H1("Ho & Lee Model – Detailed Notes", className="my-4"),
        html.Div(make_sections()),
    ],
    fluid=True,
)

# --- Single pattern-matching callback for ALL collapsible sections
@app.callback(
    Output({"type": "collapse", "index": dash.ALL}, "is_open"),
    Input({"type": "toggle-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "collapse", "index": dash.ALL}, "is_open"),
)
def toggle_collapses(n_clicks_list, is_open_list):
    """Toggle only the collapse that was clicked; leave others unchanged."""
    # If there are no collapsible sections, just return what Dash passes us.
    if n_clicks_list is None or is_open_list is None:
        return is_open_list

    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open_list

    # Determine which button fired
    triggered_spec = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        trig = json.loads(triggered_spec)  # {'type':'toggle-btn','index': k}
    except Exception:
        return is_open_list

    if trig.get("type") != "toggle-btn":
        return is_open_list

    k = trig.get("index", None)
    if k is None or k >= len(is_open_list) or k < 0:
        return is_open_list

    # Toggle only the clicked panel
    updated = list(is_open_list)
    updated[k] = not updated[k]
    return updated


if __name__ == "__main__":
    app.run_server(debug=True)
