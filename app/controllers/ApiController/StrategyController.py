import sys
import pathlib 
sys.path.append(pathlib.Path(__file__).resolve().parents[3])

from app.db.tasks import database_session
from app.models.api_db_models import  Users,Strategies




class StrategyController:

    def __init__(self):

        self.async_session,self.sync_session=database_session()




    async  def create(self,user_id,strategy_details):

        try:
            session=self.sync_session()
            user=session.query(Users).filter(Users.id == user_id).one()
            user.strategies.append(strategy_details)
            session.commit()

        except Exception as e:

            session.rollback()
            raise e





    async def update(self,s_id,s_dict):

        try:
            session=self.sync_session()
            session.query(Strategies).filter(Strategies.id == s_id).update(s_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

   

    
    
    async def delete(self,s_id):

        try:
            session=self.sync_session()
            session.query(Strategies).filter(Strategies.id == s_id).delete()
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
            q_res=session.query(Users).filter( getattr(Users,parameter) ==  parameter_val).one()
            await self.query_inner_data(q_res,relation,queue,limit)


        elif type(parameter_val) == list:

            prm=getattr(Users,parameter)


            q_res=session.query(Users).filter( prm.in_(parameter_val)).all()


            await asyncio.gather(*(self.query_inner_data(q,relation,queue,limit) for q in q_res))

        else:

            print("enter vsalid par_value str and list is valid type ")

        results=[]        
        while not queue.empty():
            results.append(await queue.get())
            queue.task_done()
             
        return results
        


            

    async def retreive_user_strategies(self,u_val,limit,parameter="id"):

        data=await self.query_data("strategies",parameter_val = u_val,limit=limit,parameter=parameter)
        return data


    

   













        







