import parsetools
import matplotlib.pyplot as plt
import matplotlib
import getopt, sys
from benchDesc import benchsDesc

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["arch="])
except getopt.getopterror as err:
    print(err)
    sys.exit(2)

file_postfix = ""
for o,a in opts:
    if o == "--arch":
        if a == "simple":
            file_postfix = file_postfix + "_simple"
        elif a == "complex":
            file_postfix = file_postfix + "_complex"
        else:
            print ("error, the architecture must be either simple or complex")


p = parsetools.AnalysisTimeParser()
res = p.parse_all_files("../log_2020_09/log_xddilp_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
time_xdd = res



p = parsetools.AnalysisTimeParser()
res = p.parse_all_files("../log_2020_09/log_hlts_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
time_hlts = res


p = parsetools.AnalysisTimeParser()
res = p.parse_all_files("../log_2020_09/log_WCETmax_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
time_max = res

p = parsetools.AnalysisTimeParser()
res = p.parse_all_files("../log_2020_09/log_exhaustive_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
time_exhau = res


labels = [pair[0] for pair in time_xdd]
x = list(range(1,len(res)+1))

BIGGER_SIZE = 11
BIGGER_BIGGER_SIZE=15

matplotlib.rc('font', size=BIGGER_SIZE)          # controls default text sizes
matplotlib.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
matplotlib.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
matplotlib.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
matplotlib.rc('legend', fontsize=BIGGER_BIGGER_SIZE)    # legend fontsize
matplotlib.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title



print(time_xdd)
print(time_exhau)
#print(time_max)
time_xdd = [x[1] for x in time_xdd]
time_max = [x[1] for x in time_max]
time_exhau = [x[1] for x in time_exhau]
time_hlts = [x[1] for x in time_hlts]

#speedup
#time_xdd = [x*100/y for x,y in zip(time_exhau,time_xdd)]
#time_max = [x*100/y for x,y in zip(time_exhau,time_max)]
#time_hlts = [x*100/y for x,y in zip(time_exhau,time_hlts)]
#time_exhau = [x/y for x,y in zip(time_exhau,time_exhau)]

fig = plt.figure()
ax = fig.add_subplot(111)
width=0.2
ax.bar([y- 1.5*width for y in x],time_max,label='max',width=width, color ="0.0", edgecolor = 'black')
ax.bar([y- 0.5*width for y in x],time_xdd,label='xdd',width=width, color = "0.4", edgecolor = 'black')
ax.bar([y+ 0.5*width for y in x],time_exhau,label='exhau',width=width, color = "0.84",edgecolor = 'black')
ax.bar([y+ 1.5*width for y in x],time_hlts,label='Etime',width=width, color = "1.0", edgecolor = 'black')

ax.legend()
ax.set_ylabel('analysis time (s)',fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels,rotation=80)
plt.subplots_adjust(bottom=0.17,top=0.75,right=0.999,left=0.042)
plt.yscale('log')
#plt.ylim(top=200)

plt.yticks(fontsize=15)
plt.show()



#ax = df.plot.scatter(x='evt',)
