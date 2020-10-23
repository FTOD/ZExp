import re
import pandas as pd
import argparse
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import numpy as np
import getopt, sys
from scipy.optimize import curve_fit

rx= re.compile(r'BLOCK TIME=(\d+)')
myPath = "../log/"

def usage():
    print("command [-p PATH]" )


def parse_line(line,res):
    match = rx.search(line)
    if match :
        res.append(list(match.groups())[0])


res0 = []
with open(join(myPath,"rijndael_enc_90"),'r') as fp:
    line = fp.readline()
    while line:
        parse_line(line,res0)
        line = fp.readline()


res1 = []
with open(join(myPath,"rijndael_enc_80"),'r') as fp:
    line = fp.readline()
    while line:
        parse_line(line,res1)
        line = fp.readline()

for i in range(0, len(res0)):
    if res0[i]!=res1[i]:
        print(res0[i],res1[i])

exit(1)

def parse_files(path):
    logs_file = [join(myPath,f) for f in listdir(myPath) if isfile(join(myPath,f))]
    log_file = [join(myPath,"rijndael_enc_90"),join(myPath,"rijndael_enc_80")]
    print(logs_file)

    res = []

    #parse all file
    for f in logs_file:
        with open(f,'r') as fp:
            line = fp.readline()
            while line:
                parse_line(line,res)
                line = fp.readline()
    print(res)
    exit(1)
    df = pd.DataFrame(res,columns=['benchname','threshold','wcet'])
    return df



try:
    opts, args = getopt.getopt(sys.argv[1:], "p:", ["help"])
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)




for o,a in opts:
    if o == "-p":
        myPath = a
    elif o in ("-h","--help"):
        usage()
        sys.exit()
    else:
        assert False, "?????"
df = parse_files(myPath)
df = df.sort_values(by='threshold')
_ref_wcet = df[df.threshold==90]
df['precision'] = df.apply(lambda row: row['wcet']/_ref_wcet[_ref_wcet.benchname==row['benchname']].iloc[0]['wcet'] - 1,axis=1)

print(df)

#print (type(_ref_wcet[_ref_wcet.benchname=='statemate'].iloc[0]['wcet']))
#print(df)
#df0 = df[df.benchname == 'statemate']
#df1 = df[df.benchname == 'gsm_dec']
#df2 = df[df.benchname == 'rijndael_enc']
#print(df2)

fig,ax  = plt.subplots()
for key,grp in df.groupby(['benchname']):
    ax = grp.plot(ax=ax, x = 'threshold', y = 'wcet', label=key)
plt.show()


