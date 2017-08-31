# export PK_ENABLE_MXNET=1
export PK_FACE_PARSER=mtcnn
export PK_FACE_PARSER=hog
export PK_FACE_PARSER=hc
#export PK_FACE_PARSER=mtcnn
#export CUDA_VISIBLE_DEVICES=
#export PK_ENABLE_LOGGING=1

#!/bin/bash

# Uncomment to disable TensorFlow GPU support.
#export CUDA_VISIBLE_DEVICES=
export PK_ENABLE_LOGGING=1

mkdir -p log

if [[ "$1" = "mxnet" ]]
then
  export PK_ENABLE_MXNET=1
fi


./main.py &

cd dashboard

port=8080
url="http://localhost:${port}"

PORT=$port ./server.py &

# Old disabled logic opening up a standalone JavaScript web page.
: '
check_node_http=`which http-server`
if [[ "$check_node_http" != "" ]]
then
  http-server -p $port &
else
  python -m SimpleHTTPServer $port &
fi
'

check_open=`which xdg-open`
if [[ "$check_open" != "" ]]
then
  xdg-open "$url" 2>/dev/null
else
  open "$url"
fi
