#!/usr/bin/env expect

set timeout 60

set NET_ADMIN [lindex $argv 0]
set CLIENT_MONITOR_PATH /home/nsi/switch/monitor

spawn ssh nsi@$NET_ADMIN
send "\r"

#while 1 {
#    expect {
#            "*password:" {
#                send "baidu.com@nsi\r\r"
#                break
#            }
#    }
#}

sleep 1

send "echo Login $NET_ADMIN OK!\r"
send "mkdir -p $CLIENT_MONITOR_PATH\r"
send "ls $CLIENT_MONITOR_PATH\r\r"

send "exit\r"

expect eof
catch close
catch wait

