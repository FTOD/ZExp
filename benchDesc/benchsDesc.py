#!/usr/bin/python3
import subprocess,os
import json
import getopt, sys

PapaBenchFBW_tasks = ["check_failsafe_task",
"check_mega128_values_task",
"send_data_to_autopilot_task",
"servo_transmit",
"test_ppm_task",
"__vector_5",
"__vector_6",
"__vector_10"]

PapaBenchAutoPilot_tasks = ["altitude_control_task",
"climb_control_task",
"link_fbw_send",
"navigation_task",
"radio_control_task",
"receive_gps_data_task",
"reporting_task",
"stabilisation_task",
"__vector_5",
"__vector_12",
"__vector_17",
"__vector_30"]

DEBIE_tasks = [
"InitHealthMonitoring",
"HandleHealthMonitoring",
"InitHitTriggerTask",
"HandleHitTrigger",
"InitAcquisitionTask",
"HandleAcquisition",
"InitTelecommandTask",
"HandleTelecommand"
]

def regrouping_parallel_res(res):
    res_papaFBW = 0
    res_papaAP = 0
    res_debie = 0
    res_other = []
    for i in res:
        if i[0] in PapaBenchAutoPilot_tasks:
            res_papaAP = res_papaAP + i[1]
        elif i[0] in PapaBenchFBW_tasks:
            res_papaFBW = res_papaFBW + i[1]
        elif i[0] in DEBIE_tasks:
            res_debie = res_debie + i[1]
        else:
            res_other.append(i)
    res_other.append(("PapaBench_AutoPilot",res_papaAP))
    res_other.append(("PapaBench_FlyByWire",res_papaFBW))
    res_other.append(("DEBIE",res_debie))
    return res_other



def process(tacle_path, test_error=False):
    kernel_basedir = tacle_path + "kernel"
    sequential_basedir = tacle_path + "sequential"
    app_basedir = tacle_path + "app"
    parallel_basedir = tacle_path + "parallel"

    otawa_exec = "../xdd"

    kernel_apps = [x for x in os.listdir(kernel_basedir)]
    sequential_apps = [x for x in os.listdir(sequential_basedir)]
    app_apps = [x for x in os.listdir(app_basedir)]

    #parallel group is organized differently, set manually
    parallel_apps = ["DEBIE", "PapaBench", "rosace"]


    # those who does not work, refer to Googl drive XDD/otawa+tacle Excel for detail of each error
    kernel_error = ["recursion", #halfAbs
    "pm", #halfAbs
    "quicksort", #CFG checker
    "jfdctint" #dcache
    ]

    sequential_error = ["ndes", #branching_node = nullptr
    "h264_dec", #CFG disconnected
    "huff_dec", #HalfAbs
    "huff_enc", #CFG disconnected
    "anagram", #CFG checker
    "gsm_enc", #HalfAbs
    "rijndael_dec", #.ff
    "epic", #.ff
    "susan", #CFG disconnected
    "cjpeg_transupp", #CFG disconnected
    "cjpeg_wrbmp", #.ff, zbai incapable to fix it
    "ammunition", #CFG disconnected
    "adpcm_dec", #dcache
    "adpcm_enc", #infinity in CLPBlockBuilder
    "mpeg2", #infinity CLPAnalysis
    ]

    app_error = []
    parallel_error = ['ros_th2_main',
    'ros_th1_main',
    "receive_gps_data_task",
    "reporting_task",
    "navigation_task"
    ]




    kernel_infinite = ["bitonic", #ACS builder
            "filterbank" #ILP solver, error code 2 after long time
        ]
    sequential_infinite = ["mpeg2"]
    app_infinite = []


    #A benchmark of group parallel has several tasks per executable, and may have several executables.
    #The information can be found in TASK.json

    parallel_testSet = []
    for app in parallel_apps:
        _dir_json = parallel_basedir + "/" + app + "/TASKS.json"
        with open(_dir_json) as json_file:
            _j = json.load(json_file)
            _tasks =_j['tasks']
            _executable =_j['execs']


        for _t in _tasks:
            #Do not include those who does not work
            if _t['name'] in parallel_error:
                break
            #can not found executable information for a task
            if 'exec' not in _t:
                print("No exec precised, use the first one on execs lists")
                exit(0)
            #executable info found, try to find the executable file
            if find_executable(_t['exec'],_executable) != None:
                exec_path=parallel_basedir + "/" +app+"/"+find_executable(_t["exec"],_executable)
                task_name = _t['name']
                parallel_testSet.append((exec_path,task_name,task_name))
            #executable info provided but file not found?
            else:
                print("Executable specified but not found")
                exit(0)




    if not test_error:
        #final test set, removing bad and complex benchs
        kernel_apps = [x for x in kernel_apps if x not in kernel_error and x not in kernel_infinite]
        sequential_apps = [x for x in sequential_apps if x not in sequential_error and x not in sequential_infinite]
        app_apps = [x for x in app_apps if x not in app_error and x not in app_infinite]
    else:
        kernel_apps = [x for x in kernel_error if x not in kernel_infinite]
        sequential_apps = [x for x in sequential_error if x not in sequential_infinite]
        app_apps = [x for x in app_error if x not in app_infinite]

    print("-----------------\n",kernel_apps)
    print("-----------------\n",sequential_apps)
    print("-----------------\n",app_apps)
    print("=================\n")
    #create complete file name
    kernel_testSet = [ (complete_exec_filename(kernel_basedir,x),complete_fun_name(x),x) for x in kernel_apps]
    sequential_testSet = [ (complete_exec_filename(sequential_basedir,x),complete_fun_name(x),x) for x in sequential_apps ]
    app_testSet= [ (complete_exec_filename(app_basedir,x),complete_fun_name(x),x) for x in app_apps ]

    all_testSet = kernel_testSet + sequential_testSet + app_testSet + parallel_testSet

    print(all_testSet)
    return all_testSet



#complete file with test_name(benchname)
def complete_exec_filename(basedir, benchname):
    return basedir + "/" + benchname + "/" +  benchname + ".elf"

#complete the entry point of each benchmark, convention is benchname_main.
def complete_fun_name (benchname):
    return benchname + "_main"

#find executable path
def find_executable(task, execs):
    for _exec in execs:
        if _exec['name'] == task:
            return _exec['path']
    return None



if __name__ == "__main__":
    print("testing module benchDesc")
    tacle_path = "/home/baiz/Work/tacle-bench/bench/"
    process(tacle_path)
