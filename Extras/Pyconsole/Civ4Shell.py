#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Shell to Civ4.
        See Readme for setup information.
"""

import cmd
import sys
import re
import os.path
import socket

if sys.platform[0:3] == "win32":
    import pyreadline as readline
else:
    import readline  # For history, do not remove

from socket import gethostname
from time import sleep

# For reply's
# from threading import Thread

# Constants
# from civ4_api import *

################################################
# Attention, the console is not password protected
# Non-local IPs open your whole system!
################################################

# Default values for connection
PYCONSOLE_PORT = 3333
# PYCONSOLE_HOSTNAME = "0.0.0.0" # Invalid on windows
PYCONSOLE_HOSTNAME = "127.0.0.1"

# MY_HOSTNAME = "0.0.0.0"  # Invalid on windows
MY_HOSTNAME = "127.0.0.1"  # or
# MY_HOSTNAME = gethostname()  # or
# MY_HOSTNAME = "192.168.X.X"

# Makes ANSI escape character sequences (for producing colored terminal
# text and cursor positioning) work under MS Windows.
# Note that colouring does not work in Git bash (Win), but Cmd.exe.
USE_COLORAMA = True

# Storage file for history
PYCONSOLE_HIST_FILE = ".pyconsole.history"

MY_PROMPT = ''
# MY_PROMPT = 'civ4> '
RESULT_LINE_PREFIX = '    '
RESULT_LINE_SPLIT = (160, '  ')

BUFFER_SIZE = 1024
EOF = '\x04'

################################################

if USE_COLORAMA:
    from colorama import init, Fore, Back, Style
    init()
    ColorOut = Fore.BLUE
    ColorWarn = Fore.RED
    ColorReset = Style.RESET_ALL
else:
    ColorOut = ""
    ColorWarn = ""
    ColorReset = ""

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, tAddrPort):
        print("Connect to %s" % str(tAddrPort))
        self.s.connect(tAddrPort)

    def close(self):
        if not self.s is None:
            warn("Close Client")
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.s = None

    def send(self, msg, bRecv=True):
        self.s.send(msg + EOF)
        # self.s.send(EOF)
        ret = ""
        if bRecv:
            recv = self.s.recv(BUFFER_SIZE)
            while len(recv) == BUFFER_SIZE and recv[-1] != EOF:
                sys.stdout.write(recv)
                ret += recv
                recv = self.s.recv(BUFFER_SIZE)

            recv = recv.strip(EOF)
            # sys.stdout.write(recv)
            ret += recv
        return ret

class Civ4Shell(cmd.Cmd):
    intro = """
    Welcome to the Civ4 shell. Type help or ? to list commands.
    Connect to local Civ4 server with 'connect port'.
    Exit shell with 'bye'.
    """

    remote_server_adr = (PYCONSOLE_HOSTNAME, PYCONSOLE_PORT)
    local_server_adr = (MY_HOSTNAME, PYCONSOLE_PORT + 1)

    prompt = ''

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args)
        self.client = None
        self.server = None
        self.bImport_doc = False

        # Overwrite address
        self.remote_server_adr = (
                        kwargs.get("host", self.remote_server_adr[0]),
                        kwargs.get("port", self.remote_server_adr[1]))
        print(kwargs)
        print(self.remote_server_adr)
        # Start client 
        self.init()

    def init(self):
        # Client
        if(self.client is not None):
            self.client.close()
        self.client = Client()
        try:
            self.client.connect(self.remote_server_adr)
        except ValueError:
            warn("Connectiong failed. Invalid port?")

        """
        # Server
            if self.server is not None:
                self.server.stop()
                self.server_thread.join()
            self.server = Server(self.local_server_adr)
            self.server_thread = Thread(target=self.server.start)
            self.server_thread.start()
        """

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    # ----- internal shell commands -----
    def do_connect(self, arg):
        """Connect to Civ4-Instance:                       connect [PORT] [HOSTNAME]

        Default PORT: %i
        Default HOSTNAME: %s
        """
        words = arg.split(' ')
        if len(words) > 1:
            self.remote_server_adr = (str(words[1]), int(words[0]))
        elif len(words) > 0:
            self.remote_server_adr = (self.remote_server_adr[0], int(words[0]))

        self.local_server_adr = (
            self.local_server_adr[0],
            self.remote_server_adr[1] + 1)
        self.init()

    do_connect.__doc__ %= (remote_server_adr[1], remote_server_adr[0])

    def do_bye(self, arg):
        """Close Civ4 shell and exit:          bye
        """
        warn('Quitting Civ4 shell.')
        # self.send("Q:", True)  # Inform server that client quits.
        self.close()
        return True

    def do_test(self, arg):
        """Send test commands to backend."""
        print(" Change amount of gold (Player 0):")
        self.default("gc.getPlayer(0).setGold(100)")

        print(" Number of units (Player 0):")
        self.default("print('Num Units: %i' % gc.getPlayer(0).getNumUnits())")
        print(" Add unit (Player 0):")
        # Attention pydoc.doc(CyPlayer.initUnit)) returns wrong declaration!
        self.default("gc.getPlayer(0).initUnit(1, 1, 1," 
                "UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)")
        self.default("print('Num Units: %i' % gc.getPlayer(0).getNumUnits())")

    def do_doc(self, arg):
        """Fetch pydoc information"""
        if len(arg) > 0:
            d = "pydoc.doc(%s)" % (arg)
        else:
            d = "pydoc.doc(%s)" % ("gc")
        if not self.bImport_doc:
            d = "import pydoc; " + d
            self.bImport_doc = True

        print(d)
        self.default(d)

    def default(self, line):
        """Send input as python command"""
        result = str(self.send("P:"+line))
        if RESULT_LINE_SPLIT is not None:
          result = self.restrict_textwidth(
                  result,
                  RESULT_LINE_SPLIT[0],
                  RESULT_LINE_SPLIT[1])

        result_with_tabs = "%s%s%s%s" % (
            ColorOut,
            RESULT_LINE_PREFIX,
            result.rstrip('\n').replace('\n', '\n' + RESULT_LINE_PREFIX),
            ColorReset)
        print(result_with_tabs)
        # Restore prompt
        sys.stdout.write("%s" % (MY_PROMPT))

    '''
    def do_help(self, args):
        """%s"""
        if args == "":
            cmd.Cmd.do_help(self, args)
            # Apend commands with irregular python function names
            print("Civ4 help")
            print("===========")
            print(self.do_khelp.__doc__)
            print("Further commands")
            print("================")
            print("None\n")
        elif args == "!":
            print("TODO")
        else:
            cmd.Cmd.do_help(self, args)

    do_help.__doc__ %= (cmd.Cmd.do_help.__doc__)

    def do_khelp(self, args):
        """khelp [regex pattern] lists matching library functions/important variables.

        If a more detailed description exists the entry will be
        marked with '*'.
        Patterns with an unique result show the description.
        Note: The lookup table is big, but incomplete.
        """

        kname = args.strip()
        if kname == "":
            kname = ".*"
        kname = "^"+kname+"$"
        bRegexOk = True
        try:
            re_name = re.compile(kname, re.IGNORECASE)
        except:
            bRegexOk = False
            warn("Can not compile regular expression.")
            return

        lElems = []
        if bRegexOk:
            lElems.extend([i for i in CIV4_LIB_FUNCTIONS
                           if re.search(re_name, i["name"])
                           is not None])
            lElems.extend([i for i in CIV4_LIB_CLASSES
                           if re.search(re_name, i["name"])
                           is not None])
            lElems.extend([i for i in CIV4_LIB_OTHER
                           if re.search(re_name, i["name"])
                           is not None])

        l = ["%s%s" % (el["name"],
                       "*" if el["desc"] != "" else "")
             for el in lElems]
        if(len(l) == 0):
            warn("No Civ4 function/class/etc found for %s" % (kname,))
            return
        elif(len(l) > 20):
            print(civ4_library_abc(l))
        elif(len(l) > 1):
            print(" ".join(l))
            return
        else:
            print(civ4_library_help(lElems[0]))
            return
    '''

    def close(self):
        if(self.client is not None):
            self.client.close()
        """
        if self.server is not None:
            self.server.stop()
            self.server_thread.join()
        """    

    def send(self, s, bRecv=True):
        try:
            return self.client.send(s, bRecv)
        except:
            warn("Sending of '%s' failed" % (s,))

        return ""

    def restrict_textwidth(self, text, max_width, prefix):
        """ Fill in extra line breaks if destance between two newline
        characters is to long.
        """
        if len(text) <= max_width:
            return text

        posL = 0
        while len(text) - posL > max_width:
            posR = text.find('\n', posL, posL+max_width)
            if posR == -1:
                text = "%s\n%s%s" % (
                        text[0:posL+max_width],
                        prefix,
                        text[posL+max_width:])
                posL += max_width + 1 + len(prefix) + 1
            else:
                posL = posR+1

        return text

# -----------------------------------------

# Setup tab completion
class Completer:

    def __init__(self, completer=None, shell=None, bBind=True):
        self.prefix = None
        self.shell = shell
        self.completer = \
            self.complete_advanced if completer is None else completer
        if bBind:
            readline.parse_and_bind('tab: complete')
            readline.set_completer(self.complete)

    def complete(self, prefix, index):
        if prefix != self.prefix:
            # New prefix. Find all words that start with this prefix.
            self.matching_words = self.completer(prefix, index)
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

    def complete_simple(self, text, state):
        """Re-uses the lists the vim syntax file."""
        FOOBAR = []
        l = [i for i in FOOBAR if i.startswith(text)]
        l.extend([i for i in FOOBAR if i.startswith(text)])
        return l
        # if(state < len(l)):
        #    return l[state]
        # return None

    def complete_advanced(self, text, state):
        """Old stuff"""
        l = []

        if len(l) == 0:
            l.extend([i["name"] for i in CIV4_LIB_FUNCTIONS
                      if i["name"].startswith(text)])
            l.extend([i["name"] for i in CIV4_LIB_CLASSES
                      if i["name"].startswith(text)])
            l.extend([i["name"] for i in CIV4_LIB_OTHER
                      if i["name"].startswith(text)])

        return l
        # if(state < len(l)):
        #    return l[state]
        # return None


def warn(s):
    print(ColorWarn+s+ColorReset)

try:
    lib_dict
except NameError:
    lib_dict = dict()

CIV4_LIB_FUNCTIONS = []
CIV4_LIB_CLASSES = []
CIV4_LIB_OTHER = []



def start(**kwargs):
    shell = Civ4Shell(**kwargs)
    # completer = Completer(shell=shell)

    # Load history
    try:
        readline.read_history_file(PYCONSOLE_HIST_FILE)
    except IOError:
        warn("Can't read history file")

    # Load help system in background thread
    # doc_thread = Thread(target=load_civ4_library)
    # doc_thread.start()

    # Start Input loop
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        warn("Ctrl+C pressed. Quitting Civ4 shell.")
        shell.close()
    except TypeError:
        warn("Type error. Quitting Civ4 shell.")
        shell.close()
    finally:
        shell.close()

    # Write history
    try:
        readline.set_history_length(100000)
        readline.write_history_file(".pyconsole.history")
    except IOError:
        warn("Can't write history file")

if __name__ == '__main__':
    print("Use 'python Pyconsole [port]' in above folder for start")
    # start()
