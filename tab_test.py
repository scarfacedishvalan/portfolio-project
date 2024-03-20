#in addition to import pandas as pd & from dash import html:
import numpy as np
from dash import html
import pandas as pd
from json_recipe_handler import strategy_runner, load_json_recipe
from data_fetch import PriceData

table_style = {'border': '1px solid'}
header_section_style = {'border': '2px solid'}
body_section_style = {'border': '2px solid'}
body_index_cell_style = {'text-align': 'left',
                    'border':'1px solid',
                    'backgroundColor': 'rgb(210, 210, 255)',
                    'valign':'top',
                    'font-weight': 'bold'}
body_column_cell_style = {'text-align': 'right',
                     'border':'1px solid grey',
                     'backgroundColor': 'rgb(210, 255, 210)'}
header_index_cell_style = {'text-align': 'left',
                    'border':'2px solid',
                    'backgroundColor': 'rgb(165, 165, 255)',
                    'valign':'top',
                    'font-weight': 'bold'}
header_column_cell_style = {'text-align': 'right',
                     'border':'2px solid',
                     'backgroundColor': 'rgb(165, 255, 165)',
                     'font-weight': 'bold'}
def multiindex_table(df):
    # storing rowSpan values for every cell of index;
    # if rowSpan==0, html item is not going to be included
    pos = np.diff(df.index.codes, axis=1, prepend=-1)
    for row in pos:
        counts = np.diff(np.flatnonzero(np.r_[row, 1]))
        row[row.astype(bool)] = counts

    # filling up header of table;
    column_names = df.columns.values
    headTrs = html.Tr([html.Th(n, style=header_index_cell_style) for n in df.index.names] +
                      [html.Th(n, style=header_column_cell_style) for n in column_names])
    # filling up rows of table;
    bodyTrs = []
    for rowSpanVals, idx, col in zip(pos.T, df.index.tolist(), df.to_numpy()):
        rowTds = []
        for name, rowSpan in zip(idx, rowSpanVals):
            if rowSpan != 0:
                rowTds.append(html.Td(name, rowSpan=rowSpan, style=body_index_cell_style))
        for name in col:
            rowTds.append(html.Td(name, style=body_column_cell_style))
        bodyTrs.append(html.Tr(rowTds))

    table = html.Table([
        html.Thead(headTrs, style=header_section_style),
        html.Tbody(bodyTrs, style=body_section_style)
    ], style=table_style)
    return table

import dash
app = dash.Dash(__name__)
d = {'Full':
    {'Lithuania':
         {'Aukštaitija': ('Panevėžys',	'6.3°C'),
          'Žemaitija': ('Telšiai', '5.9°C'),
          'Dzūkija': ('Alytus', '6.4°C'),
          'Suvalkija': ('Marijampolė', 'No data'),
          'Mažoji Lietuva': ('Tilžė', '8.2°C')},
     'Latvia':
         {'Kurzeme': ('Jelgava', '7.1°C'),
          'Zemgale': ('Jelgava', '7.1°C'),
          'Vidūmō': ('Riga', '6.1°C'),
          'Latgale': ('Daugavpils', '5.5°C')}
    },
    'Short':
    {'Lithuania':
         {'Aukštaitija': ('Panevėžys',	'6.3°C'),
          'Žemaitija': ('Telšiai', '5.9°C'),
          'Dzūkija': ('Alytus', '6.4°C'),
          'Suvalkija': ('Marijampolė', 'No data')},
     'Latvia':
         {'Kurzeme & Zemgale': ('Jelgava', '7.1°C'),
          'Vidūmō': ('Riga', '6.1°C'),
          'Latgale': ('Daugavpils', '5.5°C')}
    },
    }
recipe = load_json_recipe("recipe.json")
pricedata = PriceData()
chosen_assets = ["NIFTYBEES", "CPSEETF", "JUNIORBEES", "MON100", "MOM100", "CONSUMBEES"]
bnds = ((0.1, 1), (0.05, 1), (0.05, 0.5), (0.05, 0.5), (0.1, 0.5), (0.05, 1))
# pbtest = PortfolioBtest(pricedata, chosen_assets=chosen_assets, bounds=bnds)

# df_shares_opt_all = pbtest.get_backtest_data(target_returns=0.1)

# data = bt.get('spy,agg', start='2010-01-01')
data = pricedata._dfraw[chosen_assets]
# Run strategies
res = strategy_runner(data=data, json_file_path="recipe.json")
df = res.get_transactions()
df.index = df.index.set_levels(df.index.levels[0].strftime('%Y-%m-%d'), level=0)
a=2
# df = pd.concat([pd.concat([pd.DataFrame(d2).T for d2 in d1.values()],
#                                 keys=d1.keys()) for d1 in d.values()],
#                      keys=d.keys())

# df.index.set_names(['Portion', 'Country', 'Cultural Region'], inplace=True)
# df.columns = ['Capital', 'Average Temperature']
app.layout = multiindex_table(df)
if __name__ == '__main__':
    app.run_server(debug=True)