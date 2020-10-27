#!/usr/bin/python3
import json
import pandas as pd
import tasksJsonDecode
import os

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


class UnknownBenchsType(Exception):
    pass


class BenchmarksJson:
    def __init__(self, file):
        self._info = set()
        with open(file) as f:
            j = json.load(f)
        self._name = j['Name']
        self._base_dir = j['BaseDir']
        self._groups = j['Groups']

        self._tab = pd.DataFrame()

        for group_name in self._groups:
            # Build a local dictionnary, that will be filled for DataFrame
            data = dict()
            data['Bench'] = []
            data['Group'] = []
            data['Status'] = []
            data['ELF'] = []
            # Group Object
            group_object = j[group_name]
            # Get benches with respect to the type of group
            if group_object['Type'] == "Simple":
                # Takes benches directely
                data['Bench'] = group_object["Benches"]
                # ELF path can be determined
                data['ELF'] = [os.path.join(self._base_dir, group_object['Dir'], b + ".elf") for b in data["Bench"]]

            elif group_object['Type'] == "Tasks":
                benches = []
                for bench in group_object['Benches']:
                    tasks = tasksJsonDecode.TasksJson(
                        os.path.join(self._base_dir, group_object['Dir'], bench, "TASKS.json"))
                    __benches = tasks.generate_all_benches()
                    __benches = [(b[0], os.path.join(group_object['Dir'], bench, b[1])) for b in __benches]
                    benches = benches + __benches
                data['Bench'] = [b[0] for b in benches]
                data['ELF'] = [os.path.join(self._base_dir, b[1]) for b in benches]
            else:
                raise UnknownBenchsType

            # Number of benchmarks in this group
            nb_benches = len(data['Bench'])
            # Group name can be initialized
            data['Group'] = [group_name] * nb_benches

            # Update Status
            for b in data['Bench']:
                if b in group_object["Errors"]:
                    data['Status'].append("Error:" + group_object["Errors"][b])
                elif b in group_object["Infinite"]:
                    data['Status'].append("Infinite:" + group_object["Infinite"][b])
                else:
                    data['Status'].append("OK")

            self._tab = self._tab.append(pd.DataFrame(data), ignore_index=True)

    def generate_all_benches(self):
        return self._tab

    def name(self):
        return self._name


if __name__ == "__main__":
    t = BenchmarksJson("samples/TACLe.json")
    print(t.generate_all_benches())
