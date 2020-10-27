#!/usr/bin/python3
import unittest
from benchDesc import benchmarksJsonDecode


class MyTestCase(unittest.TestCase):
    def test_benchJson(self):
        t = benchmarksJsonDecode.BenchmarksJson("TACLe.json")
        print(t.get_info())


if __name__ == '__main__':
    unittest.main()
