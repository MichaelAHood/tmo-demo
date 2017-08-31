#!/bin/bash

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
