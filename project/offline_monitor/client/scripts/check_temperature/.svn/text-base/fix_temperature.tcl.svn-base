#!/usr/bin/env expect

set ip [lindex $argv 0]
set serv_ip [lindex $argv 1]
set timeout 400

spawn telnet $ip

while 1 {
    expect {
        "login:" {
            send "luofeng\r"
#            send "admin\r"
                break
        }
    }
}

while 1 {
    expect {
        "Password:" {
            send "NSIluofeng@02\r"
#            send "admin\r"
                break
        }
    }
}

while 1 {
    expect {
        ">" {
            send "start shell sh\r"
                break
        }
    }
}

while 1 {
    expect {
        "assword:" {
            send "toor\r"
                break
        }
    }
}
while 1 {
    expect {
        "\\$" {
            send "su\r"
                break
        }
    }
}

while 1 {
    expect {
        "assword:" {
            send "toor\r"
                break
        }
    }
}

while 1 {
    expect {
        "\\#" {
            send "cd /\r"
                break
        }
    }
}

while 1 {
    expect {
        "\\#" {
            send "tftp -gr i2c_reset_drv.ko $serv_ip\r"
            break
        }
    }
}

while 1 {
    expect {
        "\\#" {
            send "insmod i2c_reset_drv.ko reset=Ctrl && rmmod i2c_reset_drv\r"
                break
        }
    }
}

while 1 {
    expect {
        "\\#" {
            send "exit\r\r"
                break
        }
    }
}

while 1 {
    expect {
        "\\$" {
            send "exit\r\r"
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

