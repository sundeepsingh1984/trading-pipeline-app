import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.config import OPENFIGI_URL, OPENFIGI_KEY
import asyncio
import aiohttp
import ujson
import time
from time import perf_counter
from app.helpers.datatype_helpers import divide_chunks,unwrap
import pandas as pd
import nest_asyncio

class OpenFigi:

    

    def __init__(self):
        self. url = OPENFIGI_URL
        self. key = OPENFIGI_KEY
        self.config_loop()
        self.counter=0

    

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






    async def consume_openfigi(self,job, queue, client):

        openfigi_headers = {'Content-Type': 'text/json'}
        
        if self . key:
            openfigi_headers['X-OPENFIGI-APIKEY'] = self . key

        res = await client.post(self.url, json=job, headers=openfigi_headers)

        if res.status != 200:

            if res.status == 429:
                print(f"bad status {res}")
                print("limit exceeded waiting for a wule to continue")
                time.sleep(60)
                await self.consume_openfigi(job,queue,client)

            else:
                raise ValueError(f"Bad statuscode {res.status=};expected 200")
           


        response=await res.json(loads=ujson.loads)


        for item in response:
            await queue.put(item.get("data"))

    

    async def dispatch_consume_openfigi(self,symbols: list):

        queue: asyncio.Queue[bytes] = asyncio . Queue()
        client = aiohttp. ClientSession()
        jobs = [{"idType": "TICKER", "idValue": symbol}for symbol in symbols]
       

        

        if len(jobs) > 100:
            jobs = list(divide_chunks(jobs, 100))

            listed_jobs=list(divide_chunks(jobs,25))

          
            async with client:
                for jobs in listed_jobs:

                    await asyncio.gather(
                        *(
                            self.consume_openfigi(job, queue, client)
                            for job in jobs
                            )
                        )

                    time.sleep(10)

        else:

            await self.consume_openfigi(jobs,queue,client)
        




        results: List[bytes] = []
        while not queue.empty():


            results.append(await queue.get())
            queue.task_done()

        return results

    


    def get_figi(self, tickers):

        network_io_start = perf_counter()

        raw_results = unwrap(
            asyncio.run(
                self.dispatch_consume_openfigi(tickers)
            )
        )

        network_io_stop = perf_counter()
        print(f"Data retrieved in {network_io_stop-network_io_start:.2f} seconds.")
        print("Performing Transforms...")
        
        df = pd.concat(
            (pd.DataFrame(result_chunk)
             for result_chunk in raw_results),
            ignore_index=True,
        )
        
        return df[df["exchCode"] == "US"]

