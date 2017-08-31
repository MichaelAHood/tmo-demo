from __future__ import division

import numpy as np
import pandas as pd
import cv2
from scipy import misc
from pprint import pprint
from scipy.spatial.distance import euclidean


def inv_softmax(z, topN):
    # An inverted softmax fucntion that maps faceNet vector distance to probability
    # for the topN closts vectors.
    # A euclidean distance of 0 is equivalent to a p=1.0
    # A euclidean distance of 4 is equivlent to a p=0.0 
    return np.exp(4 - z) / np.exp(4 - topN).sum()

def get_names_and_vectors(docs):
    vectors = []
    names = []
    pins = []
    for doc in docs:
        try:
            vectors.append(doc['vector'])
            names.append(doc['name'])
            pins.append(doc['pin'])
        except:
            continue
    return names, np.array(vectors), pins


def get_distances(img_vector, vectors):
    return np.apply_along_axis(euclidean, 1, vectors, img_vector)

def get_identity(img_vector, docs, is_mxnet=True, verify_pin=False):    
    names, vectors, pins = get_names_and_vectors(docs)
    distances = get_distances(img_vector, vectors)
    threshold = 25.0 if is_mxnet else 1.1
    if verify_pin:
        if distances[distances < threshold].size == 0:
            return "Unknown", None
        try:
            min_ix = np.argmin(distances)
            return names[min_ix], pins[min_ix]
        except:
            return "Unknown"    
    else:
        if distances[distances < threshold].size == 0:
            return "Unknown"
        try:
            return names[np.argmin(distances)]
        except:
            return "Unknown"

def align_image(img, bb, image_size=160):
    cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
    return cv2.resize(cropped, (image_size, image_size))


def new_align_image(img, bounding_boxes, image_size=160, margin=32):
    det = np.array([bounding_boxes])[:,0:4]
    img_size = np.asarray(img.shape)[0:2]
    bounding_box_size = (det[:,2]-det[:,0])*(det[:,3]-det[:,1])
    img_center = img_size / 2
    offsets = np.vstack([ (det[:,0]+det[:,2])/2-img_center[1], (det[:,1]+det[:,3])/2-img_center[0] ])
    offset_dist_squared = np.sum(np.power(offsets,2.0),0)
    index = np.argmax(bounding_box_size-offset_dist_squared*2.0) # some extra weight on the centering
    det = det[index,:]
    det = np.squeeze(det)
    bb = np.zeros(4, dtype=np.int32)
    bb[0] = np.maximum(det[0]-margin/2, 0)
    bb[1] = np.maximum(det[1]-margin/2, 0)
    bb[2] = np.minimum(det[2]+margin/2, img_size[1])
    bb[3] = np.minimum(det[3]+margin/2, img_size[0])
    cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
    scaled = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
    return scaled

def mxnet_face_pre_process_images(images, size):
    processed_images = []
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (size, size)) / 255.
        gray = np.expand_dims(gray, axis=0)
        processed_images.append(gray)
    return np.array(processed_images)  
                            
