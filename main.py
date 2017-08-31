#!/usr/bin/env python
# main.py
from datetime import timedelta
import os
import sys
import cv2
import numpy as np
import platform
import requests
from custom_timer import CustomTimer
from flask import Flask, current_app, make_response, render_template, request, Response
import logging
from functools import update_wrapper
from pymongo import MongoClient
from helpers import get_identity, get_distances

DB_HOST = "mongodb://127.0.0.1:27017"
DB_NAME = "test"
LOG_FILE_DIRECTORY = "log/log_file.log"
# Required image size of Facenet, resize before sending to Facenet as network optimization.
IMAGE_SIZE = 160
VIDEO_SIZE = (640, 360)

# Check OS environment variable PK_ENABLE_WS to run with Flask web service.
pk_enable_ws = False
if os.getenv("PK_ENABLE_WS"):
    pk_enable_ws = True

mxnet_face_model = False
COLLECTION_NAME = "face"
if os.getenv("PK_ENABLE_MXNET"):
    mxnet_face_model = True
    COLLECTION_NAME = "mxnet"

def setup(mxnet_face_model):
    # Set up global camera object to be used for subsequent requests.
    global g_camera
    g_camera = VideoCamera()
    global CUSTOMER_STATUS
    CUSTOMER_STATUS = "unknown"
    print CUSTOMER_STATUS
    global SESSION_NAME
    SESSION_NAME = None
    # If web services not enabled, then import/run required facenet services locally.
    setup_db_connection(DB_HOST)
    if not pk_enable_ws:
        global pfs
        import pk_facenet_service as pfs
        if mxnet_face_model:
            pfs.setup_face_parser(margin=8, image_size=128)
            pfs.setup_mxnet_face()
        else:
            pfs.setup_face_parser(margin=32, image_size=160)
            pfs.setup_facenet()
            

def setup_db_connection(host, is_Mongo=True):
    print "Connecting to Mongo DB"
    global CLIENT
    CLIENT = MongoClient(host)

def facenet_classify_image_bbs(cv2_image):
    facenet_result = None
    cv2_image_resized = cv2.resize(cv2_image, (IMAGE_SIZE, IMAGE_SIZE))
    cv2_image_string = cv2.imencode('.png', cv2_image_resized)[1].tostring()
    response = requests.post('http://localhost:5000/get-image-facenet', files={'image_data': cv2_image_string})
    facenet_result = np.asarray(response.json())
    return facenet_result

def facenet_classify_image_data(cv2_image, docs, is_mxnet=mxnet_face_model, return_vector=False, classify_face=False, customer_status="unknown", session_name=None):
    facenet_result = None
    if pk_enable_ws:
        cv2_image_string = cv2.imencode('.png', cv2_image)[1].tostring()
        response = requests.post('http://localhost:5000/get-image-with-bbs', files={'image_data': cv2_image_string})
        file_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
        facenet_result = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED), False
    else:
        # print "facenet_classify_image_data: Classify Face ", classify_face
        facenet_result = pfs.get_image_with_bbs(cv2_image, docs, 
                                                is_mxnet=mxnet_face_model, 
                                                return_vector=False,
                                                classify_face=classify_face, 
                                                customer_status=customer_status,
                                                session_name=session_name)
    return facenet_result

def facenet_get_classified_image(cv2_image, docs, classify_face, customer_status, session_name=None):
    facenet_result = None
    cv2_image_resized = cv2.resize(cv2_image, VIDEO_SIZE)
    # print "facenet_get_classified_image: Classify Face ", classify_face
    facenet_result = facenet_classify_image_data(cv2_image_resized, docs, 
                                                 classify_face=classify_face, 
                                                 customer_status=customer_status,
                                                 session_name=session_name)
    return facenet_result 

# def get_frame(self, VideoCaptureObj):
#     success, image = VideoCaptureObj.read()
#     img = facenet_get_classified_image(image)
#     return img

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        #self.video = cv2.VideoCapture(0)
        self.setup_camera()
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
        print "Starting Camera"
    def __del__(self):
        self.video.release()

    def setup_camera(self):
        uname = platform.uname()
        print("platform.uname:", uname)
        video_spec = 0
        if any("Darwin" in name for name in uname):
            print("Darwin detected")
            video_spec = 0
        elif any("tegra" in name for name in uname):
            print("tegra detected")
            video_spec = "nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720,format=(string)I420, framerate=(fraction)24/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
        else:
            print("Unknown")

        print("Opening camera:", video_spec)
        self.video = cv2.VideoCapture(video_spec)

    def get_frame(self, docs=None, return_raw_image=False, classify_face=False, customer_status="unknown", session_name=None):
        success, raw_image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        if return_raw_image:
            image = cv2.resize(raw_image, VIDEO_SIZE)
            return image
        else:
            # Predict and write result to image
            image, _ = facenet_get_classified_image(raw_image, docs, 
                                                    classify_face=classify_face, 
                                                    customer_status=customer_status,
                                                    session_name=session_name)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

