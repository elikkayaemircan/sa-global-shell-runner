#!/bin/bash

##
##    Bu script Linux sunucularda
##    Centrify DC ajan durumu ve sunucunun bagli bulundugu zone
##    bilgisini kontrol amaciyla yazilmistir.
##
##    v1.1 Last Update: 18.02.2022
##
##    by Emircan ELIKKAYA <elikkaya.emircan@gmail.com>
##

## On Kontroller
if [[ ! (`uname -s` == "Linux") ]]; then
    echo "checkNA,Sunucu Linux Degil"; exit 0
fi

if ! command -v adinfo &> /dev/null; then
    echo "checkNA,centrifydc Kurulu Degil"; exit 0
fi

## Ana Kontrol Blogu
declare raw=$( adinfo )

if [[ $( echo "$raw" | grep '^CentrifyDC mode' | awk -F':' '{print $2}' | xargs ) == "connected" ]]; then
  echo "OK","$( echo "$raw" | grep '^Zone' | awk -F':' '{print $2}' | xargs )"; exit 0
fi

if [[ $( echo "$raw" | grep '^CentrifyDC mode' | awk -F':' '{print $2}' | xargs ) == "disconnected" ]]; then
  echo "WARN","disconnected $( echo "$raw" | grep '^Zone' | awk -F':' '{print $2}' | xargs )"; exit 0
fi

echo "FAIL","not joined any zone"; exit 0
