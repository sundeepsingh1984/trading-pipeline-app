from os import error
import sys
import pathlib
from fastapi.encoders import jsonable_encoder
from numpy.lib.shape_base import dstack
from sqlalchemy.sql.functions import random
from sqlalchemy.util.langhelpers import symbol
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.controllers.BackendController.Alpaca import AssetsAlpaca,BarsAlpaca,TradesAlpaca,QuoteAlpaca,FileDataAlpaca
from app.db.tasks import database_session
from app.controllers.ApiController.SourceController import SourceController as source
import logging
import random
import asyncio
import logging.config
from app.config import LOG_CONF_FILE
import datetime
import pandas as pd
import json
#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("api")



class DataController(AssetsAlpaca):



    def __init__(self,source_id):
        self.source_id=source_id
        super().__init__()




    async def get_source_details(self):
        try:
            s_obj=source()
            s_infm=await s_obj.source_by_parm(self.source_id)
            self.source_nme=s_infm[0]["source_name"]
        
        except Exception as e:
            print("error fetching source")
            logger.exception("there was some error fetching source")
            raise ConnectionError

       


    





    async def get_stocks(self,filter_by=None,filter_val=None,limit=50000):

        await self.get_source_details()
        if self.source_nme == "Alpaca":
            if filter_by and filter_val:
                 await self.fetch_filtered_stock(filter_by,filter_val,limit)

            else :
                return await self.fetch_all_stocks()

        
    
    
    
    async def get_prices(self,assets,timestamp,date_frm=None,date_to=None,tpe="unadj",limit=50000):

        if date_frm != None and date_to != None:
            start=datetime.datetime.strptime(date_frm,"%Y-%m-%d").date()
            end=datetime.datetime.strptime(date_to,"%Y-%m-%d").date()

        else:
            start=None
            end=None
        
        await self.get_source_details()

        if self.source_nme == "Alpaca":
            try:
                bar_obj=BarsAlpaca()

                if timestamp == "minute":
                    data=await bar_obj.get_bar_min_by_ticker(assets,start=start,end=end,limit=limit)

                    if end == datetime.datetime.now().date() or end == None:
                        
                        obj=FileDataAlpaca()
                        real_time=await obj.get_from_file("Bars",assets)
                            
                        if len(data) > 1 and len(real_time) > 0:
                            data=[pd.DataFrame.from_dict(d["data"]) for d in data]
                            dfs=[]
                            for i,d in enumerate(data):
                                if type(real_time[i]) == int:
                                    dfs.append({
                                        "symbol":symbol[i],
                                        "data":df.to_json(orient="records")
                                    })
                                
                                else:
                                    if tpe == "unadj":
                                        rl_time=real_time[i]
                                        rl_time["adjusted"]=False
                                    else:
                                        rl_time["adjusted"] = True
                                    
                                    rl_time["stock_id"] = d.iloc[0]['stock_id']
                                    rl_time["id"]= random.randint(10000,1000000000)
                                    df=pd.concat([d,rl_time])
                                    dfs.append({
                                        "symbol":symbol[i],
                                        "data":df.to_json(orient="records")
                                    
                                    
                                    })
                            data=dfs

                    
                        else:
                            if type(real_time) == int:
                                pass
                                
                            else:
                                data=pd.DataFrame.from_dict(data[0]["data"])
                                if tpe == "unadj":
                                    real_time["adjusted"]=False
                                else:
                                    real_time["adjusted"] = True

                                real_time["stock_id"] = data.iloc[0]['stock_id']
                                real_time["id"]= random.randint(10000,1000000000)
                                df=pd.concat([data,real_time])
                                data=df.to_json(orient="records")
                                data={
                                   "symbol":assets ,
                                   "data": data,
                                    }

                elif timestamp == "hour":
                    data= await bar_obj.get_bar_hour_by_ticker(assets,start=start,end=end,limit=limit)

                else:
                    data =  await bar_obj.get_bar_daily_by_ticker(assets,start=start,end=end,limit=limit)
                    
              
                return data

            except Exception as e:
                raise e
              
                print("error fetching data")
                logger.exception("there was some error fetching source")
                raise e

                

    
    async def get_trades(self,assets,start=None,end=None,limit=50000):
        try:
            trades_obj=TradesAlpaca()
            if end != None:
                end=datetime.datetime.strptime(end,"%Y-%m-%d").date()
            if start != None:
                start=datetime.datetime.strptime(start,"%Y-%m-%d").date()
            data=await trades_obj.get_trades_by_ticker(assets,start,end,limit)
            
            if end == datetime.datetime.now().date() or end == None:
                obj=FileDataAlpaca()
                real_time_trades=await obj.get_from_file("Trades",assets)
               

                
                if len(data) > 1 and len(real_time_trades) > 0:
                    data=[pd.DataFrame.from_dict(d["data"]) for d in data]
                    dta=[]
                    for i,d in enumerate(data):
                        if type(real_time_trades[i]) == int:
                            dta.append({
                                "symbol" : assets[i] ,
                                "data": data.to_json(orient="records"),
                             })

                        else:
                            rl_time=real_time_trades[i]
                            rl_time["stock_id"] = d.iloc[0]['stock_id']
                            rl_time["id"]= random.randint(10000,1000000000)
                            df=pd.concat([d,rl_time])    
                            data={
                                "symbol":assets[i],
                                "data": df.to_json(orient="records")}
                            dta.append(data)
                    data=dta
                
                else:
                    if type(real_time_trades) != int:
                        data=pd.DataFrame.from_dict(data[0]["data"])
                        real_time_trades["stock_id"] = data.iloc[0]['stock_id']
                        real_time_trades["id"]= random.randint(10000,1000000000)
                      
                        df=pd.concat([data,real_time_trades])
                        
                        data={
                            "symbol":assets,
                            "data":df.to_json(orient="records")}
            
            return data 
        
                            
                    
        except Exception as e:
            raise e
            print("error fetching source")
            logger.exception("there was some error fetching source")
            raise ConnectionError

    
    
    
    async def get_quotes(self,assets,start=None,end=None,limit=50000):
        try:
            quotes_obj=QuoteAlpaca()
            if end != None:
                end=datetime.datetime.strptime(end,"%Y-%m-%d").date()
            if start != None:
                start=datetime.datetime.strptime(start,"%Y-%m-%d").date()
            data=await quotes_obj.get_quotes_by_ticker(assets,start,end,limit=100000)
            
            if end == datetime.datetime.now().date() or end == None:
                obj=FileDataAlpaca()
                real_time_quotes=await obj.get_from_file("Quote",assets)
               

                
                if len(data) > 1 and len(real_time_quotes) > 0:
                    data=[pd.DataFrame.from_dict(d["data"]) for d in data]
                    dta=[]
                    for i,d in enumerate(data):
                        if type(real_time_quotes[i]) == int:
                            dta.append({
                                "symbol" : assets[i] ,
                                "data": data.to_json(orient="records"),
                             })

                        else:
                            rl_time=real_time_quotes[i]
                            rl_time["stock_id"] = d.iloc[0]['stock_id']
                            rl_time["id"]= random.randint(10000,1000000000)
                            df=pd.concat([d,rl_time])    
                            data={
                                "symbol":assets[i],
                                "data": df.to_json(orient="records")}
                            dta.append(data)
                    data=dta
                
                else:
                    if type(real_time_quotes) != int:
                        data=pd.DataFrame.from_dict(data[0]["data"])
                        real_time_quotes["stock_id"] = data.iloc[0]['stock_id']
                        real_time_quotes["id"]= random.randint(10000,1000000000)
                      
                        df=pd.concat([data,real_time_quotes])
                        
                        data={
                            "symbol":assets,
                            "data":df.to_json(orient="records")}
            
            return data 
        
                            
                    
        except Exception as e:
            raise e
            print("error fetching source")
            logger.exception("there was some error fetching source")
            raise ConnectionError








    

        

        
# obj=DataController(2)
# trades=asyncio.run(obj.get_trades("AAL","2021-01-01","2021-09-17"))





























