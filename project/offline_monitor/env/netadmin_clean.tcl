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
send "sudo /etc/init.d/collectd stop\r"
sleep 1
send "sudo /etc/init.d/collectd stop\r"
send "sudo /etc/init.d/collectd status\r"
sleep 2

send "kill -9 `ps -ef | grep run_monitor.sh | grep -v grep | awk '{print \$2}'`\r\r"
send "rm -rf $CLIENT_MONITOR_PATH\r"
sleep 2

send "exit\r"

expect eof
catch close
catch wait

