#!/bin/awk -f
BEGIN {
    RS="e"
}
{
    printf("%s[%s]", $0, RT)
}
