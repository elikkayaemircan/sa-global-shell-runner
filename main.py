#
# _author_ = Emircan Elikkaya <elikkaya.emircan@gmail.com>
#
# Copyright (c) 2023
#
# Licensed under the No Man's License, Version 1.0 (the "License");
# just kidding! Use it as you want and cite the Author.
#
# v0.X Last Update: November 26, 2021
#


"""
#### Synopsis
SA Global Shell Runner: A top-level program to offer parallel execution

#### Description
This top-level program offers you a parallel execution environment which can be used for reporting and server configuration.
One can implement any kind of custom script to use in here. After the basic integration, just run the code with the following instructions..

#### Available Actions
allChecks:
    ... (will be added later)
allConfigs:
    ... (will be added later)

#### Available Targets
    ... (will be added later)

#### Python Example
    ... (will be added later)
"""


import threading as mt
import queue

import os, sys, shutil, csv, subprocess

from allchecks import *
from allconfigs import *
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime
from time import sleep
from getpass import getpass


WORKDIR = os.getcwd()
TIMESTAMP = datetime.now().strftime("%Y-%m-%d")


allChecks = { "DRY_CHECK": DryCheck,
              "CENTRIFY" : CentrifyCheck,
              "TELEGRAF" : TelegrafCheck,
              "ROOT"     : RootCheck,
              "AUDIT"    : AuditCheck,
              "SYSDNS"   : SysDNSCheck,
              "BMCIP"    : BmcIPCheck,
              "PATCHREPO": PatchRepo,
}

allConfigs = { "DRY_CONF"  : DryConf,
               "ADJOIN"    : AdjoinConf,
               "NWTEAM"    : NWTeamConf,
               "NWBACKUP"  : NWBackupConf,
               "ROOTPASS"  : RootPassConf,
}

allAdmins = { "DNUSERNAME" : ("NAME SURNAME"),
}


class Parser:

    def __init__(self, target, action):
        self.target = target
        self.action = action
        self.threadS = set()
        self.threadQ = queue.Queue(maxsize=0)

    def collect(self):

        if self.target.upper() == "ALL" or \
           self.target.upper() in allAdmins:

            if not os.path.exists(WORKDIR+"/tmp/OPSWARE_"+TIMESTAMP+".csv"):
                source = "/data/opsware_hostlist.csv"
                destination = WORKDIR+"/tmp/OPSWARE_"+TIMESTAMP+".csv"
                shutil.copy(source, destination)
            os.chdir(WORKDIR+"/tmp")
            if self.target.upper() in allAdmins:    # Select the admin nodes
                os.system("grep -i '"+allAdmins[self.target.upper()]+"' OPSWARE_"+TIMESTAMP+".csv >> "+self.target+".csv")
            else:
                shutil.copy("OPSWARE_"+TIMESTAMP+".csv", self.target+".csv")
            with open(self.target+".csv", "r") as csv_read:
                csv_reader = csv.reader(csv_read, delimiter=",")
                [ self.threadS.add(node[3]) for node in csv_reader ]
            os.remove(self.target+".csv")
            return self.threadS

        else:

            source = WORKDIR+"/"+args.run_for
            if self.action.upper() in allChecks:
                with open(source, "r") as csv_read:
                    csv_reader = csv.reader(csv_read, delimiter=",")
                    [ self.threadS.add(node[0]) for node in csv_reader ]
            elif self.action.upper() in allConfigs:
                if self.action.upper() in [ "ADJOIN", "ROOTPASS" ]: credentials = UserAuth()
                else: credentials = []
                self.threadS = []
                with open(source, "r") as csv_read:
                    csv_reader = csv.reader(csv_read, delimiter=",")
                    [ self.threadS.append(node+credentials) for node in csv_reader ]
            else: print("Action not found..") ; print("\n") ; sys.exit(1)
            return self.threadS

    def dropExceptions(self, q_out):

        if self.action.upper() in allConfigs:

            if self.target.upper() not in [ "ALL" ] and \
               self.target.upper() not in allAdmins:
                # No exception needed here, custom configuration list given
                [ self.threadQ.put(node) for node in self.threadS ]
                del self.threadS
                return self.threadQ
            else:
                # This method is quite dangerous, do not use this without The Admin
                print("This method is quite dangerous! Usage is forbidden..") ; print("\n") ; sys.exit(1)
                """
                if os.path.exists(WORKDIR+"/exceptions/"+self.action.upper()+".txt"):
                    with open(WORKDIR+"/exceptions/"+self.action.upper()+".txt", "r") as csv_read:
                        csv_reader = csv.reader(csv_read, delimiter=":")
                        [ (self.threadS.discard(node_except[0].strip()), q_out.put([ node_except[0].strip() , "EXCEPTION:\n"+node_except[1].strip() ])) for node_except in csv_reader ]
                    [ self.threadQ.put(node) for node in self.threadS ]
                    del self.threadS
                    return self.threadQ
                else:
                    [ self.threadQ.put(node) for node in self.threadS ]
                    del self.threadS
                    return self.threadQ
                """

        elif self.action.upper() in allChecks:

            if os.path.exists(WORKDIR+"/exceptions/"+self.action.upper()+".txt"):
                with open(WORKDIR+"/exceptions/"+self.action.upper()+".txt", "r") as csv_read:
                    csv_reader = csv.reader(csv_read, delimiter=":")
                    [ (self.threadS.discard(node[0].strip()), q_out.put([ node[0].strip() , "EXCEPTION" , node[1].strip() ])) for node in csv_reader ]
                [ self.threadQ.put(node) for node in self.threadS ]
            else:
                [ self.threadQ.put(node) for node in self.threadS ]
            del self.threadS
            return self.threadQ

        else:
            print("Something went wrong. Exiting..") ; print("\n") ; sys.exit(1)



