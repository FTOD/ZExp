#!/usr/bin/python3
import json

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class BenchTasks:
    def __init__(self):
        self.__info = set()
        self.__name = None

    def load_from_json(self, file):
        with open(file) as f:
            j = json.load(f)
        self.__name = j['name']
        tasks = j['tasks']
        execs = j['execs']
        for t in tasks:
            path = None
            for exec in execs:
                if t['exec'] == exec['name']:
                    path = exec['path']
                    break
            if path is None:
                print("Can not find the executable of task ", t['name'])
            self.__info.add((t['name'], path))

    def generate_all_benches(self, exclude=None):
        if exclude is None:
            exclude = {}
        info_excluding_errors = [x for x in self.__info if x[0] not in exclude]
        return info_excluding_errors

    def name(self):
        return self.__name
