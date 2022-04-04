import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.models.alpaca_db_models import Crons
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
import asyncio 
import nest_asyncio
import logging
import logging.config
from app.config import LOG_CONF_FILE

#config file
logging.config.fileConfig(LOG_CONF_FILE)
logger=logging.getLogger("backend")


class CronController:

    def __init__(self):
        try:
            self.session,self.sync_session=database_session("Alpaca")

        except Exception as e:
            logger.exception("error creating connection to database")
            raise ConnectionError


    
    def create(self,cron_details):
        try:
            session=self.sync_session()
            dta=Crons(cron_id=cron_details["cron_id"], cron_type=cron_details["cron_type"], cron_on=cron_details["cron_on"] , cron_status=cron_details["cron_status"])
            session.add(dta)
            session.commit()
            return 1

        except Exception as e:
            raise e
            session.rollback()
            logger.exception("error adding  record")
            return ConnectionError("error adding records")




    def retreive(self):

        try:
            session=self.sync_session()
            sorces= session.query(Crons).all()

            session.commit()
            return [dict(s) for s in sorces] 
        except Exception as e:
            logger.exception("error occured")





    def update(self,cron_id,c_dict):

        try:
            session=self.sync_session()
            session.query(Crons).filter(Crons.cron_id == cron_id).update(c_dict)
            session.commit()
            
        except Exception as e:
           
            raise e

   

    
    
    def delete(self,c_id):

        try:
            session=self.sync_session()
            session.query(Crons).filter(Crons.cron_id == c_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e



    def crons_by_parm(self,parm_val,parm_name="cron_id"):

        try:
            session=self.sync_session()
            sources= session.query(Crons).filter(getattr(Crons,parm_name) == parm_val).all()
            session.commit()
            if sources:
                return [dict(s) for s in sources] 
            else:
                return 0

        except Exception as e:
            logger.exception("error occured")
            raise ConnectionError()

   


 









		








