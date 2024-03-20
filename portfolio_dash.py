# -*- coding: utf-8 -*-


from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import about

app_description = """
How does asset allocation affect portfolio performance?   Select the percentage of stocks, bonds and cash
 in a portfolio and see annual returns over any time period from 1928 to 2021.
"""
app_title = "Asset Allocation Visualizer"
app_image = "https://www.wealthdashboard.app/assets/app.png"

metas = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    {"property": "twitter:card", "content": "summary_large_image"},
    {"property": "twitter:url", "content": "https://www.wealthdashboard.app/"},
    {"property": "twitter:title", "content": app_title},
    {"property": "twitter:description", "content": app_description},
    {"property": "twitter:image", "content": app_image},
    {"property": "og:title", "content": app_title},
    {"property": "og:type", "content": "website"},
    {"property": "og:description", "content": app_description},
    {"property": "og:image", "content": app_image},
]

asset_dropdown_width = {"width": "80%"}
tooltip_styling={
        "always_visible": True,
        "placement": "bottom",
    }
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME],
    meta_tags=metas,
    title=app_title,
)

#  make dataframe from  spreadsheet:
df = pd.read_csv("historic.csv")

MAX_YR = df.Year.max()
MIN_YR = df.Year.min()
START_YR = 2007

# since data is as of year end, need to add start year
df = (
    pd.concat([df, pd.DataFrame([{"Year": MIN_YR - 1}])], ignore_index=True)
    .sort_values("Year", ignore_index=True)
    .fillna(0)
)

COLORS = {
    "cash": "#3cb521",
    "bonds": "#fd7e14",
    "stocks": "#446e9b",
    "inflation": "#cd0200",
    "background": "whitesmoke",
}

"""
==========================================================================
Markdown Text
"""

datasource_text = dcc.Markdown(
    """
    [Data source:](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)
    Historical Returns on Stocks, Bonds and Bills from NYU Stern School of
    Business
    """
)

asset_allocation_text = dcc.Markdown(
    """
> **Asset allocation** is one of the main factors that drive portfolio risk and returns.   Play with the app and see for yourself!

> Change the allocation to cash, bonds and stocks on the sliders and see how your portfolio performs over time in the graph.
  Try entering different time periods and dollar amounts too.
"""
)

learn_text = dcc.Markdown(
    """
    Past performance certainly does not determine future results, but you can still
    learn a lot by reviewing how various asset classes have performed over time.

    Use the sliders to change the asset allocation (how much you invest in cash vs
    bonds vs stock) and see how this affects your returns.

    Note that the results shown in "My Portfolio" assumes rebalancing was done at
    the beginning of every year.  Also, this information is based on the S&P 500 index
    as a proxy for "stocks", the 10 year US Treasury Bond for "bonds" and the 3 month
    US Treasury Bill for "cash."  Your results of course,  would be different based
    on your actual holdings.

    This is intended to help you determine your investment philosophy and understand
    what sort of risks and returns you might see for each asset category.

    The  data is from [Aswath Damodaran](http://people.stern.nyu.edu/adamodar/New_Home_Page/home.htm)
    who teaches  corporate finance and valuation at the Stern School of Business
    at New York University.

    Check out his excellent on-line course in
    [Investment Philosophies.](http://people.stern.nyu.edu/adamodar/New_Home_Page/webcastinvphil.htm)
    """
)

cagr_text = dcc.Markdown(
    """
    (CAGR) is the compound annual growth rate.  It measures the rate of return for an investment over a period of time, 
    such as 5 or 10 years. The CAGR is also called a "smoothed" rate of return because it measures the growth of
     an investment as if it had grown at a steady rate on an annually compounded basis.
    """
)

footer = html.Div(
    [
        dcc.Markdown(
            """
             This information is intended solely as general information for educational
            and entertainment purposes only and is not a substitute for professional advice and
            services from qualified financial services providers familiar with your financial
            situation.            
            """
        ),

    ],
    className="p-2 mt-5 bg-primary text-white small",
)