def get_docs(client, db_name, collection_name):
    db = client[db_name]
    coll = db[collection_name]
    docs = [doc for doc in coll.find()]
    return docs

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Add Flask cross domain support for AJAX XHR requests.
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    docs = get_docs(CLIENT, DB_NAME, COLLECTION_NAME)
    print "{0} documents received from Mogno".format(len(docs))
    timer = CustomTimer(interval=5.0, function=get_docs, args=[CLIENT, DB_NAME, COLLECTION_NAME])
    timer.start()

    while True:
        frame = camera.get_frame(docs)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        #  If the timer interval is expired...
        if timer.isAlive() == False:
            # Get the return value of get_cursor as the new cursor
            docs = timer.join()
            # Overwrite the old timer with a new timer
            timer = CustomTimer(interval=5.0, function=get_docs, args=[CLIENT, DB_NAME, COLLECTION_NAME])
            timer.start()

@app.route('/video_frame')
@crossdomain(origin='*')
def video_frame():
    global g_camera
    global CUSTOMER_STATUS
    global SESSION_NAME
    docs = get_docs(CLIENT, DB_NAME, COLLECTION_NAME)
    if CUSTOMER_STATUS == "unknown":
        frame = g_camera.get_frame(docs, return_raw_image=False, classify_face=False, customer_status=CUSTOMER_STATUS)
        return Response(frame, mimetype='image/jpeg')
    frame = g_camera.get_frame(docs, return_raw_image=False, classify_face=True, customer_status=CUSTOMER_STATUS, session_name=SESSION_NAME)
    return Response(frame, mimetype='image/jpeg')

@app.route('/register_face', methods=['GET', 'POST'])
@crossdomain(origin='*')
def register_face():
    name = request.values.get("name")
    pin = request.values.get("pin").replace('-', '')
    frame = g_camera.get_frame(return_raw_image=True)
    print "Frame: ", frame.shape
    vector, return_status = pfs.get_image_with_bbs(frame, is_mxnet=mxnet_face_model, return_vector=True)
    print vector.shape, return_status
    collection = MongoClient(DB_HOST)[DB_NAME][COLLECTION_NAME]
    if return_status == True:
        new_doc = {"name": name,
                   "vector": vector.tolist(),
                   "pin": pin}
        collection.update_many({"name":name}, 
                               {"$set": {"pin":pin,
                                         "vector": vector.tolist()}}, upsert=True)  
        return Response("{0} added to records.".format(name))    
    return Response("Unable to locate a face in the camera. Try another perspective.".format(name))

@app.route('/lookup_face', methods=['GET', 'POST'])
@crossdomain(origin='*')
def lookup_face():
    global CUSTOMER_STATUS
    global SESSION_NAME
    submitted_name = request.values.get("name")
    submitted_account = request.values.get("account")
    submitted_pin = request.values.get("pin").replace('-', '')

    frame = g_camera.get_frame(return_raw_image=True)
    vector, return_status = pfs.get_image_with_bbs(frame, 
                                                   is_mxnet=mxnet_face_model, 
                                                   return_vector=True,
                                                   classify_face=True,
                                                   customer_status=CUSTOMER_STATUS,
                                                   session_name=SESSION_NAME)
    
    collection = MongoClient(DB_HOST)[DB_NAME][COLLECTION_NAME]
    if return_status == True:
        records = list(collection.find({"name": submitted_name}))
        if not records:
            return Response("Number not found. Unable to authenticate customer.")
        record_vec = np.array(records[0]['vector']).reshape((1, 128))
        similarity = get_distances(record_vec, vector.reshape((1, 128)))
        is_similar_img =  similarity < 1.1
        is_correct_pin = records[0]["pin"] == submitted_pin
        if is_correct_pin and is_similar_img:
            CUSTOMER_STATUS = "verified"
            SESSION_NAME = submitted_name
            return Response("{0} was verified.".format(submitted_name))
        else:
            CUSTOMER_STATUS = "unverified"
            return Response("Customer not authenticated. Number Status: {0}, Facial Recognition Status: {1} -- Image similarity is {2}".format(is_correct_pin, 
                                                                                                                                            is_similar_img,
                                                                                                                                            similarity))
    no_face_detected_response = "Unable to verify identity. No face was detected."
    return Response(no_face_detected_response)

@app.route('/reset_pin', methods=['GET', 'POST'])
@crossdomain(origin='*')
def reset_pin():
    name = response.get('name')
    pin = response.get('pin')
    collection = MongoClient(DB_HOST)[DB_NAME][COLLECTION_NAME]
    collection.update_many({"name":name}, {"$set": {"pin":pin}}, upsert=True)  
    return Response("Pin reset for {0}.".format(name)) 
    

@app.route('/reset_session', methods=['GET', 'POST'])
@crossdomain(origin='*')
def reset_session():
    global CUSTOMER_STATUS
    CUSTOMER_STATUS = "unknown"
    global SESSION_NAME
    SESSION_NAME = None
    return Response("Customer Session Reset")

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.errorhandler(Exception)
def all_exception_handler(error):
    print('Error:', error)
    return 'Error', 500

if __name__ == '__main__':

    setup(mxnet_face_model)
    exit = False
    while not exit:
        try:
            print("Starting app...")
            app.run(host='0.0.0.0', debug=False)
            exit = True
        except:
            print("Unexpected error:", sys.exc_info()[0])
