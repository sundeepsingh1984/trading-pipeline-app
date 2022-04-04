import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
from app.models.alpaca_db_models import Stocks,BarMinute,Trades,Quotes,BarDaily,BarHour
from app.controllers.BackendController.Alpaca import AssetsAlpaca
from app.db.tasks import database_session

from app.providers import Alpaca
from app.providers import OpenFigi
import os
from app.helpers.database_helper import bulk_insert
from app.helpers.datatype_helpers import divide_chunks
from sqlalchemy.future import select
import sqlalchemy
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime
from app.config import LOG_CONF_FILE,basepath,FILE_SYSTEM_DIR
import pandas as pd
import time,datetime
import logging
import logging.config
import asyncio

#log's info
logging.config.fileConfig(LOG_CONF_FILE,disable_existing_loggers=False)
logger=logging.getLogger("backend")


class DataPopulateController:

    ASSET_PATH=FILE_SYSTEM_DIR["ALPACA"]+"assets.csv"
    FIGI_PATH=FILE_SYSTEM_DIR["ALPACA"]+"openfigi.csv"
    ASSET_LIST_PATH=FILE_SYSTEM_DIR["ALPACA"]+"asset_final.csv"
       
    
    def __init__(self):
        self.session,self.sync_session= database_session("Alpaca")


    #get existing stocks

    def get_existing_assets(self):
        obj=AssetsAlpaca()
        assets=asyncio.run(obj.fetch_all_stocks())
        return pd.DataFrame(assets)

    #get stocks from database
    
    def fetch_stocks_list(self):
        try:
            ssn=self.sync_session()
            data=ssn.query(Stocks.ticker).all()
            ssn.commit()
            data=[dict(d) for d in data]
            return data 
        
        except Exception as e:
            print("error occured check log file for details")
            logger.exception("exception occured on fetching stocks from database")
    
    
    #filesystem openfigi and assets check
    def check_file_exists_update(self,path,check_date=True,days=7):
        if os.path.isfile(path):
            if check_date:
                creation_time=os.path.getctime(path)
                ts_creation=datetime.datetime.fromtimestamp(creation_time)
                current=datetime.datetime.now()
                diff=(current-ts_creation).days
                
                if diff > days:
                    return False
                else:
                    logger.info(f"{path} is uptodate")
                    return True
            
            else:
                return True
        
        else:
            return False

    
    # get asset from alpaca
    def get_assets(self):
        st=time.perf_counter() 
        obj=Alpaca()
        assets=obj.getAssets()
        asset_df=pd.concat((pd.DataFrame(asset) for asset in assets),ignore_index=True,)
        active_df=asset_df[asset_df['status'] == 'active']
        asset_list=active_df["symbol"].tolist()
        logger.info(f"Timetaken to get assets{st-time.perf_counter()}")
        asset_df.to_csv(self.ASSET_PATH)
        return asset_list,active_df


    
    #read assets from csv
    def read_assets(self):
        df=pd.read_csv(self.ASSET_PATH)
        active_df=df[df['status'] == 'active']
        asset_list=active_df["symbol"].tolist()
        return asset_list,active_df

    
    # get figi from openfigi
    def get_figi(self,asset_list):
        o_figi=OpenFigi()
        figi_details=o_figi.get_figi(asset_list)
        figi_details.to_csv(self.FIGI_PATH,mode="a")
        df=figi_details.loc[ figi_details["figi"] == figi_details["compositeFIGI"] ]
        return df 


    
    #read figi from csv
    def read_figi(self):
        figi_details=pd.read_csv(self.FIGI_PATH)
        df=figi_details.loc[ figi_details["figi"] == figi_details["compositeFIGI"] ]
        return df 


    #inserts data into database
    def insert_to_database(self,relation,df):
        session=self.sync_session()
        try:
            session.bulk_insert_mappings(relation,df.to_dict(orient="records"))
            
            session.commit()
            logger.info(f"records added to {relation.__name__}")
            print(f"record added to relaion {relation.__name__} ")
        
        except Exception as e:
           
            logger.exception(f'error on record addition to {relation.__name__} trying update')
        
            if type(e).__name__ == "IntegrityError":

                session.rollback()
                
                try:
                    session.bulk_update_mappings(relation,df.to_dict(orient="records"))
                    session.commit()
                    logger.info(f"updated relation {relation.__name__}")
                    print(f"record updated to relaion {relation.__name__} ")
                except Exception as e:

                    if e.__class__ == sqlalchemy.orm.exc.StaleDataError and relation.__name__ == "Stocks":

                        existing_assets=self.get_existing_assets()
                        filtered_assets=df[~df.unique_id.isin(existing_assets["unique_id"])]

                        print(filtered_assets.info())
                        update_assets=df[df.unique_id.isin(existing_assets["unique_id"])]
                        print(update_assets.info())
                        self.insert_to_database(relation,filtered_assets)
                        print("added new records")
                        session.bulk_update_mappings(relation,update_assets.to_dict(orient="records"))
                        session.commit()
                        logger.info(f"updated relation {relation.__name__}")
                        print(f"record updated to relaion {relation.__name__} ")








                    

                    else:
                        print("error updating/adding check logs")
                        session.rollback()
                        logger.exception(f"error on update of {relation.__name__}")


            else:
                print("error adding check log")
                logger.exception(f'error on record addition to {relation.__name__}')








    #populate database with assets
    

    def populate_assets(self):
        if self.check_file_exists_update(self.ASSET_PATH) == False:
            asset_list,assets_df=self.get_assets()

        else:
            asset_list,assets_df=self.read_assets()


        if self.check_file_exists_update(self.FIGI_PATH,check_date=False) == False:
            figi_details=self.get_figi(asset_list)

        else:
            figi_details=self.read_figi()

        figi_details=figi_details.drop_duplicates(subset="ticker")
        figi_details.set_index("ticker",inplace=True)
        assets_df.set_index("symbol",inplace=True)
        join_df=pd.concat([figi_details,assets_df],axis=1,join="inner")
        join_df.index.set_names("ticker")
        join_df.reset_index(inplace=True)
        join_df=join_df.loc[:,~join_df.columns.duplicated()]
        join_df.drop(["Unnamed: 0","id","class","status","marginable","shortable","easy_to_borrow","fractionable"],axis=1,inplace=True)
        join_df.rename({"figi":"unique_id","tradable":"active","index":"ticker"},axis=1,inplace=True)
        print(join_df.info())
        join_df.drop_duplicates(subset=["unique_id"], inplace=True)
        print(join_df.info())
        join_df.to_csv(FILE_SYSTEM_DIR["ALPACA"]+"asset_final.csv")
        self.insert_to_database(Stocks,join_df)
       

    

    #process the data
    def process_data(self,timeframe,data,data_type):
        ssn=self.sync_session()
        dfs=[]
        for dt in data:
            try:
                u_id=ssn.query(Stocks.unique_id).filter(Stocks.ticker == dt["symbol"] ).one()


                if data_type == "bars":
                    df=pd.DataFrame(dt["bars"])
                    df.rename({"t":"timestamp","o":"open","h":"high","l":"low","c":"close","v":"volume"},axis=1,inplace=True)


                elif data_type == "trades":
                    df=pd.DataFrame(dt["trades"])
                    df.rename({"t":"timestamp","x":"exchange","p":"trade_price","s":"trade_side","c":"trade_condition","i":"trade_id","z":"tape"},axis=1,inplace=True)
                    df["exchange"].replace(' ',"NA",inplace=True)

                else:

                    df=pd.DataFrame(dt["quotes"])
                    df.rename({"t":"timestamp","ax":"ask_exchange","ap":"ask_price","bx":"bid_exchange","bp":"bid_price","bs":"bid_size","c":"quote_condition"},axis=1,inplace=True)
                    df["ask_exchange"].replace(' ',"NA",inplace=True)
                    df["bid_exchange"].replace(' ',"NA",inplace=True)

                df["stock_id"]=u_id[0]
                dfs.append(df)

            except Exception as e:
                print(f"there is some error in fetching details for {dt['symbol']}")
                logger.exception(f"error fetching records for {dt['symbol']}")

        ssn.commit()
        ssn.close()
        df=pd.concat(dfs)
        
        if data_type == "bars" and timeframe == "1Min":
            df.drop_duplicates(subset=["timestamp","stock_id"],inplace=True)
            self.insert_to_database(BarMinute,df)

        elif data_type == "bars" and timeframe == "1Hour":
            df.drop_duplicates(subset=["timestamp","stock_id"],inplace=True)
            self.insert_to_database(BarHour,df)

        elif data_type == "bars" and timeframe == "1Day" :
            df.drop_duplicates(subset=["timestamp","stock_id"],inplace=True)
            self.insert_to_database(BarDaily,df)


        elif data_type == "quotes" and timeframe == None :
            self.insert_to_database(Quotes,df)

        else  :
            df.drop_duplicates(subset="trade_id",inplace=True,keep="last")
            self.insert_to_database(Trades,df)



    #populates database with trade quote and bars
    def populate_price_quote_trade(self,start,request_for="bars",timeframe=None,end=str(datetime.datetime.now().strftime('%Y-%m-%d')),save_to="queue",chunk_size=50):
        stocks=self.fetch_stocks_list()
        df=pd.DataFrame(stocks)
        asset_list=df["ticker"].tolist()
        alpaca=Alpaca()
        st=time.perf_counter()
        asset_chuncks=list(divide_chunks(asset_list,chunk_size))
        
        for asset_list in asset_chuncks:
            if request_for == "bars":
                data=alpaca.getData(request_for,asset_list,start=start,end=end,save_to=save_to,timeframe=timeframe)
            elif request_for == "quotes":
                data=alpaca.getData(request_for,asset_list,start=start,end=end,save_to=save_to,)
            else:
                data=alpaca.getData(request_for,asset_list,start=start,end=end,save_to=save_to)
            
            if save_to == "queue" and len(data)>0:
                self.process_data(timeframe,data,request_for)

            print(f"data fetched in {time.perf_counter() - st }")

        

   




    

        



           



         









       




# obj=DataPopulateController()
# obj.populate_assets()





        
















