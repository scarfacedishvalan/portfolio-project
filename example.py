from bt_components import load_bt_graph
from json_recipe_handler import load_json_recipe, handle_recipe_dict, recipe_details_to_df
import constants as cts
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, ALL, no_update
import os
import pandas as pd
import plotly.graph_objects as go

def get_bt_graph():
    recipe_json = load_json_recipe("recipe.json")
    recipe = handle_recipe_dict(recipe_json)
    asset_list = cts.SELECTED_ASSETS
    figbt, datap, trdict, metrics_dict, dfstats = load_bt_graph(asset_list=asset_list, recipe=recipe, cache=True)
    graph =  dcc.Graph(id="bt-graph", figure = figbt)
    return graph

def plot_all_bt_results(data):
    fig = go.Figure()
    f = lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
    data["Date"] = data["Date"].apply(f)
    for strategy in list(data.columns)[1:]:
       fig.add_trace(go.Scatter(x=data["Date"], y=data[strategy], mode='lines', name=strategy))
    fig.update_layout(
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Value'),
                        showlegend=True,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), 
                        width = 800, height = 400
                    )
    return fig

if __name__ == "__main__":
    credential_path = "C:\\Users\\abhir\\Downloads\\stone-goal-401904-364eb9bc2e42.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    src = r"C:\Python\data\article_data\graph_data"
    for i in range(1, 5):
        recipe_name = f"rec{i}"
        # recipe_json = load_json_recipe(f"{recipe_name}.json")
        # recipe = handle_recipe_dict(recipe_json)
        # asset_list = cts.SELECTED_ASSETS
        # figbt, datap, trdict, metrics_dict, dfstats = load_bt_graph(asset_list=asset_list, recipe=recipe)
        # datap.to_csv(src + "/" + f"rec{i}_plotdata.csv", index = False)
        datap = pd.read_csv(src + "/" + f"rec{i}_plotdata.csv")
        figbt = plot_all_bt_results(datap)
        figbt.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), width = 800, height = 400)

        folder = r"C:\Python\data\article_data"
        figbt.write_html(folder + "/" + recipe_name + ".html")
    # dfstats.to_excel(folder + "/" + recipe_name + "_stats.xlsx", index = False)
    # get_bt_graph()
    b=2