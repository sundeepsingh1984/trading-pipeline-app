import sys
import pathlib
from starlette.routing import NoMatchFound 
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.db.tasks import database_session
from app.models.api_db_models import Source
from app.config import LOG_CONF_FILE

import logging
import logging.config
#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("api")

class SourceController:

    def __init__(self):
        self.async_session,self.sync_session=database_session("API")


    async def create(self,source_details):
        try:
            session=self.sync_session()
            dta=Source(source_name=source_details["source_name"])
            session.add(dta)
            session.commit()
            return 1

        except Exception as e:
            session.rollback()
            logger.exception("error adding  record")
            raise ConnectionError("error adding records")




    async def retreive(self):

        try:
            session=self.sync_session()
            sorces= session.query(Source).all()

            session.commit()
            return [dict(s) for s in sorces] 
        except Exception as e:
            logger.exception("error occured")





    async def update(self,s_id,s_dict):

        try:
            session=self.sync_session()
            session.query(Source).filter(Source.source_id == s_id).update(s_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

   

    
    
    async def delete(self,s_id):

        try:
            session=self.sync_session()
            session.query(Source).filter(Source.source_id == s_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e



    async def source_by_parm(self,parm_val,parm_name="source_id"):

        try:
            session=self.sync_session()
            sources= session.query(Source).filter(getattr(Source,parm_name) == parm_val).all()
            session.commit()
            if sources:
                return [dict(s) for s in sources] 
            else:
                return 0

        except Exception as e:
            logger.exception("error occured")
            raise ConnectionError()

   


 









		







