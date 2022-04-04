import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.controllers.BackendController.Alpaca import StreamAlpaca,CronsAlpaca
from app.db.tasks import database_session
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from app.config import Config
import logging
import logging.config
import asyncio
import datetime
from sqlalchemy.future import select
import sqlalchemy.orm
import pytz
from app.config import LOG_CONF_FILE,basepath,FILE_SYSTEM_DIR
import time,datetime
import logging
import logging.config

#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("cron")


class StreamDataAlpaca(StreamAlpaca) :

    def __init__(self):
        super().__init__()


    
    def start_streaming(self):
        crn_obj=CronsAlpaca()
        crn_id=str(datetime.datetime.now().strftime('%Y-%m-%d:%H:%M:%S'))+"_"+"streaming"
        cron_entry={"cron_id" : crn_id , "cron_type" : "Insert", "cron_on" : "update_on" , "cron_status" : "started"}
            
        try:
            st= crn_obj.create(cron_entry) 

  

            if st == 1:
                print("cron added to table")
                logger.info("Data Straming Started")
                self. get_all_streams(dir)
                logger.info("FILE SYSTEM UPDATE COMPLETED")
        

        
        except Exception as e:
            raise e
            crn_obj.update(crn_id,{"cron_status" : "failed"})
            logger.exception("FILE SYSTEM UPDATE FAILED")




def main():
    obj=StreamDataAlpaca()
    try:
       threads=[threading.Thread(target=obj.stream_sp_quotes,daemon=True),threading.Thread(target=obj.stream_sp_bars,daemon=True),threading.Thread(target=obj.stream_sp_trades,daemon=True)]

       [t.join() for t in threads]

    except Exception as e:

        raise e



        
    # try:


    #     with ProcessPoolExecutor (max_workers=2) as executor:
    #         executor.submit(obj.stream_sp_bars)
    #         executor.submit(obj.stream_sp_trades)
    #         executor.submit(obj.stream_sp_quotes)
 
    # except  Exception as e:
    #     raise e 


        






if __name__ == "__main__":

    main()

