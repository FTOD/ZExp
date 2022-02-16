import os.path
import re
import parsetools
from benchdb import BenchsDB
import matplotlib.pyplot as plt
import matplotlib
import getopt, sys
import pandas as pd
from parsetools import LineParser, FileParser

test_str = """BB 0001098c:(*000055c3a11bb930)
called by00010a4c
MAX_EFFECT=9 @ 000108d0
EventsNB=12
MaxNBConcreteState=128
AverageAge=5.5
BBEventsCount=3
PipeStateCount=2/2
dsafdsafdas
fasdfasdfasd
fasdfdsa
BB 0001098c:(*000055c3a11bb930)
called by00010a4c
MAX_EFFECT=9 @ 000108d0
EventsNB=12
MaxNBConcreteState=128
AverageAge=5.5
BBEventsCount=3
PipeStateCount=2/2
"""
rx = re.compile(r"BB (\S+):\S+\n"
                r".*\n"
                r"MAX_EFFECT=(\d+).+\n"
                r"EventsNB=(\d+).*\n"
                r"MaxNBConcreteState=(\d+).*\n"
                r"AverageAge=(\d+)\.(\d+)\n"
                r"BBEventsCount=(\d+)\n"
                r"PipeStateCount=(\d+)/\d+"
                )
match = rx.findall(test_str)


# reformat one info, used in EventsStatsParser
def reformat(info):
    max_effect = int(info[1])
    events_count = int(info[2])
    max_concrete_states = int(info[3])
    average_age = float(info[4] + info[5])
    # events in the bb (not all events in the state)
    pipe_states_count = int(info[6])
    return [max_effect, events_count, max_concrete_states, average_age, pipe_states_count]


class EventsStatsParser(FileParser):
    def __init__(self):
        super(EventsStatsParser, self).__init__(re.compile(
            r"Edge \S+->(\S+):.*\n"
            r"MAX_EFFECT=(\d+).+\n"
            r"EventsNB=(\d+).*\n"
            r"MaxNBConcreteState=(\d+).*\n"
            r"AverageAge=(\d+)\.(\d+)\n"
            r"PipeStateCount=(\d+)/\d+"
        ))

    def reformat_res(self):
        # remove the bench name
        self.res = [x[1:] for x in self.res]
        # from list of lists to a list
        self.res = [x for sublist in self.res for x in sublist]
        # reformat each info tuplet
        self.res = [reformat(x) for x in self.res]
        print(self.res)

    def plot(self):
        self.reformat_res()
        print(self.res)
        x = [info[-1] for info in self.res]
        y = [info[2] for info in self.res]
        print(x)
        print(y)

        fig, ax = plt.subplots()

        ax.scatter(x, y)
        ax.set_yscale('log', base=2)
        ax.set(xticks=range(0, 18))

        plt.show()


class EventsAgeDistributionParser(FileParser):
    def __init__(self):
        super(EventsAgeDistributionParser, self).__init__(re.compile(r"(#DIST#\d+:\d+)"))

    def get_count_from_info(self, info):
        return int(info[6:].split(":")[1])

    def rework_bench_res(self):
        res = [0] * 30
        for res_per_bench in self.res:
            res = [a + self.get_count_from_info(b) for a, b in zip(res, res_per_bench[1:])]
        self.res = res

    def plot(self):
        self.rework_bench_res()
        res = self.res
        plt.style.use('_mpl-gallery')
        print(res)

        # make data
        x = list(range(0, 30))
        y = [res[x] for x in range(0, 30)]
        print(x)
        print(y)

        # plot
        fig, ax = plt.subplots()

        ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
        ax.set(xlim=(-1, 30), xticks=range(0, 30), yticks=range(0, 200, 10))

        plt.show()


def plot_events_stats(res):
    total_events = [info[3] for info in res]
    return


if __name__ == "__main__":
    db = BenchsDB()
    db.load_database()
    df = db.select_db(["OK"])
    # with pd.option_context('display.max_rows', 100, 'display.max_columns', 20, 'display.expand_frame_repr', False):
    #    print(df)
    names = df["BenchName"].tolist()
    log_path = db.LOG_PATH
    log_files = [os.path.join(log_path, x) for x in names]

    # debug use
    log_files = ["/tmp/caca", "/tmp/caca"]

    p = EventsStatsParser()
    p.parse_all_files(log_files)
    # p = EventsAgeDistributionParser()
    # p.parse_all_files(log_files)
    p.plot()
