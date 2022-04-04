from typing	import List
from fastapi import APIRouter,Request,HTTPException
import sys,os,pathlib
from typing import Optional
# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
from controllers.ApiController import *
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from app.schemas import *
from fastapi.templating import Jinja2Templates
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,date
from typing import Optional
import logging
from app.config import LOG_CONF_FILE

#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("api")




# from app.controllers import SymbolController
router=APIRouter()



#routes

#get assets
@router.get("/stocks/{source}")
async def tickers(request:Request,source:str,market:Optional[str]=None):

    try:
        d_obj=DataController(source)
        data = await d_obj.get_stocks()
        data_json = jsonable_encoder(data)
        return  JSONResponse(content=data_json)
    except Exception as e:
        logger.exception("some error occured")
        return ConnectionError




     
#get sources

@router.get("/sources")

async def sources(request:Request):

    try:
        s_obj=SourceController()
       
        data=await s_obj.retreive()
        data_json = jsonable_encoder(data)
        return JSONResponse(content=data_json)

    except Exception as e:
           logger.exception("some error occured")
           return ConnectionError


#add source
@router.get("/addsource")

async def addSource(request:Request,name:str):

    try:
        sourcedetails={"source_name":name}
        
        s_obj=SourceController()
        add=await s_obj.create(sourcedetails)
        if add == 1:
            return({
                "status":"success",
                "msg":"source_added",
                })

    except Exception as e:
        logger.exception("some error occured")
        return ConnectionError

        




#getPrices

@router.get("/prices/{source_id}/{assets}/{timeframe}")

async def getPrices(request:Request,source_id:int,timeframe:str,assets:str,start:Optional[str]=None,end:Optional[str]=None,limit:Optional[int]=50000):
    try:
        dt_obj=DataController(source_id)
        data=await dt_obj.get_prices(assets,timeframe,start,end,limit=limit)

        if type(data) == int:
             raise HTTPException(status_code=404, detail="Item not found")
       

        data_json = jsonable_encoder(data)
        return JSONResponse(content=data_json)

    except Exception as e:
        logger.exception(f"error fetching prices for assets:{assets} timeframe:{timeframe} from source {source_id} ts:{start} to {end}")
        raise HTTPException(status_code=404, detail="Item not found")
       
       


     


@router.get("/trades/{source_id}/{assets}")

async def getTrades(source_id:int,assets:str,start:Optional[str]=None,end:Optional[str]=None,limit:Optional[int]=50000):
    try:
        dt_obj=DataController(source_id)
        data=await dt_obj.get_trades(assets,start,end,limit)
        data_json = jsonable_encoder(data)
        return JSONResponse(content=data_json)


    except Exception as e:

        logger.exception(f"error fetching trades for assets:{assets}")
        
        raise HTTPException(status_code=404, detail="Item not found")
        



@router.get("/quotes/{source_id}/{assets}")

async def get(assets:str,source_id:int,start:Optional[str]=None,end:Optional[str]=None,limit:Optional[int]=50000):
    try:
        dt_obj=DataController(source_id)
        data=await dt_obj.get_trades(assets,start,end,limit)
        data_json = jsonable_encoder(data)
        return JSONResponse(content=data_json)


    except Exception as e:
        logger.exception(f"error fetching trades for assets:{assets}")
        raise HTTPException(status_code=404, detail="Item not found")
        
       







    






    

