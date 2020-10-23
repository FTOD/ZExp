#!/usr/bin/python3
import subprocess,os

kernel_test = []
basedir = '/home/baiz/Work/tacle-bench/bench/kernel'

def complet_dir (benchname):
    return basedir + '/' + benchname + '/' +  benchname + '.elf'
#get the filename without dir
for filename in os.listdir(basedir):
    kernel_test.append( (filename ,complet_dir(filename))   )

print(kernel_test)

for fp in kernel_test :
    f_out = "/home/baiz/Work/xdd/log/" + fp[0] + ".log"
    with open(f_out,"w+") as fout:
        subprocess.run(["odisasm",fp[1],fp[0]+"_main"],stdout=fout,stderr=fout)

