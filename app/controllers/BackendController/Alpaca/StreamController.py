import sys
import pathlib
import os
import asyncio
import threading

from sqlalchemy.sql.expression import asc, desc
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.providers import AlpacaStream
from app.db.tasks import database_session
from app.helpers.database_helper import to_filesystem_database
from app.models.alpaca_db_models import Stocks
import pandas as pd
import logging
import app.config as Config  
import logging.config
from app.config import SP_DIR
#log's info
logging.config.fileConfig(Config.LOG_CONF_FILE,disable_existing_loggers=False)

logger=logging.getLogger("alpacastream")



class StreamController(AlpacaStream):

    #streaming channels

    CHANNELS=["bars","trades","quotes"]

    def __init__(self,feed="sip"):
        super().__init__()
        self.handlers={
            "trades":self.trade_handler,
            "trades_update":self.trade_update_handler,
            "quotes":self.quote_handler,
            "bars":self.bars_handler,
            }

        self.feed=feed

        self.session,self.sync_session= database_session("Alpaca")

    
    #fetches s&p 500 from file system

    def fetch_sp(self):

        try:
            df=pd.read_csv(SP_DIR)
            
            symbols=df["Symbol"].to_list()
            return symbols

        except Exception as e:
            raise e
            logger.exception("error fetching standard and poor")

    
    #fetches list of stock from list
    
    def fetch_stocks_list(self,not_in_list=None):

        try:
            ssn=self.sync_session()
            if not_in_list:
                data=ssn.query(Stocks.ticker).filter(~Stocks.ticker.in_(not_in_list)).order_by(asc(Stocks.ticker)).all()
            
            else:
                data=ssn.query(Stocks.ticker).all()
            
            ssn.commit()
            data=[dict(d) for d in data]
            return data 

        except Exception as e:
            raise e
            print("error occured check log file for details")
            logger.exception("exception occured on fetching stocks from database")

    #handler for trades

    async def trade_handler(self,data):
        await to_filesystem_database([data],data_type="Trades",symbol=data["S"])
        

    #handler for trade updates
    

    async def trade_update_handler(self,data):
        await to_filesystem_database([data],data_type="Trades",symbol=data["S"])
         
         
        
    #handler for quotes


    async def quote_handler(self,quote_dta):

        await to_filesystem_database([quote_dta],data_type="Quote",symbol=quote_dta["S"])
       
        
    #handler for bars
    

    async def bars_handler(self,data):
        await to_filesystem_database([data],data_type="Bars",symbol=data["S"])
         



    def get_all_streams(self,limit=None,with_sp=True):
        
        if with_sp:
            ex_lst=self.fetch_sp()
            stocks=pd.DataFrame(self.fetch_stocks_list(not_in_list=ex_lst))
            stocks=stocks["ticker"].tolist()
            if limit:
                stocks=stocks[:limit]+ex_lst
            else:
                stocks=stocks+ex_lst
            
        else:
            stocks=pd.DataFrame(self.fetch_stocks_list())
            stocks=stocks["ticker"].tolist()
        
        try:
            self.get_streams(self.feed,self.CHANNELS,stocks,self.handlers)

        except Exception as e:
            raise e
            logger.exception("error in streaming data")

    #stream_trades

    def stream_sp_trades(self):
        sp=self.fetch_sp()

        try:
            self.get_streams(self.feed,["trades","trades_update"],sp,self.handlers)

        except Exception as e:
            logger.exception("error streaming trades for s&p")

    
    #stream quotes

    def stream_sp_quotes(self):
        sp=self.fetch_sp()

        try:
            self.get_streams(self.feed,["quotes"],sp,self.handlers)

        except Exception as e:
            logger.exception("error streaming quotes for s&p")

    
    

    #stream bars
    def stream_sp_bars(self):
        sp=self.fetch_sp()
        try:
            self.get_streams(self.feed,["bars"],sp,self.handlers)

        except Exception as e:
            raise e
            logger.exception("error streaming bars for s&p")



