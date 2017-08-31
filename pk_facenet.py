from __future__ import absolute_import
from __future__ import division

import tensorflow as tf
import numpy as np
import argparse
import facenet
# from facenet import get_model_filenames, load_model, load_data
import os
import sys
import math
from sklearn import metrics
from scipy.optimize import brentq
from scipy import interpolate

class pkFaceNet:

    def __init__(self):
        self.graph = None
        self.sess = None
        self.images_placeholder = None
        self.phase_train_placeholder = None
        self.embeddings = None
        self.image_size = 160
        self.embedding_size = 128
        self.feed_dict = None



    def load_model(self, model_path="model/20170216-091149" ):
        print "Loading the FaceNet model. This could take a minute."
        
        self.graph = tf.Graph()
        self.sess = tf.Session()

        with self.sess.as_default():
            # Load the model
            if model_path.endswith('.pb'):
                print('Model pb: %s' % model_path)
                with tf.gfile.FastGFile(model_path, 'rb') as f:
                    graph_def = tf.GraphDef()
                    graph_def.ParseFromString(f.read())
                    _ = tf.import_graph_def(graph_def, name='')
            else:
                print('Model directory: %s' % model_path)
                meta_file, ckpt_file = facenet.get_model_filenames(os.path.expanduser(model_path))

                print('Metagraph file: %s' % meta_file)
                print('Checkpoint file: %s' % ckpt_file)
                facenet.load_model(model_path, meta_file, ckpt_file)

            # Get input and output tensors
            self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
         
            print("FaceNet loaded!")




    def vectorize(self, images, do_prewhiten=True, input_is_array=True):
        """
        Input: - image_paths (list of strings); a list of the paths to the images
               that you want to vectorize, i.e. the inputs to FaceNet.
               - image_size (int); the size that you want to use to rescale the images.

        Output: numpy array of 128-d vectors; the output of FaceNet.

        Desc: vectorize is a method that currently takes as input a list of
              images paths and reutrns the FaceNet embeddings of each image. 

        Desired desc: Takes       
        """

        with self.sess.as_default():
            # Replace load_data with an np arrays of images
            if input_is_array == False:
                paths_batch = [(image_path) for image_path in images]
                # print(type(paths_batch), paths_batch.shape)
                images_arr = facenet.load_data(paths_batch, False, False, self.image_size, do_prewhiten, input_is_array)
            else:
                images_arr = facenet.load_data(images, False, False, self.image_size, do_prewhiten, input_is_array)
        
            self.feed_dict = { self.images_placeholder:images_arr, self.phase_train_placeholder:False }
            result = self.sess.run(self.embeddings, feed_dict=self.feed_dict)
        return result

