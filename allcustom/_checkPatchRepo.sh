#!/bin/bash

##
##    Bu script Linux sunucularda
##    Satellite Repo durumunu ve guncellenecebilecek
##    paket bilgisini kontrol amaciyla yazilmistir.
##
##    v1.0 Last Update: 15.02.2022
##
##    by Emircan ELIKKAYA <elikkaya.emircan@gmail.com>
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

## Ana Kontrol Blogu
sat_name=$( subscription-manager identity | grep '^name' | sed 's/name: //' 2> /dev/null )
sat_repo=$( subscription-manager config | grep 'manage_repos' | grep -o '[0-1]' )


if [[ $sat_repo == 0 ]]; then
    echo "checkNA,Satellite Management Disabled"; exit 0
fi

if [[ $sat_name != $(hostname) ]]; then
    echo "FAIL,Satellite Name Differs from Host"; exit 0
fi


subscription-manager refresh &> /dev/null

find /etc/yum.repos.d/ -maxdepth 1 -name '*.repo' ! -name 'redhat.repo' -type f -exec sed -i 's/^enabled=.*/enabled=0/g' {} \;

subscription-manager repos --enable=* &> /dev/null

rm -rf /var/cache/yum &> /dev/null

yum check-update &> /dev/null

echo "OK,Updates Checked"; exit 0
