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
        ".Int>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
			send "show route table ipv4 unicast final |no-more\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "show route forward-route ipv4 all |no-more\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "show route forward-host ipv4 all |no-more\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "quit\r"
                break
        }
    }
}

while 1 {
    expect {
        ".Int>" {
            send "\r"
                break
        }
    }
}
expect eof
catch close
catch wait

#close $channel
