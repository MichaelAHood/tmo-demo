#!/usr/bin/env python
import os
import cv2
import pandas as pd
import numpy as np
from face_parser import FaceParser
from pk_facenet import pkFaceNet
from pk_mxnet_face import pkMXNetFace
from helpers import get_identity
from datetime import datetime

global BBOX_COLORS
BBOX_COLORS = {"blue" : (255,100,0),
               "green": (0,150,0),
               "red"  : (0, 0, 150)
               }

LOG_FILE_DIRECTORY = "log/log_file.log"

# Check OS environment variable PK_ENABLE_LOGGING to output logging.
pk_enable_logging = False
if os.getenv("PK_ENABLE_LOGGING"):
    pk_enable_logging = True

pk_face_parser = os.getenv("PK_FACE_PARSER")
print "PK_FACE_PARSER: ", pk_face_parser
def setup_face_parser(margin, image_size):
    global fp
    print("Begin setup_face_parser with margin={0} and image_size={1}".format(margin, image_size))
    if pk_face_parser == "mtcnn":
        from face_parser import FaceParser
        fp = FaceParser()
    elif pk_face_parser == "hc":
        from face_parser_hc import FaceParserHC
        fp = FaceParserHC()
    elif pk_face_parser == "hog":
        from face_parser_hog import FaceParserHOG
        fp = FaceParserHOG()
    else:
        from face_parser_hog import FaceParser
        fp = FaceParser()
    # Use margin=16 and size=128 for mxnet
    # Use margin=32 and size=160 for facenet
    fp.load_model(margin, image_size)
    print("end setup_face_parser")

def setup_mxnet_face():
    global mxface
    mxface = pkMXNetFace()
    #pkfn.load_model()
    mxface.load_model(model_prefix="model/lightened_cnn/lightened_cnn")

def setup_facenet():
    global pkfn
    pkfn = pkFaceNet()
    #pkfn.load_model()
    pkfn.load_model(model_path="model/facenet-20170216-091149.pb")

def setup_reference_table():
    global reference_table
    reference_table = pd.read_csv("reference_table.csv")

# Get image face bounding boxes.
# Assume image already greyscaled.
def get_image_fbbs(cv2_image):
    return fp.find_faces(cv2_image, input_is_array=True)

def log_output(name, dir):
    log_output = name + "," + str(datetime.now())
    os.system("echo {0} >> {1}".format(log_output, dir))

# Get image with bounding boxes.
def get_image_with_bbs(cv2_image, 
                       docs=None, 
                       is_mxnet=True, 
                       return_vector=False,
                       classify_face=False, 
                       customer_status="unknown",
                       session_name=None):

    bbs = get_image_bbs(cv2_image)
    faces = fp.extract_faces(cv2_image, bbs)
    # print "Faces: ", faces
    if classify_face:
        if faces:
            # print "Faces detected."
            if is_mxnet:
                face_vecs = mxface.vectorize(faces)
                # print "MXNet output {0} vectors".format(len(face_vecs))
            else:
                face_vecs = pkfn.vectorize(faces)
                # print "FaceNet output {0} vectors".format(len(face_vecs))
        else:
            # If no faces, just return the image, and is_image flag
            return cv2_image, False
    if return_vector:
        bbs_area = []
        face_vecs = pkfn.vectorize(faces)
        for bb in bbs:
            x, y, w, h = bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]
            bbs_area.append((x+w) * (y+h))
        return face_vecs[np.argmax(bbs_area)], True
    # set colors and names here
    if customer_status == "verified":
        assert len(face_vecs) > 0, "There is no face detected."
        names = [get_identity(vec, docs, is_mxnet) for vec in face_vecs]
        for bb, name in zip(bbs, names):
            x, y, w, h = bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]
            if name == session_name:
                cv2.rectangle(cv2_image,(x,y),(x+w,y+h), BBOX_COLORS['green'], 2)
                cv2.putText(cv2_image, name, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            else:
                cv2.rectangle(cv2_image,(x,y),(x+w,y+h), BBOX_COLORS['red'], 2)
                cv2.putText(cv2_image, "Not Authorized", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            if pk_enable_logging:
                log_output(name, LOG_FILE_DIRECTORY)
        return cv2_image, True

    elif customer_status == "unverified":
        names = ["Unknown Customer" for bb in bbs]
        color = BBOX_COLORS['red']
    else:
        customer_status == "unknown"
        names = ["Unknown Customer" for bb in bbs]
        color = BBOX_COLORS['blue']
    
    for bb, name in zip(bbs, names):
        x, y, w, h = bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]
        cv2.rectangle(cv2_image,(x,y),(x+w,y+h), color,2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(cv2_image, name, (x,y), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        if pk_enable_logging:
            log_output(name, LOG_FILE_DIRECTORY)
    return cv2_image, True

def get_image_bbs(cv2_image):
    # Returns the bounding boxes for each face in the image
    return fp.find_faces(cv2_image, input_is_array=True)

# Determines if images have been rotated and fixes them
def check_and_fix(image):
    if image.shape[0] < image.shape[1]:
        return np.transpose(image, (1, 0, 2))
    return image

