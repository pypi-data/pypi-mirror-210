import logging
import pyclbr
import bisect

mod = None


class ModUtils:
    def __init__(self, mod):
        line2func = []
        try:
            mod = pyclbr.readmodule_ex(mod)
        except Exception:
            print("ltlog internal error!")
            return
        for classname, cls in mod.items():
            if isinstance(cls, pyclbr.Function):
                line2func.append((cls.lineno, "<no-class>", cls.name))
            elif isinstance(cls, pyclbr.Class):
                for methodname, start in cls.methods.items():
                    line2func.append((start, classname, methodname))
            else:
                continue
        self.line2func = line2func
        self.line2func.sort()
        keys = [item[0] for item in self.line2func]
        self.keys = keys

    def line_to_class(self, lineno):
        index = bisect.bisect(self.keys, lineno) - 1
        if index < 0:
            return '<main>'
        return self.line2func[index][1]


class LtLogRecord(logging.LogRecord):
    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func, sinfo):
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)
        self.className = mod.line_to_class(self.lineno)


def getLogger(_mod):
    global mod
    mod = ModUtils(_mod)
    FORMAT = '[%(asctime)-15s] %(levelname)5s %(module)s | %(className)s.%(funcName)s():%(lineno)d -> %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger(_mod)
    logging.setLogRecordFactory(LtLogRecord)
    return logger
