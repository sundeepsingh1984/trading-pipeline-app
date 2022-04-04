
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

"""

from re import S
import sys,os,pathlib

from aiohttp.client_reqrep import Fingerprint
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

import app.config as Config
import asyncio
import ujson
import aiohttp
import sys
import os
import nest_asyncio
from datetime import datetime,timedelta
import time
from math import ceil 
import pandas as pd
import time
import threading 
from pathlib import Path
import pytz
from app.helpers.database_helper import processTickerData, bulk_insert


class Alpaca:
    

    __dataUrl=Config.ALPACA_DATA_URL
    __baseUrl=Config.ALPACA_API_URL
    
    NY = pytz.timezone("America/New_York")
    
    
    bars="/stocks/{}/bars"
    trades="/stocks/{}/trades"
    quotes="/stocks/{}/quotes"
    
    __Queue=asyncio.Queue()
    __DATAFLAG=False
    
    __Header={
        "APCA-API-KEY-ID":Config.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY":Config.ALPACA_SECRET_KEY
        }
    
    def __init__(self):
    
        self.config_loop()
        # super().__init__()
        
    
    
    def config_loop(self):
        try:
            get_ipython()  # type: ignore
            nest_asyncio.apply()
        except NameError:
            try:
                import uvloop
                
                print("running on uvloop")
                uvloop.install()
            except:
                pass
        
        
        if sys.platform == "win32":
            asyncio.set_event_loop_policy( asyncio.WindowsSelectorEventLoopPolicy())
    
        
    
    
    async def requestAssets(self,client,queue,symbol=None):
        
        if symbol:
            url=self.__baseUrl+f"/v2/assets/{symbol}"
        else:
            url=self.__baseUrl+"/v2/assets"
        
        res=await client.get(url,headers=self.__Header)
        
        if res.status != 200:
            
            raise ValueError(f"Bad Status {res.status} ;expected 200")
                    
        await queue.put( await res.json(loads=ujson.loads))
    
       
    
    async def gatherAssets(self,assets=None):
        client=aiohttp.ClientSession()
        queue=asyncio.Queue()
        
        async with client:
            if assets:
                if type(assets) == str:
                    try:
                        await self.requestAssets(client,queue,assets)
                    
                    except Exception as e:
                        raise e
                else:
                    try:
                        await asyncio.gather(*(self.requestAssets(client, queue,asset) for asset in assets))
                    except Exception as e:
                        raise e
                    
            else: 
                
                try:
                     await self.requestAssets(client,queue)
                    
                except Exception as e:
                    raise e
                    
                    
            results=[]        
            while not queue.empty():
                results.append(await queue.get())
                queue.task_done()
             
            return results
        


    def getAssets(self,symbol=None):
        try:
            assets=asyncio.run(self.gatherAssets(symbol))
            return assets
        except Exception as e:
            raise e 
            
            


    async def requestData(self,request_for,client,queue,symbol,start_date,end_date,limit=10000,timeframe="1Min" ,save_to="filesystem",token=''):

        params={
            'start':start_date,
            'end':end_date,
            'limit':limit,
            }
        
        if request_for == "bars":
            params["timeframe"]=timeframe
                
        if token:
            params['page_token']=token
            
            
        url=self.__dataUrl+getattr(self,request_for).format(symbol)
        res=await client.get(url,headers=self.__Header,params=params)
       
        if res.status != 200:
            raise ValueError(f"Bad Status {res.status} ;expected 200")
            
        json=await res.json(loads=ujson.loads)
       
        if save_to == "filesystem":
            await self.to_filesystem_database(json,request_for,symbol)


        else:
            await queue.put(json)

        if json["next_page_token"]:
            
      
            
            await self.requestData(request_for,client,queue,symbol,start_date,end_date,limit,timeframe,save_to,json["next_page_token"])
            
        


        
        
        
    async def to_filesystem_database(self,json,data_type,symbol):

        FILE_SYSTEM=Config.FILE_SYSTEM_DIR["ALPACA"]
        data_dir=FILE_SYSTEM+"/"+data_type
        index_dir=data_dir +"/" +symbol[0]
        symbol_dir=index_dir + '/ ' + symbol
        if not os.path.isdir(data_dir):
            os.path.join(data_dir) 
            os.mkdir(data_dir) 
            
        if not os.path.isdir(index_dir):
            os.path.join(index_dir) 
            os.mkdir(index_dir) 
       
        if not os.path.isdir(symbol_dir):
            os.path.join(symbol_dir) 
            os.mkdir(symbol_dir)
            
        data=json.get("data_from")
        df=pd.DataFrame(data)
        df['Symbol']=symbol
        directory=symbol_dir+"/"+symbol + ".csv"
        
        if not os.path.isfile(directory):
            df.to_csv(directory)
        else: 
            df.to_csv(directory, mode='a', header=False)
            
            
            
   
        
        
        
        
            
        
   
    async def gatherData(self,request_for,symbols,start,end,limit=10000,timeframe="1Min",save_to="filesystem"):

        
        client=aiohttp.ClientSession()
        self.__DATAFLAG=True 
        
        

        
        async with client:
            try:
                start=pd.Timestamp(start,tz=self.NY)
                end=pd.Timestamp(end,tz=self.NY)

            except Exception as e:
                start=pd.Timestamp(start)
                end=pd.Timestamp(end,tz=self.NY)

                
            

            if request_for == 'bars' and timeframe == '1Min':
                max_chunk_days=5
                periods = ceil((end - start).days / max_chunk_days)

            elif request_for == 'bars' and timeframe == '1Hour':
                max_chunk_days=255
                periods = ceil((end - start).days / max_chunk_days)

            elif request_for == 'bars' and timeframe == '1Day':
                periods =0

            else:
                max_chunk_days=5
                periods = ceil((end - start).days / max_chunk_days)
            
            
            



            intervals  = pd.interval_range(start=start,end=end + timedelta(days=1), periods=periods).to_tuples()
            if type(symbols)==str:
                
                if periods > 1 :
                    await asyncio.gather(*(self.requestData(request_for,client,self.__Queue,symbols,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'),limit,timeframe,save_to) for start,end in intervals))
                else:
                    await self.requestData(request_for,client,self.__Queue,symbols,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'),limit,timeframe,save_to)


            else:

                if periods > 1 :
                    for symbol in symbols:
                        await asyncio.gather(*(self.requestData(request_for,client,self.__Queue,symbol,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'),limit,timeframe,save_to) for start,end in intervals))

                else:
                    await asyncio.gather(*(self.requestData(request_for,client,self.__Queue,symbol,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'),limit,timeframe,save_to) for symbol in symbols))
                       
    

        if save_to == "queue":
            
            results=[]        
            while not self.__Queue.empty():
                results.append(await self.__Queue.get())
                self.__Queue.task_done()
             
            return results
        






 
        
        
                
       
        
    def getData(self,request_for,symbol,start,end=str(datetime.now().strftime('%Y-%m-%d')),limit=10000,timeframe="1Min",save_to="filesystem"):
        try:
           data= asyncio.run(self.gatherData(request_for,symbol,start,end,limit,timeframe,save_to))
           return data

        except Exception as e:
  
            if e.__class__ == aiohttp.client_exceptions.ServerDisconnectedError or e.__class__ == asyncio.exceptions.TimeoutError:
                print("apaca server rejected the request will try to reach out in a while....")
                time.sleep(20)
                data= asyncio.run(self.gatherData(request_for,symbol,start,end,limit,timeframe,save_to))
                return data
            else :
                raise e
           

            

            

        
        
    
 




                    
                    
        
        
        
    
    

    
         
         
         