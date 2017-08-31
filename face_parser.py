from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from scipy import misc
import sys
import os
import argparse
import tensorflow as tf
import numpy as np
import facenet
import align.detect_face
import random
from time import sleep
import cv2
from helpers import new_align_image
# import png



class FaceParser:
    
    def __init__(self):
        self.margin = None
        self.image_size = None
        self.gpu_memory_fraction = None
        self.pnet = None
        self.rnet = None
        self.onet = None
        self.minsize = None
        self.threshold = None
        self.factor = None
        self.sess = None

        self.path = None
        self.images = []
        self.number_of_images = None
        # self.face_bounding_boxes = None
    

    def load_model(self, margin=32, image_size=160, gpu_memory_fraction=0.25):

        print("Creating networks and loading parameters")
        self.margin = margin
        self.image_size = image_size
        self.gpu_memory_fraction = gpu_memory_fraction

        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
            self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.sess, None)
        
        self.minsize = 20 # minimum size of face
        self.threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
        self.factor = 0.709 # scale factor  

        print("FaceDetection Model loaded!")


    def find_faces(self, image, input_is_array=True):
    
    # Input:  The path of the image that you want to parse.
    # Output: A list of numpy arrays for each face in the image.
    # Desc:   get_faces is a method that extracts all of the faces in an
    #         image as numpy arrays.

        # print("Finding Faces.")
        # Read in the iamge
        if input_is_array == True:
            img = image
        else:
            img = cv2.imread(image)
        # Takes an image np array as input and outputs bbs
        
        raw_bounding_boxes, _ = align.detect_face.detect_face(img, 
                                                              self.minsize, 
                                                              self.pnet, 
                                                              self.rnet, 
                                                              self.onet, 
                                                              self.threshold, 
                                                              self.factor)
        
        nrof_faces = raw_bounding_boxes.shape[0]
        #DBG print("Found {0} faces in the image.".format(nrof_faces))
        return np.rint(np.array(raw_bounding_boxes)).astype(int).tolist()

    
    def extract_faces(self, image, bounding_boxes):
        extracted_faces = []
        for bounding_box in bounding_boxes:
            aligned_image = new_align_image(image, bounding_box)
            extracted_faces.append(aligned_image)
        return extracted_faces


    def save_images(self, parsed_images_dir, image_name):
        num_images_written = 0
        for i, image in enumerate(self.images):
            # Scale the images to 160 x 160
            scaled = misc.imresize(image, (160, 160), interp='bilinear')
            try:
                png.from_array(scaled, 'RGB').save(parsed_images_dir + '/' + image_name)
                num_images_written += 1
            except:
                continue
        print("Successfully wrote {0} of {1} parsed images".format(num_images_written, self.number_of_images))







