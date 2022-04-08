import os
from os import listdir
from os.path import isfile, join
import re
import parsetools
from benchdb import BenchsDB
import matplotlib.pyplot as plt
import matplotlib
import getopt, sys
import pandas as pd
from parsetools import LineParser, FileParser

# test_str = """
# Edge 00010624->0001078c:
# MAX_EFFECT=-1 @ nullptr
# EventsNB=0
# MaxNBConcreteState=0
# AverageAge=4.5
# PipeStateCount=1/1
# """
# r = re.compile(r"Edge \S+->(\S+):.*\n"
#                r"(?:.*\n)?"
#                r"MAX_EFFECT=(-?\d+).+\n"
#                r"EventsNB=(\d+).*\n"
#                r"(?:MaxGen=\d+.*\n)?"
#                r"MaxNBConcreteState=(\d+).*\n"
#                r"AverageAge=(\d+(?:\.\d+)?)\n"
#                r"PipeStateCount=(\d+)/\d+"
#                )
# find = r.findall(test_str)
# print(find)
# exit(1)


class AnalysisTimeParser(FileParser):
    def __init__(self):
        super(AnalysisTimeParser, self).__init__(re.compile(
            r"ANALYSIS_TIME=(.+)"
        ))

    def convert_auto_time_to_s(self):
        res = []
        for info in self.res:
            ms_format = re.compile(r"(\d+(?:\.\d+)?) ms")
            s_format = re.compile(r"(\d+(?:\.\d+)?) s")
            m_format = re.compile(r"(\d+) m, (\d+(?:\.\d+)?) s")

            time_str = info[1]
            match = ms_format.fullmatch(time_str)
            time = -1
            if match:
                time = float(match.groups()[0]) / 1000.0
            match = s_format.fullmatch(time_str)
            if match:
                time = float(match.groups()[0])
            match = m_format.fullmatch(time_str)
            if match:
                time = int(match.groups()[0]) * 60 + float(match.groups()[1])
            res.append([info[0], time])
        self.res = res

    def plot_analysis_time(self):
        self.convert_auto_time_to_s()
        self.res.sort(key=lambda xx: xx[0])
        x = list(range(0, len(self.res)))
        y = [info[1] for info in self.res]
        fig, ax = plt.subplots()
        labels = [info[0] for info in self.res]
        labels = [x.replace("papabench", "ppb") for x in labels]
        labels = [x.replace("_task", "") for x in labels]
        labels = [x.replace("powerwindow-", "") for x in labels]
        ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
        ax.set_yscale('log', base=10)
        ax.set_xticks(range(0, len(labels)))
        ax.set_xticklabels(labels, rotation=60, ha="right")
        ax.set_ylabel("Analysis Time (s)", fontsize=50)
        plt.yticks(fontsize=50)
        plt.xticks(fontsize=30)
        plt.subplots_adjust(right=0.999, top=0.999, left=0.06, bottom=0.286)
        plt.show()


# reformat one info, used in EventsStatsParser
def reformat(info):
    max_effect = int(info[1])
    events_count = int(info[2])
    max_concrete_states = int(info[3])
    average_age = float(info[4])
    # events in the bb (not all events in the state)
    pipe_states_count = int(info[5])
    return [max_effect, events_count, max_concrete_states, average_age, pipe_states_count]


