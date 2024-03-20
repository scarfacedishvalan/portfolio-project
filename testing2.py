import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import plotly.express as px
from data_fetch import PriceData
from portfolio_backtest import PortfolioBtest
from portfolio_optimizer import PortfolioOptimizer
from algo_optimiser import MPTOptimiser

chosen_assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"]
bnds = ((0.1, 1), (0.05, 1), (0.05, 0.5), (0.05, 0.5), (0.1, 0.5), (0.05, 1))
# pbtest = PortfolioBtest(pricedata, chosen_assets=chosen_assets, bounds=bnds)

# df_shares_opt_all = pbtest.get_backtest_data(target_returns=0.1)

# data = bt.get('spy,agg', start='2010-01-01')
pd2 = PriceData(asset_list=chosen_assets)
pbtest = PortfolioBtest(pricedata_obj=pd2)
res = pbtest.get_buy_and_hold_results()
data_df = res["weighed"].__dict__["return_table"].round(2)
# Sample data for the heatmap
z_data = np.random.rand(10, 10)

# Create a Dash app
app = dash.Dash(__name__)
data=data_df.values
fig = px.imshow(data,
                labels=dict(x="Year", y="Month", color="Returns"),
                x=list(data_df.columns),
                y=list(data_df.index),
                text_auto=True,
                color_continuous_scale='RdYlGn'
               )
fig.update_xaxes(side="top")
# Define the layout
app.layout = html.Div([
    dcc.Graph(
        id='heatmap',
        figure=fig,
        style={'width': '800px', 'height': '600px'}
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
