import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from interest_rates.fred_real_yields import USYieldCurveLoader
from interest_rates.nelson_siegal import NelsonSiegelFitter
from interest_rates.holee_page import make_sections, add_collapse_callbacks
import dash
import pandas as pd
from datetime import date
import numpy as np
import plotly.graph_objects as go


ROW_STYLE = {"margin-top": "40px"}

collapsible_config = {
    "Mathematical Framework for Nelson Siegal": True
}

NS_FRAMEWORK = {"Mathematical Framework for Nelson Siegal": [
    "The Nelson–Siegel model expresses the yield curve as a function of maturity τ:",
    r"\[ y(\tau) = \beta_0 + \beta_1 \frac{1 - e^{-\lambda \tau}}{\lambda \tau} + \beta_2 \left( \frac{1 - e^{-\lambda \tau}}{\lambda \tau} - e^{-\lambda \tau} \right) \]",

    "where:",
    r"\( \beta_0 \) = long-term level of interest rates (level factor),",
    r"\( \beta_1 \) = short-term component capturing slope,",
    r"\( \beta_2 \) = medium-term component capturing curvature,",
    r"\( \lambda \) = decay parameter controlling how fast the exponential term decays.",

    "Discount factor is obtained from zero yield:",
    r"\[ P(t,\tau) = e^{-y(\tau) \cdot \tau} \]",

    "Fitting is done by minimizing the sum of squared errors (SSE):",
    r"\[ SSE(\beta_0, \beta_1, \beta_2, \lambda) = \sum_{\tau} \left( y^{obs}(\tau) - y(\tau) \right)^2 \]"
]}



def fitting_process(data, selected_date):
    curve_loader = USYieldCurveLoader()
    curve_loader.set_data(data, selected_date)
    df_fit = curve_loader.get_curve_data_for_fitting()
    tau_obs = df_fit["tau"].to_list()
    y_obs = df_fit["continuous_zero_rates"].to_list()

    tau_eval = np.linspace(1/365, 30.0, 2000)
    nsf = NelsonSiegelFitter(tau_obs, y_obs, tau_grid=tau_eval)
    l, b  = nsf.fit()
    df_params = pd.DataFrame(columns=["Parameter", "Value"])
    df_params["Parameter"] = ["λ", "β0", "β1", "β2"]
    df_params["Value"] = [np.round(l, 2)] + list([np.round(x, 4) for x in b])
    fig = nsf.plot_sse_vs_lambda()
    return df_params, fig

def fitted_curve_details(data, selected_date):
    curve_loader = USYieldCurveLoader()
    curve_loader.set_data(data, selected_date)
    df_fit = curve_loader.get_curve_data_for_fitting()
    tau_obs = df_fit["tau"].to_list()
    y_obs = df_fit["continuous_zero_rates"].to_list()

    tau_eval = np.linspace(1/365, 30.0, 2000)
    nsf = NelsonSiegelFitter(tau_obs, y_obs, tau_grid=tau_eval)
    nsf.fit()
    return nsf

def initial_load_details():
    curve_loader = USYieldCurveLoader()
    data = curve_loader.load_data()
    df = data.reset_index()
    max_date = df["DATE"].max().date()
    df_params, sse_fig = fitting_process(data=data, selected_date=max_date)
    l = df_params.iloc[0,1]
    nsf = fitted_curve_details(data=data, selected_date=max_date)
    base_yield_fig = nsf.base_yield_plot()

    datestr = pd.to_datetime(max_date).strftime("%Y-%m-%d")
    base_yield_fig.update_layout(
        xaxis_title="Maturity (years)",
        yaxis_title="Yield",
        template="plotly_white",
        title=dict(text=f"Nelson–Siegel Yield Curve (As of {datestr})", x=0.5, xanchor="center"),
    )
    base_yield_fig = nsf.add_lambda_trace(lmbda=l, fig=base_yield_fig)
    return max_date, df_params, sse_fig, l, base_yield_fig

