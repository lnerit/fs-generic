#!/bin/bash -x

# gcc -o interpose_python.so interpose_python.c -shared -g -Wall -fPIC -D_REENTRANT
gcc -o interpose_time_calls.so interpose_time_calls.c -shared -g -Wall -fPIC -D_REENTRANT
