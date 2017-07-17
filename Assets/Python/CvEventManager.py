# Sid Meier's Civilization 4
# Copyright Firaxis Games 2006
##
# CvEventManager
# This class is passed an argsList from CvAppInterface.onEvent
# The argsList can contain anything from mouse location to key info
# The EVENTLIST that are being notified can be found
# ---------------------
# Edited by Pie, Austria since 2010

#####################
# ColorTypes()
# 1,3 = schwarz
# 2 = weiss
# 4 = dunkelgrau
# 5,6 = grau
# 7 = rot
# 8 = gruen
# 9 = blau
# 10 = tuerkis
# 11 = gelb
# 12 = lila
# 13 = orange
# 14 = graublau
#####################
# import sys
# import pickle
# import math
# import re
# import itertools  # faster repeating of stuff

from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import CvDebugTools
import PyHelpers
import Popup as PyPopup
import CvCameraControls
import CvTopCivs
import CvAdvisorUtils
# import CvWBPopups
# import CvWorldBuilderScreen
# import CvTechChooser
# import CvScreenEnums

### Starting points part 1 (by The_J) ###
import StartingPointsUtil

# OOS Logging Tool by Gerikes
import OOSLogger

## Platy WorldBuilder ##
import WBCityEditScreen
import WBUnitScreen
import WBPlayerScreen
import WBGameDataScreen
import WBPlotScreen
import CvPlatyBuilderScreen
## Platy WorldBuilder ##

# PAE River Tiles / navigable rivers (Ramk)
import CvRiverUtil
# Trade and cultivation (Pie, Boggy, Flunky)
import PAE_Trade
import PAE_Cultivation
import PAE_Christen
import PAE_Barbaren
import PAE_Mercenaries
import PAE_City
import PAE_Unit
import PAE_Sklaven
import PAE_Vassal
import PAE_Disasters
# rundenbezogene Features
import PAE_Turn_Features
import PAE_Lists as L

# Flunky: Scenario files
import PeloponnesianWar
import PeloponnesianWarKeinpferd
import Schmelz
import FirstPunicWar

""" Flag to enable Civ4 shell (See Extras/Pyconsole).
    Note that the flag will also be used to enable/disable
    other debugging features of Ramkhamhaeng
"""
CIV4_SHELL = True
RAMK_EXTENDED_DEBUG = False
RAMK_WRAP_FUNCTIONS = False
if CIV4_SHELL:
    import Civ4ShellBackend
    civ4Console = Civ4ShellBackend.Server(tcp_port=3333)

if RAMK_EXTENDED_DEBUG:
    # Ramk - Redirect exception handler
    import ExtendedDebug
    ExtendedDebug.init_extended_debug()  # Made game very slow!

gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
PyCity = PyHelpers.PyCity
PyGame = PyHelpers.PyGame

###################################################
class CvEventManager:

    def __init__(self):
        #################### ON EVENT MAP ######################
        # print "EVENTMANAGER INIT"
        # In CvEventManager.__init__:
        if CIV4_SHELL:
            self.glob = globals()
            self.loc = locals()
            civ4Console.init()

        # PAE - Great General Names
        self.GG_UsedNames = []

        # PAE - Show message which player is on turn
        self.bPAE_ShowMessagePlayerTurn = False
        self.iPAE_ShowMessagePlayerHumanID = 0

        # PAE - River tiles
        # The plot tiles require some initialisation at
        # game startup, but the setup fails if it will be
        # done into onLoadGame. Use same solution like
        # FinalFrontier. Comment about this flag/issue in FF:
        # Used when loading, since the order is wonky and trying to update display in onLoad 'splodes

        self.bRiverTiles_NeedUpdate = False
        self.bRiverTiles_WaitOnMainInterface = False
        # PAE - River tiles end

        self.bCtrl = False
        self.bShift = False
        self.bAlt = False
        self.bAllowCheats = False

        # OnEvent Enums
        self.EventLButtonDown = 1
        self.EventLcButtonDblClick = 2
        self.EventRButtonDown = 3
        self.EventBack = 4
        self.EventForward = 5
        self.EventKeyDown = 6
        self.EventKeyUp = 7

        # self.__LOG_MOVEMENT = 1
        # self.__LOG_BUILDING = 1
        # self.__LOG_COMBAT = 1
        # self.__LOG_CONTACT = 1
        # self.__LOG_IMPROVEMENT = 1
        # self.__LOG_CITYLOST = 1
        # self.__LOG_CITYBUILDING = 1
        # self.__LOG_TECH = 1
        # self.__LOG_UNITBUILD = 1
        # self.__LOG_UNITKILLED = 1
        # self.__LOG_UNITLOST = 1
        # self.__LOG_UNITPROMOTED = 1
        # self.__LOG_UNITSELECTED = 1
        # self.__LOG_UNITPILLAGE = 1
        # self.__LOG_GOODYRECEIVED = 1
        # self.__LOG_GREATPERSON = 1
        # self.__LOG_RELIGION = 1
        # self.__LOG_RELIGIONSPREAD = 1
        # self.__LOG_GOLDENAGE = 1
        # self.__LOG_ENDGOLDENAGE = 1
        # self.__LOG_WARPEACE = 1
        # self.__LOG_PUSH_MISSION = 1

        self.__LOG_MOVEMENT = 0
        self.__LOG_BUILDING = 0
        self.__LOG_COMBAT = 0
        self.__LOG_CONTACT = 0
        self.__LOG_IMPROVEMENT = 0
        self.__LOG_CITYLOST = 0
        self.__LOG_CITYBUILDING = 0
        self.__LOG_TECH = 0
        self.__LOG_UNITBUILD = 0
        self.__LOG_UNITKILLED = 0
        self.__LOG_UNITLOST = 0
        self.__LOG_UNITPROMOTED = 0
        self.__LOG_UNITSELECTED = 0
        self.__LOG_UNITPILLAGE = 0
        self.__LOG_GOODYRECEIVED = 0
        self.__LOG_GREATPERSON = 0
        self.__LOG_RELIGION = 0
        self.__LOG_RELIGIONSPREAD = 0
        self.__LOG_GOLDENAGE = 0
        self.__LOG_ENDGOLDENAGE = 0
        self.__LOG_WARPEACE = 0
        self.__LOG_PUSH_MISSION = 0

        # EVENTLIST
        self.EventHandlerMap = {
            'mouseEvent': self.onMouseEvent,
            'kbdEvent': self.onKbdEvent,
            'ModNetMessage': self.onModNetMessage,
            'Init': self.onInit,
            'Update': self.onUpdate,
            'UnInit': self.onUnInit,
            'OnSave': self.onSaveGame,
            'OnPreSave': self.onPreSave,
            'OnLoad': self.onLoadGame,
            'GameStart': self.onGameStart,
            'GameEnd': self.onGameEnd,
            'plotRevealed': self.onPlotRevealed,
            'plotFeatureRemoved': self.onPlotFeatureRemoved,
            'plotPicked': self.onPlotPicked,
            'nukeExplosion': self.onNukeExplosion,
            'gotoPlotSet': self.onGotoPlotSet,
            'BeginGameTurn': self.onBeginGameTurn,
            'EndGameTurn': self.onEndGameTurn,
            'BeginPlayerTurn': self.onBeginPlayerTurn,
            'EndPlayerTurn': self.onEndPlayerTurn,
            'endTurnReady': self.onEndTurnReady,
            'combatResult': self.onCombatResult,
            'combatLogCalc': self.onCombatLogCalc,
            'combatLogHit': self.onCombatLogHit,
            'improvementBuilt': self.onImprovementBuilt,
            'improvementDestroyed': self.onImprovementDestroyed,
            'routeBuilt': self.onRouteBuilt,
            'firstContact': self.onFirstContact,
            'cityBuilt': self.onCityBuilt,
            'cityRazed': self.onCityRazed,
            'cityAcquired': self.onCityAcquired,
            'cityAcquiredAndKept': self.onCityAcquiredAndKept,
            'cityLost': self.onCityLost,
            'cultureExpansion': self.onCultureExpansion,
            'cityGrowth': self.onCityGrowth,
            'cityDoTurn': self.onCityDoTurn,
            'cityBuildingUnit': self.onCityBuildingUnit,
            'cityBuildingBuilding': self.onCityBuildingBuilding,
            'cityRename': self.onCityRename,
            'cityHurry': self.onCityHurry,
            'selectionGroupPushMission': self.onSelectionGroupPushMission,
            'unitMove': self.onUnitMove,
            'unitSetXY': self.onUnitSetXY,
            'unitCreated': self.onUnitCreated,
            'unitBuilt': self.onUnitBuilt,
            'unitKilled': self.onUnitKilled,
            'unitLost': self.onUnitLost,
            'unitPromoted': self.onUnitPromoted,
            'unitSelected': self.onUnitSelected,
            'UnitRename': self.onUnitRename,
            'unitPillage': self.onUnitPillage,
            'unitSpreadReligionAttempt': self.onUnitSpreadReligionAttempt,
            'unitGifted': self.onUnitGifted,
            'unitBuildImprovement': self.onUnitBuildImprovement,
            'goodyReceived': self.onGoodyReceived,
            'greatPersonBorn': self.onGreatPersonBorn,
            'buildingBuilt': self.onBuildingBuilt,
            'projectBuilt': self.onProjectBuilt,
            'techAcquired': self.onTechAcquired,
            'techSelected': self.onTechSelected,
            'religionFounded': self.onReligionFounded,
            'religionSpread': self.onReligionSpread,
            'religionRemove': self.onReligionRemove,
            'corporationFounded': self.onCorporationFounded,
            'corporationSpread': self.onCorporationSpread,
            'corporationRemove': self.onCorporationRemove,
            'goldenAge': self.onGoldenAge,
            'endGoldenAge': self.onEndGoldenAge,
            'chat': self.onChat,
            'victory': self.onVictory,
            'vassalState': self.onVassalState,
            'changeWar': self.onChangeWar,
            'setPlayerAlive': self.onSetPlayerAlive,
            'playerChangeStateReligion': self.onPlayerChangeStateReligion,
            'playerGoldTrade': self.onPlayerGoldTrade,
            'windowActivation': self.onWindowActivation,
            'gameUpdate': self.onGameUpdate,    # sample generic event
        }

        ################## Events List ###############################
        #
        # Dictionary of Events, indexed by EventID (also used at popup context id)
        #   entries have name, beginFunction, applyFunction [, randomization weight...]
        #
        # Normal events first, random events after
        #
        ################## Events List ###############################
        # BTS Original
        # self.Events={
        #  CvUtil.EventEditCityName : ('EditCityName', self.__eventEditCityNameApply, self.__eventEditCityNameBegin),
        #  CvUtil.EventEditCity : ('EditCity', self.__eventEditCityApply, self.__eventEditCityBegin),
        #  CvUtil.EventPlaceObject : ('PlaceObject', self.__eventPlaceObjectApply, self.__eventPlaceObjectBegin),
        #  CvUtil.EventAwardTechsAndGold: ('AwardTechsAndGold', self.__eventAwardTechsAndGoldApply, self.__eventAwardTechsAndGoldBegin),
        #  CvUtil.EventEditUnitName : ('EditUnitName', self.__eventEditUnitNameApply, self.__eventEditUnitNameBegin),
        #  CvUtil.EventWBAllPlotsPopup : ('WBAllPlotsPopup', self.__eventWBAllPlotsPopupApply, self.__eventWBAllPlotsPopupBegin),
        #  CvUtil.EventWBLandmarkPopup : ('WBLandmarkPopup', self.__eventWBLandmarkPopupApply, self.__eventWBLandmarkPopupBegin),
        #  CvUtil.EventWBScriptPopup : ('WBScriptPopup', self.__eventWBScriptPopupApply, self.__eventWBScriptPopupBegin),
        #  CvUtil.EventWBStartYearPopup : ('WBStartYearPopup', self.__eventWBStartYearPopupApply, self.__eventWBStartYearPopupBegin),
        #  CvUtil.EventShowWonder: ('ShowWonder', self.__eventShowWonderApply, self.__eventShowWonderBegin),
        #}
        ## Platy WorldBuilder ##
        self.Events = {
            CvUtil.EventEditCityName: ('EditCityName', self.__eventEditCityNameApply, self.__eventEditCityNameBegin),
            CvUtil.EventPlaceObject: ('PlaceObject', self.__eventPlaceObjectApply, self.__eventPlaceObjectBegin),
            CvUtil.EventAwardTechsAndGold: ('AwardTechsAndGold', self.__eventAwardTechsAndGoldApply, self.__eventAwardTechsAndGoldBegin),
            CvUtil.EventEditUnitName: ('EditUnitName', self.__eventEditUnitNameApply, self.__eventEditUnitNameBegin),
            CvUtil.EventWBLandmarkPopup: ('WBLandmarkPopup', self.__eventWBLandmarkPopupApply, self.__eventWBScriptPopupBegin),
            CvUtil.EventShowWonder: ('ShowWonder', self.__eventShowWonderApply, self.__eventShowWonderBegin),
            1111: ('WBPlayerScript', self.__eventWBPlayerScriptPopupApply, self.__eventWBScriptPopupBegin),
            2222: ('WBCityScript', self.__eventWBCityScriptPopupApply, self.__eventWBScriptPopupBegin),
            3333: ('WBUnitScript', self.__eventWBUnitScriptPopupApply, self.__eventWBScriptPopupBegin),
            4444: ('WBGameScript', self.__eventWBGameScriptPopupApply, self.__eventWBScriptPopupBegin),
            5555: ('WBPlotScript', self.__eventWBPlotScriptPopupApply, self.__eventWBScriptPopupBegin),
        }
        ## Platy WorldBuilder ##

#################### EVENT STARTERS ######################
    def handleEvent(self, argsList):
        'EventMgr entry point'
        # extract the last 6 args in the list, the first arg has already been consumed
        self.origArgsList = argsList  # point to original
        tag = argsList[0]        # event type string
        idx = len(argsList)-6
        self.bDbg, bDummy, self.bAlt, self.bCtrl, self.bShift, self.bAllowCheats = argsList[idx:]
        ret = 0
        if tag in self.EventHandlerMap:
            fxn = self.EventHandlerMap[tag]
            ret = fxn(argsList[1:idx])
        return ret

#################### EVENT APPLY ######################
    def beginEvent(self, context, argsList=-1):
        'Begin Event'
        entry = self.Events[context]
        return entry[2](argsList)

    def applyEvent(self, argsList):
        'Apply the effects of an event '
        context, playerID, netUserData, popupReturn = argsList

        if context == CvUtil.PopupTypeEffectViewer:
            return CvDebugTools.g_CvDebugTools.applyEffectViewer(playerID, netUserData, popupReturn)

        entry = self.Events[context]

        if context not in CvUtil.SilentEvents:
            self.reportEvent(entry, context, (playerID, netUserData, popupReturn))
        return entry[1](playerID, netUserData, popupReturn)   # the apply function

    def reportEvent(self, entry, context, argsList):
        'Report an Event to Events.log '
        if gc.getGame().getActivePlayer() != -1:
            message = "DEBUG Event: %s (%s)" % (entry[0], gc.getActivePlayer().getName())
            CyInterface().addImmediateMessage(message, "")
            CvUtil.pyPrint(message)
        return 0

#################### ON EVENTS ######################
    def onKbdEvent(self, argsList):
        'keypress handler - return 1 if the event was consumed'

        eventType, key, mx, my, px, py = argsList
        # game = gc.getGame()

        if self.bAllowCheats:
            # notify debug tools of input to allow it to override the control
            argsList = (eventType, key, self.bCtrl, self.bShift, self.bAlt, mx, my, px, py, gc.getGame().isNetworkMultiPlayer())
            if CvDebugTools.g_CvDebugTools.notifyInput(argsList):
                return 0

        if eventType == self.EventKeyDown:
            theKey = int(key)

# From FfH-Mod: by Kael 07/05/2008
            if theKey == int(InputTypes.KB_LEFT):
                if self.bCtrl:
                    CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 45.0)
                    return 1
                elif self.bShift:
                    CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 10.0)
                    return 1

            if theKey == int(InputTypes.KB_RIGHT):
                if self.bCtrl:
                    CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 45.0)
                    return 1
                elif self.bShift:
                    CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 10.0)
                    return 1
# From FfH: End

# PAE Spieler am Zug Message aktivieren/deaktvieren: STRG+P / CTRL+P --
            if theKey == int(InputTypes.KB_P):
                if self.bCtrl:
                    if self.bPAE_ShowMessagePlayerTurn:
                        self.bPAE_ShowMessagePlayerTurn = False
                        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN_DEACTIVATED", ("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)
                    else:
                        self.bPAE_ShowMessagePlayerTurn = True
                        self.iPAE_ShowMessagePlayerHumanID = gc.getGame().getActivePlayer()
                        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN_ACTIVATED", ("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)
                    return 1

            CvCameraControls.g_CameraControls.handleInput(theKey)

## AI AutoPlay ##
            if CyGame().getAIAutoPlay():
                if theKey == int(InputTypes.KB_SPACE) or theKey == int(InputTypes.KB_ESCAPE):
                    CyGame().setAIAutoPlay(0)
                    return 1
## AI AutoPlay ##

            if self.bAllowCheats:
                # Shift - T (Debug - No MP)
                if theKey == int(InputTypes.KB_T):
                    if self.bShift:
                        self.beginEvent(CvUtil.EventAwardTechsAndGold)
                        # self.beginEvent(CvUtil.EventCameraControlPopup)
                        return 1

                elif theKey == int(InputTypes.KB_W):
                    if self.bShift and self.bCtrl:
                        self.beginEvent(CvUtil.EventShowWonder)
                        return 1

                # Shift - ] (Debug - currently mouse-overd unit, health += 10
                elif theKey == int(InputTypes.KB_LBRACKET) and self.bShift:
                    unit = CyMap().plot(px, py).getUnit(0)
                    if not unit.isNone():
                        d = min(unit.maxHitPoints()-1, unit.getDamage() + 10)
                        unit.setDamage(d, PlayerTypes.NO_PLAYER)

                # Shift - [ (Debug - currently mouse-overd unit, health -= 10
                elif theKey == int(InputTypes.KB_RBRACKET) and self.bShift:
                    unit = CyMap().plot(px, py).getUnit(0)
                    if not unit.isNone():
                        d = max(0, unit.getDamage() - 10)
                        unit.setDamage(d, PlayerTypes.NO_PLAYER)

                elif theKey == int(InputTypes.KB_F1):
                    if self.bShift and self.bAlt:
                        CyInterface().addImmediateMessage("BEGIN Python file optimization", "")
                        import ResolveConstantFunctions
                        ResolveConstantFunctions.main(True)
                        CyInterface().addImmediateMessage("END Python file optimization", "")
                        return 1
                    elif self.bShift:
                        CvScreensInterface.replayScreen.showScreen(False)
                        return 1
                    # don't return 1 unless you want the input consumed

                elif theKey == int(InputTypes.KB_F2):
                    if self.bShift and self.bAlt:
                        import remote_pdb
                        remote_pdb.RemotePdb("127.0.0.1", 4444).set_trace()
                        return 1
                    elif self.bShift:
                        # import CvDebugInfoScreen
                        CvScreensInterface.showDebugInfoScreen()
                        return 1

                elif theKey == int(InputTypes.KB_F3):
                    if self.bShift:
                        CvScreensInterface.showDanQuayleScreen(())
                        return 1

                elif theKey == int(InputTypes.KB_F4):
                    if self.bShift:
                        CvScreensInterface.showUnVictoryScreen(())
                        return 1

        return 0

    def onModNetMessage(self, argsList):
        'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'

        iData1, iData2, iData3, iData4, iData5 = argsList
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("onModNetMessage: ",iData1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        print("Modder's net message!")
        CvUtil.pyPrint('onModNetMessage')

        # iData1 = iMessageID (!)

        # Inquisitor
        if iData1 == 665:
            pPlot = CyMap().plot(iData2, iData3)
            pCity = pPlot.getPlotCity()
            # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Inquisitor iData4: ",iData4)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_City.doInquisitorPersecution(pCity, pUnit)
        # Horse down
        elif iData1 == 666:
            # pPlot = CyMap().plot(iData2, iData3)
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_Unit.doHorseDown(pUnit)
        # Horse up
        elif iData1 == 667:
            pPlot = CyMap().plot(iData2, iData3)
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_Unit.doHorseUp(pPlot, pUnit)
        # Emigrant
        elif iData1 == 672:
            pPlot = CyMap().plot(iData2, iData3)
            pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_City.doEmigrant(pCity, pUnit)
        # Disband city
        elif iData1 == 673:
            pPlot = CyMap().plot(iData2, iData3)
            pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_City.doDisbandCity(pCity, pUnit, pPlayer)
        # Hunnen
        elif iData1 == 674:
            # iData2 = iPlayer , iData3 = unitID
            gc.getPlayer(iData2).changeGold(-100)
            pUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).getUnit(iData3)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_HUNS_PAID", ()), None, 2, None, ColorTypes(14), 0, 0, False, False)
        # City Revolten
        elif iData1 == 675:
            # iData2 = iPlayer , iData3 = City ID, iData4 = Revolt Turns , iData5 = Button
            # Button 0: 1st Payment: pop * 10 - 5% chance
            # Button 1: 2nd Payment: pop * 5 - 30% chance
            # Button 2: Cancel: 100% revolt
            pPlayer = gc.getPlayer(iData2)
            pCity = pPlayer.getCity(iData3)
            pPlot = pCity.plot()

            if iData5 == 0:
                if pPlayer.getGold() >= pCity.getPopulation() * 10:
                    pPlayer.changeGold(pCity.getPopulation() * (-10))
                    iChance = 1
                else:
                    iChance = 10
            elif iData5 == 1:
                if pPlayer.getGold() >= pCity.getPopulation() * 5:
                    pPlayer.changeGold(pCity.getPopulation() * (-5))
                    iChance = 5
                else:
                    iChance = 10
            else:
                iChance = 10

            iRand = CvUtil.myRandom(10, "675")
            if iRand < iChance:
                if pPlot.getNumUnits() > pCity.getPopulation():
                    iData4 = 2
                PAE_City.doCityRevolt(pCity, iData4)
                CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_1", (pCity.getName(),)), None, 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            else:
                CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_2", (pCity.getName(),)), None, 2, None, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

        # 676 vergeben (Tech - Unit)

        # 677 Goldkarren / Beutegold / Treasure zw 80 und 150
        elif iData1 == 677:
            pPlot = CyMap().plot(iData2, iData3)
            pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            iGold = 50 + CvUtil.myRandom(76, "677")
            pPlayer.changeGold(iGold)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GOLDKARREN_ADD_GOLD", (iGold,)), "AS2D_BUILD_BANK", 2, None, ColorTypes(8), 0, 0, False, False)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Beutegold eingesackt (Zeile 444)",150)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Provinzhauptstadt Statthalter Tribut
        elif iData1 == 678:
            PAE_City.onModNetMessage(argsList)

        elif iData1 in [668, 669, 670, 679, 680, 681, 682, 692, 693, 696]:
            PAE_Sklaven.onModNetMessage(iData1, iData2, iData3, iData4, iData5)

        elif iData1 == 671 or (iData1 >= 682 and iData1 <= 691):
            PAE_Vassal.onModNetMessage(iData1, iData2, iData3, iData4, iData5)

        # Sklave wird verkauft (am Sklavenmarkt)
        elif iData1 == 694:
            PAE_Sklaven.doSell(iData2, iData3)

        # Unit wird verkauft (beim Soeldnerposten) - Sell unit
        elif iData1 == 695:
            # Confirmation?
            # 695, 0, 0, iOwner, iUnitID
            if iData2 == 0:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_CONFIRM_SELL_UNIT", ("",)))
                popupInfo.setData1(iData4)
                popupInfo.setData2(iData5)
                popupInfo.setOnClickedPythonCallback("popupSellUnit")  # EntryPoints/CvScreenInterface und CvGameUtils / 695
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_YES2", ("",)), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_NO2", ("",)), "")
                popupInfo.addPopup(iData4)
            # Confirmed
            # 695, 1, 0, iOwner, iUnitID
            else:
                if iData4 == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer = gc.getPlayer(iData4)
                pUnit = pPlayer.getUnit(iData5)
                iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost() / 2
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")):
                    iCost = iCost / 2
                iGold = CvUtil.myRandom(iCost-4, "695") + 5

                FormationArray = [
                    gc.getInfoTypeForString("PROMOTION_WILDLIFE"),
                    gc.getInfoTypeForString("PROMOTION_LOYALITAT"),
                    gc.getInfoTypeForString("PROMOTION_MERCENARY")
                ]

                # +3 Gold pro Promotion
                iRange = gc.getNumPromotionInfos()
                for j in range(iRange):
                    if "_FORM_" in gc.getPromotionInfo(j).getType():
                        continue
                    if "_RANG_" in gc.getPromotionInfo(j).getType():
                        continue
                    if "_MORAL_" in gc.getPromotionInfo(j).getType():
                        continue
                    if "_TRAIT_" in gc.getPromotionInfo(j).getType():
                        continue
                    if pUnit.isHasPromotion(j) and j not in FormationArray:
                        iGold += 3

                pPlayer.changeGold(iGold)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_UNIT_SOLD", (iGold,)), None, 2, None, ColorTypes(8), 0, 0, False, False)
                pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                pUnit = None

        # Trojanisches Pferd
        # TODO: select which city in range should be affected
        elif iData1 == 697:
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            iX = iData2
            iY = iData3
            iRange = 1
            for x in range(-iRange, iRange+1):
                for y in range(-iRange, iRange+1):
                    loopPlot = plotXY(iX, iY, x, y)
                    if loopPlot is not None and not loopPlot.isNone():
                        if loopPlot.isCity():
                            pCity = loopPlot.getPlotCity()
                            if pCity.getOwner() != pUnit.getOwner():
                                if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
                                    iDamage = pCity.getDefenseModifier(0)
                                    if iDamage > 0:
                                        PAE_Unit.doTrojanHorse(pCity, pUnit)

        # Unit bekommt Edle Ruestung
        elif iData1 == 699:
            #pPlot = CyMap().plot(iData2, iData3)
            #pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            iCost = gc.getUnitInfo(pUnit.getUnitType()).getCombat() * 12
            if iCost < 0:
                iCost *= (-1)
            pPlayer.changeGold(-iCost)
            iPromo = gc.getInfoTypeForString("PROMOTION_EDLE_RUESTUNG")
            pUnit.setHasPromotion(iPromo, True)
            pUnit.finishMoves()
            PAE_Unit.doGoToNextUnit(pUnit)

        # Pillage Road
        elif iData1 == 700:
            pPlot = CyMap().plot(iData2, iData3)
            pPlot.setRouteType(RouteTypes.NO_ROUTE)
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            pUnit.getGroup().setActivityType(-1)  # to reload the map!
            pUnit.finishMoves()
            PAE_Unit.doGoToNextUnit(pUnit)

        # Unit bekommt Wellen-Oil
        elif iData1 == 701:
            #pPlot = CyMap().plot(iData2, iData3)
            #pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost()
            if iCost <= 0:
                iCost = 180
            pPlayer.changeGold(-iCost)
            iPromo = gc.getInfoTypeForString("PROMOTION_OIL_ON_WATER")
            pUnit.setHasPromotion(iPromo, True)
            pUnit.finishMoves()
            PAE_Unit.doGoToNextUnit(pUnit)

