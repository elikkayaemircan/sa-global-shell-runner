#!/bin/bash

##
##    Bu script Linux Fiziksel sunucularda
##    IPMITOOL ile Management IP bilgilerini ve
##    DNS kayitlarini kontrol amaciyla yazilmistir.
##
##    v1.0 Last Update: 28.01.2022
##
##    by Emircan ELIKKAYA
##

## On Kontroller
if [[ ! (`uname -s` == "Linux") ]]; then
    echo "checkNA,Sunucu Linux Degil,-,-"; exit 0
fi

if ! command -v ipmitool &> /dev/null; then
    echo "checkNA,IPMITOOL Kurulu Degil,-,-"; exit 0
fi

## Ana Kontrol Blogu
declare -a DOMAINLIST=( "example.com" "example.com.tr" "example.net" "example.org" )

IPMI=$( ipmitool lan print 2> /dev/null | grep '^IP Address.*' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' )

if [[ -z $IPMI ]]; then
    echo "checkNA,IPMI kaydi bulunamadi,-,-"; exit 0
fi

for _domain in "${DOMAINLIST[@]}"; do

    DNS=$( nslookup "$HOSTNAME"-bmc."$_domain" )

    # DNS kaydi donmeyen domainler icin loop atla
    if [[ -z $( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ) ]]; then
        continue
    fi

    if [[ $IPMI == $( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ) ]]; then
        echo "OK,$HOSTNAME-bmc.$_domain,$IPMI,$( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' )"; exit 0
    elif [[ `echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | wc -l` -ne 1 ]]; then
        echo "FAIL,Coklu DNS kaydi mevcut $HOSTNAME-bmc.$_domain,$IPMI,$( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | xargs )"; exit 0
    else
        echo "FAIL,DNS ve IPMI farkli $HOSTNAME-bmc.$_domain,$IPMI,$( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' )"; exit 0
    fi

done

echo "FAIL,DNS kaydi bulunamadi,$IPMI,-"; exit 0
