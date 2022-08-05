import re
from os import listdir
from os.path import isfile, join
import ntpath

error_code = 9999999

# parse data that appears once per file, and in several lines
class FileParser:

    def __init__(self, rx, pass_error=True):
        self.__rx = rx
        self.res = None
        self.pass_error = pass_error

    def parse_all_files(self, log_files):
        self.res = []
        # parse all files
        for f in log_files:
            with open(f, 'r') as fp:
                # load the total content once
                content = fp.read()
                match = self.__rx.findall(content)
                if match:
                    info = match
                    info.insert(0, ntpath.basename(f))
                    # add data of one file in the list
                    self.res.append(info)
                else:
                    if self.pass_error:
                        print("error, data not found in", f)
                    else:
                        # use 99999 as error code
                        self.res.append([ntpath.basename(f), error_code])
        return self.res


# Abstract class
class LineParser:

    def update(self, res, info):
        raise NotImplementedError("Should have implemented this")

    def top(self):
        raise NotImplementedError("Should have implemented this")

    def __init__(self, rx):
        self.__rx = rx
        self.res = []

    def test(self, _str):
        match = self.__rx.search(_str)
        if match:
            print("pattern found, info = ", list(match.groups()), ", test OK")
        else:
            print("pattern not found, test failed")

    def parse_line(self, line, res):
        match = self.__rx.search(line)
        if match:
            info = list(match.groups())
            res = self.update(info, res)

        return res

    def parse_all_files(self, files):
        # files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
        # print(files)

        for f in files:
            _res = self.top()
            with open(f, 'r', errors='backslashreplace') as fp:
                line = fp.readline()
                i = 1
                while line:
                    _res = self.parse_line(line, _res)
                    try:
                        line = fp.readline()
                        i = i + 1
                    except UnicodeDecodeError:
                        print("Error reading ", f, "reading ")
                        print("line:", i, "  Abort!!!")
                        exit(-1)
                self.res.append([ntpath.basename(f), _res])

        return self.res

    def get_res(self):
        return self.res


class WcetResParser(LineParser):
    def __init__(self):
        super(WcetResParser, self).__init__(re.compile('WCET = (\d+)'))

    def update(self, info, res):
        return int(info[0])

    def top(self):
        return None


class BBInfoParser(LineParser):
    def __init__(self):
        a = (r'(\S+_\S+)\|(\d+) evts\|(\d+) INBLOCK evts\|(\d+) XG Nodes\|(\d+) final Nodes\|(\d+) final Leafs\|(\d+) '
             r'Manager Nodes\|analysis time = (\d+)')
        super(BBInfoParser, self).__init__(re.compile(a))

    def update(self, info):
        if not info:
            return self.res
        info = info[:1] + [int(x) for x in info[1:]]
        self.res.append(info)
        return self.res

    def top(self):
        return []


class IlpVarCountParser(LineParser):
    def __init__(self):
        super(IlpVarCountParser, self).__init__(re.compile(r'ILP VARS COUNT = (\d+)'))

    def update(self, info):
        return int(info[0])

    def top(self):
        return None


class BoundedEventsCountParser(LineParser):
    def __init__(self):
        super(BoundedEventsCountParser, self).__init__(re.compile(r'BOUNDED IN_BLOCK EVENT: YES'))

    def update(self, info):
        self.res = self.res + 1
        return self.res 

    def top(self):
        return 0


class UnboundedEventsCountParser(LineParser):
    def __init__(self):
        super(UnboundedEventsCountParser, self).__init__(re.compile(r'BOUNDED IN_BLOCK EVENT: NO'))

    def update(self, info):
        return self.res + 1

    def top(self):
        return 0


class AnalysisTimeParser(LineParser):
    def __init__(self):
        super(AnalysisTimeParser, self).__init__(re.compile(r'User time \(seconds\): (\d+\.\d+)'))

    def update(self, info):
        return float(info[0])

    def top(self):
        return 0


class DcacheAnalysisRes(FileParser):
    def __init__(self):
        super(DcacheAnalysisRes, self).__init__(re.compile(
            r'always-hit:\s*(\d+)\s*\((\d+)\..*\).*\s*first-hit:\s*(\d)+\s*\((\d+)\..*\).*\s*first-miss:\s*(\d+)\s*\('
            r'(\d+)\..*\).*\s*always-miss:\s*(\d+)\s*\((\d+)\..*\).*\s*not-classified:\s*(\d+)\s*\(('
            r'\d+)\..*\).*\s*total:\s*(\d+)'))
            


if __name__ == "__main__":
    p = DcacheAnalysisRes()
    print(p.parse_all_files("../log_2020_09/log_exhaustive_15_complex"))
    # p.test("00010544_00010568|4 evts|2 INBLOCK evts|40 XG Nodes|20 final Nodes|9 final Leafs|76 Manager Nodes|analysis time = 0|                 ILP VARS COUNT = 6")
    # print(p.parse_all_files("../log"))
