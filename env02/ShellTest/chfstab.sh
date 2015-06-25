#!/bin/bash

function change(){
cat fstab | grep -q '^none.*sys'
    if [ $? -eq 0 ]; then
        temp=`cat fstab | sed -n '/^none.*sys/p' | sed 's/none/sysfs/g'`
        sed -i -e "/^none.*sys/a $temp" -e '/^none.*sys/d' fstab
    fi
}
function annotation(){
    cat fstab | grep -q '^none.*sys'
    if [ $? -eq 0 ]; then
	old=`cat fstab | sed -n '/^none.*sys/p'`
        annotation="#"$old
        temp=`echo $old | sed 's/none/sysfs/g'`
	sed -i -e "/^none.*sys/a $annotation" -e "/^none.*sys/a $temp" -e '/^none.*sys/d' fstab
    fi
}
annotation