# Vasallen Technologie +++++++++++++++++++++++++

        # Vassal Tech
        elif iData1 == 702:
            PAE_Vassal.do702(iData2, iData3, iData4, iData5)
            # 702 , iHegemon (HI) , iVassal, iTech , iTechCost
            # Yes  : iTech und iTechCost = -1 (+1 Beziehung)
            # Money: iTech und iTechCost
            # NO:  : iTech = -1

        # Vassal Tech (HI-HI)
        elif iData1 == 703:
            # 703 , iHegemon (HI) , iVassal (HI), iTech , iTechCost
            # Yes  : iTech und iTechCost
            # NO:  : iTechCost = -1
            PAE_Vassal.do703(iData2, iData3, iData4, iData5)

        # Religionsaustreibung
        elif iData1 == 704:
            # 704, iPlayer, iCity, iButton, iUnit
            PAE_City.doInquisitorPersecution2(iData2, iData3, iData4, -1, iData5)

        # Veteran -> Eliteunit, Bsp: Principes + Hastati Combat4 -> Triarii mit Combat3 - Belobigung
        elif iData1 == 705:
            # iData1,... 705, 0, iNewUnit, iPlayer, iUnitID
            PAE_Unit.doUpgradeVeteran(gc.getPlayer(iData4).getUnit(iData5), iData3, True)

        # Renegade City (Keep or raze) TASK_RAZE / TASK_DISBAND
        elif iData1 == 706:
            # 706 , iWinner , iCityID, iLoser , keep(0) | enslave(1) | raze(2)
            pPlayer = gc.getPlayer(iData2)
            pCity = pPlayer.getCity(iData3)
            if iData5 == 1:
                if pCity is not None:
                    # --- Getting goldkarren / treasure / Beutegold and slaves / Sklaven ------
                    iPop = pCity.getPopulation()
                    if iPop > 2:
                        iNum = int(iPop / 2)
                    else:
                        iNum = 1

                    if iNum > 0:
                        for _ in range(iNum):
                            CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), pCity.plot(), pPlayer)
                            CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.plot(), pPlayer)
                        pCity.setPopulation(iNum)

                    # set city and temple slaves => 0
                    PAE_Sklaven.doEnslaveCity(pCity)

            elif iData5 == 2:
                if pCity is not None:
                    # --- Getting goldkarren / treasure / Beutegold ------
                    iBeute = int(pCity.getPopulation() / 2) + 1
                    # if iBeute > 0: das ist >=1
                    for _ in range(iBeute):
                        CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), pCity.plot(), pPlayer)

                    pPlayer.disband(pCity)

        # Hire or Commission Mercenary Menu
        elif iData1 >= 707 and iData1 <= 717:
            PAE_Mercenaries.onModNetMessage(argsList)

        # Unit FORMATIONS ----------------------
        elif iData1 == 718:
            # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("718 erreicht",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            # iData1,... 705, 0, iFormation, iPlayer, iUnitID
            PAE_Unit.doUnitFormation(gc.getPlayer(iData4).getUnit(iData5), iData3)

        # Promotion Trainer Building (Forest 1, Hills1, ...)
        elif iData1 == 719:
            # 719, iCityID, iBuilding, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pCity = pPlayer.getCity(iData2)
            pUnit = pPlayer.getUnit(iData5)

            pCity.setNumRealBuilding(iData3, 1)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # Legendary unit can become a Great General (Feldherr)
        elif iData1 == 720:
            # 720, 0, 0, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_GREAT_GENERAL"), pUnit.plot(), pPlayer)
            PAE_Unit.doRetireVeteran(pUnit)

        # Elefantenstall
        elif iData1 == 721:
            # 721, iCityID, (1 = Elefantenstall | 2 = Kamellager), iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pCity = pPlayer.getCity(iData2)
            pUnit = pPlayer.getUnit(iData5)

            if iData3 == 1:
                pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE"), 1)
                self.onBuildingBuilt([pCity, gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")])
            elif iData3 == 2:
                pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE"), 1)
                self.onBuildingBuilt([pCity, gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")])
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # Piraten-Feature
        elif iData1 == 722:
            # iData2 = 1: Pirat -> normal
            # iData2 = 2: Normal -> Pirat
            # 722, iData2, 0, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)

            iX = pUnit.getX()
            iY = pUnit.getY()
            bSwitch = True
            iVisible = pUnit.visibilityRange()
            loopPlot = pUnit.plot()
            for i in range(-iVisible, iVisible+1):
                for j in range(-iVisible, iVisible+1):
                    loopPlot = plotXY(iX, iY, i, j)
                    iNumUnits = loopPlot.getNumUnits()
                    if iNumUnits > 0:
                        for k in range(iNumUnits):
                            if iData4 != loopPlot.getUnit(k).getOwner() and loopPlot.getUnit(k).getOwner() != gc.getBARBARIAN_PLAYER():
                                bSwitch = False
                                break
                    if not bSwitch:
                        break
                if not bSwitch:
                    break

            if bSwitch:
                lShips = {
                    gc.getInfoTypeForString("UNIT_KONTERE"): gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),
                    gc.getInfoTypeForString("UNIT_BIREME"): gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),
                    gc.getInfoTypeForString("UNIT_TRIREME"): gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),
                    gc.getInfoTypeForString("UNIT_LIBURNE"): gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"),
                    gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"): gc.getInfoTypeForString("UNIT_KONTERE"),
                    gc.getInfoTypeForString("UNIT_PIRAT_BIREME"): gc.getInfoTypeForString("UNIT_BIREME"),
                    gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"): gc.getInfoTypeForString("UNIT_TRIREME"),
                    gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"): gc.getInfoTypeForString("UNIT_LIBURNE")
                }
                try:
                    # Unload units: geht net weil darin canUnload geprueft wird
                    #pUnit.doCommand(CommandTypes.COMMAND_UNLOAD_ALL, -1, -1 )
                    PAE_Unit.convert(pUnit, lShips[pUnit.getUnitType()], pPlayer)
                except KeyError:
                    pass

            else:
                CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE3", ("",)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(11), loopPlot.getX(), loopPlot.getY(), True, True)

        # iData1 723: EspionageMission Info im TechChooser

        # Veteran -> Reservist
        elif iData1 == 724:
            # 724, iCityID, 0, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pCity = pPlayer.getCity(iData2)
            pUnit = pPlayer.getUnit(iData5)

            pCity.changeFreeSpecialistCount(19, 1)  # SPECIALIST_RESERVIST
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # Reservist -> Veteran
        elif iData1 == 725:
            # iData1, iData2, ... iData5
            # First:  725, iCityID, iPlayer, -1, 0
            # Second: 725, iCityID, iPlayer, iButtonID (Typ), 0
            pPlayer = gc.getPlayer(iData3)
            pCity = pPlayer.getCity(iData2)
            iTeam = pPlayer.getTeam()
            pTeam = gc.getTeam(iTeam)

            iReservists = pCity.getFreeSpecialistCount(19)  # SPECIALIST_RESERVIST

            # Units
            bUnit1 = True
            # bUnit2 = True
            bUnit3 = True
            bUnit4 = True
            eCiv = gc.getCivilizationInfo(pPlayer.getCivilizationType())

            # Unit 1
            iUnit1 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SCHILDTRAEGER"))
            if not pCity.canTrain(iUnit1, 0, 0):
                bUnit1 = False
            # Unit 2
            iUnit2 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
            if not pCity.canTrain(iUnit2, 0, 0):
                # bUnit2 = False
                iUnit2 = gc.getInfoTypeForString("UNIT_ARCHER")
            # Unit 3
            iUnit3 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
            if not pTeam.isHasTech(gc.getUnitInfo(iUnit3).getPrereqAndTech()):
                bUnit3 = False
            # Unit 4
            iUnit4 = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
            if not (pTeam.isHasTech(gc.getUnitInfo(iUnit4).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE"))):
                bUnit4 = False

            # Reservist aufstellen
            if iData4 != -1:
                iUnit = -1
                if iData4 == 0 and bUnit1:
                    iUnit = iUnit1
                elif iData4 == 1:
                    iUnit = iUnit2
                elif iData4 == 2 and bUnit3:
                    iUnit = iUnit3
                elif iData4 == 3 and bUnit4:
                    iUnit = iUnit4

                if iUnit != -1:
                    NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

                    pCity.changeFreeSpecialistCount(19, -1)
                    iReservists -= 1
                    # NewUnit.finishMoves()
                    NewUnit.setImmobileTimer(1)

            # PopUp
            if iReservists > 0:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_RESERVIST_MAIN", (pCity.getName(), iReservists)))
                popupInfo.setData1(iData2)  # CityID
                popupInfo.setData2(iData3)  # iPlayer
                popupInfo.setOnClickedPythonCallback("popupReservists")

                # Button 0: Schildtraeger
                sz = u""
                if not bUnit1:
                    sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE", ())
                szText = gc.getUnitInfo(iUnit1).getDescriptionForm(0) + sz
                popupInfo.addPythonButton(szText, gc.getUnitInfo(iUnit1).getButton())
                # Button 1: Bogenschuetze
                popupInfo.addPythonButton(gc.getUnitInfo(iUnit2).getDescriptionForm(0), gc.getUnitInfo(iUnit2).getButton())
                # Button 2: Hilfstrupp
                sz = u""
                if not bUnit3:
                    sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE", ())
                szText = gc.getUnitInfo(iUnit3).getDescriptionForm(0) + sz
                popupInfo.addPythonButton(szText, gc.getUnitInfo(iUnit3).getButton())
                # Button 3: Berittener Hilfstrupp
                sz = u""
                if not bUnit4:
                    sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE", ())
                szText = gc.getUnitInfo(iUnit4).getDescriptionForm(0) + sz
                popupInfo.addPythonButton(szText, gc.getUnitInfo(iUnit4).getButton())

                # Cancel button
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
                popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
                popupInfo.addPopup(iData3)

# Alte Bonusverbreitung UNIT_SUPPLY_FOOD (Obsolete)
##    if iData1 == 726:  frei

        # Getreidelieferung UNIT_SUPPLY_FOOD
        elif iData1 == 727:
            # 727, iCityID, 0, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pCity = pPlayer.getCity(iData2)
            pUnit = pPlayer.getUnit(iData5)

            pCity.changeFood(50)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # Karte zeichnen
        if iData1 == 728:
            # 728, iPage/iButtonId, -1, iPlayer, iUnitID
            iPlayer = iData4
            pPlayer = gc.getPlayer(iPlayer)

            # First Page
            if iData2 == -1:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN", ("", )))
                popupInfo.setOnClickedPythonCallback("popupKartenzeichnungen")
                popupInfo.setData1(iData4)  # iPlayer
                popupInfo.setData2(iData5)  # iUnitID

                # Kosten / Erfolgschance / Trait-Bonus

                # Gebirge: 100 G/30% TRAIT_ORGANIZED oder TRAIT_PROTECTIVE
                txtBonus = ""
                iChance = 30
                iGold = 100
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_ORGANIZED")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_1", (iGold, iChance))+txtBonus, ",Art/Interface/Buttons/BaseTerrain/Peak.dds,Art/Interface/Buttons/BaseTerrain_TerrainFeatures_Atlas.dds,7,1")

                # Weltwunderstaedte: 200 G/50% TRAIT_CREATIVE oder TRAIT_INDUSTRIOUS
                txtBonus = ""
                iChance = 50
                iGold = 200
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_INDUSTRIOUS")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_2", (iGold, iChance))+txtBonus, ",Art/Interface/Buttons/Buildings/PoliceStation.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,1,5")

                # Hafenstaedte: 300 G/50% TRAIT_MARITIME
                txtBonus = ""
                iChance = 50
                iGold = 300
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_MARITIME")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_3", (iGold, iChance))+txtBonus, ",Art/Interface/Buttons/Builds/BuildCityRuins.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,3,10")

                # Grosse Handelsstaedte: 400 [ICON_GOLD]/70% (Bonus) TRAIT_FINANCIAL
                txtBonus = ""
                iChance = 70
                iGold = 400
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_FINANCIAL")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_4", (iGold, iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_metropole.dds")

                # Metropolen: 600 G/90% TRAIT_EXPANSIVE
                txtBonus = ""
                iChance = 90
                iGold = 600
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EXPANSIVE")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_5", (iGold, iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_metropole.dds")

                # Provinzen (ab Pop 10): 800 G/90% TRAIT_IMPERIALIST
                txtBonus = ""
                iChance = 90
                iGold = 800
                if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_IMPERIALIST")):
                    iGold = int(iGold * .75)
                    txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS", ("", ))
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_6", (iGold, iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_provinz.dds")

                # Staedte (ab Pop 6): 1000 G/90%
                txtBonus = ""
                iChance = 90
                iGold = 1000
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_7", (iGold, iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_stadt.dds")

                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
                popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
                popupInfo.addPopup(iPlayer)

            else:

                bRemoveUnit = False
                iTeam = pPlayer.getTeam()
                MapH = CyMap().getGridHeight()
                MapW = CyMap().getGridWidth()

                # Gebirge: 100 G/30% TRAIT_ORGANIZED oder TRAIT_PROTECTIVE
                if iData2 == 0:
                    iChance = 30
                    iGold = 100
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_ORGANIZED")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        pPlayer.changeGold(-iGold)
                        bRemoveUnit = True
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isPeak():
                                        bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Weltwunderstaedte: 200 G/50% TRAIT_CREATIVE oder TRAIT_INDUSTRIOUS
                elif iData2 == 1:
                    iChance = 50
                    iGold = 200
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_INDUSTRIOUS")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_2"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.getNumWorldWonders() > 0:
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Hafenstaedte: 300 G/50% TRAIT_MARITIME
                elif iData2 == 2:
                    iChance = 50
                    iGold = 300
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_MARITIME")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_3"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.isCoastal(5):
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Grosse Handelsstaedte (Traderoutes > 5): 400 [ICON_GOLD]/70% (Bonus) TRAIT_FINANCIAL
                elif iData2 == 3:
                    iChance = 70
                    iGold = 400
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_FINANCIAL")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_4"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.getTradeRoutes() > 5:
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Metropolen: 600 G/90% TRAIT_EXPANSIVE
                elif iData2 == 4:
                    iChance = 90
                    iGold = 600
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EXPANSIVE")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_5"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_METROPOLE")):
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Provinzen (ab Pop 10): 800 G/90% TRAIT_IMPERIALIST
                elif iData2 == 5:
                    iChance = 90
                    iGold = 800
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_IMPERIALIST")):
                        iGold = int(iGold * .75)
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_6"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.getPopulation() > 9:
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Staedte (ab Pop 6): 1000 G/90%
                elif iData2 == 6:
                    iChance = 90
                    iGold = 1000
                    if pPlayer.getGold() < iGold:
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                    else:
                        bRemoveUnit = True
                        pPlayer.changeGold(-iGold)
                        if iPlayer == gc.getGame().getActivePlayer():
                            CyAudioGame().Play2DSound("AS2D_COINS")
                        if iChance >= CvUtil.myRandom(100, "728_7"):
                            for i in range(MapW):
                                for j in range(MapH):
                                    pPlot = CyMap().plot(i, j)
                                    bShow = False
                                    if pPlot.isCity():
                                        pCity = pPlot.getPlotCity()
                                        if pCity.getPopulation() > 5:
                                            bShow = True
                                    # Show plot
                                    if bShow:
                                        pPlot.setRevealed(iTeam, 1, 0, -1)
                        else:
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED", ("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

                # Scout entfernen
                if bRemoveUnit:
                    pUnit = pPlayer.getUnit(iData5)
                    pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pUnit = None

        # Sklaven -> Bibliothek / Library
        elif iData1 == 729:
            pPlot = CyMap().plot(iData2, iData3)
            pCity = pPlot.getPlotCity()
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            PAE_Sklaven.doSlave2Library(pCity, pUnit)

        # Release slaves
        elif iData1 == 730:
            # 730, iCityID, 0, iPlayer, -1/iButton
            pPlayer = gc.getPlayer(iData4)
            pCity = pPlayer.getCity(iData2)
            PAE_Sklaven.doReleaseSlaves(pPlayer, pCity, iData5)

        # Spread religion with a missionary
        elif iData1 == 731:
            # 731, -1, -1, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            iReligion = -1

            # Religion herausfinden
            # pUnit.canSpread (PLOT, iReligion, bool) => geht leider nur in Zusammenhang mit einem PLOT!
            # also wenn die Einheit schon in der Stadt steht, die aber erst gesucht werden muss!
            # Flunky: was ist hiermit?
            # for iReligion in range(gc.getNumReligionInfos()):
            # if gc.getUnitInfo(pUnit.getUnitType()).getReligionSpreads(iReligion): break

            if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_CELTIC_MISSIONARY"):
                iReligion = 0
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY"):
                iReligion = 1
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PHOEN_MISSIONARY"):
                iReligion = 2
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY"):
                iReligion = 3
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_ROME_MISSIONARY"):
                iReligion = 4
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_ZORO_MISSIONARY"):
                iReligion = 5
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY"):
                iReligion = 6
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SUMER_MISSIONARY"):
                iReligion = 7
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_HINDU_MISSIONARY"):
                iReligion = 8
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_BUDDHIST_MISSIONARY"):
                iReligion = 9
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_JEWISH_MISSIONARY"):
                iReligion = 10
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY"):
                iReligion = 11
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_MISSIONARY_JAINISMUS"):
                iReligion = 12

            if iReligion != -1:
                bCanSpread = False
                iNumCities = pPlayer.getNumCities()
                for i in range(iNumCities):
                    pCity = pPlayer.getCity(i)
                    if not pCity.isNone():
                        if not pCity.isHasReligion(iReligion):
                            pUnit.getGroup().pushMoveToMission(pCity.getX(), pCity.getY())
                            pUnit.getGroup().pushMission(MissionTypes.MISSION_SPREAD, iReligion, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
                            bCanSpread = True

                if not bCanSpread:
                    CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SPREAD_RELIGION_NEG", (gc.getReligionInfo(iReligion).getDescription(), "")), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Build Limes PopUp
        elif iData1 == 733:
            # 733, -1 oder iButtonID, -1, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)

            lBuildInfos = [
                gc.getInfoTypeForString("BUILD_LIMES1"),
                gc.getInfoTypeForString("BUILD_LIMES2"),
                gc.getInfoTypeForString("BUILD_LIMES3"),
                gc.getInfoTypeForString("BUILD_LIMES4"),
                gc.getInfoTypeForString("BUILD_LIMES5"),
                gc.getInfoTypeForString("BUILD_LIMES6"),
                gc.getInfoTypeForString("BUILD_LIMES7"),
                gc.getInfoTypeForString("BUILD_LIMES8"),
                gc.getInfoTypeForString("BUILD_LIMES9"),
            ]
            lImpInfos = [
                gc.getInfoTypeForString("IMPROVEMENT_LIMES1"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES2"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES3"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES4"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES5"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES6"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES7"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES8"),
                gc.getInfoTypeForString("IMPROVEMENT_LIMES9")
            ]
            if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_DEFENCES_2")):
                lBuildInfos.extend([
                    gc.getInfoTypeForString("BUILD_LIMES2_1"),
                    gc.getInfoTypeForString("BUILD_LIMES2_2"),
                    gc.getInfoTypeForString("BUILD_LIMES2_3"),
                    gc.getInfoTypeForString("BUILD_LIMES2_4"),
                    gc.getInfoTypeForString("BUILD_LIMES2_5"),
                    gc.getInfoTypeForString("BUILD_LIMES2_6"),
                    gc.getInfoTypeForString("BUILD_LIMES2_7"),
                    gc.getInfoTypeForString("BUILD_LIMES2_8"),
                    gc.getInfoTypeForString("BUILD_LIMES2_9")
                ])
                lImpInfos.extend([
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_1"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_2"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_3"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_4"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_5"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_6"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_7"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_8"),
                    gc.getInfoTypeForString("IMPROVEMENT_LIMES2_9")
                ])

            # PopUp
            if iData2 == -1:

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setOnClickedPythonCallback("popupBuildLimes")
                popupInfo.setData1(iData4)  # iPlayer
                popupInfo.setData2(iData5)  # iUnitID
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_BUILDLIMES_1", ("", )))

                j = 0
                for i in lBuildInfos:
                    pBuildInfo = gc.getBuildInfo(i)
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_BUILDLIMES_2", (pBuildInfo.getDescription(), pBuildInfo.getCost(), gc.getImprovementInfo(lImpInfos[j]).getDefenseModifier())), pBuildInfo.getButton())
                    j += 1

                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
                popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
                popupInfo.addPopup(iData4)

            # Build improvement
            else:
                pBuildInfo = gc.getBuildInfo(lBuildInfos[iData2])
                if pPlayer.getGold() >= pBuildInfo.getCost():
                    pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"), False)
                    pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"), False)
                    pUnit.getGroup().popMission()
                    pUnit.getGroup().pushMission(MissionTypes.MISSION_BUILD, lBuildInfos[iData2], 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)

        # Sklaven zu Feldsklaven oder Bergwerksklaven (HI only)
        elif iData1 == 734:
            # 731, iCityID, Typ: 1=Feld 2=Bergwerk, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            pCity = pPlayer.getCity(iData2)
            # Feldsklaven
            if iData3 == 1:
                pCity.changeFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD"), 1)
            # Bergwerksklave
            else:
                pCity.changeFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD"), 1)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # Salae oder Dezimierung
        elif iData1 == 735:
            # 735, Typ: 1=Sold 2=Dezimierung, 0=PopUp oder 1=Anwenden,  iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)

            # Sold
            if iData2 == 1:
                # +x Gold pro Promotion
                FormationArray = [
                    gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"),
                    gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"),
                    gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"),
                    gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"),
                    gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"),
                    gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"),
                    gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"),
                    gc.getInfoTypeForString("PROMOTION_FORM_KEIL"),
                    gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"),
                    gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"),
                    gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"),
                    gc.getInfoTypeForString("PROMOTION_FORM_GASSE"),
                    gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"),
                    gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"),
                    gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"),
                    gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"),
                    gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"),
                    gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"),
                    gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"),
                    gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG"),
                    gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"),
                    gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"),
                    gc.getInfoTypeForString("PROMOTION_WILDLIFE"),
                    gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE"),
                    gc.getInfoTypeForString("PROMOTION_TRAIT_MARITIME"),
                    gc.getInfoTypeForString("PROMOTION_LOYALITAT"),
                    gc.getInfoTypeForString("PROMOTION_MERCENARY")
                ]
                iGold = 0
                iRange = gc.getNumPromotionInfos()
                for j in range(iRange):
                    if pUnit.isHasPromotion(j) and j not in FormationArray:
                        iGold += 5

                iGold += pUnit.baseCombatStr() * 4

                if pPlayer.hasBonus(gc.getInfoTypeForString("BONUS_SALT")):
                    iGold -= iGold / 4

                # PopUp Beschreibung und Auswahl
                if iData3 == 0:
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_ACTION_SALAE_2", (iGold,)))
                    popupInfo.setData1(iData4)
                    popupInfo.setData2(iData5)
                    popupInfo.setData3(1)
                    popupInfo.setOnClickedPythonCallback("popupActionSalaeDecimatio")  # EntryPoints/CvScreenInterface und CvGameUtils / 735
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_SALAE_YES", ("",)), "")
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_SALAE_NO", ("",)), "")
                    popupInfo.addPopup(iData4)

                # Anwenden
                else:
                    pPlayer.changeGold(-iGold)

                    # Erfolgreich
                    if CvUtil.myRandom(2, "735") == 0:
                        # Promo herausfinden
                        iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
                        if not pUnit.isHasPromotion(iPromo):
                            iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG5")
                            if not pUnit.isHasPromotion(iPromo):
                                iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG4")
                                if not pUnit.isHasPromotion(iPromo):
                                    iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG3")
                                    if not pUnit.isHasPromotion(iPromo):
                                        iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG2")
                                        if not pUnit.isHasPromotion(iPromo):
                                            iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG1")
                        pUnit.setHasPromotion(iPromo, False)
                        CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_SALAE_POS", (gc.getPromotionInfo(iPromo).getDescription(),)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_salae.dds", ColorTypes(8), pUnit.getX(), pUnit.getY(), True, True)

                    # Keine Auswirkung
                    else:
                        CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_SALAE_NEG", ("",)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_salae.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)

                    pUnit.finishMoves()
                    PAE_Unit.doGoToNextUnit(pUnit)

            # Dezimierung
            elif iData2 == 2:
                # PopUp Beschreibung und Auswahl
                if iData3 == 0:
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_2", ("",)))
                    popupInfo.setData1(iData4)
                    popupInfo.setData2(iData5)
                    popupInfo.setData3(2)
                    popupInfo.setOnClickedPythonCallback("popupActionSalaeDecimatio")  # EntryPoints/CvScreenInterface und CvGameUtils / 735
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_YES", ("",)), "")
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_NO", ("",)), "")
                    popupInfo.addPopup(iData4)

                # Anwenden
                else:

                    iRand = CvUtil.myRandom(10, "Dezimierung")

                    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")):
                        iChance = 1  # entspricht 10%
                    else:
                        iChance = 0

                    # Einheit wird barbarisch
                    if iRand < iChance:

                                # Einen guenstigen Plot suchen
                        rebelPlotArray = []
                        reservePlotArray = []
                        iRange = 1
                        iX = pCity.getX()
                        iY = pCity.getY()
                        for i in range(-iRange, iRange+1):
                            for j in range(-iRange, iRange+1):
                                loopPlot = plotXY(iX, iY, i, j)
                                if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                                    if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                                        rebelPlotArray.append(loopPlot)
                                    if loopPlot.getOwner() == iPlayer and not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()):
                                        reservePlotArray.append(loopPlot)

                        if not rebelPlotArray:
                            rebelPlotArray = reservePlotArray

                        if rebelPlotArray:
                            iPlot = CvUtil.myRandom(len(rebelPlotArray), "rebelPlotArray")
                            pPlot = rebelPlotArray[iPlot]
                            NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(pUnit.getUnitType(), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                            iRange = gc.getNumPromotionInfos()
                            for j in range(iRange):
                                if pUnit.isHasPromotion(j):
                                    NewUnit.setHasPromotion(j, True)

                            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG5"), False)
                            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"), False)
                            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"), False)
                            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"), False)
                            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG1"), False)

                            CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_BARBAR", ("",)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_dezimierung.dds", ColorTypes(7), NewUnit.getX(), NewUnit.getY(), True, True)
                            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                            pUnit = None
                        else:
                            CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_OUT", ("",)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_dezimierung.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
                            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                            pUnit = None

                    # Decimatio ist erfolgreich
                    elif iRand < iChance+5:
                        # Unit verletzen
                        pUnit.changeDamage(10, False)

                        lBadPromo = [
                            gc.getInfoTypeForString("PROMOTION_MERCENARY"),
                            gc.getInfoTypeForString("PROMOTION_MORAL_NEG5"),
                            gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"),
                            gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"),
                            gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"),
                            gc.getInfoTypeForString("PROMOTION_MORAL_NEG1")
                        ]

                        lGoodPromo = [
                            gc.getInfoTypeForString("PROMOTION_COMBAT6"),
                            gc.getInfoTypeForString("PROMOTION_COMBAT5"),
                            gc.getInfoTypeForString("PROMOTION_COMBAT4"),
                            gc.getInfoTypeForString("PROMOTION_COMBAT3")
                        ]

                        # Promo herausfinden
                        for iPromo in lBadPromo:
                            if pUnit.isHasPromotion(iPromo):
                                pUnit.setHasPromotion(iPromo, False)
                                break

                        # Rang verlieren
                        for iPromo in lGoodPromo:
                            if pUnit.isHasPromotion(iPromo):
                                pUnit.setHasPromotion(iPromo, False)
                                break

                        CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_POS", (gc.getPromotionInfo(iPromo).getDescription(),)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_dezimierung.dds", ColorTypes(8), pUnit.getX(), pUnit.getY(), True, True)
                        pUnit.finishMoves()
                        PAE_Unit.doGoToNextUnit(pUnit)

                    # Keine Auswirkung
                    else:
                        CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_NEG", ("",)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_action_dezimierung.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
                        pUnit.finishMoves()
                        PAE_Unit.doGoToNextUnit(pUnit)

        # Handelsposten errichten
        elif iData1 == 736:
            # 736, 0, 0, iPlayer, iUnitID
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            PAE_Unit.doBuildHandelsposten(pUnit)

        # Statthalter / Tribut
        elif iData1 == 737:
            PAE_City.onModNetMessage(argsList)

        # 738-743: Cultivation feature / Bonusverbreitung ( Cultivation / Trade / Boggy )
        # 744-748: Automated trade routes

        #~ # 738: Create popup for bonus cultivation
        #~ if iData1 == 738:
            #~ pPlayer = gc.getPlayer(iData2)
            #~ pUnit = pPlayer.getUnit(iData3)
            #~ # iData4 = int von iIsCity
            #~ PAE_Cultivation.doPopupChooseBonusForCultivation(pUnit, iData4)

        # 738, iPlayer, iUnit, iIsCity
        # Cultivate bonus.
        if iData1 == 738:
            pPlayer = gc.getPlayer(iData2)
            pUnit = pPlayer.getUnit(iData3)
            eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
            if eBonus != -1:
                pPlot = pUnit.plot()
                if pPlot.isCity():
                    pPlot = PAE_Cultivation.getCityCultivationPlot(pPlot.getPlotCity(), eBonus)
                PAE_Cultivation.doCultivateBonus(pPlot, pUnit, eBonus)

        # Collect bonus from plot
        elif iData1 == 739:
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            if iData2 == -1:
                # Kaufen
                if iData3 == 1:
                    PAE_Cultivation.doPopupChooseBonus4Cultivation(pUnit)
                # Collect
                elif iData3 == 0:
                    PAE_Cultivation.doCollectBonus4Cultivation(pUnit)
            # im Popup ausgewaehlt, iData2 = BonusType
            else:
                PAE_Cultivation.doBuyBonus4Cultivation(pUnit, iData2)

        # Create popup for buying bonus (in city)
        elif iData1 == 740:
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            pCity = CyMap().plot(iData2, iData3).getPlotCity()
            PAE_Trade.doPopupChooseBonus(pUnit, pCity)

        # Sell bonus (in city)
        elif iData1 == 741:
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            pCity = CyMap().plot(iData2, iData3).getPlotCity()
            PAE_Trade.doSellBonus(pUnit, pCity)
            PAE_Unit.doGoToNextUnit(pUnit)

        # Buy bonus (in city). Called by CvScreensInterface.
        elif iData1 == 742:
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            eBonus = iData2
            iCityOwner = iData3
            PAE_Trade.doBuyBonus(pUnit, eBonus, iCityOwner)

        # Automated trade route: first popup (choose civ 1)
        elif iData1 == 744:
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            # Falls Erstellung der Route zwischendurch abgebrochen wird, kann eine halbfertige Route im
            # ScriptData gespeichert sein - daher wird die Route zunaechst auf inaktiv gesetzt und erst
            # am Ende des Vorgangs aktiviert
            CvUtil.addScriptData(pUnit, "autA", 0)
            # Next step: choose civ
            PAE_Trade.doPopupAutomatedTradeRoute(pUnit, 1, -1, -1)

        # Automated trade route: after choosing city 1
        elif iData1 == 745:
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            pCity = gc.getPlayer(iData2).getCity(iData3)
            CvUtil.addScriptData(pUnit, "autX1", pCity.getX())
            CvUtil.addScriptData(pUnit, "autY1", pCity.getY())
            # Next step: Choose bonus 1 => civ 2 => city 2 => bonus 2
            PAE_Trade.doPopupAutomatedTradeRoute(pUnit, 3, iData2, iData3)

        # Automated trade route: after choosing city 2
        elif iData1 == 746:
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            pCity = gc.getPlayer(iData2).getCity(iData3)
            CvUtil.addScriptData(pUnit, "autX2", pCity.getX())
            CvUtil.addScriptData(pUnit, "autY2", pCity.getY())
            # Next step: Choose bonus 2
            PAE_Trade.doPopupAutomatedTradeRoute(pUnit, 6, iData2, iData3)

        # Automated trade route: after choosing bonus
        elif iData1 == 747:
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            eBonus = iData2
            bFirst = iData3
            if bFirst:
                CvUtil.addScriptData(pUnit, "autB1", eBonus)
                # Next step: choose civ 2 => city 2 => bonus 2
                PAE_Trade.doPopupAutomatedTradeRoute(pUnit, 4, -1, -1)
            else:
                CvUtil.addScriptData(pUnit, "autB2", eBonus)
                # Start trade route
                CvUtil.addScriptData(pUnit, "autA", 1)
                PAE_Trade.doAutomateMerchant(pUnit, False)
                # Falls Haendler in Stadt zieht und noch Fortbewegung hat, soll direkt ge-/verkauft werden
                # if pUnit.canMove():
                #    PAE_Trade.doAutomateMerchant(pUnit, False)

        elif iData1 == 748:
            pUnit = gc.getPlayer(iData4).getUnit(iData5)
            CvUtil.addScriptData(pUnit, "autA", 0)
            PAE_Unit.doGoToNextUnit(pUnit)

        # --------------------------------
        # 749: Allgemeine Infos zu Buttons
        # 750: Unit Ehtnic Info
        # --------------------------------

        # 751: Unit Rang Promo / Upgrade to new unit with new additional PAE ranking system
        elif iData1 == 751:
                # iData1, iData2, ... , iData5
                # 751, -1, -1, iPlayer, iUnitID
            PAE_Unit.doUpgradeRang(iData4, iData5)

        # 752: bless units
        elif iData1 == 752:
            # iData1, iData2, ... , iData5
            # 752, iX, iY, iPlayer, iUnitID
            PAE_Unit.doBlessUnits(iData2, iData3, iData4)

        # Slave -> Latifundium
        elif iData1 == 753:
            # 733, -1 oder iButtonID, -1, iPlayer, iUnitID
            pPlayer = gc.getPlayer(iData4)
            pUnit = pPlayer.getUnit(iData5)
            pPlot = pUnit.plot()
            pPlot.changeUpgradeProgress(10)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None

        # 754: Obsolete Unit text in Tech Screen


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def onInit(self, argsList):
        'Called when Civ starts up'
        CvUtil.pyPrint('OnInit')
        if RAMK_WRAP_FUNCTIONS:
            import Wrappers
            Wrappers.addWrappers()

    def onUpdate(self, argsList):
        'Called every frame'
        fDeltaTime = argsList[0]

        # allow camera to be updated
        CvCameraControls.g_CameraControls.onUpdate(fDeltaTime)

        # PAE - River tiles
        if self.bRiverTiles_NeedUpdate:
            self.bRiverTiles_NeedUpdate = False
            CvRiverUtil.initRiverTiles(False)
            CvRiverUtil.addGoldNearbyRiverTiles()
        # PAE - River tiles end

    def onWindowActivation(self, argsList):
        'Called when the game window activates or deactivates'
        bActive = argsList[0]

    def onUnInit(self, argsList):
        'Called when Civ shuts down'
        CvUtil.pyPrint('OnUnInit')

    def onPreSave(self, argsList):
        "called before a game is actually saved"
        CvUtil.pyPrint('OnPreSave')

    def onSaveGame(self, argsList):
        "return the string to be saved - Must be a string"
        return ""

    def onLoadGame(self, argsList):

        # +++++ PAE Debug: disband/delete things to check CtD reasons)
        # self.onGameStartAndKickSomeAss()

        # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
        gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), False)

        # PAE - River tiles
        self.bRiverTiles_WaitOnMainInterface = True

        # PAE_Lists needs to be initialised
        L.init()
        # PAE_Trade needs to be initialised
        PAE_Trade.init()
        PAE_Cultivation.init()

        PAE_Christen.init()

        # ---------------- Schmelzen 2/4 (BoggyB) --------
        # Beim Neuladen (Felder aus 3/4 bleiben nicht gespeichert)
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName == "SchmelzEuro" or sScenarioName == "SchmelzWelt":
            Schmelz.onLoadGame(sScenarioName)

        # --------- BTS --------
        CvAdvisorUtils.resetNoLiberateCities()
        return 0

    # +++++ PAE Debug: disband/delete things (for different reasons: CtD or OOS)
    def onGameStartAndKickSomeAss(self):
        pass
        """
        iRange = gc.getMAX_PLAYERS()
        for iPlayer in range(iRange):
            pPlayer = gc.getPlayer(iPlayer)
            if pPlayer is not None and not pPlayer.isNone() and pPlayer.isAlive():
                if pPlayer.isBarbarian():
                    # Units
                    # if not pPlayer.isHuman():
                    lUnits = PyPlayer(pPlayer.getID()).getUnitList()
                    for pUnit in lUnits:
                        if pUnit is not None and not pUnit.isNone():
                            eUnitType = pUnit.getUnitType()
                            if (eUnitType == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT")
                                    or eUnitType == gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN")
                                    or eUnitType == gc.getInfoTypeForString("UNIT_EMIGRANT")
                                    or eUnitType == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")):
                                pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                                pUnit = None
                # City buildings
                #iNumCities = pPlayer.getNumCities()
                #for iCity in range (iNumCities):
                #  pCity = pPlayer.getCity(iCity)
                #  if not pCity.isNone():
                #    iRange2 = gc.getNumBuildingInfos()
                #    for iBuilding in range (iRange2):
                #        pCity.setNumRealBuilding(iBuilding,0)
        """
        """
        # Remove a certain improvement from all plots
        for i in xrange(CyMap().numPlots()):
            loopPlot = CyMap().plotByIndex(i)
            if loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_MINE"):
                loopPlot.setImprovementType(-1)
        """

    def onGameStart(self, argsList):
        'Called at the start of the game'

        # +++++ PAE Debug: disband/delete things to check CtD reasons)
        # self.onGameStartAndKickSomeAss()

        # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
        gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), False)

        # PAE - River tiles
        self.bRiverTiles_WaitOnMainInterface = True

        # PAE_Lists needs to be initialised
        L.init()
        # PAE_Trade needs to be initialised
        PAE_Trade.init()
        PAE_Cultivation.init()

        PAE_Christen.init()

        ### Starting points part 2 ###
        MapName = CyMap().getMapScriptName()
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START) and gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR"):
            MapName = ""
            bPlaceCivs = True
            bPlaceBarbs = True
            # PAE Maps
            if sScenarioName == "EuropeStandard":
                MapName = "StartingPoints_EuropeStandard.xml"
            elif sScenarioName == "EuropeMini":
                MapName = "StartingPoints_EuropeMini.xml"
            elif sScenarioName == "EuropeMedium":
                MapName = "StartingPoints_EuropeMedium.xml"
            elif sScenarioName == "EuropeLarge":
                MapName = "StartingPoints_EuropeLarge.xml"
            elif sScenarioName == "EuropeSmall":
                MapName = "StartingPoints_EuropeSmall.xml"
            elif sScenarioName == "SchmelzEuro":
                MapName = "StartingPoints_EuropeLarge.xml"
            elif sScenarioName == "EuropeXL":
                MapName = "StartingPoints_EuropeXL.xml"
            elif sScenarioName == "Eurasia":
                MapName = "StartingPoints_Eurasia.xml"
            # elif sScenarioName == "EasternMed":
            #    MapName = "StartingPoints_EasternMed.xml"
            #    bPlaceCivs = False
            # iRange = gc.getMAX_PLAYERS()
            # for iPlayer in range(iRange):
            # player = gc.getPlayer(iPlayer)
            # if player.isAlive() and player.isHuman():
              # CyInterface().addMessage(iPlayer,False,15,"Loaded map name "+MapName,'',0,'Art/Interface/Buttons/General/warning_popup.dds',ColorTypes(gc.getInfoTypeForString("COLOR_RED")), 1, 1, True,True)
            if MapName != "":
                Debugging = False
                AddPositionsToMap = False
                MyFile = open("Mods/PieAncientEuropeV/Assets/XML/Misc/" + MapName)
                StartingPointsUtil.ReadMyFile(MyFile, Debugging, AddPositionsToMap, bPlaceCivs, bPlaceBarbs)
                MyFile.close()
        # --------------------------------

        # +++++ Special dawn of man texts for Szenario Maps in PAE in CvDawnOfMan.py ++++++++++++++++++++++++++++++++
        # if (gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR") and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
        iEra = gc.getGame().getStartEra()
        lTechs = [
            gc.getInfoTypeForString("TECH_NONE"),
            gc.getInfoTypeForString("TECH_TECH_INFO_1"),
            gc.getInfoTypeForString("TECH_TECH_INFO_2"),
            gc.getInfoTypeForString("TECH_TECH_INFO_4"),
            gc.getInfoTypeForString("TECH_TECH_INFO_5"),
            gc.getInfoTypeForString("TECH_TECH_INFO_6"),
            gc.getInfoTypeForString("TECH_TECH_INFO_7"),
            gc.getInfoTypeForString("TECH_TECH_INFO_8"),
            gc.getInfoTypeForString("TECH_TECH_INFO_9"),
            gc.getInfoTypeForString("TECH_TECH_INFO_10"),
        ]
        lTechsReli = [
            gc.getInfoTypeForString("TECH_RELIGION_NORDIC"),
            gc.getInfoTypeForString("TECH_RELIGION_CELTIC"),
            gc.getInfoTypeForString("TECH_RELIGION_HINDU"),
            gc.getInfoTypeForString("TECH_RELIGION_EGYPT"),
            gc.getInfoTypeForString("TECH_RELIGION_SUMER"),
            gc.getInfoTypeForString("TECH_RELIGION_GREEK"),
            gc.getInfoTypeForString("TECH_RELIGION_PHOEN"),
            gc.getInfoTypeForString("TECH_RELIGION_ROME"),
            gc.getInfoTypeForString("TECH_DUALISMUS"),
            gc.getInfoTypeForString("TECH_MONOTHEISM"),
            gc.getInfoTypeForString("TECH_ASKESE"),
            gc.getInfoTypeForString("TECH_MEDITATION"),
        ]
        iTechRome = gc.getInfoTypeForString("TECH_ROMAN")
        iTechGreek = gc.getInfoTypeForString("TECH_GREEK")
        lCivsRome = [
            gc.getInfoTypeForString("CIVILIZATION_ROME"),
            gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"),
        ]
        lCivsGreek = [
            gc.getInfoTypeForString("CIVILIZATION_GREECE"),
            gc.getInfoTypeForString("CIVILIZATION_ATHENS"),
            gc.getInfoTypeForString("CIVILIZATION_SPARTA"),
            gc.getInfoTypeForString("CIVILIZATION_THEBAI"),
            gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"),
        ]

        # +++++ Corrections in scenarios ++++++++++++++++++++++++++++++++
        iRange = gc.getMAX_PLAYERS()
        for iPlayer in range(iRange):
            player = gc.getPlayer(iPlayer)
            if player.isAlive():
                # Flunky: (unit, pIter) statt for range
                # +++++ Correct naming for units (not available in BTS)
                (unit, pIter) = player.firstUnit(False)
                while unit:
                    UnitText = unit.getName()
                    if UnitText[:7] == "TXT_KEY":
                        sz = UnitText.split()
                        sTranslatedName = CyTranslator().getText(str(sz[0]), ("",))
                        unit.setName(sTranslatedName)
                    # PAE Debug: delete certain units
                    # if player.getUnit(j).getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
                    #   player.getUnit(j).doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

                    # Handelskarren CityID eintragen
                    # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
                    #   pPlot = unit.plot()
                    #   if pPlot.isCity():
                    #     #unit.setScriptData(str(pPlot.getPlotCity().getID()))
                    #     CvUtil.addScriptData(unit, "c", pPlot.getPlotCity().getID()) # CityID

                    (unit, pIter) = player.nextUnit(pIter, False)

                # Flunky: Einrueckung angepasst
                # Trait-Gebaeude ueberpruefen
                PAE_City.doCheckGlobalTraitBuildings(iPlayer)

                # Flunky: (city, pIter) statt for range
                # +++++ Check city status
                # und Trait-Gebaeude / trait buildings
                (loopCity, pIter) = player.firstCity(False)
                while loopCity:
                    if not loopCity.isNone() and loopCity.getOwner() == player.getID(): #only valid cities
                        PAE_City.doCheckCityState(loopCity)
                        PAE_City.doCheckTraitBuildings(loopCity)
                    (loopCity, pIter) = player.nextCity(pIter, False)

                # Start in spaeterer Aera -> unerforschbare und Relitechs entfernen
                # Start in later era -> remove unresearchable and religious techs
                # Scenarios ausgeschlossen!!!
                if sScenarioName == "":
                    iTeam = player.getTeam()
                    pTeam = gc.getTeam(iTeam)
                    for iTech in lTechs:
                        pTeam.setHasTech(iTech, 0, iPlayer, 0, 0)
                    if iEra > 0:
                        for iTech in lTechsReli:
                            pTeam.setHasTech(iTech, 0, iPlayer, 0, 0)
                    if player.getCivilizationType() not in lCivsRome:
                        pTeam.setHasTech(iTechRome, 0, iPlayer, 0, 0)
                    if player.getCivilizationType() not in lCivsGreek:
                        pTeam.setHasTech(iTechGreek, 0, iPlayer, 0, 0)

                if player.isHuman():
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setText(u"showDawnOfMan")
                    popupInfo.addPopup(iPlayer)

        # Flunky: sollte eigentlich problemlos gehen
        # ++++ Das Zedernholz benoetigt Savanne. Da es in den BONUS-Infos nicht funktioniert, muss es manuell gemacht werden
        #feat_forest = gc.getInfoTypeForString("FEATURE_SAVANNA")
        #bonus_zedern = gc.getInfoTypeForString("BONUS_ZEDERNHOLZ")
        #iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
        #iMapW = gc.getMap().getGridWidth()
        #iMapH = gc.getMap().getGridHeight()

        # for x in range(iMapW):
        #  for y in range(iMapH):
        #    loopPlot = gc.getMap().plot(x,y)
        #    #if loopPlot is not None and not loopPlot.isNone():
        #    if loopPlot.getFeatureType() == iDarkIce: continue
        #    if loopPlot.getBonusType(-1) == bonus_zedern and loopPlot.getFeatureType() != feat_forest:
        #       loopPlot.setFeatureType(feat_forest,1)
        # -----------

        # BTS Standard
        if gc.getGame().isPbem():
            iRange = gc.getMAX_PLAYERS()
            for iPlayer in range(iRange):
                pPlayer = gc.getPlayer(iPlayer)
                if pPlayer is not None and not pPlayer.isNone() and pPlayer.isAlive() and pPlayer.isHuman():
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
                    popupInfo.setOption1(True)
                    popupInfo.addPopup(iPlayer)

        CvAdvisorUtils.resetNoLiberateCities()

    def onGameEnd(self, argsList):
        'Called at the End of the game'
        print("Game is ending")
        return

    # this is a LOCAL function !!!
    def onBeginGameTurn(self, argsList):
        'Called at the beginning of the end of each turn'
        iGameTurn = argsList[0]
        ## AI AutoPlay ##
        if CyGame().getAIAutoPlay() == 0:
            CvTopCivs.CvTopCivs().turnChecker(iGameTurn)
        ## AI AutoPlay ##
        # CvTopCivs.CvTopCivs().turnChecker(iGameTurn)

        # Historische Texte ---------
        PAE_Turn_Features.doHistory()


    # global
    def onEndGameTurn(self, argsList):
        'Called at the end of the end of each turn'
        iGameTurn = argsList[0]

        # Special Scripts for PAE Scenarios
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName != "":
            if sScenarioName == "PeloponnesianWar":
                PeloponnesianWar.onEndGameTurn(iGameTurn)

            # ---------------- Schmelzen 3/4 (BoggyB) --------
            if sScenarioName == "SchmelzEuro" or sScenarioName == "SchmelzWelt":
                Schmelz.onEndGameTurn(iGameTurn, sScenarioName)

            if sScenarioName == "PeloponnesianWarKeinpferd":
                PeloponnesianWarKeinpferd.onEndGameTurn(iGameTurn)

        # Goody-Doerfer erstellen (goody-huts / GoodyHuts / Goodies / Villages) ##
        # PAE V: Treibgut erstellen
        # PAE V: Barbarenfort erstellen
        # PAE Trade Cities Special Bonus
        if gc.getGame().getGameTurnYear() > -2400:
            if iGameTurn % 20 == 0:
                PAE_Turn_Features.setGoodyHuts()
                PAE_Trade.addCityWithSpecialBonus(iGameTurn)
            PAE_Trade.doUpdateCitiesWithSpecialBonus(iGameTurn)

        # PAE V: Treibgut -> Strandgut
        PAE_Turn_Features.doStrandgut()

        # PAE Disasters / Katastrophen
        # Permanent Alliances entspricht = Naturkatastrophen (PAE)
        if not (gc.getGame().isOption(GameOptionTypes.GAMEOPTION_PERMANENT_ALLIANCES) or gc.getGame().isGameMultiPlayer()):
            PAE_Disasters.doGenerateDisaster(iGameTurn)

        # Seewind / Fair wind ----
        if iGameTurn % 15 == 0:
            PAE_Turn_Features.doSeewind()

        # PAE Debug Mark
        #"""
        if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
            if iGameTurn % 5 == 0:
                # Seevoelker erschaffen: Langboot + Axtkrieger oder Axtkaempfer | -1500 bis -800
                if gc.getGame().getGameTurnYear() > -1400 and gc.getGame().getGameTurnYear() < -800:
                    PAE_Barbaren.doSeevoelker()
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Seevoelker erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                # Wikinger erschaffen: Langboot + Berserker | ab 400 AD
                if gc.getGame().getGameTurnYear() >= 400:
                    PAE_Barbaren.doVikings()
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Wikinger erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Huns | Hunnen erschaffen: Hunnischer Reiter | ab 250 AD  ---------
        PAE_Barbaren.doHuns(iGameTurn)

        # Handelsposten erzeugen Kultur (PAE V Patch 3: und wieder Forts/Festungen)
        # Berberloewen erzeugen
        # Wildpferde, Wildelefanten, Wildkamele ab PAE V
        # Barbarenfort beleben (PAE V Patch 4)
        PAE_Turn_Features.doPlotFeatures()

        # Christentum gruenden
        if gc.getGame().getGameTurnYear() >= 0:
            if not PAE_Christen.bChristentum:
                PAE_Christen.setHolyCity()

        # PAE Debug Mark
        #"""

    # global
    def onBeginPlayerTurn(self, argsList):
        'Called at the beginning of a players turn'
        iGameTurn, iPlayer = argsList
        pPlayer = gc.getPlayer(iPlayer)
        pTeam = gc.getTeam(pPlayer.getTeam())

        # Reset InstanceModifier (Fighting Promotions, Hiring costs for mercenaries)
        PAE_Unit.PAEInstanceFightingModifier = []
        PAE_Mercenaries.PAEInstanceHiringModifier = {}
        PAE_Mercenaries.PAEMercComission = {}
        PAE_City.PAEStatthalterTribut = {}

        # --- Automated trade routes for HI (Boggy)
        if pPlayer.isHuman():
            (pLoopUnit, pIter) = pPlayer.firstUnit(False)
            while pLoopUnit:
                iUnitType = pLoopUnit.getUnitType()
                if iUnitType in PAE_Trade.lTradeUnits:
                    bTradeRouteActive = int(CvUtil.getScriptData(pLoopUnit, ["autA", "t"], 0))
                    if bTradeRouteActive and pLoopUnit.getGroup().getLengthMissionQueue() == 0:
                        PAE_Trade.doAutomateMerchant(pLoopUnit, False)
                        # pLoopUnit.finishMoves()
                        # Falls Haendler in Stadt zieht und noch Fortbewegung hat, soll direkt ge-/verkauft werden
                        #if pLoopUnit.canMove(): PAE_Trade.doAutomateMerchant(pLoopUnit, False)
                (pLoopUnit, pIter) = pPlayer.nextUnit(pIter, False)

        # ------- Scenario PeloponnesianWarKeinpferd Events Poteidaia, Megara, Plataiai, Syrakus
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName == "PeloponnesianWarKeinpferd":
            PeloponnesianWarKeinpferd.onBeginPlayerTurn(iGameTurn, pPlayer)

