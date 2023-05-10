#!/usr/bin/bash

TN=team0
IP=$1
GW=$2
VLAN=$3

echo 'Checking the interfaces..'
for iface in `ip link show | grep 'mq state UP' | awk -F ':' '{print $2}'` ; do
  if [[ `tcpdump -nn -v -i $iface -s 1500 -c 1 'ether[20:2] == 0x2000' | grep 'Native VLAN ID.*' | awk -F ':' '{print $3}' | grep $VLAN | wc -l  2>/dev/null` -eq 1 ]]; then
    IF1=$iface ;
    break ;
  fi
done

for iface in `ip link show | grep 'mq state UP' | awk -F ':' '{print $2}' | grep -v $IF1` ; do
  if [[ `tcpdump -nn -v -i $iface -s 1500 -c 1 'ether[20:2] == 0x2000' | grep 'Native VLAN ID.*' | awk -F ':' '{print $3}' | grep $VLAN | wc -l  2>/dev/null` -eq 1 ]]; then
    IF2=$iface ;
    break ;
  fi
done

if [[ -z "$IF1" ]] || [[ -z "$IF2" ]]; then
  echo 'Redundant interfaces cannot be found!'
  exit 1;
else
  echo 'Interfaces to create team: ' $IF1 $IF2 ;
fi

nmcli connection add type team autoconnect yes con-name $TN ifname $TN

nmcli connection modify $TN team.config '{ "runner": {"name": "activebackup"}}'
nmcli connection modify $TN ipv4.addresses $IP ipv4.method manual ipv4.gateway $GW
nmcli connection modify $TN ipv4.dns-search example.com
nmcli connection modify $TN ipv4.dns 127.0.0.1 +ipv4.dns 127.0.0.2

nmcli connection add type team-slave con-name $TN-port1 ifname $IF1 master $TN
nmcli connection add type team-slave con-name $TN-port2 ifname $IF2 master $TN

nmcli con down team0
nmcli connection delete $IF1
nmcli connection delete $IF2
nmcli con up team0

sleep 5

echo "OK"