"""
==========================================================================
Tables
"""

total_returns_table = dash_table.DataTable(
    id="total_returns",
    columns=[{"id": "Year", "name": "Year", "type": "text"}]
    + [
        {"id": col, "name": col, "type": "numeric", "format": {"specifier": "$,.0f"}}
        for col in ["Cash", "Bonds", "Stocks", "Total"]
    ],
    page_size=15,
    style_table={"overflowX": "scroll"},
)

annual_returns_pct_table = dash_table.DataTable(
    id="annual_returns_pct",
    columns=(
        [{"id": "Year", "name": "Year", "type": "text"}]
        + [
            {"id": col, "name": col, "type": "numeric", "format": {"specifier": ".1%"}}
            for col in df.columns[1:]
        ]
    ),
    data=df.to_dict("records"),
    sort_action="native",
    page_size=15,
    style_table={"overflowX": "scroll"},
)


def make_summary_table(dff):
    """Make html table to show cagr and  best and worst periods"""

    table_class = "h5 text-body text-nowrap"
    cash = html.Span(
        [html.I(className="fa fa-money-bill-alt"), " Cash"], className=table_class
    )
    bonds = html.Span(
        [html.I(className="fa fa-handshake"), " Bonds"], className=table_class
    )
    stocks = html.Span(
        [html.I(className="fa fa-industry"), " Stocks"], className=table_class
    )
    inflation = html.Span(
        [html.I(className="fa fa-ambulance"), " Inflation"], className=table_class
    )

    start_yr = dff["Year"].iat[0]
    end_yr = dff["Year"].iat[-1]

    df_table = pd.DataFrame(
        {
            "": [cash, bonds, stocks, inflation],
            f"Rate of Return (CAGR) from {start_yr} to {end_yr}": [
                cagr(dff["all_cash"]),
                cagr(dff["all_bonds"]),
                cagr(dff["all_stocks"]),
                cagr(dff["inflation_only"]),
            ],
            f"Worst 1 Year Return": [
                worst(dff, "3-mon T.Bill"),
                worst(dff, "10yr T.Bond"),
                worst(dff, "S&P 500"),
                "",
            ],
        }
    )
    return dbc.Table.from_dataframe(df_table, bordered=True, hover=True)


"""
==========================================================================
Figures
"""


def make_pie(slider_input, title):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Cash", "Bonds", "Stocks"],
                values=slider_input,
                textinfo="label+percent",
                textposition="inside",
                marker={"colors": [COLORS["cash"], COLORS["bonds"], COLORS["stocks"]]},
                sort=False,
                hoverinfo="none",
            )
        ]
    )
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        margin=dict(b=25, t=75, l=35, r=25),
        height=325,
        paper_bgcolor=COLORS["background"],
    )
    return fig


