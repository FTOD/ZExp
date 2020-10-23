import re
import pandas as pd
import argparse
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import getopt, sys
from scipy.optimize import curve_fit


rx = re.compile(r'xdds/000109d8->00010b08\|\d+ evts\|\d+ INBLOCK evts\|\d+ XG Nodes\|(\d+) final Nodes\|(\d+) final Leafs\|(\d+) Manager Nodes\|analysis time = (\d+)')


def parse_line(line,res):
    match = rx.search(line)
    if match :
        info = list(match.groups())
        info = [int(x) for x in info]
        res=res.append(info)
        return True
    else :
        return False



def parse_files():
    logs_file = ["test1","test2","test3","test4","test5","test6"]
    logs_file = [ "/tmp/"+x for x in logs_file ]
    print(logs_file)


    res = []
    #parse all file
    for f in logs_file:
        with open(f,'r') as fp:
            line = fp.readline()
            while line:
                if (parse_line(line,res)):
                    break
                line = fp.readline()
    return res


print(parse_files())

x1 = [1,2,3,4,5,6]

