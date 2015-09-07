#!/usr/bin/env expect

set ip [lindex $argv 0]
set timeout 400

spawn telnet $ip
send "\r"

while 1 {
    expect {
        "login:" {
            send "luofeng\r"
            #send "admin\r"
                break
        }
    }
}

while 1 {
    expect {
        "Password:" {
            send "NSIluofeng@02\r"
            #send "admin\r"
                break
        }
    }
}

while 1 {
    expect {
        ">" {
            send "start shell diag\r"
                break
        }
    }
}

while 1 {
    expect {
        "password:" {
            send "toor\r"
                break
        }
    }
}

while 1 {
    expect {
        "BCM.0>" {
            send "ctr Interval=1000000\r"
                break
        }
    }
}

while 1 {
    expect {
        "BCM.0>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        "BCM.0>" {
            send "exit\r\r\r"
                break
        }
    }
}

while 1 {
    expect {
        ">" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ">" {
            send "exit\r"
                break
        }
    }
}

expect eof
catch close
catch wait

