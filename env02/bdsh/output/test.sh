#!/bin/bash

env x='() { :;}; touch CVE-2014-6271' bash -c ":"
if [ -f 'CVE-2014-6271' ]; then
    echo CVE-2014-6271 : vulnerable
else 
    echo CVE-2014-6271 : pass
fi
rm -f 'CVE-2014-6271'

foo='() { touch CVE-2014-6277; }' bash -c foo
if [ -f 'CVE-2014-6277' ]; then
    echo CVE-2014-6277 : vulnerable
else
    echo CVE-2014-6277 : pass
fi
rm -f 'CVE-2014-6277'

_x='() { echo CVE-2014-6278 : vulnerable; }' bash -c '_x 2>/dev/null || echo CVE-2014-6278 : pass'

env x='() { (a)=>\' sh -c "log date"
env x='() { (a)=>\' bash -c "log date"
if [ -f log ]; then
    echo CVE-2014-7169 : vulnerable
else
    echo CVE-2014-7169 : pass
fi
rm -f 'log'

sh -c 'true <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF' || touch 'CVE-2014-7186'
if [ -f 'CVE-2014-7186' ]; then
    echo CVE-2014-7186 : vulnerable
else
    echo CVE-2014-7186 : pass
fi 
rm -f 'CVE-2014-7186'

(for x in {1..200} ; do echo "for x$x in ; do :"; done; for x in {1..200} ; do echo done ; done) | bash || touch 'CVE-2014-7187'
if [ -f 'CVE-2014-7187' ]; then
    echo CVE-2014-7187 : vulnerable
else
    echo CVE-2014-7187 : pass
fi
rm -f 'CVE-2014-7187'


