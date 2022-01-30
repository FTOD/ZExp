#!/usr/bin/python3
import json
import pandas as pd
import os
import colorama
from colorama import Fore, Back, Style
import subprocess
from multiprocessing import Pool

colorama.init()

TACLe_root_path = "/home/blanc/work/tacle-bench/bench"
TACLe_default_subdir = ["kernel", "sequential", "parallel", "app"]
TACLe_default_kernel_benchs = ["insertsort", "fir2dim", "st", "deg2rad", "sha", "recursion", "filterbank",
                               "bitonic", "cubic", "cosf", "ludcmp", "pm", "bsort", "lms", "countnegative",
                               "iir", "minver", "prime", "complex_updates", "rad2deg", "fft", "matrix1",
                               "bitcount", "binarysearch", "md5", "fac", "quicksort", "isqrt", "jfdctint"]
TACLe_default_sequential_benchs = ["ndes", "cjpeg_transupp", "cjpeg_wrbmp", "gsm_dec", "adpcm_enc", "epic", "mpeg2",
                                   "huff_enc", "petrinet", "rijndael_enc", "gsm_enc", "rijndael_dec", "statemate",
                                   "anagram", "susan", "g723_enc", "fmref", "ammunition", "audiobeam", "dijkstra",
                                   "huff_dec", "h264_dec", "adpcm_dec"]
TACLe_default_app_benchs = ["lift", "powerwindow"]
TACLe_default_parallel_benchs = ["DEBIE", "PapaBench", "rosace"]

analysis_cmd = ["/home/blanc/work/XDD/xstep/collSemantic_test", "-v", "--add-prop", "otawa::dfa::CONST_SECTION=.got",
                "--log", "proc",
                "--add-prop", "otawa::PROCESSOR_PATH=/home/blanc/work/XDD/arch/simple.xml",
                "--add-prop", "otawa::CACHE_CONFIG_PATH=/home/blanc/work/XDD/arch/simple_cache.xml",
                "--add-prop", "otawa::MEMORY_PATH=/home/blanc/work/XDD/arch/simple_mem.xml"
                ]


def error_handle(err):
    print(Fore.RED)
    print(err)
    print(Fore.RESET)


