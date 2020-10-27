#!/usr/bin/python3
import unittest
from benchDesc import tasksJson


class TestTasksJsonDecode(unittest.TestCase):
    def testPapapbenchTasks(self):
        t = tasksJson.TasksJson("TASKS.json")
        print(t.generate_all_benches())
        self.assertEqual("papabench", t.name())


if __name__ == '__main__':
    unittest.main()
