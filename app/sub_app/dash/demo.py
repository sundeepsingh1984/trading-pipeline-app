import dash
from dash import dcc 
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from ast import literal_eval
import requests
from dash import dash_table
from functools import lru_cache
import plotly.graph_objs as go
import plotly.express as px

def create_app():
    app=dash.Dash(requests_pathname_prefix='/app/dash/',external_stylesheets=[dbc.themes.BOOTSTRAP])
    controls = dbc.Card([
        dbc.FormGroup([
                dbc.Label("Asset-Type"),
                dcc.RadioItems(
                    id="asset_type",
                    options=[
                        
                        {"label":"Stocks" ,"value":"STOCKS"},
                       
                        ],
                        value="STOCKS",
                    ),
                ]
            ),

        dbc.FormGroup(
            [
                dbc.Label("Ticker"),
                dcc.Dropdown(
                    id="ticker",
                 
                ),
            ]
        ),

        

   
        dbc.FormGroup([
            dbc.Label("Time-Frame"),
            dcc.RadioItems(
                id="tf",
                options=[
                {"label":"Daily" ,"value":"day"},
                {"label":"Minute" ,"value":"minute"},
                {"label":"Hourly" ,"value":"hourly"}
                ],
                value="day",),]),
        ],body=True,)    

            
    app.layout = dbc.Container([
        html.H1("Trading"),
        html.Hr(),
        dbc.Row([dcc.Location(id="url",refresh=False)]),
        dbc.Row([
            dbc.Col(controls, md=4),
            dbc.Col([
                html.H3(id="stock_name"), 
                dcc.Graph(id="open-close-graph"),
                dcc.Graph(id="high-low-graph"),], md=8)],)],fluid=True)




#     @app.callback([ Output("ticker", "value"),Output("ticker", "options")], [Input("asset_type" , "value")] )

#     def updateOptions(asset_type):

#         tickers=request_ticker(asset_type)
#         options=[ {"label":ticker["ticker"], "value": ticker["ticker"]} for ticker in tickers]

#         return tickers[0]["ticker"],options




#     @app.callback([
#         Output("ticker", "options"),
#         Output("ticker", "value"),
#         Output("open-close-graph","figure"),
#         Output("high-low-graph","figure"),
#         Output("stock_name","children"),]
#         ,
#         [
#         Input("url", "pathname")
#         ],
#         )





        





    return app




# def create_fig(df,x_axis,y_axis,hover_name,title):
    
#     fig = px.line(df, x=x_axis,y= y_axis,hover_name=hover_name,title=title)
#     return fig

# @lru_cache

# def request_ticker(source):
#     URL="http://127.0.0.1:8000/api/stocks/{source}".format(source)
#     data=requests.get(URL)
#     return data.json()


# def request_prices(ticker,source,timeframe="minute"):
#     URL="http://127.0.0.1:8000/api/prices/{}/{}/{}".format(source,ticker,timeframe)
#     data=requests.get(URL)
#     return pd.DataFrame.from_dict(data.json())









          








   















if __name__ == '__main__':
    app=create_app()
    app.run_server(debug=True)