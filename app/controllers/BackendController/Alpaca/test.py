import logging
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL
import sys
import pathlib
import time
import os
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

import app.config as Config

log = logging.getLogger(__name__)



os.environ["APCA_API_KEY_ID"]=Config.ALPACA_API_KEY
os.environ["APCA_API_SECRET_KEY"]=Config.ALPACA_SECRET_KEY
os.environ["APCA_API_BASE_URL"]=Config.ALPACA_API_URL


async def print_bars(b):
    print("hi")
    print('trade', b)


async def print_quote(q):
    print('quote', q)


async def print_trade_update(tu):
    print('trade update', tu)


def main():
    
    logging.basicConfig(level=logging.INFO)
    feed = 'iex'  # <- replace to SIP if you have PRO subscription
    try:
        stream = Stream(data_feed=feed,raw_data=True)
        
        stream.subscribe_quotes(print_bars,'AAPL')



        @stream.on_bar('MSFT')
        async def _(bar):
            print('bar', bar)







        @stream.on_status("*")

        async def _(status):
            print('status', status)
        
        stream.run()

    except Exception as e:
        raise e 




    
 


if __name__ == "__main__":
    main()
