#!/usr/bin/python

#
# Configuration  scripts are collected here
# Respect to defined input, configuration jobs are running on the target hosts
# A csv based task logbook is produced under reports
#


import os, subprocess

WORKDIR = os.getcwd()


def DryConf(node):
    """ Returns nothing, do nothing..
    Only the hosts and the config parameters from custom input. """
    return node


def AdjoinConf(node):
    """ Runs adjoin job with given parameters
    DMZ or LOCAL needed, zone name needed, password input will be implemented. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node[0], "-w", "180", "-s", WORKDIR+"/allcustom/_confAdjoin.sh", node[1], node[2], node[3], node[4] ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node[0] ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node[0], "UNKNOWN", "Timeout 180 saniye asildi" ]
    else:
        return [ node[0], "ERROR", err.rstrip("\n").strip() ]


def NWTeamConf(node):
    """ Configure network interfaces
    create TEAM with given ip/cidr, default gw, vlan id. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node[0], "-w", "240", "-s", WORKDIR+"/allcustom/_confNWTeam.sh", node[1], node[2], node[3] ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node[0],  "TEAM_CREATED", node[1] ]
    elif callCheck.returncode == 248:
        return [ node[0], "UNKNOWN", "Timeout 240 saniye asildi" ]
    else:
        return [ node[0], "ERROR", err.rstrip("\n").strip() ]


def NWBackupConf(node):
    """ Configure backup interface and agent
    create agent, add network connection with ip/cidr, vlan id, static routes. """
    if len(node) > 3:
        SRs=node[3:-1] ; SRs = ",".join(SRs)+","+node[-1]
        callCheck = subprocess.Popen(
            ["rosh", "-l", "root", "-n", node[0], "-w", "240", "-s", WORKDIR+"/allcustom/_confNWBackup.sh", node[1], node[2], SRs ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = callCheck.communicate()
        if callCheck.returncode == 0:
            return [ node[0],  "BACKUP_CONFIGURED", node[1] ]
        elif callCheck.returncode == 248:
            return [ node[0], "UNKNOWN", "Timeout 240 saniye asildi" ]
        else:
            return [ node[0], "ERROR", err.rstrip("\n").strip() ]
    else:
        callCheck = subprocess.Popen(
            ["rosh", "-l", "root", "-n", node[0], "-w", "240", "-s", WORKDIR+"/allcustom/_confNWBackup.sh", node[1], node[2] ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = callCheck.communicate()
        if callCheck.returncode == 0:
            return [ node[0],  "BACKUP_CONFIGURED", node[1] ]
        elif callCheck.returncode == 248:
            return [ node[0], "UNKNOWN", "Timeout 240 saniye asildi" ]
        else:
            return [ node[0], "ERROR", err.rstrip("\n").strip() ]


def RootPassConf(node):
    """ Change root password on target hosts
    password input will be implemented. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node[0], "-w", "60", "-s", WORKDIR+"/allcustom/_confPasswd.sh", node[1], node[2] ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node[0] ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node[0], "UNKNOWN", "Timeout 60 saniye asildi" ]
    else:
        return [ node[0], "ERROR", err.rstrip("\n").strip() ]
