#!/bin/bash

##
##    Bu script RHEL7 ve RHEL8 sunucularda
##    Audit Log konfigurasyon kontrol amaciyla yazilmistir.
##
##    v1.0 Last Update: 05.11.2021
##
##    by Emircan ELIKKAYA
##

## On Kontroller
if [[ ! (`uname -s` == "Linux") ]]; then
    echo "checkNA,Sunucu Linux Degil"; exit 0
fi

if [[ `uname -a | grep 'el8' | wc -l` -eq 1 ]]; then
    RELEASE="RHEL8"
elif [[ `uname -a | grep 'el7' | wc -l` -eq 1 ]]; then
    RELEASE="RHEL7"
else
    echo "checkNA,Sunucu RHEL7 veya RHEL8 Degil"; exit 0
fi

if [[ $RELEASE = "RHEL8" ]]; then
    if ( pgrep -x auditd &> /dev/null ); then
        if [[ $( ps -eo pid,ppid,cmd  | grep '\/sbin\/auditd' | awk '{print $1}' ) == $( ps -eo pid,ppid,cmd  | grep '\/sbin\/audisp-remote' | awk '{print $2}' ) ]]; then
            if [[ ( `grep '^remote_server' /etc/audit/audisp-remote.conf | grep -E '127.0.0.1' | wc -l ` -ge 1 )
               && ( `grep '^port' /etc/audit/audisp-remote.conf | grep '[^0-9]514$' | wc -l ` -ge 1 )
               && ( `grep '^format' /etc/audit/audisp-remote.conf | grep 'ascii' | wc -l ` -ge 1 )
               && ( `grep '^active' /etc/audit/plugins.d/au-remote.conf | grep 'yes' | wc -l ` -ge 1 ) ]]; then
                echo  "OK,audit log gonderiliyor"
            else
                echo "FAIL,audisp-remote konfigurasyonu hatali"
            fi
        else
            echo "FAIL,audisp-remote calismiyor"
        fi
    else
        echo "FAIL,audit calismiyor"
    fi
fi

if [[ $RELEASE = "RHEL7" ]]; then
    if ( pgrep -x auditd &> /dev/null ); then
        if [[ $( ps -eo pid,ppid,cmd  | grep '\/sbin\/auditd' | awk '{print $1}' ) == $( ps -eo pid,ppid,cmd  | grep '\/sbin\/audispd' | awk '{print $2}' )
           && $( ps -eo pid,ppid,cmd  | grep '\/sbin\/audispd' | awk '{print $1}' ) == $( ps -eo pid,ppid,cmd  | grep '\/sbin\/audisp-remote' | awk '{print $2}' ) ]]; then
            if [[ ( `grep '^remote_server' /etc/audisp/audisp-remote.conf | grep -E '127.0.0.1' | wc -l ` -ge 1 )
               && ( `grep '^port' /etc/audisp/audisp-remote.conf | grep '[^0-9]514$' | wc -l ` -ge 1 )
               && ( `grep '^format' /etc/audisp/audisp-remote.conf | grep 'ascii' | wc -l ` -ge 1 )
               && ( `grep '^active' /etc/audisp/plugins.d/au-remote.conf | grep 'yes' | wc -l ` -ge 1 ) ]]; then
                echo  "OK,audit log gonderiliyor"
            else
                echo "FAIL,audisp-remote konfigurasyonu hatali"
            fi
        else
            echo "FAIL,audisp-remote calismiyor"
        fi
    else
        echo "FAIL,audit calismiyor"
    fi
fi
