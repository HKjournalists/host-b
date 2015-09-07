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

while 1 {
	expect {
		"#" {
			send "set vlan-interface interface vlan100 dhcp-relay disable true\r"
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
			send "set vlan-interface interface vlan100 dhcp-relay disable false\r"
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
