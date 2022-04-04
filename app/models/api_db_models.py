import sys,os,pathlib

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date,DateTime,UniqueConstraint, ForeignKey, Sequence, Text, Boolean, Float, Enum, BigInteger,TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.event import listens_for
import enum
import app.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dictalchemy import DictableModel,make_class_dictable



Base = declarative_base()

make_class_dictable(Base)




class Users(Base):

    __tablename__ = "users"


    id = Column("id",Integer,primary_key=True,index=True)
    name = Column("name",String)
    email = Column("email",String )
    password = Column("password",String)
    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True),server_default=func.now())

    # relations
    strategies=relationship("Strategies",backref="users",order_by='desc(Strategies.created_at)', lazy='dynamic')


class Strategies(Base):

    #table name

    __tablename__="user_strategies"

    #primary key

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)

    # foreign keys
    created_by=Column(Integer,ForeignKey("users.id"))


    # columns
    strategy_name=Column(String,nullable=False)
    backtested=Column(Boolean,default=False)
    backtest_id=Column(ARRAY(Integer))
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    #relations

    backtest_details=relationship("Backtests",backref="user_strategies",order_by='desc(Backtests.backtest_id)', lazy='dynamic')







class Backtests(Base):

    #table name

    __tablename__="backtests"

    #primary key

    backtest_id=Column(Integer,primary_key=True,index=True,autoincrement=True)

    #foreign key
    strategy_id=Column(Integer,ForeignKey("user_strategies.id"))

    #columns

    avg_return_mon=Column(Float, nullable=True)
    sd_monthly=Column(Float,nullable=True)
    avg_return_annual=Column(Float,nullable=True)
    avg_std=Column(Float,nullable=True)
    sharpe_ratio=Column(Float,nullable=True)
    colmar_ratio=Column(Float,nullable=True)
    worst_monthly_drw_dwn=Column(Float,nullable=True)
    best_month_performance=Column(Float,nullable=True)
    worst_drw_down=Column(Float,nullable=True)



class Source(Base):


    __tablename__="source"

     #primary key

    source_id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    source_name=Column(String)


    data_available=relationship("SourceData",backref="source")





class SourceData(Source):
        #table name

    __tablename__="source_data"

    #primary key

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)

    #foreign key
    source_id=Column(Integer,ForeignKey("source.source_id"))
    data_type=Column(String)






