import sys

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.controllers.BackendController.Alpaca import BarsAlpaca,PopulateAlpaca,AssetsAlpaca
from app.db.tasks import database_session
from app.models.alpaca_db_models import Crons
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

class AlpacaUpdateCron(BarsAlpaca,PopulateAlpaca):
    def __init__(self):
        super().__init__()
        self.async_session , self.session = database_session("Alpaca")
    
    def get_start_end_date(self):
        obj=AssetsAlpaca()
        stock = asyncio.run(obj.fetch_one_stock())
        bars =  asyncio.run(self.get_bar_daily_by_ticker(stock[0]["ticker"],1))
        timezone = timezone = pytz.timezone("America/new_york")
        date_last = timezone.localize(bars[0]["data"][0]["timestamp"])
        end_date = datetime.datetime.now(tz = timezone)
        start_date = date_last+datetime.timedelta(days=1)
        return start_date,end_date


    def update_models(self,update_on,timeframe='1Min',chunk_sz=500):
        start,end = self.get_start_end_date()
        diff=(end-start)

        print(start)
        print(end)
        print(diff)
    
        if diff.days  > 0:
            try:
                crn_id=str(start.strftime('%Y-%m-%d:%H:%M:%S'))+"_"+update_on
                session=self.session()
                cron_entry=Crons(cron_id = crn_id , cron_type = "Insert", cron_on = update_on ,cron_status="started")
                logger.info(f"Cron updating on {update_on} for timeframe {timeframe}  started")
                self.populate_price_quote_trade(request_for=update_on,timeframe=timeframe,start=start,chunk_size=chunk_sz)
                session.query(Crons).filter(Crons.cron_id == crn_id).update({Crons.cron_status : "finished"})
                logger.info(f"Cron updating on {update_on} for timeframe {timeframe} finished")

            except Exception as e:
                logger.exception(f"Cron updating on {update_on} failed for timeframe {timeframe} ")
                session.query(Crons).filter(Crons.cron_id == crn_id).update({Crons.cron_status : "failed"})
                

            finally:
                session.commit()

        else:

            logger.info(f"data already updated for {update_on} for timeframe {timeframe} ")


   

def main():
    
    obj=AlpacaUpdateCron()
    # obj.update_models("bars",timeframe="1Min",chunk_sz=5000)
    # obj.update_models("bars",timeframe="1Hour",chunk_sz=5000)
    # obj.update_models("trades",chunk_sz=100)
    # obj.update_models("quotes",chunk_sz=100)
    obj.update_models("bars",timeframe="1Day",chunk_sz=5000)




if __name__ == "__main__":
    main()









           





       











		
	
		