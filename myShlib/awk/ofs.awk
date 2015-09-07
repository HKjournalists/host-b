#!/bin/awk -f
BEGIN{
    FS="c";
    OFS="#"
}
{
    print $1, $2
}

