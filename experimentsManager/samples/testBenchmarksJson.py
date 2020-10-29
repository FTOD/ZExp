#!/usr/bin/python3
import unittest
from experimentsManager import benchmanager


class MyTestCase(unittest.TestCase):
    def test_benchJson(self):
        t = benchmanager.Benchmarks()
        t.load_from_json("TACLe.json")
        print(t.get_info())
        print(t.get_ok_benches_as_list())


if __name__ == '__main__':
    unittest.main()
