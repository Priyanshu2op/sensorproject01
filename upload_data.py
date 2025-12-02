from pymongo.mongo_client import MongoClient
import pandas as pd
import json

# url info
url = "mongodb+srv://priyanshu:d7N25Drm5fLYUyIe@cluster0.gtnrcag.mongodb.net/?appName=Cluster0"


from pymongo.mongo_client import MongoClient

# The url variable will now be updated by the previous cell '7Ghjfxr7AZo4'
# We don't need complex URL parsing if the password does not contain special characters that conflict with URI syntax.
# The new password 'RM3X956ol8L3UORL' should not require escaping.

print(f"Using URL: {url}")

client = MongoClient(url)



# create database name and collection name 
DATABASE_NAME="PRIYANSHU"
COLLECTION_NAME="waferfault"


df=pd.read_csv("D:\sensor project\notebook\wafer_23012020_041211.csv")

df=df.drop("Unnamed: 0",axis=1)
json_record=list(json.loads(df.T.to_json()).values()) 
client[DATABASE_NAME][COLLECTION_NAME].insert_many(json_record)