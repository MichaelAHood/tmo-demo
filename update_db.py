import sys, os, glob
import pandas as pd
import numpy as np
import cv2
import time

# To make sure that we can import these 
sys.path.insert(0, "/Users/mhood/repos/ai-video/facenet")
from face_parser import FaceParser
from pk_facenet import pkFaceNet
from helpers import get_distances
import pymongo

# Defaults
PHOTO_DIRECTORY = "/Users/mhood/Pictures/Photo Booth Library/Pictures"
MODEL_PATH = "model/facenet-20170216-091149.pb"
DB_HOST = "mongodb://127.0.0.1:27017"

# Capture Photo & Meta Data, e.g. name, etc
def get_most_recent_photo(directory=PHOTO_DIRECTORY):
    list_of_files = glob.glob(directory + '/*.jpg') 
    # Assuming the most recent photo you took is the one you want
    return max(list_of_files, key=os.path.getctime)

# Compare filename(photoname-timestamp) to see if there is a new image
def is_new_image(last_image_taken, most_recent_image):
	if last_image_taken == most_recent_image:
		return False
	return True

def setup_models():
	global fp
	fp = FaceParser()
	fp.load_model()
	global pkfn
	pkfn = pkFaceNet()
	pkfn.load_model(model_path=MODEL_PATH)

def get_face(img_path):
	img = cv2.imread(img_path)
	bbs = fp.find_faces(img, input_is_array=True)
	return fp.extract_faces(img, bbs)

def get_name():
    name = raw_input("What is the name of the person in this photo? ")
    return name

def get_company():
    company = raw_input("What organization is the person in this photo affiliated with? ")
    return company

def get_contact():
    contact = raw_input("What is a good contact? ")
    return contact

def get_meta_data():
	return get_name(), get_company(), get_contact()

def create_mongo_doc(name, company, contact, vector):
    new_doc = {"name": name,
                "company": company,
                "contact": contact,
                "vector": vector}
    return new_doc


def start_checker(db):
	last_image_taken = None
	while True:
		time.sleep(0.5)
		most_recent_image = get_most_recent_photo()
		if is_new_image(last_image_taken, most_recent_image):
			last_image_taken = most_recent_image
			face = get_face(most_recent_image)
			try:
				img_vector = pkfn.vectorize(face)[0].tolist()
			except:
				print "Unabel to find a face."
				continue
			# get all face_vectors and see if anyone is below 1.1
			cursor = db.face.find()
			# docs = [doc for doc in cursor]
			# print len(docs)
			# print docs[0]
			distances = get_distances(cursor, img_vector)
			if distances[distances < 1.1].size > 0:
				answer = raw_input("It looks like you're in the databse. Are you sure you want to make a new entry? ('y' or 'n') ")
				if answer in ["y", "Y"]:
					print "Let's collect some information."
					name, company, contact = get_meta_data()
					new_doc = create_mongo_doc(name, company, contact, img_vector)
					db.face.insert_one(new_doc)
				else:
					continue
			else:
				# No similiar face vectors were found, so add a new one.
				print "Let's collect some information."
				name, company, contact = get_meta_data()
				new_doc = create_mongo_doc(name, company, contact, img_vector)
				db.face.insert_one(new_doc)

if __name__ == '__main__':
	client = pymongo.MongoClient(DB_HOST)
	db = client.test
	setup_models()
	start_checker(db)





