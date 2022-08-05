import parsetools
from os.path import isfile, join
from os import listdir
import matplotlib.pyplot as plt
import matplotlib

p = parsetools.WcetResParser()
path = "../log2022-07-31-etime"
files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
res = p.parse_all_files(files)
wcet_etime = res
wcet_etime_dict = dict(wcet_etime)
print(wcet_etime)

p = parsetools.WcetResParser()
path = "../log2022-07-31-xdd"
files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
res = p.parse_all_files(files)
wcet_xdd = res
wcet_xdd_dict = dict(wcet_xdd)
print(wcet_xdd)

res = []
for info in wcet_xdd:
    if (info[0] not in wcet_etime_dict) or (wcet_etime_dict[info[0]] is None):
        res.append((info[0], 0))
    elif info[1] is None:
        res.append((info[0], -0.1))
    else:
        time_etime = float(wcet_etime_dict[info[0]])
        time_xdd = float(info[1])
        res.append((info[0],  (time_etime - time_xdd) * 100 / time_etime))
res.sort(key=lambda xx: xx[0])
print(res)

labels = [info[0] for info in res]
labels = [x.replace("papabench", "ppb") for x in labels]
labels = [x.replace("_task", "") for x in labels]
labels = [x.replace("powerwindow-", "") for x in labels]

fig, ax = plt.subplots()
x = list(range(0, len(res)))
ax.bar(x, [y[1] for y in res], width=0.8, edgecolor="white", linewidth=0.7, color="blue")
ax.set_xticks(range(0, len(labels)))
ax.set_xticklabels(labels, rotation=60, ha="right")
ax.set_ylabel(" WCET gain (%)", fontsize=20)
plt.yticks(fontsize=20)
plt.xticks(fontsize=15)
plt.xlim([-1, 69])
plt.subplots_adjust(right=0.999, top=0.8, left=0.045, bottom=0.31, wspace=0.0, hspace=0.0)
print(len(x))
plt.show()
