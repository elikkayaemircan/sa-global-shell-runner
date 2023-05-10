#!/usr/bin/bash

usage() {
  echo -n "
Usage: $(basename $0) [options]

$(basename $0) Checks the network interfaces to find the backup VLAN and configure it with given IP

  ## Examples
  DC 1: sh $(basename $0) 127.0.0.1/24 1 192.168.0.0/24,127.0.0.1
  DC 2: sh $(basename $0) 127.0.0.1/24 2 192.168.0.0/24,127.0.0.1
  DC 3: sh $(basename $0) 127.0.0.1 3

" >&2
        exit 1
}

IP=$1
VLAN=$2
ROUTE=$3

if [[ -z $IP ]] || [[ -z $VLAN ]] ; then
  usage ;
fi

## End of the variables


echo "Start erasing with older packages.."
yum erase -y lgtoclnt lgtonode lgtoman lgtoxtdclnt &> /dev/null
if [[ `rpm -qa | grep 'lgto.*' | grep -v 'lgto.*19\.2.*' | wc -l` -ne 0 ]]; then
  echo "Check the lgto packages: nmda might be installed! Don't forget to take config backup!" ;
  exit 1 ;
else
  echo "Packages erased!" ;
fi

echo "Get the new packages.."
mkdir /tmp/networker_packages
wget -qO /tmp/networker_packages/lgtoclnt-19.2.1.1-1.x86_64.rpm ftp://127.0.0.1/lgtoclnt-19.2.1.1-1.x86_64.rpm
wget -qO /tmp/networker_packages/lgtoxtdclnt-19.2.1.1-1.x86_64.rpm ftp://127.0.0.1/lgtoxtdclnt-19.2.1.1-1.x86_64.rpm
wget -qO /tmp/networker_packages/lgtoman-19.2.1.1-1.x86_64.rpm ftp://127.0.0.1/lgtoman-19.2.1.1-1.x86_64.rpm
if [[ `ls -l /tmp/networker_packages/lgto* | wc -l` -ne 3 ]]; then
  echo "Check the downloaded packages: they are missing or outversioned!" ;
  exit 1;
else
  echo "Packages downloaded!" ;
fi

echo "Installing the packages.."
yum localinstall -y /tmp/networker_packages/lgtoclnt-19.2.1.1-1.x86_64.rpm /tmp/networker_packages/lgtoxtdclnt-19.2.1.1-1.x86_64.rpm /tmp/networker_packages/lgtoman-19.2.1.1-1.x86_64.rpm > /dev/null
if [[ `rpm -qa | grep 'lgto.*-19\.2\.1\.1.*' | wc -l` -ne 3 ]]; then
  echo "Check the installed packages!" ;
  exit 1;
else
  echo "Packages installed!" ;
fi

echo "Checking the backup network interface.."
for iface in `ip link show | grep 'mq state UP' | awk -F ':' '{print $2}'` ; do
  if [[ `tcpdump -nn -v -i $iface -s 1500 -c 1 'ether[20:2] == 0x2000' | grep 'Native VLAN ID.*' | awk -F ':' '{print $3}' | grep $VLAN | wc -l  2>/dev/null` -eq 1 ]]; then
    bck_iface=$iface ;
    break ;
  fi
done
if [[ -z "$bck_iface" ]]; then
  echo "Backup vlan cannot be found!" ;
  exit 1 ;
else
  echo "Backup vlan" $bck_iface ;
fi

echo "Setting up the backup network.."
nmcli con del $bck_iface
nmcli con add con-name $bck_iface ifname $bck_iface type ethernet autoconnect yes
nmcli con mod $bck_iface ipv4.method manual ipv4.addresses $IP

if [[ -z $ROUTE ]]; then
  echo "No route needed!"
else
  echo "Adding static routes.."
  IFS=',' read -ra RS <<< "$ROUTE"
  GW=${RS[-1]}
  for SR in ${RS[@]/$GW}; do
    nmcli con mod $bck_iface +ipv4.routes "$SR $GW"
  done
fi

nmcli con down $bck_iface
nmcli con up $bck_iface

systemctl restart networker

echo "Cleaning the installation packages.."
rm -r /tmp/networker_packages
