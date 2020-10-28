#!/usr/bin/python3
import unittest
from benchDesc import benchmarks


class MyTestCase(unittest.TestCase):
    def test_benchJson(self):
        t = benchmarks.Benchmarks()
        t.load_from_json("TACLe.json")
        print(t.get_info())
        print(t.get_ok_benches_as_list())


if __name__ == '__main__':
    unittest.main()
