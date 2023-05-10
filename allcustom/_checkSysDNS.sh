#!/bin/bash

##
##    Bu script Linux sunucularda
##    DNS kayitlarini kontrol amaciyla yazilmistir.
##
##    v1.1 Last Update: 12.03.2022
##
##    by Emircan ELIKKAYA <elikkaya.emircan@gmail.com>
##

declare -a DOMAINLIST=( "example.com" "example.com.tr" "example.net" "example.org" )

for _domain in "${DOMAINLIST[@]}"; do

    DNS=$( /usr/bin/nslookup "$1"."$_domain" )

    if [[ $2 == $( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ) ]]; then
        echo "OK,$1.$_domain,$( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ),$2"
        exit 0
    elif [[ ! -z $( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ) ]]; then
        if [[ `echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | wc -l` -ne 1 ]]; then
            echo "FAIL,$1.$_domain,Coklu DNS kaydi mevcut,$2"
            exit 0
        else
            echo "FAIL,$1.$_domain,$( echo "$DNS" | grep '^Address.*' | grep -v '#' | grep -o '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' ),$2"
            exit 0
        fi
    fi

done

echo "FAIL,DNS kaydi bulunamadi,-,$2"; exit 0
