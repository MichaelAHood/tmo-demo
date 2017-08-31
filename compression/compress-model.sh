#!/bin/bash -xv
# Compresses FaceNet model.

git clone https://github.com/tomasreimers/tensorflow-graph-compression.git
cd tensorflow-graph-compression
time python ./converge_weights.py ../../model/facenet-20170216-091149.pb
mv facenet-20170216-091149.pb.min facenet-20170216-091149-min.pb
zip facenet-20170216-091149-min.zip facenet-20170216-091149-min.pb
