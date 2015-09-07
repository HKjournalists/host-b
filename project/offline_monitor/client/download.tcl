#!/usr/bin/env expect

set timeout 60

set SERVER_PATH [lindex $argv 0]
set LOCAL_PATH [lindex $argv 1]

#spawn scp -r nsi@tc-sysnoc-nb.tc:$SERVER_PATH $LOCAL_PATH
spawn rsync -Wvrtgo --exclude=".*" nsi@tc-sysnoc-nb.tc.baidu.com:$SERVER_PATH $LOCAL_PATH
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

expect eof
catch close
catch wait
