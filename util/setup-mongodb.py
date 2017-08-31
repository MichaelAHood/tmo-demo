#!/usr/bin/env python
# 

import pprint
from pymongo import MongoClient
import numpy as np

#client = MongoClient('localhost', 27017)
client = MongoClient("mongodb://localhost:27017/")

db = client["test"]

collection = db["face"]

post = {"name": "test",
        "vector": np.random.random(size=(1,128)).tolist()
       }

post_id = collection.insert_one(post).inserted_id
print("DBG post_id:", post_id)

print("DBG posts:", db.collection_names(include_system_collections=False))

for post in collection.find():
    print("DBG _id:", post["_id"])
    pprint.pprint(post)

print("DBG count:", collection.find({"name": "test"}).count())
