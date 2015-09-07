#!/bin/bash


function process_clean_pkill()
{
    local cmd
    if [ ${UID} -eq 0 ];then
        cmd="kill"
    else
        cmd="sudo kill"
    fi
    ${cmd} -9 $1
    return 0
}
process_clean_pkill $1
