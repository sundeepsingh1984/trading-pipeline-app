import sys
import pathlib 
sys.path.append(pathlib.Path(__file__).resolve().parents[3])
from app.db.tasks import database_session
from app.models.api_db_models import Strategies,Backtests



class BackTestController:

    def __init__(self):

        self.async_session,self.sync_session=database_session("API")



    


    async  def create(self,s_id,backtest_details):

        try:
            session=self.sync_session()
            user=session.query(Strategies).filter(Strategies.id == s_id).one()
            user.backtest_details.append(backtest_details)
            session.commit()

        except Exception as e:

            session.rollback()
            raise e



    


    async def update(self,bt_id,bt_dict):

        try:
            session=self.sync_session()
            session.query(Backtests).filter(Backtests.backtest_id == bt_id).update(bt_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

   

    
    
    


    async def delete(self,bt_id):

        try:
            session=self.sync_session()
            session.query(Source).filter(Backtests.backtest_id == bt_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e




    async def query_inner_data(self,query,relation,queue):
        data=getattr(query,relation).limit(limit).all()
        await queue.put([dict(d) for d in data])

        

    
    async def query_data(self,relation,parameter_val=None,limit=50000,parameter="id"):

        session=self.sync_session()

        queue=asyncio.Queue()
        
        if type(parameter_val) == str:
            q_res=session.query(Strategies).filter( getattr(Strategies,parameter) ==  parameter_val).one()
            await self.query_inner_data(q_res,relation,queue,limit)


        elif type(parameter_val) == list:

            prm=getattr(Strategies,parameter)


            q_res=session.query(Strategies).filter( prm.in_(parameter_val)).all()


            await asyncio.gather(*(self.query_inner_data(q,relation,queue,limit) for q in q_res))

        else:

            print("enter vsalid par_value str and list is valid type ")

        results=[]        
        while not queue.empty():
            results.append(await queue.get())
            queue.task_done()
             
        return results
        


            

    async def retreive_strategy_backtests(self,s_val,limit,parameter="id"):

        data=await self.query_data("strategies",parameter_val = u_val,limit=limit,parameter=parameter)
        return data





   









        