class BenchsDB:
    def __init__(self):
        self.db = None

    def init(self):
        if not os.path.isfile("benchsDB.json"):
            print(Fore.GREEN + "creating database" + Fore.RESET)
        else:
            print(Fore.YELLOW + "Warning: overwriting existing database" + Fore.RESET)

        self.db = pd.DataFrame(columns=["BenchName", "TAGs", "TestStatus", "TestInfo", "ExecPath", "EntryPoint"])

        # kernel benchmarks
        for bench in TACLe_default_kernel_benchs:
            fullpath = os.path.join(TACLe_root_path, "kernel", bench, bench + ".elf")
            if not os.path.isfile(fullpath):
                print(Fore.RED + "Error: file " + Fore.YELLOW + fullpath
                      + Fore.RED + " does not exist" + Fore.RESET)
                exit(-1)
            else:
                new_row = pd.Series({"BenchName": bench, "TAGs": ["kernel"], "TestStatus": "None",
                                     "TestInfo": "", "ExecPath": fullpath, "EntryPoint": bench + "_main"})
                self.db = pd.concat([self.db, new_row.to_frame().T], ignore_index=True)

        # sequential benchmarks
        for bench in TACLe_default_sequential_benchs:
            fullpath = os.path.join(TACLe_root_path, "sequential", bench, bench + ".elf")
            if not os.path.isfile(fullpath):
                print(Fore.RED + "Error: file " + Fore.YELLOW + fullpath
                      + Fore.RED + "does not exist" + Fore.RESET)
                exit(-1)
            else:
                new_row = pd.Series({"BenchName": bench, "TAGs": ["sequential"], "TestStatus": "None",
                                     "TestInfo": "", "ExecPath": fullpath + ".elf", "EntryPoint": bench + "_main"})
                self.db = pd.concat([self.db, new_row.to_frame().T], ignore_index=True)

        # parallel benchmarks
        for bench in TACLe_default_parallel_benchs:
            benchpath = os.path.join(TACLe_root_path, "parallel", bench)
            tasks_json_file = os.path.join(benchpath, "TASKS.json")
            if not os.path.isfile(tasks_json_file):
                print(Fore.RED + "Error: Tasks json file note found at "
                      + tasks_json_file + Fore.RESET)
                exit(-1)
            else:
                with open(tasks_json_file) as f:
                    j = json.load(f)
                benchname = j["name"]
                execs = j["execs"]
                for task in j["tasks"]:
                    new_bench = dict()
                    new_bench["BenchName"] = benchname + "/" + task["name"]
                    new_bench["TAGs"] = ["parallel"]
                    new_bench["TestStatus"] = "None"
                    new_bench["TestInfo"] = ""
                    exec_path = [exec1["path"] for exec1 in execs if exec1["name"] == task["exec"]]
                    if len(exec_path) != 1:
                        print(Fore.RED + "Several execs of same name, abort!", Fore.RESET)
                        exit(-1)
                    exec_path = exec_path[0]
                    new_bench["ExecPath"] = os.path.join(benchpath, exec_path)
                    new_bench["EntryPoint"] = task["name"]
                    new_bench = pd.Series(new_bench)
                    self.db = pd.concat([self.db, new_bench.to_frame().T], ignore_index=True)

        # app benchmarks
        for bench in TACLe_default_app_benchs:
            benchpath = os.path.join(TACLe_root_path, "app", bench)
            tasks_json_file = os.path.join(benchpath, "TASKS.json")
            if not os.path.isfile(tasks_json_file):
                print(Fore.RED + "Error: Tasks json file note found at "
                      + tasks_json_file + Fore.RESET)
                exit(-1)
            else:
                with open(tasks_json_file) as f:
                    j = json.load(f)
                benchname = j["name"]
                execs = j["execs"]
                for task in j["tasks"]:
                    new_bench = dict()
                    new_bench["BenchName"] = benchname + "/" + task["name"]
                    new_bench["TAGs"] = ["app"]
                    new_bench["TestStatus"] = "None"
                    new_bench["TestInfo"] = ""
                    exec_path = [exec1["path"] for exec1 in execs if exec1["name"] == task["exec"]]
                    if len(exec_path) != 1:
                        print(Fore.RED + "Several execs of same name, abort!", Fore.RESET)
                        exit(-1)
                    exec_path = exec_path[0]
                    new_bench["ExecPath"] = os.path.join(benchpath, exec_path)
                    new_bench["EntryPoint"] = task["name"]
                    new_bench = pd.Series(new_bench)
                    self.db = pd.concat([self.db, new_bench.to_frame().T], ignore_index=True)
        with pd.option_context('display.max_rows', 100, 'display.max_columns',
                               15):  # more options can be specified also
            print(self.db)
        if not os.path.isfile("benchsDB.json"):
            print(Fore.RED + "Database not found! How did you load it?" + Fore.RESET)
            exit(-1)
        self.save_database()

    def load_database(self):
        if not os.path.isfile("benchsDB.json"):
            print(Fore.RED + "Database not found! Abort" + Fore.RESET)
            exit(-1)
        self.db = pd.read_json("benchsDB.json", orient="records", lines=True)

    def ko_test_status(self, benchname):
        self.db.loc[self.db["BenchName"] == benchname, "TestStatus"] = "KO"

    def save_database(self):
        if not os.path.isfile("benchsDB.json"):
            print(Fore.RED + "Database not found! How did you load it?" + Fore.RESET)
            exit(-1)
        self.db.to_json("benchsDB.json", orient='records', lines=True)

    def is_db_loaded(self):
        if self.db is None:
            print(Fore.RED + "ERROR: database should be loaded before any operation" + Fore.RESET)
            exit(-1)
        else:
            return True

    def run_all(self, log="/tmp/logcaca", tags=None):  # TODO currently ignoring tags
        if tags is None:
            tags = []
        self.is_db_loaded()
        if not os.path.isdir(log):
            os.mkdir(log)
        filtered_db = self.db[self.db["TestStatus"] == "None"]
        benchs = [(bn, [exe, ep]) for bn, exe, ep in
                  zip(filtered_db["BenchName"], filtered_db["ExecPath"], filtered_db["EntryPoint"])]
        pool = Pool(4)
        for b in benchs:
            res = pool.apply_async(self.run_bench, args=[b, log], error_callback=error_handle)
        pool.close()
        pool.join()

    def run_bench(self, bench, log):
        os.environ["LD_LIBRARY_PATH"] = "/home/blanc/otawa/lib/otawa/otawa"
        print(" ".join(analysis_cmd) + " " + " ".join(bench[1]))
        result = subprocess.run(analysis_cmd + bench[1],
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        with open(os.path.join(log, bench[0]), "w") as f:
            f.write(result.stderr.decode("utf-8"))
            f.write(result.stdout.decode("utf-8"))

        if result.returncode != 0:
            print(Fore.RED + bench[0] + " failed with exit code " + str(result.returncode) + Fore.RESET)
            self.ko_test_status(bench[0])
            self.load_database()
            self.db.loc[self.db["BenchName"] == bench[0], "TestStatus"] = "KO"
            self.db.loc[self.db["BenchName"] == bench[0], "TestInfo"] = "Exit Code " + str(result.returncode)
            self.save_database()
        else:
            self.load_database()
            self.db.loc[self.db["BenchName"] == bench[0], "TestStatus"] = "OK"
            self.save_database()
            print(Fore.GREEN + bench[0] + " OK " + Fore.RESET)

        self.save_database()


if __name__ == "__main__":
    db = BenchsDB()
    db.init()
    db.run_all()
