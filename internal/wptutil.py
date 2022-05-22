import logging
import platform
import time
from datetime import datetime
import os
import json
from shutil import rmtree


def util_remove_file(_file):
    try:
        os.remove(_file)
    except:
        pass

def util_remove_dir(_dir):
    try:
        rmtree(_dir)
    except:
        pass

def util_makeDirs(_dir):
    if not os.path.isdir(_dir):
        os.makedirs(_dir)


def util_dbg_check_results(dir):
    """Checks to make sure common files are present in the persistent work dir"""
    currentFiles = f"{os.getcwd()}/results/{dir}"

    currentFiles = os.listdir(dir)
    expectedFiles = ["1_progress.csv.gz",
                     "1_trace.json.gz",
                     "1_user_timing.json.gz",
                     "1_timeline_cpu.json.gz",
                     "1_script_timing.json.gz",
                     "1_interactive.json.gz",
                     "1_long_tasks.json.gz",
                     "1_feature_usage.json.gz",
                     "1_v8stats.json.gz",
                     "1_screen.jpg",
                     "1_console_log.json.gz",
                     "1_timed_events.json.gz",
                     "1.0.histograms.json.gz",
                     "1_visual_progress.json.gz",
                     "1_devtools_requests.json.gz",
                     "1_page_data.json.gz"]

    for file in expectedFiles:
        if file not in currentFiles:
            LogSingleton.write(f"{file}: WAS NOT FOUND BUT IT WAS EXPECTED")
            logging.critical(f"{file}: WAS NOT FOUND BUT IT WAS EXPECTED")


def util_dbg_options(options):
    """Default args for single test run"""
    LogSingleton(log=True, profile=True)
    #options.verbose = 4
    if platform.system() == 'Linux':
        logging.debug("Setting default arguments for headless server on Linux")
        #options.dockerized = True
        #options.xvfb = True
        #options.noidle = True
        #options.location = 'Test'
        #options.testout = 'id'
        #options.browser = 'Chrome'
    #elif platform.system() == 'Windows' # Could add support with Github actions

    if options.testurl == None or "google" in options.testurl:
        options.testurl = r"https://www.google.com/"
    elif "light" in options.testurl:
        options.testurl = r"http://sqa.3genlabs.net/hawksyntheticpageserver/Main.ashx?type=html&details=%22image%22:%7b%22count%22:10,%22height%22:300,%22width%22:500,%22delay%22:0,%22redirect%22:0%7d,%22css%22:%7b%22count%22:10,%22size%22:8000,%22delay%22:0,%22redirect%22:0%7d"
    elif "medium" in options.testurl:
        options.testurl = r"http://sqa.3genlabs.net/hawksyntheticpageserver/Main.ashx?type=html&details=%22image%22:%7B%22count%22:20,%22height%22:1024,%22width%22:1080,%22delay%22:0,%22redirect%22:10%7D,%22css%22:%7B%22count%22:20,%22size%22:2700,%22delay%22:0,%22redirect%22:10%7D,%22iframe%22:%7B%22count%22:20,%22rawtext%22:%7B%22linebreak%22:100,%22asciistart%22:33,%22asciiend%22:126,%22random%22:true,%22bytecount%22:100000%7D,%22delay%22:0,%22redirect%22:5%7D,%22iframe%22:%7B%22count%22:10,%22size%22:5000,%22delay%22:0,%22redirect%22:10%7D"
    elif "heavy" in options.testurl:
        options.testurl = r"http://sqa.3genlabs.net/hawksyntheticpageserver/Main.ashx?type=html&details=%22image%22:{%22count%22:100,%22height%22:1024,%22width%22:1080,%22delay%22:0,%22redirect%22:5},%22css%22:{%22count%22:100,%22size%22:2700,%22delay%22:0,%22redirect%22:5},%22iframe%22:{%22count%22:50,%22rawtext%22:{%22linebreak%22:100,%22asciistart%22:33,%22asciiend%22:126,%22random%22:true,%22bytecount%22:900000},%22delay%22:0,%22redirect%22:5},%22iframe%22:{%22count%22:10,%22size%22:800000,%22delay%22:0,%22redirect%22:10}"
    return options
    

