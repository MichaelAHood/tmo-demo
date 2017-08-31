# TensorFlow Neural Network Model Compression

## Usage

Using the TensorFlow compression scripts provided by Tomas Reimers, we were able to compress the FaceNet Inception model on a p2.xlarge EC2 instance (1 GPU, 4 vCPU, 61GB memory, 2496 cores, 12GB GPU memory, $0.90/hour) on AWS taking under 8 hours to complete.

Based on the referenced research paper, it produces a model with the same number of nodes but tries to create redundant weights that were originally close in value to allow for better external compression (e.g. zip).  So if anything allows the compressed model to be deploy quicker to smaller footprint platforms etc., but doesn’t necessarily help with performance per se (at least without further work in other areas of graph compression).

```bash
# Example compress script with commands below in compress-model.sh.
# Assumes original FaceNet model in parent model directory along with TensorFlow installed.
$ git clone https://github.com/tomasreimers/tensorflow-graph-compression.git
$ cd tensorflow-graph-compression
$ time python ./converge_weights.py ../../model/facenet-20170216-091149.pb
$ mv facenet-20170216-091149.pb.min facenet-20170216-091149-min.pb

Model is the same size uncompressed:

$ ls -lh facenet*pb
-rw-r--r--  1 jbond  staff    89M May 12 17:22 facenet-20170216-091149-min.pb
-rw-r--r--  1 jbond  staff    89M May  9 01:01 facenet-20170216-091149.pb

But compressed you can see the savings:

$ ls -lh *.zip
-rw-r--r--  1 jbond  staff    35M May 17 14:29 facenet-20170216-091149-min.zip
-rw-r--r--  1 jbond  staff    81M May 12 22:07 facenet-20170216-091149.zip
```

We haven’t thoroughly tested the compressed model, but seems to have similar performance/accuracy on the surface testing it with our video facial detection app.

Models uploaded to Analytics SharePoint at:

https://prokarma001.sharepoint.com/usa/advancedanalytics/Shared%20Documents/Forms/AllItems.aspx?id=%2Fusa%2Fadvancedanalytics%2FShared%20Documents%2FInternal%2FProducts%2FTensorFlow


## References

- https://medium.com/@tomasreimers/when-smallers-better-4b54cedc3402
- https://github.com/tomasreimers/tensorflow-graph-compression
- https://arxiv.org/abs/1510.00149
