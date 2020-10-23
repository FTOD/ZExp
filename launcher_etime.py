#!/usr/bin/python3
from benchDesc.benchsDesc import *
import getopt, sys
tacle_path = "/home/baiz/Work/tacle-bench/bench/"
#tacle_path = "/home/zhenyubai/tacle-bench/bench/"


try:
        opts,args = getopt.getopt(sys.argv[1:], '',['debug-errors','arch=','logPath=','taclePath=','split-threshold=','path='])
except getopt.GetoptError as err:
        print(err)
        print("command -arch=[complex,simple] -xdd=[xdd,xddp]")


logPath = "../log/"
debug_error = False
options = " "
for o,a in opts:
    if o == "--arch":
        if a == "complex":
            options = options + " --complex"
        elif a == "simple":
            pass
        else:
            print("error arch option")

    elif o =="--split-threshold":
        options = options + " --split-threshold=" + a

    elif o == "--path":
        logPath = a

    elif o == "--taclePath":
        tacle_path = a

    elif o == "--debug-errors":
        debug_error = True
    else :
        print("error," + o)



test_set = process(tacle_path,debug_error)


f = open ("Makefile", "w")
f.write(".PHONY:all\n")
f.write("all:")
for bench in test_set:
    f.write((bench[2]+" "))
f.write("\n$(info Starting all)\n");


for bench in test_set:
    w0 = bench[2] + ": \n" + "\t$(info analyzing " + bench[2] + " )\n" + "\t -@ (time -v ../etime -v  " + bench[0] + " " + bench[1] + options + " ) 2>" + logPath + bench[2] + "\n"

    f.write(w0)
f.close()
