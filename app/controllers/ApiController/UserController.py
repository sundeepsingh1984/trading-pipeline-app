import sys
import pathlib 
sys.path.append(pathlib.Path(__file__).resolve().parents[3])

from app.db.tasks import database_session
from app.models.api_db_models import Users




class UserController:

    def __init__(self):

        self.async_session,self.sync_session=database_session()




    async  def create(self,user_details):

        try:

            session=self.sync_session()

            Users(user_details)

            session.commit()

        except Exception as e:

            session.rollback()
            raise e




    async def retreive(self):

        try:
            session=self.sync_session()
            users= session.query(Users).all()

            session.commit()
            return [dict(u) for u in users] 

        except Exception as e:
            raise e





    async def update(self,u_id,u_dict):

        try:
            session=self.sync_session()
            session.query(Users).filter(User.id == u_id).update(u_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

   

    
    
    async def delete(self,u_id):

        try:
            session=self.sync_session()
            session.query(Users).filter(User.id == u_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e



    async def user_by_id(self,u_id):

        try:
            session=self.sync_session()
            users= session.query(Users).filter(User.id == u_id).all()
            session.commit()
            return [dict(u) for u in users] 

        except Exception as e:
            raise e


    async def user_by_email(self,email):

        try:
            session=self.sync_session()
            users= session.query(Users).filter(User.email == email).all()
            session.commit()
            return [dict(u) for u in users] 

        except Exception as e:
            raise e

   









        







