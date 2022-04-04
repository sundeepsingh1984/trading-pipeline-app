import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.models.api_db_models import SourceData,Source
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
import asyncio 
import nest_asyncio






class SourceDataController():

  


    def __init__(self):
        self.session , self.sync_session = database_session("Alpaca")
        self.config_loop()


    


    def create(self,source_id,data_type):


        session =self.sync_session()

        try:

            src=session.query(Source).filter(Source.source_id == source_id).one()

            src.data_available.append(data_type = data_type )

            session.commit()

        except Exception as e:
            raise e

            session.rollback()










    

    
























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
                data=getattr(query,relation).filter(r_obj.datetime.between(start,end)).limit(limit).all()
        else:
            data=getattr(query,relation).limit(limit).all()


        await queue.put([dict(d) for d in data])

        

    async def query_data(self,r_obj,relation,parameter_val=None,start=None,end=None,limit=50000,parameter="source_id"):

        session=self.sync_session()

        queue=asyncio.Queue()
        
        if type(parameter_val) == str:
            q_res=session.query(Source).filter( getattr(Source,parameter) ==  parameter_val).one()
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
        


            

    async def get_source_data_by_id(self,source_id,limit):

        data=await self.query_data(SourceData,"data_available",parameter_val = source_id,limit=limit )
        return data


    

 




