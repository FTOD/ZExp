import parsetools
from benchDesc import benchsDesc
import matplotlib.pyplot as plt
import matplotlib
import getopt, sys

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["arch="])
except getopt.GetoptError as err:
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
            print ("ERROR, the architecture must be either simple or complex")


p = parsetools.BoundedEventsCountParser()
res = p.parse_all_files("../log_2020_09/log")
res = benchsDesc.regrouping_parallel_res(res)
bounded_count = res
print("BOUNDED=", bounded_count)

p = parsetools.UnboundedEventsCountParser()
res = p.parse_all_files("../log_2020_09/log")
res = benchsDesc.regrouping_parallel_res(res)
unbounded_count = res
print("UNBOUNDED=", unbounded_count)


p = parsetools.WcetResParser()
res = p.parse_all_files("../log_2020_09/log_xddilp_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
wcet_xdd = res
#add a single result
print(res)
print(len(res))

p = parsetools.WcetResParser()
res = p.parse_all_files("../log_2020_09/log_hlts_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
wcet_hlts = res
print(res)
print(len(res))


p = parsetools.WcetResParser()
res = p.parse_all_files("../log_2020_09/log_WCETmax_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
wcet_max = res
print(res)
print(len(res))

p = parsetools.WcetResParser()
res = p.parse_all_files("../log_2020_09/log_exhaustive_15"+file_postfix)
res = benchsDesc.regrouping_parallel_res(res)
wcet_exhau = res
print(res)
print(len(res))

x = list(range(1,len(res)+1))
print(x)
print("=======================================================")


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

#unbound_ratio = [ float(x[1]) / float(x[1]+y[1]) for x,y in zip(unbounded_count,bounded_count)]
unbound_ratio = [( x[0], float(x[1]) / float(x[1]+y[1]) ) for x,y in zip(unbounded_count,bounded_count)]
unbound_ratio.sort(key = lambda i:i[1])

print("***************************")
print(unbound_ratio)
print("***************************")
label_order = [x[0] for x in unbound_ratio]
print(label_order)

unbound_ratio = [x[1] for x in unbound_ratio]

wcet_xdd.sort(key = lambda i: label_order.index(i[0]))
wcet_hlts.sort(key = lambda i: label_order.index(i[0]))
wcet_max.sort(key = lambda i: label_order.index(i[0]))
wcet_exhau.sort(key = lambda i: label_order.index(i[0]))



wcet_xdd = [x[1] for x in wcet_xdd]
wcet_hlts = [x[1] for x in wcet_hlts]
wcet_max = [x[1] for x in wcet_max]
wcet_exhau = [x[1] for x in wcet_exhau]


wcet_xdd = [(y-x)/y for x,y in zip(wcet_xdd,wcet_max)]
wcet_hlts = [(y-x)/y for x,y in zip(wcet_hlts,wcet_max)]
## Rounding, due to imprecision of Etime
wcet_hlts = [ 0.0 if x < 0.0 else x for x in wcet_hlts ]
wcet_exhau = [(y-x)/y for x,y in zip(wcet_exhau,wcet_max)]
print("=======================================================")
print(wcet_xdd)
print(len(res))
print("=======================================================")
print(wcet_exhau)
print(len(res))
print("=======================================================")
print(wcet_hlts)
print(len(res))

ax = fig.add_subplot(111)
width = 0.2
ax.bar([y-width for y in x],wcet_xdd,label='xdd',width=width, color ="1.0" , edgecolor='black')
ax.bar([y for y in x],wcet_exhau,label='exhaustive',width=width, color = "0.7", edgecolor='black')
ax.bar([y+width for y in x],wcet_hlts,label='Etime',width=width, color = "0",edgecolor='black')
#ax.bar([y+0.2 for y in x],wcet_max,label='MAX',width=0.5,color='darkgray')



ax.set_ylabel('WCET / WCET of max partitioning',fontsize=12)
#ax.set_xlabel('benchmark',fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(label_order,rotation=80)
ax.legend(loc='upper left')
#plt.yscale('log')
plt.ylim(top=0.6)

unbound_ratio = [x for x in unbound_ratio]
ax1 = ax.twinx()
ax1.set_ylabel("percentage on unbounded events")
ax1.plot(x,unbound_ratio,'o-',color='black')
plt.subplots_adjust(bottom=0.17,top=0.70,right=0.965,left=0.042)
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



#ax = df.plot.scatter(x='evt',)
