# app.py
import json
import re
import dash
import dash_latex as dl
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
from interest_rates.holee_content import content_data

# --- Configure which sections are collapsible (True) vs always open (False)
collapsible_config = {
    "1. Introduction": False,
    "2. Bond Pricing Equation (BPE) Setup": True,
    "3. No-Arbitrage Interpretation": False,
    "4. Calibration Problem": False,
    "5. Calibration Setup": True,
    "6. Solving the Integral Equation": True,
    "7. Final Calibration Formula": False,
}


# --- Helper: split text into paragraphs and LaTeX components
def render_latex_section(text):
    """
    Splits LaTeX content into multiple DashLatex or HTML elements so that
    each equation renders on a separate line.
    Supports $$...$$ and \[...\] block equations, plus inline \( ... \).
    """
    # Pattern to match LaTeX block equations: $$...$$ or \[...\]
    # parts = re.split(r"(\$\$.*?\$\$|\\\[.*?\\\])", text, flags=re.S)

    rendered = []
    for part in text:
        if not part.strip():
            continue

        # Block equation
        if part.strip().startswith("$$") or part.strip().startswith("\\[") or part.strip().startswith("\\["):
            rendered.append(html.Div(dl.DashLatex(part.strip()), className="my-eq"))

        # Regular text (may contain inline math)
        else:
            rendered.append(html.Div(dl.DashLatex(part.strip()), className="my-2"))

    return rendered


# --- Build section layout
def make_sections(content, collapsible_config, start_idx = 0):
    sections = []
    collapsible_idx = start_idx

    for title, text in content.items():
        is_collapsible = collapsible_config.get(title, False)

        # Each part gets its own <div>
        body_parts = render_latex_section(text)

        # Wrap each part in its own Div for spacing
        body = dbc.CardBody(body_parts)

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
                    className="mb-3",
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
                    className="mb-3",
                )
            )
    return sections


# --- Layout
def holee_notes_layout():
    return dbc.Container(
        [
            html.H1("Ho & Lee Model – Detailed Notes", className="my-4"),
            html.Div(make_sections(content_data, collapsible_config)),
        ],
        fluid=True,
    )

def add_collapse_callbacks(app):
    # --- Single pattern-matching callback for ALL collapsible sections
    @app.callback(
        Output({"type": "collapse", "index": dash.ALL}, "is_open"),
        Input({"type": "toggle-btn", "index": dash.ALL}, "n_clicks"),
        State({"type": "collapse", "index": dash.ALL}, "is_open"),
    )
    def toggle_collapses(n_clicks_list, is_open_list):
        """Toggle only the collapse that was clicked; leave others unchanged."""
        if n_clicks_list is None or is_open_list is None:
            return is_open_list

        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open_list

        triggered_spec = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            trig = json.loads(triggered_spec)
        except Exception:
            return is_open_list

        if trig.get("type") != "toggle-btn":
            return is_open_list

        k = trig.get("index", None)
        if k is None or k >= len(is_open_list) or k < 0:
            return is_open_list

        updated = list(is_open_list)
        updated[k] = not updated[k]
        return updated
    
    return app

if __name__ == "__main__":
    # app.run_server(debug=True)
    a=2
