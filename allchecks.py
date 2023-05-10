#!/usr/bin/python

#
# Check (reporting) scripts are collected here
# Respect to custom script output or ogfs return code
# result will be decided here
#


import os, subprocess, re

WORKDIR = os.getcwd()


def DryCheck(node):
    """ Returns nothing, do nothing..
    Only the hosts for the specified targed. """
    return [ node ]


def CentrifyCheck(node):
    """ Check centrifydc agent status
    and zone that the node is joined. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "60", "-s", WORKDIR+"/allcustom/_checkCentrify.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 60 saniye asildi" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip() ]


def TelegrafCheck(node):
    """ Check telegraf agent status
    and configuration version. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "60", "-s", WORKDIR+"/allcustom/_checkTelegraf.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 60 saniye asildi" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip() ]


def RootCheck(node):
    """ Check root privileges defined on centrify
    get the zone and the privileged users. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "90", "-s", WORKDIR+"/allcustom/_checkRoot.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 90 saniye asildi" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip() ]


def AuditCheck(node):
    """ Check audit service and configuration
    for servers. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "60", "-s", WORKDIR+"/allcustom/_checkAudit.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").replace("\n", ",").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 60 saniye asildi" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip() ]


def SysDNSCheck(node):
    """ Check system DNS record and OGFS IP
    compare them if they are equal or not. """
    try:
        _OGFSIP = re.findall( "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*",
            re.findall( "primary_ip: *[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*",
            subprocess.check_output([ "/bin/cat", "/opsw/Server/@/"+node+"/info"  ]) )[0] )[0]
    except:
        return [ node, "checkNA", "-", "-", "OGFS IP adresi alinamadi" ]
    callCheck = subprocess.Popen(
        ["/bin/bash", WORKDIR+"/allcustom/_checkSysDNS.sh", node, _OGFSIP ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 30 saniye asildi", "-", "-" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip(), "-", "-" ]


def BmcIPCheck(node):
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "30", "-s", WORKDIR+"/allcustom/_checkBmcIP.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.rstrip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 30 saniye asildi", "-", "-" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip(), "-", "-" ]


def PatchRepo(node):
    """ Check Satellite Repo status
    and available updates on the system. """
    callCheck = subprocess.Popen(
        ["rosh", "-l", "root", "-n", node, "-w", "120", "-s", WORKDIR+"/allcustom/_checkPatchRepo.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = callCheck.communicate()
    if callCheck.returncode == 0:
        return [ node ] + out.strip("\n").rsplit(",")
    elif callCheck.returncode == 248:
        return [ node, "checkNA", "Timeout 120 saniye asildi", "-" ]
    else:
        return [ node, "checkNA", err.rstrip("\n").strip(), "-" ]
