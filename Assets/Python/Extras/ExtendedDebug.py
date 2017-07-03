#!/usr/bin/env python
# encoding: utf-8

# Helper to for easier debugging of Civ4 Python errors.
#
# Uses remote debugger and/or write current state into
# the Python error logs.

import sys
from os import linesep
import StringIO
import traceback
import inspect
from remote_pdb import RemotePdb

# from CvUtil import SHOWEXCEPTIONS
SHOWEXCEPTIONS = 1
CONFIG_REMOTE = {"port": 4444, "host": "127.0.0.1"}

_USE_REMOTE = False
_USE_LOG = True


Remote = None
Locs = [None]
Depth = 0


class ErrorWrap(StringIO.StringIO):
    def __init__(self, fOut=None, bRemote=_USE_REMOTE, bLog=_USE_LOG):
        # super(ErrorWrap, self).__init__()
        StringIO.StringIO.__init__(self)
        self.fOut = fOut
        self.bRemote = bRemote
        self.bLog = bLog
        self.msg = ""
        self.remote = RemotePdb(CONFIG_REMOTE["host"], CONFIG_REMOTE["port"])

        self.backup = []
        for name in (
            'stderr', 'stdout', 'stdin',
            # '__stderr__', '__stdout__', '__stdin__',
        ):
            self.backup.append((name, getattr(sys, name)))

        sys.stderr = self

    def write(self, msg):
        if self.bLog:
            pass
        if self.bRemote:
            self.remote.set_trace()

    def writelines(self, iterable):
        for i in iterable:
            self.write(str(i) + linesep)



# ====== Trace stuff to save frame stack
def traceit(frame, event, arg):
    print("\t" + event + "\t" + str(frame.f_code.co_name))
    if event == "call":
        if frame.f_code.co_name == "extendedExceptHook":
            # Abort trace in case of exception handling
            sys.settrace(None)
            return

        globals()["Depth"] += 1
        Locs[Depth:] = [frame.f_locals]
    return traceit_2

def traceit_2(frame, event, arg):
    if event == "return":
        globals()["Depth"] -= 1
        # print "Depth:", Depth
        return


# ====== Exception stuff to print out local variables
def print_callers_locals(fout=sys.stdout, loc=None):
    """Print the local variables dict."""

    if not loc:
        return

    s = ""
    for var_name in loc:
        var_value = str(loc[var_name]).replace("\n", "\n\t\t")
        s += "\t%s: %s\n" % (var_name, var_value)

    fout.write(s)
    fout.write(linesep)


# Superseeds CvUtil.myExceptHook
def extendedExceptHook(the_type, value, tb):
    lines = traceback.format_exception(the_type, value, tb)
    pre = "---------------------Traceback lines-----------------------\n"
    mid = "---------------------Local variables-----------------------\n"
    trace = "\n".join(lines)
    post = "-----------------------------------------------------------\n"
    if SHOWEXCEPTIONS:
        fout = sys.stderr
    else:
        fout = sys.stdout

    fout.write(pre)
    fout.write(trace)
    fout.write(mid)
    print_callers_locals(fout, Locs[-1])
    fout.write(post)

    if _USE_REMOTE:
        fout.write("Starting remote console... Connect with "\
                   "'telnet %s %s' or 'nc -C %s %s'\n" % (
                       CONFIG_REMOTE["host"], CONFIG_REMOTE["port"],
                       CONFIG_REMOTE["host"], CONFIG_REMOTE["port"])
                  )
    fout.flush()

    if _USE_REMOTE:
        if not Remote:
            globals()["Remote"] = RemotePdb(CONFIG_REMOTE["host"], CONFIG_REMOTE["port"])

        Remote.set_trace()


def init_extended_debug():
    sys.settrace(traceit)
    sys.excepthook = extendedExceptHook
