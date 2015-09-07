#!/bin/sh

while read line
do
    ./fix_ntp.tcl $line
done < ip_fix.txt