class Worker(mt.Thread):

    def __init__(self, q_in, action, q_out):
        self.q_in = q_in
        self.q_out = q_out
        self.action = action
        super(Worker, self).__init__()
        super(Worker, self).setDaemon(True)

    def run(self):
        if self.action.upper() in allChecks: runFrom = allChecks
        elif self.action.upper() in allConfigs: runFrom = allConfigs
        else: print("Action not found..") ; print("\n") ; sys.exit(1)
        while not self.q_in.empty():
            node = self.q_in.get(timeout=3)  # 3s timeout
            #print(node, mt.current_thread().ident)    # open this to see which threads run your job
            # do whatever work you have to do on work
            self.q_out.put(runFrom[self.action.upper()](node))
            self.q_in.task_done()


class Harvester:

    def __init__(self, q, action):
        self.q = q
        self.action = action

    def run(self):
        with open(WORKDIR+"/reports/"+TIMESTAMP+"_"+self.action.upper()+".csv", "w") as csv_write:
            csv_writer = csv.writer(csv_write, delimiter=",")
            while True:
                try:
                    result = self.q.get(timeout=3)  # 3s timeout
                except queue.Empty:
                    return
                csv_writer.writerow( result )
                self.q.task_done()

    def mail(self):
        # Move the report first
        source = WORKDIR+"/reports/"+TIMESTAMP+"_"+self.action.upper()+".csv"
        destination = "/opsw/Server/@/reporthost/files/root/reports/"+self.action.upper()+"/"+TIMESTAMP+"_"+self.action.upper()+".csv"
        shutil.move(source, destination)
        # Copy the main db inventory if not exists
        if not os.path.exists("/opsw/Server/@/reporthost/files/root/reports/tmp/"+TIMESTAMP+"-MAINDB-INVENTORY.csv"):
            source = WORKDIR+"/tmp/MAINDB-INVENTORY_"+TIMESTAMP+".csv"
            destination = "/opsw/Server/@/reporthost/files/root/reports/tmp/"+TIMESTAMP+"-MAINDB-INVENTORY.csv"
            shutil.copy(source, destination)
        cmd = "/reports/virtualenv/bin/python3 /reports/"+self.action.upper()+"/main.py"
        send_mail = subprocess.Popen(
            ["rosh", "-l", "root", "-n", "reporthost", "-w", "120", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = send_mail.communicate()
        if send_mail.returncode == 0 or \
           send_mail.returncode == 1:
            print("Mail sent successfully.\n")
        else:
            print("Something went wrong! Mail cannot be sent..\n", err, "\n")


def ThreadCounter(q_in):
    while not q_in.empty():
        print("    Targets remain: {}").format(q_in.qsize())
        sleep(30)    # print number of hosts to scan at each 30 seconds
    print("\n")

def UserAuth():
    username = raw_input("Username: ")
    password = getpass(prompt="Password: ")
    return [ username, password ]


if __name__ == "__main__":

    timeStart = datetime.now()

    """ Get the arguments. """
    ap = ArgumentParser( description = __doc__, formatter_class=RawTextHelpFormatter )
    ap.add_argument( "-r", "--report", action="store_true", help="Use this option to run reporting" )
    ap.add_argument( "-c", "--configure", action="store_true", help="Use this option to run server configuration" )
    ap.add_argument( "-t", "--threads", type=int, help="Choose number of threads to run the action\n"
                                                          "Default is single thread \n16 is good enough for heavy loads", dest='threads', default=1 )
    ap.add_argument( "--run_for", type=str, help="Specify target host group to run on", dest="run_for", default=None, required=True )
    ap.add_argument( "--action", type=str, help="Choose which action to run the report or configuration", dest="action", default=None, required=True )
    ap.add_argument( "--mail", action="store_true", help="Use this option to mail the report")
    if len(sys.argv) == 1: ap.print_help(sys.stderr) ; sys.exit(1)
    args = ap.parse_args()

    os.system("clear")
    print("Preparing enviroment for action {} on target identified by {}...").format(args.action, args.run_for)
    outQ = queue.Queue(maxsize=0)

    ObjQ = Parser(args.run_for, args.action)
    ObjQ.collect()
    threadQ = ObjQ.dropExceptions(outQ)
    print("Number of device to connect {}! Starting...\n").format(threadQ.qsize())
    if args.configure:
        if args.action.upper() in [ "ADJOIN", "ROOTPASS" ]:
            for line in list(threadQ.queue): print("    "+"   ".join(line[:-2]))
        else:
            for line in list(threadQ.queue): print("    "+"    ".join(line))
        if raw_input("\nIs the data you gave correct (Yes/No): ").lower() != "yes": sys.exit(1)
    elif args.report:
        print("Hope you test the code before submitting!\n")
    else:
        print("Not a valid action has been choosed!\n")
        sys.exit(1)
    for t in range(args.threads):
        Worker(threadQ, args.action, outQ).start()
        #print("Worker at: ", t)
    ThreadCounter(threadQ)
    threadQ.join()  # blocks until the queue is empty.
    print("Collecting output for action {} on target identified by {}...\n").format(args.action, args.run_for)
    Report = Harvester(outQ, args.action)
    Report.run()
    outQ.join()
    if args.mail: Report.mail()

    timeFinish = datetime.now()
    print("Time to complete this job with {} thread(s): "+str(timeFinish - timeStart)+"\n").format(args.threads)

    goodBye = """### RUN COMPLETED!
    A NICE QUOTE TO SAY GOODBYE.\n"""
    print(goodBye)

# End of the code
