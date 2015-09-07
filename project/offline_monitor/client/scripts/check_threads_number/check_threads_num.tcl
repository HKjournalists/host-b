#!/usr/bin/env expect

set ip [lindex $argv 0]
set timeout 400

spawn telnet $ip
send "\r"

while 1 {
	expect {
		"login:" {
			send "luofeng\r"
				break
		}
	}
}

while 1 {
	expect {
		"Password:" {
			send "NSIluofeng@02\r"
				break
		}
	}
}

while 1 {
	expect {
		"Int>" {
			send "start shell sh\r"
				break
		}
	}
}

while 1 {
	expect {
		"Input password:" {
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
                "Password:" {
                        send "toor\r"
                                break
                }
        }
}

while 1 {
	expect {
		"\\#" {
			send "cat /proc/`ps w | grep lcmgr | grep -v grep | awk '{print \$1}'`/status | grep Threads | awk '{print \$2}'\r"
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
            send "ctr\r"
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
		"Int>" {
			send "quit\r"
				break
		}
	}
}

while 1 {
	expect {
		"Int>" {
			send "\r"
				break
		}
	}
}
expect eof
catch close
catch wait

#close $channel
