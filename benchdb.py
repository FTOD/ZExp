import json
import sys
import pandas as pd
import os
import colorama
from colorama import Fore, Back, Style
import subprocess
from multiprocessing import Pool
import getopt

colorama.init()


def error_handle(e):
    print(Fore.RED)
    print(e)
    print(Fore.RESET)


class BenchsDB:
    def __init__(self):
        with open('config.json', 'r') as f:
            config_json = json.load(f)
        self.TACLe_root_path = config_json["TACLe_ROOT"]
        self.XDD_root_path = config_json["XDD_ROOT"]
        self.OTAWA_root_path = config_json["OTAWA_ROOT"]
        self.LOG_PATH = config_json["LOG_PATH"]

        self.TACLe_default_subdir = ["kernel", "sequential", "parallel", "app"]
        self.TACLe_default_kernel_benchs = ["insertsort", "fir2dim", "st", "deg2rad", "sha", "filterbank",
                                            "bitonic", "cubic", "cosf", "ludcmp", "bsort", "lms", "countnegative",
                                            "iir", "minver", "prime", "complex_updates", "rad2deg", "fft", "matrix1",
                                            "bitcount", "binarysearch", "md5", "fac",  "isqrt", "jfdctint"]
                                            #+["quicksort", "pm", "recursion"]
        self.TACLe_default_sequential_benchs = ["ndes", "cjpeg_transupp", "cjpeg_wrbmp", "gsm_dec", "adpcm_enc", "epic",
                                                "petrinet", "rijndael_enc", "rijndael_dec",
                                                "statemate",
                                                "anagram", "susan", "g723_enc", "fmref",  "audiobeam",
                                                "dijkstra",
                                                "huff_dec", "h264_dec", "adpcm_dec"]# + ["gsm_enc", "ammunition", "huff_enc", "mpeg2"]
        self.TACLe_default_app_benchs = ["lift", "powerwindow"]
        self.TACLe_default_parallel_benchs = ["DEBIE", "PapaBench", "rosace"]

        self.analysis_cmd = [str(os.path.join(self.XDD_root_path, "xstep/collSemantic_test")),
                             "-v", "--add-prop", "otawa::dfa::CONST_SECTION=.got", "--log", "proc",
                             "--add-prop",
                             "otawa::PROCESSOR_PATH=" + str(os.path.join(self.XDD_root_path, "arch/simple.xml")),
                             "--add-prop",
                             "otawa::CACHE_CONFIG_PATH=" + str(
                                 os.path.join(self.XDD_root_path, "arch/simple_cache.xml")),
                             "--add-prop",
                             "otawa::MEMORY_PATH=" + str(os.path.join(self.XDD_root_path, "arch/simple_mem.xml")),
                             ]

        self.db = None

    def status(self, only_ko=False):
        if only_ko:
            return self.db[self.db["TestStatus"] == "KO"][["BenchName", "TAGs", "TestStatus", "TestInfo"]]
        else:
            return self.db[["BenchName", "TAGs", "TestStatus", "TestInfo"]]

    def init(self):
        if not os.path.isfile("benchsDB.json"):
            print(Fore.GREEN + "creating database" + Fore.RESET)
        else:
            print(Fore.YELLOW + "Warning: overwriting existing database" + Fore.RESET)

        self.db = pd.DataFrame(columns=["BenchName", "TAGs", "TestStatus", "TestInfo", "ExecPath", "EntryPoint"])

        # kernel benchmarks
        for bench in self.TACLe_default_kernel_benchs:
            fullpath = os.path.join(self.TACLe_root_path, "kernel", bench, bench + ".elf")
            if not os.path.isfile(fullpath):
                print(Fore.RED + "Error: file " + Fore.YELLOW + fullpath
                      + Fore.RED + " does not exist" + Fore.RESET)
                exit(-1)
            else:
                new_row = pd.Series({"BenchName": bench, "TAGs": "kernel", "TestStatus": "None",
                                     "TestInfo": "", "ExecPath": fullpath, "EntryPoint": bench + "_main"})
                self.db = pd.concat([self.db, new_row.to_frame().T], ignore_index=True)

        # sequential benchmarks
        for bench in self.TACLe_default_sequential_benchs:
            fullpath = os.path.join(self.TACLe_root_path, "sequential", bench, bench + ".elf")
            if not os.path.isfile(fullpath):
                print(Fore.RED + "Error: file " + Fore.YELLOW + fullpath
                      + Fore.RED + "does not exist" + Fore.RESET)
                exit(-1)
            else:
                new_row = pd.Series({"BenchName": bench, "TAGs": "sequential", "TestStatus": "None",
                                     "TestInfo": "", "ExecPath": fullpath, "EntryPoint": bench + "_main"})
                self.db = pd.concat([self.db, new_row.to_frame().T], ignore_index=True)

        # parallel benchmarks
        for bench in self.TACLe_default_parallel_benchs:
            benchpath = os.path.join(self.TACLe_root_path, "parallel", bench)
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
                    new_bench["BenchName"] = benchname + "-" + task["name"]
                    new_bench["TAGs"] = "parallel"
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
        for bench in self.TACLe_default_app_benchs:
            benchpath = os.path.join(self.TACLe_root_path, "app", bench)
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
                    new_bench["BenchName"] = benchname + "-" + task["name"]
                    new_bench["TAGs"] = "app"
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
        self.save_database()

    def load_database(self):
        if not os.path.isfile("benchsDB.json"):
            print(Fore.RED + "Database not found! Abort" + Fore.RESET)
            exit(-1)
        self.db = pd.read_json("benchsDB.json", orient="records", lines=True)

    def ko_test_status(self, benchname):
        self.db.loc[self.db["BenchName"] == benchname, "TestStatus"] = "KO"

    def save_database(self, file="benchsDB.json"):
        self.db.to_json(file, orient='records', lines=True)

    def is_db_loaded(self):
        if self.db is None:
            print(Fore.RED + "ERROR: database should be loaded before any operation" + Fore.RESET)
            exit(-1)
        else:
            return True

    def select_db(self, tags):
        if "all" in tags:
            return self.db
        else:
            return self.db[self.db["TestStatus"].isin(tags) | self.db["TAGs"].isin(tags)]

    def run(self, log=None, tags=None):
        if log is None:
            log = self.LOG_PATH
        self.is_db_loaded()
        if not os.path.isdir(log):
            os.mkdir(log)
        if "all" in tags:
            filtered_db = self.db
        else:
            filtered_db = self.select_db(tags)
        benchs = [(bn, [exe, ep]) for bn, exe, ep in
                  zip(filtered_db["BenchName"], filtered_db["ExecPath"], filtered_db["EntryPoint"])]
        pool = Pool(3)
        for b in benchs:
            pool.apply_async(self.run_bench, args=[b, log], error_callback=error_handle)
        pool.close()
        pool.join()

    def run_bench(self, bench, log):
        os.environ["LD_LIBRARY_PATH"] = os.path.join(self.OTAWA_root_path, "lib/otawa/otawa")
        print(" ".join(self.analysis_cmd) + " " + " ".join(bench[1]))
        try:
            result = subprocess.run(self.analysis_cmd + bench[1],
                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=300)
        except subprocess.TimeoutExpired:
            result = None

        if result is None:
            print(Fore.RED + bench[0] + " TIMED OUT" + Fore.RESET)
            self.ko_test_status(bench[0])
            self.load_database()
            self.db.loc[self.db["BenchName"] == bench[0], "TestStatus"] = "KO"
            self.db.loc[self.db["BenchName"] == bench[0], "TestInfo"] = "timeout"
            self.save_database()

        else:
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
                self.db.loc[self.db["BenchName"] == bench[0], "TestInfo"] = ""
                self.save_database()
                print(Fore.GREEN + bench[0] + " OK " + Fore.RESET)

        self.save_database()


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r", ["help", "errOnly", "tag="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        args = []
        exit(2)
    if "init" in args:
        db = BenchsDB()
        db.init()
    elif "run" in args:
        db = BenchsDB()
        db.load_database()
        tag = None
        for o, a in opts:
            if o == "--tag":
                tag = [a]
        if tag is None:
            print("You must specify a tag to run, "
                  "this could be benche set name (kernel, sequential, ... ),KO, OK, or all")
            exit(-1)
        db.run(tags=tag)

    elif "status" in args:
        db = BenchsDB()
        db.load_database()
        df = db.status()
        for o, a in opts:
            if o == "--errOnly":
                df = db.status(only_ko=True)
        with pd.option_context('display.max_rows', 100, 'display.max_columns', 20, 'display.expand_frame_repr', False):
            print(df)
