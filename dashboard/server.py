#!/usr/bin/env python

from datetime import datetime
import os
import json
import logging
from random import randint
from pymongo import MongoClient
from flask import Flask, url_for, request, send_from_directory, make_response
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

g_face_log_path = "../log/log_file.log"
g_face_log_fp = None
g_face_reference_path = "../reference_table.csv"
g_face_reference = {}
g_mongo_client = MongoClient("mongodb://localhost:27017/")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def css(path):
    return send_from_directory('static/css', path)

@app.route('/images/<path:path>')
def images(path):
    return send_from_directory('static/images', path)

@app.route('/register-face', methods=["GET", "POST"])
def register_face():
    #DBG name = request.values.get("name")
    return str(request.values)

@app.route('/get-face-logs', methods=["GET", "POST"])
def get_face_logs():
    global g_face_log_path, g_face_log_fp
    #DBG request_values = request.values
    #DBG name = request_values.get("name")

    '''
    # Read references from csv.
    if os.path.isfile(g_face_reference_path) and not g_face_reference:
        with open(g_face_reference_path, "r") as fr_fp:
            for line in fr_fp:
                if line.startswith("name"):
                    continue
                fr_fields = line.split(",")
                fr_name = fr_fields[0]
                fr_linkedin_url = fr_fields[1]
                g_face_reference[fr_name] = fr_linkedin_url
    '''
    # Read references from mongodb.
    db = g_mongo_client["test"]
    collection = db["face"]
    for rec in collection.find():
        #DBG print("DBG _id:", rec["_id"])
        #DBG print(rec)
        fr_name = rec.get("name")
        fr_linkedin_url = rec.get("linked_in")
        #DBG print("DBG name:", fr_name)
        #DBG print("DBG linked_in:", fr_linkedin_url)
        g_face_reference[fr_name] = fr_linkedin_url


    log_content = []
    if os.path.isfile(g_face_log_path):
        '''
        with open(g_face_log_path, 'r') as log_file:
            #log_content = log_file.read()
            log_content = log_file.readlines()
        '''
        if not g_face_log_fp:
            g_face_log_fp = open(g_face_log_path, "r")
        g_face_log_fp.seek(0, 1)
        for line in g_face_log_fp:
            #DBG print("log:", line)
            log_content.append(line.rstrip())

        # DBG Generate some dummy data if no data for testing purposes.
        '''
        if True and len(log_content) is 0:
            max = 3
            num_logs = randint(0,max)
            name_pool = g_face_reference.keys()
            for i in range(num_logs):
                pool_len = len(name_pool)
                if pool_len > 0:
                    rand_index = randint(0,pool_len-1)
                    log_name = name_pool[rand_index]
                    del name_pool[rand_index]
                else:
                    log_name = "Unknown"
                #DBG log_time = "2017-05-25 16:20:40.285979"
                log_time = str(datetime.now())
                log_record = log_name + "," + log_time
                log_content.append(log_record)
        '''

    # Append additional reference info (linkedin url) if available.
    for index, value in enumerate(log_content):
        log_fields = value.split(",")
        log_name = log_fields[0]
        log_time = log_fields[1]
        log_linkedin_url = g_face_reference.get(log_name);
        if log_linkedin_url:
            log_content[index] = log_name + "," + log_time + "," + log_linkedin_url

    response = make_response(json.dumps(log_content))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/login')
def login():
    return 'login'
    pass

@app.route('/user/<username>')
def profile(username):
    return 'profile'
    pass

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    return 'length: ' + str(len(request.get_data()))

@app.after_request
def add_header(response):
    response.cache_control.max_age = 1
    response.cache_control.public = True
    response.headers['Cache-Control'] = 'no-store'
    return response

with app.test_request_context():
    print url_for('index')
    print url_for('login')
    print url_for('login', next='/')
    print url_for('profile', username='John Doe')
    print url_for('static', filename='style.css')

PORT = int(os.getenv('PORT', 8080))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1
app.run(host='0.0.0.0', port=PORT, debug=True)
