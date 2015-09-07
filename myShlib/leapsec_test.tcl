#!/usr/bin/env expect

set ip [lindex $argv 0]
set ns1 [lindex $argv 1]
set ns2 [lindex $argv 2]
set timeout 400

spawn telnet $ip
send "\r"

while 1 {
    expect {
        ">" {
            send "configure\r"
            break
        }
    }
}

while 1 {
    expect {
        "#" {
            send "\r"
            break
        }
    }
}

while 1 {
	expect {
		"#" {
			send "set system ntp-server-ip $ns1\r"
			break
		}
	}
}

while 1 {
    expect {
        "#" {
            send "commit\r"
            break
        }
    }
}

while 1 {
    expect {
        "#" {
            send "set system ntp-server-ip $ns2\r"
            break
        }
    }
}

while 1 {
    expect {
        "#" {
            send "commit\r"
            break
        }
    }
}

while 1 {
	expect {
		"#" {
			send "exit\r"
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