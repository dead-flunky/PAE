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

from CvUtil import SHOWEXCEPTIONS
# SHOWEXCEPTIONS = 1  # 0: Print into PythonDbg.log, 1: Ingame popup window
CONFIG_REMOTE = {"port": 4444, "host": "127.0.0.1"}

_USE_REMOTE = False
Remote = None
Locs = [None]  # Stack of local dicts
Depth = 0      # Stack depth ( != len(Locs) after return-event )


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
def print_callers_locals(fOut=sys.stdout, loc=None):
    """Print the local variables dict."""

    if not loc:
        return

    s = ""
    for var_name in loc:
        var_value = str(loc[var_name]).replace("\n", "\n\t\t")
        s += "\t%s: %s\n" % (var_name, var_value)

    fOut.write(s)
    fOut.write(linesep)


# Superseeds CvUtil.myExceptHook
def extendedExceptHook(the_type, value, tb):
    lines = traceback.format_exception(the_type, value, tb)
    pre = "---------------------Traceback lines-----------------------\n"
    mid = "---------------------Local variables-----------------------\n"
    trace = "\n".join(lines)
    post = "-----------------------------------------------------------\n"
    if SHOWEXCEPTIONS:
        fOut = sys.stderr
    else:
        fOut = sys.stdout

    fTmp = StringIO.StringIO()
    fTmp.write(pre)
    fTmp.write(trace)
    fTmp.write(mid)
    print_callers_locals(fTmp, Locs[-1])
    fTmp.write(post)

    if _USE_REMOTE:
        fTmp.write("Starting remote console... Connect with "\
                   "'telnet %s %s' or 'nc -C %s %s'\n" % (
                       CONFIG_REMOTE["host"], CONFIG_REMOTE["port"],
                       CONFIG_REMOTE["host"], CONFIG_REMOTE["port"])
                  )

    fOut.write(fTmp.getvalue())
    if hasattr(fOut, "flush"):
        fOut.flush()

    if _USE_REMOTE:
        if not Remote:
            globals()["Remote"] = RemotePdb(CONFIG_REMOTE["host"], CONFIG_REMOTE["port"])

        Remote.set_trace()


def init_extended_debug():
    sys.settrace(traceit)
    sys.excepthook = extendedExceptHook
