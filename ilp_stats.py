import parsetools
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import collections

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



x = list(range(0,len(res)))


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
print(x)
ilp_xdd = [x[1] for x in ilp_xdd]
ilp_max = [x[1] for x in ilp_max]
ilp_exhau = [x[1] for x in ilp_exhau]
print(ilp_xdd)
print(ilp_max)
print(ilp_exhau)

ax = fig.add_subplot(111)

width = 0.3
ax.bar([y-width for y in x],ilp_xdd,label='xdd',width=width)
ax.bar([y for y in x],ilp_max,label='max',width=width)
ax.bar([y+width for y in x],ilp_exhau,label='exhau',width=width)
#ax.bar([y+0.2 for y in x],ilp_max,label='MAX',width=0.5,color='darkgray')

ax.legend()
ax.set_ylabel('number of ilp variables',fontsize=12)
ax.set_xlabel('benchmark',fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels,rotation=80)
#plt.yscale('log')
#plt.ylim(top=15000)

plt.yticks(fontsize=15)
plt.show()



#ax = df.plot.scatter(x='evt',)