# -- TESTMESSAGE

#    if CyInterface().isOOSVisible():
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("OOS-Fehler - Player",iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)

#    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("MaxPlayers",gc.getMAX_PLAYERS())), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # PAE Debug Mark
        #"""

# -- Prevent BTS TECH BUG/Forschungsbug: AI chooses Tech if -1 -> 25% to push
        if iPlayer != gc.getBARBARIAN_PLAYER() and not pPlayer.isHuman() and pPlayer.getCurrentResearch() == -1:
            if CvUtil.myRandom(4, "Forschungsbug") == 1:
                techs = []
                iRange = gc.getNumTechInfos()
                for iTech in range(iRange):
                    if pPlayer.canResearch(iTech, False):
                        iCost = pTeam.getResearchLeft(iTech)
                        if iCost > 0:
                            techs.append((-iCost, iTech))
                if techs:
                    techs.sort()
                    iTech = techs[0][1]
                    pTeam.changeResearchProgress(iTech, 1, iPlayer)
                    pPlayer.clearResearchQueue()
                    #pPlayer.pushResearch (iTech, 1)


# +++++ STACKs ---------------------------------------------------------

# PAE IV Healer aufladen
# PAE V: Staedte sind extra

        if iPlayer > -1:
            PAE_Unit.stackDoTurn(iPlayer, iGameTurn)

        # +++++ AI Marodeure anpassen UNITAI_EXPLORE / UNITAI_PILLAGE / UNITAI_ATTACK
        # if iPlayer > -1:
            # if not gc.getPlayer(iPlayer).isHuman():
            # lUnits = PyPlayer(iPlayer).getUnitList()
            # for iUnits in range(len(lUnits)):
            # pUnit = gc.getPlayer(iPlayer).getUnit(lUnits[iUnits].getID())
            # if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_AXEMAN_MARODEUR") or pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SWORDSMAN_MARODEUR"):
            # xPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
            # # Im eigenen Land soll sie zuerst ausser Landes gebracht werden
            # if xPlot.getOwner() == pUnit.getOwner():
            # pUnit.setUnitAIType(UnitAITypes.UNITAI_EXPLORE) # UNITAI_EXPLORE
            # # Im feindlichen Land soll sie dann Pluendern / UNITAI_PIRATE_SEA geht nicht
            # elif xPlot.getOwner() > -1 and xPlot.getOwner() != gc.getBARBARIAN_PLAYER():
            # if xPlot.getImprovementType() > -1:
            # pUnit.setUnitAIType(UnitAITypes.UNITAI_PILLAGE)
            # else:
            # pUnit.setUnitAIType(UnitAITypes.UNITAI_ATTACK)


        # +++++ Angesiedelte Sklaven -> Rebellen/Gladiatoren / Buerger / Gladiatoren / Reservistensterben ---
        # Soll nur alle 4 Runden pruefen
        if iGameTurn % 4 == 0 and iPlayer != -1 and iPlayer != gc.getBARBARIAN_PLAYER():
            (loopCity, pIter) = pPlayer.firstCity(False)
            while loopCity:
                if not loopCity.isNone() and loopCity.getOwner() == iPlayer:
                    PAE_City.doSettledSlavesAndReservists(loopCity)
                (loopCity, pIter) = pPlayer.nextCity(pIter, False)
            # Stehende Sklaven / unsettled slaves
            PAE_Unit.unsettledSlaves(iPlayer)
        # Sklaven und Gladiatoren (REBELLEN) Ende ---

        # -- Missionare fuer verwandte CIVs ---------
        PAE_City.doMissionaryForCivs(iPlayer)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pPlayer.getName(),pPlayer.getAnarchyTurns())), None, 2, None, ColorTypes(10), 0, 0, False, False)


        # ------ Anarchie wenn mehr als die Haelfte der Staedte revoltieren (mehr als 1 Stadt) oder von der Pest heimgesucht werden - 33 %
        # nur wenn nicht schon Anarchie herrscht
        if pPlayer.getAnarchyTurns() <= 0:
            PAE_Turn_Features.doRevoltAnarchy(iPlayer)


