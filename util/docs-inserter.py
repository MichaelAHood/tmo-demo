import sys
import pandas as pd
import numpy as np
from pymongo import MongoClient

reference_csv, drop_collection, is_mxnet = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

DB_HOST = "mongodb://127.0.0.1:27017"
DB_NAME = "test"

if is_mxnet == 1:
	COLLECTION_NAME = "mxnet"
else:
	COLLECTION_NAME = "face"

client = MongoClient(DB_HOST)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

mongo_docs = [doc for doc in collection.find()]
print "{0} docs found in Mongo".format(len(mongo_docs))
print "\n" 
if drop_collection == 1:
	print "Removing Mongo docs"
	print "\n"
	collection.remove({})
	mongo_docs = [doc for doc in collection.find()]
	print "After removing docs, {0} docs found in Mongo".format(len(mongo_docs))
	print "\n"

df = pd.read_csv(reference_csv)
docs = []

for row in df.iterrows():
	name = row[1][0].replace('_', ' ')
	linked_in = row[1][1]
	pin = row[1][2]
	vector = row[1][3:].values.tolist()
	
	doc = {"name": name,
	       "linked_in": linked_in,
	       "vector": vector,
	       "pin": pin}
	docs.append(doc)

# insert docs
print "Inserting docs into Mongo"
print "\n"
for doc in docs:
	collection.insert_one(doc)

mongo_docs = [doc for doc in collection.find()]
import random
print "Here is a sample doc: ", mongo_docs[random.choice(range(len(mongo_docs)))]
print "{0} docs are now in Mongo".format(len(mongo_docs))