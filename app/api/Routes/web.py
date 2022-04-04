from typing	import List
from fastapi import APIRouter,Request
import sys,os,pathlib


from typing import Optional
# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from app.controllers.ApiController import DataController,SourceController,SourceDataController
import app.config as Config

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from app.schemas import *
from fastapi.templating import Jinja2Templates



# from app.controllers import SymbolController
router=APIRouter()


#template setting

templates = Jinja2Templates(directory=Config.TEMPLATE_DIR)


@router.get("/")

async def index(request:Request):
    sour_obj=SourceController()
    sources=await sour_obj.retreive()
    active_source=sources[0]["source_id"]
    sym_obj=DataController(sources[0]["source_id"])






    symbols=await sym_obj.get_stocks()

    return templates.TemplateResponse("index.html",{"request":request,"symbols":symbols,"data_type":"stock","count":len(symbols),"sources":sources,"active":active_source},)


@router.get("/stocks" )
async def stocks(request:Request):
    obj=DataController()
    stocks=await obj.get_stocks()
    return templates.TemplateResponse("index.html",{"request":request,"symbols":stocks,"data_type":"stock","count":len(stocks)})



@router.get("/stockprices/{source}/{ticker}")
async def stockprices(request:Request,source:int,ticker:str,timeframe:str="daily",adjusted:bool=True,from_date:Optional[str]=None,to_date:Optional[str]=None):
    obj = DataController(source) 
    data = await obj.get_prices(ticker,timeframe, date_frm=  from_date, date_to= to_date)
    return templates.TemplateResponse("stock_details.html",{"request":request,"symbol":ticker,"adjusted":adjusted,"timeframe":timeframe,"prices":data})


@router.get("/quotes/{tickers}")
async def trades(request:Request,tickers:str,from_date:Optional[str]=None,to_date:Optional[str]=None):
    obj=DataController()
    data = await obj.get_quotes(tickers,start=from_date,end=to_date)



@router.get("/trades/{tickers}")
async def trades(request:Request,tickers:str,from_date:Optional[str]=None,to_date:Optional[str]=None):
    obj=DataController()
    data = await obj.get_trades(tickers,start=from_date,end=to_date)


























