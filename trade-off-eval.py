import parsetools
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import collections

#### Get Data ####

p = parsetools.WcetResParser()
res = p.parse_all_files("../log_xddilp_15")
wcet_xdd = res

p = parsetools.WcetResParser()
res = p.parse_all_files("../log_xddilp_50")
wcet_xdd50 = res


p = parsetools.WcetResParser()
res = p.parse_all_files("../log_WCET_MAX")

wcet_max = res

p = parsetools.WcetResParser()
res = p.parse_all_files("../log_exhaustive_15")

wcet_exhau = res

p = parsetools.IlpVarCountParser()
res = p.parse_all_files("../log_xddilp_15")
ilp_xdd = res



labels = [pair[0] for pair in ilp_xdd]

p = parsetools.IlpVarCountParser()
res = p.parse_all_files("../log_WCET_MAX")
ilp_max = res




p = parsetools.IlpVarCountParser()
res = p.parse_all_files("../log_exhaustive_15")
ilp_exhau = res



#### create useful thing for print ####
print(res)
x = list(range(1,len(res)+1))
labels = [pair[0] for pair in wcet_xdd]
print(labels)

wcet_xdd = [x[1] for x in wcet_xdd]
wcet_xdd50 = [x[1] for x in wcet_xdd50]
wcet_max = [x[1] for x in wcet_max]
wcet_exhau = [x[1] for x in wcet_exhau]

ilp_xdd = [x[1] for x in ilp_xdd]
ilp_max = [x[1] for x in ilp_max]
ilp_exhau = [x[1] for x in ilp_exhau]

# gain compared to MAX
wcet_xdd = [1-x/y for x,y in zip(wcet_xdd,wcet_max)]
wcet_xdd50 = [1-x/y for x,y in zip(wcet_xdd50,wcet_max)]
wcet_exhau = [1-x/y for x,y in zip(wcet_exhau,wcet_max)]

ilp_xdd = [x-y+1 for x,y in zip(ilp_xdd,ilp_max)]
ilp_exhau = [x-y+1 for x,y in zip(ilp_exhau,ilp_max)]
print(ilp_xdd)
print(ilp_exhau)

# gain per var augumentation
data_xdd = [improve/ilp_vars for improve,ilp_vars in zip(wcet_xdd,ilp_xdd)]
data_exhau = [improve/ilp_vars for improve,ilp_vars in zip(wcet_exhau,ilp_exhau)]

#### configure plot ####
BIGGER_SIZE = 11
BIGGER_BIGGER_SIZE=15

matplotlib.rc('font', size=BIGGER_SIZE)          # controls default text sizes
matplotlib.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
matplotlib.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
matplotlib.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
matplotlib.rc('legend', fontsize=BIGGER_BIGGER_SIZE)    # legend fontsize
matplotlib.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title



fig = plt.figure()




ax = fig.add_subplot(111)
width = 0.2
ax.bar([y-width for y in x],data_xdd,label='xdd',width=width)
ax.bar([y+width for y in x],data_exhau,label='exhaustive',width=width)

ax.set_ylabel('WCET',fontsize=12)
ax.set_xlabel('bench',fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels,rotation=80)
ax.legend()
#plt.yscale('log')
#plt.ylim(top=15000)

plt.yticks(fontsize=15)
"""
plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=True,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False
        ) # labels along the bottom edge are off
"""
plt.show()


