#!/usr/bin/python3
import unittest
from benchDesc import benchmarksJson


class MyTestCase(unittest.TestCase):
    def test_benchJson(self):
        t = benchmarksJson.BenchmarksJson("TACLe.json")
        print(t.get_info())


if __name__ == '__main__':
    unittest.main()
