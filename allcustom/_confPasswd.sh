#!/bin/bash

echo "$1" 1> /dev/null 2>&1
echo "$2" | passwd --stdin root 1> /dev/null 2>&1

if [[ $( passwd --status root | awk '{print $3}' ) == $( date +%Y-%m-%d ) ]]; then
  echo "OK","Password changed"
else
  echo "FAILED","Cannot changed"
fi

exit 0
