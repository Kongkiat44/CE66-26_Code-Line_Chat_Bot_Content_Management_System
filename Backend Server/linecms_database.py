from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os, pprint

# database connection string
MONGODB_CLIENTSTR = os.getenv("MONGODB_CLIENTSTR")

# function for creating new client to connect MongoDB
def getdbclient():
    return MongoClient(MONGODB_CLIENTSTR)

# function for testing connection by sending ping to database
def isconnect(dbclient:MongoClient):
    try:
        dbclient.admin.command('ping')    
    except Exception as e:
        return False, str(e)
    return True, 'successfully connect to MongoDB'




