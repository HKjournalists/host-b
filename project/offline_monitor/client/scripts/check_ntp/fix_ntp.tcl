#!/usr/bin/env expect

set ip [lindex $argv 0]
set timeout 400

spawn telnet $ip
send "\r"


while 0 {
	expect {
		"login:" {
			send "luofeng\r"
				break
		}
	}
}

while 0 {
	expect {
		"Password:" {
			send "NSIluofeng@02\r"
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
		"Password" {
			send "toor\r"
				break
		}
	}
}

while 1 {
	expect {
		"\\#" {
			send "killall -9 ntpd && ntpd -g\r"
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
			send "quit\r"
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
expect eof
catch close
catch wait

#close $channel
