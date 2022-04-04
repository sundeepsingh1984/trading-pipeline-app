class BarController():
	"""docstring for BarController"""
	def __init__(self):
        self.session , self.sync_session = database_session("Alpaca")
        self.config_loop()


    

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


    async def query_data(self,r_obj,relation,parameter_val=None,start=None,end=None,limit=50000,parameter="ticker"):

        session=self.sync_session()
        if parameter_val and type(parameter_val) == str:

            if start and end:
                q_res=session.query(Forex).filter( getattr(Forex,parameter) ==  parameter_val).join().one()


            else:
                q_res=session.query(Forex).filter( getattr(Forex,parameter) ==  parameter_val).join(r_obj).all()

                print(q_res)




        # if parameter:
        #     if start and end:
        #         my_time = datetime.min.time()
        #         start = datetime.combine(start, my_time)
        #         end=datetime.combine(end,my_time)
        #         data=getattr(q_res,relation).filter(r_obj.datetime.between(start,end)).limit(limit).all()
        #     else:
        #         data=getattr(q_res,relation).limit(limit).all()

        # else:
        #     if start and end:
        #         my_time = datetime.min.time()
        #         start = datetime.combine(start, my_time)
        #         end=datetime.combine(end,my_time)
        #         data=getattr(q_res,relation).filter(r_obj.datetime.between(start,end)).limit(limit).all()

                        
        #     else:
        #         data=getattr(q_res,relation).limit(limit).all()


        data=[dict(d.prices) for d in data]
        return data 


    async def get_bar_min_by_ticker(self,ticker,limit):





	





if __name__=='__main__':

obj=BarController()
obj.