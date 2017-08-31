from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from scipy import misc
import sys
import os
import argparse
import numpy as np
import random
from time import sleep
import cv2
from helpers import new_align_image
# import png



class FaceParserHC:

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



    # Get image face bounding boxes.
    # Assume image already greyscaled.
    def get_image_fbbs(self, cv2_image):
        fbbs = self.face_cascade.detectMultiScale(cv2_image, 1.3, 5)
        return fbbs


    # Get image eye bounding boxes.
    # Assume image already greyscaled.
    def get_image_ebbs(self, cv2_image):
        ebbs = self.eye_cascade.detectMultiScale(cv2_image)
        return ebbs

    def load_model(self, margin=32, image_size=160, gpu_memory_fraction=0.25):

        print("Loading FaceParserHC Model...")
        self.margin = margin
        self.image_size = image_size

        #self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(os.path.dirname(cv2.__file__) + '/../../../share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            self.face_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/testdata/cv/cascadeandhog/cascades/haarcascade_frontalface_default.xml')
        #self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        self.eye_cascade = cv2.CascadeClassifier(os.path.dirname(cv2.__file__) + '/../../../share/OpenCV/haarcascades/haarcascade_eye.xml')
        if self.eye_cascade.empty():
            self.eye_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_eye.xml')

        print("Loaded FaceParserHC Model!")


    def find_faces(self, image, input_is_array=True):

    # Input:  The path of the image that you want to parse.
    # Output: A list of numpy arrays for each face in the image.
    # Desc:   get_faces is a method that extracts all of the faces in an
    #         image as numpy arrays.


        # Read in the image.
        if input_is_array == True:
            img = image
        else:
            img = cv2.imread(image)
        # Takes an image np array as input and outputs bbs
        raw_bounding_boxes = self.face_cascade.detectMultiScale(img, 1.3, 5)
        #DBG print("type(raw_bounding_boxes):", type(raw_bounding_boxes))
        #DBG print("raw_bounding_boxes:", raw_bounding_boxes)

        bounding_boxes = []
        for (x, y, w, h) in raw_bounding_boxes:
            bounding_boxes.append([x, y, x+w, y+h, 1])
        #DBG print("bounding_boxes: ", bounding_boxes)

        return bounding_boxes


    def extract_faces(self, image, bounding_boxes):
        extracted_faces = []
        for bounding_box in bounding_boxes:
            #DBG print("bounding_box:", bounding_box)
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