def yield_curve_ns_layout():
    max_date, df_params, sse_fig, l, base_yield_fig = initial_load_details()
    math_text = html.Div(make_sections(NS_FRAMEWORK, collapsible_config, start_idx=50))
    return html.Div([
        dcc.Store(id="yield-curve-store", data={}),

       
        
        # Row 1: Historical Yield Curves
        dbc.Row([
            dbc.Col([
                html.H3("Section 1: Historical Yield Curves"),
                html.P("This chart displays historical yield curve data for all maturities "
                       "so you can see changes in interest rates over time. This data has been sourced from FRED's publically available API."),
                dcc.Graph(
                    id="historical-yield-graph",
                    figure={},  # placeholder
                    style={"height": "500px"}
                )
            ], width=12)
        ], style= ROW_STYLE, className="mb-4"),

        # Row 2: Date Picker + Button
        dbc.Row(
                    dbc.Col(
                        html.H2("Fitting Yield Curve using Nelson Siegal"),
                        width="auto"  # makes the column shrink to fit content
                    ),
                    justify="center", 
                    style=ROW_STYLE
                ),
        dbc.Row([math_text], style=ROW_STYLE),

        dbc.Row([
            dbc.Col([
                html.H3("Section 2: Select Date and Fit Model"),
                html.P("Choose a snapshot date to extract the yield curve and run the "
                       "Nelson-Siegel fitting procedure to estimate λ and β parameters."),
                dcc.DatePickerSingle(
                    id="date-picker",
                    display_format="YYYY-MM-DD",
                    style={"margin-right": "20px"},
                    initial_visible_month= date.today(),
                    date= max_date
                ),
                dbc.Button(
                    "Run Fitter",
                    id="run-fitter-btn",
                    n_clicks=0,
                    color="primary"
                )
            ], style= ROW_STYLE, width=12)
        ], className="mb-4"),

        # Row 3: Table + SSE Figure
        dbc.Row([
            dbc.Col([
                html.H3("Section 3: Fitting Results and SSE Analysis"),
                html.P("The table shows the best-fitting parameters, while the chart "
                       "illustrates how the Sum of Square Errors (SSE) changes with different λ values."),
                dash_table.DataTable(
                    id="fitted-params-table",
                    columns=[
                        {"name": "Parameter", "id": "Parameter"},
                        {"name": "Value", "id": "Value"}
                    ],
                    data=df_params.to_dict("records"),
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center"},
                    style_header={"fontWeight": "bold"}
                )
            ], width=4),

            dbc.Col([
                dcc.Graph(
                    id="sse-lambda-graph",
                    figure=sse_fig,  # placeholder
                    style={"height": "400px"}
                )
            ], width=8)
        ], style= ROW_STYLE),

        # ROW 4: vA
        dbc.Row([
            dbc.Col([
                html.H3("Section 4: Impact of fit parameters on Curve"),
                html.P("The below graph demonstrates the fitted yield curve with the best fit parameters by default.", 
                       "Additionally the user can change the values of λ to see how the curve is impacted."),
            ], width=12)
        ], style=ROW_STYLE),

        dbc.Row([
                    dbc.Col(html.Label("Select λ", style={"margin-left": "200px"}), width="auto"),
                    # dbc.Col(html.Label("Select sigma", style={"margin-left": "600px", "margin-right": "10px"}), width="auto"),
                ], style=ROW_STYLE, align="center"),


        dbc.Row([
                    dbc.Col(
                        dcc.Slider(
                            id="lambda-slider",
                            min=0.1,
                            max=5,
                            step=0.1,
                            value=l,  # default value
                            tooltip={"placement": "bottom", "always_visible": True},
                            marks={i: str(i) for i in range(1, 6)}
                        ),
                        width=3  # controls slider width
                    ),
                    # dbc.Col(
                    #     dcc.Slider(
                    #         id="sigma-slider",
                    #         min=0.01,
                    #         max=1.0,
                    #         step=0.01,
                    #         value=0.2,  # default value
                    #         tooltip={"placement": "bottom", "always_visible": True},
                    #         marks={round(i, 2): str(round(i, 2)) for i in [0.1, 0.5, 1.0]}
                    #     ),
                    #     width=3
                    # ),

                    dbc.Col(
                        dbc.Button(
                            "Add New Fit",
                            id="add-new-fit-btn",
                            n_clicks=0,
                            color="primary",
                            style={"margin-left": "20px"}
                        ),
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Clear Graph",
                            id="clear-btn",
                            n_clicks=0,
                            color="secondary",
                            style={"margin-left": "20px"}
                        ),
                        width="auto"
                    )
                ], style=ROW_STYLE, align="center"),

        # Row 5: New Fit Figure
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id="new-fit-graph",
                    figure=base_yield_fig,  # placeholder
                    style={"height": "400px"}
                )
            ], width=12)
        ], style=ROW_STYLE)
    ], style={"padding": "20px"})



