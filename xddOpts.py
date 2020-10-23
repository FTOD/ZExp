class XddOptions:
    archs = {"complex":"--complex", "simple":"--simple"}
    algos = {'xdd':'--use-xdd', 'etime':'--use-otawa'}
    const_opts = " --add-prop otawa::dfa::CONST_SECTION=.got "

    def __init__(self):
        self.__arch = None
        self.__algo = None
        self.__split_threshold = None

    def set_arch(self,arch):
        if arch in XddOptions.archs:
            self.__arch = arch
        else:
            print("not option ", arch, " for architecture option of XDD, Abort!")
            exit(0)

    def set_algo(self,algo):
        if algo in XddOptions.algos:
            self.__algo = algo
        else:
            print("not option ", algo, " for algorithm option of XDD, Abort!")
            exit(0)

    def set_split_threshold(self, thr):
        if thr > 0 :
            self.__split_threshold = thr
        else:
            print("split threshold should be positive")

    def get_opts(self):
        opt_str = ""
        if self.__arch!=None:
            opt_str = opt_str + " " + XddOptions.archs[self.__arch]
        else:
            print("ERROR !!!!!!!!!!!!!!!! arch not specified")
            exit(0)
        if self.__algo!=None:
            opt_str = opt_str + " " + XddOptions.algos[self.__algo]
        else:
            print("algo not specified")
            exit(0)
        if self.__split_threshold!=None:
            opt_str = opt_str + " --split-threshold=" + str(self.__split_threshold)
        else:
            print("split threshold not specified")
            exit(0)

        opt_str = opt_str + " " + XddOptions.const_opts
        print( "Options : ", opt_str )
        return opt_str



if __name__ == "__main__":
    print("testing XddOptions Mod")
    x = XddOptions()
    x.set_arch("complex")
    x.set_algo("xdd")
    x.set_split_threshold(100)
    print(x.get_opts())