# +++++ HI-Hegemon TECH Vasallenfeature (Chance 33% every 5th round) / Vassal Tech
        if iGameTurn % 5 == 0:
            if pPlayer.isHuman():
                iTech = gc.getInfoTypeForString("TECH_VASALLENTUM")
                iTeam = pPlayer.getTeam()
                pTeam = gc.getTeam(iTeam)
                if pTeam.isHasTech(iTech):

                    # Vasallen finden
                    iRange = gc.getMAX_PLAYERS()
                    for iVassal in range(iRange):
                        vPlayer = gc.getPlayer(iVassal)
                        if vPlayer.isAlive():
                            iTeam = vPlayer.getTeam()
                            vTeam = gc.getTeam(iTeam)
                            if vTeam.isVassal(pTeam.getID()):
                                TechArray = []
                                if CvUtil.myRandom(3, "Vasallenfeature") == 1:
                                    # Tech raussuchen, die der Vasall nicht hat
                                    iTechNum = gc.getNumTechInfos()
                                    for j in range(iTechNum):
                                        if pTeam.isHasTech(j) and not vTeam.isHasTech(j):
                                            if gc.getTechInfo(j) is not None:
                                                if gc.getTechInfo(j).isTrade():
                                                    TechArray.append(j)

                                if TechArray:
                                    iTechRand = CvUtil.myRandom(len(TechArray), "Vasallenfeature2")
                                    iTech = TechArray[iTechRand]
                                    # the more CIVs do have this tech, the cheaper
                                    iFaktor = gc.getGame().countKnownTechNumTeams(iTech)
                                    if iFaktor < 5:
                                        iFaktor = 5
                                    iTechCost = gc.getTechInfo(iTech).getResearchCost() / iFaktor
                                    popupInfo = CyPopupInfo()
                                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                                    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH", (vPlayer.getName(), vPlayer.getCivilizationShortDescription(0), gc.getTechInfo(iTech).getDescription(), iTechCost)))
                                    popupInfo.setData1(iPlayer)
                                    popupInfo.setData2(iVassal)
                                    popupInfo.setData3(iTech)
                                    popupInfo.setFlags(iTechCost)
                                    popupInfo.setOnClickedPythonCallback("popupVassalTech")  # EntryPoints/CvScreenInterface und CvGameUtils / 702
                                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_YES", ("",)), "")
                                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_MONEY", (iTechCost, iTechCost)), "")
                                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_NO", ("",)), "")
                                    popupInfo.addPopup(iPlayer)

        # PAE Debug Mark
        #"""

############################################
    # global
    def onEndPlayerTurn(self, argsList):
        'Called at the end of a players turn'
        iGameTurn, iPlayer = argsList
        pPlayer = gc.getPlayer(iPlayer)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pPlayer.getName(),pPlayer.calculateGoldRate())), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gold",pPlayer.getGold())), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # PAE Debug Mark
        #"""

# +++++ Special inits for Szenario Maps in PAE ++++++++++++++++++++++++++++++++
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName == "FirstPunicWar":
            FirstPunicWar.onEndPlayerTurn(iPlayer, iGameTurn)
        elif sScenarioName == "PeloponnesianWarKeinpferd":
            PeloponnesianWarKeinpferd.onEndPlayerTurn(iPlayer, iGameTurn)

# +++++ MAP Reveal to black fog - Kriegsnebel - Fog of War (FoW) - Karte schwarz zurueckfaerben
# AI auch, aber nur alle iPlayer-Runden
# AI wird wieder reingenommen -> wenn nur alle x Runden wahrscheinlich weniger Einheitenbewegung! -> no MAFs
        if pPlayer is not None and not pPlayer.isBarbarian():
            iTeam = pPlayer.getTeam()
            pTeam = gc.getTeam(iTeam)
            # Human oder KI alle x Runden, aber unterschiedliche Civs pro Runde fuer optimale Rundenzeiten
            if pPlayer.isHuman() or (iGameTurn % 20 == iPlayer % 20 and pTeam.isMapTrading()):
                bDontGoBlackAnymore = False
                bShowCoasts = False
                bShowPeaksAndRivers = False
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTOGRAPHIE2")):  # Strassenkarten
                    bDontGoBlackAnymore = True
                elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTEN")):  # Karte zeichnen
                    bShowCoasts = True
                    bShowPeaksAndRivers = True
                elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTOGRAPHIE")):  # Kartographie: Erste Karten
                    bShowCoasts = True

                if not bDontGoBlackAnymore:
                    iRange = CyMap().numPlots()
                    for iI in range(iRange):
                        pPlot = CyMap().plotByIndex(iI)
                        if not pPlot.isVisible(iTeam, 0):
                            bGoBlack = True
                            # fully black or standard fog of war
                            if pPlot.isCity():
                                pCity = pPlot.getPlotCity()
                                if bShowCoasts and pCity.isCapital():
                                    bGoBlack = False
                                elif pCity.getNumWorldWonders() > 0:
                                    bGoBlack = False
                            # Holy Mountain Quest
                            if bGoBlack:
                                if CvUtil.getScriptData(pPlot, ["H", "t"]) == "X":
                                    bGoBlack = False
                            # Improvements (to normal fog of war)
                            # if bGoBlack:
                            #  if pPlot.getImprovementType() == improv1 or pPlot.getImprovementType() == improv2: bGoBlack = False
                            # 50% Chance Verdunkelung
                            if bGoBlack:
                                if CvUtil.myRandom(2, "bGoBlack") == 0:
                                    bGoBlack = False
                            # Black fog
                            if bGoBlack:
                                if pPlot.isRevealed(iTeam, 0):
                                    # River and coast (land only)
                                    #if pPlot.isRevealed (iTeam, 0) and not (pPlot.isRiverSide() or pPlot.isCoastalLand()): pPlot.setRevealed (iTeam,0,0,-1)
                                    # River and coast (land and water)
                                    #if pPlot.isRevealed (iTeam, 0) and not (pPlot.isRiverSide() or pPlot.isCoastalLand() or (pPlot.isAdjacentToLand() and pPlot.isWater())): pPlot.setRevealed (iTeam,0,0,-1)
                                    if bShowCoasts:
                                        if pPlot.isCoastalLand() or pPlot.isAdjacentToLand() and pPlot.isWater():
                                            continue
                                    if bShowPeaksAndRivers:
                                        if pPlot.isRiverSide() or pPlot.isPeak():
                                            continue
                                    pPlot.setRevealed(iTeam, 0, 0, -1)


        # -- AI Commissions Mercenaries (AI Mercenaries)
        # not in first turn (scenarios)
        if not pPlayer.isHuman():
            if iGameTurn > 1 and iGameTurn % 10 == 0:
                if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SOELDNERTUM")):
                    iGold = pPlayer.getGold()
                    if iGold > 400:
                        if iGold > 800:
                            iChance = 20
                        else:
                            iChance = 10
                        if CvUtil.myRandom(100, "AI Mercenaries") < iChance:
                            PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)
                            # 20% gleich nochmal
                            if CvUtil.myRandom(5, "AI Mercenaries2") == 0:
                                PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)
                                # 10% ein drittes Mal damits interessant wird ;)
                                if CvUtil.myRandom(10, "AI Mercenaries3") == 0:
                                    PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)

        # Kriegslager soll alle x Runden Einheit erzeugen
        if iGameTurn > 1 and iGameTurn % 5 == 0:
            PAE_Barbaren.createCampUnit(iPlayer)

        # MESSAGES: city growing (nur im Hot-Seat-Modus)
        if gc.getGame().isHotSeat():
            if pPlayer.isHuman():
                for pyCity in PyPlayer(iPlayer).getCityList():
                    PAE_City.doMessageCityGrowing(pyCity.GetCy())

        # PAE Debug Mark
        #"""

# ++ Standard BTS ++
        if gc.getGame().getElapsedGameTurns() == 1:
            if gc.getPlayer(iPlayer).isHuman():
                if gc.getPlayer(iPlayer).canRevolution(0):
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC)
                    popupInfo.addPopup(iPlayer)

        CvAdvisorUtils.resetAdvisorNags()
        CvAdvisorUtils.endTurnFeats(iPlayer)
# +++ -------

