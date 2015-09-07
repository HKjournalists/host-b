#!/usr/bin/env expect

set timeout 20

set NET_ADMIN [lindex $argv 0]
set CLIENT_MONITOR_PATH /home/nsi/switch/monitor
set SERVER_MONITOR_PATH /home/nsi/switch/monitor/client

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
send "cd $CLIENT_MONITOR_PATH\r"

#send "scp -r nsi@tc-sysnoc-nb.tc:$SERVER_MONITOR_PATH/* $CLIENT_MONITOR_PATH/"
send "rsync -vrtgo --exclude=\".*\" nsi@tc-sysnoc-nb.tc:$SERVER_MONITOR_PATH/* $CLIENT_MONITOR_PATH/"
send "\r"

while 1 {
    expect {
        "(yes/no)?" {
            send "yes\r"
            expect {
                "*password:" {
                    send "baidu.com@nsi\r"
                        break
                }
            }
        }
        "*password:" {
            send "baidu.com@nsi\r"
                break
        }
    }
}

#wait for download all files
sleep 10
send "sync\r\r"
send "echo Download Files OK!\r"

#send "kill -9 `ps -ef | grep run_monitor.sh | grep -v grep | awk '{print $2}'`\r\r"
#sleep 1

send "nohup ./run_monitor.sh &\r"
send "echo run_monitor running...\r\r"
sleep 10

send "ps -aux | grep scripts/check_\r\r"
send "exit\r"

expect eof
catch close
catch wait

