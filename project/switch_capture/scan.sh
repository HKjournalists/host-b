#!/bin/bash
function scan_dir(){
    for file in $(ls $1)
    do
        local path="$1/${file}"
        #echo ${path}
        if [[ -d ${path} ]]; then
            scan_dir "$1/${file}"
        else
            echo "$1/${file}"
        fi
    done
}

scan_dir $1
