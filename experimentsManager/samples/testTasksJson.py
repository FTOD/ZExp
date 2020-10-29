#!/usr/bin/python3
import unittest
from experimentsManager import benchmanager


class TestTasksJsonDecode(unittest.TestCase):
    def testPapapbenchTasks(self):
        t = benchmanager.BenchTasks()
        t.load_from_json("TASKS.json")
        print(t.generate_all_benches())
        self.assertEqual("papabench", t.name())


if __name__ == '__main__':
    unittest.main()
