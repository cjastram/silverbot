#!/bin/bash

if test -f run.pid
then
    pid=`cat run.pid`
    if ps -p "$pid" > /dev/null
    then
        echo "running"
        exit 0
    fi
fi
echo $$ > run.pid

while true
do
    python fetch-price.py > /dev/null
    sleep 60
done
