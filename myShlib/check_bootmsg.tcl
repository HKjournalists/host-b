#!/usr/bin/env expect

set ip [lindex $argv 0]
set match_words [lindex $argv 1]
set timeout 400

spawn telnet $ip
send "\r"

while 1 {
    expect {
        ">" {
            #不能用run show不能用run show不能用run show不能用run show别问我怎么知道的！
            send "show system  boot-messages | match \"$match_words\"\r"
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
