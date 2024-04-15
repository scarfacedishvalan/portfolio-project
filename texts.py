from dash import dcc, html
import dash_bootstrap_components as dbc

DEFAULT_TEXT_STYLING = {
        "fontSize": 18,
        "padding": 15,
        "text-align": "justify",
        # 'border-bottom':'solid black 1px',
        "text-indent": 30,
        'width':'80%',
    }

ALL_TEXT_DICT = dict(

        asset_allocation_1 = dcc.Markdown(
            """
        ### Asset Allocation and Weighed Portfolios
        Asset allocation is the strategic distribution of investments among various asset classes such as stocks, bonds, and cash. It aims to balance risk and return by diversifying across different types of assets. 
        Weighted portfolios further refine this approach by assigning specific proportions to each asset class based on factors like risk tolerance, time horizon, and investment objectives. By adjusting these weights, investors can tailor their portfolios to align with their financial goals and preferences. 
        The goal is to achieve optimal risk-adjusted returns while minimizing exposure to undue market volatility. 
        """
        ),

        asset_allocation_1b = dcc.Markdown(
            """
        ### NIFTY ETF Price Data        
        ETFs, or Exchange-Traded Funds, are investment funds traded on stock exchanges, much like individual stocks. They typically hold a diversified portfolio of assets such as stocks, bonds, commodities, or a combination thereof. ETFs offer investors exposure to a wide range of assets in a single investment, providing diversification and liquidity. They are designed to track the performance of an underlying index or asset class, offering transparency and low costs compared to traditional mutual funds. 
        ETFs can be bought and sold throughout the trading day at market prices, making them a flexible and efficient investment vehicle for both retail and institutional investors. The underlying data for this app is sourced from > 30 ETFs traded on NIFTY, where the underlyings vary from top 50 market caps, midcaps, gold and many other sectoral indexes.

        > To play with your portfolio, select assets from the dropdown below to view the actual historical Close data for the selected assets. 
        """
        ),
        asset_allocation_1c = dcc.Markdown(
            """

        Choose the assets from the dropdown and from the generated sliders, change the allocation to different assets on the sliders and see how your portfolio performs over time in the graph. The weights must add up to 100, failing which an error will be thrown.
          Click the update weights button to refresh the graph after changing the weights

        """
        ),

        asset_allocation_2 = dcc.Markdown(
            """
            The graph represents the value of the weighted portfolio based on the weights chosen above. Use the show assets toggle button to show the value of the assets as well over time. Please note the points in the graph represent the value over time for an amount of 100 invested initially.

            """
        ),
        asset_allocation_3 = dcc.Markdown(
            """
            Below is the statistical summary of the performance of the weighted portfolio along with the assets.
            
            """
        ),
        backtesting_1 =  dcc.Markdown(
        """
### Modern Portfolio Theory
> **Portfolio optimization** using Modern Portfolio Theory (MPT), notably Markowitz's approach, aims to construct balanced investment portfolios maximizing returns for a given risk level. 
It involves defining objectives, selecting assets, estimating returns and risks, analyzing correlations, and optimizing asset allocation mathematically. 

> By diversifying across assets with low correlations, MPT helps reduce overall portfolio risk without sacrificing potential returns. It offers a systematic and quantitative framework for decision-making, grounded in statistical analysis. The efficient frontier concept identifies optimal portfolios that offer the highest expected return for a given risk or the lowest risk for a given return. Regular monitoring and rebalancing are essential to maintain the portfolio's desired risk-return profile. 
MPT provides investors with a powerful tool to achieve efficient and effective investment outcomes, aligning portfolios with individual preferences and objectives.
        """
    ),
        backtesting_2 =  dcc.Markdown(
        """
        ### Backtesting in Python: bt
        **bt** is a flexible backtesting framework for Python used to test quantitative trading strategies. Backtesting is the process of testing a strategy over a given data set. This framework allows you to easily create strategies that mix and match different Algos. It aims to foster the creation of easily testable, re-usable and flexible blocks of strategy logic to facilitate the rapid development of complex trading strategies.

        **The goal**: to save quants from re-inventing the wheel and let them focus on the important part of the job - strategy development. bt is coded in Python and joins a vibrant and rich ecosystem for data analysis. Numerous libraries exist for machine learning, signal processing and statistics and can be leveraged to avoid re-inventing the wheel - something that happens all too often when using other languages that don’t have the same wealth of high-quality, open-source projects.
        """
    ),

    backtesting_3 =  dcc.Markdown(
        """
        ### Example: bt Algos Implementation

        Let’s create a simple strategy. We will create a monthly rebalanced, long-only strategy where we place equal weights on each asset in our universe of assets.
        ```
        data = bt.get('spy,agg', start='2010-01-01')
        ```
        Once we have our data, we will create our strategy. The Strategy object contains the strategy logic by combining various Algos.
        ```
        s = bt.Strategy('s1', [bt.algos.RunMonthly(),
                            bt.algos.SelectAll(),
                            bt.algos.WeighEqually(),
                            bt.algos.Rebalance()])
        ```
        We will then create a Backtest, which is the logical combination of a strategy with a data set.

        ```
        test = bt.Backtest(s, data)

        ```
        Finally, we run the backtest to obtain the results. 

        ```
        res = bt.run(test)
        ```
        """),

        backtesting_4 =  dcc.Markdown(
        """
        ### Backtesting implementation in this app: A recipe driven approach
        Utilisiing the powerful base provided by bt Algos, this app provides the user to run multiple strategies with varying parameters on a set of pricing data. The pricing data (as displayed in the asset allocation tab) 
        is the daily price data of chosen ETFs traded on India's NSE NIFTY. 
        
        The user inputs an intuitive json recipe that typically looks like this:
        """
        ),

        backtesting_4b =  dcc.Markdown(
        """
        ```
        {
        "WeighMeanStrategy": 
            {
                "rebalance_freq": "RunYearly",
                "select": "all",
                "RunAfterDate": "2015-12-24",
                "optimiser":
                            {
                                "name": "WeighMeanVar",
                                "args": {
                                    "lookback" : "P3Y",
                                "covar_method" : "standard"
                                }
                            },
                "rebalance": true

            },
        }
        ``` 
        """ ),

        backtesting_4c =  dcc.Markdown(
        """
        #### Interpreting the recipe

        * ***WeighMeanStrategy*** is the name of a strategy chosen by user. The overall recipe can have multiple such strategies with different underlying params.
        * ***rebalance_freq***: As the name suggests this decides how often the portfolio will be rebalanced. Choose among: RunYearly, RunMonthly, RunQuarterly, RunWeekly, RunDaily. Custom periods are not yet supported. 
        * ***select***: Specifies the assets to select from the data being backtested.
        * ***RunAfterDate***: Date after which the strategy is implemented
        * ***optimiser***: Most important parameter! The ***name*** is the bt Algos optimiser (choose any from documentation) and the ***args*** is the paramters being passed to the optimiser. The enhancement here is if you pass a list of values in 
           a parameter, multiple strategies will be implemented with the different combinations. For example if we pass the following in optimiser:

           ```
              "optimiser":
                            {
                                "name": "WeighMeanVar",
                                "args": {
                                    "lookback" : ["P3Y", "P2Y"],
                                "covar_method" : "standard"
                                }
                            },
           ```
           The strategy runner will internally convert the above into two strategies: WeighMeanStrategy.1 and WeighMeanStrategy.2 which will run independently with the two lookbacks.
        
        * Although the lookbacks are passed as pandas date offsets typically in bt Algos, for json implementation purposes we pass a string based on the  ISO 8601 duration format. 
        """
    ),

    iso_link = html.Div([
    html.A("About the ISO 8601 duration format", href='https://www.digi.com/resources/documentation/digidocs/90001488-13/reference/r_iso_8601_duration_format.htm', target="_blank")
]),

bt_algos_link = html.Div([
    html.A("bt Algos API reference", href='https://pmorissette.github.io/bt/bt.html', target="_blank")
]),

# asset_alloc_link = dcc.Link('See Pricing Data', href='/assetalloc'),
asset_alloc_link = html.A("Asset Allocation", href="/assetalloc", target = "_blank"),
heading_bt = html.H3("Backtesting with NIFTY ETF Data", style={'textAlign': 'center'}),
redirect_home =  html.A("Backtesting App", href="/"),
backtesting_4d = dcc.Markdown(
        """
        The underlying data for this app is sourced from > 30 ETFs traded on NIFTY, where the underlyings vary from top 50 market caps, midcaps, gold and many other sectoral indexes. To see what the actual input ETF data looks like, click the below link to open the asset allocation visualiser.
        """
    ),
backtesting_5 = dcc.Markdown(
        """
        Now we will perform backtests on actual NIFTY ETF data using the recipe method described above.
        Expand the collapsible component below and edit the json recipe. Once done, click ***Validate Recipe*** button to check if all the parameters are entered correctly. If not a message will be displaed indicating error.
        
        > To see what the actual input ETF data looks like, click the below link to open the asset allocation visualiser.
        """
    ),

backtesting_5a = dcc.Markdown(
        """
         ### Recipe Table
        This table indicates the different strategies, the optimisers and arguments that will run. This is based on the interpretation of the json recipe as described above.
        """
    ),
backtesting_6 = dcc.Markdown(
        """
        ### Choose Assets
        Choose a list of assets you want to select for backtesting purposes. The backtest will be run on period where data is available. Once chosen, click ***Run Backtest*** to inititate the backtesting procedure.
        """
    ),

backtesting_7 = dcc.Markdown(
        """
        ### Backtested Portfolio Value graph

        This graph represents the value of portfolio, assuming an initial investment of 100, that is then used to invest in the basket of assets chosen. The performance of different strategies is shown in different colours.
        """
    ),

backtesting_8 = dcc.Markdown(
        """
        ### Overall Statistical Summary
        To properly evaluate the performance of each strategy, the below table lists out various metrics like CAGR, calmar ratio, maximum drawdown and many others that indicate how well a strategy has performed.
        """
    ),

backtesting_9 = dcc.Markdown(
        """
        ### Monthly Returns
        Below are heatmaps of monthly returns for each strategy along with an YTD value to assess the performances in a more granular way.
        """
    ),
backtesting_10 = dcc.Markdown(
        """
        ### Transations for rebalance
        Below is the pivot table with the data for the transaction that happen during rebalance for each strategy. The user can analyse dates of rebalance, asset prices, weights, portfolio values and their combinations using this pivot table.
        """
    ),

backtesting_11 = dcc.Markdown(
        """
        ### Monthly Return Heatmaps and Drawdowns
        > ***Monthly returns*** are helpful in analyzing portfolio performance as they offer insights into the fluctuations and trends over shorter time intervals. By examining monthly returns, investors can assess the effectiveness of their investment strategies, identify patterns and seasonality, if any. 
        These returns provide a granular view of portfolio performance.

        > A ***Drawdown*** in the context of portfolio performance refers to the decline in the value of an investment from its peak to its subsequent trough. 
        It represents the extent of loss experienced by an investment or portfolio during a specific period. Monitoring drawdowns allows investors to assess the resilience of their portfolios during market downturns and turbulent periods. By understanding the magnitude and duration of drawdowns, investors can gauge the potential downside exposure of their investments and make informed decisions to mitigate risk.
        Drawdown analysis helps investors set realistic expectations, manage their risk tolerance, and adjust their investment strategies accordingly.
        
        > Select strategy and respective metric (monthly returns/drawdowns) from the dropdowns below to check the strategy performance based on these metrics.
        """
    )


 )

def get_text_content(text_id, **kwargs):
    return html.Div(
    [
        ALL_TEXT_DICT[text_id]       
    ],
    style= DEFAULT_TEXT_STYLING,
    )