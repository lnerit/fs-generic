#!/bin/bash

# export LD_PRELOAD=`pwd`/interpose_python.so
export LD_PRELOAD=`pwd`/interpose_time_calls.so
python testFile.py