class AnalysisStatsParser(FileParser):
    def __init__(self):
        super(AnalysisStatsParser, self).__init__(re.compile(
            r"Edge \S+->(\S+):.*\n"
            r"(?:.*\n)?"
            r"MAX_EFFECT=(-?\d+).+\n"
            r"EventsNB=(\d+).*\n"
            r"(?:MaxGen=\d+.*\n)?"
            r"MaxNBConcreteState=(\d+).*\n"
            r"AverageAge=(\d+(?:\.\d+)?)\n"
            r"PipeStateCount=(\d+)/\d+"
        ))

    def reformat_res(self):
        # remove the bench name
        self.res = [x[1:] for x in self.res]
        # from list of lists to a list
        self.res = [x for sublist in self.res for x in sublist]
        # reformat each info tuplet
        self.res = [reformat(x) for x in self.res]

    def plot_concrete_vs_abstract(self):
        self.reformat_res()
        # print(self.res)
        x = [info[-1] for info in self.res]
        y = [info[2] for info in self.res]
        # print(x)
        # print(y)

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_yscale('log', base=2)
        # ax.set(xticks=range(0, 18))

        plt.subplots_adjust(right=0.999, top=0.999)

        plt.show()

    def plot_abs_states(self):
        self.reformat_res()
        stats = dict()
        for info in self.res:
            if info[-1] in stats:
                stats[info[-1]] = stats[info[-1]] + 1
            else:
                stats[info[-1]] = 1
        # print(self.res)
        x = list(stats.keys())
        y = list(stats.values())
        # print(x)
        # print(y)

        fig, ax = plt.subplots()

        ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
        ax.set_yscale('log', base=10)
        ax.set_xlabel("number of states", fontsize=80)
        ax.set_ylabel("number of edges", fontsize=80)
        plt.yticks(fontsize=70)
        plt.xticks(fontsize=70)
        plt.subplots_adjust(right=0.999, top=0.975, left=0.079, bottom=0.095)
        plt.show()



# used in EventsAgeDistributionParser
def get_count_from_info(info):
    return int(info.split(":")[1])


def get_age_from_info(info):
    return int(info.split(":")[0])


class EventsAgeDistributionParser(FileParser):
    def __init__(self):
        super(EventsAgeDistributionParser, self).__init__(re.compile(r"#EXPLICIT:\[\d+,(\d+)\]"))
        self.max_avg_age = 0

    def rework_bench_res(self):
        res = dict()
        for res_per_bench in self.res:
            for age_str in res_per_bench[1:]:
                age = int(age_str)
                if age > 175:
                    print(res_per_bench[0])
                    print(age)
                    continue
                if age in res:
                    res[age] = res[age] + 1
                else:
                    res[age] = 1
        self.res = res

    def plot(self):
        self.rework_bench_res()
        res = self.res
        plt.style.use('_mpl-gallery')
        # print(res)

        # make data
        max_age = max(list(self.res.keys()))
        x = list(range(0, max_age + 2))
        y = [res[x] if x in res else 0 for x in range(0, max_age + 2)]
        max_count = max(list(self.res.values()))
        print(x)
        print(y)

        # plot
        fig, ax = plt.subplots()

        ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
        ax.set_yscale('log', base=10)
        ax.set_ylabel("Number of Events", fontsize=50)
        ax.set_xlabel("Lifetime of Events", fontsize=50)
        plt.yticks(fontsize=50)
        plt.xticks(fontsize=50)
        plt.subplots_adjust(right=0.999, top=0.999, left=0.055, bottom=0.1)

        plt.show()


def plot_events_stats(res):
    total_events = [info[3] for info in res]
    return


if __name__ == "__main__":
    # db = BenchsDB()
    # db.load_database()
    # df = db.select_db(["all"])
    # # with pd.option_context('display.max_rows', 100, 'display.max_columns', 20, 'display.expand_frame_repr', False):
    # #    print(df)
    # names = df["BenchName"].tolist()
    # log_path = db.LOG_PATH
    # log_files = [os.path.join(log_path, x) for x in names]

    log_path = "/home/blanc/log2022-04-06-1"
    log_files = [join(log_path, f) for f in listdir(log_path) if isfile(join(log_path, f))]

    # AnalysisStatsParser
    p = AnalysisStatsParser()
    p.parse_all_files(log_files)
    p.plot_abs_states()

    # # EventsLifeTimeStats
    # p = EventsAgeDistributionParser()
    # p.parse_all_files(log_files)
    # p.plot()

    # AnalysisTimeParser
    # p = AnalysisTimeParser()
    # p.parse_all_files(log_files)
    # p.plot_analysis_time()
