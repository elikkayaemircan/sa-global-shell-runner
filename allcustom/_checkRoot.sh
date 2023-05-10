#!/bin/bash

if [[ `uname -s` != "Linux" ]] ; then
    echo "checkNA","non-linux kapsam disi"
    exit 0
fi

adflush >&2 /dev/null
adreload >&2 /dev/null

users=$( getent passwd | grep '9999' )
zone=$( adinfo | grep '^Zone:.*' | awk '{print $2}' )
declare -a BLACKLIST=()

for user in $( echo "$users" | awk -F':' '{print $1}' ); do
    if [[ `dzinfo -c $user | grep -A 1 'Wildcard' | grep -i 'root' | wc -l` -gt 0 ]]; then
        BLACKLIST+="$( echo $user ) "
    fi
done

if [[ `echo $BLACKLIST | wc -m` -gt 1 ]]; then
    ROLE=$( dzinfo $( echo $BLACKLIST | awk -F' ' '{print $1}' ) | grep -A 1 'Wildcard' | xargs | awk -F' ' '{print $4,$5}' | tr -d ' ')
    echo "FAIL","$zone","$ROLE","$BLACKLIST"
else
    echo "OK","$zone","-","-"
fi