def make_line_chart(dff):
    start = dff.loc[1, "Year"]
    yrs = dff["Year"].size - 1
    dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_cash"],
            name="All Cash",
            marker_color=COLORS["cash"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_bonds"],
            name="All Bonds (10yr T.Bonds)",
            marker_color=COLORS["bonds"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_stocks"],
            name="All Stocks (S&P500)",
            marker_color=COLORS["stocks"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Total"],
            name="My Portfolio",
            marker_color="black",
            line=dict(width=6, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["inflation_only"],
            name="Inflation",
            visible=True,
            marker_color=COLORS["inflation"],
        )
    )
    fig.update_layout(
        title=f"Returns for {yrs} years starting {start}",
        template="none",
        showlegend=True,
        legend=dict(x=0.01, y=0.99),
        height=400,
        margin=dict(l=40, r=10, t=60, b=55),
        yaxis=dict(tickprefix="$", fixedrange=True),
        xaxis=dict(title="Year Ended", fixedrange=True, dtick=dtick),
    )
    return fig


"""
==========================================================================
Make Tabs
"""

# =======Play tab components

asset_allocation_card = dbc.Card(asset_allocation_text, className="mt-2")

def get_slider_card(assetlist, values = None):
    slider_list = []
    if values is None:
        values = [100/len(assetlist)]*len(assetlist)
    for i, asset in enumerate(assetlist):
            header = html.H5(f"Allocation for {asset}", className="card-title")
            slider_list.append(header)
            sld =         dcc.Slider(
                id={"type": "weight-slider", "index": i},
                # marks={i: f"{i}%" for i in range(0, 101, 10)},
                min=0,
                max=100,
                # step=5,
                value=values[i],
                included=False,
                tooltip=tooltip_styling
            )
            slider_list.append(sld)
    return slider_list, values

# slider_card = dbc.Card(
#     [
#         html.H4("First set cash allocation %:", className="card-title"),
#         dcc.Slider(
#             id="cash",
#             marks={i: f"{i}%" for i in range(0, 101, 10)},
#             min=0,
#             max=100,
#             step=5,
#             value=10,
#             included=False,
#         ),
#         html.H4(
#             "Then set stock allocation % ",
#             className="card-title mt-3",
#         ),
#         html.Div("(The rest will be bonds)", className="card-title"),
#         dcc.Slider(
#             id="stock_bond",
#             marks={i: f"{i}%" for i in range(0, 91, 10)},
#             min=0,
#             max=90,
#             step=5,
#             value=50,
#             included=False,
#         ),
#     ],
#     body=True,
#     className="mt-4",
# )

asset_dropdown = dcc.Dropdown(
    id="asset_dropdown",
    options=[{"label": asset, "value": asset} for asset in ["MOM100", "NIFTYBEES", "Asset3"]],
    value=["MOM100", "NIFTYBEES"],  # Set default selected assets
    multi=True,
     style=asset_dropdown_width,
)

slider_card = html.Div(
     children = [
    asset_dropdown, 
    html.Br(),
    # get_slider_card(["MOM100", "NIFTYBEES"]),
    html.Div(id="slider_div", children=[]),] 
    # body=True,
    # className="mt-4",
)


# ======= InputGroup components

input_groups = html.Div(
    [start_amount, start_year, number_of_years, end_amount, rate_of_return],
    className="mt-4 p-4",
)


# ========= Build tabs
tabs = dbc.Tabs(
    [
        # dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
        dbc.Tab(
            [asset_allocation_text, slider_card, 
             html.Div(id = "sum_value"),
            #  input_groups, time_period_card
             ],
            tab_id="tab-2",
            label="Asset Allocation Analysis",
            className="pb-4",
        ),
        # dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"),
    ],
    id="tabs",
    active_tab="tab-2",
    className="mt-2",
)


"""
===========================================================================
Main Layout
"""

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Asset Allocation Visualizer",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            [
                dcc.Store(id='weights-sum'),
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
                dbc.Col(
                    [
                        dcc.Graph(id="allocation_pie_chart", className="mb-2"),
                        dcc.Graph(id="returns_chart", className="pb-4"),
                        html.Hr(),
                        html.Div(id="summary_table"),
                        html.H6(datasource_text, className="my-2"),
                    ],
                    width=12,
                    lg=7,
                    className="pt-4",
                ),
            ],
            className="ms-1",
        ),
        dbc.Row(dbc.Col(footer)),
        # dbc.Row(dbc.Col(about.card, width="auto"), justify="center")
    ],
    fluid=True,
)


"""
==========================================================================
Callbacks
"""

@app.callback(
    Output("slider_div", "children"),
    Input("asset_dropdown", "value")
)
def update_slider_div(selected_assets):
    if selected_assets is None or not selected_assets:
        return no_update
    sliders, values = get_slider_card(selected_assets)
    return sliders

