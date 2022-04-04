import sys,os
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.models.alpaca_db_models import Stocks,BarMinute,Trades,Quotes,BarDaily,BarHour
from app.db.tasks import database_session
from app.providers import Alpaca
from app.providers import OpenFigi
import os
from app.helpers.database_helper import bulk_insert
from app.helpers.datatype_helpers import divide_chunks
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
from app.config import LOG_CONF_FILE,basepath,FILE_SYSTEM_DIR
import pandas as pd
import time,datetime
import logging
import logging.config
import asyncio

#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("backend")


class FileDataController:

    async def read_source(self,tp,symbol):

        index=symbol[0]
        filename=symbol+'.csv'

        try:
            base=str(FILE_SYSTEM_DIR["ALPACA"])
            dyn_path= base+"/"+ tp +"/"+ index +"/"+symbol+"/"+filename

            if os.path.isfile(dyn_path):
                df=pd.read_csv(dyn_path)
              
                df=await self.process_data(df,tp)

                return df
            else:
                return 0
        
        except Exception as e:
             logger.exception("error reading from file system")



    async def process_data(self,df,data_type):
        if data_type == "Bars":
            df.drop(["Unnamed: 0","T","vw","S"],axis=1,inplace=True)
     
            df.rename({"t":"timestamp","o":"open","h":"high","l":"low","c":"close","v":"volume"},axis=1,inplace=True)
            df.drop_duplicates(subset=["timestamp"],inplace=True,keep="last")

        elif data_type == "Trades":
            df.drop(["Unnamed: 0","T","S"],axis=1,inplace=True)
            df.rename({"t":"timestamp","x":"exchange","p":"trade_price","s":"trade_side","c":"trade_condition","i":"trade_id","z":"tape"},axis=1,inplace=True)
            df.drop_duplicates(subset=["trade_id","timestamp"],keep="last",inplace=True)
            df["exchange"].replace(" ","NA",inplace=True)

        else:
            df.drop(["Unnamed: 0","T","S"],axis=1,inplace=True)
            df.rename({"t":"timestamp","ax":"ask_exchange","ap":"ask_price","bx":"bid_exchange","bp":"bid_price","bs":"bid_size","c":"quote_condition"},axis=1,inplace=True)
            df["bid_exchange"].replace(" ","NA",inplace=True)
            df["ask_exchange"].replace(" ","NA",inplace=True)
            
        return df



    async def get_from_file(self,tp,symbol):
        if type(symbol) == str:
            data = await self.read_source(tp,symbol)
            return data
        else:
            data=await asyncio.gather(*(self.read_source(tp,s) for s in symbol))
            return data
        







