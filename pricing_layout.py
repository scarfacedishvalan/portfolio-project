import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from texts import get_text_content
from alloc_components import asset_dropdown, update_section, pfolio_graph, stats_placeholder, slider_section, raw_graph, raw_data_dropdown

HEADINGS_DICT = {1: "Asset Allocation", 2: "NIFTY ETF Raw Data", 3: "Choose assets and weights", 
                 4: "Portfolio value graph", 5: "Summary stats" 
                 }
ALL_CARDS_DICT = {}

ALL_CARDS_DICT[1] = html.Div(children=[get_text_content("asset_allocation_1")])
ALL_CARDS_DICT[2] = html.Div(children=[get_text_content("asset_allocation_1b"), raw_data_dropdown, raw_graph]) #
ALL_CARDS_DICT[3] = html.Div(children= [get_text_content("asset_allocation_1c"), asset_dropdown] + slider_section)
ALL_CARDS_DICT[4] = html.Div(children=[get_text_content("asset_allocation_2"), pfolio_graph])
ALL_CARDS_DICT[5] = html.Div(children=[get_text_content("asset_allocation_3"), stats_placeholder])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    # "width": "24rem",
    "padding": "2rem 1rem",
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
                    "Asset Allocation Visualisation",
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
        dcc.Store(id='weights-sum'),
       
        dcc.Store(id="store-assets-weights", data=[]),
        dcc.Store(id="weights-correct-bool", data=False),
        html.Div(children = [get_text_content("redirect_home")]),
        html.Br(),
        html.H2("Table of Contents"),
        html.Ul(
            table_of_contents
        ),
    ],
    style=SIDEBAR_STYLE,
    
)

main_content = dbc.Container(all_cards,
                             style=CONTENT_STYLE
                                # className="mt-4",
                            )

overall_pricing_layout = [sidebar, main_content]