@app.callback(
    Output("weights-sum", "data"),  # Update the HTML div containing sliders
    Input({"type": "weight-slider", "index": ALL}, "value"),  # State to capture all slider values
)
def update_sliders(current_values):
    # Calculate the current sum of slider values
    print(current_values)
    current_sum = sum(current_values)

    # # Calculate the adjustment factor
    # adjustment_factor = 100 / current_sum if current_sum != 0 else 0

    # # Adjust each slider value based on the factor
    # adjusted_values = [value * adjustment_factor for value in current_values]

    # # Update the sliders with the adjusted values
    # sliders = get_slider_card(selected_assets, adjusted_values)

    return current_sum

@app.callback(
    Output("sum_value", "children"),
    Input("weights-sum", "data"),
)
def update_slider_div(current_sum):
    if not current_sum:
        return ""
    if current_sum != 100:
        return f"Total sum is not 100, readjust!"
    else:
        return ""

# @app.callback(
#     Output("allocation_pie_chart", "figure"),
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
# )
# def update_pie(stocks, cash):
#     bonds = 100 - stocks - cash
#     slider_input = [cash, bonds, stocks]

#     if stocks >= 70:
#         investment_style = "Aggressive"
#     elif stocks <= 30:
#         investment_style = "Conservative"
#     else:
#         investment_style = "Moderate"
#     figure = make_pie(slider_input, investment_style + " Asset Allocation")
#     return figure


# @app.callback(
#     Output("stock_bond", "max"),
#     Output("stock_bond", "marks"),
#     Output("stock_bond", "value"),
#     Input("cash", "value"),
#     State("stock_bond", "value"),
# )
# def update_stock_slider(cash, initial_stock_value):
#     max_slider = 100 - int(cash)
#     stocks = min(max_slider, initial_stock_value)

#     # formats the slider scale
#     if max_slider > 50:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 10)}
#     elif max_slider <= 15:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 1)}
#     else:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 5)}
#     return max_slider, marks_slider, stocks


# @app.callback(
#     Output("planning_time", "value"),
#     Output("start_yr", "value"),
#     Output("time_period", "value"),
#     Input("planning_time", "value"),
#     Input("start_yr", "value"),
#     Input("time_period", "value"),
# )
# def update_time_period(planning_time, start_yr, period_number):
#     """syncs inputs and selected time periods"""
#     ctx = callback_context
#     input_id = ctx.triggered[0]["prop_id"].split(".")[0]

#     if input_id == "time_period":
#         planning_time = time_period_data[period_number]["planning_time"]
#         start_yr = time_period_data[period_number]["start_yr"]

#     if input_id in ["planning_time", "start_yr"]:
#         period_number = None

#     return planning_time, start_yr, period_number


# @app.callback(
#     Output("total_returns", "data"),
#     Output("returns_chart", "figure"),
#     Output("summary_table", "children"),
#     Output("ending_amount", "value"),
#     Output("cagr", "value"),
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
#     Input("starting_amount", "value"),
#     Input("planning_time", "value"),
#     Input("start_yr", "value"),
# )
# def update_totals(stocks, cash, start_bal, planning_time, start_yr):
#     # set defaults for invalid inputs
#     start_bal = 10 if start_bal is None else start_bal
#     planning_time = 1 if planning_time is None else planning_time
#     start_yr = MIN_YR if start_yr is None else int(start_yr)

#     # calculate valid planning time start yr
#     max_time = MAX_YR + 1 - start_yr
#     planning_time = min(max_time, planning_time)
#     if start_yr + planning_time > MAX_YR:
#         start_yr = min(df.iloc[-planning_time, 0], MAX_YR)  # 0 is Year column

#     # create investment returns dataframe
#     dff = backtest(stocks, cash, start_bal, planning_time, start_yr)

#     # create data for DataTable
#     data = dff.to_dict("records")

#     # create the line chart
#     fig = make_line_chart(dff)

#     summary_table = make_summary_table(dff)

#     # format ending balance
#     ending_amount = f"${dff['Total'].iloc[-1]:0,.0f}"

#     # calcluate cagr
#     ending_cagr = cagr(dff["Total"])

#     return data, fig, summary_table, ending_amount, ending_cagr


if __name__ == "__main__":
    app.run_server(debug=True)