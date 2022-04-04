import sys,os,pathlib

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date,DateTime,UniqueConstraint, ForeignKey, Sequence, Text, Boolean, Float, Enum, BigInteger,TIMESTAMP

from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.dialects import postgresql

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.event import listens_for
import enum
from dictalchemy import DictableModel,make_class_dictable



Alpaca_Base = declarative_base()

make_class_dictable(Alpaca_Base)




class Stocks(Alpaca_Base):

    #table_name
    __tablename__="stocks"

    #primary
    unique_id=Column("unique_id",String,primary_key=True)

    #columns
    ticker=Column("ticker",String)
    active=Column("active", Boolean)
    exchange=Column("exchange",String)
    securityType=Column("securityType",String)
    markerSector=Column("markerSector",String)
    name=Column("name",String)
    exchCode=Column("exchCode",String)
    shareClassFIGI=Column("shareClassFIGI",String)
    compositeFIGI=Column("compositeFIGI",String)
    securityType2=Column("securityType2",String)
    securityDescription=Column("securityDescription",String)

    prices_min=relationship("BarMinute",backref="stocks",order_by="desc(BarMinute.timestamp)",lazy="dynamic")
    prices_hour=relationship("BarHour",backref="stocks",order_by="desc(BarHour.timestamp)",lazy="dynamic")
    prices_daily=relationship("BarDaily",backref="stocks",order_by="desc(BarDaily.timestamp)",lazy="dynamic")
    trades=relationship("Trades",backref="stocks",order_by="desc(Trades.timestamp)",lazy="dynamic")
    quotes=relationship("Quotes",backref="stocks",order_by="desc(Quotes.timestamp)",lazy="dynamic")
    
    





class BarMinute(Alpaca_Base):

    #table_name
    __tablename__="bars_minute"


    #constraint
    __table_args__ = tuple([UniqueConstraint('stock_id', "timestamp")])



    id=Column(Integer,index=True,primary_key=True,autoincrement=True)




    #foreign_key

    stock_id=Column("stock_id",ForeignKey('stocks.unique_id',onupdate='CASCADE'))


    #primary
    timestamp=Column("timestamp",TIMESTAMP)
    open=Column("open",Float)
    high=Column("high",Float)
    low=Column("low",Float)
    close=Column("close",Float)
    volume=Column("volume",Float)
    adjusted=Column("adjusted",Boolean,default=False)
  

class BarHour(Alpaca_Base):

    #table_name
    __tablename__="bars_hour"




    id=Column(Integer,index=True,primary_key=True,autoincrement=True)



    #constraint
    __table_args__ = tuple([UniqueConstraint('stock_id', "timestamp")])



    #foreign_key

    stock_id=Column("stock_id",ForeignKey('stocks.unique_id',onupdate='CASCADE'))


    #primary
    timestamp=Column("timestamp",TIMESTAMP)
    open=Column("open",Float)
    high=Column("high",Float)
    low=Column("low",Float)
    close=Column("close",Float)
    volume=Column("volume",Float)
    adjusted=Column("adjusted",Boolean,default=False)
  



class BarDaily(Alpaca_Base):

    #table_name
    __tablename__="bars_daily"






    __table_args__ = tuple([UniqueConstraint('stock_id', "timestamp")])



    id=Column(Integer,index=True,primary_key=True,autoincrement=True)




    #foreign_key 

    stock_id=Column("stock_id",ForeignKey('stocks.unique_id',onupdate='CASCADE'))


    #primary_key
    timestamp=Column("timestamp",TIMESTAMP)

    #columns
    open=Column("open",Float)
    high=Column("high",Float)
    low=Column("low",Float)
    close=Column("close",Float)
    volume=Column("volume",Float)
    adjusted=Column("adjusted",Boolean,default=False)




class Exch(enum.Enum):
    A = "NYSE American (AMEX)"
    B = "NASDAQ OMX BX"
    C = "NAtional Stock Exchange"
    D = "FINRA ADF"
    E = "Market Independent"
    H = "MIAX"
    I = "International Securities Exchange"
    J = "Cboe EDGA"
    K = "Cboe EDGX"
    L = "Long Term Stock Exchange"
    M = "Chicago Stock Exchange"
    N = "New York Stock Exchange"
    P = "NYSE Arca"
    Q = "NASDAQ OMX"
    S = "NASDAQ Small Cap"
    T = "NASDAQ Int"
    U = "Members Exchange"
    V = "IEX"
    W = "CBOE"
    X = "NASDAQ OMX PSX"
    Y = "CboeBYX"
    Z = "CboeBZX"
    NA = "NotKnown"








class Trades(Alpaca_Base):
    #table_name
    __tablename__="trades"
    #foreign_key 
    stock_id=Column(ForeignKey('stocks.unique_id',onupdate='CASCADE'))

    #primary_key
    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #columns
    timestamp=Column("timestamp",TIMESTAMP)
    exchange=Column("exchange",Enum(Exch))
    trade_price=Column("trade_price",Float)
    trade_size=Column("trade_size",Float)
    trade_condition=Column("trade_condition",ARRAY(String))
    trade_id=Column("trade_id",String)
    tape=Column("tape",String)


class Quotes(Alpaca_Base):
       #table_names
    __tablename__="quotes"
    #constraint
    #primary_key
    id=Column(Integer,index=True,primary_key=True,autoincrement=True)
    #foreign_key 
    stock_id=Column(ForeignKey('stocks.unique_id',onupdate='CASCADE'))
    timestamp=Column("timestamp",TIMESTAMP)
    ask_exchange=Column("ask_exchange",Enum(Exch))
    ask_price=Column("ask_price",Float)
    ask_size=Column("ask_size",Integer)
    bid_exchange=Column("bid_exchange",Enum(Exch))
    bid_price=Column("bid_price",Float)
    bid_size=Column("bid_size",Integer)
    quote_condition=Column("quote_condition",ARRAY(String))



class Crons(Alpaca_Base):
    #table_names
    __tablename__="crons"

    #constraint
    __table_args__ = tuple([UniqueConstraint('cron_id')])
 
    #primary_key
    id=Column(Integer,index=True,primary_key=True,autoincrement=True)

    #foreign_key 
    cron_id=Column("cron_id",String)
    cron_type=Column("cron_type",String)
    cron_on=Column("cron_on",String)
    started_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    completed_at=Column("updated_at",DateTime(timezone=True),server_default=func.now())
    cron_status=Column("cron_status",String)
   










