#!/usr/bin/python3
import json
import pandas as pd
import tasksJson
import os

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

# Parameters for a complete print of pandas.Dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


class UnknownBenchsType(Exception):
    """
    Exception in case of unknown Type of benchmarks,
    currently support direct (Simple) and Tasks (TASKS.json) modes.
    """
    pass


class BenchmarksJson:
    """
    Represents a Json file recording a benchmarks set,
    currently supports TACLeBench
    """

    def __init__(self, file):
        """
        Construct object using the path to Json description file of benchmarks set
        :param file:  the Json description file
        """
        # load file
        with open(file) as f:
            j = json.load(f)

        # basic infos for the bench set
        self.__name = j['Name']
        self.__base_dir = j['BaseDir']

        # capture the set of groups
        self.__groups = j['Groups']

        # the data
        self.__tab = pd.DataFrame()

        for group_name in self.__groups:

            # Build a local dictionnary, that will be filled for DataFrame
            data = dict()
            data['Bench'] = []
            data['Group'] = []
            data['Status'] = []
            data['ELF'] = []

            # Group Object
            group_object = j[group_name]
            # Get benches with respect to the type of group
            # in case of simple type
            if group_object['Type'] == "Simple":
                # Takes benches directely
                data['Bench'] = group_object["Benches"]
                # ELF path can be determined
                data['ELF'] = [os.path.join(self.__base_dir, group_object['Dir'], b + ".elf") for b in data["Bench"]]
            # in case of using TASKS.json
            elif group_object['Type'] == "Tasks":
                benches = []
                # the task and its ELF is built for every bench (using TasksJson)
                for bench in group_object['Benches']:
                    tasks = tasksJson.TasksJson(
                        os.path.join(self.__base_dir, group_object['Dir'], bench, "TASKS.json"))
                    __benches = tasks.generate_all_benches()
                    __benches = [(b[0], os.path.join(group_object['Dir'], bench, b[1])) for b in __benches]
                    benches = benches + __benches
                data['Bench'] = [b[0] for b in benches]
                data['ELF'] = [os.path.join(self.__base_dir, b[1]) for b in benches]
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

            self.__tab = self.__tab.append(pd.DataFrame(data), ignore_index=True)

    def get_info(self):
        """
        get the complete description of benchmarks as a DataFrame
        :return:  DataFrame
        """
        return self.__tab


if __name__ == "__main__":
    t = BenchmarksJson("samples/TACLe.json")
    print(t.get_info())
