from logging import debug
import dash
from dash.dependencies import Output,Input
from dash.html import H3
import dash_core_components as dcc
import dash_bootstrap_components as dbc 
import dash_html_components as html
import plotly.express as px
import pandas as pd
from functools import lru_cache
import requests

@lru_cache
def request_ticker(source):
    URL="http://127.0.0.1:8000/api/stocks/{}".format(source)
    data=requests.get(URL)
    return data.json()


@lru_cache
def request_source():
    URL="http://127.0.0.1:8000/api/sources"
    data=requests.get(URL)
    return data.json()


@lru_cache
def request_prices(src,tic,tf="daily"):
    URL="http://127.0.0.1:8000/api/prices/{}/{}/{}".format(src,tic,tf)
    data = requests.get(URL)
    data=data.json()
    df=pd.DataFrame.from_dict(data[0]["data"])
    df["symbol"]=data[0]["symbol"]
    return df


def create_app():
    BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
    app=dash.Dash(requests_pathname_prefix="/app/dash/",external_stylesheets=[BS])

    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options

    controls = dbc.Card([
            dbc.FormGroup([
                    dbc.Label("Data-Source"),
                    dcc.Dropdown(
                        id="data_source",
                       
                        ),]),

            dbc.FormGroup(
                [
                    dbc.Label("Ticker"),
                    dcc.Dropdown(
                        id="ticker"
                          
                    ),]),
            dbc.FormGroup([
                dbc.Label("Time-Frame"),
                dcc.RadioItems(
                    id="tf",
                    options=[
                    {"label":"Daily" ,"value":"daily"},
                    {"label":"Minute" ,"value":"minute"},
                    {"label":"Hourly" ,"value":"hourly"}
                    ],
                    value="daily",),]),
            ],body=True,) 

    app.layout = dbc.Container([
    html.H1(children='Trading app'),
    dbc.Row([dcc.Location(id="url",refresh=False)]),

    dbc.Row([
            dbc.Col(controls, md=2),
            dbc.Col([
                html.H3(id="stock_name"), 
                dcc.Graph(id="open-close-graph"),
                dcc.Graph(id="high-low-graph"),], md=8)],)],fluid=True)


    
    @app.callback([
        Output("data_source", "options"),
        Output("data_source", "value"),
        Output("ticker", "options"),
        Output("ticker", "value")],
        [
        Input("url", "pathname")
        ],
       
        
        )

   
   
    def initialize(pathname):
        if pathname == "/app/dash/":
     
            srcs = pd.DataFrame.from_dict(request_source()) 
            options_src=[{'label': row["source_name"], 'value': row["source_id"]} for index,row in srcs.iterrows()]
            value_src=srcs["source_id"].iloc[0]
            stocks=pd.DataFrame.from_dict(request_ticker(srcs["source_id"].iloc[0]))
            options_tick=[{'label':i, 'value': i} for i in stocks["ticker"].unique()]
            value_tick=stocks["ticker"].iloc[0]     
            stock_price=request_prices(int(value_src),value_tick)
          
            return options_src,value_src,options_tick,value_tick



    
        #callback functions

    @app.callback([Output("open-close-graph", "figure"),Output("high-low-graph","figure")],[Input("data_source","value"),Input("ticker","value"),Input("tf","value")])
    def updateOptions(data_source,ticker,tf):
        df=request_prices(data_source,ticker,tf)
        fig  = px.line(df, x="timestamp",y= ['open' ,'close'],hover_name="symbol",title="Daily Open-Close",markers=True,hover_data=["volume","adjusted"])
        fig2 = px.line(df,x="timestamp",y= ['low','high'],hover_name="symbol",title="Daily Low-High",markers=True)
        return fig,fig2










    return app
    

if __name__ == '__main__':
    
    ap=create_app()
    ap.run_server(debug=True)





