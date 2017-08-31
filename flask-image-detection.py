#!/usr/bin/env python

import sys
import cv2
import pandas as pd
import numpy as np
from face_parser import FaceParser
from pk_facenet import pkFaceNet
from helpers import get_identity
import json
import urllib, cStringIO
import ssl
import pk_facenet_service as pfs

from flask import Flask, url_for, request, make_response
app = Flask(__name__)

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)


# Flask Routes

@app.route('/')
def index():
    return 'hello'
    pass

@app.route('/login')
def login():
    return 'login'
    pass

@app.route('/user/<username>')
def profile(username):
    return 'profile'
    pass

@app.route('/get-image-with-bbs', methods=['GET', 'POST'])
def fl_get_image_with_bbs():
    # This returns an image with bbs superimposed on it
    if "image_url" in request.form.keys() and request.form['image_url']:
        image_url = request.form['image_url']
        image_data = urllib.urlopen(image_url, context=gcontext).read()
    else:
        image_data = request.files['image_data'].read()
    file_bytes = np.asarray(bytearray(image_data), dtype=np.uint8)
    cv2_image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    bbs = pfs.get_image_bbs(cv2_image)
    faces = pfs.fp.extract_faces(cv2_image, bbs)
    face_vecs = pfs.pkfn.vectorize(faces)
    names = [get_identity(vec, pfs.reference_table) for vec in face_vecs]

    cv2_image_result = pfs.get_image_with_bbs(cv2_image)
    cv2_image_string = cv2.imencode('.png', cv2_image_result)[1].tostring()
    #DBG print('length:', len(cv2_image_string))
    response = make_response(cv2_image_string)
    response.headers['Content-Type'] = 'image/png'
    # response.headers['Content-Disposition'] = 'attachment; filename=image_result.jpg'
    return response


@app.route('/get-image-bbs', methods=['GET', 'POST'])
def fl_get_image_bbs():
    # This returns the bbs as JSON
    if "image_url" in request.form.keys() and request.form['image_url']:
        image_url = request.form['image_url']
        image_data = urllib.urlopen(image_url, context=gcontext).read()
    else:
        image_data = request.files['image_data'].read()
    file_bytes = np.asarray(bytearray(image_data), dtype=np.uint8)
    cv2_image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    # Pass the pkfn vectorizer obj, the image array, and the reference data frame
    bbs = pfs.get_image_bbs(cv2_image)
    faces = pfs.fp.extract_faces(cv2_image, bbs)
    face_vecs = pfs.pkfn.vectorize(faces)
    names = [get_identity(vec, pfs.reference_table) for vec in face_vecs]
    response = make_response(json.dumps(names))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.errorhandler(Exception)
def all_exception_handler(error):
    print('Error:', error)
    return 'Error', 500

with app.test_request_context():
    print url_for('index')
    print url_for('login')
    print url_for('login', next='/')
    print url_for('profile', username='John Doe')
    print url_for('static', filename='style.css')

if __name__ == '__main__':
    pfs.setup_face_parser()
    pfs.setup_facenet()
    pfs.setup_reference_table()
    #app.run(host='0.0.0.0', debug=True)
    exit = False
    while not exit:
        try:
            app.run(host='0.0.0.0')
            exit = True
        #except (KeyboardInterrupt, SystemExit):
            #exit = True
        except:
            print("Unexpected error:", sys.exc_info()[0])

