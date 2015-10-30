#!/bin/bash
##! @TODO:   分离可执行程序的符号表
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0

#set -e后出现的代码，一旦出现了返回值非零，整个脚本就会立即退出
#set -e

OBJCOPY="ppc-linux-objcopy"
#OBJCOPY="objcopy"
STRIP="ppc-linux-strip"
#STRIP="strip"

##! @TODO: 输出帮助信息
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 1
function strip_usage()
{
    echo "Usage: "
    echo -e "sh $0 [需要分离符号表的程序的路径]"
    return 1
}

##! @TODO: 主函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: $1: 需要进行分离符号表操作的可执行文件的路径
##! @OUT: 0 => success; 1 => failed
function strip_main() 
{
    if [[ $# -ne 1 ]]
    then
        strip_usage
        return 1
    fi
    file $1 | grep -q ELF
    if [[ $? -ne 0 ]]
    then
        echo "$1 不是可执行文件" >&2
        return 1
    fi
    #从包含绝对路径的文件名中去除文件名（非目录的部分），返回剩目录的部分
    if [[ ${1:0:1} == '/' ]]; then  #绝对路径
        local file_dir=$(dirname $1)
    else                            #相对路径
        local file_dir="$(pwd)/$(dirname $1)"
    fi
    #从包含绝对路径的文件名中去除目录部分，返回文件名（非目录的部分）
    local file_name=$(basename $1)
    #符号表文件储存目录
    #local debug_dir="${file_dir%/*}/.debug"
    local debug_dir="${file_dir}"
    #符号表文件名
    local debug_file="${file_name}.debug"
    #建立符号表存放目录
    cd ${file_dir}
    #echo "file dir: ${file_dir}"
    #echo "debug dir: ${debug_dir}"
    #echo ${debug_file}
    #if [[ ! -d ${debug_dir} ]] 
    #then
    #    echo "建立符号表存放目录：${file_dir}/${debug_dir}"
    #    mkdir -p "${debug_dir}"
    #fi
    export "PATH=$PATH:/opt/ELDK/bin:/opt/ELDK/usr/bin"
    export "CROSS_COMPILE=ppc_85xxDP-"
    #从程序中分离符号表
    ${OBJCOPY} --only-keep-debug "${file_name}" "${debug_file}"
    if [[ $? -ne 0 ]]
    then
        echo "ppc-linux-objcopy --only-keep-debug failed" >&2
        return 1
    fi
    ${STRIP} --strip-debug --strip-unneeded "${file_name}"
    if [[ $? -ne 0 ]]
    then
        echo "ppc-linux-strip --strip-debug --strip-unneeded failed" >&2
        return 1
    fi
    ${OBJCOPY} --add-gnu-debuglink="${debug_file}" "${file_name}"
    if [[ $? -ne 0 ]]
    then
        echo "ppc-linux-objcopy --add-gnu-debuglink failed" >&2
        return 1
    fi
    chmod -x "${debug_file}"
    #echo "成功分离可执行文件 ${file_name} 的符号表，存放于目录：${file_dir}/${debug_dir}"
    return 0
}

if [[ ${0##*/} == "strip_debug.sh" ]]
then
    #NOT invoked by source
    strip_main $*
fi