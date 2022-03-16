# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:49:50 2021

@author: Andrew
Study the correlation between any stock.
Use environment, baba_stock_study

Tested on Spyder, Python 3.8

Requirements: 
    yfinance
    scipy
    pandas
    plotly
"""
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

import yfinance as yf
from scipy.stats import pearsonr
import pandas as pd

import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
app = Dash(__name__)
def download_stock_data(ticker, start_date, end_date, ticker_option = "Open", interval ="1d"):
    stock = yf.Ticker(ticker)
    df = stock.history(start = start_date, end = end_date, interval = interval)
    return df 

def process_stock_data(ticker1, ticker2, stock1_historical, stock2_historical, ticker1_option = "Open",  ticker2_option= "Open"):
    ## Filter pandas dataframes based on trading days; NYSE has more trading days and different holidays compared to HKEX. 
    # Only compare common days. 
    stock1_date = stock1_historical.index
    stock2_date = stock2_historical.index
    remove_extra_1 = stock1_date.difference(stock2_date)
    remove_extra_2 = stock2_date.difference(stock1_date)
    final_stock1 = stock1_historical.drop(remove_extra_1)
    final_stock2 = stock2_historical.drop(remove_extra_2)
    #Merge final data into one pd.df
    

    final_data={f'{ticker1}_{ticker1_option}': final_stock1[ticker1_option], f'{ticker2}_{ticker2_option}'
                : final_stock2[ticker2_option]}
    df=pd.DataFrame(final_data, index= final_stock1.index)
    return df

def calculate_correlations(ticker1, ticker2, stock1, stock2, stock1_option= "Open", stock2_option = "Open", rolling_window = 20):
    corr, _ = pearsonr(stock1[stock1_option], stock2[stock2_option])
    print(f"Correlation between {ticker1} and {ticker2} is {corr:.3f}.")
    return corr

def process_correlation_data(df, column_name1, column_name2):
    five_day_corr = output_rolling_corr(df[column_name1], df[column_name2], 5)
    twenty_day_corr = output_rolling_corr(df[column_name1], df[column_name2], 20)
    fifty_day_corr = output_rolling_corr(df[column_name1], df[column_name2], 50)

    output_df=pd.DataFrame(columns = ["five_day_corr", "twenty_day_corr", "fifty_day_corr"], index= df.index)
    output_df["five_day_corr"] = five_day_corr
    output_df["twenty_day_corr"] = twenty_day_corr
    output_df["fifty_day_corr"] = fifty_day_corr
    return output_df

def output_rolling_corr(series1, series2, window, pairwise = False):
    return series1.rolling(window).corr(series2)

def plot_data(df, ticker1, ticker2, ticker1_option = "Open",  ticker2_option= "Open"):
    pio.renderers.default = 'browser'
    fig = px.scatter(df, x=df.index, y=df.columns, 
                 title=f"{ticker1} {ticker1_option} vs {ticker2} {ticker2_option}")
    fig.show()
    

##Baba open and 9988.hk close
baba_ticker="baba"
baba_hk_ticker="9988.hk"
baba_hk_option = "Close"
start_date = "2020-08-19"
end_date = "2022-02-01"
INPUT_PARAMS = ["Stock_ticker1", "Stock_metric1", "Start_date1", "End_date1",
                "Stock_ticker2", "Stock_metric2", "Start_date2", "End_date2"]
default_case = ["BABA", "Open", "2020-08-19", "2022-02-01",
                "9988.hk", "Close", "2020-08-19", "2022-02-01"]
placeholder_list = ['Enter a stock ticker..., eg: BABA',
                    'Enter a stock metric..., eg: Open/Close',
                    'Enter a start date..., eg: 2020-08-19', 
                    'Enter a end date..., eg: 2022-02-01']
 
# df1 = download_stock_data(baba_ticker, start_date, end_date, "Open", interval ="1d")
# df2 = download_stock_data(baba_hk_ticker, start_date, end_date, baba_hk_option, interval ="1d")

# dff1 = df1.copy()
# dff2 = df2.copy()

# dff_final = process_stock_data(baba_ticker, baba_hk_ticker, dff1, dff2, "Open", "Close")

def generate_inputs(INPUT_PARAMS, placeholder_list,i):
    return dcc.Input(id =f"{INPUT_PARAMS[i]}",
                placeholder = placeholder_list[i%len(placeholder_list)],
                type = "text",
                value = default_case[i]
                )

server = app.server

app.layout = html.Div([
    html.H1(children='Stock correlations', style={'text-align': 'center'}), #Title?
    dbc.InputGroup([dbc.InputGroupText("Stock Ticker 1:"), dbc.Input(id = "Stock_ticker1", placeholder="Eg:BABA", value="BABA")]
    ),
    dbc.InputGroup([dbc.InputGroupText("Stock Ticker 2:"), dbc.Input(id = "Stock_ticker2", placeholder="Eg:9988.hk", value="9988.hk")]
    ),
    dbc.InputGroup([dbc.InputGroupText("Ticker 1 Option:"), dbc.Input(id = "Stock_metric1", placeholder="Eg:Open", value="Open")]
    ),
    dbc.InputGroup([dbc.InputGroupText("Ticker 2 Option:"), dbc.Input(id = "Stock_metric2", placeholder="Eg:Open", value="Close")]
    ),
    dbc.InputGroup([dbc.InputGroupText("Start Date:"), dbc.Input(id = "Start_date", placeholder="Eg:2020-02-19", value="2020-08-19")]
    ),
    dbc.InputGroup([dbc.InputGroupText("End date:"), dbc.Input(id = "End_date", placeholder="Eg:2021-02-01", value="2022-02-01")]
    ),
    
    # dbc.Row([ 
    #     dbc.Col(
    #         [generate_inputs(INPUT_PARAMS, placeholder_list,i) for i in range(len(INPUT_PARAMS))]
    #     )
    # ]),
    # dcc.Input(id=f"{input_param[i]}",
    #              placeholder = placeholder_list[INPUT_PARAMS.index[i]%len(placeholder_list)],
    #              type = "text",
    #              value = default_case[INPUT_PARAMS[i]],
    #              )
    #              for i in len(INPUT_PARAMS) 
                 #for input_param in INPUT_PARAMS
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id ='output_container', children = []),
    html.Br(),
    dcc.Graph(id='my_stock_plot', figure={})
])
             

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_stock_plot', component_property='figure')],
    [Input('submit-button-state', 'n_clicks'),
     Input(component_id='Stock_ticker1', component_property='value'),
     Input(component_id='Stock_ticker2', component_property='value'),
     Input(component_id='Stock_metric1', component_property='value'),
     Input(component_id='Stock_metric2', component_property='value'),
     Input(component_id='Start_date', component_property='value'),
     Input(component_id='End_date', component_property='value'),
    ]
)
def update_graph(n_clicks, Stock_ticker1, Stock_ticker2, Stock_metric1, Stock_metric2, Start_date, End_date):
    #print(Stock_metric)
    #print(type(Stock_metric))
    df1 = download_stock_data(Stock_ticker1, Start_date, End_date, Stock_metric1, interval ="1d")
    df2 = download_stock_data(Stock_ticker2, Start_date, End_date, Stock_metric2, interval ="1d")

    dff1 = df1.copy()
    dff2 = df2.copy()

    column_headers = [f"{Stock_ticker1}_{Stock_metric1}", f"{Stock_ticker2}_{Stock_metric2}"]
    corr_column_headers = ["five_day_corr", "twenty_day_corr", "fifty_day_corr"]
    dff_final = process_stock_data(Stock_ticker1, Stock_ticker2, dff1, dff2, Stock_metric1, Stock_metric2)
    dff_corr = process_correlation_data(dff_final, column_headers[0], column_headers[1])

    fig = make_subplots(rows = 2, cols = 1, subplot_titles = ("Price history", "Rolling correlations"))
    for i in range(0, len(dff_final.columns)):
        fig.add_trace(go.Scatter(x = dff_final.index, y = dff_final[column_headers[i]], name = column_headers[i]), 1, 1)
    for i in range(0, len(corr_column_headers)):
        fig.add_trace(go.Scatter(x = dff_corr.index, y = dff_corr[corr_column_headers[i]],  name = corr_column_headers[i]), 2, 1)
    fig.update_layout(template = 'plotly_dark')
    # fig = px.line(
    #         data_frame=dff_corr,
    #         x = dff_corr.index,
    #         y = dff_corr.columns,
    #         labels = {"Price": "Date"},
    #         template='plotly_dark', 
    #         title = f"{Stock_ticker1} {Stock_metric1} vs {Stock_ticker2} {Stock_metric2}"
    #     )
    container = "The option chosen by user was: {}".format(Stock_metric1)
    return container, fig


if __name__ == '__main__':

    app.run_server(debug=True)