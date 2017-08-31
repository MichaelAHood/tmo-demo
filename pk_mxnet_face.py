import os
import sys
PATH_TO_MXNET = "/Users/mhood/mxnet/python"
sys.path.insert(0, PATH_TO_MXNET)
import cv2
import mxnet as mx
import numpy as np

from lightened_cnn import lightened_cnn_b_feature
from helpers import mxnet_face_pre_process_images


class pkMXNetFace:

	def __init__(self):
		self.epoch = 166
		self.size = 128
		#self.context = mx.cpu(0)
		self.context = mx.gpu(0)
		self.model_args = None
		self.model_auxs = None
		self.symbol = None

	def load_model(self, model_prefix="model/lightened_cnn/lightened_cnn"):
		 _, self.model_args, self.model_auxs = mx.model.load_checkpoint(model_prefix, self.epoch)
		 self.symbol = lightened_cnn_b_feature()
		 print "MXNet-Face loaded."

	def vectorize(self, images):
		data = mxnet_face_pre_process_images(images, self.size)
		self.model_args['data'] = mx.nd.array(data, self.context) 
		exector = self.symbol.bind(self.context, self.model_args ,args_grad=None, grad_req="null", aux_states=self.model_auxs)
		exector.forward(is_train=False)
		exector.outputs[0].wait_to_read()
		return exector.outputs[0].asnumpy()