# ----- CHECK CIV on Turn - change Team ID (0 = eg Romans) in gc.getPlayer(0).
        if self.bPAE_ShowMessagePlayerTurn:

            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pPlayer.getName(),iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pPlayer.getName(),gc.getMAX_PLAYERS())), None, 2, None, ColorTypes(10), 0, 0, False, False)

            showPlayer = iPlayer + 1
            if showPlayer >= gc.getMAX_PLAYERS():
                showPlayer = 0
            while not gc.getPlayer(showPlayer).isAlive():
                showPlayer += 1
                if showPlayer >= gc.getMAX_PLAYERS():
                    showPlayer = 0
            pShowPlayer = gc.getPlayer(showPlayer)
            thisPlayer = pShowPlayer.getCivilizationDescription(0)
            if self.bAllowCheats:
                CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN", (thisPlayer, "")), None, 2, None, ColorTypes(14), 0, 0, False, False)
            else:
                iThisTeam = gc.getPlayer(showPlayer).getTeam()
                if gc.getTeam(iThisTeam).isHasMet(pPlayer.getTeam()):
                    CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN", (thisPlayer, "")), None, 2, None, ColorTypes(14), 0, 0, False, False)
                else:
                    CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN2", ("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)

    def onEndTurnReady(self, argsList):
        iGameTurn = argsList[0]

    def onFirstContact(self, argsList):
        'Contact'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iTeamX, iHasMetTeamY = argsList
        if not self.__LOG_CONTACT:
            return
        CvUtil.pyPrint('Team %d has met Team %d' % (iTeamX, iHasMetTeamY))

    def onCombatResult(self, argsList):
        'Combat Result'
        pWinner, pLoser = argsList
        iWinnerPlayer = pWinner.getOwner()
        iLoserPlayer = pLoser.getOwner()
        pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
        pLoserPlayer = gc.getPlayer(iLoserPlayer)
        playerX = PyPlayer(iWinnerPlayer)
        iWinnerUnitType = pWinner.getUnitType()
        unitX = gc.getUnitInfo(iWinnerUnitType)
        playerY = PyPlayer(iLoserPlayer)
        iLoserUnitType = pLoser.getUnitType()
        unitY = gc.getUnitInfo(iLoserUnitType)
        pLoserPlot = pLoser.plot()
        pWinnerPlot = pWinner.plot()
        # PAE
        bUnitDone = False
        bWinnerIsDead = False

        # PAE Debug Mark
        #"""
        #### ---- unabhaengige Ereignisse ---- ####

        bWinnerAnimal = (pWinner.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or
                         iWinnerUnitType in L.LUnitCanBeDomesticated or
                         iWinnerUnitType in L.LUnitWildAnimals or
                         iWinnerUnitType in L.LUnitWarAnimals or
                         iWinnerUnitType in L.LUnitDomesticated)
        bLoserAnimal = (pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or
                        iLoserUnitType in L.LUnitCanBeDomesticated or
                        iLoserUnitType in L.LUnitWildAnimals or
                        iLoserUnitType in L.LUnitWarAnimals or
                        iLoserUnitType in L.LUnitDomesticated)

        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName == "FirstPunicWar":
            FirstPunicWar.onCombatResult(pWinner, pLoser)

        # ---- Blessed Units
        # Blessed promo only helps one time
        iPromo = gc.getInfoTypeForString("PROMOTION_BLESSED")
        if pWinner.isHasPromotion(iPromo):
            pWinner.setHasPromotion(iPromo, False)
        if pLoser.isHasPromotion(iPromo):
            pLoser.setHasPromotion(iPromo, False)

        # --------- Feature - Seuche auf dem Schlachtfeld ----------------------
        # Wahrscheinlichkeit einer Seuche auf dem Schlachtfeld
        # Ab 4 Einheiten, etwa Chance 2%
        if pLoserPlot.getNumUnits() > 3:
            feat_seuche = gc.getInfoTypeForString("FEATURE_SEUCHE")
            iRand = CvUtil.myRandom(50, "FEATURE_SEUCHE")
            if iRand == 1:
                if pWinnerPlot.getFeatureType() == -1 and not pWinnerPlot.isCity() and not pWinnerPlot.isWater():
                    pWinnerPlot.setFeatureType(feat_seuche, 0)
                if pLoserPlot.getFeatureType() == -1 and not pLoserPlot.isCity() and not pLoserPlot.isWater():
                    pLoserPlot.setFeatureType(feat_seuche, 0)


        # ------- Change Culture Percent on the Plots after a battle
        # Choose Plot and add 20% culture to the winner
        if not pLoserPlot.isWater():
            iCulture = pLoserPlot.getCulture(iLoserPlayer)
            # only if the loser has culture on this plot, the winner gets culture points (eg. neutral area or 3rd civ area)
            if iCulture > 0 and not pLoserPlot.isCity() and not bWinnerAnimal and not bLoserAnimal:
                if iCulture > 9:
                    Calc = iCulture/5
                    iCalc = int(round(Calc, 0))
                else:
                    iCalc = 1
                pLoserPlot.changeCulture(iWinnerPlayer, iCalc, 1)
                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Kulturveraenderung durch Kampf (Zeile 1922)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Techboost for winning unit (when its technology is unknown)
        iTech = gc.getUnitInfo(iLoserUnitType).getPrereqAndTech()
        pWinnerTeam = gc.getTeam(pWinnerPlayer.getTeam())
        if not pWinnerTeam.isHasTech(iTech):
            if pWinnerPlayer.canResearch(iTech, False):
                iCost = gc.getTechInfo(iTech).getResearchCost()
                iCost = iCost/10
                if iCost <= 1:
                    iCost = 1
                else:
                    iCost = iCost + CvUtil.myRandom(iCost, "Techboost")
                pWinnerTeam.changeResearchProgress(iTech, iCost, iWinnerPlayer)
                if pWinnerPlayer.isHuman():
                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TECH_BY_UNIT", (gc.getTechInfo(iTech).getDescription(), iCost)), None, 2, None, ColorTypes(8), 0, 0, False, False)

        # Improvement destruction during battle / destroy imp
        iImprovement = pLoserPlot.getImprovementType()
        if iImprovement > -1 and not bWinnerAnimal and not bLoserAnimal:
            if iImprovement != gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS") and iImprovement != gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"):
                iChance = 5  # 5%

                # Forts only 2%, except with catapults
                bFortress = False
                if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT") or iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT2"):
                    iChance = 2
                    bFortress = True

                    # Get attacking unit
                    if pWinner.isAttacking():
                        sUnitType = iWinnerUnitType
                    else:
                        sUnitType = iLoserUnitType

                    if sUnitType in L.LBuildCatapults:
                        iChance = 10

                # Chance calculation
                if CvUtil.myRandom(100, "IMPROVEMENT_DESTROYED_COMBAT") < iChance:
                    # message to human winner or loser
                    if pWinnerPlayer.isHuman():
                        CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT", (gc.getImprovementInfo(iImprovement).getDescription(),)), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pLoserPlot.getX(), pLoserPlot.getY(), True, True)
                    if pLoserPlayer.isHuman():
                        CyInterface().addMessage(iLoserPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT", (gc.getImprovementInfo(iImprovement).getDescription(),)), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pLoserPlot.getX(), pLoserPlot.getY(), True, True)
                    # message to human plot owner
                    iPlotOwner = pLoserPlot.getOwner()
                    if iPlotOwner != -1 and iPlotOwner != iWinnerPlayer and iPlotOwner != iLoserPlayer:
                        if gc.getPlayer(iPlotOwner).isHuman():
                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT_PLOT_OWNER", (pWinnerPlayer.getName(), pLoserPlayer.getName(), gc.getImprovementInfo(iImprovement).getDescription())), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pLoserPlot.getX(), pLoserPlot.getY(), True, True)

                    # Destroy improvement
                    if bFortress:
                        pLoserPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"))
                    elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
                        pLoserPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"))
                    elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"):
                        pLoserPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_HAMLET"))
                    elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HAMLET"):
                        pLoserPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"))
                    elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"):
                        pLoserPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"))
                    else:
                        pLoserPlot.setImprovementType(-1)
        #### ---- Ende unabhaengige Ereignisse ---- ####

        #### ---- betrifft Winner ---- ####
        iPromoFuror1 = gc.getInfoTypeForString('PROMOTION_FUROR1')
        iPromoFuror2 = gc.getInfoTypeForString('PROMOTION_FUROR2')
        iPromoFuror3 = gc.getInfoTypeForString('PROMOTION_FUROR3')
        # Weil bSuicide in XML scheinbar so funktioniert, dass auf jeden Fall der Gegner stirbt (was ich nicht will)
        if pWinner.getUnitType() == gc.getInfoTypeForString("UNIT_BURNING_PIGS"):
            # Parallele zu isSuicide() im SDK direkt nach dieser Funktion:
            # pWinner.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pWinner.kill(True, -1)  # RAMK_CTD
            bWinnerIsDead = True
        elif pWinner.isHasPromotion(iPromoFuror1):
            # ------- Furor germanicus / teutonicus: 30% / 20% / 10% Chance
            iWinnerST = pWinner.baseCombatStr()
            iLoserST = pLoser.baseCombatStr()
            # weak units without death calc (eg animal)
            # enemy units should be equal
            if iLoserST >= (iWinnerST / 5) * 4:
                iChanceSuicide = 3
                if pWinner.isHasPromotion(iPromoFuror3):
                    iChanceSuicide = 1
                elif pWinner.isHasPromotion(iPromoFuror2):
                    iChanceSuicide = 2

                if CvUtil.myRandom(10, "Furor") < iChanceSuicide:
                    pWinner.kill(True, -1)
                    bWinnerIsDead = True
                    if pWinnerPlayer.isHuman():
                        CyInterface().addMessage(iWinnerPlayer, True, 5,
                                                 CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_FUROR_SUICIDE", (pWinner.getName(), 0)),
                                                 None, 2, pWinner.getButton(), ColorTypes(7), pWinner.getX(), pWinner.getY(), True, True)

        # Promotions for winner
        if not bWinnerIsDead:
            if pWinner.isMilitaryHappiness() or pWinner.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                PAE_Unit.doAutomatedRanking(pWinner, pLoser)

            # ------- Unit gets certain promotion PAE V Beta 2 Patch 7
            if pLoser.getUnitCombatType() != -1 and not bWinnerAnimal and not bLoserAnimal:
                if pWinner.isMadeAttack() and pWinnerPlayer.isTurnActive():
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pLoser.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                    PAE_Unit.doUnitGetsPromo(pWinner, pLoser, pLoserPlot, True)
                else:
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pWinner.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                    PAE_Unit.doUnitGetsPromo(pWinner, pLoser, pWinnerPlot, False)

        # Auto Formation Flight
        #iFormation = gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG")
        # if not pWinner.isHasPromotion(iFormation):
        #  if pWinner.getDamage() >= 80: pWinner.setHasPromotion(iFormation, True)

        #### ---- betrifft Loser ---- ####
        # ------- Loser Unit Elephant makes 20% collateral damage to friendly units
        if iLoserUnitType == gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"):
            iRange = pLoserPlot.getNumUnits()
            for iLoopUnit in range(iRange):
                pLoopUnit = pLoserPlot.getUnit(iLoopUnit)
                if pLoopUnit.getDamage() + 20 < 100:
                    pLoopUnit.changeDamage(20, False)
            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ELEPHANT_DAMAGE_1", (unitY.getDescription(), 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            if pLoserPlayer.isHuman():
                CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ELEPHANT_DAMAGE_2", (unitY.getDescription(), 0)), None, 2, None, ColorTypes(7), 0, 0, False, False)

        if not pLoserPlayer.isHuman():
            if pLoserPlot.getNumUnits() > 4:
                PAE_Unit.doAIPlotFormations(pLoserPlot, iLoserPlayer)

        # Einheit soll alles ausladen, wenn besiegt   #pie
        # Geht nicht, leider wird zuerst das Cargo und dann die Einheit gekillt! Schade!
        #    if pLoser.getDomainType() == DomainTypes.DOMAIN_LAND and pLoser.hasCargo(): pLoser.doCommand(CommandTypes.COMMAND_UNLOAD_ALL,0,0)

        bNavalUnit = pWinner.getDomainType() == DomainTypes.DOMAIN_SEA
        if bNavalUnit:
            bUnitDone = PAE_Unit.doNavalOnCombatResult(pWinner, pLoser, bWinnerIsDead)
            #pLoser could be invalid if jumped away -> some cases of bUnitDone
        elif not bWinnerIsDead:
            # ---- LAND: Player can earn gold by winning a battle
            # Flunky: but dead warriors don't take loot
            if not bLoserAnimal:
                iCost = unitY.getProductionCost()
                if iCost > 0:
                    iGold = int(iCost / 10)
                    if iGold > 1:
                        iGold = CvUtil.myRandom(iGold, "LandeinheitenKillMoney")
                        pWinnerPlayer.changeGold(iGold)
                        if iGold > 0:
                            if pWinnerPlayer.isHuman():
                                CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MONEY_UNIT_KILLED", ("", iGold)), None, 2, None, ColorTypes(8), 0, 0, False, False)
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gold durch Einheitensieg (Zeile 1711)",iGold)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # ------- Certain animals can be captured, when domestication has been researched
            # ------- Bestimmte Tiere koennen eingefangen werden, wenn Domestizier-Tech erforscht wurde
            elif iLoserUnitType in L.LUnitCanBeDomesticated:
                iTech = -1
                if iLoserUnitType == gc.getInfoTypeForString("UNIT_WILD_HORSE"):
                    iTech = gc.getInfoTypeForString("TECH_PFERDEZUCHT")
                elif iLoserUnitType == gc.getInfoTypeForString("UNIT_WILD_CAMEL"):
                    iTech = gc.getInfoTypeForString("TECH_KAMELZUCHT")
                elif iLoserUnitType == gc.getInfoTypeForString("UNIT_ELEFANT"):
                    iTech = gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")

                if iTech != -1:
                    iThisTeam = pWinnerPlayer.getTeam()
                    if gc.getTeam(iThisTeam).isHasTech(iTech):
                        bUnitDone = True
                        # Create a new unit
                        NewUnit = pWinnerPlayer.initUnit(iLoserUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                        NewUnit.finishMoves()
                        if pWinnerPlayer.isHuman():
                            CyInterface().addMessage(iWinnerPlayer, True, 5, CyTranslator().getText("TXT_KEY_UNIT_EROBERT", (unitY.getDescription(), 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
        # ----- Ende Loser Unit (not captured)

        # pWinner may get bonus experience etc, if pLoser is not being domesticated and pLoser is not Treibgut
        if not bUnitDone and not bWinnerIsDead:
            # ------- Feature 1: Generalseinheiten bekommen +1XP, wenn im selben Stack eine angreifende Einheit siegt (10%)
            # ------- Feature 2: Eine Generalseinheit bekommt HERO Promotion wenn eine Einheit einen General oder einen Held besiegt.
            # ------------------ Ist kein General im Stack bekommt die Promotion die Gewinner-Unit
            # ------------------ Und Gewinner bekommt additional +3 XP
            iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
            # ------- Diese Features betreffen nur attackierende Einheiten (keine defensiven)
            if pWinner.isMadeAttack() and not bWinnerAnimal and pWinner.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
                iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
                bPromoHero = False
                bPromoHeroDone = False
                if pLoser.isHasPromotion(iPromoLeader) or pLoser.isHasPromotion(iPromoHero):
                    bPromoHero = True
                    # Hero und +3 XP
                    bPromoHeroDone = PAE_Unit.doUnitGetsHero(pWinner, pLoser)
                # for each general who accompanies the stack: +1 XP
                # one general gets the hero promo, if not possessing
                bLeaderAnwesend = PAE_Unit.getExperienceForLeader(pWinner, pLoser, bPromoHero and not bPromoHeroDone)

                # Eine Einheit mit Mercenary-Promo kann diese verlieren, wenn ein General im Stack ist (5% Chance)
                if bLeaderAnwesend:
                    PAE_Unit.removeMercenaryPromo(pWinner)

                # Attacks not against animals
                if not bLoserAnimal and pLoser.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
                    # PAE Feature 3: Unit Rang Promos (Unit Ranks, Unit Ranking)
                    PAE_Unit.doRankPromo(pWinner)
            # end if pWinner.isMadeAttack

            # ------- Feature 1: Held Promo + 3 XP wenn Stier (Ur) oder Tier mit mehr als 3 Level erlegt wird
            # ---------------- nur wenn Einheit nicht schon ein Held ist
            # ---------------- und wenn Combat ST Sieger < als Combat ST vom Gegner
            # ------- Feature 2: Ab Tech Kriegerethos bekommen Sieger + XP
            if bLoserAnimal:
                PAE_Unit.doHunterHero(pWinner, pLoser)
            else:
                # PAE Feature: Kriegerethos
                iTech = gc.getInfoTypeForString("TECH_KRIEGERETHOS")
                pWinnerTeam = gc.getTeam(pWinnerPlayer.getTeam())
                if pWinnerTeam.isHasTech(iTech):
                    iXP = 1
                    if pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")) or pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")):
                        iXP = 2
                    pWinner.changeExperience(iXP, -1, 0, 0, 0)

        bUnitFlucht = False
        bCityRenegade = False
        bUnitRenegades = False
        pLoserFlucht = None
        if not bUnitDone:
            if bWinnerIsDead or pWinner.isDead():
                iWinnerDamage = 100
            else:
                iWinnerDamage = pWinner.getDamage()
            # pLoser tries to flee if pLoser is not being domesticated and pLoser is not Treibgut
            bUnitFlucht, pLoserFlucht = PAE_Unit.flee(pLoser, iWinnerPlayer, iWinnerDamage)
            if not bUnitFlucht:
                # Feature: Wenn die Generalseinheit stirbt, ist in jeder Stadt 2 bis 4 Hurry Anger! (GG Great General dies)
                # Richtet sich nach der Anzahl der lebenden Generals
                # PAE V: Einheiten im Stack bekommen Mercenary-Promo (je nach Anzahl an Generals im Stack)
                PAE_Unit.doDyingGeneral(pLoser, iWinnerPlayer)

                # ------- Rebell takes over slaves if capturing
                if iLoserUnitType == gc.getInfoTypeForString("UNIT_SLAVE") and iWinnerPlayer == gc.getBARBARIAN_PLAYER() and not bWinnerAnimal:
                    barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                    iUnitType = gc.getInfoTypeForString("UNIT_REBELL")
                    iNumUnits = pLoserPlot.getNumUnits()
                    for _ in range(iNumUnits):
                        NewUnit = barbPlayer.initUnit(iUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                        NewUnit.finishMoves()
                    if pLoserPlayer.isHuman():
                        CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CAPTURED_SLAVES", ("", 0)), None, 2, "Art/Interface/Buttons/Units/button_rebell.dds", ColorTypes(7), pLoserPlot.getX(), pLoserPlot.getY(), True, True)

                        # ***TEST***
                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebell holt sich Bausklaven zu sich (Zeile 1947)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                if not bWinnerIsDead:
                    # ---- Script DATAs in Units
                    PAE_Mercenaries.startMercTorture(pLoser, iWinnerPlayer)

                    # --------- Jagd - Feature ----------------------
                    # Ab Tech Jagd (Hunting) bringen Tiere Essen in nahegelegene Stadt
                    if bLoserAnimal:
                        PAE_Unit.huntingResult(pLoser, pWinner)

                if pLoserPlot.isCity():
                    pCity = pLoserPlot.getPlotCity()
                    # PAE V ab Patch 3: Einheiten mobilisieren
                    if pCity.isCapital():
                        PAE_Unit.doMobiliseFortifiedArmy(pCity)
                    # ------ ueberlaufende Stadt - City renegades
                    # pLoser wird nicht angetastet
                    bCityRenegade = PAE_City.doRenegadeOnCombatResult(pLoser, pCity, iWinnerPlayer)

                if not bCityRenegade:
                    bUnitRenegades = PAE_Unit.renegade(pWinner, pLoser)

                # LOSER: Mounted -> Melee or Horse
                # Nur wenn die Einheit nicht desertiert hat: bUnitRenegades
                if not bUnitRenegades and pLoser.getUnitCombatType() in [gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"), gc.getInfoTypeForString("UNITCOMBAT_CHARIOT")]:
                    bUnitDone = PAE_Unit.doLoserLoseHorse(pLoser, iWinnerPlayer)


        if not bCityRenegade and not bUnitRenegades and not bUnitDone and bUnitFlucht and pLoserFlucht is not None:
            PAE_Unit.doUnitGetsPromo(pLoserFlucht, pWinner, pLoserPlot, False)

        #####################################################
        # PAE Debug Mark
        #"""

        if not self.__LOG_COMBAT:
            return
        # BTS Original
        # if playerX and playerX and unitX and playerY:
        #  CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s'
        #    %(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
        #    playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))
        # PAE Spezielle Logs wegen versteckten Einheiten (zB Piraten)
        if unitX and playerX and unitY and playerY:
            if pWinner.getInvisibleType() != -1 and pLoser.getInvisibleType() != -1:
                CvUtil.pyPrint('Hidden Unit %s has defeated hidden Unit %s' % (unitX.getDescription(), unitY.getDescription()))
            elif pWinner.getInvisibleType() != -1:
                CvUtil.pyPrint('Hidden Unit %s has defeated Player %d Civilization %s Unit %s'
                               % (unitX.getDescription(), playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))
            elif pLoser.getInvisibleType() != -1:
                CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated hidden Unit %s'
                               % (playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(), unitY.getDescription()))
            else:
                CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s'
                               % (playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
                                  playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))

    def onCombatLogCalc(self, argsList):
        'Combat Result'
        genericArgs = argsList[0][0]
        cdAttacker = genericArgs[0]
        cdDefender = genericArgs[1]
        iCombatOdds = genericArgs[2]
        CvUtil.combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds)

    def onCombatLogHit(self, argsList):
        'Combat Message'
        # global gCombatMessages, gCombatLog
        genericArgs = argsList[0][0]
        cdAttacker = genericArgs[0]
        cdDefender = genericArgs[1]
        iIsAttacker = genericArgs[2]
        iDamage = genericArgs[3]

        # BTS Original
        if cdDefender.eOwner == cdDefender.eVisualOwner:
            szDefenderName = gc.getPlayer(cdDefender.eOwner).getNameKey()
        else:
            szDefenderName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())
        if cdAttacker.eOwner == cdAttacker.eVisualOwner:
            szAttackerName = gc.getPlayer(cdAttacker.eOwner).getNameKey()
        else:
            szAttackerName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())

        if iIsAttacker == 0:
            combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szDefenderName, cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
            CyInterface().addCombatMessage(cdAttacker.eOwner, combatMessage)
            CyInterface().addCombatMessage(cdDefender.eOwner, combatMessage)
            if cdDefender.iCurrHitPoints <= 0:
                combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szAttackerName, cdAttacker.sUnitName, szDefenderName, cdDefender.sUnitName))
                CyInterface().addCombatMessage(cdAttacker.eOwner, combatMessage)
                CyInterface().addCombatMessage(cdDefender.eOwner, combatMessage)
        elif iIsAttacker == 1:
            combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szAttackerName, cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
            CyInterface().addCombatMessage(cdAttacker.eOwner, combatMessage)
            CyInterface().addCombatMessage(cdDefender.eOwner, combatMessage)
            if cdAttacker.iCurrHitPoints <= 0:
                combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szDefenderName, cdDefender.sUnitName, szAttackerName, cdAttacker.sUnitName))
                CyInterface().addCombatMessage(cdAttacker.eOwner, combatMessage)
                CyInterface().addCombatMessage(cdDefender.eOwner, combatMessage)

        ## TODO: only if not hidden nationality
        # PAE Wegen Bekanntgabe der Piraten im Log wird hier auskommentiert!
        # if (iIsAttacker == 0):
        #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
        #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
        #  if (cdDefender.iCurrHitPoints <= 0):
        #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName))
        #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
        # elif (iIsAttacker == 1):
        #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
        #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
        #  if (cdAttacker.iCurrHitPoints <= 0):
        #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName))
        #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

    def onImprovementBuilt(self, argsList):
        'Improvement Built'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iImprovement, iX, iY = argsList

        if iImprovement in (-1, gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"), gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")):
            return

        # PAE: Weiler: Dichter Wald -> Wald
        if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HAMLET") \
                or iImprovement == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"):
            pPlot = gc.getMap().plot(iX, iY)
            if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
                pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"), 1)
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
            pPlot = gc.getMap().plot(iX, iY)
            if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
                pPlot.setFeatureType(-1, 0)

        if not self.__LOG_IMPROVEMENT:
            return
        CvUtil.pyPrint('Improvement %s was built at %d, %d'
                       % (PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

    def onImprovementDestroyed(self, argsList):
        'Improvement Destroyed'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iImprovement, iOwner, iX, iY = argsList

        if iImprovement in (-1, gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"), gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")):
            return

        if not self.__LOG_IMPROVEMENT:
            return
        CvUtil.pyPrint('Improvement %s was Destroyed at %d, %d'
                       % (PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

    def onRouteBuilt(self, argsList):
        'Route Built'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iRoute, iX, iY = argsList
        if not self.__LOG_IMPROVEMENT:
            return
        CvUtil.pyPrint('Route %s was built at %d, %d'
                       % (gc.getRouteInfo(iRoute).getDescription(), iX, iY))

    def onPlotRevealed(self, argsList):
        'Plot Revealed'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        pPlot = argsList[0]
        iTeam = argsList[1]

    def onPlotFeatureRemoved(self, argsList):
        'Plot Revealed'
        pPlot = argsList[0]
        iFeatureType = argsList[1]
        pCity = argsList[2]  # This can be null

    def onPlotPicked(self, argsList):
        'Plot Picked'
        pPlot = argsList[0]
        CvUtil.pyPrint('Plot was picked at %d, %d'
                       % (pPlot.getX(), pPlot.getY()))

    def onNukeExplosion(self, argsList):
        'Nuke Explosion'
        pPlot, pNukeUnit = argsList
        CvUtil.pyPrint('Nuke detonated at %d, %d'
                       % (pPlot.getX(), pPlot.getY()))

    def onGotoPlotSet(self, argsList):
        'Nuke Explosion'
        pPlot, iPlayer = argsList

    # global
    def onBuildingBuilt(self, argsList):
        'Building Completed'
        pCity, iBuildingType = argsList
        iPlayer = pCity.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        # PAE Debug Mark
        #"""
        #    #If this is a wonder...
        #    if not gc.getGame().isNetworkMultiPlayer() and gc.getPlayer(pCity.getOwner()).isHuman() and isWorldWonderClass(gc.getBuildingInfo(iBuildingType).getBuildingClassType()):
        if pPlayer.isHuman() and gc.getBuildingInfo(iBuildingType).getMovieDefineTag() != "NONE":
            ## Platy WorldBuilder ##
            if not CyGame().GetWorldBuilderMode():
                ## Platy WorldBuilder ##
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iBuildingType)
                popupInfo.setData2(pCity.getID())
                popupInfo.setData3(0)
                popupInfo.setText(u"showWonderMovie")
                popupInfo.addPopup(iPlayer)

        # Kolonie / Provinz ----------
        # Wenn der Palast neu erbaut wird
        if iBuildingType == gc.getInfoTypeForString("BUILDING_PALACE"):
            iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
            pCity.setNumRealBuilding(iBuilding, 0)
            iBuilding = gc.getInfoTypeForString("BUILDING_PRAEFECTUR")
            pCity.setNumRealBuilding(iBuilding, 0)
        # ----------------------------
            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palast erbaut (Zeile 2206)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Kanalisation -> Suempfe werden rund um der Stadt entfernt (Sumpf/Swamps)
        # Oder Deich, Damm, Levee, Kanal
        lSwampRemovingBuildings = {
            gc.getInfoTypeForString('BUILDING_SANITATION'):"TXT_KEY_MESSAGE_SANITATION_BUILT",
            # gc.getInfoTypeForString('BUILDING_LEVEE'):"TXT_KEY_MESSAGE_LEVEE_BUILT",
            gc.getInfoTypeForString('BUILDING_LEVEE2'):"TXT_KEY_MESSAGE_LEVEE2_BUILT"
        }
        try:
            sText = lSwampRemovingBuildings[iBuildingType]
            PAE_City.removeSwamp(pCity, sText)
        except KeyError:
            pass

        PAE_Cultivation.doBuildingCultivate(pCity, iBuildingType)

        # Warft (ein Huegel entsteht)
        if iBuildingType == gc.getInfoTypeForString('BUILDING_WARFT'):
            pPlot = pCity.plot()
            pPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)

        # Wonder: Tower of Babel => increasing Sympathy for all well-known AIs by +4
        if iBuildingType == gc.getInfoTypeForString('BUILDING_BABEL'):
            pPlayer = gc.getPlayer(iPlayer)
            iRange = gc.getMAX_PLAYERS()
            for iSecondPlayer in range(iRange):
                pSecondPlayer = gc.getPlayer(iSecondPlayer)
                iSecTeam = pSecondPlayer.getTeam()
                if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                    pSecondPlayer.AI_changeAttitudeExtra(iPlayer, +4)

        # Wonder: 10 Gebote => adds 1 prophet and 10 jewish cities
        if iBuildingType == gc.getInfoTypeForString('BUILDING_10GEBOTE'):
            pPlayer = gc.getPlayer(pCity.getOwner())
            iUnitType = gc.getInfoTypeForString("UNIT_PROPHET")
            NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_PROPHET, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.setName("Moses")

            # converts up to 10 local cities to judaism (PAE V Patch 4)
            iReligion = gc.getInfoTypeForString("RELIGION_JUDAISM")
            Cities = []
            (loopCity, pIter) = pPlayer.firstCity(False)
            while loopCity:
                if not loopCity.isNone() and loopCity.getOwner() == pPlayer.getID(): #only valid cities
                    if not loopCity.isHasReligion(iReligion):
                        Cities.append(loopCity)
                (loopCity, pIter) = pPlayer.nextCity(pIter, False)
            a = 10
            iCities = len(Cities)
            iAnz = min(iCities, a)
            while iCities > 0 and a > 0:
                iRand = CvUtil.myRandom(iCities, "10Gebote")
                Cities[iRand].setHasReligion(iReligion, 1, 1, 0)
                Cities.pop(iRand)
                a -= 1
                iCities -= 1

            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_10GEBOTE", (iAnz,)), None, 2, None, ColorTypes(14), 0, 0, False, False)

            #iUnitType = gc.getInfoTypeForString("UNIT_JEWISH_MISSIONARY")
            #Names = ["Sarah","Abraham","Isaak","Jakob","Pinchas","Aaron","Miriam","Josua","Bileam","Jesaja"]
            # for i in range(10):
            #  NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
            #  NewUnit.setName(Names[i])

        # PAE Debug Mark
        #"""

        CvAdvisorUtils.buildingBuiltFeats(pCity, iBuildingType)

        if not self.__LOG_BUILDING:
            return
        CvUtil.pyPrint('%s was finished by Player %d Civilization %s'
                       % (PyInfo.BuildingInfo(iBuildingType).getDescription(), iPlayer, pPlayer.getCivilizationDescription(0)))

    def onProjectBuilt(self, argsList):
        'Project Completed'
        pCity, iProjectType = argsList
        game = gc.getGame()
        if gc.getPlayer(pCity.getOwner()).isHuman():
            ## Platy WorldBuilder ##
            if not CyGame().GetWorldBuilderMode():
                ## Platy WorldBuilder ##
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iProjectType)
                popupInfo.setData2(pCity.getID())
                popupInfo.setData3(2)
                popupInfo.setText(u"showWonderMovie")
                popupInfo.addPopup(pCity.getOwner())

        # Project : Seidenstrasse
        if iProjectType == gc.getInfoTypeForString("PROJECT_SILKROAD"):
            iPlayer = pCity.getOwner()
            pPlayer = gc.getPlayer(iPlayer)
            iGold = 400
            if gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_QUICK"):
                iGold = 200  # Speed: 50%
            elif gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_MARATHON"):
                iGold = 600  # Speed: 150%

            pPlayer.changeGold(iGold)
            if iPlayer == gc.getGame().getActivePlayer():
                CyAudioGame().Play2DSound('AS2D_COINS')
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_PROJECT_SEIDENSTRASSE", (iGold,)))
                popupInfo.addPopup(iPlayer)

            # Add Trade Route to city 26.01.2013
            pCity.changeExtraTradeRoutes(1)

        # Project : Bibel / Bible
        if iProjectType == gc.getInfoTypeForString("PROJECT_BIBEL"):
            # converts up to 12 global cities to christianity (PAE V Patch 4)
            iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
            Cities = []
            iRangeMaxPlayers = gc.getMAX_PLAYERS()
            for iPlayer in range(iRangeMaxPlayers):
                ThisPlayer = gc.getPlayer(iPlayer)
                if iPlayer != gc.getBARBARIAN_PLAYER():
                    if ThisPlayer.isAlive():
                        iNumCities = ThisPlayer.getNumCities()
                        for i in range(iNumCities):
                            ThisCity = ThisPlayer.getCity(i)
                            if not ThisCity.isNone():
                                if not ThisCity.isHasReligion(iReligion):
                                    Cities.append(ThisCity)

            a = 12
            iCities = len(Cities)
            while iCities > 0 and a > 0:
                iRand = CvUtil.myRandom(iCities, "Bibel")
                pLoopCity = Cities.pop(iRand)
                pLoopCity.setHasReligion(iReligion, 1, 1, 0)
                CyInterface().addMessage(pLoopCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_BIBEL", (pLoopCity.getName(),)), None, 2, None, ColorTypes(14), 0, 0, False, False)
                a -= 1
                iCities -= 1

            # adds 12 christian missionaries (until PAE V Patch 3)
            #pPlayer = gc.getPlayer(pCity.getOwner())
            #iUnitType = gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY")
            #Names = ["Petrus","Andreas","Jakobus","Johannes","Philippus","Bartholomaeus","Thomas","Matthaeus","Jakobus","Thaddaeus","Simon","Judas"]
            # for i in range(12):
            #  NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
            #  NewUnit.setName(Names[i])

    def onSelectionGroupPushMission(self, argsList):
        'selection group mission'
        eOwner = argsList[0]
        eMission = argsList[1]
        iNumUnits = argsList[2]
        listUnitIds = argsList[3]
        pPlayer = gc.getPlayer(eOwner)

        # Handel (nur Meldung mit der gewonnenen Geldsumme)
        if eMission == MissionTypes.MISSION_TRADE:
            pUnit = pPlayer.getUnit(listUnitIds[0])
            pPlot = pUnit.plot()
            pCity = pPlot.getPlotCity()
            if pUnit.canMove():
                if pPlayer.isHuman():
                    if eOwner == gc.getGame().getActivePlayer():
                        CyAudioGame().Play2DSound("AS2D_COINS")
                    iProfit = pUnit.getTradeGold(pPlot)
                    CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_AUTOMATE_MERCHANT_DONE", (pCity.getName(), iProfit)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                # Normaler Handel - Handelsstrasse bauen: Chance 2%
                if CvUtil.myRandom(100, "Handelsstrasse bauen") < 2:
                    scriptCityId = CvUtil.getScriptData(pUnit, ["c", "t"])  # CityID
                    if scriptCityId != "":
                        pSource = pPlayer.getCity(scriptCityId).plot()
                    else:
                        pSource = pPlayer.getCapitalCity().plot()
                    pSourceCity = pSource.getPlotCity()
                    pPlotTradeRoad = PAE_Trade.getPlotTradingRoad(pSource, pPlot)
                    if pPlotTradeRoad is not None:
                        pPlotTradeRoad.setRouteType(gc.getInfoTypeForString("ROUTE_TRADE_ROAD"))
                        if pPlayer.isHuman():
                            CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT", (pPlayer.getName(), pPlayer.getCivilizationShortDescriptionKey(), pCity.getName(), pSourceCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)

        # Fernangriff / Fernkampfkosten
        # Nur 1x Fernangriff danach nur bewegen => GlobalDefines RANGED_ATTACKS_USE_MOVES=0
        if eMission == MissionTypes.MISSION_RANGE_ATTACK:
            lUnits = []
            for i in listUnitIds:
                pLoopUnit = pPlayer.getUnit(i)
                if pLoopUnit.isRanged():
                    # Liste fuer Kosten
                    lUnits.append(pLoopUnit)

                    # Nicht fuer Plaenklereinheiten
                    if (pLoopUnit.getUnitType() not in L.LUnitSkirmish and
                        pLoopUnit.getUnitClassType() not in L.LClassSkirmish):
                        if pLoopUnit.getGroup().hasMoved():
                            pLoopUnit.finishMoves()

            # Fernangriff kostet nur der HI Gold
            if pPlayer.isHuman() and lUnits:
                if pPlayer.getCivilizationType() not in L.LFernangriffNoCosts:
                    iGold = 0
                    for unit in lUnits:
                        iUnitType = unit.getUnitType()
                        iUnitClass = unit.getUnitClassType()
                        iUnitCombat = unit.getUnitCombatType()
                        try:
                            iGold += L.DFernangriffCosts[iUnitClass]
                        except:
                            iGold += 2

                    if iGold > 0:
                        pPlayer.changeGold(-iGold)
                        CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_RANGE_ATTACK_COSTS", (iGold,)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Ranged Attack - Owner",eOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Wenn die Mission nicht ausgefuehrt werden soll
        # unit.getGroup().clearMissionQueue()

        #unit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, unit.plot(), unit)

        # if eMission == MissionTypes.MISSION_BOMBARD:
        #  CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Bombard - Owner",eOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if not self.__LOG_PUSH_MISSION:
            return
        CvUtil.pyPrint("Selection Group pushed mission %d" % (eMission))

    def onUnitMove(self, argsList):
        'unit move'
        pPlot, pUnit, pOldPlot = argsList

        # PAE Debug mark
        #"""
        #    if gc.getPlayer(pUnit.getOwner()).isHuman():
        #      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("X",pPlot.getX())), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Y",pPlot.getY())), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # ----------- Flucht Promotion (Flight/Escape)
        if not pUnit.canMove() or pUnit.getDamage() < 70:
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"), False)

        # ----------- Verletzte Schiffe / Seeeinheiten sollen langsamer werden, je verletzter sie sind
        # ----------- Beladene Schiffe sollen ebenfalls um 0.25 langsamer werden
        # ----------- Bewegung / Movement / Seewind / Fair wind
        if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA:
            # ------ Seewind -----
            if pPlot.getFeatureType() > -1:
                iPlotWind = pPlot.getFeatureType()
                if iPlotWind in L.LSeewind:
                    iUnitDirection = pUnit.getFacingDirection()

                    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("direction",iUnitDirection)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                    # 1 plot move = 60
                    # Ocean movement and feature movement cost = 1
                    # +1 Bewegung in Wind,...
                    iInWind = -60
                    iInSchraegWind = -30
                    iSeitenWind = 0
                    iGegenSchraegWind = 30
                    iGegenWind = 60
                    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION1")):
                        iSeitenWind = -30
                        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION2")):
                            iGegenSchraegWind = 0
                            iGegenWind = 30
                            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION3")):
                                iInSchraegWind = -60

                    lMoves = [
                        iGegenWind,
                        iGegenSchraegWind,
                        iSeitenWind,
                        iInSchraegWind,
                        iInWind,
                        iInSchraegWind,
                        iSeitenWind,
                        iGegenSchraegWind,
                    ]
                    iWindIdx = L.LSeewind.index(iPlotWind)
                    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("wind",lMoves[abs(iWindIdx-iUnitDirection)])), None, 2, None, ColorTypes(10), 0, 0, False, False)
                    pUnit.changeMoves(lMoves[abs(iWindIdx-iUnitDirection)])
            # -- end Wind

            # ------ Verletzte Schiffe
            iDamage = pUnit.getDamage()
            if iDamage > 10:
                pUnit.changeMoves(iDamage*3)
            # Beladene Schiffe
            iCargo = pUnit.getCargo()
            if iCargo > 0:
                pUnit.changeMoves(iCargo*10)

            # Workboats sink in unknown terrain (neutral or from other team): Chance 1:6
            if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_WORKBOAT"):
                if pPlot.getOwner() != pUnit.getOwner():
                    if CvUtil.myRandom(6, "WorkboatSink") == 1:
                        if gc.getPlayer(pUnit.getOwner()).isHuman():
                            CyInterface().addMessage(pUnit.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SINKING_SHIP", (pUnit.getName(),)), "AS2D_SINKING_W0RKBOAT", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                        # COMMAND_DELETE can cause CtD if used in onUnitMove()
                        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                        pUnit.kill(True, -1)
                        return

            # Schiffe auf Hoher See erleiden Sturmschaden
            elif pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_OCEAN") and pPlot.getFeatureType() == -1 and not pPlot.isCity():
                # Damage (100=tot)
                iSchaden = 20
                # iDamage von oben
                if iDamage <= 90 - iSchaden:
                    # Chance auf Schaden: 1:10 + Worldsize * x
                    # Worldsize: 0 (Duell) - 5 (Huge)
                    iChance = 10 + gc.getMap().getWorldSize() * 3
                    if CvUtil.myRandom(iChance, "Sturmschaden") == 1:
                        iDamage += iSchaden
                        pUnit.setDamage(iDamage, -1)
                        # Types of Damage (Messages)
                        # 0 = Storm
                        iRand = CvUtil.myRandom(6, "SturmschadenTyp")
                        if iRand == 0:
                            pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_SEESTURM"), 0)
                            if gc.getPlayer(pUnit.getOwner()).isHuman():
                                CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DAMAGE_SHIP_STORM", (pUnit.getName(), iSchaden)), "AS2D_UNIT_BUILD_GALLEY", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                        elif gc.getPlayer(pUnit.getOwner()).isHuman():
                            CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DAMAGE_SHIP_"+str(iRand), (pUnit.getName(), iSchaden)), "AS2D_UNIT_BUILD_GALLEY", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

        # --------------------------------------------------------------------- #
        # ------ BARBAREN ------------------------------------------------- #
        if pUnit.isBarbarian():
            # Seevoelkereinheit wird entladen, leere Seevoelkerschiffe werden gekillt
            if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SEEVOLK"):
                if not pUnit.hasCargo():
                    # COMMAND_DELETE can cause CtD if used in onUnitMove()
                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pUnit.kill(True, -1)
                    return
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Leeres Seevoelkerschiff gekillt (Zeile 2456)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                else:
                    if pOldPlot.getOwner() == -1 and pPlot.getOwner() != -1:
                        if gc.getPlayer(pPlot.getOwner()).isHuman():
                            CyInterface().addMessage(pPlot.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SEEVOLK_ALERT", ()), None, 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

            # Barbarische Tiere sollen keine Stadt betreten / Barbarian animals will be disbanded when moving into a city
            elif pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
                if pPlot.isCity():
                    # COMMAND_DELETE can cause CtD if used in onUnitMove()
                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pUnit.kill(True, -1)
                    return
            # Barbarische Emigranten stehen nur rum und benoetigen unnoetig Rechenzeit
            elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
                # COMMAND_DELETE can cause CtD if used in onUnitMove()
                # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                pUnit.kill(True, -1)
                return

        # --------------------------------------------------------------------- #
        # Handelskarren - Merchant can be robbed and killed
        if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT") and not pUnit.isBarbarian():
            if pPlot.getNumUnits() == 1 and pUnit.getOwner() != pPlot.getOwner() and not pPlot.isCity():

                barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                iBarbCities = barbPlayer.getNumCities()
                # Chance in %
                iMinimumChance = 2
                if iBarbCities > 10:
                    iChance = 4
                elif iBarbCities > 4:
                    iChance = 3
                else:
                    iChance = iMinimumChance

                iCalcChance = int(100/iChance)

                iRand = CvUtil.myRandom(iCalcChance, "Handelskarren ausgeraubt")
                if iRand == 1:
                    iPlayer = pUnit.getOwner()
                    if gc.getPlayer(iPlayer).isHuman():
                        iRand = CvUtil.myRandom(5, "Handelskarren ausgeraubt Text")
                        if iRand == 1:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_1", (0, 0))
                        elif iRand == 2:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_2", (0, 0))
                        elif iRand == 3:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_3", (0, 0))
                        elif iRand == 4:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_4", (0, 0))
                        else:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_0", (0, 0))
                        CyInterface().addMessage(iPlayer, True, 5, text, 'AS2D_UNITCAPTURE', 2, 'Art/Interface/Buttons/Units/button_merchant.dds', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    elif pPlot.getOwner() != -1:
                        if gc.getPlayer(pPlot.getOwner()).isHuman():
                            CyInterface().addMessage(pPlot.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_1_1", (gc.getPlayer(pUnit.getOwner()).getCivilizationAdjective(3), 0)), None, 2, "Art/Interface/Buttons/Units/button_merchant.dds", ColorTypes(14), pPlot.getX(), pPlot.getY(), True, True)

                    # Generelle Info zur Chance
                    text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_INFO", (iChance, iMinimumChance))
                    CyInterface().addMessage(iPlayer, True, 5, text, None, 2, None, ColorTypes(13), 0, 0, False, False)

                    # PAE Trade: Einheit leeren
                    CvUtil.removeScriptData(pUnit, "b")

                    # Einheit killen
                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    # pUnit = None
                    # Merchants gets barbarian: 50:50
                    # if pPlot.getNumUnits() == 0:
                    #  iRand = CvUtil.myRandom(2, "Merchant gets barbarian")
                    #  if iRand == 1:
                    #    barbPlayer.initUnit(gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Haendler verschwunden (Zeile 2530)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


        # ------ Hunnen - Bewegung / Huns movement ------ #
        # verschachtelte ifs zwecks optimaler laufzeit
        if pUnit.isBarbarian():
            if pPlot.getOwner() != pOldPlot.getOwner() and pPlot.getOwner() != -1:
                iPlayer = pPlot.getOwner()
                iHunType = gc.getInfoTypeForString("UNIT_MONGOL_KESHIK")
                if gc.getBARBARIAN_PLAYER() != iPlayer and pUnit.getUnitType() == iHunType:
                    pUnit.finishMoves()
                    if gc.getPlayer(iPlayer).getGold() > 100:

                        # Human PopUp
                        if gc.getPlayer(iPlayer).isHuman():
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_HUNS", ()))
                            popupInfo.setData1(iPlayer)
                            popupInfo.setData2(pUnit.getID())
                            popupInfo.setOnClickedPythonCallback("popupHunsPayment")  # EntryPoints/CvScreenInterface und CvGameUtils
                            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_HUNS_NO", ()), "")
                            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_HUNS_YES", ()), "")
                            popupInfo.addPopup(iPlayer)
                        else:
                            # AI
                            # Bis zu 2 Einheit pro Hunne 100
                            # Bis zu 3 Einheiten pro Hunne 50:50
                            # Ab 3 Einheiten pro Hunne 0
                            iPlayerUnits = 0
                            iHunUnits = 0
                            for i in range(7):
                                for j in range(7):
                                    sPlot = gc.getMap().plot(pPlot.getX() + i - 3, pPlot.getY() + j - 3)
                                    iRange = sPlot.getNumUnits()
                                    for k in range(iRange):
                                        if sPlot.getUnit(k).getOwner() == iPlayer and sPlot.getUnit(k).canAttack():
                                            iPlayerUnits += 1
                                        if sPlot.getUnit(k).isBarbarian() and sPlot.getUnit(k).getUnitType() == iHunType:
                                            iHunUnits += 1

                            if iPlayerUnits > iHunUnits * 3:
                                iRand = 0  # kein effekt
                            elif iPlayerUnits > iHunUnits * 2:
                                iRand = CvUtil.myRandom(2, "Hunnen Schutzgeld")
                                if iRand < 1:
                                    gc.getPlayer(iPlayer).changeGold(-100)
                                    # COMMAND_DELETE can cause CtD if used in onUnitMove()
                                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                                    pUnit.kill(True, -1)
                                    pUnit = None
                            else:
                                gc.getPlayer(iPlayer).changeGold(-100)
                                # COMMAND_DELETE can cause CtD if used in onUnitMove()
                                # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                                pUnit.kill(True, -1)
                                pUnit = None

                    elif gc.getPlayer(iPlayer).isHuman():
                        CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_POPUP_HUNS_NO_MONEY", ()), None, 2, pUnit.getButton(), ColorTypes(10), pPlot.getX(), pPlot.getY(), True, True)

        # In der Stadt
        if pPlot.isCity():
            pCity = pPlot.getPlotCity()

            # Unit can stop city revolt / unit city revolt
            if pCity.getOccupationTimer() > 2:
                if pUnit.isMilitaryHappiness():
                    # if pUnit.getOwner() == pCity.getOwner():  # -> allies can help ;)
                    # if pPlot.getNumUnits() > pCity.getPopulation():
                    # if pUnit.movesLeft() <= 20:
                    if PyInfo.UnitInfo(pUnit.getUnitType()).getMoves() == 1:
                        pCity.changeOccupationTimer(-1)

            # Keine Formationen in der Stadt (rausgegeben ab PAE V Patch 2, Formationen sind auf Stadtangriff/verteidigung angepasst)
            #PAE_Unit.doUnitFormation (pUnit, -1)

        # nicht eine Stadt
        else:
            # AI Festungsformation
            iAnzahlFortifiedUnits = 2
            if not gc.getPlayer(pUnit.getOwner()).isHuman():
                iImp = pPlot.getImprovementType()

                # Bei einem Turm2 oder einer Festung1,2 oder einem Limeskastell
                if iImp in L.LImprFortShort:
                        # Alle Formationen entfernen
                        #PAE_Unit.doUnitFormation (pUnit, -1)

                        # Plot soll der AI (Unit) oder niemandem zugewiesen sein
                    if pPlot.getOwner() == pUnit.getOwner() or pPlot.getOwner() == -1:
                        # Nur fuer Axt, Speer und Schwerteinheiten
                        if pUnit.getUnitCombatType() in L.LMeleeCombats:
                            if PyInfo.UnitInfo(pUnit.getUnitType()).getMoves() == 1:
                                iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
                            else:
                                iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
                            iRange = pPlot.getNumUnits()
                            iNum = 0
                            k = 0
                            for k in range(iRange):
                                if pPlot.getUnit(k).isHasPromotion(iPromo):
                                    iNum += 1
                                if iNum > iAnzahlFortifiedUnits:
                                    break
                            if iNum < iAnzahlFortifiedUnits:
                                PAE_Unit.doUnitFormation(pUnit, iPromo)

            # Keine Formation in bestimmte Features
            #iFeat = pPlot.getFeatureType()
            # if iFeat > -1:
            #  if iFeat == gc.getInfoTypeForString("FEATURE_FOREST") or iFeat == gc.getInfoTypeForString("FEATURE_DICHTERWALD") or iFeat == gc.getInfoTypeForString("FEATURE_JUNGLE"):
            #    PAE_Unit.doUnitFormation (pUnit, -1)

        ########################################################
        # --------- Bombard - Feature ----------------------
        # Wird ein Fort mit Katapulten bombardiert, kann das Fort dadurch zerstoert werden: 10%
        #    iUnit1 = gc.getInfoTypeForString("UNIT_CATAPULT")
        #    iUnit2 = gc.getInfoTypeForString("UNIT_FIRE_CATAPULT")
        #    if pUnit.getUnitType() == iUnit1 or pUnit.getUnitType() == iUnit2:
        #      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # PAE Debug Mark
        #"""
        if not self.__LOG_MOVEMENT:
            return
        elif not pUnit.isDead():
            player = PyPlayer(pUnit.getOwner())
            unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
            if player and unitInfo:
                CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d'
                               % (player.getID(), player.getCivilizationName(), unitInfo.getDescription(),
                                  pUnit.getX(), pUnit.getY()))

    def onUnitSetXY(self, argsList):
        'units xy coords set manually'
        pPlot, pUnit = argsList
        player = PyPlayer(pUnit.getOwner())
        unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
        if not self.__LOG_MOVEMENT:
            return

    def onUnitCreated(self, argsList):
        'Unit Completed'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        unit = argsList[0]
        player = PyPlayer(unit.getOwner())
        if not self.__LOG_UNITBUILD:
            return

    # Global
    def onUnitBuilt(self, argsList):
        'Unit Completed'
        city = argsList[0]
        unit = argsList[1]
        iPlayer = city.getOwner()
        player = PyPlayer(iPlayer)
        pPlayer = gc.getPlayer(iPlayer)
        iUnitType = unit.getUnitType()
        # PAE Debug Mark
        #"""

        # ++++ AI - Unit Built/Created
        if not pPlayer.isHuman():
            # PAE V: Pirate feature - disabled cause of possible OOS when too many active AI pirates
            # if unit.getDomainType() == gc.getInfoTypeForString("DOMAIN_SEA"):
                # PAE_Unit.convertToPirate(city, unit):

            # Stadtverteidiger
            iNum = 0
            if iUnitType in L.LBuildArchers or iUnitType in L.LBuildCatapults:
                pPlot = city.plot()
                iRange = pPlot.getNumUnits()
                for i in range(iRange):
                    pLoopUnit = pPlot.getUnit(i)
                    if pLoopUnit is not None and not pLoopUnit.isNone():
                        if pLoopUnit.getUnitType() == iUnitType and pLoopUnit.getOwner() == iPlayer:
                            iNum += 1
                # UnitAIType 10 = UNITAI_CITY_DEFENSE
                if (iUnitType in L.LBuildArchers and iNum < 3 or
                    iUnitType in L.LBuildCatapults and iNum < 2):
                    unit.setUnitAIType(10)
            # Set offensive Formations
            else:
                PAE_Unit.doAIUnitFormations(unit, True, False, False)

            # Handicap: 0 (Settler) - 8 (Deity) ; 5 = King
            iHandicap = gc.getGame().getHandicapType()
            # 2nd Settler for AI (Immortal, Deity) (PAE V)
            if iHandicap >= 7 and iUnitType == gc.getInfoTypeForString("UNIT_SETTLER"):
                CvUtil.spawnUnit(iUnitType, city.plot(), pPlayer)

            # Experienced units on higher handicap level (PAE V Patch 3)
            if iHandicap >= 5:
                if unit.isMilitaryHappiness() or unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                    lPromos = []
                    lPromos.append(-1)
                    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT1"))
                    if iHandicap >= 6:
                        lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT2"))
                    if iHandicap >= 7:
                        lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT3"))
                    if iHandicap >= 8:
                        lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT4"))

                    iRange = len(lPromos)
                    iRand = CvUtil.myRandom(iRange, "PromoBonus high handicap")
                    if iRand > 0:
                        for i in range(iRange):
                            if i > 0 and i <= iRand:
                                unit.setHasPromotion(lPromos[i], True)

        # Log Message (BTS)
        CvAdvisorUtils.unitBuiltFeats(city, unit)

        # ++++ Versorger / Supply Unit
        if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
            PAE_Unit.initSupply(unit)

        # ++++ Auswanderer (Emigrants), die die Stadtbevoelkerung senken
        # deaktiviert, weil Emigrant nicht mehr absichtlich baubar
        # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
            # PAE_City.onEmigrantBuilt(city, unit)

        # ++++ Bronze-Feature / Wald roden / Waldrodung / Abholzung / Desertifizierung / betrifft nicht die Barbarenstaedte
        if iPlayer != gc.getBARBARIAN_PLAYER():
            PAE_City.doDesertification(city, unit)

        # PAE Unit Auto Promotions
        if gc.getUnitInfo(iUnitType).getCombat() > 0:
            if unit.getDomainType() == DomainTypes.DOMAIN_SEA:
                if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                    if iUnitType != gc.getInfoTypeForString("UNIT_WORKBOAT"):
                        PAE_Unit.doCityUnitPromotions4Ships(city, unit)
            else:
                PAE_Unit.doCityUnitPromotions(city, unit)
                try:
                    iBuilding = L.DManufakturen[unit.getUnitCombatType()]
                    if city.isHasBuilding(iBuilding):
                        CvUtil.spawnUnit(iUnitType, city.plot(), pPlayer)
                except KeyError:
                    pass

        # PAE V: Mercenary promotion
        if iPlayer != city.getOriginalOwner():
            if city.getPopulation() < 9:
                if city.plot().calculateCulturePercent(iPlayer) < 75:
                    if unit.isMilitaryHappiness() or unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                        unit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY"), True)

        # Blessed Units
        iBuilding = gc.getInfoTypeForString("BUILDING_CHRISTIAN_CATHEDRAL")
        if city.isHasBuilding(iBuilding):
            # Chance: 25% a unit gets blessed
            if CvUtil.myRandom(4, "unit_gets_blessed") == 1:
                unit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_BLESSED"), True)

        # PAE Debug Mark
        #"""

        if not self.__LOG_UNITBUILD:
            return
        CvUtil.pyPrint('%s was finished by Player %d Civilization %s' %(unit.getName(), player.getID(), player.getCivilizationName()))

    # nicht global?
    def onUnitKilled(self, argsList):
        'Unit Killed'
        unit, iAttacker = argsList

        player = PyPlayer(unit.getOwner())
        attacker = PyPlayer(iAttacker)

        if not self.__LOG_UNITKILLED:
            return
        CvUtil.pyPrint(u'Player %d Civilization %s Unit %s was killed by Player %d' % (player.getID(), player.getCivilizationName(), unit.getName(), attacker.getID()))

    def onUnitLost(self, argsList):
        'Unit Lost'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        if not self.__LOG_UNITLOST:
            return
        unit = argsList[0]
        player = PyPlayer(unit.getOwner())
        CvUtil.pyPrint('%s was lost by Player %d Civilization %s' % (PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))

    def onUnitPromoted(self, argsList):
        'Unit Promoted'
        if not self.__LOG_UNITPROMOTED:
            return
        pUnit, iPromotion = argsList
        player = PyPlayer(pUnit.getOwner())
        CvUtil.pyPrint('Unit Promotion Event: %s - %s' %(player.getCivilizationName(), pUnit.getName(),))

    def onUnitSelected(self, argsList):
        'Unit Selected'
        pUnit = argsList[0]

        if not gc.getPlayer(pUnit.getOwner()).isHuman():
            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")):
                if pUnit.plot().getImprovementType() not in L.LImprFortShort:
                    pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"), False)
                    pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"), False)

        if not self.__LOG_UNITSELECTED:
            return
        player = PyPlayer(pUnit.getOwner())
        CvUtil.pyPrint('%s was selected by Player %d Civilization %s' %(pUnit.getName(), player.getID(), player.getCivilizationName()))

    def onUnitRename(self, argsList):
        'Unit is renamed'
        pUnit = argsList[0]
        if pUnit.getOwner() == gc.getGame().getActivePlayer():
            self.__eventEditUnitNameBegin(pUnit)

    # global
    def onUnitPillage(self, argsList):
        'Unit pillages a plot'
        pUnit, iImprovement, iRoute, iOwner = argsList
        iPlotX = pUnit.getX()
        iPlotY = pUnit.getY()
        pPlot = pUnit.plot()
        iPlayer = pUnit.getOwner()
        # PAE Debug Mark
        #"""
        if iImprovement > -1:
            # XP nur bei enemy plots
            if pPlot.getOwner() != iPlayer:
                pUnit.changeExperience(1, -1, 0, 0, 0)

            # Versorger aufladen / Supply Wagon recharge
            lHealer = []
            iRange = pPlot.getNumUnits()
            for iUnit in range(iRange):
                pLoopUnit = pPlot.getUnit(iUnit)
                if pLoopUnit.getOwner() == iPlayer:
                    if pLoopUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                        lHealer.append(pLoopUnit)

            if lHealer:
                iSupplyChange = 0
                try:
                    iSupplyChange = L.DImprSupplyBonus[iImprovement]
                    for loopUnit in lHealer:
                        if iSupplyChange <= 0:
                            break
                        iSupplyChange = PAE_Unit.fillSupply(loopUnit, iSupplyChange)
                except KeyError:
                    pass
            # -----------------

            # Free promotion when pillaging: 20%
            if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE5")):
                if CvUtil.myRandom(10, "pillage_promo") < 2:
                    for iPromo in L.LPromoPillage:
                        if not pUnit.isHasPromotion(iPromo):
                            pUnit.setHasPromotion(iPromo, True)
                            if gc.getPlayer(iPlayer).isHuman():
                                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION", (pUnit.getName(), gc.getPromotionInfo(iPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iPromo).getButton(), ColorTypes(13), iPlotX, iPlotY, True, True)
                            break

            # Feldsklaven und Minensklaven checken
            if iImprovement != gc.getInfoTypeForString("IMPROVEMENT_FISHING_BOATS"):
                PAE_Sklaven.doCheckSlavesAfterPillage(pUnit, pPlot)

            # Handelsposten: Plot-ScriptData leeren
            if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):
                CvUtil.removeScriptData(pPlot, "p")

            # Unit soll sich nachher nicht mehr fortbewegen koennen
            pUnit.finishMoves()
        # PAE Debug Mark
        #"""

        if not self.__LOG_UNITPILLAGE:
            return
        CvUtil.pyPrint("Player %d's %s pillaged improvement %d and route %d at plot at (%d, %d)" %(iOwner, pUnit.getName(), iImprovement, iRoute, iPlotX, iPlotY))

    def onUnitSpreadReligionAttempt(self, argsList):
        'Unit tries to spread religion to a city'
        pUnit, iReligion, bSuccess = argsList

    def onUnitGifted(self, argsList):
        'Unit is gifted from one player to another'
        pUnit, iGiftingPlayer, pPlotLocation = argsList

    def onUnitBuildImprovement(self, argsList):
        'Unit begins enacting a Build (building an Improvement or Route)'
        pUnit, iBuild, bFinished = argsList

        # Holzcamp entfernen, wenn Wald entfernt wurde
        if bFinished:
            if iBuild in L.LWoodRemovedByLumberCamp:
                pPlot = pUnit.plot()
                if pPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP"):
                    pPlot.setImprovementType(-1)

            # Sklaven koennen bei einem Bauprojekt sterben / Slaves can die during an improvment construction
            if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                # Chance of unit dying 3%
                iRand = CvUtil.myRandom(33, "slave dying onBuildImprovement")
                if iRand == 1:
                    iOwner = pUnit.getOwner()
                    if gc.getPlayer(iOwner).isHuman():
                        iRand = CvUtil.myRandom(10, "slave dying text")
                        CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DYING_SLAVES_"+str(iRand), (0, 0)), 'AS2D_UNITCAPTURE', 2, 'Art/Interface/Buttons/Units/button_slave.dds', ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
                    # COMMAND_DELETE can cause CtD if used in onUnitBuildImprovement()
                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pUnit.kill(True, -1)  # RAMK_CTD
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave gestorben (Zeile 3766)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    def onGoodyReceived(self, argsList):
        'Goody received'
        iPlayer, pPlot, pUnit, iGoodyType = argsList
        if not self.__LOG_GOODYRECEIVED:
            return
        CvUtil.pyPrint('%s received a goody' %(gc.getPlayer(iPlayer).getCivilizationDescription(0)),)

    def onGreatPersonBorn(self, argsList):
        ## Platy WorldBuilder ##
        # if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
        ## Platy WorldBuilder ##
        'Great Person Born'
        pUnit, iPlayer, pCity = argsList
        pPlayer = gc.getPlayer(iPlayer)
        if pUnit.isNone() or pCity.isNone():
            return

        # Names for Great Generals / Feldherrenliste
        if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_GREAT_GENERAL"):
            try:
                listNames = L.DGGNames[pPlayer.getCivilizationType()]
            except KeyError:
                listNames = L.LGGStandard

            GG_Name = ""
            i = 0
            listlength = len(listNames)
            while i < listlength:
                i += 1
                iRand = CvUtil.myRandom(listlength, "GGNames first try")
                if listNames[iRand] not in self.GG_UsedNames:
                    GG_Name = listNames[iRand]
                    self.GG_UsedNames.append(listNames[iRand])
                    break

            if GG_Name == "":
                iRand = CvUtil.myRandom(len(L.LGGStandard), "GGNames second try")
                GG_Name = L.LGGStandard[iRand]

            if GG_Name != "":
                pUnit.setName(GG_Name)

                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GREAT_GENERAL_BORN", (GG_Name, pCity.getName())), 'NONE', 2, pUnit.getButton(), ColorTypes(11), pUnit.getX(), pUnit.getY(), True, True)

        if not self.__LOG_GREATPERSON:
            return
        CvUtil.pyPrint('A %s was born for %s in %s' %(pUnit.getName(), pPlayer.getCivilizationDescription(0), pCity.getName()))

    def onTechAcquired(self, argsList):
        'Tech Acquired'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iTechType, iTeam, iPlayer, bAnnounce = argsList
        # Note that iPlayer may be NULL (-1) and not a refer to a player object
        if iPlayer == -1:
            return

        pPlayer = gc.getPlayer(iPlayer)
        # Show tech splash when applicable
        if bAnnounce and not CyInterface().noTechSplash():
            if gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode():
                #if not gc.getGame().isNetworkMultiPlayer() and iPlayer == gc.getGame().getActivePlayer():
                if pPlayer.isHuman():
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(iTechType)
                    popupInfo.setText(u"showTechSplash")
                    popupInfo.addPopup(iPlayer)

        # Trait Creative: Bei Alphabet in jede Stadt Trait-Gebaeude setzen
        if iTechType == gc.getInfoTypeForString("TECH_ALPHABET") and pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")):
            (loopCity, pIter) = pPlayer.firstCity(False)
            iBuilding = gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_LOCAL")
            while loopCity:
                if not loopCity.isNone() and loopCity.getOwner() == pPlayer.getID(): #only valid cities
                    loopCity.setNumRealBuilding(iBuilding, 1)
                (loopCity, pIter) = pPlayer.nextCity(pIter, False)

        # freier Siedler fuer die KI ab Emperor
        if gc.getGame().getHandicapType() > 5 and not pPlayer.isHuman():
            PAE_City.doFreeTechSettler(iTechType, pPlayer)

        # Tech und freie Einheit / Free Unit
        PAE_City.doFreeTechMissionary(iTechType, iPlayer)

        # Heresy ---------------------
        # if iPlayer > -1 and iTechType == gc.getInfoTypeForString("TECH_HERESY"):

        # lCities = PyPlayer(iPlayer).getCityList()

        # iRangeCities = len(lCities)
        # for i in range(iRangeCities):
            # pCity = pPlayer.getCity(lCities[i].getID())

            # # Kulte
            # iReliHindu = gc.getInfoTypeForString("RELIGION_HINDUISM")
            # iCorpIndra = gc.getInfoTypeForString("CORPORATION_9")

            # iRange = gc.getNumCorporationInfos()
            # iRange2 = gc.getNumBuildingInfos()
            # for iCorp in range(iRange):
              # if pCity.isHasCorporation(iCorp):
                # if not ( iCorp == iCorpIndra and pCity.isHasReligion(iReliHindu) ):
                  # for i in range(iRange2):
                    # if pCity.getNumBuilding(i) > 0:
                      # thisBuilding = gc.getBuildingInfo(i)
                      # if thisBuilding.getPrereqCorporation() == iCorp or thisBuilding.getFoundsCorporation() == iCorp:
                        # pCity.setNumRealBuilding(i,0)
                  # pCity.setHasCorporation(iCorp, 0, 0, 0)

            # iRange = gc.getNumReligionInfos()
            # iRange2 = gc.getNumBuildingInfos()
            # for iReli in range(iRange):
              # if iReli not in L.LRelis:
                # if pCity.isHasReligion(iReli) and not pCity.isHolyCityByType(iReli):
                  # for i in range(iRange2):
                    # if pCity.getNumBuilding(i) > 0:
                      # thisBuilding = gc.getBuildingInfo(i)
                      # if thisBuilding.getPrereqReligion() == iReli or thisBuilding.getHolyCity() == iReli:
                        # pCity.setNumRealBuilding(i,0)
                  # pCity.setHasReligion(iReli, 0, 0, 0)

        # # Meldung (PopUp)
        # if gc.getPlayer(iPlayer).isHuman():
          # popupInfo = CyPopupInfo()
          # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HERESY_DARK_AGE_POPUP",("", )))
          # popupInfo.addPopup(iPlayer)
    # """
        # ---------------------------------------------------------

        if not self.__LOG_TECH:
            return
        CvUtil.pyPrint('%s was finished by Team %d' %(PyInfo.TechnologyInfo(iTechType).getDescription(), iTeam))


    def onTechSelected(self, argsList):
        'Tech Selected'
        iTechType, iPlayer = argsList
        if not self.__LOG_TECH:
            return
        CvUtil.pyPrint('%s was selected by Player %d' %(PyInfo.TechnologyInfo(iTechType).getDescription(), iPlayer))

    def onReligionFounded(self, argsList):
        'Religion Founded'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iReligion, iFounder = argsList
        player = PyPlayer(iFounder)
        iCityId = gc.getGame().getHolyCity(iReligion).getID()

        # PAE - capital gets Holy City for certain religions
        if iReligion in L.LRelisRemapCapital:
            pCapitalCity = gc.getPlayer(iFounder).getCapitalCity()
            if pCapitalCity:
                if iCityId != pCapitalCity.getID():
                    gc.getGame().getHolyCity(iReligion).setHasReligion(iReligion, 0, 0, 0)
                    gc.getGame().setHolyCity(iReligion, pCapitalCity, 0)
                    iCityId = pCapitalCity.getID()

        # BTS
        if gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode():
            if gc.getPlayer(iFounder).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iReligion)
                popupInfo.setData2(iCityId)
                popupInfo.setData3(1)
                popupInfo.setText(u"showWonderMovie")
                popupInfo.addPopup(iFounder)

        if not self.__LOG_RELIGION:
            return
        CvUtil.pyPrint('Player %d Civilization %s has founded %s'
                       % (iFounder, player.getCivilizationName(), gc.getReligionInfo(iReligion).getDescription()))

    def onReligionSpread(self, argsList):
        'Religion Has Spread to a City'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iReligion, iOwner, pSpreadCity = argsList
        player = PyPlayer(iOwner)
        if not self.__LOG_RELIGIONSPREAD:
            return
        CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
                       % (gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

    def onReligionRemove(self, argsList):
        'Religion Has been removed from a City'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iReligion, iOwner, pRemoveCity = argsList
        player = PyPlayer(iOwner)
        if not self.__LOG_RELIGIONSPREAD:
            return
        CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
                       % (gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

    def onCorporationFounded(self, argsList):
        'Corporation Founded'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iCorporation, iFounder = argsList
        player = PyPlayer(iFounder)

        # Clear cult headquarter
        CyGame().clearHeadquarters(iCorporation)

        if not self.__LOG_RELIGION:
            return
        CvUtil.pyPrint('Player %d Civilization %s has founded %s'
                       % (iFounder, player.getCivilizationName(), gc.getCorporationInfo(iCorporation).getDescription()))

    def onCorporationSpread(self, argsList):
        'Corporation Has Spread to a City'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iCorporation, iOwner, pSpreadCity = argsList
        player = PyPlayer(iOwner)
        if not self.__LOG_RELIGIONSPREAD:
            return
        CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
                       % (gc.getCorporationInfo(iCorporation).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

    def onCorporationRemove(self, argsList):
        'Corporation Has been removed from a City'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iCorporation, iOwner, pRemoveCity = argsList
        player = PyPlayer(iOwner)
        if not self.__LOG_RELIGIONSPREAD:
            return
        CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
                       % (gc.getCorporationInfo(iCorporation).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

    def onGoldenAge(self, argsList):
        'Golden Age'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iPlayer = argsList[0]
        player = PyPlayer(iPlayer)
        if not self.__LOG_GOLDENAGE:
            return
        CvUtil.pyPrint('Player %d Civilization %s has begun a golden age'
                       % (iPlayer, player.getCivilizationName()))

    def onEndGoldenAge(self, argsList):
        'End Golden Age'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iPlayer = argsList[0]
        player = PyPlayer(iPlayer)
        if not self.__LOG_ENDGOLDENAGE:
            return
        CvUtil.pyPrint('Player %d Civilization %s golden age has ended'
                       % (iPlayer, player.getCivilizationName()))

    def onChangeWar(self, argsList):
        'War Status Changes'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        bIsWar = argsList[0]
        iTeam = argsList[1]
        iRivalTeam = argsList[2]
        if not self.__LOG_WARPEACE:
            return
        if bIsWar:
            strStatus = "declared war"
        else:
            strStatus = "declared peace"
        CvUtil.pyPrint('Team %d has %s on Team %d'
                       % (iTeam, strStatus, iRivalTeam))

    def onChat(self, argsList):
        'Chat Message Event'
        chatMessage = "%s" % (argsList[0],)

    def onSetPlayerAlive(self, argsList):
        'Set Player Alive Event'
        iPlayerID = argsList[0]
        bNewValue = argsList[1]
        CvUtil.pyPrint("Player %d's alive status set to: %d" % (iPlayerID, int(bNewValue)))

    def onPlayerChangeStateReligion(self, argsList):
        'Player changes his state religion'
        iPlayer, iNewReligion, iOldReligion = argsList

    def onPlayerGoldTrade(self, argsList):
        'Player Trades gold to another player'
        iFromPlayer, iToPlayer, iGoldAmount = argsList

    def onCityBuilt(self, argsList):
        'City Built'
        city = argsList[0]
        if city.getOwner() == gc.getGame().getActivePlayer():
            ## AI AutoPlay ##
            if CyGame().getAIAutoPlay() == 0 and not CyGame().GetWorldBuilderMode():
                self.__eventEditCityNameBegin(city, False)
            ## AI AutoPlay ##
            #self.__eventEditCityNameBegin(city, False)
        CvUtil.pyPrint('City Built Event: %s' % (city.getName()))

        # Kolonie / Provinz ----------
        # Stadt bekommt automatisch das Koloniegebaeude und Trait-Gebaeude
        PAE_City.doCheckCityState(city)
        PAE_City.doCheckTraitBuildings(city)
        PAE_City.doCheckGlobalTraitBuildings(city.getOwner())
        # ----------------------------

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Neue Kolonie (Zeile 3041)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    def onCityRazed(self, argsList):
        'City Razed'
        city, iPlayer = argsList
        pPlayer = gc.getPlayer(iPlayer)
        #### Message - Wonder capturing ####
        if city.getNumWorldWonders() > 0:
            iRange = gc.getNumBuildingInfos()
            iRange2 = gc.getMAX_PLAYERS()
            for i in range(iRange):
                thisBuilding = gc.getBuildingInfo(i)
                if city.getNumBuilding(i) > 0:
                    iBuildingClass = thisBuilding.getBuildingClassType()
                    thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
                    if thisBuildingClass.getMaxGlobalInstances() == 1:
                        iConquerTeam = pPlayer.getTeam()
                        ConquerName = pPlayer.getName()
                        WonderName = thisBuilding.getDescription()
                        iX = city.getX()
                        iY = city.getY()
                        for iThisPlayer in range(iRange2):
                            ThisPlayer = gc.getPlayer(iThisPlayer)
                            iThisTeam = ThisPlayer.getTeam()
                            ThisTeam = gc.getTeam(iThisTeam)
                            if ThisTeam.isHasMet(iConquerTeam) and ThisPlayer.isHuman():
                                if iThisPlayer == iPlayer:
                                    CyInterface().addMessage(iThisPlayer, False, 10, CyTranslator().getText("TXT_KEY_WONDER_RAZED_YOU", (ConquerName, WonderName)), '', 0, thisBuilding.getButton(), ColorTypes(7), iX, iY, True, True)
                                else:
                                    CyInterface().addMessage(iThisPlayer, False, 10, CyTranslator().getText("TXT_KEY_WONDER_RAZED", (ConquerName, WonderName)), '', 0, thisBuilding.getButton(), ColorTypes(7), iX, iY, True, True)

        # -- Owner auslesen
        iOwner = city.findHighestCulture()
        if iOwner == -1:
            iOwner = city.getOriginalOwner()
        pOwner = gc.getPlayer(iOwner)
        # - Slaves (iRand = City Population) + settled slaves and glads (Angesiedelte Sklaven und Gladiatoren erobern)
        iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
        iThisTeam = pPlayer.getTeam()
        team = gc.getTeam(iThisTeam)
        if team.isHasTech(iTechEnslavement):
            iSlaves = city.getPopulation()
            for _ in range(iSlaves):
                CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  city.plot(), pPlayer)

            if pPlayer.isHuman():
                if iSlaves == 1:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_1", (0, 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
                else:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_2", (iSlaves, 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            elif pOwner.isHuman():
                if iSlaves == 1:
                    CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_3", (city.getName(), 0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                else:
                    CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_4", (city.getName(), iSlaves)), None, 2, None, ColorTypes(7), 0, 0, False, False)

        if pOwner.isAlive():
            # - Nearest city revolts
            if iOwner > -1 and iOwner != iPlayer:
                PAE_City.doNextCityRevolt(city.getX(), city.getY(), iOwner, iPlayer)

        # --- Partisans!
        #    if city.canConscript():
        # Seek Plots
            rebelPlotArray = []
            PartisanPlot1 = []
            PartisanPlot2 = []
            iX = city.getX()
            iY = city.getY()
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
                if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                    if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                        if loopPlot.isHills():
                            PartisanPlot1.append(loopPlot)
                        else:
                            PartisanPlot2.append(loopPlot)
            if PartisanPlot1:
                rebelPlotArray = PartisanPlot1
            else:
                rebelPlotArray = PartisanPlot2

            # Set Partisans
            if rebelPlotArray:
                eCiv = gc.getCivilizationInfo(pOwner.getCivilizationType())
                iUnit1 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SCHILDTRAEGER"))
                iUnit2 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AXEMAN"))
                iUnit3 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AXEWARRIOR"))
                iUnit4 = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_WARRIOR"))
                pOwnerTeam = gc.getTeam(pOwner.getTeam())
                if pOwnerTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")) and city.canTrain(iUnit1, 0, 0):
                    iUnitType = iUnit1
                elif pOwnerTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")) and city.canTrain(iUnit2, 0, 0):
                    iUnitType = iUnit2
                elif pOwnerTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG")):
                    iUnitType = iUnit3
                else:
                    iUnitType = iUnit4

                iAnzahl = CvUtil.myRandom(city.getPopulation() - 1, "Number of Partisans") + 1
                for _ in range(iAnzahl):
                    iPlot = CvUtil.myRandom(len(rebelPlotArray), "PartisanPlot")
                    pUnit = pOwner.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                    iDamage = CvUtil.myRandom(50, "Partisan damage")
                    pUnit.setDamage(iDamage, iOwner)

        CvUtil.pyPrint("City Razed Event: %s" % (city.getName(),))

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadt razed (Zeile 3116)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    def onCityAcquired(self, argsList):
        'City Acquired'
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        iPreviousOwner, iNewOwner, pCity, bConquest, bTrade = argsList
        CvUtil.pyPrint('City Acquired Event: %s' % (pCity.getName()))
        pPlayer = gc.getPlayer(iNewOwner)
        pPreviousOwner = gc.getPlayer(iPreviousOwner)
        # pPlot = pCity.plot()

        # PAE Debug Mark
        #"""

        # Trait-Gebaeude anpassen
        PAE_City.doCheckTraitBuildings(pCity)
        PAE_City.doCheckGlobalTraitBuildings(iNewOwner, pCity, iPreviousOwner)

        # Assimilation Tech (PAE V Patch 4)
        bAssimilation = gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ASSIMILATION"))

        # Szenarien
        sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S", "t"])
        if sScenarioName == "FirstPunicWar":
            FirstPunicWar.onCityAcquired(pCity, iNewOwner)

        # PAE triumph movies when city is reconquered
        if pPlayer.isHuman():
            if pCity.getOriginalOwner() == iNewOwner:
                if pPlayer.getCurrentEra() > 2:
                    iVids = 3
                elif pPlayer.getCurrentEra() > 1:
                    iVids = 2
                else:
                    iVids = 1
                # GG dying movies starts at no 3 (CvWonderMovieScreen)
                iMovie = 1 + CvUtil.myRandom(iVids, "GG dying movie selection")

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iMovie)  # dynamicID in CvWonderMovieScreen
                popupInfo.setData2(-1)  # fix pCity.getID()
                popupInfo.setData3(5)  # fix PAE Movie ID for reconquering cities
                popupInfo.setText(u"showWonderMovie")
                popupInfo.addPopup(iNewOwner)


        # ------- Stadtnamenswechsel: Rename barbarian tribes (cities) B(xy) to C(xy)
        if pCity.getOriginalOwner() == gc.getBARBARIAN_PLAYER() or iPreviousOwner == gc.getBARBARIAN_PLAYER():
            # get all city names (if AI has already founded that city)
            lCityNames = []
            iRange = gc.getMAX_PLAYERS()
            for i in range(iRange):
                pP = gc.getPlayer(i)
                iNumCities = pP.getNumCities()
                for j in range(iNumCities):
                    lCityNames.append(pP.getCity(j).getName())

            NewCityName = ""
            # range a,b: a <= x < b (!)
            for i in range(1, 138):
                if i < 10:
                    zus = "0" + str(i)
                else:
                    zus = str(i)

                BarbCityName = CyTranslator().getText("TXT_KEY_CITY_NAME_B" + zus, ())
                if pCity.getName() == BarbCityName:
                    NewCityName = CyTranslator().getText("TXT_KEY_CITY_NAME_C" + zus, ())
                    if NewCityName != "" and NewCityName != "NONE":
                        if NewCityName not in lCityNames:
                            pCity.setName(NewCityName, 0)
                    break

            # Rename City to CityNameList when there is no B->C entry
            # Nicht bei Szenarien verwenden (sScenarioName wird ganz oben initialisiert)
            if NewCityName == "" and sScenarioName == "":
                pCity.setName(pPlayer.getNewCityName(), 0)

        PAE_City.correctCityBuildings(pCity, pPlayer, pPreviousOwner)

        # ------- Create partisans and slaves, catch great people (only during active war), nearest city riots
        if gc.getTeam(pPreviousOwner.getTeam()).isAtWar(pPlayer.getTeam()):
            # --- Partisans!
            if not bAssimilation and (not bTrade or bConquest) and not pPlayer.isBarbarian() and pPreviousOwner.isAlive():
                PAE_City.doPartisans(pCity, iPreviousOwner)

            if not bAssimilation:
                # --- Slaves (max num = City Population)
                PAE_City.doCaptureSlaves(pCity, iNewOwner, iPreviousOwner)
                # ---- Settled slaves -> Freed Slaves (Befreite Sklaven)
                PAE_Sklaven.freeSlaves(pCity, pPlayer)

            # --- Great People can be catched as unit to resettle
            PAE_City.catchGreatPeople(pCity, iNewOwner, iPreviousOwner, bAssimilation)

            # --- Nearest city revolts 33% chance
            if bConquest and iPreviousOwner != gc.getBARBARIAN_PLAYER() and pPreviousOwner.isAlive():
                if CvUtil.myRandom(3, "Nearest City revolt") == 1:
                    PAE_City.doNextCityRevolt(pCity.getX(), pCity.getY(), iPreviousOwner, iNewOwner)

            # --- Getting Technology when conquering (Forschungsbonus)
            # --- PAE V Patch4: nur ab Pop 3 (sonst exploit)
            if bConquest and (bAssimilation or pCity.getPopulation() > 2):
                PAE_City.getTechOnConquer(pCity, iPreviousOwner, iNewOwner)

            if not bAssimilation:
                # --- Getting goldkarren / treasure / Beutegold ------
                # --- PAE V Patch4: ab Pop 3 (sonst exploit)
                # --- Kein Goldkarren bei Assimilierung
                if pCity.getPopulation() > 2:
                    PAE_City.getGoldkarren(pCity, pPlayer)
                    PAE_City.doRefugeeToNeighborCity(pCity, iPreviousOwner, iNewOwner)

                # set city slaves to null
                if not bTrade:
                    PAE_Sklaven.doEnslaveCity(pCity)

            # Ab Tech Assimilation soll die Stadtpop mind. 5 sein (PAE V Patch 4)
            # TODO: was wenn die vorher schon kleiner war?
            if bAssimilation and pCity.getPopulation() < 5:
                pCity.setPopulation(5)

            # --- Vasallen-Feature / Vassal feature
            # iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
            if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES) and pPreviousOwner.isAlive():
                PAE_Vassal.onCityAcquired(pCity, iNewOwner, iPreviousOwner)

            # PAE Provinzcheck
            PAE_City.doCheckCityState(pCity)

            # PAE Debug Mark
            #"""

    def onCityAcquiredAndKept(self, argsList):
        'City Acquired and Kept'
        iOwner, pCity = argsList

        # iOwner funktioniert nicht und ist immer 0 !!! Deshalb muss es aus pCity geholt werden
        iOwner = pCity.getOwner()
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("onCityAcquiredAndKept: ",iOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        #### Message - Wonder capturing ####
        PAE_City.doMessageWonderCapture(pCity)

        #    CvUtil.pyPrint('City Acquired and Kept Event: %s' %(pCity.getName()))

    def onCityLost(self, argsList):
        'City Lost'
        city = argsList[0]
        player = PyPlayer(city.getOwner())
        PAE_City.doCheckGlobalTraitBuildings(city.getOwner())
        if not self.__LOG_CITYLOST:
            return
        CvUtil.pyPrint('City %s was lost by Player %d Civilization %s'
                       % (city.getName(), player.getID(), player.getCivilizationName()))

    def onCultureExpansion(self, argsList):
        ## Platy WorldBuilder ##
        if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython:
            return
        ## Platy WorldBuilder ##
        # 'City Culture Expansion'
        pCity = argsList[0]
        iPlayer = argsList[1]
        CvUtil.pyPrint("City %s's culture has expanded" % (pCity.getName(),))

    def onCityGrowth(self, argsList):
        'City Population Growth'
        pCity = argsList[0]
        iPlayer = argsList[1]
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("onCityGrowth: ",iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        pPlayer = gc.getPlayer(iPlayer)

        # AI soll zu 90% nicht mehr wachsen, wenn die Stadt ungluecklich wird
        # und zu 80% wenn ungesund wird
        # PAE V: dabei soll sie einen Getreidekarren erstellen
        if not pPlayer.isHuman():
            iChance = 0
            if pCity.goodHealth() < pCity.badHealth(False) - 1:
                iChance = 8
            if pCity.happyLevel() < pCity.unhappyLevel(0) - 1:
                iChance = 9
            if iChance > 0:
                if CvUtil.myRandom(10, "AI Wachstum vermeiden") < iChance:
                    pCity.changePopulation(-1)
                    # Getreidekarren erstellen (20%)
                    if CvUtil.myRandom(5 ,"Getreidekarren erstellen (20%)") == 1:
                        # Hegemon herausfinden. Wenn es einen gibt, bekommt der den Karren
                        pHegemon = pPlayer
                        iTeam = pPlayer.getTeam()
                        pTeam = gc.getTeam(iTeam)
                        iRange = gc.getMAX_PLAYERS()
                        for i in range(iRange):
                            pLoopPlayer = gc.getPlayer(i)
                            if pLoopPlayer.isAlive():
                                iTeam = pLoopPlayer.getTeam()
                                if pTeam.isVassal(iTeam):
                                    pHegemon = pLoopPlayer
                                    break

                        iNewUnit = gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")
                        CvUtil.spawnUnit(iNewUnit, pCity.plot(), pHegemon)

                        if pHegemon.isHuman():
                            CyInterface().addMessage(pHegemon.getID(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GET_UNIT_SUPPLY_FOOD", (pCity.getName(),)), "AS2D_BUILD_GRANARY", 2, gc.getUnitInfo(iNewUnit).getButton(), ColorTypes(8), pCity.getX(), pCity.getY(), True, True)


        # CvUtil.pyPrint("%s has grown to size %i" %(pCity.getName(),pCity.getPopulation()))
        if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GROWTH", (pCity.getName(), pCity.getPopulation())), None, 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

        # Kolonie / Provinz ----------
        PAE_City.doCheckCityState(pCity)
        # ----------------------------

        # Negatives Nahrungslager durch Stadtstatusgebaeude vermeiden (Flunky)
        if pCity.getFood() < 0:
            pCity.setFood(0)

        # ***TEST***
        #

    def onCityDoTurn(self, argsList):
        'City Production'
        pCity = argsList[0]
        iPlayer = argsList[1]
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("onCityDoTurn: ",iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        pPlayer = gc.getPlayer(iPlayer)
        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)
        # pCityPlot = pCity.plot()
        popCity = pCity.getPopulation()

        CvAdvisorUtils.cityAdvise(pCity, iPlayer)

        # PAE Debug Mark
        #"""

        # Trade feature: Check for free bonuses aquired via trade (Boggy)
        PAE_Trade.doCityCheckFreeBonuses(pCity)

        # PAE Provinzcheck
        bCheckCityState = False

        # +++++ AI Cities defend with bombardment of located units (Stadtverteidigung/Stadtbelagerung)
        # +++++ AI Hires Units (mercenaries)
        if not pPlayer.isHuman():
            PAE_City.AI_defendAndHire(pCity, iPlayer)

        # MESSAGES: city growing
        if not gc.getGame().isHotSeat():
            if pPlayer.isHuman():
                PAE_City.doMessageCityGrowing(pCity)

        # PAE V: Stadtversorgung / City supply: Troubles/Starvation because of unit maintenance in city (food)
        PAE_City.doUnitSupply(pCity, iPlayer)

        PAE_City.removeNoBonusNoBuilding(pCity)

        # Emigrants leave city when unhappy / Auswanderer verlassen die Stadt, wenn unzufrieden
        iTech = gc.getInfoTypeForString("TECH_COLONIZATION")
        if iPlayer != gc.getBARBARIAN_PLAYER() and pTeam.isHasTech(iTech) and popCity > 5:
            PAE_City.doEmigrantSpawn(pCity)

        # LEPROSY (Lepra) and PLAGUE (Pest) , Lepra ab 5, Pest ab 9, CIV-Event Influenza (Grippe) ab 7
        iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')

        bDecline = pCity.isHasBuilding(iBuildingPlague)
        # Lepra ab 5
        if not bDecline and pCity.getPopulation() >= 5:
            bDecline = PAE_City.doLeprosy(pCity)

        # Pest ab 9
        if not bDecline and pCity.getPopulation() >= 9:
            PAE_City.doSpawnPest(pCity)

        # Pest Auswirkungen
        # if city suffers from plague
        if pCity.isHasBuilding(iBuildingPlague):
            PAE_City.doPlagueEffects(pCity)

        # Slaves
        iCitySlaves = PAE_Sklaven.freeCitizen(pCity)
        # Sklavenerhalt: Available slave (2%) - Schwaechung bei christlicher Religion
        # Wenn Sklave ansaessig ist oder bei nem Sklavenmarkt
        if iCitySlaves > 0 or pCity.getNumRealBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")) > 0:
            PAE_Sklaven.spawnSlave(pCity, iCitySlaves)

        # Gladiators
        iCityGlads = PAE_Sklaven.freeCitizenGlad(pCity)

        if iCityGlads > 0:
            # Gladiator Unit (2% with gladiators)
            pTeam = gc.getTeam(pPlayer.getTeam())
            bTeamHasGladiators = False
            iTech = gc.getInfoTypeForString("TECH_GLADIATOR2")
            if pTeam.isHasTech(iTech):
                bTeamHasGladiators = True
                iCityGlads = PAE_Sklaven.spawnGlad(pCity, iCityGlads)
                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Gladiator (Zeile 3881)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            # Gladiator is dying . pro Glad 1%., min 3%
            if iCityGlads > 0:
                PAE_Sklaven.dyingGlad(pCity, iCityGlads, bTeamHasGladiators)

        PAE_Sklaven.dyingBuildingSlave(pCity)

        # City Rebellion
        # bRebellion = False
        # City Revolts / Stadt Revolten
        if pCity.getPopulation() > 1:
            if pCity.getOccupationTimer() > 0:
                bCheckCityState = PAE_City.doRevoltShrink(pCity)
            elif pCity.getPopulation() > 3:
                PAE_City.doTurnCityRevolt(pCity)

        # Judenaufstand Judentum: 2%, ab 200 BC
        bRevolt = False
        iReligionType = gc.getInfoTypeForString("RELIGION_JUDAISM")

        if pCity.isHolyCityByType(iReligionType) and gc.getGame().getGameTurnYear() > -200:
            bRevolt = PAE_City.doJewRevolt(pCity)

        # -------- Provinz Tributzahlung Statthalter
        # --- Ca 3% pro Runde = PAE IV
        iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
        if not bRevolt and pCity.isHasBuilding(iBuilding):
            bRevolt = PAE_City.provinceTribute(pCity)

        # Christentum und Haeresie (Heresy) ----------------------------
        if not bRevolt and gc.getGame().getGameTurnYear() > 0 and gc.getGame().getGameTurn() % 5 == 0:
            iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
            if gc.getGame().isReligionFounded(iReligion):
                # zum Christentum konvertieren
                if not pCity.isHasReligion(iReligion):
                    PAE_Christen.convertCity(pCity)

                # Bei christlich beeinflussten Staedten - Kulte und Religionen langsam raus (alle!)
                elif CvUtil.myRandom(10, "removePagans") == 1:  # 10%
                    PAE_Christen.removePagans(pCity)

        # PAE Provinzcheck
        if bCheckCityState:
            PAE_City.doCheckCityState(pCity)

        # PAE Debug Mark
        #"""

    def onCityBuildingUnit(self, argsList):
        'City begins building a unit'
        pCity = argsList[0]
        iUnitType = argsList[1]
        if not self.__LOG_CITYBUILDING:
            return
        CvUtil.pyPrint("%s has begun building a %s" % (pCity.getName(), gc.getUnitInfo(iUnitType).getDescription()))

    def onCityBuildingBuilding(self, argsList):
        'City begins building a Building'
        pCity = argsList[0]
        iBuildingType = argsList[1]
        if not self.__LOG_CITYBUILDING:
            return
        CvUtil.pyPrint("%s has begun building a %s" % (pCity.getName(), gc.getBuildingInfo(iBuildingType).getDescription()))

    def onCityRename(self, argsList):
        'City is renamed'
        pCity = argsList[0]
        if pCity.getOwner() == gc.getGame().getActivePlayer():
            self.__eventEditCityNameBegin(pCity, True)

    def onCityHurry(self, argsList):
        'City is renamed'
        pCity = argsList[0]
        iHurryType = argsList[1]

        # Kolonie / Provinz ----------
        PAE_City.doCheckCityState(pCity)
        # ----------------------------

    def onVictory(self, argsList):
        'Victory'
        iTeam, iVictory = argsList
        if iVictory >= 0 and iVictory < gc.getNumVictoryInfos():
            victoryInfo = gc.getVictoryInfo(int(iVictory))
            CvUtil.pyPrint("Victory!  Team %d achieves a %s victory"
                           % (iTeam, victoryInfo.getDescription()))

    def onVassalState(self, argsList):
        'Vassal State'
        iMaster, iVassal, bVassal = argsList

        if bVassal:
            CvUtil.pyPrint("Team %d becomes a Vassal State of Team %d"
                           % (iVassal, iMaster))
        else:
            CvUtil.pyPrint("Team %d revolts and is no longer a Vassal State of Team %d"
                           % (iVassal, iMaster))

    def onGameUpdate(self, argsList):
        'sample generic event, called on each game turn slice'
        genericArgs = argsList[0][0]  # tuple of tuple of my args
        turnSlice = genericArgs[0]

        if CIV4_SHELL:
            civ4Console.update(self.glob, self.loc)
        # Added by Gerikes for OOS logging.
        OOSLogger.doGameUpdate()
        # End added by Gerikes for OOS logging.

    def onMouseEvent(self, argsList):
        'mouse handler - returns 1 if the event was consumed'
        eventType, mx, my, px, py, interfaceConsumed, screens = argsList
        if px != -1 and py != -1:
            if eventType == self.EventLButtonDown:
                if self.bAllowCheats and self.bCtrl and self.bAlt and CyMap().plot(px, py).isCity() and not interfaceConsumed:
                    # Launch Edit City Event
                    self.beginEvent(CvUtil.EventEditCity, (px, py))
                    return 1

                elif self.bAllowCheats and self.bCtrl and self.bShift and not interfaceConsumed:
                    # Launch Place Object Event
                    self.beginEvent(CvUtil.EventPlaceObject, (px, py))
                    return 1

        if eventType == self.EventBack:
            return CvScreensInterface.handleBack(screens)
        elif eventType == self.EventForward:
            return CvScreensInterface.handleForward(screens)

        return 0


    #################### TRIGGERED EVENTS ##################

    # BTS Original
    def __eventPlaceObjectBegin(self, argsList):
        'Place Object Event'
        CvDebugTools.CvDebugTools().initUnitPicker(argsList)

    def __eventPlaceObjectApply(self, playerID, userData, popupReturn):
        'Place Object Event Apply'
        if getChtLvl() > 0:
            CvDebugTools.CvDebugTools().applyUnitPicker((popupReturn, userData))

    def __eventAwardTechsAndGoldBegin(self, argsList):
        'Award Techs & Gold Event'
        CvDebugTools.CvDebugTools().cheatTechs()

    def __eventAwardTechsAndGoldApply(self, playerID, netUserData, popupReturn):
        'Award Techs & Gold Event Apply'
        if getChtLvl() > 0:
            CvDebugTools.CvDebugTools().applyTechCheat((popupReturn))

    def __eventShowWonderBegin(self, argsList):
        'Show Wonder Event'
        CvDebugTools.CvDebugTools().wonderMovie()

    def __eventShowWonderApply(self, playerID, netUserData, popupReturn):
        'Wonder Movie Apply'
        if getChtLvl() > 0:
            CvDebugTools.CvDebugTools().applyWonderMovie((popupReturn))

    # BTS Original kann bei Bedarf aus dem Originalcode kopiert werden ------

    ## Platy WorldBuilder ##
    def __eventEditUnitNameBegin(self, argsList):
        pUnit = argsList
        popup = PyPopup.PyPopup(CvUtil.EventEditUnitName, EventContextTypes.EVENTCONTEXT_ALL)
        popup.setUserData((pUnit.getID(), pUnit.getOwner()))
        popup.setBodyString(localText.getText("TXT_KEY_RENAME_UNIT", ()))
        popup.createEditBox(pUnit.getNameNoDesc())
        popup.setEditBoxMaxCharCount(25)
        popup.launch()

    def __eventEditUnitNameApply(self, playerID, userData, popupReturn):
        unit = gc.getPlayer(userData[1]).getUnit(userData[0])
        newName = popupReturn.getEditBoxString(0)
        unit.setName(newName)
        if CyGame().GetWorldBuilderMode():
            WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeStats()
            WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeCurrentUnit()

    def __eventEditCityNameBegin(self, city, bRename):
        popup = PyPopup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
        popup.setUserData((city.getID(), bRename, city.getOwner()))
        popup.setHeaderString(localText.getText("TXT_KEY_NAME_CITY", ()))
        popup.setBodyString(localText.getText("TXT_KEY_SETTLE_NEW_CITY_NAME", ()))
        popup.createEditBox(city.getName())
        popup.setEditBoxMaxCharCount(15)
        popup.launch()

    def __eventEditCityNameApply(self, playerID, userData, popupReturn):
        city = gc.getPlayer(userData[2]).getCity(userData[0])
        cityName = popupReturn.getEditBoxString(0)
        city.setName(cityName, not userData[1])
        if CyGame().GetWorldBuilderMode() and not CyGame().isInAdvancedStart():
            WBCityEditScreen.WBCityEditScreen().placeStats()

    def __eventWBPlayerScriptPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        dData = CvUtil.decode_script_data(sScript)
        for key in dData:
            CvUtil.addScriptData(gc.getPlayer(userData[0]), key, dData[key])
        WBPlayerScreen.WBPlayerScreen().placeScript()
        return

    def __eventWBCityScriptPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        pCity = gc.getPlayer(userData[0]).getCity(userData[1])
        dData = CvUtil.decode_script_data(sScript)
        for key in dData:
            CvUtil.addScriptData(pCity, key, dData[key])
        WBCityEditScreen.WBCityEditScreen().placeScript()
        return

    def __eventWBUnitScriptPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        pUnit = gc.getPlayer(userData[0]).getUnit(userData[1])
        dData = CvUtil.decode_script_data(sScript)
        for key in dData:
            CvUtil.addScriptData(pUnit, key, dData[key])
        WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
        return

    def __eventWBScriptPopupBegin(self):
        return

    def __eventWBGameScriptPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        dData = CvUtil.decode_script_data(sScript)
        for key in dData:
            CvUtil.addScriptData(CyGame(), key, dData[key])
        WBGameDataScreen.WBGameDataScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
        return

    def __eventWBPlotScriptPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        pPlot = CyMap().plot(userData[0], userData[1])
        dData = CvUtil.decode_script_data(sScript)
        for key in dData:
            CvUtil.addScriptData(pPlot, key, dData[key])
        WBPlotScreen.WBPlotScreen().placeScript()
        return

    def __eventWBLandmarkPopupApply(self, playerID, userData, popupReturn):
        sScript = popupReturn.getEditBoxString(0)
        pPlot = CyMap().plot(userData[0], userData[1])
        iPlayer = userData[2]
        if userData[3] > -1:
            pSign = CyEngine().getSignByIndex(userData[3])
            iPlayer = pSign.getPlayerType()
            CyEngine().removeSign(pPlot, iPlayer)
        if sScript:
            if iPlayer == gc.getBARBARIAN_PLAYER():
                CyEngine().addLandmark(pPlot, CvUtil.convertToStr(sScript))
            else:
                CyEngine().addSign(pPlot, iPlayer, CvUtil.convertToStr(sScript))
        WBPlotScreen.iCounter = 10
        return
    ## Platy WorldBuilder ##

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # BTS END OF FILE -----------------------------------------------------------------------
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
