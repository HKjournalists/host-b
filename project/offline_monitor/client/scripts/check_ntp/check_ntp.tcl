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
			send "show system ntp-status  | match ntp_gettime\r"
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
