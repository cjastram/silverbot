#!/bin/bash

if test -f run.pid
then
    pid=`cat run.pid`
    if ps -p "$pid" > /dev/null
    then
        # Just exit quietly if loop is still running
        exit 0
    fi
fi
echo $$ > run.pid

while true
do
    python fetch-price.py > /dev/null
    sleep 60
done
