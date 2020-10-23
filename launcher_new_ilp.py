#!/usr/bin/python3
from xddOpts import *
from benchDesc.benchsDesc import *
import getopt, sys
tacle_path = "/home/baiz/Work/tacle-bench/bench/"
#tacle_path = "/home/zhenyubai/tacle-bench/bench/"

xddOptions = XddOptions()
xddOptions.set_algo("xdd")

try:
        opts,args = getopt.getopt(sys.argv[1:], '',['debug-errors','arch=','xdd=','logPath=','taclePath=','split-threshold=','path='])
except getopt.GetoptError as err:
        print(err)
        print("command -arch=[complex,simple] -xdd=[xdd,xddp]")


logPath = "../log/"
debug_error = False
for o,a in opts:
    if o == "--arch":
        if a == "complex":
            xddOptions.set_arch("complex")
        elif a == "simple":
            xddOptions.set_arch("simple")
        else:
            print("error arch option")
    elif o == "--xdd":
        if a == "xdd":
            xddOptions.set_algo("xdd")
        elif a == "etime":
            xddOptions.set_algo("etime")
        else:
            print("error xdd option:" + a)

    elif o =="--split-threshold":
        xddOptions.set_split_threshold(int(a))

    elif o == "--path":
        logPath = a

    elif o == "--taclePath":
        tacle_path = a

    elif o == "--debug-errors":
        debug_error = True
    else :
        print("error," + o)



test_set = process(tacle_path,debug_error)

options=xddOptions.get_opts()


f = open ("Makefile", "w")
f.write(".PHONY:all\n")
f.write("all:")
for bench in test_set:
    f.write((bench[2]+" "))
f.write("\n$(info Starting all)\n");


for bench in test_set:
    #w0 = bench[2] + ": \n\techo \"analyzing " + bench[2] + " \\n\"\n" + "\t- operform -v " + bench[0] + " " + bench[1] + " require:otawa::ipet::FLOW_FACTS_FEATURE require:otawa::ICACHE_ONLY_CONSTRAINT2_FEATURE require:otawa::dcache::CLP_BLOCK_FEATURE require:otawa::dcache::CONSTRAINTS_FEATURE --add-prop otawa::CACHE_CONFIG_PATH=\"../arch/simple_cache.xml\" --add-prop otawa::PROCESSOR_PATH=\"../arch/simple.xml\" --add-prop otawa::dfa::CONST_SECTION=.got 2>" + logPath + bench[2] + "\n"
    w0 = bench[2] + ": \n" + "\t$(info analyzing " + bench[2] + " )\n" + "\t -@ (time -v ../xdd -v  " + bench[0] + " " + bench[1] + options + ") 2>" + logPath + bench[2] + "\n"

    f.write(w0)
f.close()
