# Portfolio Optimisation and Backtesting with Dash and bt Algos

A Plotly Dash based implementation of bt algos.

### Why?

Here’s a simple question: How would you implement and backtest a portfolio optimisation strategy given raw price data for different assets. If we narrow the scope of the question to Python, there are two key components we desperately need:

* An Optimiser: Takes price data as input and spits out weight allocations for each asset

* A backtesting framework: A comprehensive set of functions/methods that allow the user to actually implement the allocation on different rebalance dates and visualise the results. Additionally, we should be able to see the granular details of the allocations, like transactions done for each asset to achieve the target weights, the value of the assets and the overall portfolio and ultimately, the performance metrics.

Fortunately for Quantitative Analysts, we have Philippe Morissette who developed two key packages: ffn and more importantly, bt which is an immensely powerful backtesting framework. The bt package provides a very flexible and seamless way to achieve the above two with its rich library of algorithms (bt.Algos). The implementation of each algo is very simple, it has a target, meaning the input data and the algorithm ultimately assigns weights to the assets in a temp variable. So creating your own algo is ridiculously easy as long as we assign the weights at the end of it. For a quickstart guide refer: https://pmorissette.github.io/bt/

## Recipes

 Create the full HTML string of the app, to be easily read by crawlers and search engines.
* Does not convert `dcc` components (charts, dropdowns, date pickers, etc.) saving on performance because these components can be heavy without much content, especially charts.
* Title tag, and meta tags are already supported by Dash, and you can set these using default Dash.

## Example

Every good coder appreciates the importance of a config driven approach to implementation. It allows the user to experiment with various types of inputs without making too many changes to the codebase. If we would like to implement multiple bt Algos strategies on a piece of data and most importantly, compare them, we might have to write repetitive bits of code to compile and visualise the results. To be fair, bt algos does support multiple strategy run in a very intuitive manner, I have tried a different approach of creating a recipe: a json based config that allows users to easily manipulate the parameters of any strategy. Below is a simple example of the WeighMeanVar strategy being implemented, which is basically sharpe ratio minimisation.


```json
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

## Interpreting the recipe?

WeighMeanStrategy is the name of a strategy chosen by user. The overall recipe can have multiple such strategies with different underlying params.

rebalance_freq: As the name suggests this decides how often the portfolio will be rebalanced. Choose among: RunYearly, RunMonthly, RunQuarterly, RunWeekly, RunDaily. Custom periods are not yet supported.

select: Specifies the assets to select from the data being backtested.

RunAfterDate: Date after which the strategy is implemented

optimiser: Most important parameter! The name is the bt Algos optimiser (choose any from documentation) and the args is the paramters being passed to the optimiser. Now here’s the steroid boost we provide in our implementation: if you pass a list of values in a parameter, multiple strategies will be implemented with the different combinations. 
Please note that although the lookbacks are passed as pandas date offsets typically in bt Algos, for json implementation purposes we pass a string based on the ISO 8601 duration format.

For more info on bt Algos and different alogorithms available for experimentation, visit: https://pmorissette.github.io/bt/algos.html

### Inputs

* Raw Price data: csv files on gcloud in this case for different assets, selected from dropdown
* Json Recipe: In a collapsible component with a dbc Input component.

### Outputs
* Porfolio Value Graph

![Alt text](readme_images\portfolio_graph.png?raw=true "Optional Title")

### Outputs
## Hosted Link

So here’s where the rubber meets the road: [optimarkov.com](https://optimarkov.com/). This is an admittedly quite ugly looking web app where I implemented the above ideas in Plotly Dash and put it to test publicly. The raw data is India’s top Exchange Traded Funds (no reason except for my love for them) and users can tinker with their own recipes. Since the development, testing and deployment team has a total size of one: me, there will be buggy edge cases, which I’ll be happy to address. Whether you’re a seasoned trader or just someone with an academic curiosity for portfolio strategies, I believe this app has a little something for everyone. If not, please marvel at the modern art inspired frontend!