# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 20:37:37 2021

@author: sundeep singh

"""

#imports

import asyncio
import sys
import pathlib
import sys
import os
import pathlib
import time
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
import nest_asyncio
import app.config as Config
from alpaca_trade_api.rest import REST
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import logging
import logging.config

#log's info
logging.config.fileConfig(Config.LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("alpacastream")

class AlpacaDataStream:
    
    def __init__(self):
        os.environ["APCA_API_KEY_ID"]=Config.ALPACA_API_KEY
        os.environ["APCA_API_SECRET_KEY"]=Config.ALPACA_SECRET_KEY
        os.environ["APCA_API_BASE_URL"]=Config.ALPACA_API_URL
        self._conn=None


    #gets the market open time stamp
    def get_market_clock(self):

        try:
            obj=REST()
            clk=obj.get_clock()
            return clk

        except Exception as e:
            return ConnectionError


        
      
    # gets streams
    def get_streams(self,feed,channels,symbols,handlers):

        try:
            self._conn = Stream(data_feed=feed,raw_data=True)

        except Exception as e:

            logger.exception("some error in streaming ")

       

        
        
        
        if "bars" in channels:
            self._conn.subscribe_bars(handlers["bars"],*symbols)
        

       
        
        if "trades" in channels:


            self._conn.subscribe_trade_updates(handlers["trades"])
            self._conn.subscribe_trades(handlers["trades_update"],*symbols)
        
        if "quotes" in channels:
            self._conn.subscribe_quotes(handlers["quotes"],*symbols)
      
       
        
        
        try:

            logger.info("connecting to alpaca server")
            res=self._conn.run()

            

          
            
            logger.info("connction to alpaca server terminated")
            
            print("connection established with alpaca server")
        
        except Exception as e:

            logger.exception("some error connecting to server check logs")
            
            raise e

        finally:
            print("Trying to re-establish connection")
            time.sleep(5)
            res=self._conn.run()


 
  
    
            
    

        

        




        