# Scenario PeloponnesianWar

# Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import PyHelpers

# Defines
gc = CyGlobalContext()


def onEndGameTurn(iGameTurn):
    if iGameTurn == 1:
        # Athen (0) soll mit Sparta (1) ewig Krieg fuehren
        gc.getTeam(gc.getPlayer(0).getTeam()).setPermanentWarPeace(gc.getPlayer(1).getTeam(), True)
        # gc.getPlayer(0).AI_setAttitudeExtra(1,-50)
        # gc.getPlayer(1).AI_setAttitudeExtra(0,-50)
        # gc.getTeam(gc.getPlayer(0).getTeam()).setWarWeariness(gc.getPlayer(1).getTeam(),30)
        # gc.getTeam(gc.getPlayer(1).getTeam()).setWarWeariness(gc.getPlayer(0).getTeam(),30)
