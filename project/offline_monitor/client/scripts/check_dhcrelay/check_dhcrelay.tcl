#!/usr/bin/env expect

set ip [lindex $argv 0]
set timeout 400

spawn telnet $ip

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
			send "show system processes | no-more\r"
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

expect eof
catch close
catch wait

#close $channel
