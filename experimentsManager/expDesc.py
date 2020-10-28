#!/usr/bin/python3
import json
import subprocess
from benchDesc import benchmarks
from multiprocessing import Pool
import os


class Bench:
    def __init__(self, name, cmd, _bin, entry_point):
        self.__name = name
        self.__cmd = cmd
        self.__bin = _bin
        self.__entry_point = entry_point

    def run(self, log=None):
        print(self.__cmd + [self.__bin, self.__entry_point])
        result = subprocess.run(self.__cmd + [self.__bin, self.__entry_point],
                                stderr=subprocess.PIPE)
        if log is not None:
            with open(os.path.join(log, self.__name), "w") as f:
                f.write(result.stderr.decode("utf-8"))
        else:
            print(result.stderr.decode("utf-8"))


def handler(a):
    print(a)


class Experiment:
    def __init__(self):
        self.__name = None
        self.__exec = None
        self.__opts = None
        self.__log_output = None
        self.__benches = None

    def load_exp_from_json(self, file):
        with open(file) as f:
            j = json.load(f)
        self.__name = j['Name']
        self.__exec = j['Exec']
        self.__opts = j['Options']
        self.__log_output = False

        benches = benchmarks.Benchmarks()
        # TODO avoid hard coded path
        benches.load_from_json("../benchDesc/samples/TACLe.json")
        benches = benches.get_ok_benches()
        self.__benches = [Bench(name, [self.__exec] + self.__opts, _bin, entry_point)
                          for (name, _bin, entry_point) in
                          zip(benches['Bench'].to_list(),
                              benches['ELF'].to_list(),
                              benches['EntryPoint'].to_list()
                              )]

    def run_all(self, nb_cores=4):
        self.__benches[0].run()
        with Pool(nb_cores) as pool:
            for b in self.__benches:
                pool.apply_async(b.run, error_callback=handler)


if __name__ == "__main__":
    exp = Experiment()
    exp.load_exp_from_json("samples/XDD_exp.json")
    exp.run_all()
