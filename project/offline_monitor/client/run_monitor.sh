#!/bin/bash

SUDO_PASSWD="ljfl2zql"

MONITOR_PATH=/home/wangbin/project/monitor/client
COLLECTD_CONF_PATH=$MONITOR_PATH/collectd 
MONITOR_LOG=$MONITOR_PATH/monitor.log

#IDC_NAME=`hostname | awk -F . '{ print $2 }'`
#IDC_NAME=$(echo $IDC_NAME | tr "[a-z]" "[A-Z]")
IDC_NAME="BB"
echo "Running monitor.. Date:`date +"%Y-%m-%d %H:%M:%S"` IDC: $IDC_NAME">$MONITOR_LOG

cd $MONITOR_PATH

if [ -z $IDC_NAME ]; then
    echo "No IDC name found!!! Exit!!!">>$MONITOR_LOG
    exit 1
fi

SERVER_DEVICE_INFO_PATH=/home/wangbin/project/monitor/client/devices
SERVER_MONITOR_PATH=/home/wangbin/project/monitor/client/scripts
SERVER_CONFIG_PATH=$SERVER_MONITOR_PATH/../../config/collectd/$IDC_NAME
echo "Server Path: $SERVER_CONFIG_PATH">>$MONITOR_LOG

while [[ 1 ]]
do
    if [ -s $COLLECTD_CONF_PATH/prev_version ] ; then
        ./download.tcl $SERVER_CONFIG_PATH/version $COLLECTD_CONF_PATH
				
        version_old=`cat $COLLECTD_CONF_PATH/prev_version | grep -i "version" | awk '{print $2}'`
        version_new=`cat $COLLECTD_CONF_PATH/version | grep -i "version" | awk '{print $2}'`

        if [ "$version_old" != "$version_new" ] ; then
            echo "$SUDO_PASSWD" | sudo -S /etc/init.d/collectd stop
            #rm -rf $MONITOR_PATH/*
            ./download.tcl $SERVER_CONFIG_PATH/collectd.conf $COLLECTD_CONF_PATH
            cp -f $COLLECTD_CONF_PATH/collectd.conf $COLLECTD_CONF_PATH/collectd.conf_bak
            cp -f $COLLECTD_CONF_PATH/version $COLLECTD_CONF_PATH/prev_version
            ./download.tcl $SERVER_MONITOR_PATH $MONITOR_PATH
            ./download.tcl $SERVER_DEVICE_INFO_PATH $MONITOR_PATH
            sync

            #echo "$SUDO_PASSWD" | sudo -S /usr/sbin/collectd -C ./collectd.conf
            #echo $SUDO_PASSWD | sudo -S cp -f ./collectd.conf /etc/collectd.conf
            echo $SUDO_PASSWD | sudo -S /usr/sbin/collectd -C $COLLECTD_CONF_PATH/collectd.conf 
            echo "collectd restarted for version update ($version_old)->($version_new)!">>$MONITOR_LOG
        fi
    else
        echo "$SUDO_PASSWD" | sudo -S /etc/init.d/collectd stop
        #rm -rf $MONITOR_PATH/check_*

        ./download.tcl $SERVER_MONITOR_PATH $MONITOR_PATH
        ./download.tcl $SERVER_DEVICE_INFO_PATH $MONITOR_PATH
        ./download.tcl $SERVER_CONFIG_PATH/* $COLLECTD_CONF_PATH
        #./download.tcl $SERVER_CONFIG_PATH/collectd.conf $COLLECTD_CONF_PATH
        sync

        if [ -s $COLLECTD_CONF_PATH/version ] && [ -s $COLLECTD_CONF_PATH/collectd.conf ] ; then
            cp -f $COLLECTD_CONF_PATH/version $COLLECTD_CONF_PATH/prev_version
            #echo "$SUDO_PASSWD" | sudo -S /usr/sbin/collectd -C ./collectd.conf
            #echo "$SUDO_PASSWD" | sudo -S cp -f ./collectd.conf /etc/collectd.conf
            echo "$SUDO_PASSWD" | sudo -S /usr/sbin/collectd -C $COLLECTD_CONF_PATH/collectd.conf
            echo "collectd started..">>$MONITOR_LOG
        else
            echo "no version or collectd.conf file found!!!">>$MONITOR_LOG
        fi
    fi

    sleep 30
done
