#!/bin/bash

/sbin/adleave --force 1> /dev/null 2>&1

if [[ "$1" == "DMZ" ]]; then
  /sbin/adjoin -u "$3"@domain.example.com -p $4 -c "OU=ouname,OU=ouname" -f -V -z "$2" dmz.domain.example.com 1> /dev/null 2>&1
fi

if [[ "$1" == "LOCAL" ]]; then
  /sbin/adjoin -u "$3"@domain.example.com -p $4 -c "OU=ouname,OU=ouname" -f -V -z "$2" local.domain.example.com 1> /dev/null 2>&1
fi

declare raw=$( adinfo )
if [[ $( echo "$raw" | grep '^CentrifyDC mode' | awk -F':' '{print $2}' | xargs ) == "connected" ]]; then
  echo "JOINED","$2"
else
  echo "CANNOT_JOINED","$2"
fi
