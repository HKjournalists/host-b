#!/bin/bash

##! @TODO:   简易测试框架单元测试，部分函数由于流程需要没有给出独立的单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @VERSION: 1.0_build0010

set -m
source `dirname $0`/mini_tester.sh
UNIT_TESET_CONFIG_FILE="./unit_test_tester.conf"
LOG_RESULT_PATH="mini_tester_result.log"
QUERY_LIST_NAME="query_list"

##! @TODO: 主函数单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_main_test()
{
    local cfgfile="./unit_test_tester.conf"
    rm -f ${cfgfile}
    mini_tester_main > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] param empty"
    else
        echo "[failed] param empty"
    fi
    mini_tester_main -z > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] param error"
    else
        echo "[failed] param error"
    fi
    mini_tester_main -c ${cfgfile} > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] empty config file"
    else
        echo "[failed] empty config file"
    fi
    return 0
}

##! @TODO: 测试初始化函数单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_start_test()
{
    rm -f ${UNIT_TESET_CONFIG_FILE}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    echo "MUT_PATH=\"ftp://cq01-ocean-824.epc.baidu.com/home/qacmc/good_coder/\
shell/mini_tester/mini_http_server/mini_http_server.tar.gz\"" > ${UNIT_TESET_CONFIG_FILE}
    echo "QUERY_LIST_PATH=\"ftp://cq01-ocean-824.epc.baidu.com/home/qacmc/\
good_coder/shell/mini_tester/query_list/\"" >> ${UNIT_TESET_CONFIG_FILE}
    echo "QUERY_LIST_NAME=\"query_list\"" >> ${UNIT_TESET_CONFIG_FILE}
    mini_tester_start ${UNIT_TESET_CONFIG_FILE}  > /dev/null 2>&1
    if [[ $? -eq 3 ]]
    then
        echo "[pass] global var empty"
    else
        echo "[failed] global var empty"
    fi
    echo "QUERY_LIST_MD5=\"query_list.md5\"" >> ${UNIT_TESET_CONFIG_FILE}
    echo "RESPONSE_PATH=\"server_response.log\"" >> ${UNIT_TESET_CONFIG_FILE}
    echo "LOG_RESULT_PATH=\"mini_tester_result.log\"" >> ${UNIT_TESET_CONFIG_FILE}
    return 0
}

##! @TODO: 下载待测项目文件单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_download_test()
{
    source ${UNIT_TESET_CONFIG_FILE}
    local temp=${MUT_PATH}
    MUT_PATH="ftp.youtube.com"
    mini_tester_download "./unit_test.tar.gz" > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] download failed"
    else
        echo "[failed] download failed"
    fi
    MUT_PATH=${temp}
    return 0
}

##! @TODO: 执行测试主体单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_run_test()
{
    local put_name=${MUT_PATH##*/}            #待测项目压缩包文件名
    local put_path="${BASE_PATH}/${put_name%%.*}"  #待测项目的根目录路径

    local dict="${put_path}/data/name_id_value_dict"
    mv "${dict}" "${dict}.bak" 
    mini_tester_run ${put_path} ${PROGRAM_NAME} > /dev/null 2>&1
    if [[ $? -eq 2 ]]
    then
        echo "[pass] name_id_value_dict empty"
    else
        echo "[failed] name_id_value_dict empty"
    fi
    mv "${dict}.bak" "${dict}"
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    local port=${PROGRAM_PORT}
    PROGRAM_PORT=65536
    mini_tester_run ${put_path} ${PROGRAM_NAME} > /dev/null 2>&1
    if [[ $? -eq 3 ]]
    then
        echo "[pass] port error"
    else
        echo "[failed] port error"
    fi
    PROGRAM_PORT=${port}
    return 0
}

##! @TODO: 请求部分单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_dotest_test()
{
    local port=${PROGRAM_PORT}
    local put_name=${MUT_PATH##*/}            #待测项目压缩包文件名
    local put_path="${BASE_PATH}/${put_name%%.*}"  #待测项目的根目录路径
    mini_tester_do_test ${port} ${put_path} "" > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] empty program name"
    else
        echo "[failed] empty program name"
    fi
    mini_tester_do_test 11 ${put_path} ${PROGRAM_NAME} > /dev/null 2>&1
    if [[ $? -eq 1 ]]
    then
        echo "[pass] illegal port"
    else
        echo "[failed] illegal port"
    fi
    mini_tester_do_test 8761 ${put_path} ${PROGRAM_NAME} > /dev/null 2>&1
    if [[ $? -eq 2 ]]
    then
        echo "[pass] query failed"
    else
        echo "[failed] query failed"
    fi
    return 0
}

##! @TODO: 清理进程函数单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_clean_test()
{
    local test_script="test_script.sh"
    echo "while [[ 1 ]]; do sleep 60;done" > ${test_script}
    eval "sh ${test_script} &"
    eval "sh ${test_script} &"
    eval "sh ${test_script} &"
    eval "sh ${test_script} &"
    eval "sh ${test_script} &"
    mini_tester_clean "test_script.sh" > /dev/null 2>&1
    if [[ $? -eq 0 ]]
    then
        echo "[pass] clean processes"
    else
        echo "[failed] clean processes"
    fi
    rm -f ${test_script}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    return 0
}

##! @TODO: 整体单元测试
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_all_test()
{
    
    sh mini_tester.sh -c "tester.conf"
    if [[ $? -eq 0 ]]
    then
        grep -q qps ${LOG_RESULT_PATH}
        if [[ $? -ne 0 ]]
        then
            echo "[failed] mini_tester.sh"
            return 0
        fi
        grep -q value_avg ${LOG_RESULT_PATH}
        if [[ $? -ne 0 ]]
        then
            echo "[failed] mini_tester.sh"
            return 0
        fi
        grep -q succ_rate ${LOG_RESULT_PATH}
        if [[ $? -ne 0 ]]
        then
            echo "[failed] mini_tester.sh"
            return 0
        fi
        grep -q name_num ${LOG_RESULT_PATH}
        if [[ $? -ne 0 ]]
        then
            echo "[failed] mini_tester.sh"
            return 0
        fi
        echo "[pass] mini_tester.sh"
        return 0
    else
        echo "[failed] mini_tester.sh"
    fi
    return 0
}

##! @TODO: 主函数
##! @AUTHOR: wangbin19@baidu.com
##! @IN: None
##! @OUT: 0 => success; 1 => failed
function mini_tester_unit_test_main()
{
    mini_tester_main_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_start_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_download_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_run_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_clean_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_dotest_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    mini_tester_all_test
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    rm -f ${UNIT_TESET_CONFIG_FILE}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    rm -f ${LOG_RESULT_PATH}
    if [[ $? -ne 0 ]]
    then
        return 1
    fi
    return 0
}

mini_tester_unit_test_main

