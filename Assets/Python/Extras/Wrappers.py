from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import CvEventInterface

import remote_pdb

# Add addWrappers to CvEventManager.onInit for Hooking.

def addWrappers():

    # Suche nach getPlayer-Aufrufen mit -1/None
    CyGlobalContext.getPlayerBase = CyGlobalContext.getPlayer
    def getPlayer( self, arg0):
        if arg0 is None or int(arg0) < 0:
            # remote_pdb.RemotePdb("192.168.0.21", 4444).set_trace()
            raise Exception()

        return self.getPlayerBase(arg0)

    CyGlobalContext.getPlayer = getPlayer

    # Suche nach Kill von Einheiten per doCommand
    # Auf der Konsole kann der Aufrufstack folgendermaßen ausgegeben werden:
    # import traceback
    # print(traceback.format_stack())
    #
    CyUnit.doCommandBase = CyUnit.doCommand
    def doCommand( self, eCommand, iArg1, iArg2):
        if eCommand == CommandTypes.COMMAND_DELETE:
            if self.getX() == 51 and self.getY() == 44:
                remote_pdb.RemotePdb("192.168.0.21", 4444).set_trace()
                # raise Exception()

        self.doCommandBase(eCommand, iArg1, iArg2)

    # CyUnit.doCommand = doCommand
