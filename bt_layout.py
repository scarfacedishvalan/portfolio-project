import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from texts import get_text_content
from bt_components import collapsible_inputs_bt, recipe_table, run_bt_row, asset_dropdown_bt, bt_button, graph, pivot_row, stats_table, metric_select_graph, metric_select_drowpdown, download_bt_graph

HEADINGS_DICT = {1: "Modern Portfolio Theory", 2: "Python bt package", 3: "bt Algos: Example",
                 4: "Backtesting Recipes: Introduction", 5: "Recipe Example", 6: "Recipe: Interpretation",
                 7: "Backtesting with NIFTY ETF Data", 8: "Backtesting Recipe", 9: "Asset Selection", 10: "Backtested Strategies Graph", 
                 11: "Overall Metrics", 12: "Transactions", 13: "Granular Metrics"
                 }
ALL_CARDS_DICT = {}

ALL_CARDS_DICT[1] = get_text_content("backtesting_1")
ALL_CARDS_DICT[2] = get_text_content("backtesting_2")
ALL_CARDS_DICT[3] = html.Div(children=[get_text_content("backtesting_3"), get_text_content("bt_algos_link") ])
ALL_CARDS_DICT[4] = html.Div(children=[get_text_content("backtesting_4")])
ALL_CARDS_DICT[5] = html.Code(children=[get_text_content("backtesting_4b")])
ALL_CARDS_DICT[6] = html.Div(children=[get_text_content("backtesting_4c"), get_text_content("iso_link")])
ALL_CARDS_DICT[7] = html.Div(children=[get_text_content("heading_bt"),  get_text_content("backtesting_4d"), get_text_content("asset_alloc_link"), ])
ALL_CARDS_DICT[8] = html.Div(children=[get_text_content("backtesting_5"), collapsible_inputs_bt, get_text_content("backtesting_5a"), recipe_table])
ALL_CARDS_DICT[9] = html.Div(children=[get_text_content("backtesting_6"), asset_dropdown_bt, html.Br(), bt_button])
ALL_CARDS_DICT[10] = html.Div(children=[get_text_content("backtesting_7"), html.Br(), download_bt_graph, html.Br(), html.Br(), graph])
ALL_CARDS_DICT[11] = html.Div(children=[get_text_content("backtesting_8"), stats_table])
ALL_CARDS_DICT[12] = html.Div(children=[get_text_content("backtesting_10"), pivot_row])
ALL_CARDS_DICT[13] = html.Div(children=[get_text_content("backtesting_11"), metric_select_drowpdown, html.Br(), metric_select_graph])


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    # "width": "24rem",
    "padding": "4rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Main content (dbc Cards)
heading =  dbc.Row(
            dbc.Col(
                html.H2(
                    "Backtesting Portfolio Optimization Strategies",
                    className="text-center bg-primary text-white p-2",
                ),
            ),
            style={ "width": "1800px", "height": "2000px"},
            className="h-100"
        )
all_cards = [heading]
table_of_contents = []
for i, cmp in ALL_CARDS_DICT.items():
    card = dbc.Card(
            dbc.CardBody(
                id = f"part{i}",
                children = [
                    dbc.Row([
                    # dbc.Col(),

                    # dbc.Col(cmp)
                        cmp
                    ])                
                ],
            #  style={ "width": "1800px", "height": "2000px"},                   
            ),
            style={ "width": "1800px", "height": "2000px"},
            className="h-100"
    )
    all_cards.append(card)
    bookmark = html.Li(html.A(HEADINGS_DICT[i], href=f"#part{i}"))
    table_of_contents.append(bookmark)

# Sidebar content (Table of Contents)
sidebar = html.Div(
    [

        html.H2("Table of Contents"),
        html.Ul(
            table_of_contents
        ),
        html.H3("NIFTY ETF Data"),
        html.Ul(
            html.Li(get_text_content("asset_alloc_link"))
        )
    ],
    style=SIDEBAR_STYLE,
    
)

main_content = dbc.Container(all_cards,
                             style=CONTENT_STYLE
                                # className="mt-4",
                            )

overall_bt_layout = [sidebar, main_content]