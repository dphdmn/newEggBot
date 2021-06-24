#!/bin/bash

if [ "$1" != "" ]; then
    kill -9 $1
fi
sleep 0.5
./run.sh
