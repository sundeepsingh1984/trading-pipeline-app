import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.models.alpaca_db_models import Stocks
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
import asyncio 
import nest_asyncio


class StocksController:

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




    

    async def query_data(self,relation,parameter_val=None,limit=50000,parameter=None):


        try:
            session=self.sync_session()
            if parameter_val:

                if type(parameter_val) == list:
                    q_res=session.query(relation).filter( getattr(relation,parameter).in_(parameter_val)).limit(limit).all()

                else:
                    q_res=session.query(relation).filter( getattr(relation,parameter) ==  parameter_val).limit(limit).all()


            else:
                q_res=session.query(relation).limit(limit).all()

                

            
            data=[dict(d) for d in q_res]
            
            return data 

        except Exception as e :

            raise e



    
    async def fetch_all_stocks(self):
        
        stocks=await self.query_data(Stocks)
        return stocks


    async def fetch_one_stock(self):

        stock=await self.query_data(relation=Stocks,limit=1)
        return stock

    









    
    async def fetch_filtered_stock(self,filtered_by,filtration_val,limit=50000):
        stocks=await self.query_data(Stocks,parameter_val=filtration_val,parameter=filtered_by,limit=limit)
        return stocks








