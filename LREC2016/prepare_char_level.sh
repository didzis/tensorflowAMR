#!/bin/sh

if [ $# -lt 2 ]; then
	echo "usage: $0 input output"
	exit 1
fi

sed -e "s/\ /+/g"  -e "s/./&\ /g" < $1 > $2
