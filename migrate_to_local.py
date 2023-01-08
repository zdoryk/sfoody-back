import pymongo
from env_variables import MONGO_LOGIN, MONGO_PASS

# Replace MONGO_LOGIN and MONGO_PASS with your MongoDB Atlas login and password
client = pymongo.MongoClient(
    f"mongodb+srv://{MONGO_LOGIN}:{MONGO_PASS}@sfoodie.mexl1zk.mongodb.net/?retryWrites=true&w=majority"
)

# Connect to the 'Sfoodie' database on the MongoDB Atlas cluster
cloud_db = client["Sfoodie"]


# Connect to a local MongoDB server running on the default port
local_client = pymongo.MongoClient()

# Get a reference to the local "Sfoodie" database
local_db = local_client['Sfoodie']

# Copy the collections
local_db['USERS'].insert_many(cloud_db['USERS'].find())
local_db['Products'].insert_many(cloud_db['Products'].find())
local_db['Receipts'].insert_many(cloud_db['Receipts'].find())