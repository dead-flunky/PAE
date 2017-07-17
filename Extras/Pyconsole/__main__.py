import sys
import Civ4Shell

port = Civ4Shell.PYCONSOLE_PORT
if len(sys.argv) > 1:
    port = int(sys.argv[1])

if len(sys.argv) > 2:
    host = str(sys.argv[2])
    Civ4Shell.start(port=port, host=host)
else:
    Civ4Shell.start(port=port)
