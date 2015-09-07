#!/bin/bash

usage()
{
  echo "build date: 2013.12.20"
  echo "./bashcheck.sh <dir>"
  exit
}

if [ $# -ne 1 ]; then
  usage
elif [ "x${1:0:1}" == "x-" ]; then
  usage
fi
server=http://cq01-testing-ps70245.vm.baidu.com:8080/coverage/bashcheck

id=`find "$1" -name "*.sh" 2>/dev/null | tar -T - -czf - 2>/dev/null | curl -F file=@-  $server/upload.php 2>/dev/null`

if [[ ${id} =~ ^[0-9]+$ ]];then  
  echo -n "[bashcheck] checking "
  while :
  do
    result=`curl $server/get.php?id=$id 2>/dev/null`
    if [[ $result == "wait" ]]; then
       echo -n " . "
       sleep 1
    elif [[ $result == "succ" ]]; then
       echo "succ"
       curl $server/result/$id.txt 2>/dev/null
       break
    else
       echo "fail"
       echo "$result"
       break
    fi
  done
else
  echo "[bashcheck] fail"
fi
