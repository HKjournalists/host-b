#!/bin/bash

devs=`df -T | grep '^/dev/sd[^a]' | awk '{print $1}'| awk -F'/' '{print $3}'`

all=($devs)

if [ -f /var/run/diskinit.pid ]; then
    rm -f /var/run/diskinit.pid
fi
if [ -f /tmp/diskinit_pre.sh ]; then
    rm -f /tmp/diskinit_pre.sh
fi
for i in ${all[*]}
do
    umount /dev/$i
    label=`echo $i | awk -F'1' '{print $1}'`
    parted -s /dev/$label rm 1
    rm -rf /dev/$i
done
df -T | grep 'home'
if [ $? -eq 0 ]; then
    umount /home
fi