class LogSingleton:
    __instance = None

    def __init__(self, workDir: str = "logging", compareDir: str = "compare", logFileName: str = "log.txt", profileFileName: str = "profile.json",
                 log: bool = False, profile: bool = False,
                 grabFunctionName: bool = True):
        """(Only One Class can be active) This Class Handles Logs, Profiling, and Comparing of Profiled Data"""
        if LogSingleton.__instance != None:
            raise Exception("Class is a singleton.")
        else:
            LogSingleton.__instance = self

        self.f_out_log = None  # a Log File type txt for logging out to
        self.f_out_profile = None  # a profile file type json to write to

        self.starttime = time.time()  # Start time
        self.lastcalltime = time.time()  # For logging last call time
        
        self.grabFunctionName = grabFunctionName # true false value for heavy stack inspection function
        self.grabProfile = profile  # true false value for grabing profile data
        self.grabLogs = log  # true false value for grabing logs
        self.logTime = True  # global log timing system
        self.logTotalTime = 0  # Total log time
        
        # ---- DIR ----
        self.cwd = os.getcwd()
        self.workDir = workDir # logging
        self.compareDir = f"{workDir}/{compareDir}" # logging/compare
        self.logFileName = logFileName # log.txt
        self.profileFileName = profileFileName # profile.json

        util_makeDirs(self.workDir) # Make the logging dir if not already there

        if os.path.isdir(self.compareDir): # Delete everything in compare dir
            util_remove_dir(self.compareDir)

        if self.grabLogs:  # Create the File Handler for Logs
            self.f_out_log = open(f"{self.cwd}/{workDir}/{logFileName}", "w", buffering=1)

        if self.grabProfile: # Create the File Handler for profile
            self.f_out_profile = open(f"{self.cwd}/{workDir}/{profileFileName}", "w", buffering=1)
            self.grabFunctionName == True
            self.profileData = {}

        if self.grabFunctionName:
            self.inspect = __import__("inspect")
    @staticmethod
    def set_time_now():
        if LogSingleton.__instance == None:
            return
        self = LogSingleton.__instance

        self.starttime = time.time()  # Start time
        self.lastcalltime = time.time()  # For logging last call time
        
    @staticmethod
    def get():
        """ Static access method. """
        if LogSingleton.__instance == None:
            LogSingleton()
        return LogSingleton.__instance

    @staticmethod
    def finish():
        """Finish function for LogSingleton, Only if LogSingleton was initialize will Something be done"""
        if LogSingleton.__instance == None:
            return
        LogSingleton.__instance.__del__()

    @staticmethod
    def write(_out: str = "", grabF=True):
        """(ONLY RUNS IF LOGSINGLETON IS ENABLED) Log writing tool that outputs to .txt file. This tool is meant to be used to debug testruns and not meant to be running constantly.
        _out is the string going to the .txt file.
        _grabF enables or disables a resource intensive stack calling(avg 5ms per call) for grabing the name of the function that called this write function"""
        if LogSingleton.__instance == None or LogSingleton.__instance.grabLogs == False:
            return

        self, logTime, _fileName, _lineNumber, _cn = LogSingleton.__instance, 0, "", "", ""

        if self.logTime:  # Check if Logging is enabled
            logTime = time.time()
            # Clear the dec with the int then cast back str
            elapsed = str(int((logTime - self.lastcalltime) * 1000))
            self.lastcalltime = logTime  # Set Last call time

        if self.grabFunctionName and grabF == True:  # Grabs Stack Info
            stack = self.inspect.stack()
            _fileName, _lineNumber, _cn = stack[1].filename.replace(
                self.cwd, ""), stack[1].lineno, stack[1][3]

        _timestamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')[:-3]
        _timeFromStart = str(int((time.time() - self.starttime)*1000))

        self.f_out_log.write(
            f"{_timestamp} | {_timeFromStart.ljust(5)} | {elapsed.ljust(5)} | {_out.ljust(28)} | {_fileName}|{_cn}|{str(_lineNumber)}>\n")

        if self.logTime:  # Finish Time of Logger
            self.logTotalTime += time.time() - logTime

    @staticmethod
    def prof(_cn: str = "", _des: str = "", **data):
        """Profiler for functions, Takes _cn (CallerName for specific Function), _des(Description if you want), data which can be compared later or tested
        for similarity, This function should be called once before and once after with same _cn name.\n
        example: \n
        prof("randomFunctionName", randomData=randomData)\n
        function_to_be_profiled(randomData)\n
        prof("randomFunctionName", randomData=randomData)"""
        if LogSingleton.__instance == None:
            return
        self = LogSingleton.__instance  # Set self

        if self.grabProfile == False:  # Check if we are profiling
            return

        secTime = (time.time() - self.starttime) * 1000  # Timing

        if _cn == "":  # If we should call stack
            _cn = self.inspect.stack()[1][3]

        if self.profileData.setdefault(_cn, {"description": _des, "start_ms": 0.0, "end_ms": 0.0, "dif_ms": 0.0, "Similar": {}, "data": {"before": {}, "after": {}}})["start_ms"] == 0.0:
            self.profileData[_cn]["start_ms"] = round(secTime, 4)
            for key, value in data.items():  # If Data is passes it will be set into the _cn
                self.profileData[_cn]['data']['before'][key] = value
            return
        elif(self.profileData[_cn]["dif_ms"] == 0.0):
            self.profileData[_cn]['end_ms'] = round(secTime, 4)
            self.profileData[_cn]['dif_ms'] = round(
                secTime - self.profileData[_cn]['start_ms'], 4)

            for key, value in data.items():
                self.profileData[_cn]['data']['after'][key] = value
                # If Data was passed twice then data is checked for similarity
                if key in self.profileData[_cn]['data']['before']:
                    self.profileData[_cn]["Similar"][key] = self.profileData[_cn]['data'][
                        'before'][key] == self.profileData[_cn]['data']['after'][key]
            return
        else:
            print(f"log_profiler: Was called one to many times in {_cn}")

    @staticmethod
    def comp(_cn: str = "", _cn1: str = "", _cn2: str = "", _data: list = []):
        """Compare looks at data args sent to the profiler, _cn is a name for this in the json, _cn1 is the first callername passed to the profil function.\n
        _cn2 is the second callername passed to the profil function\n 
        data is the string name of the data fields passed to the profiler\n
        logs.comp("CompareOfFunctions","ProfiledFunctionName","ProfiledFunctionName2",["randomDataName",...etc])"""
        if LogSingleton.__instance == None:
            return
        self = LogSingleton.__instance  # Set self

        try: # Import the nested_diff for comparing profil data
            from nested_diff import diff
        except:
            logging.exception("Please install nested_diff: pip3 install nested_diff")
            return

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
            }
        }
        util_makeDirs(f"{self.workDir}/compare/") # Making compare dir inside workingDir

        for key in _data: # Loop Through all the data
            if key not in self.profileData[_cn1]['data']['after'] and key not in self.profileData[_cn2]['data']['after']:
                logging.critical(f"COMPARE KEY WAS NOT FOUND: {key}")
                return

            cn1, cn2 = self.profileData[_cn1]['data']['after'][key], self.profileData[_cn2]['data']['after'][key]
            
            diffC.update(diff(cn1,cn2,U=False))
            with open(f"{self.workDir}/compare/{key}.json", "w") as f_out:
                json.dump(diffC,f_out)
                #f_out.write(str(diffC))

    def __del__(self):
        """Writes out open files"""
        try:
            if self.grabProfile:
                json.dump(self.profileData, self.f_out_profile)
                self.f_out_profile.close()

            if self.grabLogs:
                if self.logTime:
                    self.write(
                        _out=f"Total Log Time taken in MS : {int(self.logTotalTime * 1000)}")
                self.f_out_log.close()

            LogSingleton.__instance = None
        except:
            pass

def test_logsingleton():
    """Testing LogSingleton"""
    # Inits LogSingleton
    LogSingleton(log=True, profile=True) 
    
    # Try to init LogSingleton again, should fail
    try:
        LogSingleton(log=True, profile= True)
        assert False
    except:
        assert True
    # Write some logs.
    LogSingleton.write("testing", False)
    LogSingleton.write("testing", False)

    # Profile
    data = {"test":"HERE","test1":"test"}
    LogSingleton.prof("WriteFunction", data=data)
    LogSingleton.write("testadfasdf")
    LogSingleton.prof("WriteFunction", data=data)

    data = {"test":"HERE","test1":"TEST"}
    LogSingleton.prof("WriteFunction2", data=data)
    LogSingleton.write("teatsdfasdf")
    LogSingleton.prof("WriteFunction2", data=data)

    # Compare the data between the two profiles
    LogSingleton.comp("WriteFunctionComp", "WriteFunction","WriteFunction2", ["data"])

    LogSingleton.finish()

    assert os.path.isfile("logging/profile.json")
    assert os.path.isfile("logging/log.txt")
    assert os.path.isfile("logging/compare/data.json")



