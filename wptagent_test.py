from ast import Global
import logging
import shutil
import pytest
import warnings
import os
global DEVTOOLS_OPT, DIRPATH

def setup_work_dir():
    ### SETUP FOR FINDING WORKING PATH ###
    if not os.path.isdir("work"): # Check to See if the Work Dir is present
        warnings.warn(UserWarning("No Work Dir Was Found")) 

    global DEVTOOLS_OPT, DIRPATH
    DEVTOOLS_OPT = {'devtools': "1_devtools.json.gz",
                    'netlog': "1_netlog_requests.json.gz",
                    'requests': "1_timeline_requests.json.gz",
                    'optimization': "1_optimization.json.gz",
                    'user': "1_user_timing.json.gz",
                    'coverage': None,
                    'cpu': "1_timeline_cpu.json.gz",
                    'v8stats': "1_v8stats.json.gz",
                    'cached': None,
                    'out': None,
                    'noheaders': None,
                    'new_func': None}
                    
    try:
        DIRPATH = "work/{}".format(os.listdir("work")[0])
    except:
        warnings.warn(UserWarning("No WorkPath Was Found")) 

    for dir in os.listdir(DIRPATH): # Finding the folder with browser data in it
        if ".1.0" in dir:
            DIRPATH = "{}/{}".format(DIRPATH,dir) # work/workID.1.0/
            break

    for key,file in DEVTOOLS_OPT.items(): # For each item in DEVTOOLS_OPT we want to check if its a file
        if file == None:
            continue

        DEVTOOLS_OPT[key] = f"{DIRPATH}/{file}" # work/workID.1.0/1_filename.json.gz
        if not os.path.isfile(DEVTOOLS_OPT[key]): # If not a file set None
            DEVTOOLS_OPT[key] = None

    ### END OF SETUP FOR FINDING WORKING PATH ###

def test_imports():
    # pylint: disable=W0611
    import logging
    import gzip
    import zipfile
    import re
    import traceback
    import psutil
    import glob

    import hashlib
    import multiprocessing
    import shutil
    import threading

    import gc
    import PIL
    import numpy
    import requests
    import selenium
    
    import wptagent
    from internal.browsers import Browsers
    from internal.webpagetest import WebPageTest
    from internal.traffic_shaping import TrafficShaper
    from internal.adb import Adb
    from internal.ios_device import iOSDevice


    try:
        import ujson as json
    except BaseException:
        warnings.warn(UserWarning("Ujson couldn't import, defaulting to json lib"))
        import json

def test_wptutil():
    import internal.wptutil as wptutil
    wptutil.test_logsingleton()

def devtools_parser(): 
    """Runs the Devtool processs tools, with new and old functions"""
    import internal.support.devtools_parser as dp
    from internal.wptutil import LogSingleton as logs

    setup_work_dir()

    # Init Logsingleton
    logs(log=True, profile=False) 
    # Init Logging
    logging.basicConfig(level=logging.CRITICAL, format="%(asctime)s.%(msecs)03d - %(message)s", datefmt="%H:%M:%S")
    
    # Set up config
    DEVTOOLS_OPT["out"] = f"{DIRPATH}/orginalData.json" # Set the out file
    DEVTOOLS_OPT["cached"] = 0
    DEVTOOLS_OPT["noheaders"] = False 
    
    logs.write("")
    logs.write("*** (OLD) Running Devtools ***")

    # Init DevtoolsParser
    devtools = dp.DevToolsParser(DEVTOOLS_OPT)
    devtools.process()

    logs.set_time_now()
    # Set up config to run new functions
    DEVTOOLS_OPT["new_func"] = True
    DEVTOOLS_OPT["out"] = f"{DIRPATH}/newData.json" # Set the out file

    logs.write("")
    logs.write("*** (NEW) Running Devtools ***")
    # Init DevtoolsParser
    devtools = dp.DevToolsParser(DEVTOOLS_OPT)
    devtools.process()
    logs.finish()

def devtools_parser_compare_data():
    orginalData = {}
    newData = {}
    
    # Import the nested_diff for comparing profil data
    try: 
        from nested_diff import diff
    except:
        logging.exception("Please install nested_diff: pip3 install nested_diff")
        return
    import ujson as json
    
    # Read Pagedata in from Files
    with open("{}/{}".format(DIRPATH,"orginalData.json")) as f_in:
        orginalData = json.load(f_in)
    with open("{}/{}".format(DIRPATH,"newData.json")) as f_in:
        newData = json.load(f_in)
    # Put Info in about what each letter stands for.    
    diffC = {"info":{
                "A": "stands for 'added', it's value - added item.",
                "C": "is for comments; optional, value - arbitrary string.",
                "D": "means 'different' and contains subdiff.",
                "E": "diffed entity (optional), value - empty instance of entity's class.",
                "I": "index for sequence item, used only when prior item was omitted.",
                "N": "is a new value for changed item.",
                "O": "is a changed item's old value.",
                "R": "key used for removed item.",
                "U": "represent unchanged item.",
            },
            "diff": {}
        }
    diffC['diff'].update(diff(orginalData,newData,U=False))
    with open(f"{DIRPATH}/pageDataComp.json", "w") as f_out:
        json.dump(diffC,f_out)

    print("** Checking For Differences **")
    if any(diffC['diff']): # If not empty {} then print diff and fail
        print("Keys:\n{}\nDifferences:\n{}".format(diffC['info'],diffC['diff']))
        assert False
    else: # Else No Differences
        print("    No Differences Found\n")

def devtools_parser_log_print():
    orginal = ""
    with open("logging/log.txt") as f_in:
        orginal = f_in.read()

    print(orginal)

import argparse
parser = argparse.ArgumentParser(description='WebPageTest Agent.', prog='wpt-agent')

parser.add_argument('-v', '--verbose', action='count',help="Increase verbosity (specify multiple times for more)."
                    " -vvvv for full debug output.")

parser.add_argument('-d', action='store_true', default=False, help="Runs Metrics Devtools on the local store files")

#parser.add_argument('-r', type=int, default=1, help="Prints the avg of running the new and old functions")
parser.add_argument('-c', action='store_true', default=False, help="Prints the Compared Data from new and old functions")
parser.add_argument('-p', action='store_true', default=False, help="Prints the Performance metrics of new and old functions")
parser.add_argument('-l', action='store_true', default=False, help="Prints the default logs")

options, _ = parser.parse_known_args()

FunctionStack = []

if options.d:
    FunctionStack.append(devtools_parser)
if options.c:
    FunctionStack.append(devtools_parser_compare_data)
if options.p:
    FunctionStack.append(devtools_parser_log_print)
if options.l:
    FunctionStack.append(devtools_parser_log_print)
#for i in range(options.r): # Run count
for f in FunctionStack: # Call the function Stack
    f()

