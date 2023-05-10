#!/bin/bash

##
##    Bu script Linux sunucularda
##    Telegraf ajan durumunu kontrol amaciyla yazilmistir.
##
##    v1.0 Last Update: 01.12.2021
##
##    by Emircan ELIKKAYA
##

## On Kontroller
if [[ ! (`uname -s` == "Linux") ]]; then
    echo "checkNA,Sunucu Linux Degil"; exit 0
fi

if [[ `uname -a | grep 'el5' | wc -l` -eq 1 ]]; then
    echo "checkNA,RHEL5 Kapsam Disi"; exit 0
fi

if ( pgrep -x telegraf &> /dev/null ); then
    if [[ `grep 'urls' /etc/telegraf/telegraf.conf | grep -v '#' | grep -E '127.0.0.1' | wc -l` -ne 0 ]]; then
        echo "OK,metric gonderiliyor"
    else
        echo "FAIL,konfigurasyon hatali"
    fi
elif [[ `rpm -qa | grep -i telegraf | wc -l` -ne 0 ]]; then
    echo "FAIL,telegraf yuklu ve calismiyor"
else
    echo "FAIL,telegraf yuklu degil"
fi
