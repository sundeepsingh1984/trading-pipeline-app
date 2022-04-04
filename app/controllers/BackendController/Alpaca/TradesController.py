import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.models.alpaca_db_models import Stocks,Trades
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
import asyncio 
import nest_asyncio

class TradesController():

    def __init__(self):
        self.session , self.sync_session = database_session("Alpaca")
        self.config_loop()


    
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



    
    async def query_inner_data(self,query,relation,r_obj,queue,start,end,limit):


        if start and end:
                my_time = datetime.min.time()
                start = datetime.combine(start, my_time)
                end=datetime.combine(end,my_time)
                data=getattr(query,relation).filter(r_obj.timestamp.between(start,end)).limit(limit).all()
        else:
            data=getattr(query,relation).limit(limit).all()



        data_fin={

        "symbol":query.ticker,

        "data":[dict(d) for d in data],
        }



        await queue.put(data_fin)

        

    async def query_data(self,r_obj,relation,parameter_val=None,start=None,end=None,limit=50000,parameter="ticker"):

        session=self.sync_session()
        queue=asyncio.Queue()
        
        if type(parameter_val) == str:
            q_res=session.query(Stocks).filter( getattr(Stocks,parameter) ==  parameter_val).one()
            await self.query_inner_data(q_res,relation,r_obj,queue,start,end,limit)

        elif type(parameter_val) == list:
            prm=getattr(Stocks,parameter)
            q_res=session.query(Stocks).filter( prm.in_(parameter_val)).all()
            await asyncio.gather(*(self.query_inner_data(q,relation,r_obj,queue,start,end,limit) for q in q_res))

        
        else:
            print("enter vsalid par_value str and list is valid type ")

        
        results=[]        
        while not queue.empty():
            results.append(await queue.get())
            queue.task_done()
             
        return results
        


    async def get_trades_by_ticker(self,ticker,start,end,limit):

        data=await self.query_data(Trades,"trades",parameter_val = ticker ,start=start ,end=end , limit=limit)
        return data











    





