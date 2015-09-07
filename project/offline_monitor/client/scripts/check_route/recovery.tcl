#!/usr/bin/env expect

set ip [lindex $argv 0]

spawn telnet $ip
send "\r"

while 0 {
    expect {
        "login:" {
            send "sti\r"
            break
        }
    }
}

while 0 {
    expect {
        "Password:" {
            send "NSIsti@01\r"
            break
        }
    }
}

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


set i 1
while {$i < $argc} {
    set ae [lindex $argv $i]
    incr i 1
	if {$ae == "0"} {
		continue
	}

	while 1 {
		expect {
			"#" {
				send "set interface aggregate-ethernet $ae disable true\r"
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
				send "set interface aggregate-ethernet $ae disable false\r"
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
	
	after 70000

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
			send "show route table ipv4 unicast final |count\r"
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
			send "show route forward-route ipv4 all |match count\r"
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
