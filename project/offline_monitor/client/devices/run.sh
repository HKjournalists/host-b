#!/bin/sh

cd `dirname $0`

while true
do
    sh get_tor_info.sh 
    sleep 14400
done
