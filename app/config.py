
from starlette.config import Config
from starlette.datastructures import Secret,URL
import pathlib
import sys
import logging
  

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))

basepath=str(pathlib.Path(__file__).resolve().parents[0])


"""
--------------------------------------------------------------------------------------------------------------------------------------

                                                         APP CONFIG

-------------------------------------------------------------------------------------------------------------------------------------

"""
ROOT_DIR="/app/"
config = Config(basepath+"/.env")

PROJECT_NAME = "Trading-app"
VERSION = "1.0.0"
API_PREFIX = "/api"
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")

ASSET_DIR=config("ASSET_DIR", cast=str, default=str(pathlib.Path(__file__).resolve().parents[1])+ROOT_DIR+"assets")

TEMPLATE_DIR=config("TEMPLATE_DIR", cast=str, default=str(pathlib.Path(__file__).resolve().parents[1])+ROOT_DIR+"views")

SP_DIR=config("TEMPLATE_DIR", cast=str, default=str(pathlib.Path(__file__).resolve().parents[1])+ROOT_DIR+"assets/file-system/sandp500.csv")


sys.path.append(str(pathlib.Path(__file__).resolve().parents[2])+ROOT_DIR)
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2])+ASSET_DIR)
"""
----------------------------------------------------------------------------------------------------------------------------

                                                      DATABASE CONFIG DETAILS

---------------------------------------------------------------------------------------------------------------------------------
"""
POSTGRES_USER = config("DB_USER", cast=str)
POSTGRES_PASSWORD = config("DB_PASSWORD", cast=Secret ,default="Sunny@123")
POSTGRES_SERVER = config("DB_HOST", cast=str)
POSTGRES_PORT = config("DB_PORT", cast=str)
POSTGRES_DB = config("API_DB", cast=str)
POSTGRES_DB_ALPACA=config("DB_NAME_ALPACA", cast=str)

DATABASE_URL_ASYNC = config(
    "DB_URL",
    cast=URL,
    default=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

DATABASE_URL = config(
    "DB_URL",
    cast=URL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


DATABASE_URL_ALPACA = config(
    "DB_URL",
    cast=URL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB_ALPACA}"
)

DATABASE_URL_ALPACA_ASYNC = config(
    "DB_URL",
    cast=URL,
    default=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)



"""
--------------------------------------------------------------------------------------------------------------------------------------------------
                                                       OPENFIGI CONFIG DETAILS
--------------------------------------------------------------------------------------------------------------------------------------------------

"""
OPENFIGI_URL = config("OPEN_FIGI_URL", cast=str,default="")
OPENFIGI_KEY = config("OPEN_FIGI_KEY", cast=str,default="")




"""
--------------------------------------------------------------------------------------------------------------------------------------------------
                ALPACA DETAILS
--------------------------------------------------------------------------------------------------------------------------------------------------

"""

ALPACA_API_URL = 'https://paper-api.alpaca.markets'
ALPACA_API_KEY = 'PKSA9BSJ33EP1KEOZS5J'
ALPACA_SECRET_KEY = 'owQnQPqUPPx30Pz52NYGyXCtrIoZ8UzwffAjKszg'
ALPACA_DATA_URL="https://data.alpaca.markets/v2"




#Loggers Config

ALPACA_LOG_FILE="alpaca.log"
ALPACA_LOG_HANDLER=logging.FileHandler(ALPACA_LOG_FILE)
LOGGER_LEVEL=ALPACA_LOG_HANDLER.setLevel(logging.DEBUG)
LOG_FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ALPACA_LOG_HANDLER.setFormatter(LOG_FORMAT)



#file System Directory


FILE_SYSTEM_DIR={
"ALPACA":"D:\\trading-final\Trading-final\\trading\\app\db\FILE-DB\Alpaca",
"ALPACA_READER":"\{}\{}\{}\{}"


}


#Logs
FILE_NAME="/logging.ini"

LOG_CONF_FILE=basepath+FILE_NAME