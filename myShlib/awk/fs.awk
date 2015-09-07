#!/bin/awk -f
BEGIN{
    FS="c"
}
{
    print $1, $2
}