def add_yield_callbacks(app):

    @app.callback(
        [Output("historical-yield-graph", "figure"),
         Output("yield-curve-store", "data")],
        [Input("run-fitter-btn", "n_clicks")],  # fires on load & button click
        prevent_initial_call=False
    )
    def load_historical_yield_curve(n_clicks):
        """
        Loads the historical yield curve figure and raw data into dcc.Store.
        Button input is unused but included so the callback is consistent.
        """
        # TODO: Replace with actual processing logic
        curve_loader = USYieldCurveLoader()
        data = curve_loader.load_data()
        fig = curve_loader.plot_historical_yields()  
        data = data.reset_index()       # placeholder Plotly figure
        raw_data = data.to_dict("records")  # placeholder raw data (e.g., DataFrame to dict)

        return fig, raw_data


    @app.callback(
        [
            Output("date-picker", "min_date_allowed"),
            Output("date-picker", "max_date_allowed")
        ],
        [Input("yield-curve-store", "data")]
    )
    def update_date_picker_range(raw_data):
        """
        Updates the date picker range and defaults to the max date.
        """
        if not raw_data:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update
            )

        df = pd.DataFrame(raw_data)
        df["DATE"] = pd.to_datetime(df["DATE"])
        
        min_date = df["DATE"].min().date()
        max_date = df["DATE"].max().date()

        # Set both start/end range and selected date to max date
        return min_date, max_date


    @app.callback(
        [Output("fitted-params-table", "data"),
         Output("sse-lambda-graph", "figure")],
        [Input("run-fitter-btn", "n_clicks"),
        Input("date-picker", "date"),
         Input("yield-curve-store", "data")],
        prevent_initial_call=False
    )
    def run_ns_fitter(n_clicks, selected_date, raw_data):
        """
        Runs Nelson-Siegel fitting based on selected date and stored yield curve data.
        Triggered when 'Run Fitter' button is clicked.
        """
        try:
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            if not raw_data:
                return [dash.no_update, dash.no_update]
            df = pd.DataFrame(raw_data)
            data = df.set_index("DATE")            
            if "run-fitter-btn" in changed_id:
                df_params, sse_fig = fitting_process(data=data, selected_date=selected_date)
                l = df_params.iloc[0,1]
                # TODO: Replace with actual fitting logic
                table_data = df_params.to_dict("records")  # placeholder: list of dicts [{"Parameter":..., "Value":...}]

                return [table_data, sse_fig]
            return [dash.no_update, dash.no_update]
        except Exception as e:
            print(f"Error: {str(e)}")
            return [dash.no_update, dash.no_update]
    
    @app.callback(
    Output("new-fit-graph", "figure"),
    [Input("add-new-fit-btn", "n_clicks"), Input("clear-btn", "n_clicks"), Input("lambda-slider", "value"), Input("yield-curve-store", "data"), Input("date-picker", "date")],
    [State("new-fit-graph", "figure")]
    )
    def add_line(n1, n2, lmbda, raw_data, selected_date, existing_fig):
        try:
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            if not raw_data:
                return [dash.no_update, dash.no_update]
            df = pd.DataFrame(raw_data)
            data = df.set_index("DATE")            
            if "add-new-fit-btn" in changed_id:
                nsf = fitted_curve_details(data=data, selected_date=selected_date)
                fig = go.Figure(existing_fig)
                new_fig = nsf.add_lambda_trace(lmbda=lmbda, fig=fig)
                return new_fig
            if "clear-btn" in changed_id:
                nsf = fitted_curve_details(data=data, selected_date=selected_date)                
                base_fig = nsf.base_yield_plot()
                datestr = pd.to_datetime(selected_date).strftime("%Y-%m-%d")
                base_fig.update_layout(
                    xaxis_title="Maturity (years)",
                    yaxis_title="Yield",
                    template="plotly_white",
                    title=dict(text=f"Nelson–Siegel Yield Curve (As of {datestr})", x=0.5, xanchor="center"),
                )
                return base_fig            
            return dash.no_update
        except Exception as e:
            print(f"Error: {str(e)}")
            return dash.no_update

        

    return app
