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
                    'minWidth': 140,
                    'font-weight': 'bold'}
body_column_cell_style = {'text-align': 'right',
                     'border':'1px solid grey',
                     'backgroundColor': 'rgb(210, 255, 210)',
                     'minWidth': 120}
header_index_cell_style = {'text-align': 'left',
                    'border':'2px solid',
                    'backgroundColor': 'rgb(165, 165, 255)',
                    'valign':'top',
                    'minWidth': 140,
                    'font-weight': 'bold'}
header_column_cell_style = {'text-align': 'right',
                     'border':'2px solid',
                     'backgroundColor': 'rgb(165, 255, 165)',
                     'font-weight': 'bold',
                     'minWidth': 120}
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