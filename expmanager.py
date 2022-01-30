#!/usr/bin/python3
import json
import subprocess
from multiprocessing import Pool
import os
import benchmanager

# Some constant for colored text
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class Bench:
    def __init__(self, name, cmd, _bin, entry_point):
        self.__name = name
        self.__cmd = cmd
        self.__bin = _bin
        self.__entry_point = entry_point

    def run(self, log=None):
        os.environ["LD_LIBRARY_PATH"] = "/home/blanc/otawa/lib/otawa/otawa"
        print(HEADER + OKCYAN + "starting " + self.__entry_point + ENDC)
        print(" ".join(self.__cmd) + " " + self.__bin + " "+ self.__entry_point)
        result = subprocess.run(self.__cmd + [self.__bin, self.__entry_point],
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if log is not None:
            with open(os.path.join(log, self.__name), "w") as f:
                f.write(result.stderr.decode("utf-8"))
                f.write(result.stdout.decode("utf-8"))
        else:
            print(result.stderr.decode("utf-8"))
        if result.returncode != 0:
            print(HEADER + FAIL + self.__entry_point + " failed with exit code " + str(result.returncode))
        else:
            print(HEADER + OKGREEN + self.__entry_point + " finished " + ENDC)


def handler(a):
    print(HEADER + FAIL)
    print(a)


class Experiment:
    def __init__(self):
        self.__name = None
        self.__exec = None
        self.__opts = None
        self.__log_output = None
        self.__benches = None
        self.__basedir = None
        self.__log_path = None
        self.__bench_groups = None

    def load_exp_from_json(self, file):
        with open(file) as f:
            j = json.load(f)
        self.__name = j['Name']
        self.__basedir = j['BaseDir']
        self.__exec = j['Exec']
        self.__exec = os.path.join(self.__basedir, self.__exec)
        self.__opts = j['Options']
        self.__log_path = j['LogPath']
        self.__bench_groups = j["BenchGroups"]

        benches = benchmanager.Benchmarks()
        # TODO avoid hard coded path
        benches.load_from_json("samples/TACLe_tmp.json")
        benches = benches.get_ok_benches()
        self.__benches = [Bench(name, [self.__exec] + self.__opts, _bin, entry_point)
                          for (name, _bin, entry_point) in
                          zip(benches['Bench'].to_list(),
                              benches['ELF'].to_list(),
                              benches['EntryPoint'].to_list()
                              )]

    def prepare_dir(self):
        os.chdir(self.__basedir)
        if not os.path.isdir(self.__log_path):
            os.mkdir(self.__log_path)

    def run_all(self, nb_cores=4):
        self.prepare_dir()
        os.chdir(self.__basedir)
        pool = Pool(nb_cores)
        for b in self.__benches:
            pool.apply_async(b.run, args=[self.__log_path], error_callback=handler)
        pool.close()
        pool.join()


if __name__ == "__main__":
    exp = Experiment()
    exp.load_exp_from_json("samples/XDD_exp.json")
    exp.run_all()
