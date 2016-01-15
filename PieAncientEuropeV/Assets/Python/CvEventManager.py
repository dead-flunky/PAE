## Sid Meier's Civilization 4
## Copyright Firaxis Games 2006
##
## CvEventManager
## This class is passed an argsList from CvAppInterface.onEvent
## The argsList can contain anything from mouse location to key info
## The EVENTLIST that are being notified can be found
## ---------------------
## Edited by Pie, Austria 2010-2014

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

from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import CvDebugTools
import CvWBPopups
import PyHelpers
import Popup as PyPopup
import CvCameraControls
import CvTopCivs
import sys
import CvWorldBuilderScreen
import CvAdvisorUtils
import CvTechChooser
import pickle
import math
import time
import re
import time
import random # Seed! fixed MP-OOS
import itertools # faster repeating of stuff
import CvScreenEnums
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

gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
PyCity = PyHelpers.PyCity
PyGame = PyHelpers.PyGame


# PAE Random Seed
seed = int(time.strftime("%d%m%Y"))
random.seed(seed)
CyRandom().init(seed)

# globals
###################################################
class CvEventManager:
  def __init__(self):
    #################### ON EVENT MAP ######################
    #print "EVENTMANAGER INIT"

    # PAE - Great General Names
    self.GG_UsedNames = []

    # PAE - Show message which player is on turn
    self.bPAE_ShowMessagePlayerTurn = False

    # PAE - ICE AGE (Boggy) - Schmelzen 1/4
    self.IceSnow = []
    self.IceCoast = []
    self.IceTundra = []
    self.IceTundra2 = []
    self.IceEis = []
    self.IceDesertEbene = []
    self.IceDesertCoast = []

    # PAE - InstanceChanceModifier for units in getting Fighting-Promotions (per turn)
    # [PlayerID, UnitID]
    self.PAEInstanceFightingModifier = []

    # PAE - InstanceCostModifier for players when hiring mercenaries (per turn)
    # [PlayerID, Amount of HiredMercenaries]
    self.PAEInstanceHiringModifier = []

    # PAE Statthalter Tribut
    self.PAEStatthalterTribut = []

    self.bCtrl = False
    self.bShift = False
    self.bAlt = False
    self.bAllowCheats = False

    # OnEvent Enums
    self.EventLButtonDown=1
    self.EventLcButtonDblClick=2
    self.EventRButtonDown=3
    self.EventBack=4
    self.EventForward=5
    self.EventKeyDown=6
    self.EventKeyUp=7

    self.__LOG_MOVEMENT = 0
    self.__LOG_BUILDING = 0
    self.__LOG_COMBAT = 0
    self.__LOG_CONTACT = 0
    self.__LOG_IMPROVEMENT = 0
    self.__LOG_CITYLOST = 0
    self.__LOG_CITYBUILDING = 0
    self.__LOG_TECH = 0
    self.__LOG_UNITBUILD = 0
    self.__LOG_UNITKILLED = 1
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

    ## EVENTLIST
    self.EventHandlerMap = {
      'mouseEvent'   : self.onMouseEvent,
      'kbdEvent'     : self.onKbdEvent,
      'ModNetMessage': self.onModNetMessage,
      'Init'         : self.onInit,
      'Update'       : self.onUpdate,
      'UnInit'       : self.onUnInit,
      'OnSave'       : self.onSaveGame,
      'OnPreSave'    : self.onPreSave,
      'OnLoad'       : self.onLoadGame,
      'GameStart'    : self.onGameStart,
      'GameEnd'      : self.onGameEnd,
      'plotRevealed' : self.onPlotRevealed,
      'plotFeatureRemoved': self.onPlotFeatureRemoved,
      'plotPicked'      : self.onPlotPicked,
      'nukeExplosion'   : self.onNukeExplosion,
      'gotoPlotSet'     : self.onGotoPlotSet,
      'BeginGameTurn'   : self.onBeginGameTurn,
      'EndGameTurn'     : self.onEndGameTurn,
      'BeginPlayerTurn' : self.onBeginPlayerTurn,
      'EndPlayerTurn'   : self.onEndPlayerTurn,
      'endTurnReady'    : self.onEndTurnReady,
      'combatResult'    : self.onCombatResult,
      'combatLogCalc'   : self.onCombatLogCalc,
      'combatLogHit'    : self.onCombatLogHit,
      'improvementBuilt': self.onImprovementBuilt,
      'improvementDestroyed': self.onImprovementDestroyed,
      'routeBuilt'   : self.onRouteBuilt,
      'firstContact' : self.onFirstContact,
      'cityBuilt'    : self.onCityBuilt,
      'cityRazed'    : self.onCityRazed,
      'cityAcquired' : self.onCityAcquired,
      'cityAcquiredAndKept': self.onCityAcquiredAndKept,
      'cityLost'         : self.onCityLost,
      'cultureExpansion' : self.onCultureExpansion,
      'cityGrowth'       : self.onCityGrowth,
      'cityDoTurn'       : self.onCityDoTurn,
      'cityBuildingUnit' : self.onCityBuildingUnit,
      'cityBuildingBuilding': self.onCityBuildingBuilding,
      'cityRename'       : self.onCityRename,
      'cityHurry'        : self.onCityHurry,
      'selectionGroupPushMission': self.onSelectionGroupPushMission,
      'unitMove'    : self.onUnitMove,
      'unitSetXY'   : self.onUnitSetXY,
      'unitCreated' : self.onUnitCreated,
      'unitBuilt'   : self.onUnitBuilt,
      'unitKilled'  : self.onUnitKilled,
      'unitLost'    : self.onUnitLost,
      'unitPromoted': self.onUnitPromoted,
      'unitSelected': self.onUnitSelected,
      'UnitRename'  : self.onUnitRename,
      'unitPillage' : self.onUnitPillage,
      'unitSpreadReligionAttempt': self.onUnitSpreadReligionAttempt,
      'unitGifted'  : self.onUnitGifted,
      'unitBuildImprovement': self.onUnitBuildImprovement,
      'goodyReceived'     : self.onGoodyReceived,
      'greatPersonBorn'   : self.onGreatPersonBorn,
      'buildingBuilt'     : self.onBuildingBuilt,
      'projectBuilt'      : self.onProjectBuilt,
      'techAcquired'      : self.onTechAcquired,
      'techSelected'      : self.onTechSelected,
      'religionFounded'   : self.onReligionFounded,
      'religionSpread'    : self.onReligionSpread,
      'religionRemove'    : self.onReligionRemove,
      'corporationFounded': self.onCorporationFounded,
      'corporationSpread' : self.onCorporationSpread,
      'corporationRemove' : self.onCorporationRemove,
      'goldenAge'     : self.onGoldenAge,
      'endGoldenAge'  : self.onEndGoldenAge,
      'chat'          : self.onChat,
      'victory'       : self.onVictory,
      'vassalState'   : self.onVassalState,
      'changeWar'     : self.onChangeWar,
      'setPlayerAlive': self.onSetPlayerAlive,
      'playerChangeStateReligion': self.onPlayerChangeStateReligion,
      'playerGoldTrade' : self.onPlayerGoldTrade,
      'windowActivation': self.onWindowActivation,
      'gameUpdate'      : self.onGameUpdate,    # sample generic event
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
    #self.Events={
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
    self.Events={
      CvUtil.EventEditCityName : ('EditCityName', self.__eventEditCityNameApply, self.__eventEditCityNameBegin),
      CvUtil.EventPlaceObject : ('PlaceObject', self.__eventPlaceObjectApply, self.__eventPlaceObjectBegin),
      CvUtil.EventAwardTechsAndGold: ('AwardTechsAndGold', self.__eventAwardTechsAndGoldApply, self.__eventAwardTechsAndGoldBegin),
      CvUtil.EventEditUnitName : ('EditUnitName', self.__eventEditUnitNameApply, self.__eventEditUnitNameBegin),
      CvUtil.EventWBLandmarkPopup : ('WBLandmarkPopup', self.__eventWBLandmarkPopupApply, self.__eventWBScriptPopupBegin),
      CvUtil.EventShowWonder: ('ShowWonder', self.__eventShowWonderApply, self.__eventShowWonderBegin),
      1111 : ('WBPlayerScript', self.__eventWBPlayerScriptPopupApply, self.__eventWBScriptPopupBegin),
      2222 : ('WBCityScript', self.__eventWBCityScriptPopupApply, self.__eventWBScriptPopupBegin),
      3333 : ('WBUnitScript', self.__eventWBUnitScriptPopupApply, self.__eventWBScriptPopupBegin),
      4444 : ('WBGameScript', self.__eventWBGameScriptPopupApply, self.__eventWBScriptPopupBegin),
      5555 : ('WBPlotScript', self.__eventWBPlotScriptPopupApply, self.__eventWBScriptPopupBegin),
## Platy WorldBuilder ##
    }

#################### EVENT STARTERS ######################
  def handleEvent(self, argsList):
    'EventMgr entry point'
    # extract the last 6 args in the list, the first arg has already been consumed
    self.origArgsList = argsList  # point to original
    tag = argsList[0]        # event type string
    idx = len(argsList)-6
    bDummy = False
    self.bDbg, bDummy, self.bAlt, self.bCtrl, self.bShift, self.bAllowCheats = argsList[idx:]
    ret = 0
    if self.EventHandlerMap.has_key(tag):
      fxn = self.EventHandlerMap[tag]
      ret = fxn(argsList[1:idx])
    return ret

#################### EVENT APPLY ######################
  def beginEvent( self, context, argsList=-1 ):
    'Begin Event'
    entry = self.Events[context]
    return entry[2]( argsList )

  def applyEvent( self, argsList ):
    'Apply the effects of an event '
    context, playerID, netUserData, popupReturn = argsList

    if context == CvUtil.PopupTypeEffectViewer:
      return CvDebugTools.g_CvDebugTools.applyEffectViewer( playerID, netUserData, popupReturn )

    entry = self.Events[context]

    if ( context not in CvUtil.SilentEvents ):
      self.reportEvent(entry, context, (playerID, netUserData, popupReturn) )
    return entry[1]( playerID, netUserData, popupReturn )   # the apply function

  def reportEvent(self, entry, context, argsList):
    'Report an Event to Events.log '
    if (gc.getGame().getActivePlayer() != -1):
      message = "DEBUG Event: %s (%s)" %(entry[0], gc.getActivePlayer().getName())
      CyInterface().addImmediateMessage(message,"")
      CvUtil.pyPrint(message)
    return 0

#################### RANDOM ######################
  def myRandom (self, num, txt):
    #return gc.getGame().getMapRandNum(num, None)
    if num <= 1: return 0
    else: return random.randint(0, num-1)

#################### ON EVENTS ######################
  def onKbdEvent(self, argsList):
    'keypress handler - return 1 if the event was consumed'

    eventType,key,mx,my,px,py = argsList
    game = gc.getGame()

    if (self.bAllowCheats):
      # notify debug tools of input to allow it to override the control
      argsList = (eventType,key,self.bCtrl,self.bShift,self.bAlt,mx,my,px,py,gc.getGame().isNetworkMultiPlayer())
      if ( CvDebugTools.g_CvDebugTools.notifyInput(argsList) ):
        return 0

    if ( eventType == self.EventKeyDown ):
      theKey=int(key)

#From FfH-Mod: by Kael 07/05/2008
      if (theKey == int(InputTypes.KB_LEFT)):
        if self.bCtrl:
            CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 45.0)
            return 1
        elif self.bShift:
            CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 10.0)
            return 1

      if (theKey == int(InputTypes.KB_RIGHT)):
          if self.bCtrl:
              CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 45.0)
              return 1
          elif self.bShift:
              CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 10.0)
              return 1
#From FfH: End

# PAE Spieler am Zug Message aktivieren/deaktvieren: STRG+P / CTRL+P --
      if (theKey == int(InputTypes.KB_P)):
        if self.bCtrl:
            if self.bPAE_ShowMessagePlayerTurn:
              self.bPAE_ShowMessagePlayerTurn = False
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN_DEACTIVATED",("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)
            else:
              self.bPAE_ShowMessagePlayerTurn = True
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN_ACTIVATED",("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)
            return 1

      CvCameraControls.g_CameraControls.handleInput( theKey )

## AI AutoPlay ##
      if CyGame().getAIAutoPlay():
        if theKey == int(InputTypes.KB_SPACE) or theKey == int(InputTypes.KB_ESCAPE):
          CyGame().setAIAutoPlay(0)
          return 1
## AI AutoPlay ##

      if (self.bAllowCheats):
        # Shift - T (Debug - No MP)
        if (theKey == int(InputTypes.KB_T)):
          if ( self.bShift ):
            self.beginEvent(CvUtil.EventAwardTechsAndGold)
            #self.beginEvent(CvUtil.EventCameraControlPopup)
            return 1

        elif (theKey == int(InputTypes.KB_W)):
          if ( self.bShift and self.bCtrl):
            self.beginEvent(CvUtil.EventShowWonder)
            return 1

        # Shift - ] (Debug - currently mouse-overd unit, health += 10
        elif (theKey == int(InputTypes.KB_LBRACKET) and self.bShift ):
          unit = CyMap().plot(px, py).getUnit(0)
          if ( not unit.isNone() ):
            d = min( unit.maxHitPoints()-1, unit.getDamage() + 10 )
            unit.setDamage( d, PlayerTypes.NO_PLAYER )

        # Shift - [ (Debug - currently mouse-overd unit, health -= 10
        elif (theKey == int(InputTypes.KB_RBRACKET) and self.bShift ):
          unit = CyMap().plot(px, py).getUnit(0)
          if ( not unit.isNone() ):
            d = max( 0, unit.getDamage() - 10 )
            unit.setDamage( d, PlayerTypes.NO_PLAYER )

        elif (theKey == int(InputTypes.KB_F1)):
          if ( self.bShift ):
            CvScreensInterface.replayScreen.showScreen(False)
            return 1
          # don't return 1 unless you want the input consumed

        elif (theKey == int(InputTypes.KB_F2)):
          if ( self.bShift ):
            import CvDebugInfoScreen
            CvScreensInterface.showDebugInfoScreen()
            return 1

        elif (theKey == int(InputTypes.KB_F3)):
          if ( self.bShift ):
            CvScreensInterface.showDanQuayleScreen(())
            return 1

        elif (theKey == int(InputTypes.KB_F4)):
          if ( self.bShift ):
            CvScreensInterface.showUnVictoryScreen(())
            return 1

    return 0

  def onModNetMessage(self, argsList):
    'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'

    iData1, iData2, iData3, iData4, iData5 = argsList

    print("Modder's net message!")
    CvUtil.pyPrint( 'onModNetMessage' )

    #iData1 = iMessageID (!)

    # Inquisitor
    if iData1 == 665:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doInquisitorPersecution(pCity, pUnit)
    # Horse down
    if iData1 == 666:
      pPlot = CyMap().plot(iData2, iData3)
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doHorseDown(pPlot, pUnit)
    # Horse up
    if iData1 == 667:
      pPlot = CyMap().plot(iData2, iData3)
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doHorseUp(pPlot, pUnit)
    # Slave -> Bordell
    if iData1 == 668:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Bordell(pCity, pUnit)
    # Slave -> Gladiator
    if iData1 == 669:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Gladiator(pCity, pUnit)
    # Slave -> Theatre
    if iData1 == 670:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Theatre(pCity, pUnit)
    # Emigrant
    if iData1 == 672:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doEmigrant(pCity, pUnit)
    # Disband city
    if iData1 == 673:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doDisbandCity(pCity, pUnit, pPlayer)
    # Hunnen
    if iData1 == 674:
      # iData2 = iPlayer , iData3 = unitID
      gc.getPlayer(iData2).changeGold(-100)
      #gc.getPlayer(gc.getBARBARIAN_PLAYER()).getUnit(iData3).kill(1,gc.getBARBARIAN_PLAYER())
      gc.getPlayer(gc.getBARBARIAN_PLAYER()).getUnit(iData3).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_HUNS_PAID",()), None, 2, None, ColorTypes(14), 0, 0, False, False)
    # City Revolten
    if iData1 == 675:
      # iData2 = iPlayer , iData3 = City ID, iData4 = Revolt Turns , iData5 = Button
      # Button 0: 1st Payment: pop * 10 - 5% chance
      # Button 1: 2nd Payment: pop * 5 - 30% chance
      # Button 2: Cancel: 100% revolt
      pPlayer = gc.getPlayer(iData2)
      pCity = pPlayer.getCity(iData3)
      pPlot = CyMap().plot(pCity.getX(), pCity.getY())

      if iData5 == 0:
        if pPlayer.getGold() >= pCity.getPopulation() * 10:
          pPlayer.changeGold(pCity.getPopulation() * (-10))
          iChance = 1
        else: iChance = 20
      elif iData5 == 1:
        if pPlayer.getGold() >= pCity.getPopulation() * 5:
          pPlayer.changeGold(pCity.getPopulation() * (-5))
          iChance = 6
        else: iChance = 20
      else: iChance = 20

      iRand = self.myRandom(20, None)
      if iRand < iChance:
        if pPlot.getNumUnits() > pCity.getPopulation(): iData4 = 2

        self.doCityRevolt (pCity,iData4)

        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_1",(pCity.getName(),)), None, 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
      else:
        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_2",(pCity.getName(),)), None, 2, None, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

    # 676 vergeben (Tech - Unit)

    # 677 Goldkarren / Beutegold / Treasure zw 80 und 150
    if iData1 == 677:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iGold = 80 + self.myRandom(71, None)
      pPlayer.changeGold(iGold)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GOLDKARREN_ADD_GOLD",(iGold,)), "AS2D_BUILD_BANK", 2, None, ColorTypes(8), 0, 0, False, False)
      #iBuilding = gc.getInfoTypeForString("BUILDING_PALACE")
      #pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, 1)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Beutegold eingesackt (Zeile 444)",150)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Provinzhauptstadt Statthalter Tribut
    if iData1 == 678:
      # iData2 = iPlayer, iData3 = CityID, iData4 = Antwort [0,1,2] , iData5 = Tribut
      pPlayer = gc.getPlayer(iData2)
      pCity = pPlayer.getCity(iData3)
      iTribut = iData5
      iTribut2 = iData5 / 2

      iGold = pPlayer.getGold()
      bDoRebellion = False
      iAddHappiness = -1
      bPaid = False
      iRebellionRand = self.myRandom(100, None)

      if iGold >= iTribut:
        if iData4 == 0:
          pPlayer.changeGold(-iTribut)
          iAddHappiness = 2
          bPaid = True
        elif iData4 == 1:
          pPlayer.changeGold(-iTribut2)
          iAddHappiness = 1
          bPaid = True

      elif iGold >= iTribut2:
        if iData4 == 0:
          pPlayer.changeGold(-iTribut2)
          iAddHappiness = 1
          bPaid = True

      elif iGold > 0:
        if iData4 == 0:
          pPlayer.setGold(0)
          iAddHappiness = 0


      # Happiness setzen (Bug bei CIV, Man muss immer den aktuellen Wert + die Aenderung setzen)
      iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
      iBuildingHappiness = pCity.getBuildingHappiness(iBuilding)
      pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding).getBuildingClassType(), iBuildingHappiness + iAddHappiness)


      # Chance einer Rebellion: Unhappy Faces * Capital Distance
      iCityHappiness = pCity.happyLevel() - pCity.unhappyLevel(0)
      if iCityHappiness < 0:
              # Abstand zur Hauptstadt
              if not pPlayer.getCapitalCity().isNone() and pPlayer.getCapitalCity() != None:
                iDistance = plotDistance(pPlayer.getCapitalCity().getX(), pPlayer.getCapitalCity().getY(), pCity.getX(), pCity.getY())
              else: iDistance = 20
              iChance = iCityHappiness * (-1) * iDistance
              if iChance > iRandRebellion: bDoRebellion = True


      if bDoRebellion:
        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_NEG",(pCity.getName(),)), "AS2D_REVOLTSTART", 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_NEG",(pCity.getName(), )))
        popupInfo.addPopup(iData2)
        self.doProvinceRebellion(pCity)
      elif bPaid:
        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_POS",(pCity.getName(),)), "AS2D_BUILD_BANK", 2, None, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
        szBuffer = CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN",(pCity.getName(), ))
        iRand = 1 + self.myRandom(23, None)
        szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_"+str(iRand),())

        # 1 Unit as gift:
        lGift = []
        # Auxiliar
        lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR")))
        if pCity.canTrain(gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"))
        # Food
        lGift.append(gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"))
        # Slave
        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
        # Mounted
        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
          lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_CHARIOT"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
        # Elefant
        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
          lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))

        # Choose unit
        iRand = self.myRandom(len(lGift), None)

        # Auxiliars as gift:
        #iAnz = 1 + self.myRandom(3, None)
        #if iAnz == 1: szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2_SINGULAR",("", ))
        #else: szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2_PLURAL",(iAnz, ))
        szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2",(gc.getUnitInfo(lGift[iRand]).getDescriptionForm(0), ))

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(szBuffer)
        popupInfo.addPopup(iData2)

        pPlayer.initUnit(lGift[iRand], pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)



    # Slave -> Schule
    if iData1 == 679:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Schule(pCity, pUnit)

    # Slave -> Manufaktur Nahrung
    if iData1 == 680:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Manufaktur(pCity, pUnit, 0)

    # Slave -> Manufaktur Produktion
    if iData1 == 681:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Manufaktur(pCity, pUnit, 1)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Vasallen Start -------------------------------------------------------
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # iLoser gets Vassal of iWinner with 1/2 Gold of iLoser
    if iData1 == 671:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)

      iWinnerTeam = pWinner.getTeam()
      pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      pLoserTeam = gc.getTeam(iLoserTeam)

      # Botschafter Kill
      # Verschlechterung der Beziehungen um -1
      # Verbesserung der Beziehungen mit jenen, die mit diesem im Krieg sind um +1
      if iData4 == -1:
        # Verlierer bekommt Absage
        if iData5 == 0:
          # Verlierer bekommt -1 zum Gewinner
          pLoser.AI_changeAttitudeExtra(iData2,-1)
          # Alle, die mit dem Verlierer im Krieg sind, bekommen zum Gewinner +1
          # ausser die Vasallen des Gewinners
          iRange = gc.getMAX_PLAYERS()
          for i in range(iRange):
            if gc.getPlayer(i).isAlive():
              iTeam = gc.getPlayer(i).getTeam()
              if pLoserTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pWinnerTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iData2,1)
        # Gewinner bekommt Absage
        else:
          # Gewinner bekommt -1 zum Verlierer
          pWinner.AI_changeAttitudeExtra(iData3,-1)
          # Alle, die mit dem Gewinner im Krieg sind, bekommen zum Verlierer +1
          # ausser die Vasallen des Verlierers
          iRange = gc.getMAX_PLAYERS()
          for i in range(iRange):
            if gc.getPlayer(i).isAlive():
              iTeam = gc.getPlayer(i).getTeam()
              if pWinnerTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pLoserTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iData3,1)
      else:
        pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
        self.VassalHegemonGetsVassal(iData3) # Hegemon verliert seine Vasallen
        pWinner.changeGold(iData4)
        pLoser.changeGold(iData4 * (-1))
        if iData2 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')


    # HI-HI Interaktion Start ++++++++++++++++++++++++++++++
    # 1) Der Loser darf beginnen und sich als Vasall vorschlagen
    # 1a) Wenn negativ, dann soll Winner eine Meldung bekommen und dem Loser einen Vorschlag unterbreiten => 2
    # 1b) Der Winner darf entscheiden, ob der Vorschlag angenommen wird
    # 2) Der Loser darf entscheiden, ob er mit dem Angebot des Winners Vasall wird
    # = Net-ID , iWinner , iLoser, iGold1
    if iData1 == 682:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)

      iWinnerTeam = pWinner.getTeam()
      pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      pLoserTeam = gc.getTeam(iLoserTeam)

      # Loser moechte nix zu tun haben = 1a
      # Winner bietet Hegemonschaft an
      if iData4 == -1:
              iGold1 = self.myRandom(pWinner.getGold() / 4, None)
              if iGold1 < pWinner.getGold() / 8: iGold1 = pWinner.getGold() / 8 + iGold1
              iGold2 = iGold1 * 2
              iGold1 = int(iGold1)
              iGold2 = int(iGold2)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iGold1)
              popupInfo.setFlags(iGold2)
              popupInfo.setOnClickedPythonCallback("popupVassal04") # EntryPoints/CvScreenInterface und CvGameUtils / 683
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_1",(iGold1,pWinner.getCivilizationAdjective(2))), "")
              if iGold2 > 0: popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_2",(iGold2,pWinner.getCivilizationAdjective(2))), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_NO",()), "")
              popupInfo.addPopup(iData2)
      # Loser schlagt vor, Winner entscheidet = 1b
      else:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0),iData4)) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iData4)
              popupInfo.setOnClickedPythonCallback("popupVassal06") # EntryPoints/CvScreenInterface und CvGameUtils / 685
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06_YES",()), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06_NO",()), "")
              iRand = 1 + self.myRandom(9, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
              popupInfo.addPopup(iData2)

    # 1a => 2
    if iData1 == 683:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)

      iWinnerTeam = pWinner.getTeam()
      pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      pLoserTeam = gc.getTeam(iLoserTeam)

      # Winner bietet Hegemonschaft an
      # Loser entscheidet
      if iData4 >= 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0),iData4)) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iData4)
              popupInfo.setOnClickedPythonCallback("popupVassal05") # EntryPoints/CvScreenInterface und CvGameUtils / 684
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_YES",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_NO",(iData4,)), "")
              iRand = 1 + self.myRandom(9, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
              popupInfo.addPopup(iData3)

    # 2 => Loser entscheidet: YES: Loser wird Vasall, NO: Winner bekommt Meldung
    if iData1 == 684:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)

      iWinnerTeam = pWinner.getTeam()
      pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      pLoserTeam = gc.getTeam(iLoserTeam)

      # Winner bietet Hegemonschaft an
      # Loser nicht einverstanden
      if iData4 == 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(1) # zur Winnerauswahl
              popupInfo.setOnClickedPythonCallback("popupVassal07") # EntryPoints/CvScreenInterface und CvGameUtils / 686 / 1
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_YES",()), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_NO",()), "")
              popupInfo.addPopup(iData2)

      # Botschafter vom Winner wird gekillt
      elif iData4 == -1:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
              popupInfo.addPopup(iData3)

              # Verschlechterung der Beziehungen des Gewinners zum Verlierer -1
              pWinner.AI_changeAttitudeExtra(iData3,-1)
              # Alle, die mit dem Gewinner im Krieg sind, bekommen zum Verlierer +1
              # ausser die Vasallen des Verlierers
              iRange = gc.getMAX_PLAYERS()
              for i in range(iRange):
                if gc.getPlayer(i).isAlive():
                  iTeam = gc.getPlayer(i).getTeam()
                  if pWinnerTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pLoserTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iData3,1)

      else:
        pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
        self.VassalHegemonGetsVassal(iData3) # Hegemon verliert seine Vasallen
        pLoser.changeGold(iData4)
        pWinner.changeGold(iData4 * (-1))
        if iData3 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

    # 1b Winner entscheidet: YES: Loser wird Vasall, NO: Loser bekommt Meldung
    if iData1 == 685:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)

      iWinnerTeam = pWinner.getTeam()
      pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      pLoserTeam = gc.getTeam(iLoserTeam)

      # Winner bietet Hegemonschaft an
      # Loser entscheidet

      # Winner lehnt ab, nochmal entscheiden?
      if iData4 == 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0))) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(0) # zur Loserauswahl
              popupInfo.setOnClickedPythonCallback("popupVassal07") # EntryPoints/CvScreenInterface und CvGameUtils / 686 / 0
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_YES",()), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_NO",()), "")
              popupInfo.addPopup(iData3)

      # Botschafter vom Loser wird gekillt
      elif iData4 == -1:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0))) )
              popupInfo.addPopup(iData3)
              # Verschlechterung der Beziehungen vom Verlierer zum Gewinner -1
              pLoser.AI_changeAttitudeExtra(iData2,-1)
              # Alle, die mit dem Verlierer im Krieg sind, bekommen zum Gewinner +1
              # ausser die Vasallen des Gewinners
              iRange = gc.getMAX_PLAYERS()
              for i in range(iRange):
                if gc.getPlayer(i).isAlive():
                  iTeam = gc.getPlayer(i).getTeam()
                  if pLoserTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pWinnerTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iData2,1)

      # Vasall werden
      else:
        pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
        self.VassalHegemonGetsVassal(iData3) # Hegemon verliert seine Vasallen
        pWinner.changeGold(iData4)
        pLoser.changeGold(iData4 * (-1))
        if iData2 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

    # Es wird nochmal entschieden
    if iData1 == 686:
      # zur Loserauswahl
      if iData4 == 0:
        # iWinner , iLoser, pCity
        self.VassalHItoHI (iData2, iData3, None)
      # zur Winnerauswahl
      else:
        CyMessageControl().sendModNetMessage( 682, iData1, iData2, -1, 0 )

    # HI-HI Interaktion Ende +++++++++++++++++++++++++++++++++

    # Winner greift einen Hegemon an und bekommt ein positives Kriegsangebot von einem seiner Vasallen
    # Message-ID / HI - Winner / KI-Loser (Hegemon) / KI-Vasall / Bestechungsgeld
    if iData1 == 687:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)
      pVassal = gc.getPlayer(iData4)

      #iWinnerTeam = pWinner.getTeam()
      #pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      #pLoserTeam = gc.getTeam(iLoserTeam)
      #pHegemonTeam.freeVassal(iTeam)
      iVassalTeam = pVassal.getTeam()
      pVassalTeam = gc.getTeam(iVassalTeam)

      # Zuerst allen Frieden schliessen
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        if gc.getPlayer(i).isAlive():
          iTeam = gc.getPlayer(i).getTeam()
          if pVassalTeam.isAtWar(iTeam): gc.getTeam(iTeam).makePeace(pVassalTeam.getID())

      # Danach dem alten Hegemon Krieg erklaeren
      gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)
      pVassal.changeGold(iData5)
      pWinner.changeGold(iData5 * (-1))
      if iData4 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

    # HI ist Vasall eines Hegemons, der soeben eine Stadt verloren hat
    # iData5: 0=Krieg gegen Hegemon, 1=treu
    if iData1 == 688:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)
      pVassal = gc.getPlayer(iData4)
      #iWinnerTeam = pWinner.getTeam()
      #pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      #pLoserTeam = gc.getTeam(iLoserTeam)

      if iData5 == 0:
        gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)
        # Beziehungsstatus aendern
        pLoser.AI_changeAttitudeExtra(iData4,-2)
        pWinner.AI_changeAttitudeExtra(iData4,2)
        if pWinner.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
          popupInfo.addPopup(iData2)
        if pLoser.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_2",(pVassal.getCivilizationAdjective(4),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
          popupInfo.addPopup(iData3)
      else:
        # Beziehungsstatus aendern
        pLoser.AI_changeAttitudeExtra(iData4,3)
        pWinner.AI_changeAttitudeExtra(iData4,-1)
        if pWinner.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_3",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
          popupInfo.addPopup(iData2)
        if pLoser.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_4",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
          popupInfo.addPopup(iData3)

    # 1. Schritt HI-Winner und HI-Vasall
    if iData1 == 689:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)
      pVassal = gc.getPlayer(iData4)
      #iWinnerTeam = pWinner.getTeam()
      #pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      #pLoserTeam = gc.getTeam(iLoserTeam)

      # Winner bietet dem Vasall ein Angebot an (iData5 = Gold)
      if iData5 > 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iData5,gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription())) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iData4)
              popupInfo.setFlags(iData5)
              popupInfo.setOnClickedPythonCallback("popupVassal11") # EntryPoints/CvScreenInterface und CvGameUtils / 690
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription())), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_NO",()), "")
              iRand = 1 + self.myRandom(9, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
              popupInfo.addPopup(iData4)

      # Winner hat kein Interesse
      # Vasall darf entscheiden, ob er Krieg erklaert
      else:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iData4)
              popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
              popupInfo.addPopup(iData4)

    # HI Vasall: Kriegserklaerung an Hegemon oder Botschafterkill
    if iData1 == 690:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)
      pVassal = gc.getPlayer(iData4)
      #iWinnerTeam = pWinner.getTeam()
      #pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      #pLoserTeam = gc.getTeam(iLoserTeam)

      # Botschafter-Kill
      if iData5 == -1:
        pWinner.AI_changeAttitudeExtra(iData4,-1)
        if pWinner.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),pVassal.getCivilizationShortDescription(0))) )
              popupInfo.addPopup(iData2)

      # Angebot angenommen mit Kriegserklaerung
      else:
        # Zuerst mit allen Frieden schliessen
        iVassalTeam = pVassal.getTeam()
        pVassalTeam = gc.getTeam(iVassalTeam)
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
          if gc.getPlayer(i).isAlive():
            iTeam = gc.getPlayer(i).getTeam()
            if pVassalTeam.isAtWar(iTeam): gc.getTeam(iTeam).makePeace(pVassalTeam.getID())

        # Danach Krieg erklaeren
        gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)
        pVassal.changeGold(iData5)
        pWinner.changeGold(iData5 * (-1))
        if iData4 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

        if pWinner.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription() )) )
          popupInfo.addPopup(iData2)

    # HI Vasall erklaert eigenmaechtig Krieg gegen Hegemon
    if iData1 == 691:
      pWinner = gc.getPlayer(iData2)
      pLoser = gc.getPlayer(iData3)
      pVassal = gc.getPlayer(iData4)
      #iWinnerTeam = pWinner.getTeam()
      #pWinnerTeam = gc.getTeam(iWinnerTeam)
      iLoserTeam = pLoser.getTeam()
      #pLoserTeam = gc.getTeam(iLoserTeam)

      gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)

      if pWinner.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription() )) )
          popupInfo.addPopup(iData2)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Vasallen Ende --------------------------------------------------------
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Sklaven -> Palast
    if iData1 == 692:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Palace(pCity, pUnit)

    # Sklaven -> Tempel
    if iData1 == 693:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Temple(pCity, pUnit)

    # Sklave wird verkauft (am Sklavenmarkt)
    if iData1 == 694:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iGold = self.myRandom(31, None) + 10
      pPlayer.changeGold(iGold)
      gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
      if pPlayer.isHuman():
         CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_SLAVE_SOLD",(iGold,)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
      # New kill / neuer Kill befehl
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

    # Unit wird verkauft (beim Soeldnerposten) - Sell unit
    if iData1 == 695:
      #Confirmation?
      # 695, 0, 0, iOwner, iUnitID
      if iData2 == 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_CONFIRM_SELL_UNIT",("",)) )
              popupInfo.setData1(iData4)
              popupInfo.setData2(iData5)
              popupInfo.setOnClickedPythonCallback("popupSellUnit") # EntryPoints/CvScreenInterface und CvGameUtils / 695
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_YES2",("",)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_NO2",("",)), "")
              popupInfo.addPopup(iData4)
      # Confirmed
      # 695, 1, 0, iOwner, iUnitID
      else:
        if iData4 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
        pPlayer = gc.getPlayer(iData4)
        pUnit = pPlayer.getUnit(iData5)
        iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost() / 2
        iGold = self.myRandom(iCost-4, None) + 5

        FormationArray = []
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_WILDLIFE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_TRAIT_MARITIME"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_LOYALITAT"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_MERCENARY"))


        # +3 Gold pro Promotion
        iRange = gc.getNumPromotionInfos()
        for j in range(iRange):
          if pUnit.isHasPromotion(j) and j not in FormationArray: iGold += 3

        pPlayer.changeGold(iGold)
        gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
        if pPlayer.isHuman():
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_UNIT_SOLD",(iGold,)),None,2,None,ColorTypes(8),0,0,False,False)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
        #pUnit.kill(1,pUnit.getOwner())

    # Sklaven -> Feuerwehr
    if iData1 == 696:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Feuerwehr(pCity, pUnit)

    # Trojanisches Pferd
    if iData1 == 697:
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iX = iData2
      iY = iData3
      for x in range(3):
        for y in range(3):
          loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isCity():
              pCity = loopPlot.getPlotCity()
              if pCity.getOwner() != pUnit.getOwner():
                if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
                  iDamage = pCity.getDefenseModifier(0)
                  if iDamage > 0:
                    self.doTrojanHorse(pCity, pUnit)

    # Unit bekommt Edle Ruestung
    if iData1 == 699:
      #pPlot = CyMap().plot(iData2, iData3)
      #pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iCost = gc.getUnitInfo(pUnit.getUnitType()).getCombat() * 12
      if iCost < 0: iCost * (-1)
      pPlayer.changeGold(-iCost)
      iPromo = gc.getInfoTypeForString("PROMOTION_EDLE_RUESTUNG")
      pUnit.setHasPromotion(iPromo, True)
      pUnit.finishMoves()
      self.doGoToNextUnit(pPlayer, pUnit)

    # Pillage Road
    if iData1 == 700:
      pPlot = CyMap().plot(iData2, iData3)
      pPlot.setRouteType(RouteTypes.NO_ROUTE)
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      pUnit.getGroup().setActivityType(-1) # to reload the map!
      pUnit.finishMoves()
      self.doGoToNextUnit(pPlayer, pUnit)

    # Unit bekommt Wellen-Oil
    if iData1 == 701:
      #pPlot = CyMap().plot(iData2, iData3)
      #pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost()
      if iCost <= 0: iCost = 180
      pPlayer.changeGold(-iCost)
      iPromo = gc.getInfoTypeForString("PROMOTION_OIL_ON_WATER")
      pUnit.setHasPromotion(iPromo, True)
      pUnit.finishMoves()
      self.doGoToNextUnit(pPlayer, pUnit)

# Vasallen Technologie +++++++++++++++++++++++++

    # Vassal Tech
    if iData1 == 702:
      # 702 , iHegemon (HI) , iVassal, iTech , iTechCost
      # Yes  : iTech und iTechCost = -1 (+1 Beziehung)
      # Money: iTech und iTechCost
      # NO:  : iTech = -1
      pHegemon = gc.getPlayer(iData2)
      pVassal = gc.getPlayer(iData3)
      iVassalTeam = pVassal.getTeam()
      pVassalTeam = gc.getTeam(iVassalTeam)
      iTech = iData4
      iTechCost = iData5

      # Yes
      if iTech > -1 and iTechCost == -1:
        pVassalTeam.setHasTech(iTech, 1, iData3, 0, 1)
        if pVassal.isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_GETTING_TECH",(gc.getTechInfo(iTech).getDescription (), )))
            popupInfo.addPopup(iData3)
        else: pVassal.AI_changeAttitudeExtra(iData2,1)

      # Money
      elif iTech > -1:
        if pVassal.getGold() >= iTechCost:
          # HI - HI Konfrontation
          if pVassal.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2",(gc.getTechInfo(iTech).getDescription(),iTechCost )) )
              popupInfo.setData1(iData2)
              popupInfo.setData2(iData3)
              popupInfo.setData3(iTech)
              popupInfo.setFlags(iTechCost)
              popupInfo.setOnClickedPythonCallback("popupVassalTech2") # EntryPoints/CvScreenInterface und CvGameUtils / 702
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_YES",("",iTechCost)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_NO",("",)), "")
              popupInfo.addPopup(iData3)
          else:
            pVassalTeam.setHasTech(iTech, 1, iData3, 0, 1)
            pVassal.changeGold(-iTechCost)
            pHegemon.changeGold(iTechCost)
            if iData2 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_THX",(gc.getTechInfo(iTech).getDescription (),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
        else:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_HAS_NO_MONEY",(gc.getTechInfo(iTech).getDescription (), iTechCost)))
            popupInfo.addPopup(iData2)

      # No
      elif not pVassal.isHuman(): pVassal.AI_changeAttitudeExtra(iData2,-1)

    # Vassal Tech (HI-HI)
    if iData1 == 703:
      # 702 , iHegemon (HI) , iVassal (HI), iTech , iTechCost
      # Yes  : iTech und iTechCost
      # NO:  : iTechCost = -1
      pHegemon = gc.getPlayer(iData2)
      pVassal = gc.getPlayer(iData3)
      iVassalTeam = pVassal.getTeam()
      pVassalTeam = gc.getTeam(iVassalTeam)
      iTech = iData4
      iTechCost = iData5

      if iData5 == -1:
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_DECLINE",("",)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_DECLINE",("", )))
            popupInfo.addPopup(iData2)
      else:
            pVassalTeam.setHasTech(iTech, 1, iData3, 0, 1)
            pVassal.changeGold(-iTechCost)
            pHegemon.changeGold(iTechCost)
            if iData2 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')
            # Meldungen
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_THX",(gc.getTechInfo(iTech).getDescription (),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_GETTING_TECH",(gc.getTechInfo(iTech).getDescription (), )))
            popupInfo.addPopup(iData3)


    # Religionsaustreibung
    if iData1 == 704:
      # 704, iPlayer, iCity, iButton, iUnit
      self.doInquisitorPersecution2(iData2, iData3, iData4, -1, iData5)


    # Veteran -> Eliteunit, Bsp: Principes + Hastati Combat4 -> Triarii mit Combat3 - Belobigung
    if iData1 == 705:
      # iData1,... 705, 0, iNewUnit, iPlayer, iUnitID
      self.doUpgradeVeteran(gc.getPlayer(iData4).getUnit(iData5), iData3)


    # Renegade City (Keep or raze) TASK_RAZE / TASK_DISBAND
    if iData1 == 706:
      # 706 , iWinner , iCityID, iLoser , keep(0), enslave(1) or raze(2)
      pPlayer = gc.getPlayer(iData2)
      pCity = pPlayer.getCity(iData3)
      if iData5 == 1:
        if pCity != None:
          # --- Getting goldkarren / treasure / Beutegold and slaves / Sklaven ------
          iPop = pCity.getPopulation()
          if iPop > 2: iNum = int(iPop / 2)
          else: iNum = 1

          if iNum > 0:
            for _ in itertools.repeat(None, iNum):
              pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pCity.setPopulation(iNum)
      elif iData5 == 2:
        if pCity != None:
          # --- Getting goldkarren / treasure / Beutegold ------
          iBeute = int(pCity.getPopulation() / 2) + 1
          ##if iBeute > 0: das ist >=1
          for _ in itertools.repeat(None, iBeute):
            pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          pPlayer.disband(pCity)


    # Hire or Commission Mercenary Menu
    if iData1 == 707:
       # iData1, iData2, ...
       # 707, iCityID, -1, -1, iPlayer
       pPlayer = gc.getPlayer(iData5)
       pCity = pPlayer.getCity(iData2)

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_MAIN" + str(1 + self.myRandom(5, None)),(pCity.getName(), )) )
       popupInfo.setData1(iData2) # CityID
       popupInfo.setData2(iData5) # iPlayer
       popupInfo.setOnClickedPythonCallback("popupMercenariesMain") # EntryPoints/CvScreenInterface und CvGameUtils -> 708, 709 usw
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE",("", )), "Art/Interface/Buttons/Actions/button_action_mercenary_hire.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN",("", )), "Art/Interface/Buttons/Actions/button_action_mercenary_assign.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iData5)

    # Hire Mercenaries
    if iData1 == 708:
       # iData1, iData2, ... iData5 = iPlayer
       # 708, iCityID, iButtonID (Typ), iButtonID (Unit), iButtonID (Cancel)
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)
       pCity = pPlayer.getCity(iData2)
       iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
       iMinRanking = 1 # trainiert
       iMaxRanking = 3 # per Unit, 3 = kampferprobt

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE2",("", )) )
       popupInfo.setData1(iData2)
       popupInfo.setData3(iPlayer)

       # Check neighbours
       Neighbors = []
       # Eigene CIV inkludieren
       if pCity.isConnectedToCapital(iPlayer): Neighbors.append(pPlayer)
       iRange = gc.getMAX_PLAYERS()
       for iAllPlayer in range (iRange):
           # Nachbarn inkludieren
           if pCity.isConnectedToCapital(iAllPlayer):
              Neighbors.append(gc.getPlayer(iAllPlayer))
           # alt:
           #ThisPlayer = gc.getPlayer(iAllPlayer)
           #if ThisPlayer.isAlive():
           #  if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
           #    Neighbors.append(ThisPlayer)
         # ------------------

       if iData3 == -1:

         if len(Neighbors) == 0:
           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
           popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE3",("", )))
           popupInfo.addPopup(iPlayer)
         else:
           popupInfo.setOnClickedPythonCallback("popupMercenariesHire")
           popupInfo.addPythonButton(gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ARCHER")).getDescription(), gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ARCHER")).getButton())
           popupInfo.addPythonButton(gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MELEE")).getDescription(), gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MELEE")).getButton())
           popupInfo.addPythonButton(gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")).getDescription(), gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")).getButton())
           popupInfo.addPythonButton(gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT")).getDescription(), gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT")).getButton())
           popupInfo.addPythonButton(gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_NAVAL")).getDescription(), gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_NAVAL")).getButton())
           popupInfo.setData2(-1)

       else:

         # PAEInstanceHiringModifier per turn
         iMultiplier = 0
         iPAEInstanceIndex = -1
         #if any(iPlayer in s[0] for s in self.PAEInstanceHiringModifier):
         if len(self.PAEInstanceHiringModifier) > 0:
           for s in self.PAEInstanceHiringModifier:
             iPAEInstanceIndex += 1
             if s[0] == iPlayer:
               iMultiplier = s[1] + 1
               break
         # --------

         # Unit list
         popupInfo.setOnClickedPythonCallback("popupMercenariesHireUnits")
         popupInfo.setData2(iData3)
         # ------------------

         if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM")): bCivicSoeldner = True
         else: bCivicSoeldner = False

         # Archers
         if iData3 == 0:

           # Hire Units
           if iData4 != -1:
             iUnit = -1
             if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_PELTIST")
             if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_ARCHER")
             if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
             if iData4 == 3: iUnit = gc.getInfoTypeForString("UNIT_SKIRMISHER")

             if iUnit != -1:
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4

               if pPlayer.getGold() < iCost:
                 CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                 iUnit = -1

             if iUnit != -1:
                if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer.changeGold(-iCost)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(iUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setHasPromotion(iPromo, True)
                NewUnit.setImmobileTimer(1)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)

                # PAEInstanceHiringModifier per turn
                if iPAEInstanceIndex > -1:
                  self.PAEInstanceHiringModifier[iPAEInstanceIndex] = (iPlayer,iMultiplier)
                else:
                  self.PAEInstanceHiringModifier.append((iPlayer,1))
                iMultiplier += 1


           # List Units

           # Check knowledge
           # UNIT_ARCHER: TECH_ARCHERY2
           # UNIT_COMPOSITE_ARCHER: TECH_ARCHERY3
           # UNIT_SKIRMISHER: TECH_SKIRMISH_TACTICS
           bUnit1 = false
           bUnit2 = false
           bUnit3 = false
           for Neighbor in Neighbors:
             if bUnit1 and bUnit2 and bUnit3: break
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY2")): bUnit1 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY3")): bUnit2 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SKIRMISH_TACTICS")):
               ## ab Plaenkler duerfen alle Kompositbogis
               bUnit2 = true
               bUnit3 = true


           iUnit = gc.getInfoTypeForString("UNIT_PELTIST")
           iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
           iCost += iCost / 10 * 2 * iMultiplier
           if bCivicSoeldner: iCost -= iCost/4
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit1:
             iUnit = gc.getInfoTypeForString("UNIT_ARCHER")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit2:
             iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit3:
             iUnit = gc.getInfoTypeForString("UNIT_SKIRMISHER")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())


         # Melee
         elif iData3 == 1:

           # Hire Units
           if iData4 != -1:
             if pPlayer.getCurrentEra() <= 2:
               if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN")
               if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
               if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_AXEMAN")
               if iData4 == 3: iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT"))
               if iData4 == 4: iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
               if iData4 == 5: iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")
             else:
               if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
               if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")
               if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_AXEMAN2")
               if iData4 == 3: iUnit = gc.getInfoTypeForString("UNIT_SWORDSMAN")
               if iData4 == 4: iUnit = gc.getInfoTypeForString("UNIT_WURFAXT")

             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4

             if pPlayer.getGold() < iCost:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                iUnit = -1

             if iUnit != -1:
                if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer.changeGold(-iCost)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(iUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setHasPromotion(iPromo, True)
                #NewUnit.finishMoves()
                NewUnit.setImmobileTimer(1)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)

                # PAEInstanceHiringModifier per turn
                if iPAEInstanceIndex > -1:
                  self.PAEInstanceHiringModifier[iPAEInstanceIndex] = (iPlayer,iMultiplier)
                else:
                  self.PAEInstanceHiringModifier.append((iPlayer,1))
                iMultiplier += 1

           # List Units

           # Check knowledge
           # UNIT_LIGHT_SPEARMAN: TECH_SPEERSPITZEN
           # UNIT_AXEWARRIOR: TECH_BEWAFFNUNG
           # UNIT_AXEMAN: TECH_BEWAFFNUNG2 + Bronze or Iron
           # UNITCLASS_KURZSCHWERT: TECH_BEWAFFNUNG3 + Bronze or Iron
           # UNIT_SCHILDTRAEGER: TECH_BEWAFFNUNG4 + Bronze or Iron
           # UNIT_SPEARMAN: TECH_BUERGERSOLDATEN + Bronze or Iron
           # UNIT_AXEMAN2: TECH_BUERGERSOLDATEN + Iron
           # UNIT_SWORDSMAN: TECH_BEWAFFNUNG5 + Iron
           # UNIT_WURFAXT: TECH_WURFAXT + Iron
           iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
           iBonus2 = gc.getInfoTypeForString("BONUS_IRON")

           bUnit1 = false
           bUnit2 = false
           bUnit3 = false
           bUnit4 = false
           bUnit5 = false
           bUnit6 = false

           # vor Klassik Light Spearman and Axewarrior fix
           # ab Klassik Spearman und Shield bearer fix
           bUnit1 = true
           bUnit2 = true

           for Neighbor in Neighbors:
             if bUnit3 and bUnit4 and bUnit5 and bUnit6: break
             if pPlayer.getCurrentEra() <= 2:
               if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")): bUnit3 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG3")): bUnit4 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")): bUnit5 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): bUnit6 = true
             else:
               if Neighbor.hasBonus(iBonus2):
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): bUnit3 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG5")): bUnit4 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WURFAXT")): bUnit5 = true


           if pPlayer.getCurrentEra() <= 2:
             iUnit = gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             iUnit = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit3:
               iUnit = gc.getInfoTypeForString("UNIT_AXEMAN")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit4:
               iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT"))
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit5:
               iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit6:
               iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           else:
             iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit3:
               iUnit = gc.getInfoTypeForString("UNIT_AXEMAN2")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit4:
               iUnit = gc.getInfoTypeForString("UNIT_SWORDSMAN")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit5:
               iUnit = gc.getInfoTypeForString("UNIT_WURFAXT")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())


         # Mounted
         elif iData3 == 2:

           # Hire Units
           if iData4 != -1:
             if pPlayer.getCurrentEra() <= 2:
               if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT")
               if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER")
               if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_CHARIOT")
             else:
               if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_CHARIOT")
               if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_HORSEMAN")
               if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_HORSE_ARCHER")
               if iData4 == 3: iUnit = gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN")

             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4

             if pPlayer.getGold() < iCost:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                iUnit = -1

             if iUnit != -1:
                if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer.changeGold(-iCost)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(iUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setHasPromotion(iPromo, True)
                #NewUnit.finishMoves()
                NewUnit.setImmobileTimer(1)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)

                # PAEInstanceHiringModifier per turn
                if iPAEInstanceIndex > -1:
                  self.PAEInstanceHiringModifier[iPAEInstanceIndex] = (iPlayer,iMultiplier)
                else:
                  self.PAEInstanceHiringModifier.append((iPlayer,1))
                iMultiplier += 1

           # List Units

           # Check knowledge
           # UNIT_LIGHT_CHARIOT: TECH_CHARIOTS
           # UNIT_CHARIOT_ARCHER: TECH_PFERDEZUCHT + TECH_ARCHERY2
           # UNIT_CHARIOT: TECH_THE_WHEEL3 + Horse + Bronze or Iron
           # UNIT_HORSEMAN: TECH_HORSEBACK_RIDING_2 + Horse
           # UNIT_HORSE_ARCHER: TECH_HORSEBACK_RIDING_3 + TECH_HORSE_ARCHER + Horse
           # UNIT_HEAVY_HORSEMAN: TECH_CAVALRY + Horse + Bronze or Iron
           iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
           iBonus2 = gc.getInfoTypeForString("BONUS_IRON")
           iBonus3 = gc.getInfoTypeForString("BONUS_HORSE")

           bUnit1 = false
           bUnit2 = false
           bUnit3 = false
           bUnit4 = false

           for Neighbor in Neighbors:
             if bUnit1 and bUnit2 and bUnit3 and bUnit4: break
             if pPlayer.getCurrentEra() <= 2:
               if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_CHARIOTS")): bUnit1 = true
               if Neighbor.hasBonus(iBonus3):
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PFERDEZUCHT")) and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY2")):
                   bUnit2 = true
                 if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                   if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_THE_WHEEL3")):
                     bUnit2 = true
                     bUnit3 = true
             else:
               if Neighbor.hasBonus(iBonus3):
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_2")): bUnit2 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_3")) and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSE_ARCHER")): bUnit3 = true
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_CAVALRY")):
                   if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                     bUnit3 = true
                     bUnit4 = true

           if pPlayer.getCurrentEra() <= 2:
             if bUnit1:
               iUnit = gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit2:
               iUnit = gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit3:
               iUnit = gc.getInfoTypeForString("UNIT_CHARIOT")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           else:
             iUnit = gc.getInfoTypeForString("UNIT_CHARIOT")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit2:
               iUnit = gc.getInfoTypeForString("UNIT_HORSEMAN")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit3:
               iUnit = gc.getInfoTypeForString("UNIT_HORSE_ARCHER")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
             if bUnit4:
               iUnit = gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())


         # Elephants
         elif iData3 == 3:

           # Hire Units
           if iData4 != -1:
             iUnit = gc.getInfoTypeForString("UNIT_WAR_ELEPHANT")

             iCost = PyInfo.UnitInfo(iUnit).getProductionCost() * 2
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4

             if pPlayer.getGold() < iCost:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                iUnit = -1

             if iUnit != -1:
                if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer.changeGold(-iCost)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(iUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setHasPromotion(iPromo, True)
                #NewUnit.finishMoves()
                NewUnit.setImmobileTimer(1)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)

                # PAEInstanceHiringModifier per turn
                if iPAEInstanceIndex > -1:
                  self.PAEInstanceHiringModifier[iPAEInstanceIndex] = (iPlayer,iMultiplier)
                else:
                  self.PAEInstanceHiringModifier.append((iPlayer,1))
                iMultiplier += 1

           # List Units

           # Check knowledge
           # UNIT_WAR_ELEPHANT: TECH_ELEFANTENZUCHT + BONUS_IVORY
           iBonus1 = gc.getInfoTypeForString("BONUS_IVORY")

           bUnit1 = false

           for Neighbor in Neighbors:
                if bUnit1: break
                if Neighbor.hasBonus(iBonus1):
                   if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
                     bUnit1 = true

           if bUnit1:
               iUnit = gc.getInfoTypeForString("UNIT_WAR_ELEPHANT")
               iCost = PyInfo.UnitInfo(iUnit).getProductionCost() * 2
               iCost += (iCost / 10) * 2 * iMultiplier
               if bCivicSoeldner: iCost -= iCost/4
               popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())

         # Ships / Vessels
         if iData3 == 4:

           # Hire Units
           if iData4 != -1:
             if iData4 == 0: iUnit = gc.getInfoTypeForString("UNIT_KONTERE")
             if iData4 == 1: iUnit = gc.getInfoTypeForString("UNIT_BIREME")
             if iData4 == 2: iUnit = gc.getInfoTypeForString("UNIT_TRIREME")
             if iData4 == 3: iUnit = gc.getInfoTypeForString("UNIT_GALLEY")
             if iData4 == 4: iUnit = gc.getInfoTypeForString("UNIT_LIBURNE")

             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += (iCost / 10) * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4

             if pPlayer.getGold() < iCost:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
                iUnit = -1

             if iUnit != -1:
                if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
                pPlayer.changeGold(-iCost)
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(iUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setHasPromotion(iPromo, True)
                NewUnit.setImmobileTimer(1)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)

                # PAEInstanceHiringModifier per turn
                if iPAEInstanceIndex > -1:
                  self.PAEInstanceHiringModifier[iPAEInstanceIndex] = (iPlayer,iMultiplier)
                else:
                  self.PAEInstanceHiringModifier.append((iPlayer,1))
                iMultiplier += 1


           # List Units

           # Check knowledge
           # UNIT_KONTERE: TECH_COLONIZATION2
           # UNIT_BIREME:  TECH_RUDERER2  (+ Bronze)
           # UNIT_TRIREME: TECH_RUDERER3  (+ BUILDING_STADT + Bronze oder Eisen)
           # UNIT_GALLEY:  TECH_WARSHIPS  (+ BUILDING_STADT + BONUS_COAL)
           # UNIT_LIBURNE: TECH_WARSHIPS2 (+ BUILDING_STADT + Eisen)

           #iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
           #iBonus2 = gc.getInfoTypeForString("BONUS_IRON")
           #iBonus3 = gc.getInfoTypeForString("BONUS_COAL")
           #iBuilding1 = gc.getInfoTypeForString("BUILDING_STADT")

           bUnit1 = false
           bUnit2 = false
           bUnit3 = false
           bUnit4 = false
           bUnit5 = false
           for Neighbor in Neighbors:
             if bUnit1 and bUnit2 and bUnit3 and bUnit4 and bUnit5: break
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_COLONIZATION2")): bUnit1 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_RUDERER2")): bUnit2 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_RUDERER3")): bUnit3 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WARSHIPS")): bUnit4 = true
             if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WARSHIPS2")): bUnit5 = true


           if bUnit1:
             iUnit = gc.getInfoTypeForString("UNIT_KONTERE")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit2:
             iUnit = gc.getInfoTypeForString("UNIT_BIREME")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit3:
             iUnit = gc.getInfoTypeForString("UNIT_TRIREME")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit4:
             iUnit = gc.getInfoTypeForString("UNIT_GALLEY")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())
           if bUnit5:
             iUnit = gc.getInfoTypeForString("UNIT_LIBURNE")
             iCost = PyInfo.UnitInfo(iUnit).getProductionCost()
             iCost += iCost / 10 * 2 * iMultiplier
             if bCivicSoeldner: iCost -= iCost/4
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(iUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(iUnit).getButton())


         # -----------------------

         popupInfo.setData2(iData3)
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MAIN_MENU_GO_BACK",("", )), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")


       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)


    # Commission Mercenaries (CIV)
    if iData1 == 709:
       # iData1, iData2, ...
       # 709, (1) -1 (2) iButtonId (CIV) , -1, -1, iPlayer
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       # Check neighbours
       Neighbors = []
       iRange = gc.getMAX_PLAYERS()
       for iAllPlayer in range (iRange):
         ThisPlayer = gc.getPlayer(iAllPlayer)
         if iAllPlayer != gc.getBARBARIAN_PLAYER() and iAllPlayer != iPlayer:
           if ThisPlayer.isAlive():
             if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
               Neighbors.append(iAllPlayer)

       # iButtonId of CIV
       # Forward to 2nd screen -> 710
       #if iData2 != -1:
         #i = 0
         #for j in Neighbors:
           #if i == iData2:
             #iData1 = 710 # geht direkt weiter in dieser def
             #iData2 = j
             #break
           #i += 1

       if iData2 != -1 and iData2 < len(Neighbors):
         iData2 = Neighbors[iData2]
         iData1 = 710

       # First screen (Civilizations)
       else:
         popupInfo = CyPopupInfo()
         popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
         popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN1",("", )) )
         popupInfo.setOnClickedPythonCallback("popupMercenariesAssign1") # EntryPoints/CvScreenInterface -> 709
         popupInfo.setData3(iPlayer)

         # List neighbors ---------
         # Friendly >= +10
         # Pleased >= +3
         # Cautious: -
         # Annoyed: <= -3
         # Furious: <= -10
         # ATTITUDE_FRIENDLY
         # ATTITUDE_PLEASED
         # ATTITUDE_CAUTIOUS
         # ATTITUDE_ANNOYED
         # ATTITUDE_FURIOUS
         if len(Neighbors) == 0:
           popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN1_1",("", )) )
         else:
           for i in Neighbors:
             ThisPlayer = gc.getPlayer(i)
             Att = ThisPlayer.AI_getAttitude(iPlayer)
             if   Att == AttitudeTypes.ATTITUDE_FRIENDLY: szBuffer = "<color=0,255,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_PLEASED:  szBuffer = "<color=0,155,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_CAUTIOUS: szBuffer = "<color=255,255,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_ANNOYED:  szBuffer = "<color=255,180,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_FURIOUS:  szBuffer = "<color=255,0,0,255>"

             szBuffer = szBuffer + " (" + localText.getText("TXT_KEY_"+str(Att), ()) + ")"
             popupInfo.addPythonButton(ThisPlayer.getCivilizationShortDescription(0) + szBuffer, gc.getCivilizationInfo(ThisPlayer.getCivilizationType()).getButton())
             #popupInfo.addPythonButton(gc.getCivilizationInfo(ThisPlayer.getCivilizationType()).getText(), gc.getCivilizationInfo(ThisPlayer.getCivilizationType()).getButton())

         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
         popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
         popupInfo.addPopup(iPlayer)


    # Commission Mercenaries (Inter/national mercenaries)
    # on-site
    # local
    # international
    # elite
    if iData1 == 710:
       # Werte von 709 weitervererbt
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2",("", )) )
       popupInfo.setOnClickedPythonCallback("popupMercenariesAssign2") # EntryPoints/CvScreenInterface -> 711
       popupInfo.setData1(iData2) # iTargetPlayer
       popupInfo.setData3(iPlayer) # iPlayer

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_1",("", )), gc.getCivilizationInfo(gc.getPlayer(iData2).getCivilizationType()).getButton())
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_2",("", )), gc.getCivilizationInfo(pPlayer.getCivilizationType()).getButton())
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_3",("", )), "Art/Interface/Buttons/Actions/button_action_merc_international.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_4",("", )), "Art/Interface/Buttons/Actions/button_action_merc_elite.dds")

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (mercenary size)
    # small
    # medium
    # large
    # army
    if iData1 == 711:
       # iData1, iData2, iData3, ...
       # 710, iTargetPlayer, iFaktor, -1, iPlayer
       # iFaktor:
       # 1: Urban (iTargetCiv) +200 Kosten
       # 2: Own units          +300
       # 3: international      +400
       # 4: elite              +500
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3",("", )) )
       popupInfo.setOnClickedPythonCallback("popupMercenariesAssign3") # EntryPoints/CvScreenInterface -> 712
       popupInfo.setData1(iData2) # iTargetPlayer
       popupInfo.setData2(iData3) # iFaktor
       popupInfo.setData3(iPlayer) # iPlayer

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_1",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries1.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_2",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries2.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_3",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries3.dds")
       if iData3 != 4: popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_4",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries4.dds")

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (primary unit types)
    # defensice
    # ranged combat
    # offensive
    # city attack
    if iData1 == 712:
       # iData1, iData2, iData3, ...
       # 710, iTargetPlayer, iFaktor, -1, iPlayer
       # iFaktor:
       # 10: small group    +0
       # 20: medium group   +150
       # 30: big group      +300
       # 40: huge group     +400
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4",("", )) )
       popupInfo.setOnClickedPythonCallback("popupMercenariesAssign4") # EntryPoints/CvScreenInterface -> 713
       popupInfo.setData1(iData2) # iTargetPlayer
       popupInfo.setData2(iData3) # iFaktor
       popupInfo.setData3(iPlayer) # iPlayer

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_1",("", )), "Art/Interface/Buttons/Promotions/tarnung.dds")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_2",("", )), ",Art/Interface/Buttons/Promotions/Cover.dds,Art/Interface/Buttons/Promotions_Atlas.dds,2,5")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_3",("", )), ",Art/Interface/Buttons/Promotions/Shock.dds,Art/Interface/Buttons/Promotions_Atlas.dds,4,5")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_4",("", )), ",Art/Interface/Buttons/Promotions/CityRaider1.dds,Art/Interface/Buttons/Promotions_Atlas.dds,5,2")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_UNITCOMBAT_NAVAL",("", )), ",Art/Interface/Buttons/Promotions/Naval_Units.dds,Art/Interface/Buttons/Promotions_Atlas.dds,3,7")

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (siege units)
    if iData1 == 713:
       # iData1, iData2, iData3, ...
       # 710, iTargetPlayer, iFaktor, -1, iPlayer
       # iFaktor:
       # 100: defensive
       # 200: ranged
       # 300: offensive
       # 400: city raiders
       # 500: naval units
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5",("", )) )
       popupInfo.setOnClickedPythonCallback("popupMercenariesAssign5") # EntryPoints/CvScreenInterface -> 714
       popupInfo.setData1(iData2) # iTargetPlayer
       popupInfo.setData2(iData3) # iFaktor
       popupInfo.setData3(iPlayer) # iPlayer

       if gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_MECHANIK")) > 0:
         iUnit = gc.getInfoTypeForString("UNIT_BATTERING_RAM2")
         szName = localText.getText("TXT_KEY_UNIT_BATTERING_RAM2_PLURAL", ())
       elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_WEHRTECHNIK")) > 0:
         iUnit = gc.getInfoTypeForString("UNIT_BATTERING_RAM")
         szName = localText.getText("TXT_KEY_UNIT_BATTERING_RAM_PLURAL", ())
       elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_BELAGERUNG")) > 0:
         iUnit = gc.getInfoTypeForString("UNIT_RAM")
         szName = localText.getText("TXT_KEY_UNIT_RAM_PLURAL", ())
       else: iUnit = -1

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_1",("", )), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")
       if iUnit != -1:
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 2, 50)), gc.getUnitInfo(iUnit).getButton())
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 4, 90)), gc.getUnitInfo(iUnit).getButton())
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 6, 120)), gc.getUnitInfo(iUnit).getButton())

       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (confirmation)
    if iData1 == 714:
       # iData1, iData2, iData3, ...
       # 710, iTargetPlayer, iFaktor, -1, iPlayer
       # iFaktor:
       # 1000: no siege +0
       # 2000: 2x       +50
       # 3000: 4x       +90
       # 4000: 6x       +120
       iPlayer = iData5
       pPlayer = gc.getPlayer(iPlayer)

       # Kosten berechnen
       sFaktor = str(iData3)
       iCost = 0
       # siege units
       if sFaktor[0] == "2":   iCost += 50
       elif sFaktor[0] == "3": iCost += 90
       elif sFaktor[0] == "4": iCost += 120
       # size
       if sFaktor[2] == "2":   iCost += 150
       elif sFaktor[2] == "3": iCost += 300
       elif sFaktor[2] == "4": iCost += 400
       # inter/national
       if sFaktor[3] == "1":   iCost += 200
       elif sFaktor[3] == "2": iCost += 300
       elif sFaktor[3] == "3": iCost += 400
       elif sFaktor[3] == "4": iCost += 500
       # ----------

       szText = ""
       if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM")):
         iCost -= iCost/4
         szText = CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN_BONUS",(25,))

       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN6",(gc.getPlayer(iData2).getCivilizationShortDescription(0), iCost, szText)) )
       popupInfo.setOnClickedPythonCallback("popupMercenariesAssign6") # EntryPoints/CvScreenInterface -> 715
       popupInfo.setData1(iData2) # iTargetPlayer
       popupInfo.setData2(iData3) # iFaktor
       popupInfo.setData3(iPlayer) # iPlayer

       # Confirm
       popupInfo.addPythonButton(CyTranslator().getText( "TXT_KEY_POPUP_MERCENARIES_ASSIGN6_" + str(1 + self.myRandom(13, None)) , ("", ) ), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
       popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (confirmation)
    if iData1 == 715:
       # iData1, iData2, iData3, ...
       # 715, iTargetPlayer, iFaktor, -1, iPlayer
       # iFaktor: 1111 - 4534
       self.doComissionMercenaries(iData2,iData3,iData5)

    # Mercenaries Torture / Folter
    if iData1 == 716:
       # iData1, iData2, iData3
       # 716, iMercenaryCiv, iPlayer
       iPlayer = iData3
       iMercenaryCiv = iData2
       pPlayer = gc.getPlayer(iPlayer)

       if pPlayer.getGold() < 80:
         if gc.getPlayer(iPlayer).isHuman():
           CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
           popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
           popupInfo.addPopup(iPlayer)
       else:

         pPlayer.changeGold(-80)

         if 0 == self.myRandom(2, None): self.doFailedMercenaryTortureMessage(iPlayer)
         else:

           # Check neighbours
           Neighbors = []
           iRange = gc.getMAX_PLAYERS()
           for iAllPlayer in range (iRange):
             ThisPlayer = gc.getPlayer(iAllPlayer)
             if iAllPlayer != gc.getBARBARIAN_PLAYER():
               if ThisPlayer.isAlive():
                 if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()) or iAllPlayer == iPlayer:
                   Neighbors.append(iAllPlayer)

           # select neighbours if more than 5
           while len(Neighbors) > 5:
             iRand = self.myRandom(len(Neighbors), None)
             if Neighbors[iRand] != iMercenaryCiv:
               Neighbors.remove(Neighbors[iRand])

           szText = CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE2",("",)) + localText.getText("[NEWLINE]", ())
           # List neighbors ---------
           # ATTITUDE_FRIENDLY
           # ATTITUDE_PLEASED
           # ATTITUDE_CAUTIOUS
           # ATTITUDE_ANNOYED
           # ATTITUDE_FURIOUS
           for i in Neighbors:
             ThisPlayer = gc.getPlayer(i)
             Att = ThisPlayer.AI_getAttitude(iPlayer)
             if   Att == AttitudeTypes.ATTITUDE_FRIENDLY: szBuffer = "<color=0,255,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_PLEASED:  szBuffer = "<color=0,155,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_CAUTIOUS: szBuffer = "<color=255,255,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_ANNOYED:  szBuffer = "<color=255,180,0,255>"
             elif Att == AttitudeTypes.ATTITUDE_FURIOUS:  szBuffer = "<color=255,0,0,255>"

             szText = szText + localText.getText("[NEWLINE][ICON_STAR] <color=255,255,255,255>", ()) + ThisPlayer.getCivilizationShortDescription(0) + szBuffer + " (" + localText.getText("TXT_KEY_"+str(Att), ()) + ")"



           szText = szText + localText.getText("[NEWLINE][NEWLINE]<color=255,255,255,255>", ()) + CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE2_1",("", ))
           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
           popupInfo.setText(szText)
           popupInfo.setData1(iMercenaryCiv) # iMercenaryCiv
           popupInfo.setData2(iPlayer) # iPlayer
           popupInfo.setOnClickedPythonCallback("popupMercenaryTorture2") # EntryPoints/CvScreenInterface und CvGameUtils -> 717
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES1",(75,50)), "")
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES2",(50,25)), "")
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES3",(25,10)), "")
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
           popupInfo.addPopup(iPlayer)


    # Mercenaries Torture 2
    if iData1 == 717:
       # iData1, iData2, iData3, iData4
       # 717, iMercenaryCiv, iPlayer, iButtonId
       iPlayer = iData3
       iMercenaryCiv = iData2
       pPlayer = gc.getPlayer(iPlayer)

       if iData4 == 0:
         iGold = 75
         iChance = 10
       elif iData4 == 1:
         iGold = 50
         iChance = 5
       elif iData4 == 2:
         iGold = 25
         iChance = 2

       if pPlayer.getGold() < iGold:
         if gc.getPlayer(iPlayer).isHuman():
           CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
           popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
           popupInfo.addPopup(iPlayer)
       else:

         pPlayer.changeGold(-iGold)
         if iChance < self.myRandom(20, None): self.doFailedMercenaryTortureMessage(iPlayer)
         else:
           if iPlayer != iMercenaryCiv:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_1",(gc.getPlayer(iMercenaryCiv).getCivilizationShortDescription(0),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
             popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_1",(gc.getPlayer(iMercenaryCiv).getCivilizationShortDescription(0), )))
             popupInfo.addPopup(iPlayer)
           else:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_2",("",)), None, 2, None, ColorTypes(8), 0, 0, False, False)
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
             popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_2",("", )))
             popupInfo.addPopup(iPlayer)

    # END Mercenaries ----------------------

    # Unit FORMATIONS ----------------------
    if iData1 == 718:
       # iData1,... 705, 0, iFormation, iPlayer, iUnitID
       self.doUnitFormation(gc.getPlayer(iData4).getUnit(iData5), iData3)

    # Promotion Trainer Building (Forest 1, Hills1, ...)
    if iData1 == 719:
       # 719, iCityID, iBuilding, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.setNumRealBuilding(iData3,1)
       pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

    # Legendary unit can become a Great General
    if iData1 == 720:
       # 720, 0, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pUnit = pPlayer.getUnit(iData5)

       pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GREAT_GENERAL"), pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

       self.doRetireVeteran(pUnit)

    # Elefantenstall
    if iData1 == 721:
       # 721, iCityID, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE"),1)
       pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

    # Piraten-Feature
    if iData1 == 722:
       # iData2 = 1: Pirat -> normal
       # iData2 = 2: Normal -> Pirat
       # 722, iData2, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pUnit = pPlayer.getUnit(iData5)

       bSwitch = True
       iVisible = pUnit.visibilityRange()
       iRange = iVisible * 2 + 1
       for i in range(iRange):
         for j in range(iRange):
           loopPlot = gc.getMap().plot(pUnit.getX() + i - iVisible, pUnit.getY() + j - iVisible)
           iNumUnits = loopPlot.getNumUnits()
           if iNumUnits > 0:
             for k in range (iNumUnits):
               if iData4 != loopPlot.getUnit(k).getOwner() and loopPlot.getUnit(k).getOwner() != gc.getBARBARIAN_PLAYER():
                 bSwitch = False
                 break
           if not bSwitch: break
         if not bSwitch: break

       if bSwitch:
         if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_KONTERE"): iNewUnit = gc.getInfoTypeForString("UNIT_PIRAT_KONTERE")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_BIREME"):  iNewUnit = gc.getInfoTypeForString("UNIT_PIRAT_BIREME")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_TRIREME"): iNewUnit = gc.getInfoTypeForString("UNIT_PIRAT_TRIREME")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_LIBURNE"): iNewUnit = gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"): iNewUnit = gc.getInfoTypeForString("UNIT_KONTERE")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_BIREME"):  iNewUnit = gc.getInfoTypeForString("UNIT_BIREME")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"): iNewUnit = gc.getInfoTypeForString("UNIT_TRIREME")
         elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"): iNewUnit = gc.getInfoTypeForString("UNIT_LIBURNE")

         # Unload units: geht net weil darin canUnload geprueft wird
         #pUnit.doCommand(CommandTypes.COMMAND_UNLOAD_ALL, -1, -1 )

         #NewUnit = pPlayer.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
         NewUnit = pPlayer.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes(pUnit.getFacingDirection()))
         NewUnit.setExperience(pUnit.getExperience(), -1)
         NewUnit.setLevel(pUnit.getLevel())
         NewUnit.setDamage(pUnit.getDamage(), -1)
         # 1 Bewegungspunkt Verlust
         NewUnit.changeMoves(pUnit.getMoves() + 60)

         #if NewUnit.getName() != sPlot.getUnit(iRand).getName(): NewUnit.setName(sPlot.getUnit(iRand).getName())
         UnitName = pUnit.getName()
         #if UnitName != "" and UnitName != NewUnit.getName(): NewUnit.setName(UnitName)
         if UnitName != gc.getUnitInfo(pUnit.getUnitType()).getText():
            UnitName = re.sub(" \(.*?\)","",UnitName)
            NewUnit.setName(UnitName)
         # Check its promotions
         iRange = gc.getNumPromotionInfos()
         for j in range(iRange):
           if pUnit.isHasPromotion(j):
              NewUnit.setHasPromotion(j, True)

         # Veteran und Mercenary Promo checken
         # Veteran ohne Mercenary bleibt ohne Mercenary
         iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
         if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")):
           if not pUnit.isHasPromotion(iPromoMercenary):
             if NewUnit.isHasPromotion(iPromoMercenary):
                NewUnit.setHasPromotion(iPromoMercenary, False)

         # Original unit killen
         pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

        # changeMoves
       else:
         CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE3",("",)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(11), pUnit.getX() + i - iVisible, pUnit.getY() + j - iVisible, True, True)

    # iData1 723: EspionageMission Info im TechChooser

    # Veteran -> Reservist
    if iData1 == 724:
       # 724, iCityID, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.changeFreeSpecialistCount(19, 1) # SPECIALIST_RESERVIST
       pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

    # Reservist -> Veteran
    if iData1 == 725:
       # iData1, iData2, ... iData5
       # First:  725, iCityID, iPlayer, -1, 0
       # Second: 725, iCityID, iPlayer, iButtonID (Typ), 0
       pPlayer = gc.getPlayer(iData3)
       pCity = pPlayer.getCity(iData2)
       iTeam = pPlayer.getTeam()
       pTeam = gc.getTeam(iTeam)

       iReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST

       # Units
       bUnit1 = true
       bUnit2 = true
       bUnit3 = true
       bUnit4 = true

       # Unit 1
       iUnit1 = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
       if not pCity.canTrain(iUnit1,0,0): bUnit1 = false
       # Unit 2
       iUnit2 = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
       if not pCity.canTrain(iUnit2,0,0):
          bUnit2 = false
          iUnit2 = gc.getInfoTypeForString("UNIT_ARCHER")
       # Unit 3
       iUnit3 = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
       if not pTeam.isHasTech(gc.getUnitInfo(iUnit3).getPrereqAndTech()): bUnit3 = false
       # Unit 4
       iUnit4 = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
       if not (pTeam.isHasTech(gc.getUnitInfo(iUnit4).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE"))): bUnit4 = false

       # Reservist aufstellen
       if iData4 != -1:
           iUnit = -1
           if iData4 == 0 and bUnit1: iUnit = iUnit1
           elif iData4 == 1: iUnit = iUnit2
           elif iData4 == 2 and bUnit3: iUnit = iUnit3
           elif iData4 == 3 and bUnit4: iUnit = iUnit4

           if iUnit != -1:
               NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
               NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
               NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
               NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
               NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

               pCity.changeFreeSpecialistCount(19, -1)
               iReservists -= 1
               #NewUnit.finishMoves()
               NewUnit.setImmobileTimer(1)

       # PopUp
       if iReservists > 0:
         popupInfo = CyPopupInfo()
         popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
         popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_RESERVIST_MAIN",(pCity.getName(), iReservists)) )
         popupInfo.setData1(iData2) # CityID
         popupInfo.setData2(iData3) # iPlayer
         popupInfo.setOnClickedPythonCallback("popupReservists")

         # Button 0: Schildtraeger
         sz = u""
         if not bUnit1: sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE",())
         szText = gc.getUnitInfo(iUnit1).getDescriptionForm(0) + sz
         popupInfo.addPythonButton( szText, gc.getUnitInfo(iUnit1).getButton() )
         # Button 1: Bogenschuetze
         popupInfo.addPythonButton( gc.getUnitInfo(iUnit2).getDescriptionForm(0), gc.getUnitInfo(iUnit2).getButton() )
         # Button 2: Hilfstrupp
         sz = u""
         if not bUnit3: sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE",())
         szText = gc.getUnitInfo(iUnit3).getDescriptionForm(0) + sz
         popupInfo.addPythonButton( szText, gc.getUnitInfo(iUnit3).getButton() )
         # Button 3: Berittener Hilfstrupp
         sz = u""
         if not bUnit4: sz += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE",())
         szText = gc.getUnitInfo(iUnit4).getDescriptionForm(0) + sz
         popupInfo.addPythonButton( szText, gc.getUnitInfo(iUnit4).getButton() )

         # Cancel button
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
         popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
         popupInfo.addPopup(iData3)

    # Bonusverbreitung UNIT_SUPPLY_FOOD
    if iData1 == 726:
       # 726, iPage, iButtonId, iPlayer, iUnitID
       iPlayer = iData4
       pPlayer = gc.getPlayer(iPlayer)

       # First Page
       if iData2 == -1:
         popupInfo = CyPopupInfo()
         popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
         popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG",("", )) )
         popupInfo.setOnClickedPythonCallback("popupBonusverbreitung")
         popupInfo.setData1(iData4) # iPlayer
         popupInfo.setData2(iData5) # iUnitID
         popupInfo.setData3(-1)
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_1",("", )), "Art/Interface/Buttons/Actions/button_bonusverbreitung1.dds")
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_2",("", )), "Art/Interface/Buttons/Actions/button_bonusverbreitung2.dds")
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_3",("", )), "Art/Interface/Buttons/Actions/button_bonusverbreitung3.dds")
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_4",("", )), "Art/Interface/Buttons/Actions/button_bonusverbreitung4.dds")
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
         popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
         popupInfo.addPopup(iPlayer)
       else:

         # Inits
         pUnit = pPlayer.getUnit(iData5)
         pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())
         pCity = pPlot.getPlotCity()
         lBonus = []

         # Getreide
         if iData2 == 0:
           lBonus.append("")
           lBonus.append(gc.getInfoTypeForString("BONUS_WHEAT"))
           lBonus.append(gc.getInfoTypeForString("BONUS_GERSTE"))
           lBonus.append(gc.getInfoTypeForString("BONUS_HAFER"))
           lBonus.append(gc.getInfoTypeForString("BONUS_ROGGEN"))
           lBonus.append(gc.getInfoTypeForString("BONUS_HIRSE"))
           lBonus.append(gc.getInfoTypeForString("BONUS_RICE"))
         # Vieh
         elif iData2 == 1:
           lBonus.append("")
           lBonus.append(gc.getInfoTypeForString("BONUS_COW"))
           lBonus.append(gc.getInfoTypeForString("BONUS_PIG"))
           lBonus.append(gc.getInfoTypeForString("BONUS_SHEEP"))
         # Plantage
         elif iData2 == 2:
           lBonus.append("")
           lBonus.append(gc.getInfoTypeForString("BONUS_OLIVES"))
           lBonus.append(gc.getInfoTypeForString("BONUS_DATTELN"))
         # Kamele
         elif iData2 == 3:
           lBonus.append("")
           lBonus.append(gc.getInfoTypeForString("BONUS_CAMEL"))

         # Bonusgut
         iRange = len(lBonus)
         if iRange > 0:
           bDone = False
           iBonus = -1
           # Bonus verbreiten versuchen (0 = back to Index)
           if iData3 > 0:
             iBonus = lBonus[iData3]

             # Bonus checken
             if iBonus != -1:
               loopPlot, iChance = self.doBonusCityGetPlot(pCity, iBonus)

               # Bonus verbreiten
               if loopPlot != None and not loopPlot.isNone():

                 # Bei gleichem Bonusgut keine Auswirkungen
                 if loopPlot.getBonusType(iPlayer) != iBonus:

                   if self.myRandom(100, None) < iChance:
                     loopPlot.setBonusType(iBonus)
                     CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_DONE",(gc.getBonusInfo(iBonus).getDescription(),pCity.getName())), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)
                   else:
                     CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_INFO_BONUSVERBREITUNG_NEG",(gc.getBonusInfo(iBonus).getDescription(),pCity.getName())), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

                   pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                   bDone = True


           # Bonus selektieren
           if not bDone:
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
             popupInfo.setOnClickedPythonCallback("popupBonusverbreitung")
             popupInfo.setData1(iData4) # iPlayer
             popupInfo.setData2(iData5) # iUnitID
             popupInfo.setData3(iData2) # iPage
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MAIN_MENU_GO_BACK",("", )), "Art/Interface/Buttons/Actions/button_bonusverbreitung.dds")

             iReplace = -1
             for i in range(iRange):
               if i > 0:
                 iBonus = lBonus[i]
                 szText = gc.getBonusInfo(iBonus).getDescription() + " (" + str(pPlayer.getNumAvailableBonuses(iBonus)) + " "
                 szText += CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_INBESITZ",("",)) + ")"
                 loopPlot, iChance = self.doBonusCityGetPlot(pCity, iBonus)
                 if loopPlot == None or loopPlot.isNone(): szText += " " + CyTranslator().getText("TXT_KEY_POPUP_NOT_POSSIBLE",())
                 else:
                   if loopPlot.getBonusType(iPlayer) == iBonus:
                     szText += " " + CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_HIER",("",))
                     iReplace = iBonus
                   else:
                     szText += " " + CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_CHANCE",(iChance,))
                 popupInfo.addPythonButton(szText, gc.getBonusInfo(iBonus).getButton())

             szTextHead = CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG",("", ))
             if iReplace != -1: szTextHead += CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_REPLACE",(gc.getBonusInfo(iReplace).getDescription(), ))
             popupInfo.setText( szTextHead )

             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
             popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
             popupInfo.addPopup(iPlayer)

    # ---- Ende Bonusverbreitung

    # Getreidelieferung UNIT_SUPPLY_FOOD
    if iData1 == 727:
       # 727, iCityID, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.changeFood(50)
       pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

    # Karte zeichnen
    if iData1 == 728:
       # 726, iPage/iButtonId, -1, iPlayer, iUnitID
       iPlayer = iData4
       pPlayer = gc.getPlayer(iPlayer)

       # First Page
       if iData2 == -1:
         popupInfo = CyPopupInfo()
         popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
         popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN",("", )) )
         popupInfo.setOnClickedPythonCallback("popupKartenzeichnungen")
         popupInfo.setData1(iData4) # iPlayer
         popupInfo.setData2(iData5) # iUnitID

         # Kosten / Erfolgschance / Trait-Bonus

         # Gebirge: 100 G/30% TRAIT_ORGANIZED oder TRAIT_PROTECTIVE
         txtBonus = ""
         iChance = 30
         iGold = 100
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_ORGANIZED")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_1",(iGold,iChance))+txtBonus, ",Art/Interface/Buttons/BaseTerrain/Peak.dds,Art/Interface/Buttons/BaseTerrain_TerrainFeatures_Atlas.dds,7,1")

         # Weltwunderstaedte: 200 G/50% TRAIT_CREATIVE oder TRAIT_INDUSTRIOUS
         txtBonus = ""
         iChance = 50
         iGold = 200
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_INDUSTRIOUS")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_2",(iGold,iChance))+txtBonus, ",Art/Interface/Buttons/Buildings/PoliceStation.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,1,5")

         # Hafenstaedte: 300 G/50% TRAIT_MARITIME
         txtBonus = ""
         iChance = 50
         iGold = 300
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_MARITIME")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_3",(iGold,iChance))+txtBonus, ",Art/Interface/Buttons/Builds/BuildCityRuins.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,3,10")

         # Grosse Handelsstaedte: 400 [ICON_GOLD]/70% (Bonus) TRAIT_FINANCIAL
         txtBonus = ""
         iChance = 70
         iGold = 400
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_FINANCIAL")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_4",(iGold,iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_building_colonia.dds")

         # Metropolen (ab Pop 18): 600 G/90% TRAIT_EXPANSIVE
         txtBonus = ""
         iChance = 90
         iGold = 600
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EXPANSIVE")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_5",(iGold,iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_metropole.dds")

         # Provinzen (ab Pop 10): 800 G/90% TRAIT_IMPERIALIST
         txtBonus = ""
         iChance = 90
         iGold = 800
         if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_IMPERIALIST")):
           iGold = int(iGold * .75)
           txtBonus = " " + CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_TRAITBONUS",("", ))
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_6",(iGold,iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_provinz.dds")

         # Staedte (ab Pop 6): 1000 G/90%
         txtBonus = ""
         iChance = 90
         iGold = 1000
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_7",(iGold,iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_stadt.dds")

         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
         popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
         popupInfo.addPopup(iPlayer)

       else:

         bRemoveUnit = false
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
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             pPlayer.changeGold(-iGold)
             bRemoveUnit = true
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isPeak(): bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Weltwunderstaedte: 200 G/50% TRAIT_CREATIVE oder TRAIT_INDUSTRIOUS
         elif iData2 == 1:
           iChance = 50
           iGold = 200
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")) or pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_INDUSTRIOUS")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.getNumWorldWonders() > 0: bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Hafenstaedte: 300 G/50% TRAIT_MARITIME
         elif iData2 == 2:
           iChance = 50
           iGold = 300
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_MARITIME")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.isCoastal(5): bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Grosse Handelsstaedte (Traderoutes > 5): 400 [ICON_GOLD]/70% (Bonus) TRAIT_FINANCIAL
         elif iData2 == 3:
           iChance = 70
           iGold = 400
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_FINANCIAL")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.getTradeRoutes() > 5: bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Metropolen (ab Pop 18): 600 G/90% TRAIT_EXPANSIVE
         elif iData2 == 4:
           iChance = 90
           iGold = 600
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EXPANSIVE")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.getPopulation() > 17: bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Provinzen (ab Pop 10): 800 G/90% TRAIT_IMPERIALIST
         elif iData2 == 5:
           iChance = 90
           iGold = 800
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_IMPERIALIST")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.getPopulation() > 9: bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Staedte (ab Pop 6): 1000 G/90%
         elif iData2 == 6:
           iChance = 90
           iGold = 1000
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = true
             pPlayer.changeGold(-iGold)
             if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
             if iChance >= self.myRandom(100, None):
               for i in range (MapW):
                 for j in range (MapH):
                   pPlot = CyMap().plot(i, j)
                   bShow = False
                   if pPlot.isCity():
                     pCity = pPlot.getPlotCity()
                     if pCity.getPopulation() > 5: bShow = True
                   # Show plot
                   if bShow: pPlot.setRevealed (iTeam,1,0,-1)
             else:
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_FAILED",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)

         # Scout entfernen
         if bRemoveUnit:
           pUnit = pPlayer.getUnit(iData5)
           pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)


    # Sklaven -> Bibliothek / Library
    if iData1 == 729:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doSlave2Library(pCity, pUnit)

    # Release slaves
    if iData1 == 730:
       # 730, iCityID, 0, iPlayer, -1/iButton
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)

       iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
       iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
       iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
       iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
       iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

       bPopUp = false

       if iData5 == -1:
         # wenn es nur Gladiatoren gibt, automatisch einen abziehen
         if iCityGlads >= 1 and iCitySlaves == 0:
            NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            pCity.changeFreeSpecialistCount(15, -1)
            iCityGlads -= 1
         elif iCitySlaves >= 1:

           # wenns nur Haussklaven gibt
           if iCityGlads == 0 and iCitySlaves == iCitySlavesHaus:
             NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             NewUnit.finishMoves()
             pCity.changeFreeSpecialistCount(16, -1)
             iCitySlavesHaus -= 1
             iCitySlaves -= 1
           # wenns nur Feldsklaven gibt
           elif iCityGlads == 0 and iCitySlaves == iCitySlavesFood:
             NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             NewUnit.finishMoves()
             pCity.changeFreeSpecialistCount(17, -1)
             iCitySlavesFood -= 1
             iCitySlaves -= 1
           # wenns nur Bergwerksklaven gibt
           elif iCityGlads == 0 and iCitySlaves == iCitySlavesProd:
             NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             NewUnit.finishMoves()
             pCity.changeFreeSpecialistCount(18, -1)
             iCitySlavesProd -= 1
             iCitySlaves -= 1
           # wenns verschiedene angesiedelte Sklaven gibt -> PopUP
           else:
             bPopUp = true

       # PopUp
       if iData5 > -1 or bPopUp:

             # Sklaven abziehen
             if iData5 > -1:
               if iData5 == 0 and iCityGlads >= 1:
                 NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                 NewUnit.finishMoves()
                 pCity.changeFreeSpecialistCount(15, -1)
                 iCityGlads -= 1
               elif iData5 == 1 and iCitySlavesHaus >= 1:
                 NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                 NewUnit.finishMoves()
                 pCity.changeFreeSpecialistCount(16, -1)
                 iCitySlavesHaus -= 1
                 iCitySlaves -= 1
               elif iData5 == 2 and iCitySlavesFood >= 1:
                 NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                 NewUnit.finishMoves()
                 pCity.changeFreeSpecialistCount(17, -1)
                 iCitySlavesFood -= 1
                 iCitySlaves -= 1
               elif iData5 == 3 and iCitySlavesProd >= 1:
                 NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                 NewUnit.finishMoves()
                 pCity.changeFreeSpecialistCount(18, -1)
                 iCitySlavesProd -= 1
                 iCitySlaves -= 1
             # -----

             # PopUp
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
             popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_RELEASE_SLAVES",(pCity.getName(),iCityGlads+iCitySlaves)) )
             popupInfo.setData1(iData2) # CityID
             popupInfo.setData2(iData4) # iPlayer
             popupInfo.setOnClickedPythonCallback("popupReleaseSlaves")

             # Button 0: Gladiatoren
             szText = localText.getText("TXT_KEY_UNIT_GLADIATOR", ()) + " (" + str(iCityGlads) + ")"
             popupInfo.addPythonButton(szText, gc.getSpecialistInfo(15).getButton())
             # Button 1: Haussklaven
             szText = localText.getText("TXT_KEY_UNIT_SLAVE_HAUS", ()) + " (" + str(iCitySlavesHaus) + ")"
             popupInfo.addPythonButton(szText, gc.getSpecialistInfo(16).getButton())
             # Button 2: Feldsklaven
             szText = localText.getText("TXT_KEY_UNIT_SLAVE_FOOD", ()) + " (" + str(iCitySlavesFood) + ")"
             popupInfo.addPythonButton(szText, gc.getSpecialistInfo(17).getButton())
             # Button 3: Bergwerksklaven
             szText = localText.getText("TXT_KEY_UNIT_SLAVE_PROD", ()) + " (" + str(iCitySlavesProd) + ")"
             popupInfo.addPythonButton(szText, gc.getSpecialistInfo(18).getButton())

             # Cancel button
             popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
             popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
             popupInfo.addPopup(iData4)

    # Spread religion with a missionary
    if iData1 == 731:
      # 731, -1, -1, iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iReligion = -1

      # Religion herausfinden
      # pUnit.canSpread (PLOT, iReligion, bool) => geht leider nur in Zusammenhang mit einem PLOT!
      # also wenn die Einheit schon in der Stadt steht, die aber erst gesucht werden muss!
      if pUnit.getUnitType()   == gc.getInfoTypeForString("UNIT_CELTIC_MISSIONARY"): iReligion = 0
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY"): iReligion = 1
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_PHOEN_MISSIONARY"):  iReligion = 2
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY"):  iReligion = 3
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_ROME_MISSIONARY"):   iReligion = 4
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_ZORO_MISSIONARY"):   iReligion = 5
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY"):  iReligion = 6
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SUMER_MISSIONARY"):  iReligion = 7
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_HINDU_MISSIONARY"):  iReligion = 8
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_BUDDHIST_MISSIONARY"):  iReligion = 9
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_JEWISH_MISSIONARY"):    iReligion = 10
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY"): iReligion = 11
      elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_MISSIONARY_JAINISMUS"): iReligion = 12

      if iReligion != -1:
        bCanSpread = false
        iNumCities = pPlayer.getNumCities()
        for i in range (iNumCities):
          pCity = pPlayer.getCity(i)
          if not pCity.isNone():
            if not pCity.isHasReligion(iReligion):
              pUnit.getGroup().pushMoveToMission (pCity.getX(), pCity.getY())
              pUnit.getGroup().pushMission(MissionTypes.MISSION_SPREAD, iReligion, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
              bCanSpread = true

        if not bCanSpread:
          CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SPREAD_RELIGION_NEG",(gc.getReligionInfo(iReligion).getDescription(),"")), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Trade Mission: send and submit merchant into next foreign city
    if iData1 == 732:
      # 732, -1, -1, iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      self.doAutomateMerchant(pUnit)

    # Build Limes PopUp
    if iData1 == 733:
      # 733, -1 oder iButtonID, -1, iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)

      lBuildInfos = []
      lImpInfos = []
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES1"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES3"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES4"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES5"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES6"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES7"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES8"))
      lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES9"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES1"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES3"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES4"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES5"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES6"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES7"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES8"))
      lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES9"))
      if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_DEFENCES_2")):
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_1"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_2"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_3"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_4"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_5"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_6"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_7"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_8"))
       lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_9"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_1"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_2"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_3"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_4"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_5"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_6"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_7"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_8"))
       lImpInfos.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_9"))

      # PopUp
      if iData2 == -1:

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setOnClickedPythonCallback("popupBuildLimes")
        popupInfo.setData1(iData4) # iPlayer
        popupInfo.setData2(iData5) # iUnitID
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_BUILDLIMES_1",("", )) )

        j=0
        for i in lBuildInfos:
          pBuildInfo = gc.getBuildInfo(i)
          popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_BUILDLIMES_2",( pBuildInfo.getDescription(),pBuildInfo.getCost(),gc.getImprovementInfo(lImpInfos[j]).getDefenseModifier() )), pBuildInfo.getButton() )
          j+=1

        popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
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
    if iData1 == 734:
      # 731, iCityID, Typ: 1=Feld 2=Bergwerk, iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      pCity = pPlayer.getCity(iData2)

      # Feldsklaven
      if iData3 == 1:
         pCity.changeFreeSpecialistCount(17, 1)
      # Bergwerksklave
      else:
        pCity.changeFreeSpecialistCount(18, 1)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

    # Salae oder Dezimierung
    if iData1 == 735:
      # 735, Typ: 1=Sold 2=Dezimierung, 0=PopUp oder 1=Anwenden,  iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)

      # Sold
      if iData2 == 1:
       # +x Gold pro Promotion
       FormationArray = []
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_WILDLIFE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_TRAIT_MARITIME"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_LOYALITAT"))
       FormationArray.append(gc.getInfoTypeForString("PROMOTION_MERCENARY"))
       iGold = 0
       iRange = gc.getNumPromotionInfos()
       for j in range(iRange):
         if pUnit.isHasPromotion(j) and j not in FormationArray: iGold += 5

       iGold += pUnit.baseCombatStr() * 4

       if pPlayer.hasBonus(gc.getInfoTypeForString("BONUS_SALT")): iGold -= iGold / 4

       # PopUp Beschreibung und Auswahl
       if iData3 == 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_ACTION_SALAE_2",(iGold,)) )
              popupInfo.setData1(iData4)
              popupInfo.setData2(iData5)
              popupInfo.setData3(1)
              popupInfo.setOnClickedPythonCallback("popupActionSalaeDecimatio") # EntryPoints/CvScreenInterface und CvGameUtils / 735
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_SALAE_YES",("",)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_SALAE_NO",("",)), "")
              popupInfo.addPopup(iData4)

       # Anwenden
       else:
        pPlayer.changeGold(-iGold)

        # Erfolgreich
        if self.myRandom(2, None) == 0:
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
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_SALAE_POS",(gc.getPromotionInfo(iPromo).getDescription(),)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_salae.dds",ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)

        # Keine Auswirkung
        else:
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_SALAE_NEG",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_salae.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)

        pUnit.finishMoves()
        self.doGoToNextUnit(pPlayer, pUnit)


      # Dezimierung
      elif iData2 == 2:
       # PopUp Beschreibung und Auswahl
       if iData3 == 0:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_2",("",)) )
              popupInfo.setData1(iData4)
              popupInfo.setData2(iData5)
              popupInfo.setData3(2)
              popupInfo.setOnClickedPythonCallback("popupActionSalaeDecimatio") # EntryPoints/CvScreenInterface und CvGameUtils / 735
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_YES",("",)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_NO",("",)), "")
              popupInfo.addPopup(iData4)

       # Anwenden
       else:

        iRand = self.myRandom(10, None)

        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")): iChance = 1 # entspricht 10%
        else: iChance = 0

        # Einheit wird barbarisch
        if iRand < iChance:

          # Einen guenstigen Plot suchen
          rebelPlotArray = []
          for i in range(3):
                for j in range(3):
                  loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                  if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                    if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                      rebelPlotArray.append(loopPlot)

          if len(rebelPlotArray) == 0:
                for i in range(3):
                  for j in range(3):
                    loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                    if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                      if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()) and loopPlot.getOwner() == iPlayer:
                        rebelPlotArray.append(loopPlot)

          if len(rebelPlotArray) > 0:
            iPlot = self.myRandom(len(rebelPlotArray), None)
            NewUnit = gc.getBARBARIAN_PLAYER().initUnit(pUnit.getUnitType(), rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            iRange = gc.getNumPromotionInfos()
            for j in range(iRange):
              if pUnit.isHasPromotion(j):
                NewUnit.setHasPromotion(j, True)

            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG5"), False)
            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"), False)
            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"), False)
            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"), False)
            NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG1"), False)

            CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_BARBAR",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(7),NewUnit.getX(),NewUnit.getY(),True,True)
            # New kill / neuer Kill befehl
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
            #pUnit.kill(1,pUnit.getOwner())
          else:
            CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_OUT",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
            # New kill / neuer Kill befehl
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
            #pUnit.kill(1,pUnit.getOwner())

        # Decimatio ist erfolgreich
        elif iRand < iChance+5:
          # Unit verletzen
          pUnit.changeDamage(10,False)

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

          # Rang verlieren
          if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT6")): pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT6"), False)
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")): pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5"), False)
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")): pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), False)
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")): pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), False)

          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_POS",(gc.getPromotionInfo(iPromo).getDescription(),)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)
          pUnit.finishMoves()
          self.doGoToNextUnit(pPlayer, pUnit)

        # Keine Auswirkung
        else:
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_NEG",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
          pUnit.finishMoves()
          self.doGoToNextUnit(pPlayer, pUnit)

    # Handelsposten errichten
    if iData1 == 736:
      # 736, 0, 0, iPlayer, iUnitID
      pUnit = gc.getPlayer(iData4).getUnit(iData5)
      self.doBuildHandelsposten(pUnit)

    # Statthalter / Tribut
    if iData1 == 737:
       # iData1, iData2, ... , iData5
       # First:  737, iCityID, iPlayer, -1, -1
       # Second: 737, iCityID, iPlayer, iButtonID (Typ), -1
       # Third:  737, iCityID, iPlayer, iTyp, iButtonID
       pPlayer = gc.getPlayer(iData3)
       pCity = pPlayer.getCity(iData2)

       if iData4 == -1:
         popupInfo = CyPopupInfo()
         popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
         popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_0",(pCity.getName(),)) )
         popupInfo.setData1(iData2) # CityID
         popupInfo.setData2(iData3) # iPlayer
         popupInfo.setData3(-1) # iTyp (Einfluss oder Tribut)
         popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

         # Button 0: Einfluss verbessern
         popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_1",()), "Art/Interface/Buttons/Actions/button_statthalter_einfluss.dds" )
         # Button 1: Tribut fordern
         popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_2",()), ",Art/Interface/Buttons/Civics/Decentralization.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,4,1" )

         # Cancel button
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
         popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
         popupInfo.addPopup(iData3)

       # -- Einfluss verbessern --
       elif iData4 == 0:

         iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
         iBuildingHappiness = pCity.getExtraHappiness()
         # Button 0: kleine Spende
         iGold1 = pCity.getPopulation() * 16
         iHappy1 = 1
         # Button 1: grosse Spende
         iGold2 = pCity.getPopulation() * 28
         iHappy2 = 2

         # Gold-Check
         if iData5 == 0 and pPlayer.getGold() < iGold1: iData5 = -1
         if iData5 == 1 and pPlayer.getGold() < iGold2: iData5 = -1

         if iData5 == -1:

           szText = localText.getText("[H2]", ()) + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_1",()).upper() + localText.getText("[\H2][NEWLINE]", ())
           szText += CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG",())
           szText += u": %d " % (abs(iBuildingHappiness))
           if iBuildingHappiness < 0: szText += localText.getText("[ICON_UNHAPPY]", ())
           else: szText += localText.getText("[ICON_HAPPY]", ())

           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
           popupInfo.setText( szText )
           popupInfo.setData1(iData2) # CityID
           popupInfo.setData2(iData3) # iPlayer
           popupInfo.setData3(iData4) # iTyp (Einfluss oder Tribut)
           popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

           # Button 0: kleine Spende
           popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_GOLD1",(iGold1,iHappy1)), "Art/Interface/Buttons/Actions/button_statthalter_gold1.dds" )
           # Button 1: grosse Spende
           popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_GOLD2",(iGold2,iHappy2)), "Art/Interface/Buttons/Actions/button_statthalter_gold2.dds" )

           # Cancel button
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
           popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
           popupInfo.addPopup(iData3)

         # Triumphzug
         elif iData5 == 0:
           pCity.changeExtraHappiness(iHappy1)
           pPlayer.changeGold(-iGold1)
           iImmo = 2

         # Mehrtaegiges Fest
         elif iData5 == 1:
           pCity.changeExtraHappiness(iHappy2)
           pPlayer.changeGold(-iGold2)
           iImmo = 3

         if iData5 == 0 or iData5 == 1:
           if iData3 == gc.getGame().getActivePlayer():
             CyAudioGame().Play2DSound("AS2D_COINS")
             CyAudioGame().Play2DSound("AS2D_WELOVEKING")

           # Einheiten sind nun beschaeftigt
           pPlot = pCity.plot()
           iNumUnits = pPlot.getNumUnits()
           if iNumUnits > 0:
             for k in range (iNumUnits):
               if iData3 == pPlot.getUnit(k).getOwner():
                 pPlot.getUnit(k).setImmobileTimer(iImmo)


       # -- Tribut fordern --
       elif iData4 == 1:

         iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
         iBuildingHappiness = pCity.getExtraHappiness()
         iUnit1  = gc.getInfoTypeForString("UNIT_GOLDKARREN")
         iUnhappy1 = 2
         iUnit2  = gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
         iUnhappy2 = 1
         iUnit3  = gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")
         iUnhappy3 = 1
         iUnit4  = gc.getInfoTypeForString("UNIT_SLAVE")
         iUnhappy4 = 1

         if iData5 == -1:

           szText = localText.getText("[H2]", ()) + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_2",()).upper() + localText.getText("[\H2][NEWLINE]", ())
           szText += CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG",())
           szText += u": %d " % (abs(iBuildingHappiness))
           if iBuildingHappiness < 0: szText += localText.getText("[ICON_UNHAPPY]", ())
           else: szText += localText.getText("[ICON_HAPPY]", ())

           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
           popupInfo.setText( szText )
           popupInfo.setData1(iData2) # CityID
           popupInfo.setData2(iData3) # iPlayer
           popupInfo.setData3(iData4) # iTyp (Einfluss oder Tribut)
           popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

           # Button 0: Goldkarren
           popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT1",(gc.getUnitInfo(iUnit1).getDescriptionForm(0),iUnhappy1)), gc.getUnitInfo(iUnit1).getButton() )
           # Button 1: Hilfstrupp
           popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT2",(gc.getUnitInfo(iUnit2).getDescriptionForm(0),iUnhappy2)), gc.getUnitInfo(iUnit2).getButton() )
           # Button 2: Getreidekarren
           popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT3",(gc.getUnitInfo(iUnit3).getDescriptionForm(0),iUnhappy3)), gc.getUnitInfo(iUnit3).getButton() )
           # Button 3: Sklave
           if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")):
             popupInfo.addPythonButton( CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT4",(gc.getUnitInfo(iUnit4).getDescriptionForm(0),iUnhappy4)), gc.getUnitInfo(iUnit4).getButton() )

           # Cancel button
           popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
           popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
           popupInfo.addPopup(iData3)

         # Goldkarren
         elif iData5 == 0:
           # pCity.setBuildingHappyChange geht nicht, weil die Stadt auch Negatives positiv anrechnet
           pCity.changeExtraHappiness(-iUnhappy1)
           NewUnit = pPlayer.initUnit(iUnit1, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           NewUnit.setImmobileTimer(1)
         # Hilfstrupp
         elif iData5 == 1:
           pCity.changeExtraHappiness(-iUnhappy2)
           NewUnit = pPlayer.initUnit(iUnit2, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           NewUnit.setImmobileTimer(1)
         # Getreide
         elif iData5 == 2:
           pCity.changeExtraHappiness(-iUnhappy3)
           NewUnit = pPlayer.initUnit(iUnit3, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           iRand = 1 + self.myRandom(3, None)
           if iRand >= 1: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
           if iRand >= 2: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
           if iRand >= 3: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
           NewUnit.setImmobileTimer(1)
         # Sklaven
         elif iData5 == 3:
           pCity.changeExtraHappiness(-iUnhappy4)
           NewUnit = pPlayer.initUnit(iUnit4, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           NewUnit.setImmobileTimer(1)

         if iData5 > -1:
           if iData3 == gc.getGame().getActivePlayer():
             CyAudioGame().Play2DSound("AS2D_UNIT_BUILD_UNIT")

    # --------------------------------
    # 738: Allgemeine Infos zu Buttons
    # --------------------------------



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

  def onInit(self, argsList):
    'Called when Civ starts up'
    CvUtil.pyPrint( 'OnInit' )

  def onUpdate(self, argsList):
    'Called every frame'
    fDeltaTime = argsList[0]

    # allow camera to be updated
    CvCameraControls.g_CameraControls.onUpdate( fDeltaTime )

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

    # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
    gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), false)

    # ---------------- Schmelzen 2/4 (BoggyB) --------
    # Beim Neuladen (Felder aus 3/4 bleiben nicht gespeichert)
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    if sScenarioScriptData == "SchmelzEuro" or sScenarioScriptData == "SchmelzWelt":
           iXLaenge = CyMap().getGridWidth()
           iYLaenge = CyMap().getGridHeight()
           eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
           eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
           #eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
           eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
           eEis = gc.getInfoTypeForString("FEATURE_ICE")
           eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
           #eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
           eDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
           for x in xrange(iXLaenge):
             for y in xrange(iYLaenge):
               pPlot = CyMap().plot(x,y)
               if pPlot.getTerrainType() == eDarkIce: continue
               elif pPlot.getTerrainType() == eSnow: self.IceSnow.append(pPlot)
               elif pPlot.getTerrainType() == eTundra:
                 # Extra Tundra-Bereich, wos langsamer gehn soll
                 if sScenarioScriptData == "SchmelzEuro" and x >= 42 and y >= 49: self.IceTundra2.append(pPlot)
                 else: self.IceTundra.append(pPlot)
               elif pPlot.getFeatureType() == eEis: self.IceEis.append(pPlot)
               #Ueberflutung
               if pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isHills() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1:
                 if sScenarioScriptData == "SchmelzEuro":
                   if y >= 28: self.IceCoast.append(pPlot)
                 else: self.IceCoast.append(pPlot)
               #Desertifizierung
               if sScenarioScriptData == "SchmelzEuro" and y <= 8:
                 if pPlot.getTerrainType() == eEbene and not pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isRiver(): self.IceDesertEbene.append(pPlot)
                 elif pPlot.getTerrainType() == eCoast and y <=6 and x >= 2 and x <= 60: self.IceDesertCoast.append(pPlot)

    # +++++ PAE Debug: disband certain units ++++++++++++++++++++++++++++++++
    #iRange = gc.getMAX_PLAYERS()
    #for iPlayer in range(iRange):
    #  player = gc.getPlayer(iPlayer)
    #  if player.isAlive():
    #    iNumUnits = player.getNumUnits()
    #    for j in range(iNumUnits):
    #      if player.getUnit(j).getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
    #         player.getUnit(j).kill(1,player.getUnit(j).getOwner())

    # --------- BTS --------
    CvAdvisorUtils.resetNoLiberateCities()
    return 0

  def onGameStart(self, argsList):
    'Called at the start of the game'

    # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
    gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), false)

    ### Starting points part 2 ###
    MapName = CyMap().getMapScriptName ()
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START) and gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR"):
      MapName = ""
      bPlaceCivs = True
      bPlaceBarbs = True
      # PAE Maps
      if sScenarioScriptData == "EuropeStandard": MapName = "StartingPoints_EuropeStandard.xml"
      elif sScenarioScriptData == "EuropeMini": MapName = "StartingPoints_EuropeMini.xml"
      elif sScenarioScriptData == "EuropeMedium": MapName = "StartingPoints_EuropeMedium.xml"
      elif sScenarioScriptData == "EuropeLarge": MapName = "StartingPoints_EuropeLarge.xml"
      elif sScenarioScriptData == "EuropeSmall": MapName = "StartingPoints_EuropeSmall.xml"
      elif sScenarioScriptData == "SchmelzEuro": MapName = "StartingPoints_EuropeLarge.xml"
      elif sScenarioScriptData == "EuropeXL": MapName = "StartingPoints_EuropeXL.xml"
      elif sScenarioScriptData == "Eurasia": MapName = "StartingPoints_Eurasia.xml"
      elif sScenarioScriptData == "PAE_PB": MapName = "StartingPoints_PAE_PB.xml"
      #elif sScenarioScriptData == "EasternMed":
      #    MapName = "StartingPoints_EasternMed.xml"
      #    bPlaceCivs = False

      if MapName != "":
         Debuging = False
         AddPositionsToMap = False
         MyFile = open("Mods/PieAncientEuropeV/Assets/XML/Misc/" + MapName)
         StartingPointsUtil.ReadMyFile(MyFile,Debuging,AddPositionsToMap,bPlaceCivs,bPlaceBarbs)
         MyFile.close()
    # --------------------------------

    # +++++ Special dawn of man texts for Szenario Maps in PAE in CvDawnOfMan.py ++++++++++++++++++++++++++++++++
    #if (gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR") and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
    iEra = gc.getGame().getStartEra()
    lTechs = []
    lTechs.append(gc.getInfoTypeForString("TECH_NONE"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_1"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_2"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_3"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_4"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_5"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_6"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_7"))
    lTechs.append(gc.getInfoTypeForString("TECH_TECH_INFO_8"))
    lTechsReli = []
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_NORDIC"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_CELTIC"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_HINDU"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_EGYPT"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_SUMER"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_GREEK"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_PHOEN"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_RELIGION_ROME"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_DUALISMUS"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_MONOTHEISM"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_ASKESE"))
    lTechsReli.append(gc.getInfoTypeForString("TECH_MEDITATION"))
    iTechRome = gc.getInfoTypeForString("TECH_ROMAN")
    iTechGreek = gc.getInfoTypeForString("TECH_GREEK")
    lCivsRome = []
    lCivsRome.append(gc.getInfoTypeForString("CIVILIZATION_ROME"))
    lCivsRome.append(gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"))
    lCivsGreek = []
    lCivsGreek.append(gc.getInfoTypeForString("CIVILIZATION_GREECE"))
    lCivsGreek.append(gc.getInfoTypeForString("CIVILIZATION_ATHENS"))
    lCivsGreek.append(gc.getInfoTypeForString("CIVILIZATION_SPARTA"))
    lCivsGreek.append(gc.getInfoTypeForString("CIVILIZATION_THEBAI"))
    lCivsGreek.append(gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"))

    # +++++ Corrections in scenarios ++++++++++++++++++++++++++++++++
    iRange = gc.getMAX_PLAYERS()
    for iPlayer in range(iRange):
      player = gc.getPlayer(iPlayer)
      if player.isAlive():
        ##Flunky: (unit, iter) statt for range
        # +++++ Correct naming for units (not available in BTS)
        (unit, iter) = player.firstUnit(false)
        while unit:
          UnitText = unit.getName()
          if UnitText[:7] == "TXT_KEY":
            sz = UnitText.split()
            sTranslatedName = CyTranslator().getText(str(sz[0]),("",))
            unit.setName(sTranslatedName)
          #PAE Debug: delete certain units
          #if player.getUnit(j).getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
          #   player.getUnit(j).kill(1,player.getUnit(j).getOwner())
          (unit, iter) = player.nextUnit(iter, false)

        ##Flunky: (city, iter) statt for range
        # +++++ Check city status
        (city, iter) = player.firstCity(false)
        while city:
          self.doCheckCityState(city)
          (city,iter) = player.nextCity(iter, false)
        ##/Flunky

        #Start in spaeterer Aera -> unerforschbare und Relitechs entfernen
        #Start in later era -> remove unresearchable and religious techs
        # Scenarios ausgeschlossen!!!
        if sScenarioScriptData == "":
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


    # ++++ Das Zedernholz benoetigt Savanne. Da es in den BONUS-Infos nicht funktioniert, muss es manuell gemacht werden
    feat_forest = gc.getInfoTypeForString("FEATURE_SAVANNA")
    bonus_zedern = gc.getInfoTypeForString("BONUS_ZEDERNHOLZ")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for x in range(iMapW):
      for y in range(iMapH):
        loopPlot = gc.getMap().plot(x,y)
        #if loopPlot != None and not loopPlot.isNone():
        if loopPlot.getFeatureType() == iDarkIce: continue
        if loopPlot.getBonusType(-1) == bonus_zedern and loopPlot.getFeatureType() != feat_forest:
           loopPlot.setFeatureType(feat_forest,1)
    # -----------

    # BTS Standard
    if gc.getGame().isPbem():
      iRange = gc.getMAX_PLAYERS()
      for iPlayer in range(iRange):
        player = gc.getPlayer(iPlayer)
        if (player.isAlive() and player.isHuman()):
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
    #CvTopCivs.CvTopCivs().turnChecker(iGameTurn)

    ###### Historische Texte ---------
    self.doHistory(iGameTurn)

  # global
  def onEndGameTurn(self, argsList):
    'Called at the end of the end of each turn'
    iGameTurn = argsList[0]

    # Special Scripts for PAE Scenarios
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    #if iGameTurn > 1 and iGameTurn % 10 == 0:
    if iGameTurn == 1:
      if sScenarioScriptData == "PeloponnesianWar":
        # Athen (0) soll mit Sparta (1) ewig Krieg fuehren
        gc.getTeam(gc.getPlayer(0).getTeam()).setPermanentWarPeace(gc.getPlayer(1).getTeam(), true)
        #gc.getPlayer(0).AI_setAttitudeExtra(1,-50)
        #gc.getPlayer(1).AI_setAttitudeExtra(0,-50)
        #gc.getTeam(gc.getPlayer(0).getTeam()).setWarWeariness(gc.getPlayer(1).getTeam(),30)
        #gc.getTeam(gc.getPlayer(1).getTeam()).setWarWeariness(gc.getPlayer(0).getTeam(),30)
      # ---------------- Schmelzen 3/4 (BoggyB) --------
      elif sScenarioScriptData == "SchmelzEuro" or sScenarioScriptData == "SchmelzWelt":
           iXLaenge = CyMap().getGridWidth()
           iYLaenge = CyMap().getGridHeight()
           eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
           eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
           #eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
           eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
           eEis = gc.getInfoTypeForString("FEATURE_ICE")
           eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
           #eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
           eDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
           for x in xrange(iXLaenge):
             for y in xrange(iYLaenge):
               pPlot = CyMap().plot(x,y)
               if pPlot.getTerrainType() == eDarkIce: continue
               if pPlot.getTerrainType() == eSnow: self.IceSnow.append(pPlot)
               elif pPlot.getTerrainType() == eTundra:
                 # Extra Tundra-Bereich, wos langsamer gehn soll
                 if sScenarioScriptData == "SchmelzEuro" and x >= 42 and y >= 49: self.IceTundra2.append(pPlot)
                 else: self.IceTundra.append(pPlot)
               elif pPlot.getFeatureType() == eEis: self.IceEis.append(pPlot)
               #Ueberflutung
               if pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isHills() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1:
                 if sScenarioScriptData == "SchmelzEuro":
                   if y >= 28: self.IceCoast.append(pPlot)
                 else: self.IceCoast.append(pPlot)
               #Desertifizierung
               if sScenarioScriptData == "SchmelzEuro" and y <= 8:
                 if pPlot.getTerrainType() == eEbene and not pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isRiver(): self.IceDesertEbene.append(pPlot)
                 elif pPlot.getTerrainType() == eCoast and y <=6 and x >= 2 and x <= 60: self.IceDesertCoast.append(pPlot)
      # --------------

    # ----------------

    elif iGameTurn == 228:
      if sScenarioScriptData == "PeloponnesianWarKeinpferd":
        # Athen (0) soll von 414 an mit Sparta (1) ewig den dekeleischen Krieg fuehren
        gc.getTeam(gc.getPlayer(0).getTeam()).setPermanentWarPeace(gc.getPlayer(1).getTeam(), true)

    # ---------------- Schmelzen 4/4 (BoggyB)--------
    elif iGameTurn > 1:
      if sScenarioScriptData == "SchmelzEuro" or sScenarioScriptData == "SchmelzWelt":
        #Normal alle 40 Runden (insg. 940 Runden)
        #Schnell alle 32 Runden (insg. 770 Runden)
        #Episch alle 45 Runden (insg. 1095 Runden)
        #Marathon alle 52 Runden (insg. 1220 Runden)
        iTurnSchmelzIntervall = 40
        iTurnLimit = 800
        if gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_QUICK"):
          iTurnSchmelzIntervall = 32
          iTurnLimit = 600
        elif gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_EPIC"):
          iTurnSchmelzIntervall = 45
          iTurnLimit = 900
        elif gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_MARATHON"):
          iTurnSchmelzIntervall = 52
          iTurnLimit = 1000

        ## ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Summe Eis",len(self.IceSnow))), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if iGameTurn % iTurnSchmelzIntervall == 0 and iGameTurn <= iTurnLimit:
           iWahrscheinlichkeit = 8
           #if sScenarioScriptData == "SchmelzWelt":
           #  iWahrscheinlichkeit = 8

           eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
           eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
           eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
           eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
           eEis = gc.getInfoTypeForString("FEATURE_ICE")
           eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
           eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")

           #Schnee -> Tundra
           if len(self.IceSnow):
             for pPlot in self.IceSnow:
               iRand = self.myRandom(iWahrscheinlichkeit, None)
               if iRand == 1:
                 pPlot.setTerrainType(eTundra,1,1)
                 self.IceSnow.remove(pPlot)
                 # Tundra Liste updaten
                 if sScenarioScriptData == "SchmelzEuro" and pPlot.getX() >= 42 and pPlot.getY() >= 49: self.IceTundra2.append(pPlot)
                 else: self.IceTundra.append(pPlot)

           #Tundra -> Gras (25%) oder Ebene (75%)
           if len(self.IceTundra):
             for pPlot in self.IceTundra:
               iRand = self.myRandom(iWahrscheinlichkeit, None)
               if iRand == 1:
                 iRand = self.myRandom(4, None)
                 if iRand == 1: pPlot.setTerrainType(eGras,1,1)
                 else: pPlot.setTerrainType(eEbene,1,1)
                 self.IceTundra.remove(pPlot)
           if len(self.IceTundra2):
             for pPlot in self.IceTundra2:
               iRand = self.myRandom(iWahrscheinlichkeit*3, None)
               if iRand == 1:
                 iRand = self.myRandom(4, None)
                 if iRand == 1: pPlot.setTerrainType(eGras,1,1)
                 else: pPlot.setTerrainType(eEbene,1,1)
                 self.IceTundra2.remove(pPlot)

           #Eis schmilzt
           if len(self.IceEis):
             for pPlot in self.IceEis:
               iRand = self.myRandom(iWahrscheinlichkeit, None)
               if iRand == 1:
                 pPlot.setFeatureType(-1, 0)
                 self.IceEis.remove(pPlot)

           #Ueberflutung
           if len(self.IceCoast):
             for pPlot in self.IceCoast:
               iRand = self.myRandom(50, None)
               if iRand == 1:
                 pPlot.setTerrainType(eCoast,1,1)
                 self.IceCoast.remove(pPlot)

           #Desertifizierung
           if sScenarioScriptData == "SchmelzEuro":
              if len(self.IceDesertEbene):
                 for pPlot in self.IceDesertEbene:
                     iRand = self.myRandom(iWahrscheinlichkeit, None)
                     if iRand == 1:
                        pPlot.setTerrainType(eDesert,1,1)
                        pPlot.setImprovementType(-1)
                        self.IceDesertEbene.remove(pPlot)
              elif len(self.IceDesertCoast):
                   for pPlot in self.IceDesertCoast:
                       iRand = self.myRandom(iWahrscheinlichkeit, None)
                       if iRand == 1:
                          pPlot.setTerrainType(eEbene,1,1)
                          self.IceDesertCoast.remove(pPlot)
                          # Desert Liste updaten
                          self.IceDesertEbene.append(pPlot)
    #---------------------------Ende Schmelzen---------------------------------------

    # --------------------------------------------

    # PAE Debug Mark
    #"""
# Seevoelker erschaffen: Langboot + Axtkrieger oder Axtkaempfer | -1500 bis -800
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
     if iGameTurn % 5 == 0 and gc.getGame().getGameTurnYear() > -1400 and gc.getGame().getGameTurnYear() < -800:
      barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
      iUnitTypeShip = gc.getInfoTypeForString("UNIT_SEEVOLK")
      iUnitTypeWarrior1 = gc.getInfoTypeForString("UNIT_SEEVOLK_2")
      iUnitTypeWarrior2 = gc.getInfoTypeForString("UNIT_SEEVOLK_3")

      # Handicap: 0 (Settler) - 8 (Deity)
      # Worldsize: 0 (Duell) - 5 (Huge)
      iRange = 1 + gc.getMap().getWorldSize() + gc.getGame().getHandicapType()

      for i in range (iRange):
        # Diese Koordinaten entsprechen ungefaehr dem Mittelmeer: Ships(range):3 | X: 19-59(40) | Y:9-37(28)
        #iRandX = 19 + self.myRandom(40, None)
        #iRandY = 9 + self.myRandom(28, None)

        # Wird geaendert zu einem Mittelmeerstreifen: x: 5 bis (X-5), y: 5 bis letztes Drittel von Y
        iMapX = gc.getMap().getGridWidth() - 5
        iMapY = int(gc.getMap().getGridHeight() / 3 * 2)
        iRandX = 5 + self.myRandom(iMapX, None)
        iRandY = 5 + self.myRandom(iMapY, None)

        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Plot soll ein Ozean sein
        terr_ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
        feat_ice = gc.getInfoTypeForString("FEATURE_ICE")
        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

        if None != loopPlot and not loopPlot.isNone():
          if loopPlot.getFeatureType() == iDarkIce: continue
          if not loopPlot.isUnit() and not loopPlot.isOwned() and loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
            # Schiffe erstellen
            if gc.getGame().getGameTurnYear() > -1000: iAnz = 3
            elif gc.getGame().getGameTurnYear() > -1200: iAnz = 2
            else: iAnz = 1
            for j in range (iAnz):
              barbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
              barbPlayer.initUnit(iUnitTypeWarrior1, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              barbPlayer.initUnit(iUnitTypeWarrior2, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Seevoelker erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# -- Seevoelker Ende ------------------------------------------

# Wikinger erschaffen: Langboot + Berserker | ab 400 AD
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
     if iGameTurn % 5 == 0 and gc.getGame().getGameTurnYear() >= 400:
      barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
      iUnitTypeShip = gc.getInfoTypeForString("UNIT_VIKING_1")
      iUnitTypeUnit = gc.getInfoTypeForString("UNIT_VIKING_2")
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      for i in range (4):
        iRandX = iMapH - self.myRandom(5, None)
        iRandY = self.myRandom(iMapW, None)
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Es soll auch ein 2tes Feld Wasser sein
        loopPlot2 = gc.getMap().plot(iRandX+1, iRandY)
        if None != loopPlot and not loopPlot.isNone() and None != loopPlot2 and not loopPlot2.isNone():
          if loopPlot.getFeatureType() == iDarkIce or loopPlot2.getFeatureType() == iDarkIce: continue
          if not loopPlot.isUnit() and loopPlot.isWater() and loopPlot2.isWater() and not loopPlot.isOwned():
            # Wikinger erstellen
            barbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
            for j in range (4):
              barbPlayer.initUnit(iUnitTypeUnit, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Wikinger erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# Handelskarren erschaffen: -1800 bis 0
    if iGameTurn % 20 == 0 and gc.getGame().getGameTurnYear() > -1800 and gc.getGame().getGameTurnYear() < 0:
      barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
      iUnitTypeMerchant1 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANT")
      iUnitTypeMerchant2 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN")
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()
      for i in range (4):
        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Es soll auch ein 2tes Feld Wasser sein fuers Handelsschiff
        loopPlot2 = gc.getMap().plot(iRandX+1, iRandY)
        if None != loopPlot and not loopPlot.isNone() and None != loopPlot2 and not loopPlot2.isNone():
          if loopPlot.getFeatureType() != iDarkIce and loopPlot2.getFeatureType() != iDarkIce:
            if not loopPlot.isUnit() and not loopPlot.isOwned():
              if loopPlot.isWater() and loopPlot2.isWater() and gc.getGame().getGameTurnYear() > -600:
                barbPlayer.initUnit(iUnitTypeMerchant2, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              elif not loopPlot.isWater() and not loopPlot.isPeak():
                barbPlayer.initUnit(iUnitTypeMerchant1, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barb. Handelskarren erschaffen",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# -- Merchants Ende ------------------------------------------

# -- Huns | Hunnen erschaffen: Hunnischer Reiter | ab 250 AD  ---------

    iHuns = 0
    if gc.getGame().getGameTurnYear() == 250: iHuns = 20
    elif gc.getGame().getGameTurnYear() == 255: iHuns = 24
    elif gc.getGame().getGameTurnYear() == 260: iHuns = 28
    elif gc.getGame().getGameTurnYear() >= 270 and gc.getGame().getGameTurnYear() <= 400 and iGameTurn % 10 == 0: iHuns = 28  # Diesen Wert auch unten bei der Meldung angeben!

    if iHuns > 0:

      CivHuns = gc.getInfoTypeForString("CIVILIZATION_HUNNEN")
      bHunsAlive = False

      iRange = gc.getMAX_PLAYERS()
      for iPlayer in range(iRange):
        pPlayer = gc.getPlayer(iPlayer)
        # Hunnen sollen nur auftauchen, wenn es nicht bereits Hunnen gibt
        if pPlayer.getCivilizationType() == CivHuns and pPlayer.isAlive():
          bHunsAlive = True
          break

      if not bHunsAlive:
        iRange = gc.getMAX_PLAYERS()
        for iPlayer in range(iRange):
          pPlayer = gc.getPlayer(iPlayer)

          # Message PopUps
          if iHuns < 28 and pPlayer.isAlive() and pPlayer.isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            if iHuns == 2: popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_1",("", )))
            elif iHuns == 4: popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_2",("", )))
            else: popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_3",("", )))
            popupInfo.addPopup(pPlayer.getID())
            CyAudioGame().Play2DSound('AS2D_THEIRDECLAREWAR')

        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()
        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

        # 15 Versuche einen Plot zu finden
        bPlot = False
        for i in range (15):
          # Diese Koordinaten entsprechen Nord-Osten
          iRandX = iMapW - 15 + self.myRandom(15, None)
          iRandY = iMapH - 15 + self.myRandom(15, None)
          loopPlot = gc.getMap().plot(iRandX, iRandY)
          if None != loopPlot and not loopPlot.isNone():
            if loopPlot.getFeatureType() != iDarkIce:
              if not loopPlot.isUnit() and not loopPlot.isWater() and not loopPlot.isOwned():
                bPlot = True
                break

        # wenn ein Plot gefunden wurde
        if bPlot:

          # Hunnen versuchen zu erstellen  1 == 2: Ausgeschaltet!
          if gc.getGame().getGameTurnYear() >= 250 and gc.getGame().countCivPlayersAlive() < 18 and 1 == 2:
            # freie PlayerID herausfinden
            iHunsID = 0
            for i in range(18):
              pPlayer = gc.getPlayer(i)
              if not pPlayer.isEverAlive():
                iHunsID = i
                break
            # wenn keine nagelneue ID frei ist, dann eine bestehende nehmen
            if iHunsID == 0:
              for i in range(18):
                j = 18-i
                pPlayer = gc.getPlayer(j)
                if not pPlayer.isAlive():
                  iHunsID = j
                  break

            if iHunsID > 0:
              # Hunnen erstellen
              LeaderHuns = gc.getInfoTypeForString("LEADER_ATTILA")
              gc.getGame().addPlayer(iHunsID,LeaderHuns,CivHuns)
              pPlayer = gc.getPlayer(iHunsID)

              for i in range(8):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              for i in range(4):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SPEARMAN"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              for i in range(6):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_WORKER"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              for i in range(3):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SETTLER"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              for i in range(9):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_ARCHER"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              for i in range(9):
                pPlayer.initUnit(gc.getInfoTypeForString("UNIT_HORSE"), loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

              pPlayer.setCurrentEra(3)
              pPlayer.setGold(300)

              # increasing Anger to all other CIVs
              # and looking for best tech player
              pTeam = gc.getTeam(pPlayer.getTeam())
              iPlayerBestTechScore = -1
              iTechScore = 0
              iRange = gc.getMAX_PLAYERS()
              for i in range(iRange):
                pSecondPlayer = gc.getPlayer(i)
                # increases Anger for all AIs
                if pSecondPlayer.getID() != pPlayer.getID() and pSecondPlayer.isAlive():
                  # Haltung aendern
                  pPlayer.AI_changeAttitudeExtra(i,-5)
                  # Krieg erklaeren
                  pTeam.declareWar(pSecondPlayer.getTeam(), 0, 6)
                  # TechScore herausfinden
                  if iTechScore < pSecondPlayer.getTechScore():
                    iTechScore = pSecondPlayer.getTechScore()
                    iPlayerBestTechScore = i

              # Techs geben
              if iPlayerBestTechScore > -1:
                xTeam = gc.getTeam(gc.getPlayer(iPlayerBestTechScore).getTeam())
                iTechNum = gc.getNumTechInfos()
                for iTech in range(iTechNum):
                  if gc.getTechInfo(iTech) != None:
                    if xTeam.isHasTech(iTech) and not pTeam.isHasTech(iTech):
                      if gc.getTechInfo(iTech).isTrade():
                        pTeam.setHasTech(iTech, 1, iHunsID, 0, 0)

          else:
            iUnitType = gc.getInfoTypeForString('UNIT_MONGOL_KESHIK')
            barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
            for j in range(iHuns):
              barbPlayer.initUnit(iUnitType, loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

# -- Hunnen Ende ------------------------------------------



# ------ Handelsposten erzeugen Kultur (PAE V Patch 3: und wieder Forts/Festungen)
# ------ Berberloewen erzeugen
# ------ Wildpferde, Wildelefanten, Wildkamele ab PAE V
    lImpForts = []
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_HANDELSPOSTEN'))
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT'))
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT2'))

    bonus_lion = gc.getInfoTypeForString('BONUS_LION')
    bonus_horse = gc.getInfoTypeForString('BONUS_HORSE')
    bonus_camel = gc.getInfoTypeForString('BONUS_CAMEL')
    bonus_ivory = gc.getInfoTypeForString('BONUS_IVORY')
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for x in range(iMapW):
      for y in range(iMapH):
        loopPlot = gc.getMap().plot(x,y)
        #if loopPlot != None and not loopPlot.isNone():
        if loopPlot.getFeatureType() == iDarkIce: continue
        if not loopPlot.isWater() and not loopPlot.isPeak() and not loopPlot.isCity():

            iPlotOwner = loopPlot.getOwner()

            # Handelsposten und Forts
            if iPlotOwner == -1 and loopPlot.getImprovementType() in lImpForts:
              # Init
              iOwner = -1

              # Handelsposten
              if loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):

                str = loopPlot.getScriptData()
                if str.isdigit(): iOwner = int(str)

              # Forts
              else:

                if loopPlot.getNumUnits() > 0:
                  # Besitzer ist der mit den meisten Einheiten drauf
                  OwnerArray = []
                  iRange = gc.getMAX_PLAYERS()
                  for i in range(iRange):
                    OwnerArray.append(0)

                  iNumUnits = loopPlot.getNumUnits()
                  for i in range (iNumUnits):
                    if loopPlot.getUnit(i).isMilitaryHappiness():
                      iOwner = loopPlot.getUnit(i).getOwner()
                      if iOwner > -1: OwnerArray[iOwner] += 1

                  if max(OwnerArray) > 0:
                    iOwner = OwnerArray.index(max(OwnerArray))
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Owner",iOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

              iRange = gc.getMAX_PLAYERS()
              for i in range(iRange):
                iPlayerID = gc.getPlayer(i).getID()
                if iPlayerID == iOwner:
                  loopPlot.setCulture(iPlayerID,1,True)
                  loopPlot.setOwner(iPlayerID)
                else:
                  loopPlot.setCulture(iPlayerID,0,True)

            # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS)
            # Lion - 2% Appearance
            elif iPlotOwner == -1 and loopPlot.getBonusType(-1) == bonus_lion:
              if loopPlot.getImprovementType() == -1:
                if loopPlot.getNumUnits() < 3:
                  if self.myRandom(50, None) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_LION")
                    gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitType, x, y, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barb. Atlasloewe erschaffen",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Horse - 1.5% Appearance
            elif loopPlot.getBonusType(iPlotOwner) == bonus_horse: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if self.myRandom(75, None) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_WILD_HORSE")

                    # Check Owner
                    iNewUnitOwner = gc.getBARBARIAN_PLAYER()
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PFERDEZUCHT")):
                        iNewUnitOwner = iPlotOwner

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pferd erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Camel - 1.5% Appearance
            elif loopPlot.getBonusType(iPlotOwner) == bonus_camel: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if self.myRandom(75, None) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_WILD_CAMEL")

                    # Check Owner
                    iNewUnitOwner = gc.getBARBARIAN_PLAYER()
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_KAMELZUCHT")):
                        iNewUnitOwner = iPlotOwner

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Kamel erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Elefant - 1.5% Appearance
            elif loopPlot.getBonusType(iPlotOwner) == bonus_ivory: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if self.myRandom(75, None) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_ELEFANT")

                    # Check Owner
                    iNewUnitOwner = gc.getBARBARIAN_PLAYER()
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
                        iNewUnitOwner = iPlotOwner

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Elefant erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# --------------------
    # PAE Debug Mark
    #"""

# global
  def onBeginPlayerTurn(self, argsList):
    'Called at the beginning of a players turn'
    iGameTurn, iPlayer = argsList
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())

    # Reset InstanceModifier (Fighting Promotions, Hiring costs for mercenaries)
    self.PAEInstanceFightingModifier = []
    self.PAEInstanceHiringModifier = []

    # ------- Scenario PeloponnesianWarKeinpferd Events Poteidaia, Megara, Plataiai, Syrakus
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    if sScenarioScriptData == "PeloponnesianWarKeinpferd":
      iTeam = pPlayer.getTeam()
      iAthen = 0
      iSparta = 1
      iKorinth = 2
      iTheben = 4
      iSyrakus = 16
      # Event 1: Poteidaia verlangt geringere Abgaben
      iTurnPotei = 8 # Runde, in der das Popup fuer den Menschen erscheinen soll
      # Die KI reagiert sofort noch in dieser Runde, der Mensch erhaelt erst in der naechsten Runde das Popup
      # Nur, wenn Poteidaia existiert + von Athen kontrolliert wird
      pPoteidaia = CyMap().plot(56, 46).getPlotCity()
      if iTeam == iAthen and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia != None:
       if pPoteidaia.getOwner() == iAthen:
        if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_DESC",()))
          popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia1")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_1", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_2", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_3", ()), "")
          popupInfo.addPopup(iPlayer)
        else:
          iAiDecision = self.myRandom(3, None)
          CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia1([iAiDecision])
      # Event 2: Krieg um Poteidaia
      iTurnPotei = 18 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      # Nur, wenn Poteidaia existiert + von Athen kontrolliert wird
      if iTeam == iAthen and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia != None:
        if pPoteidaia.getOwner() == iAthen:
          # Event 2.1: Reaktion Athens
          # Poteidaia wechselt zu Korinth (Team 2)
          self.doRenegadeCity(pPoteidaia, 2, -1, -1, -1)
          pKorinth = gc.getPlayer(iKorinth)
          ePantodapoi = gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON")
          iRange = self.myRandom(3, None)
          # Korinth erhaelt 0 - 2 zusaetzliche makedonische Hilfstrupps in Poteidaia
          for i in range(iRange): pKorinth.initUnit(ePantodapoi, 56, 46, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 15, CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_WORLDNEWS", ()), None, 2, None, ColorTypes(11), 0, 0, False, False)
          if pPlayer.isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_DESC",()))
            popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia2")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_1", ()), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_2", ()), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_3", ()), "")
            popupInfo.addPopup(iPlayer)
          else:
            iAiDecision = self.myRandom(3, None)
            CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia2([iAiDecision])
      # Nur, wenn Poteidaia existiert + von Korinth oder Athen kontrolliert wird (menschlicher Spieler spielt Korinth: zu diesem Zeitpunkt gehoert Poteidaia noch Athen; KI spielt Korinth: ist bereits zu Korinth gewechselt)
      elif iTeam == iKorinth and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia != None:
        if pPoteidaia.getOwner() == iKorinth or pPoteidaia.getOwner() == iAthen:
          # Event 2.2: Reaktion Korinths
          if pPlayer.isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_DESC",()))
            popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia3")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_1", ()), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_2", ()), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_3", ()), "")
            popupInfo.addPopup(iPlayer)
          else:
            iAiDecision = self.myRandom(3, None)
            CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia3([iAiDecision])
      # Event 3: Megara unterstuetzt Korinth
      iTurnMegaraAthen = 22 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      # Nur, wenn Megara existiert + von Korinth kontrolliert wird
      pMegara = CyMap().plot(55, 30).getPlotCity()
      if iTeam == iAthen and ((iGameTurn == iTurnMegaraAthen-1 and pPlayer.isHuman()) or (iGameTurn == iTurnMegaraAthen and not pPlayer.isHuman())) and not pMegara.isNone() and pMegara != None:
       if pMegara.getOwner() == iKorinth:
        # Event 3.1: Reaktion Athens
        if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_DESC",()))
          popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Megara1")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_1", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_2", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_3", ()), "")
          popupInfo.addPopup(iPlayer)
        else:
          iAiDecision = self.myRandom(3, None)
          CvScreensInterface.peloponnesianWarKeinpferd_Megara1([iAiDecision])
      # Event 3.2: Reaktion Spartas (nur wenn Sparta noch keinen Krieg mit Athen hat)
      iTurnMegaraSparta = 23 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      # Nur, wenn Megara existiert + von Korinth kontrolliert wird
      if iTeam == iSparta and ((iGameTurn == iTurnMegaraSparta-1 and pPlayer.isHuman()) or (iGameTurn == iTurnMegaraSparta and not pPlayer.isHuman())) and not pMegara.isNone() and pMegara != None:
       if pMegara.getOwner() == iKorinth and not gc.getTeam(iTeam).isAtWar(iAthen):
        if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_DESC",()))
          popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Megara2")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3", ()), "")
          popupInfo.addPopup(iPlayer)
        else:
          iAiDecision = self.myRandom(3, None)
          CvScreensInterface.peloponnesianWarKeinpferd_Megara2([iAiDecision])
      # Event 4: Kriegseintritt Thebens
      iTurnPlataiai = 28 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      if iTeam == iTheben and ((iGameTurn == iTurnPlataiai-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPlataiai and not pPlayer.isHuman())):
        if not gc.getTeam(iTeam).isAtWar(iAthen): # Nur wenn Theben und Athen Frieden haben
         if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_DESC",()))
          popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Plataiai1")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_1", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_2", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_3", ()), "")
          popupInfo.addPopup(iPlayer)
         else:
          iAiDecision = self.myRandom(3, None)
          CvScreensInterface.peloponnesianWarKeinpferd_Plataiai1([iAiDecision])
      # Event 5: Volksversammlung Athens will Krieg gegen Syrakus
      # Event 5.1: Ankuendigung fuer Athen
      iTurnSyra1 = 194 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      pSyrakus = CyMap().plot(15, 24).getPlotCity()
      # Nur wenn Syrakus (Stadt) noch existiert und der Civ Syrakus gehoert
      if iTeam == iAthen and (iGameTurn == iTurnSyra1 -1) and not pSyrakus.isNone() and pSyrakus != None:
       if pSyrakus.getOwner() == iSyrakus:
        if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_SAVEMONEY",()))
          popupInfo.addPopup(iPlayer)
      # Event 5.2: Athen waehlt Groesse der Flotte
      iTurnSyra2 = 204 # Runde, in der die Popups fuer den Menschen erscheinen sollen
      if iTeam == iAthen and ((iGameTurn == iTurnSyra2 -1 and pPlayer.isHuman()) or (iGameTurn == iTurnSyra2 and not pPlayer.isHuman())):
        if not gc.getTeam(iTeam).isAtWar(iSyrakus): # Nur wenn Syrakus und Athen Frieden haben
         if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_DESC",()))
          popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Syra1")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_1", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_2", ()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_3", ()), "")
          popupInfo.addPopup(iPlayer)
         else:
          iAiDecision = self.myRandom(3, None)
          CvScreensInterface.peloponnesianWarKeinpferd_Syra1([iAiDecision])

      # Temporaere Effekte der Events rueckgaengig machen (Event 3.1 Handelsboykott, Event 3.2 Bronze fuer Sparta)
      if iGameTurn == iTurnMegaraAthen + 10:
        iAthen = 0
        iNordIonien = 12
        iSuedIonien = 13
        eHafen = gc.getInfoTypeForString("BUILDING_HARBOR")
        eMarkt = gc.getInfoTypeForString("BUILDING_MARKET")
        eHafenClass = gc.getBuildingInfo(eHafen).getBuildingClassType()
        eMarktClass = gc.getBuildingInfo(eMarkt).getBuildingClassType()
        lPlayer = [iAthen, iNordIonien, iSuedIonien]
        for iPlayer in lPlayer:
          pPlayer = gc.getPlayer(iPlayer)
          iNumCities = pPlayer.getNumCities()
          for iCity in range(iNumCities):
            pCity = pPlayer.getCity(iCity)
            if pCity != None and not pCity.isNone():
              if pCity.isHasBuilding(eHafen):
                iStandard = 0 # Normaler Goldertrag ohne Event
                pCity.setBuildingCommerceChange(eHafenClass, 0, iStandard) # 0 = Gold
              if pCity.isHasBuilding(eMarkt):
                iStandard = 0
                pCity.setBuildingCommerceChange(eMarktClass, 0, iStandard) # 0 = Gold
      if iGameTurn == iTurnMegaraSparta + 10:
        # Bronze wird a
        eBronze = gc.getInfoTypeForString("BONUS_BRONZE")
        pCity = CyMap().plot(52, 23).getPlotCity()
        if pCity != None and not pCity.isNone():
          if pCity.getFreeBonus(eBronze) > 1:pCity.changeFreeBonus(eBronze, -10)


    #---------End PeloponnesianWarKeinpferd-------------------

#    if iPlayer == gc.getGame().getActivePlayer():
#      lCities = PyPlayer(iPlayer).getCityList()
#      iCities = len(lCities)
#
#      if iCities > 0:
#        pCity = pPlayer.getCity( lCities[ 0 ].getID( ) )
#        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Food",pCity.getFood())), None, 2, None, ColorTypes(10), 0, 0, False, False)
#        pCity.changeFood(10)
#        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Food",pCity.getFood())), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ----- CHECK CIV on Turn - change Team ID (0 = eg Romans) in gc.getPlayer(0).
    if self.bPAE_ShowMessagePlayerTurn:
      showPlayer = iPlayer # + 1
      #if showPlayer > gc.getMAX_PLAYERS(): iPlayer = 0
      if showPlayer < gc.getMAX_PLAYERS():
        if gc.getPlayer(showPlayer).isAlive():
          thisPlayer = gc.getPlayer(showPlayer).getCivilizationDescription(0)
          if (self.bAllowCheats):
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN",(thisPlayer,"")), None, 2, None, ColorTypes(14), 0, 0, False, False)
          else:
            iThisTeam = gc.getPlayer(showPlayer).getTeam()
            if gc.getTeam(iThisTeam).isHasMet(pPlayer.getTeam()):
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN",(thisPlayer,"")), None, 2, None, ColorTypes(14), 0, 0, False, False)
            else:
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN2",("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)

          # nur notwendig, wenn man wissen moechte, wer als naechster kommt:
          #if gc.getPlayer(iPlayer+1).isAlive(): nextPlayer = gc.getPlayer(iPlayer+2).getCivilizationShortDescription(0)

# -- TESTMESSAGE
#    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test1",gc.getGame().getActivePlayer())), None, 2, None, ColorTypes(10), 0, 0, False, False)

#    if CyInterface().isOOSVisible():
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("OOS-Fehler - Player",iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)

#    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("MaxPlayers",gc.getMAX_PLAYERS())), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # PAE Debug Mark
    #"""

# -- Prevent BTS TECH BUG/Forschungsbug: AI chooses Tech if -1 -> 25% to push
    if iPlayer != gc.getBARBARIAN_PLAYER() and not pPlayer.isHuman() and pPlayer.getCurrentResearch() == -1:
      if self.myRandom(4, None) == 1:
        techs = []
        iRange = gc.getNumTechInfos()
        for iTech in range(iRange):
                if pPlayer.canResearch(iTech, false):
                    iCost = pTeam.getResearchLeft(iTech)
                    if iCost > 0:
                        techs.append((-iCost, iTech))
        if techs:
                techs.sort()
                iTech = techs[0][1]
                pTeam.changeResearchProgress(iTech, 1, iPlayer)
                pPlayer.clearResearchQueue()
                #pPlayer.pushResearch (iTech, 1)

    # MESSAGES: city growing (nur im Hot-Seat-Modus)
    if gc.getGame().isHotSeat():
#     for iPlayer in range(gc.getMAX_PLAYERS()):
#      pPlayer = gc.getPlayer(iPlayer)
      if pPlayer.isHuman():
        iNumCities = pPlayer.getNumCities()
        for i in range (iNumCities):
              pCity = pPlayer.getCity(i)
              if not pCity.isNone():
                if pCity.getFoodTurnsLeft() == 2  and pCity.foodDifference(True) > 0 and not pCity.isFoodProduction() and not pCity.AI_isEmphasize(5):
                  # MESSAGE: city will grow / Stadt wird wachsen
                  iPop = pCity.getPopulation() + 1
                  CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_WILL_GROW",(pCity.getName(),iPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

                  # MESSAGE: city gets/is unhappy / Stadt wird/ist unzufrieden
                  if pCity.happyLevel() - pCity.unhappyLevel(0) <= 0:
                    if pCity.happyLevel() - pCity.unhappyLevel(0) == 0:
                      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                    else:
                      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

                  # MESSAGE: city gets/is unhealthy / Stadt wird/ist ungesund
                  if pCity.goodHealth() - pCity.badHealth(False) <= 0:
                    if pCity.goodHealth() - pCity.badHealth(False) == 0:
                      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                    else:
                      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)


# +++++ AI Cities defend with bombardment of located units (Stadtverteidigung/Stadtbelagerung)
# +++++ AI Hires Units (mercenaries)
    if not pPlayer.isHuman():

      iNumCities = pPlayer.getNumCities()
      for iCity in range (iNumCities):
       pCity = pPlayer.getCity(iCity)
       if not pCity.isNone():
        pPlot = pCity.plot()


        # Auf welchen Plots befinden sich gegnerische Einheiten
        if pPlot != None and not pPlot.isNone():
         PlotArray = []
         iEnemyUnits = 0
         for x in range(3):
          for y in range(3):
              loopPlot = gc.getMap().plot(pPlot.getX()-1+x,pPlot.getY()-1+y)
              if loopPlot != None and not loopPlot.isNone():
                iNumUnits = loopPlot.getNumUnits()
                if iNumUnits >= 4:
                  for i in range (iNumUnits):
                    iOwner = loopPlot.getUnit(i).getOwner()
                    if pTeam.isAtWar(gc.getPlayer(iOwner).getTeam()):
                      if not loopPlot.getUnit(i).isInvisible(pPlayer.getTeam(),0):
                        PlotArray.append(loopPlot)
                        iEnemyUnits += loopPlot.getNumUnits()
                        break


         # Stadteinheiten durchgehen
         if len(PlotArray) > 0:
           # Schleife fuer Stadteinheiten
           # Bombardement
           iNumUnits = pPlot.getNumUnits()
           for i in range (iNumUnits):
             pUnit = pPlot.getUnit(i)
             if pUnit.isRanged():
              if pUnit.getOwner() == iPlayer:
               if not pUnit.isMadeAttack() and pUnit.getImmobileTimer() <= 0:

                 # getbestdefender -> getDamage
                 BestDefender = []
                 for plot in PlotArray:
                   pBestDefender = plot.getBestDefender(-1,-1,pUnit,1,0,0)
                   BestDefender.append((pBestDefender.getDamage(),plot))

                 # bestdefenderplot angreifen ->  pCityUnit.rangeStrike(x,y)
                 BestDefender.sort()
                 # Ab ca 50% Schaden aufhoeren
                 if BestDefender[0][0] < 55:
                   plot = BestDefender[0][1]
                   pUnit.rangeStrike(plot.getX(),plot.getY())
                   #self.doRangedStrike(pCity,pUnit,plot,True)
                 else:
                   break


           # AI - Extern Unit support
           # 1) Reservists
           # 2) Hire Mercenaries
           # Muessen Mercenaries angeheuert werden? AI Hire
           # 70% Archer
           # 30% Other
           # BETTER AI: half price
           iCityUnits = pPlot.getNumUnits()
           iMaintainUnits = pCity.getYieldRate(0) - iCityUnits

           # 1) Reservisten
           if iMaintainUnits > 0 and iCityUnits * 2 <= iEnemyUnits:
             iReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST

             if iReservists > 0:

               # Einheiten definieren
               lResUnits = []
               # Schildtraeger fuer AI immer verfuegbar
               lResUnits.append(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"))
               # Auxiliars
               iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
               if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()): lResUnits.append(iUnit)
               iUnit = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
               if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE")): lResUnits.append(iUnit)
               # Archer
               iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
               if pCity.canTrain(iUnit,0,0): lResUnits.append(iUnit)
               else: lResUnits.append(gc.getInfoTypeForString("UNIT_ARCHER"))

               while iReservists > 0 and iMaintainUnits > 0:
                 # choose unit
                 iRand = self.myRandom(len(lResUnits), None)
                 iUnit = lResUnits[iRand]

                 NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                 NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
                 NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
                 NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
                 NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

                 pCity.changeFreeSpecialistCount(19, -1)
                 iReservists -= 1
                 iMaintainUnits -= 1
                 iCityUnits += 1


           # 2) Mercenaries
           # PAE Better AI: AI has no cost malus when hiring units
           # Units amount 1:3
           iMultiplikator = 3
           if iMaintainUnits > 0 and iCityUnits * iMultiplikator <= iEnemyUnits and pPlayer.getGold() > 100:
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SOELDNERPOSTEN")):

             # Check neighbours
             Neighbors = []
             # Eigene CIV inkludieren
             if pCity.isConnectedToCapital(iPlayer): Neighbors.append(pPlayer)
             # Nachbarn inkludieren
             iRange = gc.getMAX_PLAYERS()
             for iAllPlayer in range (iRange):
               if pCity.isConnectedToCapital(iAllPlayer):
                  Neighbors.append(gc.getPlayer(iAllPlayer))
               # alt:
               #ThisPlayer = gc.getPlayer(iAllPlayer)
               #if ThisPlayer.isAlive():
               #  if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
               #    Neighbors.append(ThisPlayer)
             # ------------------

             if len(Neighbors) > 0:
              # check units
              bUnit1 = false
              bUnit2 = false
              bUnit3 = false
              bUnit4 = false
              bUnit5 = false
              bUnit6 = false
              bUnit7 = false
              bUnit8 = false
              bUnit9 = false
              bUnit10 = false
              bUnit11 = false
              bUnit12 = false
              bUnit13 = false
              bUnit14 = false
              bUnit15 = false
              bUnit16 = false
              bUnit17 = false

              # Archers werden fix angeheuert
              iUnitArcher1 = gc.getInfoTypeForString("UNIT_ARCHER")
              iUnitArcher2 = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
              iCostArcher1 = PyInfo.UnitInfo(iUnitArcher1).getProductionCost() / 2
              iCostArcher2 = PyInfo.UnitInfo(iUnitArcher2).getProductionCost() / 2

              iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
              iBonus2 = gc.getInfoTypeForString("BONUS_IRON")
              iBonus3 = gc.getInfoTypeForString("BONUS_HORSE")
              iBonus4 = gc.getInfoTypeForString("BONUS_IVORY")

              OtherUnits = []
              OtherUnits.append(gc.getInfoTypeForString("UNIT_PELTIST"))
              for Neighbor in Neighbors:
               if not bUnit1 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY2")): bUnit1 = true
               if not bUnit2 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY3")): bUnit2 = true
               if not bUnit3 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SKIRMISH_TACTICS")): bUnit3 = true

               if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                 if not bUnit4 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")): bUnit4 = true
                 if not bUnit5 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): bUnit5 = true
                 if not bUnit6 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG3")): bUnit6 = true
                 if not bUnit7 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")): bUnit7 = true
               if Neighbor.hasBonus(iBonus2):
                 if not bUnit8 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG5")): bUnit8 = true
                 if not bUnit9 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WURFAXT")): bUnit9 = true
                 if not bUnit17 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): bUnit17 = true

               if pPlayer.getCurrentEra() <= 2:
                 if not bUnit10 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_CHARIOTS")): bUnit10 = true
                 if Neighbor.hasBonus(iBonus3):
                   if not bUnit11 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PFERDEZUCHT")) and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY2")):
                     bUnit11 = true
                   if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                     if not bUnit12 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_THE_WHEEL3")):
                       bUnit11 = true
                       bUnit12 = true
               else:
                 if Neighbor.hasBonus(iBonus3):
                   if not bUnit13 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_2")): bUnit13 = true
                   if not bUnit14 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_3")) and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_HORSE_ARCHER")):
                     bUnit14 = true
                   if not bUnit15 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_CAVALRY")):
                     if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                       bUnit14 = true
                       bUnit15 = true

               if Neighbor.hasBonus(iBonus4):
                 if not bUnit16 and gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")): bUnit16 = true


              # Fill OtherUnits
              if bUnit1: iUnitArcher1 = gc.getInfoTypeForString("UNIT_ARCHER")
              if bUnit2: iUnitArcher2 = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
              if bUnit3: OtherUnits.append(gc.getInfoTypeForString("UNIT_SKIRMISHER"))

              if bUnit17: OtherUnits.append(gc.getInfoTypeForString("UNIT_AXEMAN2"))
              elif bUnit4: OtherUnits.append(gc.getInfoTypeForString("UNIT_AXEMAN"))
              else: OtherUnits.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
              if bUnit5: OtherUnits.append(gc.getInfoTypeForString("UNIT_SPEARMAN"))
              else: OtherUnits.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))

              if bUnit7: OtherUnits.append(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"))
              elif bUnit6: OtherUnits.append(gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT")))

              if bUnit8: OtherUnits.append(gc.getInfoTypeForString("UNIT_SWORDSMAN"))
              if bUnit9: OtherUnits.append(gc.getInfoTypeForString("UNIT_WURFAXT"))

              if bUnit11: OtherUnits.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
              if bUnit12: OtherUnits.append(gc.getInfoTypeForString("UNIT_CHARIOT"))
              elif bUnit10: OtherUnits.append(gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT"))

              if bUnit13: OtherUnits.append(gc.getInfoTypeForString("UNIT_HORSEMAN"))
              if bUnit14: OtherUnits.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
              if bUnit15: OtherUnits.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))

              if bUnit16: OtherUnits.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))

              # choose units
              iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
              # AI hires max 2 - 4 units per city and turn
              iHiredUnits = 0
              iHiredUnitsMax = 2 + self.myRandom(3, None)
              while iMaintainUnits > 0 and pPlayer.getGold() > 100 and iHiredUnits < iHiredUnitsMax and iCityUnits * iMultiplikator < iEnemyUnits:
                iUnit = -1
                iGold = pPlayer.getGold()

                iRand = self.myRandom(10, None)
                if iRand < 7:
                 if bUnit2 and iGold > iCostArcher2 and self.myRandom(5, None) == 1: iUnit = iUnitArcher2
                 elif iGold > iCostArcher1: iUnit = iUnitArcher1
                else:
                 iTry = 0
                 while iTry < 3:
                   iOtherUnit = self.myRandom(len(OtherUnits), None)
                   iUnit = OtherUnits[iOtherUnit]
                   iCost = PyInfo.UnitInfo(iUnit).getProductionCost() / 2
                   if iCost <= 0: iCost = 50
                   if pPlayer.getGold() <= iCost:
                     iTry += 1
                   else:
                     break

                if iUnit != -1:
                 iCost = PyInfo.UnitInfo(iUnit).getProductionCost() / 2
                 if iCost <= 0: iCost = 50
                 if pPlayer.getGold() > iCost:

                   pPlayer.changeGold(-iCost)
                   gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
                   NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                   NewUnit.setHasPromotion(iPromo, True)
                   #NewUnit.finishMoves()
                   NewUnit.setImmobileTimer(1)

                   iMaintainUnits -= 1
                   iCityUnits += 1
                   iHiredUnits += 1

                # quit while
                if iGold <= iCostArcher1: break




# +++++ STACKs ---------------------------------------------------------

# Belagerugsstacks der KI herausfinden fuer Fernangriff auf die gegnerische Stadt

# PAE IV Healer aufladen
# PAE V: Staedte sind extra

    # Plots herausfinden
    #if iPlayer != gc.getBARBARIAN_PLAYER():
    # iPlayer > -1: wegen einrueckung!
    # PAE Better AI:
    # HI: 20 : 40 Units
    # AI: 30 : 50 Units

    if pPlayer.isHuman():
       iStackLimit1 = 20
       iStackLimit2 = 40
    else:
       iStackLimit1 = 40
       iStackLimit2 = 60

    if iPlayer > -1:
     PlotArrayRebellion = []
     PlotArraySupply = []
     PlotArrayStackAI = []
     iNumUnits = pPlayer.getNumUnits()
     lHealerPlots = []
     lFormationPlots = []
     iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
     iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")

     for i in range(iNumUnits):
       sUnit = pPlayer.getUnit(i)
       # tmpA: OBJECTS (tmpPlot) KANN MAN NICHT mit NOT IN in einer Liste pruefen!
       tmpA = [sUnit.getX(),sUnit.getY()]
       tmpPlot = gc.getMap().plot(sUnit.getX(),sUnit.getY())
       if not tmpPlot.isWater():
         if sUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
           if tmpA not in lHealerPlots:
             lHealerPlots.append(tmpA)
         # PAE V: bei den Staedten gibts ne eigene funktion bei city supply
         if not tmpPlot.isCity():
           if tmpA not in PlotArraySupply:
             # 1. Instanz - Versorgung auf Land
             tmpAnz = tmpPlot.getNumDefenders(iPlayer)
             if tmpAnz >= 6:

              # AI Stack ausserhalb einer Stadt, in feindlichem Terrain
              if not pPlayer.isHuman():
                if tmpPlot.getOwner() > -1:
                  if tmpPlot.getOwner() != iPlayer:
                    if tmpA not in PlotArrayStackAI:
                      if pTeam.isAtWar(gc.getPlayer(tmpPlot.getOwner()).getTeam()):
                        PlotArrayStackAI.append(tmpA)

              if tmpAnz >= iStackLimit1:
               PlotArraySupply.append(tmpA)
               # 2. Instanz - Rebellionsgefahr auf Land
               if tmpAnz >= iStackLimit2:
                 PlotArrayRebellion.append(tmpA)
               # ***TEST***
               #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stack (Zeile 3377)",tmpPlot.getNumDefenders(iPlayer))), None, 2, None, ColorTypes(10), 0, 0, False, False)

       # PAE V - Formations ++++
       # DEBUG: Formation entfernen
       #if sUnit != None: self.doUnitFormation (sUnit, -1)

       # Flucht
       #iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT")
       #if sUnit.isHasPromotion(iFormation):
       #   if sUnit.getDamage() < 70: sUnit.setHasPromotion(iFormation, False)

       # Kapitulation
       #iFormation = gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG")
       #if sUnit.isHasPromotion(iFormation):
       #    if sUnit.getDamage() < 80 or sUnit.hasCargo(): sUnit.setHasPromotion(iFormation, False)
       #elif sUnit.getDamage() >= 80 and not sUnit.hasCargo(): sUnit.setHasPromotion(iFormation, True)

        # AI Formations
       if not pPlayer.isHuman():
         if tmpPlot.getNumUnits() > 2:
           if tmpA not in lFormationPlots:
             lFormationPlots.append(tmpA)
         else:
          # more than 50% damage -> go defensive
           if sUnit.getDamage() > 50: self.doAIUnitFormations (sUnit, False, False, False)

         # Missing fort on a plot
         if sUnit.isHasPromotion(iPromoFort) or sUnit.isHasPromotion(iPromoFort2):
            iImp = tmpPlot.getImprovementType()
            if iImp > -1:
               if gc.getImprovementInfo(iImp).getDefenseModifier() < 10 or tmpPlot.getOwner() != sUnit.getOwner(): self.doUnitFormation (sUnit, -1)
            else: self.doUnitFormation (sUnit, -1)


     if len(lFormationPlots) > 0:
       for h in lFormationPlots:
         loopPlot = gc.getMap().plot(h[0],h[1])
         if not loopPlot.isCity(): self.doAIPlotFormations (loopPlot, iPlayer)

     # End Formations ++++++

     # AI Stacks vor einer gegnerischen Stadt ---------------------------------------
     if len(PlotArrayStackAI) > 0:
       for h in PlotArrayStackAI:

         pPlotEnemyCity = None
         for x in range(3):
           for y in range(3):
              loopPlot = gc.getMap().plot(h[0]-1+x,h[1]-1+y)
              if loopPlot != None and not loopPlot.isNone():
                if loopPlot.isCity():
                      if pTeam.isAtWar(gc.getPlayer(loopPlot.getOwner()).getTeam()):
                          pPlotEnemyCity = loopPlot
                          break
           if pPlotEnemyCity != None: break

         # vor den Toren der feindlichen Stadt
         if pPlotEnemyCity != None:
           # Bombardement
           pStackPlot = gc.getMap().plot(h[0],h[1])
           iNumUnits = pStackPlot.getNumUnits()
           for i in range (iNumUnits):
             pUnit = pStackPlot.getUnit(i)
             if pUnit.isRanged():
              if pUnit.getOwner() == iPlayer:
               if not pUnit.isMadeAttack() and pUnit.getImmobileTimer() <= 0:

                 # getbestdefender -> getDamage
                 pBestDefender = pPlotEnemyCity.getBestDefender(-1,-1,pUnit,1,0,0)
                 # Ab ca 50% Schaden aufhoeren
                 if pBestDefender.getDamage() < 55:
                   pUnit.rangeStrike(pPlotEnemyCity.getX(), pPlotEnemyCity.getY())
                   #self.doRangedStrike(pPlotEnemyCity.getPlotCity(),pUnit,pPlotEnemyCity,False)
                 else:
                   break


     # +++++ Aufladen der Versorger UNIT_SUPPLY_WAGON ---------------------------------------
     if len(lHealerPlots) > 0:
       for h in lHealerPlots:
         loopPlot = gc.getMap().plot(h[0],h[1])

         # Init
         lHealer = []
         iSupplyChange = 0

         # Units calc
         iRange = loopPlot.getNumUnits()
         for iUnit in range(iRange):
           if loopPlot.getUnit(iUnit).getOwner() == iPlayer:
             if loopPlot.getUnit(iUnit).getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
               lHealer.append(loopPlot.getUnit(iUnit))

         # Plot properties
         if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"): bDesert = True
         else: bDesert = False

         # Inits for Supply Units (nur notwendig, wenns Versorger gibt)
         if len(lHealer) > 0:

           # Eigenes Terrain
           if loopPlot.getOwner() == iPlayer:
             if loopPlot.isCity():
               pCity = loopPlot.getPlotCity()
               # PAE V
               if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                 iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer)
               # PAE IV
               #if pCity.happyLevel() - pCity.unhappyLevel(0) == 0 or pCity.goodHealth() - pCity.badHealth(False) == 0: iSupplyChange += 25
               #elif pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
             elif loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_FORT"): iSupplyChange += 35
             elif loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_FORT2"): iSupplyChange += 35
             elif loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"): iSupplyChange += 25
             # PAE V: deaktiviert (weil Einheitengrenze sowieso vom Verbrauch abgezogen wird)
             #else: iSupplyChange += 20
           # Fremdes Terrain
           elif loopPlot.getOwner() != iPlayer:

             lImpFood = []
             lImpFood.append(gc.getInfoTypeForString("IMPROVEMENT_FARM"))
             lImpFood.append(gc.getInfoTypeForString("IMPROVEMENT_PASTURE"))
             lImpFood.append(gc.getInfoTypeForString("IMPROVEMENT_PLANTATION"))
             lImpFood.append(gc.getInfoTypeForString("IMPROVEMENT_BRUNNEN"))

             if loopPlot.getOwner() != -1:
               iTeam = pPlayer.getTeam()
               pTeam = gc.getTeam(iTeam)
               iTeamPlot = gc.getPlayer(loopPlot.getOwner()).getTeam()
               pTeamPlot = gc.getTeam(iTeamPlot)

               # Versorger auf Vassalenterrain - Aufladechance - Stadt: 100%, Land 20%
               if pTeamPlot.isVassal(pTeam.getID()):
                   if loopPlot.isCity():
                     pCity = loopPlot.getPlotCity()
                     # PAE V
                     if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                       iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(loopPlot.getOwner())
                     # PAE IV
                     #if pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
                   else:
                     if self.myRandom(10, None) < 2:
                       iSupplyChange += 20
                       if pPlayer.isHuman():
                         CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_SUPPLY_RELOAD_1",(gc.getPlayer(loopPlot.getOwner()).getCivilizationAdjective(3),0)), None, 2, lHealer[0].getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)

               # Versorger auf freundlichem Terrain - Aufladechance 30%, 20% oder 10%
               elif not pTeam.isAtWar(gc.getPlayer(loopPlot.getOwner()).getTeam()):
                 # Attitudes
                 #-11 and lower = Gracious
                 #-1 through -10 = Polite
                 #0 = Cautious
                 #1-10 = Annoyed
                 #11 through 100 = Furious
                 iAtt = gc.getPlayer(loopPlot.getOwner()).AI_getAttitude(iPlayer)
                 if iAtt < -10: iChance = 3
                 elif iAtt < 0: iChance = 2
                 elif iAtt == 0: iChance = 1
                 else: iChance = 0
                 if iChance > 0 and self.myRandom(10, None) < iChance:
                   if loopPlot.isCity():
                     pCity = loopPlot.getPlotCity()
                     # PAE V
                     if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                       iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(loopPlot.getOwner())
                     # PAE IV
                     #if pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
                   else: iSupplyChange += 20
                   if pPlayer.isHuman() and iSupplyChange > 0:
                     CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_SUPPLY_RELOAD_2",(gc.getPlayer(loopPlot.getOwner()).getNameKey(),0)), None, 2, lHealer[0].getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)


               # Versorger steht auf feindlichem Terrain
               else:
                 # Plot wird beschlagnahmt
                 if loopPlot.getImprovementType() in lImpFood: iSupplyChange += 10
                 #if loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_OASIS"): iSupplyChange += 10

             # Neutrales Terrain
             else:
                 if loopPlot.getImprovementType() in lImpFood: iSupplyChange += 10
                 #if loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_OASIS"): iSupplyChange += 10

           # Fluss
           if loopPlot.isRiver(): iSupplyChange += 10


           # ++++ Supply Units update ------------
           # 1. Aufladen
           for loopUnit in lHealer:

             if iSupplyChange <= 0: break

             # Maximalwert herausfinden
             if loopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_DRUIDE") or loopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_BRAHMANE"): iMaxHealing = 100
             else: iMaxHealing = 200
             # Trait Strategist / Stratege: +50% Kapazitaet / +50% capacity
             if gc.getPlayer(loopUnit.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_STRATEGE")):
                 iMaxHealing *= 3
                 iMaxHealing /= 2

             txt = loopUnit.getScriptData()
             if txt == "": txt = str(iMaxHealing) # 0 = leer/verbraucht, aber "" ist fabriksneu ;)
             iSupplyValue = int(txt)
             if iSupplyValue + iSupplyChange > iMaxHealing:
               iSupplyChange -= iMaxHealing - iSupplyValue
               iSupplyValue = iMaxHealing
             else:
               iSupplyValue += iSupplyChange
               iSupplyChange = 0
             loopUnit.setScriptData(str(iSupplyValue))


     # +++++ Versorgung der Armee - supply wagon ---------------------------------------
     if len(PlotArraySupply) > 0:

       # gc.getInfoTypeForString("UNIT_SUPPLY_WAGON") # Tickets: 200
       # gc.getInfoTypeForString("UNIT_DRUIDE") # Tickets: 100
       # gc.getInfoTypeForString("UNIT_BRAHMANE") # Tickets: 100
       # => UNITCOMBAT_HEALER

       lMounted = [gc.getInfoTypeForString("UNITCOMBAT_CHARIOT"),gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"),gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT")]
       lMelee = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"),gc.getInfoTypeForString("UNITCOMBAT_ARCHER")]

       for h in PlotArraySupply:
         loopPlot = gc.getMap().plot(h[0],h[1])

         # Init
         iMounted = 0
         iMelee = 0
         lHealer = []
         iSupplyChange = 0
         iNumUnits = loopPlot.getNumUnits()
         # PAE V: Stack Limit mit iStackLimit1 einbeziehen
         iHungryUnits = iNumUnits - iStackLimit1

         # Units calc
         for i in range(iNumUnits):
           if loopPlot.getUnit(i).getOwner() == iPlayer:
             iUnitType = loopPlot.getUnit(i).getUnitCombatType()
             if iUnitType == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
               lHealer.append(loopPlot.getUnit(i))
             elif iHungryUnits > 0:
               if iUnitType in lMounted:
                 iMounted += 1
                 iHungryUnits -= 1
               elif iUnitType in lMelee:
                 iMelee += 1
                 iHungryUnits -= 1

         # ***TEST***
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("UNITCOMBAT_MOUNTED",iMounted)), None, 2, None, ColorTypes(10), 0, 0, False, False)
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("UNITCOMBAT_MELEE",iMelee)), None, 2, None, ColorTypes(10), 0, 0, False, False)
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("UNITCOMBAT_HEALER",len(lHealer))), None, 2, None, ColorTypes(10), 0, 0, False, False)

         # Plot properties
         if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"): bDesert = True
         else: bDesert = False


         # Inits for Supply Units (nur notwendig, wenns Versorger gibt)
         if len(lHealer) > 0:

           # 2. Versorgen
           for loopUnit in lHealer:
             if iMounted <= 0 and iMelee <= 0: break
             if loopUnit.getScriptData() == "" or loopUnit.getScriptData() == "0": iSupplyValue = 0
             else: iSupplyValue = int(loopUnit.getScriptData())

             # ***TEST***
             #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Supply Unit init "+str(loopUnit.getID()),iSupplyValue)), None, 2, None, ColorTypes(10), 0, 0, False, False)

             if iSupplyValue > 0:
               # Mounted Units
               if bDesert:
                 if iSupplyValue > iMounted * 2:
                   iSupplyValue -= iMounted * 2
                   iMounted = 0
                 else:
                   iCalc = iSupplyValue / 2
                   iSupplyValue -= iCalc * 2
                   iMounted -= iCalc
               else:
                 iSupplyValue -= iMounted
                 if iSupplyValue < 0:
                   iMounted = -iSupplyValue
                   iSupplyValue = 0
                 else: iMounted = 0

               # Melee Units
               iSupplyValue -= iMelee
               if iSupplyValue < 0:
                 iMelee = -iSupplyValue
                 iSupplyValue = 0
               else: iMelee = 0

               loopUnit.setScriptData(str(iSupplyValue))

               # ***TEST***
               #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Supply Unit changed",iSupplyValue)), None, 2, None, ColorTypes(10), 0, 0, False, False)

         # 3. Units verletzen
         iSum = iMounted + iMelee
         if iSum > 0:

           iRange = loopPlot.getNumUnits()
           for iUnit in range(iRange):
             if iSum <= 0: break
             xUnit = loopPlot.getUnit(iUnit)
             if xUnit.getUnitCombatType() in lMounted:
               xDamage = xUnit.getDamage()
               if xDamage + 25 < 100:
                 xUnit.changeDamage(15,False)
                 if gc.getPlayer(xUnit.getOwner()).isHuman():
                   CyInterface().addMessage(xUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_PLOT",(xUnit.getName(),15)), None, 2, None, ColorTypes(12), loopPlot.getX(), loopPlot.getY(), True, True)
                 iSum -= 1
             elif xUnit.getUnitCombatType() in lMelee:
               xDamage = xUnit.getDamage()
               if xDamage + 30 < 100:
                 xUnit.changeDamage(20,False)
                 if gc.getPlayer(xUnit.getOwner()).isHuman():
                   CyInterface().addMessage(xUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_PLOT",(xUnit.getName(),20)), None, 2, None, ColorTypes(12), loopPlot.getX(), loopPlot.getY(), True, True)
                 iSum -= 1


     # +++++ Rebellious STACKs ---------------
     # Stack can become independent / rebellious
     # per Unit 0.5%, aber nur jede 3te Runde
     if len(PlotArrayRebellion) > 0 and iGameTurn % 3 == 0:

      bAtWar = False
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        if gc.getPlayer(i).isAlive() and not bAtWar:
          if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(i).getTeam()): bAtWar = True

      iPromoLeader = gc.getInfoTypeForString('PROMOTION_LEADER')
      iPromoHero = gc.getInfoTypeForString('PROMOTION_HERO')
# Loyale Einheiten sind dem Feldherren loyal gewesen!
#      iPromoLoyal = gc.getInfoTypeForString('PROMOTION_LOYALITAT')

      for h in PlotArrayRebellion:
        sPlot = gc.getMap().plot(h[0],h[1])
        iNumUnits = sPlot.getNumUnits()

        # (Inaktiv: 30 / 5 = 4. Daher ziehe ich 5 ab, damit es bei 1% beginnt)
        #iPercent = int(iNumUnits / 2)
        iPercent = 0

        # wenn Krieg ist -20%
        if bAtWar: iPercent -= 20

        # for each general who accompanies the stack: -10%
        iCombatSiege = gc.getInfoTypeForString('UNITCOMBAT_SIEGE')
        iCombatUnits = 0
        for i in range(iNumUnits):
          if sPlot.getUnit(i).getOwner() == iPlayer:
            if sPlot.getUnit(i).isMilitaryHappiness():
              if sPlot.getUnit(i).getUnitCombatType() != iCombatSiege:
                iCombatUnits += 1
            if sPlot.getUnit(i).isHasPromotion(iPromoLeader): iPercent -= 20
            if sPlot.getUnit(i).isHasPromotion(iPromoHero): iPercent -= 10

        if iCombatUnits >= iStackLimit2:
          # PAE better AI
          if pPlayer.isHuman(): iPercent += iCombatUnits
          else: iPercent += iCombatUnits / 2
        else:
          iPercent = -1

# Loyale Einheiten sind dem Feldherren loyal gewesen!
#          if sPlot.getUnit(i).isHasPromotion(iPromoLoyal): fPercent -= 0.1
        # auf eigenem Terrain -2, auf feindlichem +2, auf neutralem 0
        #if sPlot.getOwner() == iPlayer: iPercent -= 1
        #elif sPlot.getOwner() > -1: iPercent += 1

        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iPlayer",iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Units",iNumUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iPercent",iPercent)), None, 2, None, ColorTypes(10), 0, 0, False, False)


        if iPlayer > -1 and iPercent > 0:

         iRand = self.myRandom(100, None)
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iRand",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)

         # PAE IV Update: 1. Check
         if iRand < iPercent:
          # PAE IV Update: 2. Check: 25% Rebellion, 75% Meldung
          # PAE V: 2. Check: 20% Rebellion, 80% Meldung
          iRand = self.myRandom(5, None)
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("2.Check",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          # Rebellious stack
          if iRand == 1:

           #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("REBELLION",1)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(10), sPlot.getX(), sPlot.getY(), True, True)

           # Einen guenstigen Plot auswaehlen
           rebelPlotArray = []
           for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(sPlot.getX() + i - 1, sPlot.getY() + j - 1)
              if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                if loopPlot.isHills():
                  rebelPlotArray.append(loopPlot)

           if len(rebelPlotArray) == 0:
            for i in range(3):
              for j in range(3):
                loopPlot = gc.getMap().plot(sPlot.getX() + i - 1, sPlot.getY() + j - 1)
                if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                  if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()):
                    rebelPlotArray.append(loopPlot)

           # es kann rebelliert werden
           if len(rebelPlotArray) > 0:
            iRebelPlot = self.myRandom(len(rebelPlotArray), None)

            #Anzahl der rebellierenden Einheiten
            iNumRebels = self.myRandom(iNumUnits, None)
            if iNumRebels < 10: iNumRebels = 9

            # kleine Rebellion
            if iNumRebels * 2 < iNumUnits:
              text = CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_1",("Units",iNumUnits))
              if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 5, text, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)
              self.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())

            # grosse Rebellion (+ Generalseinheit)
            else:
              if pPlayer.isHuman():
                text = CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_2",("Units",iNumUnits))
                CyInterface().addMessage(iPlayer, True, 5, text, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)

              listNamesStandard = ["Adiantunnus","Divico","Albion","Malorix","Inguiomer","Archelaos","Dorimachos","Helenos","Kerkidas","Mikythos","Philopoimen","Pnytagoras","Sophainetos","Theopomopos","Gylippos","Proxenos","Theseus","Balakros","Bar Kochba","Julian ben Sabar","Justasas","Patricius","Schimon bar Giora","Artaphernes","Harpagos","Atropates","Bahram Chobin","Datis","Schahin","Egnatius","Curius Aentatus","Antiochos II","Spartacus","Herodes I","Calgacus","Suebonius Paulinus","Maxentus","Sapor II","Alatheus","Saphrax","Honorius","Aetius","Achilles","Herodes","Heros","Odysseus","Anytos"]
              iName = self.myRandom(len(listNamesStandard), None)

              iUnitType = gc.getInfoTypeForString("UNIT_GREAT_GENERAL")
              unit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitType, rebelPlotArray[iRebelPlot].getX(), rebelPlotArray[iRebelPlot].getY(), UnitAITypes.UNITAI_GENERAL, DirectionTypes.DIRECTION_SOUTH)
              unit.setName(listNamesStandard[iName])
              self.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())
              self.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())

            # PopUp
            if pPlayer.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(text)
              popupInfo.addPopup(iPlayer)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stack Rebellion (Zeile 2028)",iPlayer)), None, 2, None, ColorTypes(10), sPlot.getX(), sPlot.getY(), True, True)

            # Units become rebels
            for i in range(iNumRebels):
             # Zufallsunit, getnumunits muss jedesmal neu ausgerechnet werden, da ja die rebell. units auf diesem plot wegfallen
             iRand = self.myRandom(sPlot.getNumDefenders(iPlayer), None)
             #Unit kopieren

             if sPlot.getUnit(iRand).getOwner() == iPlayer:

              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(sPlot.getUnit(iRand).getUnitType(),  rebelPlotArray[iRebelPlot].getX(), rebelPlotArray[iRebelPlot].getY(), UnitAITypes(sPlot.getUnit(iRand).getUnitAIType()), DirectionTypes.DIRECTION_SOUTH)
              NewUnit.setExperience(sPlot.getUnit(iRand).getExperience(), -1)
              NewUnit.setLevel(sPlot.getUnit(iRand).getLevel())

              #if NewUnit.getName() != sPlot.getUnit(iRand).getName(): NewUnit.setName(sPlot.getUnit(iRand).getName())
              UnitName = sPlot.getUnit(iRand).getName()
              #if UnitName != "" and UnitName != NewUnit.getName(): NewUnit.setName(UnitName)
              if UnitName != gc.getUnitInfo(sPlot.getUnit(iRand).getUnitType()).getText():
                UnitName = re.sub(" \(.*?\)","",UnitName)
                NewUnit.setName(UnitName)

              NewUnit.setDamage(sPlot.getUnit(iRand).getDamage(), -1)
              # Check its promotions
              iRange = gc.getNumPromotionInfos()
              for j in range(iRange):
                if sPlot.getUnit(iRand).isHasPromotion(j):
                  NewUnit.setHasPromotion(j, True)
              # Original unit killen
              sPlot.getUnit(iRand).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

            # Meldung an den Spieler auf dem Territorium einer dritten Partei
            if sPlot.getOwner() > -1:
              if sPlot.getOwner() != iPlayer and gc.getPlayer(sPlot.getOwner()).isHuman():
                CyInterface().addMessage(sPlot.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_4",(gc.getPlayer(iPlayer).getCivilizationAdjective(1),)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebellisches Stack (Zeile 1557)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)



          # ne kleine Warnung ausschicken
          else:
           if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_0",("",)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)
           else:
            # AI kills a weak unit to prevent a rebellion
            #iST = seekUnit = seekST = 0
            #for i in range(iNumUnits):
            #  iST = sPlot.getUnit(i).baseCombatStr()
            #  if iST < seekST and iST > 0 or seekST == 0:
            #   seekUnit = i
            #   seekST = iST
            #sPlot.getUnit(seekUnit).kill(1,iPlayer)

            # AI teilt Stack (jede 4. Einheit)
            for i in range(iNumUnits):
              if i % 4 == 1 and sPlot.getUnit(i).getOwner() == iPlayer: sPlot.getUnit(i).jumpToNearestValidPlot()

            # Meldung an den Spieler auf dem Territorium einer dritten Partei
            if sPlot.getOwner() > -1:
              if sPlot.getOwner() != iPlayer and gc.getPlayer(sPlot.getOwner()).isHuman():
                CyInterface().addMessage(sPlot.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_3",(gc.getPlayer(iPlayer).getCivilizationAdjective(1),)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)


# +++++ Rebellious Stack -- end ---------------------------------------------



# +++++ AI Marodeure anpassen UNITAI_EXPLORE / UNITAI_PILLAGE / UNITAI_ATTACK
#    if iPlayer > -1:
#      if not gc.getPlayer(iPlayer).isHuman():
#        lUnits = PyPlayer(iPlayer).getUnitList()
#        for iUnits in range(len(lUnits)):
#          pUnit = gc.getPlayer(iPlayer).getUnit(lUnits[iUnits].getID())
#
#          if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_AXEMAN_MARODEUR") or pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SWORDSMAN_MARODEUR"):
#            xPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
#            # Im eigenen Land soll sie zuerst ausser Landes gebracht werden
#            if xPlot.getOwner() == pUnit.getOwner():
#              pUnit.setUnitAIType(UnitAITypes.UNITAI_EXPLORE) # UNITAI_EXPLORE
#            # Im feindlichen Land soll sie dann Pluendern / UNITAI_PIRATE_SEA geht nicht
#            elif xPlot.getOwner() > -1 and xPlot.getOwner() != gc.getBARBARIAN_PLAYER():
#              if xPlot.getImprovementType() > -1: pUnit.setUnitAIType(UnitAITypes.UNITAI_PILLAGE)
#              else: pUnit.setUnitAIType(UnitAITypes.UNITAI_ATTACK)


# +++++ Angesiedelte Sklaven -> Rebellen/Gladiatoren / Buerger / Gladiatoren / Reservistensterben ---
# Soll nur alle 4 Runden pruefen
    bRevolt = False
    if iGameTurn % 4 == 0 and iPlayer != gc.getBARBARIAN_PLAYER():
      pOwner = gc.getPlayer(iPlayer)
      lCities = PyPlayer(iPlayer).getCityList()

      iRangeCities = len(lCities)
      for iCity in range(iRangeCities):
        pCity = pOwner.getCity(lCities[iCity].getID())
        iCityPop = pCity.getPopulation()
        iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
        iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
        iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
        iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
        iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
        iCitySlaves2 = 0 # Unsettled Slaves in city

        iCityReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST


        # Wenn es Sklaven gibt = verschiedene Sterbensarten
        if iCitySlaves > 0 or iCityReservists > 0:

          # Sklaventyp aussuchen, aber es soll max. immer nur 1 Typ pro Stadt draufgehn
          iTyp = -1

          # Haussklave 4%
          if iCitySlavesHaus > 0:
            if self.myRandom(25, None) == 1: iTyp = 2
          # Feldsklave 5%
          if iCitySlavesFood > 0 and iTyp == -1:
            if self.myRandom(20, None) == 1: iTyp = 0
          # Bergwerkssklave 8%
          if iCitySlavesProd > 0 and iTyp == -1:
            if self.myRandom(13, None) == 1: iTyp = 1
          # Reservist 3%
          if iCityReservists > 0 and iTyp == -1:
            if self.myRandom(33, None) == 1: iTyp = 3

          # Reservisten
          if iTyp == 3:
            pCity.changeFreeSpecialistCount(19, -1)
            if pPlayer.isHuman():
               iRand = 1 + self.myRandom(9, None)
               CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DYING_RESERVIST_"+str(iRand),(pCity.getName(),"")),None,2,",Art/Interface/MainScreen/CityScreen/Great_Engineer.dds,Art/Interface/Buttons/Warlords_Atlas_2.dds,7,6",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

          # Sklaven
          elif iTyp != -1:

            # PAE V: stehende Sklaven werden zugewiesen
            bErsatz = False
            # City Plot
            pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
            iRangePlotUnits = pCityPlot.getNumUnits()
            for iUnit in range (iRangePlotUnits):
              if pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                 #pCityPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                 pCityPlot.getUnit(iUnit).kill(1,pCityPlot.getUnit(iUnit).getOwner())
                 bErsatz = True
                 break

            # Feldsklaven
            if iTyp == 0:
              if not bErsatz:
                pCity.changeFreeSpecialistCount(17, -1)
                iCitySlavesFood -= 1
              if pPlayer.isHuman():
                iRand = 1 + self.myRandom(16, None)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_FELD_"+str(iRand),(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

            # Bergwerkssklaven
            elif iTyp == 1:
              if not bErsatz:
                pCity.changeFreeSpecialistCount(18, -1)
                iCitySlavesProd -= 1
              if pPlayer.isHuman():
                iRand = 1 + self.myRandom(20, None)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_MINE_"+str(iRand),(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

            # Haussklaven
            elif iTyp == 2:
              if not bErsatz:
                pCity.changeFreeSpecialistCount(16, -1)
                iCitySlavesHaus -= 1
              if pPlayer.isHuman():
                iRand = 1 + self.myRandom(14, None)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_HAUS_"+str(iRand),(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

            if bErsatz:
              if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_ERSATZ",("",)),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
            else:
              # Gesamtsumme aendern
              iCitySlaves -= 1



        # Wenns mehr Sklaven als Einwohner gibt = Revolte
        if iCitySlaves + iCityGlads > iCityPop:
          # City Plot
          pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())

          # Calc factor
          iChance = (iCitySlaves + iCityGlads - iCityPop) * 10
          iChance2 = iChance
          # Alt:
          #iChance  = (iCitySlaves - iCityPop) * 10
          #iChance2 = (iCityGlads - iCityPop) * 10
          # rebel bonus when unhappy
          if pCity.happyLevel() < pCity.unhappyLevel(0):
            iChance  += 25
            iChance2 += 25
          # Units that prevent a revolt
          iPromoHero = gc.getInfoTypeForString('PROMOTION_HERO')
          iRangePlotUnits = pCityPlot.getNumUnits()
          for iUnit in range (iRangePlotUnits):
            if pCityPlot.getUnit(iUnit).isHasPromotion(iPromoHero):
              iChance  -= 25
              iChance2 -= 25
            elif pCityPlot.getUnit(iUnit).isMilitaryHappiness():
              iChance  -= 2
              iChance2 -= 2
            elif pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
              iCitySlaves2 += 1
              iChance  += 2
              iChance2 += 2
          # Buildings that prevent a revolt
          iBuilding = gc.getInfoTypeForString('BUILDING_COLOSSEUM')
          if pCity.isHasBuilding(iBuilding):
              iChance  -= 5
              iChance2 -= 5
          iBuilding = gc.getInfoTypeForString('BUILDING_BYZANTINE_HIPPODROME')
          if pCity.isHasBuilding(iBuilding):
              iChance  -= 5
              iChance2 -= 5
          # Civics that promotes/prevents a revolt
          if pOwner.isCivic(14):
              iChance  += 5
              iChance2 += 5
          if pOwner.isCivic(15):
              iChance  += 5
              iChance2 += 5
          if pOwner.isCivic(16) or pOwner.isCivic(17):
              iChance  -= 5
              iChance2 -= 5


          # SLAVE REVOLT (SKLAVENAUFSTAND)
          if iCitySlaves > iCityGlads and iCitySlaves > 0 and iChance > 0:
            iRand = self.myRandom(100, None)

#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GROWTH",("CHANCE",iChance)), None, 2, None, ColorTypes(12), 0, 0, False, False)
#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GROWTH",("RAND",iRand)), None, 2, None, ColorTypes(12), 0, 0, False, False)

            # Lets rebell
            if iRand < iChance:
              if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_REVOLTSTART')

              # Einen guenstigen Plot auswaehlen
              rebelPlotArray = []
              for i in range(3):
                for j in range(3):
                  loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                  if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                    if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                      rebelPlotArray.append(loopPlot)

              if len(rebelPlotArray) == 0:
                for i in range(3):
                  for j in range(3):
                    loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                    if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                      if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()) and loopPlot.getOwner() == iPlayer:
                        rebelPlotArray.append(loopPlot)

              # es kann rebelliert werden
              if len(rebelPlotArray) > 0:
                # pruefen ob es einen Vorbesitzer fuer diese Stadt gibt
                iPreviousOwner = pCity.findHighestCulture()
                if iPlayer != iPreviousOwner and iPreviousOwner != -1:
                  if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isAtWar(gc.getPlayer(iPreviousOwner).getTeam()): barbPlayer = gc.getPlayer(iPreviousOwner)
                  else: barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                else: barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())

                # Settled slaves
                iNumRebels = self.myRandom(iCitySlaves, None) + 1
                iNumRebTmp = iNumRebels
                # Zuerst Feldsklaven
                if iNumRebTmp >= iCitySlavesFood:
                  pCity.setFreeSpecialistCount(17,0)
                  iNumRebTmp -= iCitySlavesFood
                else:
                  pCity.changeFreeSpecialistCount(17, iNumRebTmp * (-1))
                  iNumRebTmp = 0
                # Dann Bergwerkssklaven
                if iNumRebTmp >= iCitySlavesProd and iNumRebTmp > 0:
                  pCity.setFreeSpecialistCount(18,0)
                  iNumRebTmp -= iCitySlavesProd
                else:
                  pCity.changeFreeSpecialistCount(18, iNumRebTmp * (-1))
                  iNumRebTmp = 0
                # Der Rest Haussklaven
                if iNumRebTmp >= iCitySlavesHaus and iNumRebTmp > 0:
                  pCity.setFreeSpecialistCount(16,0)
                  iNumRebTmp -= iCitySlavesHaus
                else:
                  pCity.changeFreeSpecialistCount(16, iNumRebTmp * (-1))
                  iNumRebTmp = 0

                # Unsettled slaves
                iNumRebels2 = 0
                if iCitySlaves2 > 0:
                  iNumRebels2 = self.myRandom(iCitySlaves2, None) + 1
                  iUnit=0
                  iDone=0
                  iRangePlotUnits = pCityPlot.getNumUnits()
                  for iUnit in range (iRangePlotUnits):
                    if iDone < iNumRebels2 and pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                      #pCityPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                      pCityPlot.getUnit(iUnit).kill(1,pCityPlot.getUnit(iUnit).getOwner())
                      iDone = iDone + 1

                iNumRebels += iNumRebels2

                iUnitType = gc.getInfoTypeForString("UNIT_REBELL")

                for i in range(iNumRebels):
                  iPlot = self.myRandom(len(rebelPlotArray), None)
                  NewUnit = barbPlayer.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                  NewUnit.setImmobileTimer(1)
                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebell erstellt (Zeile 1116)",iNumRebels)), None, 2, None, ColorTypes(10), 0, 0, False, False)



                # City Revolt
                #pCity.setOccupationTimer(iNumRebels+1)
                # City Defender damage
                bRevolt = True
                self.doCityRevolt (pCity,iNumRebels+1)

                iRangeMaxPlayers = gc.getMAX_PLAYERS()
                for iAllPlayer in range (iRangeMaxPlayers):
                  ThisPlayer = gc.getPlayer(iAllPlayer)
                  iThisPlayer = ThisPlayer.getID()
                  iThisTeam = ThisPlayer.getTeam()
                  ThisTeam = gc.getTeam(iThisTeam)
                  if ThisTeam.isHasMet(pOwner.getTeam()) and ThisPlayer.isHuman():
                    if iThisPlayer == iPlayer: iColor = 7
                    else: iColor = 10
                    if iNumRebels == 1:
                      CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT_ONE",(pCity.getName(),pOwner.getCivilizationAdjective(1),iNumRebels)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)
                    else:
                      CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT",(pCity.getName(),pOwner.getCivilizationAdjective(1),iNumRebels)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)

            # KI soll Stadtsklaven freistellen 1:4
            else:
              if not gc.getPlayer(iPlayer).isHuman():
                if 1 == self.myRandom(4, None):
                  self.doAIReleaseSlaves(pCity)


          # GLADIATOR REVOLT (GLADIATORENAUFSTAND)
          if not bRevolt and iCityGlads > 0 and iChance2 > 0:
            iRand = self.myRandom(100, None)

            # Lets rebell
            if iRand < iChance2:
              if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_REVOLTSTART')

              # Einen guenstigen Plot auswaehlen
              rebelPlotArray = []
              for i in range(3):
                for j in range(3):
                  loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                  if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                    if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                      rebelPlotArray.append(loopPlot)

              if len(rebelPlotArray) == 0:
                for i in range(3):
                  for j in range(3):
                    loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                    if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                      if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()) and loopPlot.getOwner() == iPlayer:
                        rebelPlotArray.append(loopPlot)

              # es kann rebelliert werden
              if len(rebelPlotArray) > 0:
                # pruefen ob es einen Vorbesitzer fuer diese Stadt gibt
                iPreviousOwner = pCity.findHighestCulture()
                if iPlayer != iPreviousOwner:
                  if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isAtWar(gc.getPlayer(iPreviousOwner).getTeam()): barbPlayer = gc.getPlayer(iPreviousOwner)
                  else: barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                else: barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                # Settled gladiators
                iNumRebels = self.myRandom(iCityGlads, None)
                if iNumRebels == 0: iNumRebels = 1
                pCity.changeFreeSpecialistCount(15, iNumRebels * (-1))
                # Unsettled slaves
                iNumRebels2 = 0
                if iCitySlaves2 > 0:
                  iNumRebels2 = self.myRandom(iCitySlaves2, None)
                  if iNumRebels2 == 0: iNumRebels2 = 1
                  iUnit=iDone=0
                  iRangePlotUnits = pCityPlot.getNumUnits()
                  for iUnit in range (iRangePlotUnits):
                    if iDone < iNumRebels2 and pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                      #pCityPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                      pCityPlot.getUnit(iUnit).kill(1,pCityPlot.getUnit(iUnit).getOwner())
                      iDone = iDone + 1

                iNumRebels = iNumRebels + iNumRebels2

                iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")

                for i in range(iNumRebels):
                  iPlot = self.myRandom(len(rebelPlotArray), None)
                  barbPlayer.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiatorenaufstand (Zeile 1188)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)



                # City Revolt
                self.doCityRevolt (pCity,iNumRebels+1)
                bRevolt = True

                iRangeMaxPlayers = gc.getMAX_PLAYERS()
                for iAllPlayer in range (iRangeMaxPlayers):
                  ThisPlayer = gc.getPlayer(iAllPlayer)
                  iThisPlayer = ThisPlayer.getID()
                  iThisTeam = ThisPlayer.getTeam()
                  ThisTeam = gc.getTeam(iThisTeam)
                  if ThisTeam.isHasMet(pOwner.getTeam()) and ThisPlayer.isHuman():
                    if iThisPlayer == iPlayer: iColor = 7
                    else: iColor = 10
                    if iNumRebels == 1:
                      CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT_ONE",(pCity.getName(),pOwner.getCivilizationAdjective(1),iNumRebels)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/General/button_alert_new.dds",ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)
                    else:
                      CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT",(pCity.getName(),pOwner.getCivilizationAdjective(1),iNumRebels)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/General/button_alert_new.dds",ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)

          # Sklaven oder Gladiatoren: sobald das Christentum entdeckt wurde -> 2% per 3 turn revolt
          iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
          if not bRevolt and gc.getGame().isReligionFounded(iReligion):
           if pOwner.getStateReligion() != iReligion:
            iRand = self.myRandom(50, None)
            if iRand == 0:
              # City Revolt
              #pCity.setOccupationTimer(4)
              # City Plot
              pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
              # City Defender damage
              self.doCityRevolt (pCity,4)
              bRevolt = True
              # Message to players
              iRangeMaxPlayers = gc.getMAX_PLAYERS()
              for iAllPlayer in range (iRangeMaxPlayers):
                ThisPlayer = gc.getPlayer(iAllPlayer)
                iThisPlayer = ThisPlayer.getID()
                iThisTeam = ThisPlayer.getTeam()
                ThisTeam = gc.getTeam(iThisTeam)
                if ThisTeam.isHasMet(pOwner.getTeam()) and ThisPlayer.isHuman():
                  if iThisPlayer == iPlayer: iColor = 7
                  else: iColor = 10
                  CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS",(pCity.getName(),pOwner.getCivilizationAdjective(1))),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_kreuz.dds",ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)

              # 1 settled Slave (Slave or gladiator) gets killed
              bChristSlaves = bChristGlads = False
              if iCitySlaves > 0 and iCityGlads > 0:
                iRand = self.myRandom(2, None)
                if iRand == 0: bChristSlaves = True
                else: bChristGlads = True
              elif iCitySlaves > 0: bChristSlaves = True
              elif  iCityGlads > 0: bChristGlads  = True

              if bChristSlaves == True:
                if iCitySlavesHaus > 0 and iCitySlavesFood > 0 and iCitySlavesProd > 0:
                  iRand = self.myRandom(3, None)
                  if iRand == 1: pCity.changeFreeSpecialistCount(17, -1)
                  elif iRand == 2: pCity.changeFreeSpecialistCount(18, -1)
                  else: pCity.changeFreeSpecialistCount(16, -1)
                elif iCitySlavesHaus > 0 and iCitySlavesFood > 0:
                  iRand = self.myRandom(2, None)
                  if iRand == 1: pCity.changeFreeSpecialistCount(17, -1)
                  else: pCity.changeFreeSpecialistCount(16, -1)
                elif iCitySlavesHaus > 0 and iCitySlavesProd > 0:
                  iRand = self.myRandom(2, None)
                  if iRand == 1: pCity.changeFreeSpecialistCount(18, -1)
                  else: pCity.changeFreeSpecialistCount(16, -1)
                elif iCitySlavesFood > 0 and iCitySlavesProd > 0:
                  iRand = self.myRandom(2, None)
                  if iRand == 1: pCity.changeFreeSpecialistCount(17, -1)
                  else: pCity.changeFreeSpecialistCount(18, -1)
                elif iCitySlavesFood > 0: pCity.changeFreeSpecialistCount(17, -1)
                elif iCitySlavesProd > 0: pCity.changeFreeSpecialistCount(18, -1)
                else: pCity.changeFreeSpecialistCount(16, -1)

                if pOwner.isHuman():
                  CyInterface().addMessage(pOwner.getID(), True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS_1_SLAVE",(pCity.getName(), )),None,2,"Art/Interface/Buttons/Actions/button_kreuz.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
              elif bChristGlads == True:
                pCity.changeFreeSpecialistCount(15, -1)
                if pOwner.isHuman():
                  CyInterface().addMessage(pOwner.getID(), True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS_1_GLAD",(pCity.getName(), )),None,2,"Art/Interface/Buttons/Actions/button_kreuz.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

        # Christentum kommt in die Stadt 5%
        if iCitySlaves > 0 and not bRevolt:
          iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
          if gc.getGame().isReligionFounded(iReligion):
            iRand = self.myRandom(20, None)
            if iRand == 1:
              if not pCity.isHasReligion(iReligion):
                if pOwner.isHuman():
                  CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_SLAVES_SPREAD_CHRISTIANITY",(pCity.getName(), )),None,2,"Art/Interface/Buttons/Actions/button_kreuz.dds",ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
                pCity.setHasReligion(iReligion,1,1,0)


      # Ende Cities ----------------------------------------------------------


      # Stehende Sklaven / unsettled slaves
      if iPlayer > -1 and iPlayer != gc.getBARBARIAN_PLAYER():
        lSlaves = []
        lUnits = PyPlayer(iPlayer).getUnitList()
        iRangePlayerUnits = len(lUnits)
        for iUnits in range(iRangePlayerUnits):
          pUnit = gc.getPlayer(iPlayer).getUnit(lUnits[iUnits].getID())
          # and not pUnit.isCargo()
          if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE") and pUnit.getMoves() > 0:
            lSlaves.append(pUnit)

        iSlave = 0
        while iSlave < len(lSlaves):
          pUnit = lSlaves[iSlave]
          iSlave += 1

          # Nicht auf Hoher See (als Cargo von Schiffen) , Kueste schon
          xPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
          if xPlot.getTerrainType() != gc.getInfoTypeForString("TERRAIN_OCEAN"):

            iChance = 8
            # Civic that increase rebelling
            if gc.getPlayer(iPlayer).isCivic(17): iChance += 4
            # Military units decrease odds
            if xPlot.getNumDefenders(pUnit.getOwner()) > 0: iChance -= 4

            if iChance > self.myRandom(100, None):

              # wenn das Christentum gegruendet wurde / if christianity was found
              # Christ : Rebell = 1 : 4
              bSlave2Christ = False
              iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
              if gc.getGame().isReligionFounded(iReligion):
                iRand = self.myRandom(4, None)
                if iRand == 1: bSlave2Christ = True

              if bSlave2Christ == True:
                iUnitType = gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY")
                gc.getPlayer(iPlayer).initUnit(iUnitType, pUnit.getX(), pUnit.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
                if gc.getPlayer(iPlayer).isHuman():
                  CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_2_CHRIST",(0,)), None, 2, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(14), pUnit.getX(), pUnit.getY(), True, True)
                #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                pUnit.kill(1,pUnit.getOwner())

               # ***TEST***
               #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Christ. Missionar (Zeile 1275)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


              else:

                # Ein Sklave auf fremden Terrain kann nicht rebellieren sondern verschwindet oder macht einen Fluchtversuch 50:50
                if xPlot.getOwner() != pUnit.getOwner():
                  if pOwner.isHuman():
                    iRand = 1 + self.myRandom(4, None)
                    CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_LOST_"+str(iRand),(0,"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
                  # Barbareneinheit erschaffen
                  if 1 == self.myRandom(2, None):
                    # Einen guenstigen Plot auswaehlen
                    rebelPlotArray = []
                    for i in range(3):
                      for j in range(3):
                        loopPlot = gc.getMap().plot(pUnit.getX() + i - 1, pUnit.getY() + j - 1)
                        if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                          if not loopPlot.isImpassable() and not loopPlot.isWater() and not loopPlot.isPeak():
                            rebelPlotArray.append(loopPlot)
                    if len(rebelPlotArray) > 0:
                      iPlot = self.myRandom(len(rebelPlotArray), None)
                      iUnitType = gc.getInfoTypeForString("UNIT_SLAVE")
                      NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                  #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                  pUnit.kill(1,pUnit.getOwner())

                  # ***TEST***
                  #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave lost in enemy territory (Zeile 1297)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                else:

                  # Einen guenstigen Plot auswaehlen
                  rebelPlotArray = []
                  for i in range(3):
                    for j in range(3):
                      loopPlot = gc.getMap().plot(pUnit.getX() + i - 1, pUnit.getY() + j - 1)
                      if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                        if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                          rebelPlotArray.append(loopPlot)

                  if len(rebelPlotArray) == 0:
                    for i in range(3):
                      for j in range(3):
                        loopPlot = gc.getMap().plot(pUnit.getX() + i - 1, pUnit.getY() + j - 1)
                        if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                            if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()) and loopPlot.getOwner() == iPlayer:
                              rebelPlotArray.append(loopPlot)

                  # es kann rebelliert werden
                  if len(rebelPlotArray) > 0:
                    iPlot = self.myRandom(len(rebelPlotArray), None)
                    iUnitType = gc.getInfoTypeForString("UNIT_REBELL")
                    NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    if pOwner.isHuman():
                      CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_2_REBELL",(0,)), None, 2, "Art/Interface/Buttons/Units/button_rebell.dds", ColorTypes(7), rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), True, True)
                    #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                    pUnit.kill(1,pUnit.getOwner())
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Rebell (Zeile 1327)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Sklaven und Gladiatoren (REBELLEN) Ende ------------------------------------------------

# -- Missionare fuer verwandte CIVs ---------------------------

# -- Nordischer Missionar fuer Germanen/Vandalen
#    if gc.getGame().getGameTurnYear() == -2250:
#      Civ = gc.getInfoTypeForString("CIVILIZATION_GERMANEN")
#      iRel = gc.getInfoTypeForString("RELIGION_NORDIC")
#      #if gc.getGame().isReligionFounded(iRel):
#      if pPlayer.getCivilizationType() == Civ and pPlayer.getStateReligion() != iRel:
#
#        lCities = PyPlayer(iPlayer).getCityList()
#        pCity = pPlayer.getCity(lCities[0].getID())
#
#        iUnitType = gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY")
#        pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
#
#        if (pPlayer.isHuman()):
#          popupInfo = CyPopupInfo()
#          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
#          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_GALLIEN_MISSIONAR",("", )))
#          popupInfo.addPopup(iPlayer)

# -- Griechischer Missionar fuer Rom
    if gc.getGame().getGameTurnYear() == -1000:
      iRel = gc.getInfoTypeForString("RELIGION_GREEK")
      if gc.getGame().isReligionFounded(iRel):
        if pPlayer.getStateReligion() != iRel:
          CivArray = []
          CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ROME"))
          if pPlayer.getCivilizationType() in CivArray:

            lCities = PyPlayer(iPlayer).getCityList()
            pCity = pPlayer.getCity(lCities[0].getID())

            iUnitType = gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY")
            pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)

            if (pPlayer.isHuman()):
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_ROM_MISSIONAR",("", )))
              popupInfo.addPopup(iPlayer)

# -- Aegyptischer Missionar fuer Nubien
#    if gc.getGame().getGameTurnYear() == -3000:
#      Civ = gc.getInfoTypeForString("CIVILIZATION_NUBIA")
#      iRel = gc.getInfoTypeForString("RELIGION_EGYPT")
#      #if gc.getGame().isReligionFounded(iRel):
#      if pPlayer.getCivilizationType() == Civ and pPlayer.getStateReligion() != iRel:
#
#        lCities = PyPlayer(iPlayer).getCityList()
#        pCity = pPlayer.getCity(lCities[0].getID())
#
#        iUnitType = gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY")
#        pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
#
#        if (pPlayer.isHuman()):
#          popupInfo = CyPopupInfo()
#          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
#          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_EGYPT_MISSIONAR",("", )))
#          popupInfo.addPopup(iPlayer)

# ------------------------------------------


    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pPlayer.getName(),pPlayer.getAnarchyTurns())), None, 2, None, ColorTypes(10), 0, 0, False, False)


# ------ Anarchie wenn mehr als die Haelfte der Staedte revoltieren oder von der Pest heimgesucht werden - 33 %
    if pPlayer.getAnarchyTurns() <= 0:
      iRand = self.myRandom(3, None)
      if iRand == 1:
        iBuilding = gc.getInfoTypeForString("BUILDING_PLAGUE")
        iNumCities = pPlayer.getNumCities()
        iCityPlague = 0
        iCityRevolt = 0
        if iNumCities > 0:
          for i in range (iNumCities):
            if pPlayer.getCity(i).isHasBuilding(iBuilding): iCityPlague += 1
            if pPlayer.getCity(i).getOccupationTimer() > 0: iCityRevolt += 1

          if iNumCities <= iCityRevolt * 2:
            pPlayer.changeAnarchyTurns(iCityRevolt)
            if pPlayer.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_PLAYER_ANARCHY_FROM_REVOLTS",("", )))
              popupInfo.addPopup(iPlayer)

          elif iNumCities <= iCityPlague * 2:
            pPlayer.changeAnarchyTurns(iCityPlague)
            if pPlayer.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_PLAYER_ANARCHY_FROM_PLAGUE",("", )))
              popupInfo.addPopup(iPlayer)


# +++++ HI-Hegemon TECH Vasallenfeature (Chance 33% every 5th round) / Vassal Tech
    if iGameTurn % 5 == 0:
     if pPlayer != None:
      if pPlayer.isHuman():
       iTech = gc.getInfoTypeForString("TECH_VASALLENTUM")
       iTeam = pPlayer.getTeam()
       pTeam = gc.getTeam(iTeam)
       if pTeam.isHasTech(iTech):

        # Vasallen finden
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
         vPlayer = gc.getPlayer(i)
         iVassal = gc.getPlayer(i).getID()
         if vPlayer.isAlive():
          iTeam = vPlayer.getTeam()
          vTeam = gc.getTeam(iTeam)
          if vTeam.isVassal(pTeam.getID()):
            TechArray = []
            if self.myRandom(3, None) == 1:
              # Tech raussuchen, die der Vasall nicht hat
              iTechNum = gc.getNumTechInfos()
              for j in range(iTechNum):
                if pTeam.isHasTech(j) and not vTeam.isHasTech(j):
                 if gc.getTechInfo(j) != None:
                  if gc.getTechInfo(j).isTrade(): TechArray.append(j)

            if len(TechArray) > 0:
              iTechRand = self.myRandom(len(TechArray), None)
              iTech = TechArray[iTechRand]
              # the more CIVs do have this tech, the cheaper
              iFaktor = gc.getGame().countKnownTechNumTeams(iTech)
              if iFaktor < 6: iFaktor = 5
              iTechCost = gc.getTechInfo(iTech).getResearchCost() / iFaktor
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH",(vPlayer.getName(),vPlayer.getCivilizationShortDescription(0),gc.getTechInfo(iTech).getDescription(),iTechCost )) )
              popupInfo.setData1(iPlayer)
              popupInfo.setData2(iVassal)
              popupInfo.setData3(iTech)
              popupInfo.setFlags(iTechCost)
              popupInfo.setOnClickedPythonCallback("popupVassalTech") # EntryPoints/CvScreenInterface und CvGameUtils / 702
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_YES",("",)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_MONEY",(iTechCost,iTechCost)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_NO",("",)), "")
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
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    # +++++ Scenario: FirstPunicWar - Start
    if sScenarioScriptData == "FirstPunicWar":
      # Runde 1: In der ersten Runde soll sich Messana an Rom als Vasall anbieten
      if iGameTurn == 0:
        iCivRome = 0
        iCivCarthage = 1
        iCivMessana = 4
        iCivSyrakus = 12
        if iPlayer == iCivMessana:

          iTeamRome = gc.getPlayer(iCivRome).getTeam()
          iTeamMessana = gc.getPlayer(iCivMessana).getTeam()
          pTeamMessana = gc.getTeam(iTeamMessana)
          if not pTeamMessana.isVassal(iTeamRome):

            iTeamRome = gc.getPlayer(iCivRome).getTeam()
            gc.getTeam(iTeamRome).assignVassal (iTeamMessana, 0) # Vassal, but no surrender

            # Meldungen an die Spieler
            iRange = gc.getMAX_PLAYERS()
            for i in range (iRange):
              ThisPlayer = gc.getPlayer(i)
              iThisPlayer = ThisPlayer.getID()
              if ThisPlayer.isHuman():
                # Meldung Karthago Human
                if iThisPlayer == iCivCarthage:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_CARTHAGE",("",)))
                  popupInfo.addPopup(iThisPlayer)
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_CARTHAGE",("",)))
                  popupInfo.addPopup(iThisPlayer)
                elif iThisPlayer == iCivRome:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_ALL",("",)))
                  popupInfo.addPopup(iThisPlayer)
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_ROME",("",)))
                  popupInfo.addPopup(iThisPlayer)
                # Meldung an alle Humans
                else:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_ALL",("",)))
                  popupInfo.addPopup(iThisPlayer)
    # +++++ Scenario: FirstPunicWar - End
    # +++++ Scenario: PeloponnesianWarKeinpferd - Start
    elif sScenarioScriptData == "PeloponnesianWarKeinpferd":
      # Runde 1: In Runde 5 soll das mit Korkyra im Krieg liegende Epidamnos Vasall von Korinth werden
      if iGameTurn == 5:
        iCivKorinth = 2
        iCivKorkyra = 6
        iCivEpidamnos = 7
        iCivSparta = 1
        if iPlayer == iCivEpidamnos:

          iTeamKorinth = gc.getPlayer(iCivKorinth).getTeam()
          iTeamEpidamnos = gc.getPlayer(iCivEpidamnos).getTeam()
          pTeamEpidamnos = gc.getTeam(iTeamEpidamnos)
          if not pTeamEpidamnos.isVassal(iTeamKorinth):

            iTeamKorinth = gc.getPlayer(iCivKorinth).getTeam()
            gc.getTeam(iTeamKorinth).assignVassal (iTeamEpidamnos, 0) # Vassal, but no surrender

            # Meldungen an die Spieler
            iRange = gc.getMAX_PLAYERS()
            for i in range (iRange):
              ThisPlayer = gc.getPlayer(i)
              iThisPlayer = ThisPlayer.getID()
              if ThisPlayer.isHuman():
                # Meldung Korkyra Human
                if iThisPlayer == iCivKorkyra:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_KERKYRA",("",)))
                  popupInfo.addPopup(iThisPlayer)
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_KORKYRA",("",)))
                  popupInfo.addPopup(iThisPlayer)
                elif iThisPlayer == iCivKorinth:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_ALL",("",)))
                  popupInfo.addPopup(iThisPlayer)
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_KORINTH",("",)))
                  popupInfo.addPopup(iThisPlayer)
                # Meldung an alle Humans
                else:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_ALL",("",)))
                  popupInfo.addPopup(iThisPlayer)
    # +++++ Scenario: PeloponnesianWarKeinpferd - End


# +++++ MAP Reveal to black fog - Kriegsnebel - Fog of War (FoW) - Karte schwarz zurueckfaerben
# AI auch, aber nur alle iPlayer-Runden
# AI wird wieder reingenommen -> wenn nur alle x Runden wahrscheinlich weniger Einheitenbewegung! -> no MAFs
    if pPlayer != None:
      # Human oder KI alle 5 Runden, aber abwechslende Civs pro Runde fuer optimale Rundenzeiten
      if iPlayer > -1 and (pPlayer.isHuman() or iGameTurn % 5 == iPlayer % 5):

        MapH = CyMap().getGridHeight()
        MapW = CyMap().getGridWidth()

        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)

        bDontGoBlackAnymore = False
        bShowCoasts = False
        bShowPeaksAndRivers = False
        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTOGRAPHIE2")): # Strassenkarten
          bDontGoBlackAnymore = True
        elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTEN")): # Karte zeichnen
          bShowCoasts = True
          bShowPeaksAndRivers = True
        elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTOGRAPHIE")): # Kartographie: Erste Karten
          bShowCoasts = True

        if not bDontGoBlackAnymore:

          #improv1 = gc.getInfoTypeForString("IMPROVEMENT_FORT")
          #improv2 = gc.getInfoTypeForString("IMPROVEMENT_FORT2")

          for i in range (MapW):
            for j in range (MapH):
              pPlot = CyMap().plot(i, j)

              if not pPlot.isVisible (iTeam, 0):
                bGoBlack = True

                # fully black or standard fog of war
                if pPlot.isCity():
                  pCity = pPlot.getPlotCity()
                  if bShowCoasts and pCity.isCapital(): bGoBlack = False
                  elif pCity.getNumWorldWonders() > 0: bGoBlack = False

                # Holy Mountain Quest
                if bGoBlack:
                  if pPlot.getScriptData() == "X": bGoBlack = False

                # Improvements (to normal fog of war)
                #if bGoBlack:
                #  if pPlot.getImprovementType() == improv1 or pPlot.getImprovementType() == improv2: bGoBlack = False

                # 50% Chance Verdunkelung
                if bGoBlack:
                  if self.myRandom(2, None) == 0: bGoBlack = False

                # Black fog
                if bGoBlack:
                  if pPlot.isRevealed (iTeam, 0):
                    # River and coast (land only)
                    #if pPlot.isRevealed (iTeam, 0) and not (pPlot.isRiverSide() or pPlot.isCoastalLand()): pPlot.setRevealed (iTeam,0,0,-1)
                    # River and coast (land and water)
                    #if pPlot.isRevealed (iTeam, 0) and not (pPlot.isRiverSide() or pPlot.isCoastalLand() or (pPlot.isAdjacentToLand() and pPlot.isWater())): pPlot.setRevealed (iTeam,0,0,-1)
                    if bShowCoasts:
                      if pPlot.isCoastalLand() or pPlot.isAdjacentToLand() and pPlot.isWater(): continue
                    if bShowPeaksAndRivers:
                      if pPlot.isRiverSide() or pPlot.isPeak(): continue
                    pPlot.setRevealed (iTeam,0,0,-1)




# Globale Ereignisse pro x-Runden
    if iPlayer == gc.getBARBARIAN_PLAYER():

##### Goody-Doerfer erstellen (goody-huts / GoodyHuts / Goodies / Villages) ####
# PAE V: Treibgut erstellen

     if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS):
      if not gc.getGame().isGameMultiPlayer():
       if iGameTurn % 20 == 0 and iGameTurn > 0:

        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()
        iNumSetGoodies = 0
        iNumSetFlotsam = 0

        impGoody = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
        # Treibgut spaeter wenn jeder Schiffe hat, die auf Ozean fahren koennen (Bireme)
        iUnit = gc.getInfoTypeForString("UNIT_TREIBGUT")
        iTech = gc.getInfoTypeForString("TECH_RUDERER2")
        if gc.getTeam(pPlayer.getTeam()).isHasTech(iTech): bFlot = True
        else: bFlot = False

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
        iMapSize = gc.getMap().getWorldSize()
        if iMapSize == 0: iMaxHuts = 3
        elif iMapSize == 1: iMaxHuts = 6
        elif iMapSize == 2: iMaxHuts = 9
        elif iMapSize == 3: iMaxHuts = 12
        elif iMapSize == 4: iMaxHuts = 15
        elif iMapSize == 5: iMaxHuts = 18
        else: iMaxHuts = 20

        iMaxFlot = iMaxHuts / 2

        # Bis zu iNumTries soll versucht werden, ein Dorf zu erstellen
        # alt: iMaxHuts * 2
        iNumTries = iMaxHuts
        for i in range(iNumTries):
         iX = self.myRandom(iMapW, None)
         iY = self.myRandom(iMapH, None)

         if iNumSetGoodies == iMaxHuts: break

         # Terrain checken
         loopPlot = gc.getMap().plot(iX, iY)
         if loopPlot != None and not loopPlot.isNone():
          #Veschachtelte ifs fuer bessere Rundenzeit
          if loopPlot.getFeatureType() == iDarkIce: continue
          if loopPlot.getImprovementType() == -1:
           if loopPlot.getNumUnits() == 0:
            if not loopPlot.isActiveVisible(0):
             if not loopPlot.isWater():
              if not loopPlot.isPeak():
               if loopPlot.getOwner() == -1 or loopPlot.getOwner() == iPlayer:
                bSet = True

                # Im Umkreis von 3 Feldern soll kein weiteres Goody sein
                for x in range(7):
                  for y in range(7):
                    loopPlot2 = gc.getMap().plot(iX + x - 3, iY + y - 3)
                    if loopPlot2 != None and not loopPlot2.isNone():
                      if loopPlot2.isGoody():
                        bSet = False
                        break
                  if not bSet: break

                # Goody setzen
                if bSet:
                  iNumSetGoodies += 1
                  loopPlot.setImprovementType(impGoody)
                  #loopPlot.isActiveVisible(0)

                  # ***TEST***
                  #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Goodydorf gesetzt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


             # isWater
             elif bFlot:
               if loopPlot.getOwner() == -1:
                 if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_OCEAN"):
                   if iNumSetFlotsam < iMaxFlot:
                     # Treibgut setzen
                     pPlayer.initUnit(iUnit, loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                     iNumSetFlotsam += 1

     # --------- Strandgut -----------
     # -- PAE V: Treibgut -> Strandgut
     iTreibgut = gc.getInfoTypeForString("UNIT_TREIBGUT")
     iStrandgut = gc.getInfoTypeForString("UNIT_STRANDGUT")
     iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
     iNumUnits = pPlayer.getNumUnits()
     for u in range(iNumUnits):
       loopUnit = pPlayer.getUnit(u)
       if loopUnit.getUnitType() == iTreibgut:
         pPlot = loopUnit.plot()
         if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_COAST"):

           lPlots = []
           for i in range(3):
             for j in range(3):
               loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 1)
               if loopPlot == None or loopPlot.isNone(): continue
               if loopPlot.isPeak() or loopPlot.isUnit() or loopPlot.getFeatureType() == iDarkIce: continue
               lPlots.append(loopPlot)

           if len(lPlots) > 0:
             iPlot = self.myRandom(len(lPlots), None)
             # Create Strandgut
             pPlayer.initUnit(iStrandgut, lPlots[iPlot].getX(), lPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             # Disband Treibgut
             pPlayer.getUnit(u).kill(1,iPlayer)
     # --------- Strandgut -----------

# ------------------------------------------------------------
# +++++++++++ Naturkatastrophen / Disasters ++++++++++++++++++
# ------------------------------------------------------------
     if iGameTurn > 0 and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_PERMANENT_ALLIANCES):

       iTurnDisastersModulo = 80
       bApocalypse = False
       if not gc.getGame().isGameMultiPlayer():
         if gc.getPlayer(gc.getGame().getActivePlayer()).getName() == "Apocalypto":
           iTurnDisastersModulo = 20
           bApocalypse = True

       if gc.getGame().getGameTurnYear() > -600 and iGameTurn % 25 == 0: self.doNebel()

       # Teiler
       if gc.getGame().getGameTurnYear() > -400: iTeiler = 2
       else: iTeiler = 1

       # entweder Erdbeben, Comet, Meteore oder Vulkan

       # Katas erzeugen
       if iGameTurn % (iTurnDisastersModulo / iTeiler) == 0:
         iRand = self.myRandom(5, None)
         if iRand == 0: self.doErdbeben(0,0)
         elif iRand == 1: self.doVulkan(0,0,0)
         elif iRand == 2: self.doComet()
         else: self.doMeteorites()

       # Warnung aussenden
       elif (iGameTurn + 1) % (iTurnDisastersModulo / iTeiler) == 0:
         iBuilding1 = gc.getInfoTypeForString("BUILDINGCLASS_ORACLE")
         iBuilding2 = gc.getInfoTypeForString("BUILDINGCLASS_ORACLE2")
         iRange = gc.getMAX_PLAYERS()
         i=0
         for i in range (iRange):
           loopPlayer = gc.getPlayer(i)
           if loopPlayer.isHuman():
             iChance = 0
             if loopPlayer.getBuildingClassCount(iBuilding1) > 0: iChance = 100
             elif loopPlayer.getBuildingClassCount(iBuilding2) > 0: iChance = 50
             if iChance > 0 and iChance > self.myRandom(100, None):
               # Player gets warning message
               CyInterface().addMessage(i, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_ORACLE_WARNING",("",)), None, 2, None, ColorTypes(10), 0, 0, False, False)

       if bApocalypse:
         if iGameTurn % (85 / iTeiler) == 0: self.doSeesturm()
         if iGameTurn % (90 / iTeiler) == 0: self.doGrasshopper()
         if iGameTurn % (60 / iTeiler) == 0: self.doTornado()
       elif iGameTurn % (70 / iTeiler) == 0:
         iRand = self.myRandom(2, None)
         if iRand == 0: self.doSeesturm()
         elif iRand == 1: self.doGrasshopper()
         else: self.doTornado()

       if iGameTurn % (90 / iTeiler) == 0: self.doSandsturm()

       if iGameTurn % ((iTurnDisastersModulo / iTeiler) + 20) == 0: self.undoVulkan()

# -- Ende Naturkatastrophen -------------------------------------------

     # ---------------------
     # Ende if iPlayer == 18
     # --------------------

# -- Seewind / Fair wind ----
     if iGameTurn % 15 == 0: self.doSeewind()


# -- AI Commissions Mercenaries (AI Mercenaries)
    # not in first turn (scenarios)
    if not pPlayer.isHuman():
     if iGameTurn > 1 and iGameTurn % 10 == 0:
      if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SOELDNERTUM")):

       iGold = pPlayer.getGold()

       if iGold > 400:
         bDoIt = false

         if iGold > 800: iChance = 20
         else: iChance = 10
         if iChance > self.myRandom(100, None): bDoIt = true

         if bDoIt:
           self.doAIPlanAssignMercenaries(iPlayer)
           # 20% gleich nochmal
           if 0 == self.myRandom(5, None):
             self.doAIPlanAssignMercenaries(iPlayer)
             # 10% ein drittes Mal damits interessant wird ;)
             if 0 == self.myRandom(10, None): self.doAIPlanAssignMercenaries(iPlayer)

    # PAE Debug Mark
    #"""

# ++ Standard BTS ++
    if (gc.getGame().getElapsedGameTurns() == 1):
      if (gc.getPlayer(iPlayer).isHuman()):
        if (gc.getPlayer(iPlayer).canRevolution(0)):
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC)
          popupInfo.addPopup(iPlayer)

    CvAdvisorUtils.resetAdvisorNags()
    CvAdvisorUtils.endTurnFeats(iPlayer)
# +++ -------

  def onEndTurnReady(self, argsList):
    iGameTurn = argsList[0]

  def onFirstContact(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Contact'
    iTeamX,iHasMetTeamY = argsList
    if (not self.__LOG_CONTACT):
      return
    CvUtil.pyPrint('Team %d has met Team %d' %(iTeamX, iHasMetTeamY))

  def onCombatResult(self, argsList):
    'Combat Result'
    pWinner,pLoser = argsList
    playerX = PyPlayer(pWinner.getOwner())
    unitX = PyInfo.UnitInfo(pWinner.getUnitType())
    playerY = PyPlayer(pLoser.getOwner())
    unitY = PyInfo.UnitInfo(pLoser.getUnitType())
    # PAE
    bUnitDone = False

    # PAE Debug Mark
    #"""
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    # +++++ Scenario: FirstPunicWar - Start
    if sScenarioScriptData == "FirstPunicWar":
      if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_QUADRIREME"):
        if gc.getPlayer(pWinner.getOwner()).getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
          iTech = gc.getInfoTypeForString("TECH_WARSHIPS")
          iTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
          pTeam = gc.getTeam(iTeam)
          if not pTeam.isHasTech(iTech):
            pTeam.setHasTech(iTech, 1, pWinner.getOwner(), 0, 1)
    # +++++ Scenario: FirstPunicWar - End


# Weil bSuicide in XML scheinbar so funktioniert, dass auf jeden Fall der Gegner stirbt (was ich nicht will)
    if pWinner.getUnitType() == gc.getInfoTypeForString("UNIT_BURNING_PIGS"):
      #pWinner.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      pWinner.kill(1,pWinner.getOwner())
      return

    # Auto Formation Flight
    #iFormation = gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG")
    #if not pWinner.isHasPromotion(iFormation):
    #  if pWinner.getDamage() >= 80: pWinner.setHasPromotion(iFormation, True)

    # AI - Formations
    if not gc.getPlayer(pLoser.getOwner()).isHuman():
      pPlot = pLoser.plot()
      if pPlot.getNumUnits() > 4:
        self.doAIPlotFormations (pPlot, pLoser.getOwner())

# --------- Feature - Automated Unit Ranking via Promotions: Trained, Experienced, Seasoned, Veteran, Elite, Legendary
# ---- Trainiert, Kampferfahren, Routiniert, Veteran, Elite, Legende
    # Each promotion gives +x% Strength
    # Animal Attack brings only 1st Ranking
    if not bUnitDone and (pWinner.isMilitaryHappiness() or pWinner.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL")):
      if pLoser.isMilitaryHappiness() or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
       iCombat1 = gc.getInfoTypeForString('PROMOTION_COMBAT1')
       iCombat2 = gc.getInfoTypeForString('PROMOTION_COMBAT2')
       iCombat3 = gc.getInfoTypeForString('PROMOTION_COMBAT3')
       iCombat4 = gc.getInfoTypeForString('PROMOTION_COMBAT4')
       iCombat5 = gc.getInfoTypeForString('PROMOTION_COMBAT5')
       iCombat6 = gc.getInfoTypeForString('PROMOTION_COMBAT6')

       iNeg1 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG1')
       iNeg2 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG2')
       iNeg3 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG3')
       iNeg4 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG4')
       iNeg5 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG5')

       if not (pWinner.isHasPromotion(iCombat3) and pLoser.getOwner() == gc.getBARBARIAN_PLAYER()):

        if pWinner.isHasPromotion(iCombat5):
          iChance = 2
          iNewRank = iCombat6
        elif pWinner.isHasPromotion(iCombat4):
          iChance = 2
          iNewRank = iCombat5
        elif pWinner.isHasPromotion(iCombat3):
          iChance = 3
          iNewRank = iCombat4
        elif pWinner.isHasPromotion(iCombat2):
          iChance = 3
          iNewRank = iCombat3
        elif pWinner.isHasPromotion(iCombat1):
          iChance = 4
          iNewRank = iCombat2
        else:
          iChance = 5
          iNewRank = iCombat1

        # PAE Better AI: always gets it by 100%
        if not gc.getPlayer(pWinner.getOwner()).isHuman(): iChance = 10

        if iNewRank == iCombat1 or iNewRank == iCombat2 or not pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
          if iChance > self.myRandom(10, None) and not pWinner.isHasPromotion(iCombat6):
            if (pWinner.getOwner(),pWinner.getID()) not in self.PAEInstanceFightingModifier:
                self.PAEInstanceFightingModifier.append((pWinner.getOwner(),pWinner.getID()))
                pWinner.setHasPromotion(iNewRank, True)
                if gc.getPlayer(pWinner.getOwner()).isHuman():                                                                # unitX.getDescription()
                  CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RANKING",(pWinner.getName(),gc.getPromotionInfo(iNewRank).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewRank).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)

          # War wariness parallel ab Veteran
          elif pWinner.isHasPromotion(iCombat4) and not pWinner.isHasPromotion(iNeg5):
            if (pWinner.getOwner(),pWinner.getID()) not in self.PAEInstanceFightingModifier:
              iChance = 0
              if pWinner.isHasPromotion(iNeg4):
                iChance = 2
                iNewRank = iNeg5
              elif pWinner.isHasPromotion(iNeg3):
                iChance = 2
                iNewRank = iNeg4
              elif pWinner.isHasPromotion(iNeg2):
                iChance = 2
                iNewRank = iNeg3
              elif pWinner.isHasPromotion(iNeg1):
                iChance = 1
                iNewRank = iNeg2
              else:
                iChance = 1
                iNewRank = iNeg1

              if iChance > self.myRandom(10, None):
                self.PAEInstanceFightingModifier.append((pWinner.getOwner(),pWinner.getID()))
                pWinner.setHasPromotion(iNewRank, True)
                if gc.getPlayer(pWinner.getOwner()).isHuman():
                  CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_WAR_WEARINESS",(pWinner.getName(),gc.getPromotionInfo(iNewRank).getDescription())), "AS2D_REBELLION", 2, gc.getPromotionInfo(iNewRank).getButton(), ColorTypes(12), pWinner.getX(), pWinner.getY(), True, True)



       # PAE V: Gewinner kann Mercenary-Promo ab Veteran verlieren
       # Better AI: 100%
       if pWinner.isHasPromotion(iCombat4):
         iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
         if pWinner.isHasPromotion(iPromoMercenary):

           bDoIt = false
           if gc.getPlayer(pWinner.getOwner()).isHuman():
             iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
             iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
             iPromoLeadership = gc.getInfoTypeForString("PROMOTION_LEADERSHIP")

             if pWinner.isHasPromotion(iPromoLoyal) or pWinner.isHasPromotion(iPromoLeader) or pWinner.isHasPromotion(iPromoLeadership): iChance = 2 #50%
             else: iChance = 4 #25%

             if self.myRandom(iChance, None) == 1:
               bDoIt = true
           else: bDoIt = true

           if bDoIt:
             pWinner.setHasPromotion(iPromoMercenary, False)

       # PAE V: Old veterans needs more time to get fit again (elite needs longer)
       # Better AI: HI only
       if gc.getPlayer(pWinner.getOwner()).isHuman():
         if pWinner.isHasPromotion(iCombat6):
           if pWinner.getDamage() < 40: pWinner.setDamage(40, -1)
         elif pWinner.isHasPromotion(iCombat5):
           if pWinner.getDamage() < 20: pWinner.setDamage(20, -1)
         #elif pWinner.isHasPromotion(iCombat4):
         #  if pWinner.getDamage() < 20: pWinner.setDamage(20, -1)


# --------- Feature - Seuche auf dem Schlachtfeld ----------------------
    # Wahrscheinlichkeit einer Seuche auf drm Schlachtfeld
    # Ab 4 Einheiten, etwa Chance 2%
    if gc.getMap().plot(pLoser.getX(), pLoser.getY()).getNumUnits() > 3:
      pPlot1 = gc.getMap().plot(pWinner.getX(), pWinner.getY())
      pPlot2 = gc.getMap().plot(pLoser.getX(), pLoser.getY())
      feat_seuche = gc.getInfoTypeForString("FEATURE_SEUCHE")
      iRand = self.myRandom(50, None)
      if iRand == 1:
        if pPlot1.getFeatureType() == -1 and not pPlot1.isCity() and not pPlot1.isWater(): pPlot1.setFeatureType(feat_seuche,0)
        if pPlot2.getFeatureType() == -1 and not pPlot2.isCity() and not pPlot2.isWater(): pPlot2.setFeatureType(feat_seuche,0)
# --------------

# Einheit soll alles ausladen, wenn besiegt   #pie
# Geht nicht, leider wird zuerst das Cargo und dann die Einheit gekillt! Schade!
#    if pLoser.getDomainType() == DomainTypes.DOMAIN_LAND and pLoser.hasCargo(): pLoser.doCommand(CommandTypes.COMMAND_UNLOAD_ALL,0,0)

########################################################
# ---- Schiffe sollen nach dem Angriff die Haelfte der uebrigen Bewegungspunkte haben "
    bNavalUnit = false
    if pWinner.getDomainType() == DomainTypes.DOMAIN_SEA:
      bNavalUnit = true
      pWinner.changeMoves((pWinner.maxMoves()-pWinner.getMoves())/2)

########################################################
# ---- SEA: Schiffe sollen Treibgut erzeugen
# ---- LAND: Player can earn gold by winning a battle
    iCost = unitY.getProductionCost()

    # Ausnahmen
    UnitArray = []
    UnitArray.append(gc.getInfoTypeForString("UNIT_WORKBOAT"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_TREIBGUT"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_GAULOS"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_CAMEL"))
    UnitArray.append(gc.getInfoTypeForString("UNIT_ELEFANT"))

    AnimalArray = []
    AnimalArray.append(gc.getInfoTypeForString("UNIT_WILD_HORSE"))
    AnimalArray.append(gc.getInfoTypeForString("UNIT_WILD_CAMEL"))
    AnimalArray.append(gc.getInfoTypeForString("UNIT_ELEFANT"))

    if pLoser.getUnitType() not in UnitArray and pLoser.getUnitType() not in AnimalArray:

      # Seeeinheiten (Treibgut erzeugen)
      if bNavalUnit:
        # Treibgut Chance 50%
        if self.myRandom(2, None) == 0:

          terrain1 = gc.getInfoTypeForString("TERRAIN_OCEAN")
          terrain2 = gc.getInfoTypeForString("TERRAIN_COAST")
          iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

          # Freie Plots finden
          SeaPlots = []
          iX = pLoser.getX()
          iY = pLoser.getY()
          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iX + i - 1, iY + j - 1)
              if loopPlot != None and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isPeak() and not loopPlot.isCity() and not loopPlot.isHills():
                  if loopPlot.getTerrainType() == terrain1 or loopPlot.getTerrainType() == terrain2:
                    if loopPlot.getNumUnits() == 0: SeaPlots.append(loopPlot)

          if len(SeaPlots) > 0:
            if iCost > 180: iMaxTreibgut = 2
            else: iMaxTreibgut = 1
            iUnit = gc.getInfoTypeForString("UNIT_TREIBGUT")
            barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())

            for i in range(iMaxTreibgut):
              if len(SeaPlots) == 0: break
              iRand = self.myRandom(len(SeaPlots), None)
              loopPlot = SeaPlots[iRand]
              # Unit erzeugen
              NewUnit = barbPlayer.initUnit(iUnit, loopPlot.getX(), loopPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              NewUnit.setImmobileTimer(2)
              if gc.getPlayer(pWinner.getOwner()).isHuman():
                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_UNIT_ERSTELLT",(PyInfo.UnitInfo(iUnit).getDescription(),)), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(11), loopPlot.getX(), loopPlot.getY(), True, True)
              # Plot aus der Liste entfernen
              SeaPlots.remove(loopPlot)

      # Landeinheiten
      else:

        if iCost > 0:
          iGold = int(iCost / 10)
          if iGold > 1:
            iGold = self.myRandom(iGold, None)
            gc.getPlayer(pWinner.getOwner()).changeGold(iGold)
            if pWinner.getOwner() > -1 and iGold > 0:
              if gc.getPlayer(pWinner.getOwner()).isHuman():
                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MONEY_UNIT_KILLED",("",iGold)), None, 2, None, ColorTypes(8), 0, 0, False, False)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gold durch Einheitensieg (Zeile 1711)",iGold)), None, 2, None, ColorTypes(10), 0, 0, False, False)

########################################################
# --- Treibgut gibt Sklaven oder Gold, wenn iCargo nicht voll is
    if bNavalUnit:
      if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_TREIBGUT"):
        bUnitDone = True
        bMove2NextPlot = False
        # Ist ein freier Platz am Schiff?
        #if pWinner.getCargo() < unitX.getCargoSpace():
        if pWinner.getCargo() < pWinner.cargoSpace():
          # Treibgut einfangen
          iRand = self.myRandom(3, None)
          if iRand < 2:
            iRand = self.myRandom(2, None)
            if iRand == 0:
              iUnit = gc.getInfoTypeForString("UNIT_SLAVE")
              if gc.getPlayer(pWinner.getOwner()).isHuman():
                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_SLAVE",("",)), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(8), pLoser.getX(), pLoser.getY(), True, True)
              # Create unit
              #loopPlot = gc.getMap().plot(pLoser.getX(), pLoser.getY())
              #if loopPlot.getNumUnits() <= 1:
              #  iX = pLoser.getX()
              #  iY = pLoser.getY()
              #else:
              iX = pWinner.getX()
              iY = pWinner.getY()
              NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(iUnit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              NewUnit.setTransportUnit(pWinner)
              NewUnit.finishMoves()
            else:
              iRand = 11 + self.myRandom(20, None)
              gc.getPlayer(pWinner.getOwner()).changeGold(iRand)
              if gc.getPlayer(pWinner.getOwner()).isHuman():
                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MONEY_UNIT_KILLED",("",iRand)), None, 2, gc.getUnitInfo(gc.getInfoTypeForString("UNIT_TREIBGUT")).getButton(), ColorTypes(8), pLoser.getX(), pLoser.getY(), True, True)


          # Treibgut nicht eingefangen
          else:
            # Einheit Treibgut neu erzeugen
            bMove2NextPlot = True
            if gc.getPlayer(pWinner.getOwner()).isHuman():
              iRand = 1 + self.myRandom(9, None)
              szText = CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_CATCHME"+str(iRand),())
              CyInterface().addMessage(pWinner.getOwner(), True, 10, szText, None, 2, gc.getUnitInfo(gc.getInfoTypeForString("UNIT_TREIBGUT")).getButton(), ColorTypes(11), pLoser.getX(), pLoser.getY(), True, True)

        # Cargo voll
        else:
          # Einheit Treibgut neu erzeugen
          bMove2NextPlot = True
          if gc.getPlayer(pWinner.getOwner()).isHuman():
            CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_NOSPACE",("",)), None, 2, gc.getUnitInfo(gc.getInfoTypeForString("UNIT_TREIBGUT")).getButton(), ColorTypes(11), pLoser.getX(), pLoser.getY(), True, True)


        # Treibgut soll nicht ausserhalb der Kulturgrenze wiederauftauchen (jumpToNearestValidPlot), sondern gleich 1 Plot daneben (sofern frei)
        if bMove2NextPlot:
            lNewPlot = []
            iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
            for x in range(3):
              for y in range(3):
                loopPlot = gc.getMap().plot(pLoser.getX()-1+x,pLoser.getY()-1+y)
                if loopPlot != None and not loopPlot.isNone():
                  if loopPlot.getFeatureType() == iDarkIce: continue
                  if loopPlot.getNumUnits() == 0:
                    if loopPlot.isWater():
                      lNewPlot.append(loopPlot)

            if len(lNewPlot) >= 1:
              iRand = self.myRandom(len(lNewPlot), None)
              iX = lNewPlot[iRand].getX()
              iY = lNewPlot[iRand].getY()
            else:
              pLoser.jumpToNearestValidPlot()
              iX = pLoser.getX()
              iY = pLoser.getY()

            # Create unit
            gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_TREIBGUT"), iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)



########################################################
# --------- if unit will renegade ----------------------
    bUnitRenegades = True

# PROMOTION-IDs: LOYALITAT: 0 , LEADER: 45, LEADERSHIP: 46 (ehemals)
    iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
    iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
    iPromoLeadership = gc.getInfoTypeForString("PROMOTION_LEADERSHIP")
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    iPromoBrander = gc.getInfoTypeForString("PROMOTION_BRANDER")
    iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
    #iPromoSurrender = gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG")

    # Ausnahmen - using UnitArray from above
    if pWinner.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL: bUnitRenegades = False
    elif pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL: bUnitRenegades = False
    elif pLoser.getUnitType() in UnitArray: bUnitRenegades = False
    elif pLoser.getUnitType() in AnimalArray: bUnitRenegades = False
    # PAE V: Piraten sollen nur kentern: UnitInfos.xml: bNoCapture=1
    elif pWinner.isNoCapture(): bUnitRenegades = False
    #elif pLoser.isHasPromotion(iPromoSurrender): bUnitRenegades = True
    elif pLoser.isHasPromotion(iPromoLoyal) and not pLoser.isHasPromotion(iPromoMercenary): bUnitRenegades = False
    elif pLoser.isHasPromotion(iPromoLeader) or pLoser.isHasPromotion(iPromoBrander) or pWinner.isNoCapture(): bUnitRenegades = False
    elif pLoser.hasCargo() and pLoser.canAttack(): bUnitRenegades = False


    if bUnitRenegades:
     pLoserPlot = gc.getMap().plot(pLoser.getX(), pLoser.getY())
     if pLoserPlot.getNumUnits() == 1 and pLoser.getCaptureUnitType(pLoser.getCivilizationType()) > -1: bUnitRenegades = False

     # Attacking from Coast
     if not bUnitDone and pWinner.isCargo():
      pWinnerPlot = gc.getMap().plot(pWinner.getX(), pWinner.getY())
      if pWinnerPlot.isWater():
        iNumCargoSpace = 0
        iNumCargoUnits = 0
        iRange = pWinnerPlot.getNumUnits()
        i=0
        for i in range (iRange):
          if pWinnerPlot.getUnit(i).getOwner() == pWinner.getOwner():
            iNumCargoSpace += pWinnerPlot.getUnit(i).cargoSpace()
            iNumCargoUnits += pWinnerPlot.getUnit(i).getCargo()

        if iNumCargoSpace <= iNumCargoUnits: bUnitRenegades = False
     # ----


     if bUnitRenegades:

      #if pLoser.isHasPromotion(iPromoSurrender): iRandMax = 0 #100%

      iUnitRenegadeChance = 20 # 10%
      if pWinner.isHasPromotion(iPromoLeader): iUnitRenegadeChance += 20
      if pWinner.isHasPromotion(iPromoHero):   iUnitRenegadeChance += 10
      if pWinner.isHasPromotion(iPromoLeadership): iUnitRenegadeChance += 10
      if pLoser.isHasPromotion(iPromoHero):   iUnitRenegadeChance -= 10
      if pLoser.isHasPromotion(iPromoLeadership): iUnitRenegadeChance -= 10
      # Trait Charismatic: Mehr Ueberlaeufer / more renegades
      if gc.getPlayer(pWinner.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CHARISMATIC")): iUnitRenegadeChance += 10
      if gc.getPlayer(pLoser.getOwner() ).hasTrait(gc.getInfoTypeForString("TRAIT_CHARISMATIC")): iUnitRenegadeChance -= 10
      if pLoser.isHasPromotion(iPromoMercenary): iUnitRenegadeChance += 10

      iRand = self.myRandom(100, None)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Einheit allegiance Chance (Zeile 4150)",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # Winner gets Loser Unit
      # if iRand < iUnitRenegadeChance:
       # # Winner gets Loser Unit
       # if self.myRandom(3, None) == 0:

        # # Piratenschiffe werden normale Schiffe
        # iNewUnitType = pLoser.getUnitType()
        # if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
          # if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"): iNewUnitType = gc.getInfoTypeForString("UNIT_KONTERE")
          # elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_BIREME"): iNewUnitType = gc.getInfoTypeForString("UNIT_BIREME")
          # elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"): iNewUnitType = gc.getInfoTypeForString("UNIT_TRIREME")
          # elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"): iNewUnitType = gc.getInfoTypeForString("UNIT_LIBURNE")

        # # Create a new unit
        # NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(iNewUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        # NewUnit.finishMoves()

        # if pLoser.getUnitCombatType() != -1:
          # NewUnit.setDamage(90, -1)
          # NewUnit.setExperience(pLoser.getExperience(), -1)
          # NewUnit.setLevel(pLoser.getLevel())
          # # Check its promotions
          # iRange = gc.getNumPromotionInfos()
          # for iPromotion in range(iRange):
            # # init all promotions of the loser unit
            # if pLoser.isHasPromotion(iPromotion):
              # NewUnit.setHasPromotion(iPromotion, True)

          # # PAE V: Loyal weg, Mercenary dazu
          # if NewUnit.isHasPromotion(iPromoLoyal): NewUnit.setHasPromotion(iPromoLoyal, False)
          # if not NewUnit.isHasPromotion(iPromoMercenary): NewUnit.setHasPromotion(iPromoMercenary, True)

          # # Remove formations
          # self.doUnitFormation (NewUnit, -1)

          # # PAE V: Trait-Promotions
          # # 1. Agg und Protect Promos weg
          # # (2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten) Stimmt nicht, sie erhalten die Promo bei initUnit() sowieso
          # if not gc.getPlayer(pWinner.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
            # iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")
            # if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)
         # # if not gc.getPlayer(pWinner.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
         # #   iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_PROTECTIVE")
         # #   if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)

        # if gc.getPlayer(pWinner.getOwner()).isHuman():
          # CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RENEGADE_TO_YOU",(unitY.getDescription(),0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        # elif gc.getPlayer(pLoser.getOwner()).isHuman():
          # CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RENEGADE_FROM_YOU",(unitY.getDescription(),0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
        # bUnitDone = True

        # # ***TEST***
        # #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gewinner (" + str(pWinner.getOwner()) + ") bekommt Verlierer (" + str(pLoser.getOwner()) + ")",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


       # # Winner gets Slave
       # elif pWinner.getDomainType() == DomainTypes.DOMAIN_LAND:

        # # Ausnahmen
        # UnitArray = []
        # UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
        # UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
        # UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
        # UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
        # UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
        # UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))

        # if pLoser.getUnitType() not in UnitArray:
          # iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
          # iThisTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
          # team = gc.getTeam(iThisTeam)
          # if team.isHasTech(iTechEnslavement):
            # # Create a slave unit
            # NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            # NewUnit.finishMoves()
            # if gc.getPlayer(pWinner.getOwner()).isHuman():
              # CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_TO_YOU",(unitY.getDescription(),0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
            # elif gc.getPlayer(pLoser.getOwner()).isHuman():
              # CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_FROM_YOU",(unitY.getDescription(),0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
            # bUnitDone = True

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gewinner bekommt Sklave (Zeile 2627)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ------- End Unit renegades / desertiert -----------

# ------- Certain animals can be captured, when domestication has been researched
# ------- Bestimmte Tiere koennen eingefangen werden, wenn Domestizier-Tech erforscht wurde
    if pLoser.getUnitType() in AnimalArray:
      iTech = -1
      if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_WILD_HORSE"): iTech = gc.getInfoTypeForString("TECH_PFERDEZUCHT")
      elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_WILD_CAMEL"): iTech = gc.getInfoTypeForString("TECH_KAMELZUCHT")
      elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_ELEFANT"): iTech = gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")

      if iTech != -1:
        iThisTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
        if gc.getTeam(iThisTeam).isHasTech(iTech):
          bUnitDone = True
          # Create a new unit
          NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(pLoser.getUnitType(), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          NewUnit.finishMoves()
          if gc.getPlayer(pWinner.getOwner()).isHuman():
             CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_UNIT_EROBERT",(unitY.getDescription(),0)), None, 2, None, ColorTypes(8), 0, 0, False, False)


# ------- Loser Unit Elephant makes 10% collateral damage to friendly units
    if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"):
          pLoserPlot = gc.getMap().plot(pLoser.getX(), pLoser.getY())
          iRange = pLoserPlot.getNumUnits()
          for iLoserUnits in range (iRange):
            if pLoserPlot.getUnit(iLoserUnits).getDamage() + 20 < 100: pLoserPlot.getUnit(iLoserUnits).changeDamage(20, False)
          if gc.getPlayer(pWinner.getOwner()).isHuman():
            CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ELEPHANT_DAMAGE_1",(unitY.getDescription(),0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
          elif gc.getPlayer(pLoser.getOwner()).isHuman():
            CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ELEPHANT_DAMAGE_2",(unitY.getDescription(),0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
    # end loser elephants

# ----- Ende Loser Unit (not captured)

# ------- Feature 1: Generalseinheiten bekommen +1XP, wenn im selben Stack eine angreifende Einheit siegt (10%)
# ------- Feature 2: Eine Generalseinheit bekommt HERO Promotion wenn eine Einheit einen General oder einen Held besiegt.
# ------------------ Ist kein General im Stack bekommt die Promotion die Gewinner-Unit
# ------------------ Und Gewinner bekommt additional +3 XP
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    txtPopUpHero = ""
# ------- Diese Features betreffen nur attackierende Einheiten (keine defensiven)
    if pWinner.isMadeAttack():
        iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
        pWinnerPlot = gc.getMap().plot(pWinner.getX(), pWinner.getY())
        iNumUnits = pWinnerPlot.getNumUnits()

        bPromoHero = False
        bPromoHeroDone = False
        bLeaderAnwesend = False
        if pLoser.isHasPromotion(iPromoLeader) or pLoser.isHasPromotion(iPromoHero):
          bPromoHero = True

          # Hero und +3 XP
          pWinner.setExperience(pWinner.getExperience()+3, -1)
          if not pWinner.isHasPromotion(iPromoHero):
            pWinner.setHasPromotion(iPromoHero, True)
            bPromoHeroDone = True
            if gc.getPlayer(pWinner.getOwner()).isHuman():
              if pLoser.isHasPromotion(iPromoLeader):
                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_3",(pWinner.getName(),pLoser.getName()))
                CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
              else:
                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_4",(pWinner.getName(),0))
                CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)

        # for each general who accompanies the stack: +1 XP , Promo: LEADER = 45
        # one general gets the hero promo, if not possessing
        i=0
        for i in range(iNumUnits):
         pLoopUnit = pWinnerPlot.getUnit(i)
         if pLoopUnit.getOwner() == pWinner.getOwner():
          if pLoopUnit.isHasPromotion(iPromoLeader):
            bLeaderAnwesend = True

            # XP
            if self.myRandom(10, None) == 0: pLoopUnit.setExperience(pLoopUnit.getExperience()+1, -1)

            # First general in stack who doesnt possess hero promo gets it
            if bPromoHero and not bPromoHeroDone:
              if not pLoopUnit.isHasPromotion(iPromoHero):
                pLoopUnit.setHasPromotion(iPromoHero, True)
                bPromoHeroDone = True

                if gc.getPlayer(pWinner.getOwner()).isHuman():
                  if pLoser.isHasPromotion(iPromoLeader):
                    txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_1",(pLoopUnit.getName(),pLoser.getName()))
                    CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinnerPlot.getUnit(i).getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
                  else:
                    txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_2",(pLoopUnit.getName(),0))
                    CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinnerPlot.getUnit(i).getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)



        # Eine Einheit mit Mercenary-Promo kann diese verlieren, wenn ein General im Stack ist (5% Chance)
        if bLeaderAnwesend:
          iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
          if pWinner.isHasPromotion(iPromoMercenary):
            if self.myRandom(20, None) == 0:
              pWinner.setHasPromotion(iPromoMercenary, False)
              if gc.getPlayer(pWinner.getOwner()).isHuman():
                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_6",(pWinner.getName(),)), "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)


# ------- Furor germanicus / teutonicus: 30% / 20% / 10% Chance
    if not bUnitDone:
      iWinnerST = pWinner.baseCombatStr()
      iLoserST  = pLoser.baseCombatStr()
      # weak units without death calc (eg animal)
      # enemy units should be equal
      if iLoserST >= (iWinnerST/5)*4:

        iPromoFuror1 = gc.getInfoTypeForString('PROMOTION_FUROR1')
        iPromoFuror2 = gc.getInfoTypeForString('PROMOTION_FUROR2')
        iPromoFuror3 = gc.getInfoTypeForString('PROMOTION_FUROR3')
        if pWinner.isHasPromotion(iPromoFuror3): iChanceSuicide = 1
        elif pWinner.isHasPromotion(iPromoFuror2): iChanceSuicide = 2
        elif pWinner.isHasPromotion(iPromoFuror1): iChanceSuicide = 3
        else: iChanceSuicide = 0

        if iChanceSuicide > 0:
          if iChanceSuicide > self.myRandom(10, None):
            if gc.getPlayer(pWinner.getOwner()).isHuman():
              CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_FUROR_SUICIDE",(pWinner.getName(),0)), None, 2, pWinner.getButton(), ColorTypes(7), pWinner.getX(), pWinner.getY(), True, True)
            #pWinner.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
            pWinner.kill(1,pWinner.getOwner())
            bUnitDone = True

# ------- Flucht / Escape

    # # Flucht der Einheit / Escape of units --------
    # # Defending unit only (inaktiv)
    # # Nur wenn die Einheit nicht desertiert hat: bUnitDone
    # #if not bUnitDone and not pLoser.isAttacking():
    # # PAE V: defending units in cities gets flight (hiding behind walls) with max 70%. units kept on the city plot
    # bUnitFlucht = False
    # if not bUnitDone:

        # # Eine einzelne kaperbare Unit darf nicht fluechten
        # #if pLoser.getCaptureUnitType(pLoser.getOwner()) > -1 and gc.getMap().plot(pLoser.getX(), pLoser.getY()).getNumUnits() > 1:
        # if pLoser.getCaptureUnitType(pLoser.getCivilizationType()) == -1:

          # bIsCity = False
          # pLoserPlot = gc.getMap().plot(pLoser.getX(), pLoser.getY())
          # if pLoserPlot.isCity():
            # iChance = pLoserPlot.getPlotCity().getPopulation()
            # if iChance > 7: iChance = 7
            # bIsCity = True
            # iMaxHealth = 30 # max 30%
          # else:
            # iPromoFlucht1 = gc.getInfoTypeForString("PROMOTION_FLUCHT1")
            # iPromoFlucht2 = gc.getInfoTypeForString("PROMOTION_FLUCHT2")
            # iPromoFlucht3 = gc.getInfoTypeForString("PROMOTION_FLUCHT3")
            # if pLoser.isHasPromotion(iPromoFlucht3):
              # iChance = 8 # Flucht 3 - 80%
              # iMaxHealth = 20 # max 20%
            # elif pLoser.isHasPromotion(iPromoFlucht2):
              # iChance = 6 # Flucht 2 - 60%
              # iMaxHealth = 15 # max 15%
            # elif pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
              # bIsCity = True
              # iChance = 5
              # iMaxHealth = 12 # max 12%
            # elif pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE") \
            # or pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE_HILL"):
              # bIsCity = True
              # iChance = 5
              # iMaxHealth = 10 # max 10%
            # elif pLoser.isHasPromotion(iPromoFlucht1):
              # iChance = 4 # Flucht 1 - 40%
              # iMaxHealth = 10 # max 10%
            # elif pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
              # if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 2:
                # iChance = 8
                # iMaxHealth = 50
              # else:
                # iChance = 3
                # iMaxHealth = 25
            # else:
              # iChance = 2
              # iMaxHealth = 5 # max 5%

          # # Bei Schiffen eine Extra-Berechnung
          # if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
              # if pWinner.getDamage() >= 50:
                # iChance = 10 # 100%: somit muss man womoeglich ein Schiff 2x angreifen, bevor es sinkt
                # iMaxHealth = 20
              # else:
                # iChance += 1
                # iMaxHealth += 5

          # # Berittene nochmal +10%, except in cities -10%
          # iCombatMounted = gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")
          # if pLoser.getUnitCombatType() == iCombatMounted:
            # if bIsCity: iChance -= 1
            # else: iChance += 1

          # iRand = 1+self.myRandom(10, None)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Fluchtchance (Zeile 2924)",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Max Health (Zeile 2925)",iMaxHealth)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          # if iRand < iChance:

            # # Create a new unit
            # #pPlot = pLoser.plot()
            # #if pPlot.getNumUnits() == 1: pLoser.jumpToNearestValidPlot()
            # NewUnit = gc.getPlayer(pLoser.getOwner()).initUnit(pLoser.getUnitType(),  pLoser.getX(), pLoser.getY(), UnitAITypes(pLoser.getUnitAIType()), DirectionTypes.DIRECTION_SOUTH)
            # if pLoser.isMadeAttack(): NewUnit.finishMoves()

            # if pLoser.getUnitCombatType() != -1 or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:

             # iRandHealth = 1+self.myRandom(iMaxHealth, None)

             # NewUnit.setDamage(100-iRandHealth,-1) # Max Health
             # NewUnit.setExperience(pLoser.getExperience(), -1)
             # NewUnit.setLevel(pLoser.getLevel())

             # # Check its promotions
             # iRange = gc.getNumPromotionInfos()
             # for iPromotion in range(iRange):
               # # init all promotions the unit had
               # if pLoser.isHasPromotion(iPromotion):
                 # NewUnit.setHasPromotion(iPromotion, True)

            # #if UnitName != "" and UnitName != NewUnit.getName(): NewUnit.setName(UnitName)
            # UnitName = pLoser.getName()
            # if UnitName != gc.getUnitInfo(pLoser.getUnitType()).getText():
               # UnitName = re.sub(" \(.*?\)","",UnitName)
               # NewUnit.setName(UnitName)


            # if not bIsCity: NewUnit.jumpToNearestValidPlot()
            # if gc.getPlayer(pLoser.getOwner()).isHuman():
              # CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE",(NewUnit.getName(),0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            # if gc.getPlayer(pWinner.getOwner()).isHuman():
              # CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE_2",(NewUnit.getName(),0)), None, 2, None, ColorTypes(13), 0, 0, False, False)

            # bUnitDone = True
            # bUnitFlucht = True

            # # if Unit was a leader (PROMOTION_LEADER)
            # if pLoser.getLeaderUnitType() > -1:
              # NewUnit.setLeaderUnitType(pLoser.getLeaderUnitType())
              # pLoser.setLeaderUnitType(-1) # avoids ingame message "GG died in combat"

            # # ***TEST***
            # #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Einheit fluechtet (Zeile 2774)",iChance)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# LOSER: Mounted -> Melee or Horse
# Nur wenn die Einheit nicht desertiert hat: bUnitDone
    if not bUnitDone and (pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED") or pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT")):

        bDoIt = False
        iNewUnitType = -1
        if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
          bDoIt = True
        elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN")
        elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PRAETORIAN2_RIDER"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN2")
          bDoIt = True
        elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE")
          bDoIt = True
        elif gc.getUnitInfo(pLoser.getUnitType()).getPrereqAndBonus() == gc.getInfoTypeForString("BONUS_HORSE"):
          bDoIt = True

        if bDoIt == True:
          iRand = self.myRandom(10, None)
          if iRand == 0 and iNewUnitType != -1:
            # Create a new unit
            NewUnit = gc.getPlayer(pLoser.getOwner()).initUnit(iNewUnitType, pLoser.getX(), pLoser.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.setExperience(pLoser.getExperience(), -1)
            NewUnit.setLevel(pLoser.getLevel())
            NewUnit.finishMoves()
            NewUnit.setDamage(50, -1)
            # Check its promotions
            iRange = gc.getNumPromotionInfos()
            for iPromotion in range(iRange):
              # init all promotions the unit had
              if (pLoser.isHasPromotion(iPromotion)):
                NewUnit.setHasPromotion(iPromotion, True)

            if gc.getPlayer(pWinner.getOwner()).isHuman():
              CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_LOST_HORSE_1",(unitY.getDescription(),0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            elif gc.getPlayer(pLoser.getOwner()).isHuman():
              CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_LOST_HORSE_2",(unitY.getDescription(),0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            bUnitDone = True

          elif iRand <= 2:
            # Create horse unit
            iUnitType = gc.getInfoTypeForString("UNIT_HORSE")

            # Seek a Plot
            rebelPlotArray = []
            for i in range(3):
              for j in range(3):
                loopPlot = gc.getMap().plot(pLoser.getX() + i - 1, pLoser.getY() + j - 1)
                if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                  if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()):
                    rebelPlotArray.append(loopPlot)

            # Create Barbarian Horse Unit
            if len(rebelPlotArray) > 0:
              barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
              iPlot = self.myRandom(len(rebelPlotArray), None)
              barbPlayer.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)
            else:
              gc.getPlayer(pLoser.getOwner()).initUnit(iUnitType, pLoser.getX(), pLoser.getY(), UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)

            if gc.getPlayer(pLoser.getOwner()).isHuman():
              CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_ONLY_HORSE_LEFT",(unitY.getDescription(),0)), None, 2, None, ColorTypes(6), 0, 0, False, False)
            bUnitDone = True

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barbarisches Pferd erstellt",1)), None, 2, None, ColorTypes(10), pLoser.getX(), pLoser.getY(), False, False)


# ---- Ende Loser Mounted -> Melee


# ---- Script DATAs in Units
    if not bUnitFlucht and pLoser.getScriptData() != "":
       UnitText = pLoser.getScriptData()

       # Commissioned Mercenary  (MercFromCIV=CivID)
       if UnitText[:11] == "MercFromCIV":
          iMercenaryCiv = int(UnitText[12:])

          if not gc.getPlayer(pWinner.getOwner()).isHuman():
            # Ein minimaler Vorteil fuer die KI
            if pWinner.getOwner() != iMercenaryCiv:
              self.doAIMercTorture(pWinner.getOwner(),iMercenaryCiv)
          else:

            szText = CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE",("",))
            szText = szText + localText.getText("[NEWLINE][NEWLINE][ICON_STAR] ", ()) + CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE1",("",))

            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(szText)
            popupInfo.setData1(iMercenaryCiv) # iMercenaryCiv
            popupInfo.setData2(pWinner.getOwner()) # iPlayer
            popupInfo.setOnClickedPythonCallback("popupMercenaryTorture") # EntryPoints/CvScreenInterface und CvGameUtils -> 716
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES",(80,50)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
            popupInfo.addPopup(pWinner.getOwner())


# ------- Feature: Held Promo + 3 XP wenn Stier (Ur) oder Tier mit mehr als 3 Level erlegt wird
# ---------------- nur wenn Einheit nicht schon ein Held ist
# ---------------- und wenn Combat ST Sieger < als Combat ST vom Gegner
# ---------------- iPromoHero wird oben (Generalsfeature) init
    if not bUnitDone:
      if pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
        if gc.getUnitInfo(pWinner.getUnitType()).getCombat() < gc.getUnitInfo(pLoser.getUnitType()).getCombat():
          if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 4:
            txtPopUpHero = ""

            if pLoser.getDamage() >= 100:
              if not pWinner.isHasPromotion(iPromoHero):
                 pWinner.setHasPromotion(iPromoHero, True)
                 pWinner.setExperience(pWinner.getExperience()+3, -1)
                 if gc.getPlayer(pWinner.getOwner()).isHuman():
                   txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_5",(pWinner.getName(),pLoser.getName()))
                   CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)

            if txtPopUpHero != "":
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Text PopUp only!
              popupInfo.setText(txtPopUpHero)
              popupInfo.addPopup(pWinner.getOwner())

# --------- Jagd - Feature ----------------------
# Ab Tech Jagd (Hunting) bringen Tiere Essen in nahegelegene Stadt
    bAnimal = false
    if not bUnitDone:
     if pWinner.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL and ( pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitType() in AnimalArray ):
      bAnimal = true
      if pLoser.getCaptureUnitType(pLoser.getCivilizationType()) == -1:

       iJagd = gc.getInfoTypeForString("TECH_HUNTING")
       iThisTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
       team = gc.getTeam(iThisTeam)
       if team.isHasTech(iJagd):

        CityArray = []
        for x in range(9):
          for y in range(9):
            loopPlot = gc.getMap().plot(pWinner.getX() - 4 + x, pWinner.getY() - 4 + y)
            if loopPlot != None and not loopPlot.isNone():
              if loopPlot.isCity():
                pCity = loopPlot.getPlotCity()
                if pCity.getOwner() == playerX.getID():
                  CityArray.append(pCity)

        if len(CityArray) > 0:
          if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_BOAR"):
            # Boar/Deer 5 - 8
            iFoodMin = 5
            iFoodRand = 4
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_DEER"):
            # Deer 3 - 6
            iFoodMin = 3
            iFoodRand = 4
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_WILD_CAMEL"):
            # Camel 3 - 6
            iFoodMin = 3
            iFoodRand = 4
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_BEAR"):
            # Bear 4 - 7
            iFoodMin = 4
            iFoodRand = 4
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_WILD_HORSE"):
            # Horse 4 - 8
            iFoodMin = 4
            iFoodRand = 5
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_ELEFANT"):
            # Horse 6 - 8
            iFoodMin = 6
            iFoodRand = 3
          else:
            # Lion, Wolf, etc. 2 - 3
            iFoodMin = 2
            iFoodRand = 2

          # Hunter gets double bonus
          if pWinner.getUnitType() == gc.getInfoTypeForString("UNIT_HUNTER"): iFoodAdd = iFoodMin + iFoodRand - 1
          else: iFoodAdd = self.myRandom(iFoodRand, None) + iFoodMin

          iCity = self.myRandom(len(CityArray), None)
          CityArray[iCity].changeFood(iFoodAdd)
          if gc.getPlayer(pWinner.getOwner()).isHuman():
            CyInterface().addMessage(playerX.getID(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_ADD_FOOD",(pWinner.getName(),CityArray[iCity].getName(),iFoodAdd)), None, 2, pLoser.getButton(), ColorTypes(13), pLoser.getX(), pLoser.getY(), True, True)

    # Feature: Wenn die Generalseinheit stirbt, ist in jeder Stadt 2 bis 4 Hurry Anger! (GG Great General dies)
    # Richtet sich nach der Anzahl der lebenden Generals
    # PAE V: Einheiten im Stack bekommen Mercenary-Promo (je nach Anzahl an Generals im Stack)
    if not bUnitDone:

      # PROMOTION_LEADER
      if pLoser.getLeaderUnitType() > -1:

        # Auswirkungen nach dem Tod eines Generals
        self.doDyingGeneral(pLoser)

        # War Weariness
        iTeam = pLoser.getTeam()
        pTeam = gc.getTeam(iTeam)
        pTeam.changeWarWeariness (pWinner.getTeam(), 10)

        # PAE Movie
        if gc.getPlayer(pLoser.getOwner()).isHuman() and gc.getPlayer(pLoser.getOwner()).isTurnActive() or gc.getPlayer(pWinner.getOwner()).isHuman() and gc.getPlayer(pWinner.getOwner()).isTurnActive():

          if gc.getPlayer(pLoser.getOwner()).getCurrentEra() > 2 or gc.getPlayer(pWinner.getOwner()).getCurrentEra() > 2: iVids = 13
          else: iVids = 11
          # GG dying movies (CvWonderMovieScreen)
          iMovie = 1 + self.myRandom(iVids, None)

          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
          popupInfo.setData1(iMovie) # dynamicID in CvWonderMovieScreen
          popupInfo.setData2(-1) # fix pCity.getID()
          popupInfo.setData3(4) # fix PAE Movie ID for GG dies
          popupInfo.setText(u"showWonderMovie")
          if gc.getPlayer(pLoser.getOwner()).isHuman(): popupInfo.addPopup(pLoser.getOwner())
          if gc.getPlayer(pWinner.getOwner()).isHuman(): popupInfo.addPopup(pWinner.getOwner())

    # ---------------------

# ------- Change Culture Percent on the Plots after a battle
    # Choose Plot and add 20% culture to the winner
    pPlot = CyMap().plot(pLoser.getX(), pLoser.getY())
    if not pPlot.isWater():
      iCulture = pPlot.getCulture(pLoser.getOwner())
      # only if the loser has culture on this plot, the winner gets culture points (eg. neutral area or 3rd civ area)
      if iCulture > 0 and not pPlot.isCity() and not bAnimal:
        if iCulture > 9:
          Calc = iCulture/5
          iCalc = int(round(Calc,0))
        else:
          iCalc = 1
        pPlot.changeCulture(gc.getPlayer(pWinner.getOwner()).getID(),iCalc,1)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Kulturveraenderung durch Kampf (Zeile 1922)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# ------- Rebell takes over slaves if capturing
    if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE") and pWinner.getOwner() == gc.getBARBARIAN_PLAYER() and pWinner.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL:

      barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
      iUnitType = gc.getInfoTypeForString("UNIT_REBELL")
      iNumUnits = pPlot.getNumUnits()

#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iNumUnits",iNumUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # pPlot von Change Culture Percent (oben)
      if iNumUnits > 0:
        for i in range(iNumUnits):
          NewUnit = barbPlayer.initUnit(iUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
          NewUnit.finishMoves()

#        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iPlayer",pLoser.getOwner())), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if gc.getPlayer(pLoser.getOwner()).isHuman():
          CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CAPTURED_SLAVES",("",0)), None, 2, "Art/Interface/Buttons/Units/button_rebell.dds", ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebell holt sich Bausklaven zu sich (Zeile 1947)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# ------ ueberlaufende Stadt - City renegades
    # pPlot von oben
    bCityRenegade = False
    if pPlot.isCity():

     pCity = pPlot.getPlotCity()

     # PAE V ab Patch 3: Einheiten mobilisieren
     if pCity.isCapital():
       self.doMobiliseFortifiedArmy(pCity.getOwner())

     # ab PAE V: soll nur mehr Staedte betreffen
     iBuilding = gc.getInfoTypeForString("BUILDING_STADT")
     if pCity.isHasBuilding(iBuilding):

      ## ab PAE V: ab Tech Enslavement / Sklaverei (removed)
      #iTech = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
      iTeam = gc.getPlayer(pCity.getOwner()).getTeam()
      pTeam = gc.getTeam(iTeam)
      #if pTeam.isHasTech(iTech):

      # Anz Einheiten im Umkreis von 1 Feld, mit denen man im Krieg ist (military units)
      i=0
      j=0
      iUnitAnzahl = 0
      for i in range(3):
         for j in range(3):
           loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 1)
           iRange = loopPlot.getNumUnits()
           for iUnit in range (iRange):
             if loopPlot.getUnit(iUnit).isMilitaryHappiness():
               if pTeam.isAtWar(gc.getPlayer(loopPlot.getUnit(iUnit).getOwner()).getTeam()): iUnitAnzahl += 1

      # Anz Einheiten in der Stadt (military units)
      iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
      iUnitCity = 0
      iChanceUnits = 0
      iRange = pPlot.getNumUnits()
      for i in range (iRange):
         if pPlot.getUnit(i).canFight():
           iUnitCity += 1
           # loyal units ?
           if pPlot.getUnit(i).isHasPromotion(iPromoLoyal): iChanceUnits += 3
           else: iChanceUnits += 1


      # Verhaeltnis 1:4
      bCapital = False
      if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and pCity.isCapital(): bCapital = True

      if iUnitCity > 1 and iUnitCity * 4 < iUnitAnzahl and not bCapital and pCity.getPopulation() > 1:

         # Per defense point +1%
         iChanceDefense = pCity.getNaturalDefense() + pCity.getTotalDefense(0) - pCity.getDefenseDamage()

         # Per happy smile +5%
         iChanceHappiness = (pCity.happyLevel() - pCity.unhappyLevel(0)) * 2

         # Wonders: 1st +20%, 2nd +16%, 3rd +12%, 8, 4, 0
         iNumNWs = pCity.getNumNationalWonders()
         if iNumNWs < 6: iChanceNWs = iNumNWs * (11 - iNumNWs) * 2
         else: iChanceNWs = 60
         iNumWWs = pCity.getNumWorldWonders()
         if iNumWWs < 6: iChanceWWs = iNumWWs * (11 - iNumWWs) * 2
         else: iChanceWWs = 60

         # City population +5% each pop
         iChancePop = pCity.getPopulation() * 2

         # City connected with capital?
         if not pCity.isConnectedToCapital(pCity.getOwner()): iChancePop -= 10
         else: iChancePop += 10

         # bei negativ Nahrung - !
         iChancePop += pCity.foodDifference(1) * 5

         # Abstand zur Hauptstadt
         if not gc.getPlayer(pLoser.getOwner()).getCapitalCity().isNone() and gc.getPlayer(pLoser.getOwner()).getCapitalCity() != None:
           iDistance = plotDistance(gc.getPlayer(pLoser.getOwner()).getCapitalCity().getX(), gc.getPlayer(pLoser.getOwner()).getCapitalCity().getY(), pCity.getX(), pCity.getY())
         else: iDistance = 50

         # Total
         iChanceTotal = iChanceUnits + iChanceDefense + iChanceHappiness + iChanceNWs + iChanceWWs + iChancePop - iUnitAnzahl - iDistance

         # Zufallszahl
         iRand = self.myRandom(100, None)
         if iChanceTotal < 100:
           if iRand > iChanceTotal: bCityRenegade = True
           iChanceTotal = 100 - iChanceTotal
         else:
#           # there is always a chance of 1%
#           if iRand == 1: bCityRenegade = True
           iChanceTotal = 1

         iChanceTotal = int(iChanceTotal)
         # Meldung an den Spieler
         if not bCityRenegade and gc.getPlayer(pWinner.getOwner()).isHuman() and iChanceTotal > 0:
           CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_CHANCE",(pCity.getName(),iChanceTotal)), None, 2, None, ColorTypes(14), 0, 0, False, False)

         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Total",iChanceTotal)), None, 2, None, ColorTypes(10), 0, 0, False, False)
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Random",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
       # ---

       # ***TEST***
       #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("hier 1",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # Trait Protective: Staedte laufen nicht ueber / cities do not renegade
      if pCity.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")): bCityRenegade = False

      if bCityRenegade and not pCity.isNone():
        iWinner = pWinner.getOwner()
        iLoser = pLoser.getOwner()
        # Goldvergabe
        if gc.getPlayer(iLoser).getNumCities() > 0:
          iGold = int(gc.getPlayer(iLoser).getGold() / gc.getPlayer(iLoser).getNumCities())
          gc.getPlayer(iLoser).changeGold(-iGold)
          gc.getPlayer(iWinner).changeGold(iGold)
          if gc.getPlayer(iWinner).isHuman():
            CyInterface().addMessage(iWinner, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_1",("",iGold)), None, 2, None, ColorTypes(8), 0, 0, False, False)
          elif gc.getPlayer(iLoser).isHuman():
            CyInterface().addMessage(iLoser, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_2",("",iGold)), None, 2, None, ColorTypes(7), 0, 0, False, False)

        # City renegades
        self.doRenegadeCity(pCity, iWinner, pLoser.getID(), pWinner.getX(), pWinner.getY())

        pAcquiredCity = pPlot.getPlotCity()

        # Message
        if gc.getPlayer(iWinner).isHuman():
          if iWinner == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_REVOLTSTART')
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          iRand = 1 + self.myRandom(5, None)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_1_"+str(iRand),(pAcquiredCity.getName(), )))

          popupInfo.setData1(iWinner)
          popupInfo.setData2(pAcquiredCity.getID())
          popupInfo.setData3(iLoser)
          popupInfo.setOnClickedPythonCallback("popupRenegadeCity") # EntryPoints/CvScreenInterface und CvGameUtils / 706
          # Button 0: Keep
          iRand = 1 + self.myRandom(5, None)
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_KEEP_"+str(iRand),()), ",Art/Interface/Buttons/Actions/FoundCity.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,1,4")
          # Button 1: Enslave
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_ENSLAVE_1",()), ",Art/Interface/Buttons/Civics/Slavery.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,8,2")
          # Button 2: Raze
          iRand = 1 + self.myRandom(5, None)
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_RAZE_"+str(iRand),()), ",Art/Interface/Buttons/Builds/BuildCityRuins.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,8,9")
          popupInfo.addPopup(iWinner)

        elif gc.getPlayer(iLoser).isHuman():
          if iLoser == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_REVOLTSTART')
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          iRand = self.myRandom(5, None)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_2_"+str(iRand),(pAcquiredCity.getName(), )))
          popupInfo.addPopup(iLoser)


# ------- Unit gets certain promotion PAE V Beta 2 Patch 7
# ------- pPlot is also used for improvment destruction below
    if pLoser.getUnitCombatType() != -1 and not bAnimal:
      if pWinner.isMadeAttack() and gc.getPlayer(pWinner.getOwner()).isTurnActive():
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pLoser.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        self.doUnitGetsPromo(pWinner,pLoser,pLoser.plot(),true)
      else:
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pWinner.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        self.doUnitGetsPromo(pWinner,pLoser,pWinner.plot(),false)

    if not bCityRenegade and bUnitFlucht:
      self.doUnitGetsPromo(pLoser,pWinner,pLoser.plot(),false)


# +++++++++++++++++++++++++++++++++++++
    # Improvement destruction during battle / destroy imp
    # pPlot from pWinner.isAttacking() just above
    iImprovement = pPlot.getImprovementType()
    if iImprovement > -1 and not bAnimal:
     if iImprovement != gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS") and iImprovement != gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"):

      iChance = 5 # 5%

      # Get attacking unit
      if pWinner.isAttacking(): sUnit = pWinner
      else: sUnit = pLoser

      # Forts only 2%, except with catapults
      bFortress = false
      if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT") or iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT2"):
        iChance = 2
        bFortress = true

        lCatapults = []
        lCatapults.append(gc.getInfoTypeForString("UNIT_ONAGER"))
        lCatapults.append(gc.getInfoTypeForString("UNIT_CATAPULT"))
        lCatapults.append(gc.getInfoTypeForString("UNIT_FIRE_CATAPULT"))
        if sUnit.getUnitType() in lCatapults:
          iChance = 10

      #if sUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_GUN"): iChance = 15
      #elif sUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARMOR"): iChance = 20

      # Chance calculation
      if self.myRandom(100, None) < iChance:
        # message to human winner or loser
        if gc.getPlayer(pWinner.getOwner()).isHuman():
          CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT",(gc.getImprovementInfo(iImprovement).getDescription(),)), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pPlot.getX(), pPlot.getY(), True, True)
        elif gc.getPlayer(pLoser.getOwner()).isHuman():
          CyInterface().addMessage(pLoser.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT",(gc.getImprovementInfo(iImprovement).getDescription(),)), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pPlot.getX(), pPlot.getY(), True, True)
        # message to human plot owner
        else:
          iPlotOwner = pPlot.getOwner()
          if iPlotOwner > -1:
           if gc.getPlayer(iPlotOwner).isHuman():
            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_IMPROVEMENT_DESTROYED_COMBAT_PLOT_OWNER",(gc.getPlayer(pWinner.getOwner()).getName(),gc.getPlayer(pLoser.getOwner()).getName(),gc.getImprovementInfo(iImprovement).getDescription())), "AS2D_DESTROY", 2, gc.getImprovementInfo(iImprovement).getButton(), ColorTypes(13), pPlot.getX(), pPlot.getY(), True, True)

        # Destroy improvement
        if bFortress: pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"))
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_TOWN"): pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"))
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"): pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_HAMLET"))
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HAMLET"): pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"))
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"): pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"))
        else: pPlot.setImprovementType(-1)

    # Techboost for winning unit (when its technology is unknown)
    iTech = gc.getUnitInfo(pLoser.getUnitType()).getPrereqAndTech()
    pWinnerTeam = gc.getTeam(gc.getPlayer(pWinner.getOwner()).getTeam())
    if not pWinnerTeam.isHasTech(iTech):
       if gc.getPlayer(pWinner.getOwner()).canResearch(iTech, false):
          iCost = gc.getTechInfo(iTech).getResearchCost()
          iCost = iCost/100
          if iCost <= 1: iCost = 1
          else: iCost = iCost + self.myRandom(iCost, None)

          pWinnerTeam.changeResearchProgress(iTech, iCost, pWinner.getOwner())

          if gc.getPlayer(pWinner.getOwner()).isHuman():
             CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TECH_BY_UNIT",(gc.getTechInfo(iTech).getDescription(),iCost)), None, 2, None, ColorTypes(8), 0, 0, False, False)


    # Unit soll sich nachher nicht mehr fortbewegen duerfen, sofern die Einheit nicht Blitzkrieg hat
    #if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_BLITZ")):
    #  pWinner.finishMoves()


#####################################################
    # PAE Debug Mark
    #"""

    if (not self.__LOG_COMBAT):
      return
    # BTS Original
    #if playerX and playerX and unitX and playerY:
    #  CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s'
    #    %(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
    #    playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))
    # PAE Spezielle Logs wegen versteckten Einheiten (zB Piraten)
    if unitX and playerX and unitY and playerY:
      if pWinner.getInvisibleType() != -1 and pLoser.getInvisibleType() != -1:
        CvUtil.pyPrint('Hidden Unit %s has defeated hidden Unit %s' %(unitX.getDescription(), unitY.getDescription()))
      elif pWinner.getInvisibleType() != -1:
        CvUtil.pyPrint('Hidden Unit %s has defeated Player %d Civilization %s Unit %s'
          %(unitX.getDescription(), playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))
      elif pLoser.getInvisibleType() != -1:
        CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated hidden Unit %s'
          %(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(), unitY.getDescription()))
      else:
        CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s'
          %(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
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
    global gCombatMessages, gCombatLog
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

    if (iIsAttacker == 0):
      combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szDefenderName, cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
      CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
      CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
      if (cdDefender.iCurrHitPoints <= 0):
        combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szAttackerName, cdAttacker.sUnitName, szDefenderName, cdDefender.sUnitName))
        CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    elif (iIsAttacker == 1):
      combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szAttackerName, cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
      CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
      CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
      if (cdAttacker.iCurrHitPoints <= 0):
        combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szDefenderName, cdDefender.sUnitName, szAttackerName, cdAttacker.sUnitName))
        CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
        CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

    # PAE Wegen Bekanntgabe der Piraten im Log wird hier auskommentiert!
    #if (iIsAttacker == 0):
    #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
    #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #  if (cdDefender.iCurrHitPoints <= 0):
    #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName))
    #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #elif (iIsAttacker == 1):
    #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
    #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #  if (cdAttacker.iCurrHitPoints <= 0):
    #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName))
    #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

  def onImprovementBuilt(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Improvement Built'
    iImprovement, iX, iY = argsList

    if iImprovement in (-1, gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"), gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")):
      return

    # PAE: Weiler: Dichter Wald -> Wald
    if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HAMLET") \
    or iImprovement == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"):
      pPlot = gc.getMap().plot(iX, iY)
      if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
         pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"),1)
    elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
      pPlot = gc.getMap().plot(iX, iY)
      if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
         pPlot.setFeatureType(-1,0)

    if (not self.__LOG_IMPROVEMENT):
      return
    CvUtil.pyPrint('Improvement %s was built at %d, %d'
      %(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

  def onImprovementDestroyed(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Improvement Destroyed'
    iImprovement, iOwner, iX, iY = argsList

    if iImprovement in (-1, gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"), gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")):
      return

    if (not self.__LOG_IMPROVEMENT):
      return
    CvUtil.pyPrint('Improvement %s was Destroyed at %d, %d'
      %(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

  def onRouteBuilt(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Route Built'
    iRoute, iX, iY = argsList
    if (not self.__LOG_IMPROVEMENT):
      return
    CvUtil.pyPrint('Route %s was built at %d, %d'
      %(gc.getRouteInfo(iRoute).getDescription(), iX, iY))

  def onPlotRevealed(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Plot Revealed'
    pPlot = argsList[0]
    iTeam = argsList[1]

  def onPlotFeatureRemoved(self, argsList):
    'Plot Revealed'
    pPlot = argsList[0]
    iFeatureType = argsList[1]
    pCity = argsList[2] # This can be null

  def onPlotPicked(self, argsList):
    'Plot Picked'
    pPlot = argsList[0]
    CvUtil.pyPrint('Plot was picked at %d, %d'
      %(pPlot.getX(), pPlot.getY()))

  def onNukeExplosion(self, argsList):
    'Nuke Explosion'
    pPlot, pNukeUnit = argsList
    CvUtil.pyPrint('Nuke detonated at %d, %d'
      %(pPlot.getX(), pPlot.getY()))

  def onGotoPlotSet(self, argsList):
    'Nuke Explosion'
    pPlot, iPlayer = argsList

  #global
  def onBuildingBuilt(self, argsList):
    'Building Completed'
    pCity, iBuildingType = argsList
    game = gc.getGame()

    # PAE Debug Mark
    #"""
#    #If this is a wonder...
#    if not gc.getGame().isNetworkMultiPlayer() and gc.getPlayer(pCity.getOwner()).isHuman() and isWorldWonderClass(gc.getBuildingInfo(iBuildingType).getBuildingClassType()):
    if gc.getPlayer(pCity.getOwner()).isHuman() and gc.getBuildingInfo(iBuildingType).getMovieDefineTag() != "NONE":
  ## Platy WorldBuilder ##
      if not CyGame().GetWorldBuilderMode():
  ## Platy WorldBuilder ##
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
        popupInfo.setData1(iBuildingType)
        popupInfo.setData2(pCity.getID())
        popupInfo.setData3(0)
        popupInfo.setText(u"showWonderMovie")
        popupInfo.addPopup(pCity.getOwner())

    # Kolonie / Provinz ----------
    # Wenn der Palast neu erbaut wird
    if iBuildingType == gc.getInfoTypeForString("BUILDING_PALACE"):
      #iBuildingKolonie = gc.getInfoTypeForString('BUILDING_KOLONIE')
      #iBuildingProvinz = gc.getInfoTypeForString('BUILDING_PROVINZ')
      iBuildingProvinzpalast = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
      #pCity.setNumRealBuilding(iBuildingKolonie,0)
      #pCity.setNumRealBuilding(iBuildingProvinz,0)
      pCity.setNumRealBuilding(iBuildingProvinzpalast,0)
    # ----------------------------
      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palast erbaut (Zeile 2206)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Der Apostolische Palast verlegt das Zentrum des Christentums (doch nicht, er soll nur den +1 Kommerzbonus fuer jede christl. Stadt haben (XML))
    #if iBuildingType == gc.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE"):
    #  iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
    #  pHolyCity = gc.getGame().getHolyCity(iReligion)
    #  if pHolyCity.getID() != pCity.getID():
    #     # Geburstkirche soll bleiben falls schon dort errichtet
    #     # Religionszentrum verlegen:
    #     gc.getGame().getHolyCity(iReligion).setHasReligion(iReligion,0,0,0)
    #     gc.getGame().setHolyCity(iReligion, pCity, 0)

    # Kanalisation -> Suempfe werden rund um der Stadt entfernt (Sumpf/Swamps)
    # Oder Deich, Damm, Levee, Kanal
    iBuilding  = gc.getInfoTypeForString('BUILDING_SANITATION')
    #iBuilding2 = gc.getInfoTypeForString('BUILDING_LEVEE')
    iBuilding3 = gc.getInfoTypeForString('BUILDING_LEVEE2')
    if iBuildingType == iBuilding or iBuildingType == iBuilding3:
      bFeatSwamp = False
      feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
      for i in range(3):
        for j in range(3):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
          if None != loopPlot and not loopPlot.isNone() and loopPlot.getFeatureType() == feat_swamp:
            loopPlot = loopPlot.setFeatureType(-1,0)
            bFeatSwamp = True
      if bFeatSwamp == True and gc.getPlayer(pCity.getOwner()).isHuman():
        if iBuildingType == iBuilding:
          CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SANITATION_BUILT",(pCity.getName(),)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        #elif iBuildingType == iBuilding2:
        #  CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_LEVEE_BUILT",(pCity.getName(),)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        elif iBuildingType == iBuilding3:
          CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_LEVEE2_BUILT",(pCity.getName(),)), None, 2, None, ColorTypes(14), 0, 0, False, False)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sumpf wird entfernt (Zeile 2232)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # WEIN - FEATURE ---------------------
    # Winzer / Vintager -> Winery / Weinverbreitung
    iBuilding = gc.getInfoTypeForString('BUILDING_WINERY')
    if iBuildingType == iBuilding and self.myRandom(2, None) == 1:
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      bonus_grapes = gc.getInfoTypeForString('BONUS_GRAPES')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_WATERMILL")
      iImpType5 = gc.getInfoTypeForString("IMPROVEMENT_FARM")
      iImpType6 = gc.getInfoTypeForString("IMPROVEMENT_MINE")
      iImpType7 = gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")

      PlotPrio1 = []
      PlotPrio2 = []
      PlotPrio3 = []
      PlotPrio4 = []
      PlotPrio5 = []
      PlotPrio6 = []
      PlotPrio7 = []
      PlotPrio8 = []
      PlotPrio9 = []
      PlotPrio10 = []
      PlotPrio11 = []
      correctPlotArray = []
      setWinery = True

      # wenn bereits eine Weinressource im nahen (5x5-Feld) Umkreis der Stadt ist
      for i in range(5):

        if not setWinery: break

        for j in range(5):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)
          if loopPlot.getBonusType(-1) == bonus_grapes and not (i==0 and j==0) and not (i==4 and j==0) and not (i==0 and j==4) and not (i==4 and j==4):
            setWinery = False
            break

          # die beste position finden:
          if loopPlot != None and not loopPlot.isNone() and not (i==0 and j==0) and not (i==4 and j==0) and not (i==0 and j==4) and not (i==4 and j==4):
           # auf grass oder plain, nicht auf Sumpf oder Schwemmland, Berg oder einer anderen Bonusresi
           if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak():
            if loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

             # Moeglichkeit: Stadtplot (nach Farm und vor Mine)
             if loopPlot.isCity(): PlotPrio4.append(loopPlot)
             else:
              # 1. plain and hills, unworked
              if loopPlot.getTerrainType() == terr_plain and loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio1.append(loopPlot)
              # 2. grass and hills, unworked
              if loopPlot.getTerrainType() == terr_grass and loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio2.append(loopPlot)
              # 3. irgendeinen passenden ohne Improvement
              if loopPlot.getImprovementType() == -1: PlotPrio3.append(loopPlot)
              # 4. nach Improvements selektieren
              if loopPlot.getImprovementType() == iImpType1: PlotPrio5.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType2: PlotPrio6.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType3: PlotPrio7.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType4: PlotPrio8.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType5: PlotPrio9.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType6: PlotPrio10.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType7: PlotPrio11.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7
      elif len(PlotPrio8) > 0: correctPlotArray = PlotPrio8
      elif len(PlotPrio9) > 0: correctPlotArray = PlotPrio9
      #elif len(PlotPrio4) > 0: correctPlotArray = PlotPrio4 # Stadt doch nicht
      elif len(PlotPrio10) > 0: correctPlotArray = PlotPrio10
      elif len(PlotPrio11) > 0: correctPlotArray = PlotPrio11

      # Wein setzen
      if setWinery and len(correctPlotArray) > 0:
        iPlot = self.myRandom(len(correctPlotArray), None)
        sPlot = correctPlotArray[iPlot]
        # Feature (Wald) entfernen
        sPlot.setFeatureType(-1,0)
        # Bonus Wein adden
        sPlot.setBonusType(bonus_grapes)
        # Improvement adden
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_WINERY')
        sPlot.setImprovementType(iImprovement)

        if gc.getPlayer(pCity.getOwner()).isHuman():
          iRand = 1 + self.myRandom(4, None)
          CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_VINTAGER_BUILT"+str(iRand),(pCity.getName(),)), None, 2, gc.getBonusInfo(bonus_grapes).getButton(), ColorTypes(8), sPlot.getX(), sPlot.getY(), True, True)


        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Wein wird angebaut (Zeile 2288)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    # WEIN - FEATURE - ENDE ---------------------

    # HORSE - FEATURE ---------------------
    # Pferdeverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_PFERDEZUCHT'):
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      iBonus = gc.getInfoTypeForString('BONUS_HORSE')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_WATERMILL")
      iImpType5 = gc.getInfoTypeForString("IMPROVEMENT_FARM")
      iImpType6 = gc.getInfoTypeForString("IMPROVEMENT_MINE")
      iImpType7 = gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")

      PlotPrio1 = []
      PlotPrio2 = []
      PlotPrio3 = []
      PlotPrio4 = []
      PlotPrio5 = []
      PlotPrio6 = []
      PlotPrio7 = []
      PlotPrio8 = []
      PlotPrio9 = []
      PlotPrio10 = []
      PlotPrio11 = []
      correctPlotArray = []

      for i in range(5):
        for j in range(5):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)

          # die beste position finden:
          if loopPlot != None and not loopPlot.isNone() and not (i==0 and j==0) and not (i==4 and j==0) and not (i==0 and j==4) and not (i==4 and j==4):
            # auf grass oder plain, nicht auf Sumpf oder Schwemmland, Berg oder einer anderen Bonusresi
            if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

             # Moeglichkeit: Stadtplot (nach Farm und vor Mine)
             if loopPlot.isCity(): PlotPrio4.append(loopPlot)
             else:
              # 1. plain and hills, unworked
              if loopPlot.getTerrainType() == terr_plain and not loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio1.append(loopPlot)
              # 2. grass and hills, unworked
              if loopPlot.getTerrainType() == terr_grass and not loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio2.append(loopPlot)
              # 3. irgendeinen passenden ohne Improvement
              if loopPlot.getImprovementType() == -1: PlotPrio3.append(loopPlot)
              # 4. nach Improvements selektieren
              if loopPlot.getImprovementType() == iImpType1: PlotPrio5.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType2: PlotPrio6.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType3: PlotPrio7.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType4: PlotPrio8.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType5: PlotPrio9.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType6: PlotPrio10.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType7: PlotPrio11.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7
      elif len(PlotPrio8) > 0: correctPlotArray = PlotPrio8
      elif len(PlotPrio9) > 0: correctPlotArray = PlotPrio9
      #elif len(PlotPrio4) > 0: correctPlotArray = PlotPrio4 # Stadt doch nicht
      elif len(PlotPrio10) > 0: correctPlotArray = PlotPrio10
      elif len(PlotPrio11) > 0: correctPlotArray = PlotPrio11

      # Bonus setzen
      if len(correctPlotArray) > 0:
        iPlot = self.myRandom(len(correctPlotArray), None)
        sPlot = correctPlotArray[iPlot]
        # Feature (Wald) entfernen
        sPlot.setFeatureType(-1,0)
        # Bonus adden
        sPlot.setBonusType(iBonus)
        # Improvement adden
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_PASTURE')
        sPlot.setImprovementType(iImprovement)

    # HORSE - FEATURE - ENDE ---------------------

    # HUNDE - FEATURE ---------------------
    # Hundeverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_HUNDEZUCHT'):
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      iBonus = gc.getInfoTypeForString('BONUS_HUNDE')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_WATERMILL")
      iImpType5 = gc.getInfoTypeForString("IMPROVEMENT_FARM")
      iImpType6 = gc.getInfoTypeForString("IMPROVEMENT_MINE")
      iImpType7 = gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")

      PlotPrio1 = []
      PlotPrio2 = []
      PlotPrio3 = []
      PlotPrio4 = []
      PlotPrio5 = []
      PlotPrio6 = []
      PlotPrio7 = []
      PlotPrio8 = []
      PlotPrio9 = []
      PlotPrio10 = []
      PlotPrio11 = []
      correctPlotArray = []

      for i in range(5):
        for j in range(5):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)

          # die beste position finden:
          if loopPlot != None and not loopPlot.isNone() and not (i==0 and j==0) and not (i==4 and j==0) and not (i==0 and j==4) and not (i==4 and j==4):
            # auf grass oder plain, nicht auf Sumpf oder Schwemmland, Berg oder einer anderen Bonusresi
            if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

             # Moeglichkeit: Stadtplot (nach Farm und vor Mine)
             if loopPlot.isCity(): PlotPrio4.append(loopPlot)
             else:
              # 1. plain and hills, unworked
              if loopPlot.getTerrainType() == terr_plain and not loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio1.append(loopPlot)
              # 2. grass and hills, unworked
              if loopPlot.getTerrainType() == terr_grass and not loopPlot.isHills() and loopPlot.getImprovementType() == -1: PlotPrio2.append(loopPlot)
              # 3. irgendeinen passenden ohne Improvement
              if loopPlot.getImprovementType() == -1: PlotPrio3.append(loopPlot)
              # 4. nach Improvements selektieren
              if loopPlot.getImprovementType() == iImpType1: PlotPrio5.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType2: PlotPrio6.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType3: PlotPrio7.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType4: PlotPrio8.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType5: PlotPrio9.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType6: PlotPrio10.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType7: PlotPrio11.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7
      elif len(PlotPrio8) > 0: correctPlotArray = PlotPrio8
      elif len(PlotPrio9) > 0: correctPlotArray = PlotPrio9
      #elif len(PlotPrio4) > 0: correctPlotArray = PlotPrio4 # Stadt doch nicht
      elif len(PlotPrio10) > 0: correctPlotArray = PlotPrio10
      elif len(PlotPrio11) > 0: correctPlotArray = PlotPrio11

      # Bonus setzen
      if len(correctPlotArray) > 0:
        iPlot = self.myRandom(len(correctPlotArray), None)
        sPlot = correctPlotArray[iPlot]
        # Feature (Wald) entfernen
        #sPlot.setFeatureType(-1,0)
        # Bonus adden
        sPlot.setBonusType(iBonus)
        # Improvement adden
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_CAMP')
        sPlot.setImprovementType(iImprovement)

    # HUNDE - FEATURE - ENDE ---------------------

    # Warft (ein Huegel entsteht)
    iBuilding = gc.getInfoTypeForString('BUILDING_WARFT')
    if iBuildingType == iBuilding:
      pPlot = CyMap().plot(pCity.getX(), pCity.getY())
      pPlot.setPlotType(PlotTypes.PLOT_HILLS,True,True)

    # Wonder: Tower of Babel => increasing Sympathy for all well-known AIs by +4
    iBuilding = gc.getInfoTypeForString('BUILDING_BABEL')
    if iBuildingType == iBuilding:
      pPlayer = gc.getPlayer(pCity.getOwner())
      iPlayer = pPlayer.getID()
      iRange = gc.getMAX_PLAYERS()
      for iPlayer2 in range(iRange):
        pSecondPlayer = gc.getPlayer(iPlayer2)
        iSecondPlayer = pSecondPlayer.getID( )
        iSecTeam = pSecondPlayer.getTeam()
        if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
          pSecondPlayer.AI_changeAttitudeExtra(iPlayer,+4)

    # Wonder: 10 Gebote => adds 1 prophet and 4 jewish missionaries
    iBuilding = gc.getInfoTypeForString('BUILDING_10GEBOTE')
    if iBuildingType == iBuilding:
      pPlayer = gc.getPlayer(pCity.getOwner())
      iUnitType = gc.getInfoTypeForString("UNIT_PROPHET")
      NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_PROPHET, DirectionTypes.DIRECTION_SOUTH)
      NewUnit.setName("Moses")
      iUnitType = gc.getInfoTypeForString("UNIT_JEWISH_MISSIONARY")
      Names = ["Sarah","Abraham","Isaak","Jakob","Pinchas","Aaron","Miriam","Josua","Bileam","Jesaja"]
      for i in range(10):
        NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.setName(Names[i])

    # PAE Debug Mark
    #"""

    CvAdvisorUtils.buildingBuiltFeats(pCity, iBuildingType)

    if (not self.__LOG_BUILDING):
      return
    CvUtil.pyPrint('%s was finished by Player %d Civilization %s'
      %(PyInfo.BuildingInfo(iBuildingType).getDescription(), pCity.getOwner(), gc.getPlayer(pCity.getOwner()).getCivilizationDescription(0)))

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
      if gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_QUICK"): iGold = 200 # Speed: 50%
      elif gc.getGame().getGameSpeedType() == gc.getInfoTypeForString("GAMESPEED_MARATHON"): iGold = 600 # Speed: 150%

      pPlayer.changeGold(iGold)
      if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')
      if pPlayer.isHuman():
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_PROJECT_SEIDENSTRASSE",(iGold,)))
        popupInfo.addPopup(iPlayer)

      # Add Trade Route to city 26.01.2013
      pCity.changeExtraTradeRoutes(1)

    # Project : Bibel
    # Wonder: Bible => adds 12 christian missionaries
    if iProjectType == gc.getInfoTypeForString("PROJECT_BIBEL"):
      pPlayer = gc.getPlayer(pCity.getOwner())
      iUnitType = gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY")
      Names = ["Petrus","Andreas","Jakobus","Johannes","Philippus","Bartholomaeus","Thomas","Matthaeus","Jakobus","Thaddaeus","Simon","Judas"]
      for i in range(12):
        NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.setName(Names[i])

  def onSelectionGroupPushMission(self, argsList):
    'selection group mission'
    eOwner = argsList[0]
    eMission = argsList[1]
    iNumUnits = argsList[2]
    listUnitIds = argsList[3]

    # Handel (nur Meldung mit der gewonnenen Geldsumme)
    if eMission == MissionTypes.MISSION_TRADE:
      if gc.getPlayer(eOwner).isHuman():
        pUnit = gc.getPlayer(eOwner).getUnit(listUnitIds[0])
        if pUnit.canMove():
          if eOwner == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
          pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())
          pCity = pPlot.getPlotCity()
          iProfit = pUnit.getTradeGold(pPlot)
          CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_AUTOMATE_MERCHANT_DONE",(pCity.getName(),iProfit)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Fernangriff
    # Nur 1x Fernangriff danach nur bewegen => GlobalDefines RANGED_ATTACKS_USE_MOVES=0
    if eMission == MissionTypes.MISSION_RANGE_ATTACK:
      pPlayer = gc.getPlayer(eOwner)

      lSkirmishType = []
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_BALEAREN"))
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_BAKTRIEN"))
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_THRAKIEN_PELTAST"))
      lSkirmishClass = []
      lSkirmishClass.append(gc.getInfoTypeForString("UNITCLASS_PELTIST"))
      lSkirmishClass.append(gc.getInfoTypeForString("UNITCLASS_SKIRMISHER"))
      lSkirmishClass.append(gc.getInfoTypeForString("UNITCLASS_CHARIOT_ARCHER"))
      lSkirmishClass.append(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER"))
      lSkirmishClass.append(gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER"))

      lUnits = []
      for i in listUnitIds:
        unit = pPlayer.getUnit(i)
        if unit.isRanged():
           # Liste fuer Kosten
           lUnits.append(unit)

           # Nicht fuer Plaenklereinheiten
           if unit.getUnitType() not in lSkirmishType and unit.getUnitClassType() not in lSkirmishClass:
             if unit.getGroup().hasMoved():
               unit.finishMoves()
           # Oder nur wenn sich die Einheit bereits bewegt hatte? Oder beides?
           #if unit.getGroup().hasMoved():
           #   unit.finishMoves()

      # Fernangriff kostet nur der HI Gold
      if pPlayer.isHuman() and len(lUnits) > 0:

        lCivsNoCosts = []
        lCivsNoCosts.append(gc.getInfoTypeForString("CIVILIZATION_BERBER"))
        lCivsNoCosts.append(gc.getInfoTypeForString("CIVILIZATION_HUNNEN"))
        lCivsNoCosts.append(gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"))

        if pPlayer.getCivilizationType() not in lCivsNoCosts:

          iGold = 0
          for unit in lUnits:
            iUnitType = unit.getUnitType()
            iUnitClass = unit.getUnitClassType()
            iUnitCombat = unit.getUnitCombatType()

            # Individuelle Kosten fuer iAirRange-Units
            #if iUnitClass == gc.getInfoTypeForString("UNITCLASS_HUNTER"): iGold += 1
            if iUnitClass == gc.getInfoTypeForString("UNITCLASS_LIGHT_ARCHER"): iGold += 1
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_ARCHER") or iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_GILDE"): iGold += 3
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_COMPOSITE_ARCHER") or iUnitType == gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER_GILDE") or iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_KRETA"): iGold += 4
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER") or iUnitClass == gc.getInfoTypeForString("UNITCLASS_ARCHER_LEGION"): iGold += 5
            elif iUnitType == gc.getInfoTypeForString("UNIT_INDIAN_LONGBOW") or iUnitType == gc.getInfoTypeForString("UNIT_LIBYAN_AMAZON"): iGold += 5
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_PELTIST") or iUnitType == gc.getInfoTypeForString("UNIT_BALEAREN"): iGold += 4
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_SKIRMISHER"): iGold += 5
            elif iUnitType == gc.getInfoTypeForString("UNIT_THRAKIEN_PELTAST"): iGold += 5
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_CHARIOT_ARCHER") or iUnitType == gc.getInfoTypeForString("UNIT_HETHIT_WARCHARIOT"): iGold += 4
            elif iUnitType == gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS") or iUnitType == gc.getInfoTypeForString("UNIT_BAKTRIEN"): iGold += 5
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER") or iUnitClass == gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER"): iGold += 5
            elif iUnitType == gc.getInfoTypeForString("UNIT_BALLISTA"): iGold += 5
            elif iUnitCombat == gc.getInfoTypeForString("UNITCOMBAT_SIEGE"): iGold += 4
            elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_DECAREME"): iGold += 6

          if iGold > 0:
             pPlayer.changeGold(-iGold)
             CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_RANGE_ATTACK_COSTS",(iGold,)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Ranged Attack - Owner",eOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      #(unit, iter) = pPlayer.firstUnit(false)
      #(unit, iter) = pPlayer.nextUnit(iter, false)


    # Wenn die Mission nicht ausgefuehrt werden soll
    #unit.getGroup().clearMissionQueue()


    #unit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, unit.plot(), unit)


    #if eMission == MissionTypes.MISSION_BOMBARD:
    #  CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Bombard - Owner",eOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    if (not self.__LOG_PUSH_MISSION):
      return
    else:
      CvUtil.pyPrint("Selection Group pushed mission %d" %(eMission))

  def onUnitMove(self, argsList):
    'unit move'
    pPlot,pUnit,pOldPlot = argsList

    # PAE Debug mark
    #"""
#    if gc.getPlayer(pUnit.getOwner()).isHuman():
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("X",pPlot.getX())), None, 2, None, ColorTypes(10), 0, 0, False, False)
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Y",pPlot.getY())), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ----------- Flucht Promotion (Flight/Escape)
    if not pUnit.canMove() or pUnit.getDamage() < 70:
      pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"), False)
      #iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT")
      #if pUnit.isHasPromotion(iFormation): pUnit.setHasPromotion(iFormation, False)



# ----------- Verletzte Schiffe / Seeeinheiten sollen langsamer werden, je verletzter sie sind
# ----------- Beladene Schiffe sollen ebenfalls um 0.5 langsamer werden
# ----------- Bewegung / Movement / Seewind / Fair wind
    if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA:

      # ------ Seewind -----
      if pPlot.getFeatureType() > -1:
        feat_wind_n = gc.getInfoTypeForString("FEATURE_WIND_N")
        feat_wind_e = gc.getInfoTypeForString("FEATURE_WIND_E")
        feat_wind_s = gc.getInfoTypeForString("FEATURE_WIND_S")
        feat_wind_w = gc.getInfoTypeForString("FEATURE_WIND_W")
        feat_wind_ne = gc.getInfoTypeForString("FEATURE_WIND_NE")
        feat_wind_nw = gc.getInfoTypeForString("FEATURE_WIND_NW")
        feat_wind_se = gc.getInfoTypeForString("FEATURE_WIND_SE")
        feat_wind_sw = gc.getInfoTypeForString("FEATURE_WIND_SW")
        lSeewind = [feat_wind_n,feat_wind_e,feat_wind_s,feat_wind_w,feat_wind_ne,feat_wind_nw,feat_wind_se,feat_wind_sw]
        iPlotWind = pPlot.getFeatureType()
        if iPlotWind in lSeewind:

          iUnitDirection = pUnit.getFacingDirection()

          # 1 plot move = 60
          # Ocean movement and feature movement cost = 1
          # +1 Bewegung in Wind,...
          iInWind = -60
          iInSchraegWind = -30
          iSeitenWind = 0
          iGegenSchraegWind = 30
          iGegenWind = 60

          if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION3")):
            iInWind = -60
            iInSchraegWind = -60
            iSeitenWind = -30
            iGegenSchraegWind = 0
            iGegenWind = 30
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION2")):
            iInWind = -60
            iInSchraegWind = -30
            iSeitenWind = -30
            iGegenSchraegWind = 0
            iGegenWind = 30
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION1")):
            iInWind = -60
            iInSchraegWind = -30
            iSeitenWind = -30
            iGegenSchraegWind = 30
            iGegenWind = 60

          # Bewegung nach Norden
          if iUnitDirection == 0:
            if   iPlotWind == feat_wind_n: pUnit.changeMoves(iGegenWind)
            elif iPlotWind == feat_wind_ne or iPlotWind == feat_wind_nw: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_e or iPlotWind == feat_wind_w: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_se or iPlotWind == feat_wind_sw: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_s: pUnit.changeMoves(iInWind)
          # Bewegung nach Sueden
          elif iUnitDirection == 4:
            if   iPlotWind == feat_wind_n: pUnit.changeMoves(iInWind)
            elif iPlotWind == feat_wind_ne or iPlotWind == feat_wind_nw: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_e or iPlotWind == feat_wind_w: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_se or iPlotWind == feat_wind_sw: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_s: pUnit.changeMoves(iGegenWind)
          # Bewegung nach Osten
          elif iUnitDirection == 2:
            if   iPlotWind == feat_wind_e: pUnit.changeMoves(iGegenWind)
            elif iPlotWind == feat_wind_ne or iPlotWind == feat_wind_se: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_s: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_nw or iPlotWind == feat_wind_sw: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_w: pUnit.changeMoves(iInWind)
          # Bewegung nach Westen
          elif iUnitDirection == 6:
            if   iPlotWind == feat_wind_e: pUnit.changeMoves(iInWind)
            elif iPlotWind == feat_wind_ne or iPlotWind == feat_wind_se: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_s: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_nw or iPlotWind == feat_wind_sw: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_w: pUnit.changeMoves(iGegenWind)
          # Bewegung nach Nordosten
          elif iUnitDirection == 1:
            if   iPlotWind == feat_wind_ne: pUnit.changeMoves(iGegenWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_e: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_nw or iPlotWind == feat_wind_se: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_w or iPlotWind == feat_wind_s: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_sw: pUnit.changeMoves(iInWind)
          # Bewegung nach Suedwesten
          elif iUnitDirection == 5:
            if   iPlotWind == feat_wind_ne: pUnit.changeMoves(iInWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_e: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_nw or iPlotWind == feat_wind_se: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_w or iPlotWind == feat_wind_s: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_sw: pUnit.changeMoves(iGegenWind)
          # Bewegung nach Nordwesten
          elif iUnitDirection == 7:
            if   iPlotWind == feat_wind_nw: pUnit.changeMoves(iGegenWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_w: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_sw or iPlotWind == feat_wind_ne: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_e or iPlotWind == feat_wind_s: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_se: pUnit.changeMoves(iInWind)
          # Bewegung nach Suedosten
          elif iUnitDirection == 3:
            if   iPlotWind == feat_wind_nw: pUnit.changeMoves(iInWind)
            elif iPlotWind == feat_wind_n or iPlotWind == feat_wind_w: pUnit.changeMoves(iInSchraegWind)
            elif iPlotWind == feat_wind_sw or iPlotWind == feat_wind_ne: pUnit.changeMoves(iSeitenWind)
            elif iPlotWind == feat_wind_e or iPlotWind == feat_wind_s: pUnit.changeMoves(iGegenSchraegWind)
            elif iPlotWind == feat_wind_se: pUnit.changeMoves(iGegenWind)

          # Alt: bis PAE IV: Unit (Group only) soll sich auf ein bestimmtes Feld bewegen
          #if loopPlot != None and not loopPlot.isNone():
          #  pSelectionGroup = pUnit.getGroup()
          #  pSelectionGroup.pushMoveToMission(loopPlot.getX(), loopPlot.getY())

      # -- end Wind

      # ------ Verletzte Schiffe
      iDamage = pUnit.getDamage()
      if iDamage > 10: pUnit.changeMoves(iDamage*3)
      # Beladene Schiffe
      #iCargoSpace = pUnit.cargoSpace()
      iCargo = pUnit.getCargo()
      if iCargo > 0: pUnit.changeMoves(iCargo*20)

      # Workboats sink in unknown terrain (neutral or from other team): Chance 1:6
      if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_WORKBOAT"):
        if pPlot.getOwner() != pUnit.getOwner():
          if 1 == self.myRandom(6, None):
            if gc.getPlayer(pUnit.getOwner()).isHuman():
              CyInterface().addMessage(pUnit.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SINKING_SHIP",(pUnit.getName(),)), "AS2D_SINKING_W0RKBOAT", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
            pUnit.kill(1,pUnit.getOwner())
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
          if 1 == self.myRandom(iChance, None):

            iDamage += iSchaden
            pUnit.setDamage(iDamage, -1)

            # Types of Damage (Messages)
            # 0 = Storm
            iRand = self.myRandom(6, None)
            if iRand == 0:
              pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_SEESTURM"),0)
              if gc.getPlayer(pUnit.getOwner()).isHuman():
                CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DAMAGE_SHIP_STORM",(pUnit.getName(),iSchaden)), "AS2D_UNIT_BUILD_GALLEY", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            elif gc.getPlayer(pUnit.getOwner()).isHuman():
              CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DAMAGE_SHIP_"+str(iRand),(pUnit.getName(),iSchaden)), "AS2D_UNIT_BUILD_GALLEY", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

# ----------- A Unit get damage during movement ------------------------------- #
#    iCulture = pPlot.getCulture(pUnit.getOwner())
#    if iCulture == 0 and pUnit.canAttack():
#      # Verzweigte if-statements, zwecks runtime
#      if pUnit.getDomainType() == DomainTypes.DOMAIN_LAND and not pUnit.isAnimal() and not pUnit.isBarbarian():
#        # Erst ab einem Stack von mind. 20 Einheiten
#        if pPlot.getNumUnits() + pOldPlot.getNumUnits() > 19 and pUnit.getDamage() < 90:
#
#          noDamage = False
#
#          # Wenn das Gebiet einem Vasallen gehoert
#          iCultureOwner  = pPlot.getOwner()
#          iCultureOwner2 = pUnit.getOwner()
#          if iCultureOwner != -1:
#            if gc.getTeam(iCultureOwner).isVassal(gc.getTeam(gc.getPlayer(iCultureOwner2).getTeam()).getID()) or gc.getTeam(iCultureOwner2).isVassal(gc.getTeam(gc.getPlayer(iCultureOwner).getTeam()).getID()): noDamage = True
#
#          if not noDamage:
#
#            # Pruefen, ob es einen Versorgungszug auf dem Plot gibt
#            iHealChange = 1
#            SupplyUnit = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
#            for iUnit in range (pOldPlot.getNumUnits()):
#              if pPlot.getUnit(iUnit).getUnitType() == SupplyUnit:
#                iHealChange = 2
#                break
#            # wenn im alten Plot kein Versorgungswagen da war, dann zaehlt auch einer im neuen plot
#            if iHealChange == 1:
#              for iUnit in range (pPlot.getNumUnits()):
#                if pPlot.getUnit(iUnit).getUnitType() == SupplyUnit:
#                  iHealChange = 2
#                  break
#
#            if pUnit.maxMoves() > 60:
#              uDamageRoad = int(1 / iHealChange)
#              uDamage = int(3 / iHealChange)
#            else:
#              uDamageRoad = int(2 / iHealChange)
#              uDamage = int(6 / iHealChange)
#
#            if pPlot.isRoute():
#              pUnit.changeDamage(uDamageRoad, False)
#            else:
#              pUnit.changeDamage(uDamage, False)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Einheit wird durch Bewegung verletzt (Zeile 2444)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# --------------------------------------------------------------------- #


# ------ BARBAREN ------------------------------------------------- #
    if pUnit.isBarbarian():
      # Seevoelkereinheit wird entladen, leere Seevoelkerschiffe werden gekillt
      if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SEEVOLK"):
        if not pUnit.hasCargo():
          #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
          pUnit.kill(1,pUnit.getOwner())
          return
          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Leeres Seevoelkerschiff gekillt (Zeile 2456)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        else:
          if pOldPlot.getOwner() == -1 and pPlot.getOwner() > -1:
            if gc.getPlayer(pPlot.getOwner()).isHuman():
              CyInterface().addMessage(pPlot.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SEEVOLK_ALERT",()), None, 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)


#    if pUnit.isBarbarian():
#      if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_SEEVOLK'):#
#       if not pUnit.hasCargo():
#        pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
#       else:
#        # Sollen die Einheiten ausgeladen werden? ja: 20%
#        iRand = self.myRandom(10, "Random number of unload sea peoples")
#        if iRand < 2:

         # Einen guenstigen Plot auswaehlen
#         rebelPlotArray = []
#         for i in range(3):
#          for j in range(3):
#           loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 1)
#           if None != loopPlot and not loopPlot.isNone():
#            if loopPlot.isOwned() and loopPlot.getOwner() != gc.getBARBARIAN_PLAYER() and not (loopPlot.isUnit() or loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()):
#             rebelPlotArray.append(loopPlot)

         # Es wurde ein Plot gefunden
#         if len(rebelPlotArray) > 0:
#          iPlot = self.myRandom(len(rebelPlotArray), "Sea Peoples placement")

          # Kleine Inseln nicht angreifen
#          iPlots=0
#          for i in range(3):
#            for j in range(3):
#              loopPlot = gc.getMap().plot(rebelPlotArray[iPlot].getX() + i - 1, rebelPlotArray[iPlot].getY() + j - 1)
#              if loopPlot != None and not loopPlot.isNone():
#                if not loopPlot.isWater(): iPlots += 1

          # Die Einheit kann ausgeladen werden
#          if iPlots > 3:
#           for iUnit in range (pPlot.getNumUnits()):
#            if pPlot.getUnit(iUnit).getDomainType() == DomainTypes.DOMAIN_LAND:
#             #pPlot.getUnit(iUnit).jumpToNearestValidPlot()
#             pPlot.getUnit(iUnit).setXY(rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(),1,0,1)
# -----------------
      # Barbarische Tiere sollen keine Stadt betreten / Barbarian animals will be disbanded when moving into a city
      if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
        if pPlot.isCity():
          #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
          pUnit.kill(1,pUnit.getOwner())

# --------------------------------------------------------------------- #

    # Merchant can be robbed and killed
    if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT") and not pUnit.isBarbarian():
      if pPlot.getNumUnits() == 1 and pUnit.getOwner() != pPlot.getOwner() and not pPlot.isCity():

        barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
        iBarbCities = barbPlayer.getNumCities()
        if iBarbCities > 10: iChance = 25  # 4%
        elif iBarbCities > 4: iChance = 33 # 3%
        else: iChance = 50 # 2%

        iRand = self.myRandom(iChance, None)
        if iRand < 1:
          iPlayer = pUnit.getOwner()
          if gc.getPlayer(iPlayer).isHuman():
            iRand = self.myRandom(5, None)
            if iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_1",(0,0))
            elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_2",(0,0))
            elif iRand == 3: text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_3",(0,0))
            elif iRand == 4: text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_4",(0,0))
            else: text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_0",(0,0))
            CyInterface().addMessage(iPlayer, True, 5, text, 'AS2D_UNITCAPTURE', 2, 'Art/Interface/Buttons/Units/button_merchant.dds', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
          elif pPlot.getOwner() != -1:
            if gc.getPlayer(pPlot.getOwner()).isHuman():
              CyInterface().addMessage(pPlot.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_1_1",(gc.getPlayer(pUnit.getOwner()).getCivilizationAdjective(3),0)), None, 2, "Art/Interface/Buttons/Units/button_merchant.dds", ColorTypes(14), pPlot.getX(), pPlot.getY(), True, True)

          UnitType = pUnit.getUnitType()
          #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
          pUnit.kill(1,pUnit.getOwner())
          # Merchants gets barbarian or killed: 50:50
          if pPlot.getNumUnits() == 0:
            iRand = self.myRandom(2, None)
            if iRand == 1:
              barbPlayer.initUnit(gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

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
          if gc.getPlayer(iPlayer).getGold() > 90:

            # Human PopUp
            if gc.getPlayer(iPlayer).isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_HUNS",()))
              popupInfo.setData1(iPlayer)
              popupInfo.setData2(pUnit.getID())
              popupInfo.setOnClickedPythonCallback("popupHunsPayment") # EntryPoints/CvScreenInterface und CvGameUtils
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_HUNS_NO",()), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_HUNS_YES",()), "")
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
                  for k in range (iRange):
                    if sPlot.getUnit(k).getOwner() == iPlayer and sPlot.getUnit(k).canAttack(): iPlayerUnits += 1
                    if sPlot.getUnit(k).isBarbarian() and sPlot.getUnit(k).getUnitType() == iHunType: iHunUnits += 1

              if iPlayerUnits > iHunUnits * 3:
                iRand = 0 # kein effekt
              elif iPlayerUnits > iHunUnits * 2:
                iRand = self.myRandom(2, None)
                if iRand < 1:
                  gc.getPlayer(iPlayer).changeGold(-100)
                  #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                  pUnit.kill(1,pUnit.getOwner())
              else:
                gc.getPlayer(iPlayer).changeGold(-100)
                #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                pUnit.kill(1,pUnit.getOwner())

          elif gc.getPlayer(iPlayer).isHuman():
              CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_POPUP_HUNS_NO_MONEY",()), None, 2, pUnit.getButton(), ColorTypes(10), pPlot.getX(), pPlot.getY(), True, True)

    # In der Stadt
    if pPlot.isCity():
      pCity = pPlot.getPlotCity()

      # Unit can stop city revolt / unit city revolt
      if  pCity.getOccupationTimer() > 2:
        if pUnit.isMilitaryHappiness():
          #if pUnit.getOwner() == pCity.getOwner():  # -> allies can help ;)
          #if pPlot.getNumUnits() > pCity.getPopulation():
          #if pUnit.movesLeft() <= 20:
          if PyInfo.UnitInfo(pUnit.getUnitType()).getMoves() == 1:
            pCity.changeOccupationTimer(-1)

      # Keine Formationen in der Stadt (rausgegeben ab PAE V Patch 2, Formationen sind auf Stadtangriff/verteidigung angepasst)
      #self.doUnitFormation (pUnit, -1)

    # nicht eine Stadt
    else:
      # AI Festungsformation
      iAnzahlFortifiedUnits = 2
      if not gc.getPlayer(pUnit.getOwner()).isHuman():
        iImp = pPlot.getImprovementType()
        if iImp > -1:
          # Bei einem Turm2 oder einer Festung1,2
          if iImp == gc.getInfoTypeForString("IMPROVEMENT_TURM2") or iImp == gc.getInfoTypeForString("IMPROVEMENT_FORT") or \
          iImp == gc.getInfoTypeForString("IMPROVEMENT_FORT2"):

            # Alle Formationen entfernen
            #self.doUnitFormation (pUnit, -1)

            # Plot soll der AI (Unit) oder niemandem zugewiesen sein
            if pPlot.getOwner() == pUnit.getOwner() or pPlot.getOwner() == -1:
              # Nur fuer Axt, Speer und Schwerteinheiten
              if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN") or pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_AXEMAN") or  pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"):
                if PyInfo.UnitInfo(pUnit.getUnitType()).getMoves() == 1:
                  iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
                else:
                  iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
                iRange = pPlot.getNumUnits()
                iNum = 0
                k = 0
                for k in range (iRange):
                  if pPlot.getUnit(k).isHasPromotion(iPromo): iNum += 1
                  if iNum > iAnzahlFortifiedUnits: break
                if iNum < iAnzahlFortifiedUnits:
                  self.doUnitFormation (pUnit, iPromo)

      # Keine Formation in bestimmte Features
      #iFeat = pPlot.getFeatureType()
      #if iFeat > -1:
      #  if iFeat == gc.getInfoTypeForString("FEATURE_FOREST") or iFeat == gc.getInfoTypeForString("FEATURE_DICHTERWALD") or iFeat == gc.getInfoTypeForString("FEATURE_JUNGLE"):
      #    self.doUnitFormation (pUnit, -1)

########################################################
# --------- Bombard - Feature ----------------------
# Wird ein Fort mit Katapulten bombardiert, kann das Fort dadurch zerstoert werden: 10%
#    iUnit1 = gc.getInfoTypeForString("UNIT_CATAPULT")
#    iUnit2 = gc.getInfoTypeForString("UNIT_FIRE_CATAPULT")
#    if pUnit.getUnitType() == iUnit1 or pUnit.getUnitType() == iUnit2:
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# -----
    # PAE Debug Mark
    #"""
    if (not self.__LOG_MOVEMENT):
      return
    elif not pUnit.isDead():
      player = PyPlayer(pUnit.getOwner())
      unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
      if player and unitInfo:
        CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d'
          %(player.getID(), player.getCivilizationName(), unitInfo.getDescription(),
          pUnit.getX(), pUnit.getY()))

  def onUnitSetXY(self, argsList):
    'units xy coords set manually'
    pPlot,pUnit = argsList
    player = PyPlayer(pUnit.getOwner())
    unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
    if (not self.__LOG_MOVEMENT):
      return

  def onUnitCreated(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Unit Completed'
    unit = argsList[0]
    player = PyPlayer(unit.getOwner())
    if (not self.__LOG_UNITBUILD):
      return

  # Global
  def onUnitBuilt(self, argsList):
    'Unit Completed'
    city = argsList[0]
    unit = argsList[1]
    player = PyPlayer(city.getOwner())
    pPlayer = gc.getPlayer(city.getOwner())

    # PAE Debug Mark
    #"""

    bCheckCityState = False
    # ++++ AI - Unit Built/Created
    if not gc.getPlayer(city.getOwner()).isHuman():

      # PAE V: Pirate feature - disabled cause of possible OOS when too many active AI pirates
      #if unit.getDomainType() == gc.getInfoTypeForString("DOMAIN_SEA"):
      #  if self.myRandom(4, None) == 1:
      #    if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PIRACY")):
      #      if unit.getUnitType() == gc.getInfoTypeForString("UNIT_KONTERE"):
      #        unit.kill(1,unit.getOwner())
      #        unit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
      #      if unit.getUnitType() == gc.getInfoTypeForString("UNIT_BIREME"):
      #        unit.kill(1,unit.getOwner())
      #        unit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
      #      if unit.getUnitType() == gc.getInfoTypeForString("UNIT_TRIREME"):
      #        unit.kill(1,unit.getOwner())
      #        unit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
      #      if unit.getUnitType() == gc.getInfoTypeForString("UNIT_LIBURNE"):
      #        unit.kill(1,unit.getOwner())
      #        unit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)


      # Stadtverteidiger
      iNum = 0
      UnitsA = []
      UnitsB = []
      UnitsA.append(gc.getInfoTypeForString("UNIT_LIGHT_ARCHER"))
      UnitsA.append(gc.getInfoTypeForString("UNIT_ARCHER"))
      UnitsA.append(gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"))
      UnitsB.append(gc.getInfoTypeForString("UNIT_ONAGER"))
      UnitsB.append(gc.getInfoTypeForString("UNIT_CATAPULT"))
      UnitsB.append(gc.getInfoTypeForString("UNIT_FIRE_CATAPULT"))

      if unit.getUnitType() in UnitsA or unit.getUnitType() in UnitsB:
        pPlot = city.plot()
        iRange = pPlot.getNumUnits()
        for i in range (iRange):
          if not pPlot.getUnit(i).isNone():
            if pPlot.getUnit(i).getUnitType() == unit.getUnitType() and pPlot.getUnit(i).getOwner() == city.getOwner(): iNum += 1
        # UnitAIType 10 = UNITAI_CITY_DEFENSE
        if unit.getUnitType() in UnitsA and iNum < 3 or unit.getUnitType() in UnitsB and iNum < 2: unit.setUnitAIType(10)

      # Set offensive Formations
      else:
        self.doAIUnitFormations (unit, True, False, False)

      # Handicap: 0 (Settler) - 8 (Deity) ; 5 = King
      iHandicap = gc.getGame().getHandicapType()
      # -----------------------

      # 2nd Settler for AI (Immortal, Deity) (PAE V)
      if iHandicap >= 7 and unit.getUnitType() == gc.getInfoTypeForString("UNIT_SETTLER"):
        pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SETTLER"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

      # -----------------------
      # Experienced units on higher handicap level (PAE V Patch 3)
      if iHandicap >= 5:
        if unit.isMilitaryHappiness() or unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
          lPromos = []
          lPromos.append(-1)
          lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT1"))
          if iHandicap >= 6: lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT2"))
          if iHandicap >= 7: lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT3"))
          if iHandicap >= 8: lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT4"))

          iRange = len(lPromos)
          iRand = self.myRandom(iRange, None)
          if iRand > 0:
            for i in range(iRange):
              if i > 0 and i <= iRand:
                unit.setHasPromotion(lPromos[i], True)


    # Log Message (BTS)
    CvAdvisorUtils.unitBuiltFeats(city, unit)

    # ++++ Versorger / Supply Unit
    if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
      # gc.getInfoTypeForString("UNIT_SUPPLY_WAGON") # Tickets: 200
      city.setFood(city.getFood()/2)
      # Trait Strategist / Stratege: +50% Kapazitaet / +50% capacity
      if unit.getUnitType() == gc.getInfoTypeForString("UNIT_DRUIDE") or unit.getUnitType() == gc.getInfoTypeForString("UNIT_BRAHMANE"):
        if gc.getPlayer(unit.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_STRATEGE")): unit.setScriptData("150")
        else: unit.setScriptData("100")
      else:
          if gc.getPlayer(unit.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_STRATEGE")): unit.setScriptData("300")
          else: unit.setScriptData("200")

    # ++++ Getreidekarren
    if unit.getUnitType() == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"):
      city.setFood(city.getFood()/2)

    # ++++ Auswanderer (Emigrants), die die Stadtbevoelkerung senken
    if unit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
      pPlot = CyMap().plot(city.getX(), city.getY())
      iPop = city.getPopulation()
      # Einheit die richtige Kultur geben
      #iPlayerCulture = city.findHighestCulture() Klappt nicht, da Kultur des Stadtplots benoetigt wird
      # Muss selbst bestimmt werden, da plot.findHighestCultureTeam() das Team, aber nicht die Civ zurueckgibt
      iRange = gc.getMAX_PLAYERS()
      iPlayerCulture = -1
      iValueCulture = -1
      for i in range(iRange):
          if pPlot.getCulture(i) > iValueCulture:
              iValueCulture = pPlot.getCulture(i)
              iPlayerCulture = i
      # Sollte auf dem Plot keine Kultur sein (geht eigentlich nicht...), gehoert der Auswanderer zur Kultur des Besitzers
      if iValueCulture < 1: iPlayerCulture = unit.getOwner()
      unit.setScriptData(str(iPlayerCulture))
      # Pop*100 Kultur von dem Stadtplot abziehen (max. 1000) (es bleibt immer mind. 1 Kultur)
      iCultureMax = pPlot.getCulture(iPlayerCulture) - 1
      if iCultureMax > 1000: iCultureMax = 1000
      iCulture = iPop * 100
      if iCulture > iCultureMax: iCulture = iCultureMax
      pPlot.changeCulture(iPlayerCulture,-iCulture,1)
      # Pop senken, Nahrungslager leeren
      city.setFood(0)
      if iPop > 3:
        if pPlayer.isHuman(): city.changePopulation(-2)
        else: city.changePopulation(-1)
      else: city.setPopulation(1)

      bCheckCityState = True

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Auswanderer gebaut. Pop",iPop)), None, 2, None, ColorTypes(10), 0, 0, False, False)
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(city.getName(),city.getOwner())), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # --------------------------------------------

    # Ab PAE V Patch 3 werden Schiffe auch mit Nahrung produziert
    # ++++ Polyeren / Polyremen / Schiffe / Schiffsbau verbraucht Pop
    #if unit.getDomainType() == gc.getInfoTypeForString("DOMAIN_SEA"):
    #  BigShips = []
    #  BigShips.append(gc.getInfoTypeForString("UNIT_GALLEY"))
    #  BigShips.append(gc.getInfoTypeForString("UNIT_QUADRIREME"))
    #  BigShips.append(gc.getInfoTypeForString("UNIT_QUINQUEREME"))
    #  BigShips.append(gc.getInfoTypeForString("UNIT_ROME_DECAREME"))
    #  if unit.getUnitType() in BigShips:
    #    if city.getPopulation() > 1:
    #      city.changePopulation(-1)
    #      bCheckCityState = True
    #    city.setFood(city.getFood()/2)
    #    if pPlayer.isHuman():
    #      CyInterface().addMessage(city.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SHRINKS_DUE_UNIT",(unit.getName(),city.getName())), "", 2, None, ColorTypes(13), city.getX(), city.getY(), True, True)
    # --------------------------------------------

    # ++++ Bronze-Feature / Wald roden / Waldrodung / Abholzung / Desertifizierung / betrifft nicht die Barbarenstaedte
    if city.getOwner() != gc.getBARBARIAN_PLAYER():
     iCurrentEra = gc.getPlayer(city.getOwner()).getCurrentEra()
     if iCurrentEra > 0 and unit.getUnitCombatType() > 0:
      if unit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_ARCHER") and unit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"):
       NoForgeUnit = []
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_WARRIOR"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_HUNTER"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_SCOUT"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_WORKBOAT"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_DRUIDE"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_BRAHMANE"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_HORSE"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_CAMEL"))
       NoForgeUnit.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
       if unit.getUnitType() not in NoForgeUnit:
         # ***TEST***
         #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Waldrodung",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

         iHolzLager = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
         iMine = gc.getInfoTypeForString("IMPROVEMENT_MINE")
         iFeatType1 = gc.getInfoTypeForString("FEATURE_FOREST")
         iFeatType2 = gc.getInfoTypeForString("FEATURE_SAVANNA")
         iFeatType3 = gc.getInfoTypeForString("FEATURE_JUNGLE")
         iFeatType4 = gc.getInfoTypeForString("FEATURE_DICHTERWALD")
         # nicht bei Zedernholz
         bonus_zedern = gc.getInfoTypeForString("BONUS_ZEDERNHOLZ")

         # Einen guenstigen Plot auswaehlen
         # Priority:
         # 1. Leerer Wald
         # 2. Leere Savanne
         # 3. Leerer Dschungel
         # 4. Bewirtschaftetes Feld mit Wald aber ohne Holzlager
         # 5. Dichter Wald
         # 6. Wald im feindlichen Terrain (-1 Beziehung zum Nachbarn), aber nur wenn kein Holzlager drauf is
         PlotArray1 = []
         PlotArray2 = []
         PlotArray3 = []
         PlotArray4 = []
         PlotArray5 = []
         PlotArray6 = []
         PlotArrayX = []
         for i in range(5):
           for j in range(5):
             loopPlot = gc.getMap().plot(city.getX() + i - 2, city.getY() + j - 2)
             if None != loopPlot and not loopPlot.isNone():
               if loopPlot.getFeatureType() == iFeatType1 or loopPlot.getFeatureType() == iFeatType2 or loopPlot.getFeatureType() == iFeatType3 or loopPlot.getFeatureType() == iFeatType4:

                 if loopPlot.getBonusType(loopPlot.getOwner()) != bonus_zedern:

                   if loopPlot.getOwner() == city.getOwner():
                     if loopPlot.getImprovementType() == iMine: PlotArray1.append(loopPlot)
                     if loopPlot.getImprovementType() == -1:
                       # Wald / Savanne / Dschungel / Dichter Wald
                       if loopPlot.getFeatureType() == iFeatType1: PlotArray1.append(loopPlot)
                       elif loopPlot.getFeatureType() == iFeatType2: PlotArray2.append(loopPlot)
                       elif loopPlot.getFeatureType() == iFeatType3: PlotArray3.append(loopPlot)
                       elif loopPlot.getFeatureType() == iFeatType4: PlotArray5.append(loopPlot)
                     elif loopPlot.getImprovementType() != iHolzLager: PlotArray4.append(loopPlot)

                   elif loopPlot.getImprovementType() != iHolzLager:
                     if loopPlot.getFeatureType() != iFeatType4:
                       # PAE V: no unit on the plot (Holzraub)
                       if loopPlot.getNumUnits() == 0:
                         PlotArray6.append(loopPlot)

         # Plot wird ausgewaehlt, nach Prioritaet zuerst immer nur Wald checken, wenn keine mehr da, dann Savanne, etc...
         # Wald: Chance: Bronzezeit: 4%, Eisenzeit: 5%, Klassik: 6%
         if len(PlotArray1) > 0:
           iChance = 30 - iCurrentEra * 5
           if self.myRandom(iChance, None) == 0: PlotArrayX = PlotArray1
         # Savanne: Bronze: 6%, Eisen: 10%, Klassik: 20%
         elif len(PlotArray2) > 0:
           iChance = 20 - iCurrentEra * 5
           if self.myRandom(iChance, None) == 0: PlotArrayX = PlotArray2
         # Dschungel: wie Wald
         elif len(PlotArray3) > 0:
           iChance = 30 - iCurrentEra * 5
           if self.myRandom(iChance, None) == 0: PlotArrayX = PlotArray3
         # Bewirt. Feld ohne Holzlager: wie Savanne
         elif len(PlotArray4) > 0:
           iChance = 20 - iCurrentEra * 5
           if self.myRandom(iChance, None) == 0: PlotArrayX = PlotArray4
         # Dichter Wald: Bronze: 2%, Eisen: 2.5%, Klassik: 3%
         elif len(PlotArray5) > 0:
           iChance = 60 - iCurrentEra * 10
           if self.myRandom(iChance, None) == 0: PlotArrayX = PlotArray5

         # Ausl. Feld 10%, erst wenn es nur mehr 1 Waldfeld gibt (das soll auch bleiben)
         if len(PlotArray1) + len(PlotArray2) + len(PlotArray3) + len(PlotArray4) + len(PlotArray5) < 2:
           if len(PlotArray6) > 0:
             if self.myRandom(10, None) == 0: PlotArrayX = PlotArray6
             else: PlotArrayX = [] # Feld leeren
           else: PlotArrayX = [] # Feld leeren

         # Gibts einen Waldplot
         if len(PlotArrayX) > 0:
           iPlot = self.myRandom(len(PlotArrayX), None)

           # Auswirkungen Feature (Wald) entfernen, Holzlager entfernen, Nachbar checken
           # Feature (Wald) entfernen
           # Dichten Wald zu normalen Wald machen
           if PlotArrayX[iPlot].getFeatureType() == iFeatType4: PlotArrayX[iPlot].setFeatureType(iFeatType1,0)
           else:
             PlotArrayX[iPlot].setFeatureType(-1,0)
             # Lumber camp entfernen
             if PlotArrayX[iPlot].getImprovementType() == iHolzLager: PlotArrayX[iPlot].setImprovementType(-1)

           # Meldung
           # Attention: AS2D_CHOP_WOOD is additional defined in XML/Audio/Audio2DScripts.xml   (not used, AS2D_BUILD_FORGE instead)
           if PlotArrayX[iPlot].getOwner() == city.getOwner():
             CyInterface().addMessage(city.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_1",(city.getName(),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), PlotArrayX[iPlot].getX(), PlotArrayX[iPlot].getY(), True, True)

           elif PlotArrayX[iPlot].getOwner() > -1 and PlotArrayX[iPlot].getOwner() != gc.getBARBARIAN_PLAYER():
             CyInterface().addMessage(city.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_2",(gc.getPlayer(PlotArrayX[iPlot].getOwner()).getCivilizationShortDescription(0),gc.getPlayer(PlotArrayX[iPlot].getOwner()).getCivilizationAdjective(1))), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), PlotArrayX[iPlot].getX(), PlotArrayX[iPlot].getY(), True, True)
             CyInterface().addMessage(PlotArrayX[iPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_3",(gc.getPlayer(city.getOwner()).getCivilizationShortDescription(0),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), PlotArrayX[iPlot].getX(), PlotArrayX[iPlot].getY(), True, True)
             gc.getPlayer(PlotArrayX[iPlot].getOwner()).AI_changeAttitudeExtra(city.getOwner(),-1)

    # Feature Waldrodung Ende
    # --------------------------------------------


    # ++++++++ Names for Legions +++++++++++++++++
    # Reusing names of fallen Legions
    if unit.getUnitType() == gc.getInfoTypeForString("UNIT_LEGION2"):

      LegioUsedNames = []
      iRange = pPlayer.getNumUnits()
      for i in range(iRange):
        if pPlayer.getUnit(i).getUnitType() == gc.getInfoTypeForString("UNIT_LEGION2"):
          LegioUsedNames.append(re.sub(" \(.*?\)","",pPlayer.getUnit(i).getName()))

      LegioNames = ["Legio I Adiutrix","Legio I Germanica","Legio I Italica","Legio I Macriana Liberatrix","Legio I Minervia","Legio I Parthica","Legio II Adiutrix","Legio II Augusta","Legio II Italica","Legio II Parthica","Legio II Traiana Fortis","Legio III Augusta","Legio III Cyrenaica","Legio III Gallica","Legio III Italica","Legio III Parthica","Legio III Macedonica","Legio IV Flavia Felix","Legio IV Scythica","Legio V Alaudae","Legio V Macedonica","Legio VI Ferrata","Legio VI Victrix","Legio VII Claudia","Legio VII Gemina","Legio VIII Augusta","Legio IX Hispana","Legio X Fretensis","Legio X Equestris","Legio XI Claudia","Legio XII Fulminata","Legio XIII Gemina","Legio XIV Gemina","Legio XV Apollinaris","Legio XV Primigenia","Legio XVI Gallica","Legio XVI Flavia Firma","Legio XVII","Legio XVIII","Legio XIX","Legio XX Valeria Victrix","Legio XXI Rapax","Legio XXII Deiotariana","Legio XXII Primigenia","Legio XXX Ulpia Victrix","Legio I Iulia Alpina","Legio I Armeniaca","Legio I Flavia Constantia","Legio I Flavia Gallicana","Legio I Flavia Martis","Legio I Flavia Pacis","Legio I Illyricorum","Legio I Iovia","Legio I Isaura Sagitaria","Legio I Martia","Legio I Maximiana","Legio I Noricorum","Legio I Pontica","Legio II Iulia Alpina","Legio II Armeniaca","Legio II Brittannica","Legio II Flavia Virtutis","Legio II Herculia","Legio II Isaura","Legio III Iulia Alpina","Legio III Diocletiana","Legio III Flavia Salutis","Legio III Herculia","Legio III Isaura","Legio IV Italica","Legio IV Martia","Legio IV Parthica","Legio V Iovia","Legio V Parthica","Legio VI Gallicana","Legio VI Herculia","Legio VI Hispana","Legio VI Parthica","Legio XII Victrix","Legio Thebaica"]
      iRange = len(LegioNames)
      for i in range(iRange):
        if LegioNames[i] not in LegioUsedNames:
          unit.setName(LegioNames[i])
          break
    # --- end Legion Names

    # PAE Provinzcheck
    if bCheckCityState:
      self.doCheckCityState(city)

    # PAE Unit Auto Promotions
    if gc.getUnitInfo(unit.getUnitType()).getCombat() > 0:
      if unit.getDomainType() == DomainTypes.DOMAIN_SEA:
        if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
          self.doCityUnitPromotions4Ships(city,unit)
      else:
        self.doCityUnitPromotions(city,unit)

    # PAE V: Mercenary promotion
    if city.getOwner() != city.getOriginalOwner():
      if city.getPopulation() < 9:
        if city.plot().calculateCulturePercent(city.getOwner()) < 75:
          if unit.isMilitaryHappiness() or unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
             unit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY"), True)

    # PAE Debug Mark
    #"""

    if (not self.__LOG_UNITBUILD):
      return
#    CvUtil.pyPrint('%s was finished by Player %d Civilization %s'
#      %(unit.getName(), player.getID(), player.getCivilizationName()))

  # nicht global?
  def onUnitKilled(self, argsList):
    'Unit Killed'
    unit, iAttacker = argsList

    player = PyPlayer(unit.getOwner())
    attacker = PyPlayer(iAttacker)

    if (not self.__LOG_UNITKILLED):
      return
    CvUtil.pyPrint('Player %d Civilization %s Unit %s was killed by Player %d'
      %(player.getID(), player.getCivilizationName(), unit.getName(), attacker.getID()))

  def onUnitLost(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Unit Lost'
    if (not self.__LOG_UNITLOST):
      return
    unit = argsList[0]
    player = PyPlayer(unit.getOwner())
    CvUtil.pyPrint('%s was lost by Player %d Civilization %s'
      %(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))

  def onUnitPromoted(self, argsList):
    'Unit Promoted'
    if (not self.__LOG_UNITPROMOTED):
      return
    pUnit, iPromotion = argsList
#    player = PyPlayer(pUnit.getOwner())
#    CvUtil.pyPrint('Unit Promotion Event: %s - %s' %(player.getCivilizationName(), pUnit.getName(),))

  def onUnitSelected(self, argsList):
    'Unit Selected'
    pUnit = argsList[0]

    if (not self.__LOG_UNITSELECTED):
      return
#    player = PyPlayer(pUnit.getOwner())
#    CvUtil.pyPrint('%s was selected by Player %d Civilization %s'
#      %(pUnit.getName(), player.getID(), player.getCivilizationName()))

  def onUnitRename(self, argsList):
    'Unit is renamed'
    pUnit = argsList[0]
    if (pUnit.getOwner() == gc.getGame().getActivePlayer()):
      self.__eventEditUnitNameBegin(pUnit)

  #global
  def onUnitPillage(self, argsList):
    'Unit pillages a plot'
    pUnit, iImprovement, iRoute, iOwner = argsList
    iPlotX = pUnit.getX()
    iPlotY = pUnit.getY()
    pPlot = CyMap().plot(iPlotX, iPlotY)

    # PAE Debug Mark
    #"""
    if iImprovement > -1:
      # XP nur bei enemy plots
      if pPlot.getOwner() != pUnit.getOwner(): pUnit.changeExperience (1,-1,0,0,0)

      # Versorger aufladen / Supply Wagon recharge
      lHealer = []
      iRange = pPlot.getNumUnits()
      for iUnit in range(iRange):
        if pPlot.getUnit(iUnit).getOwner() == pUnit.getOwner():
          if pPlot.getUnit(iUnit).getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
            lHealer.append(pPlot.getUnit(iUnit))

      if len(lHealer) > 0:
        iSupplyChange = 0
        if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FARM"): iSupplyChange += 50
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_PASTURE"): iSupplyChange += 50
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_PLANTATION"): iSupplyChange += 30
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_BRUNNEN"): iSupplyChange += 20
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"): iSupplyChange += 10
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HAMLET"): iSupplyChange += 15
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"): iSupplyChange += 20
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_TOWN"): iSupplyChange += 25
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"): iSupplyChange += 25
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT"): iSupplyChange += 30
        elif iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT2"): iSupplyChange += 40

        for loopUnit in lHealer:
             # Maximalwert herausfinden
             if loopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_DRUIDE") or loopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_BRAHMANE"): iMaxHealing = 100
             else: iMaxHealing = 200
             # Trait Strategist / Stratege: +50% Kapazitaet / +50% capacity
             if gc.getPlayer(loopUnit.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_STRATEGE")):
                 iMaxHealing *= 3
                 iMaxHealing /= 2

             txt = loopUnit.getScriptData()
             if txt == "": txt = str(iMaxHealing) # 0 = leer/verbraucht, aber "" ist fabriksneu ;)
             iSupplyValue = int(txt)
             iSupplyValue += iSupplyChange
             if iSupplyValue > iMaxHealing: iSupplyValue = iMaxHealing
             loopUnit.setScriptData(str(iSupplyValue))
      # -----------------

      # Free promotion when pillaging: 20%
      if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE5")):
        if 2 > self.myRandom(10, None):
          if   pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE5")
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE4")
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE3")
          elif pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE2")
          else: iNewPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE1")

          pUnit.setHasPromotion(iNewPromo, True)
          if gc.getPlayer(pUnit.getOwner()).isHuman():
            CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION",(pUnit.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)

      # Feldsklaven und Minensklaven checken
      if iImprovement != gc.getInfoTypeForString("IMPROVEMENT_FISHING_BOATS"):
        self.doCheckSlavesAfterPillage(pUnit,pPlot)

      # Handelsposten: Plot-ScriptData leeren
      if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):
        pPlot.setScriptData("")

      # Unit soll sich nachher nicht mehr fortbewegen koennen
      pUnit.finishMoves()
    # PAE Debug Mark
    #"""

    if (not self.__LOG_UNITPILLAGE):
      return
#    CvUtil.pyPrint("Player %d's %s pillaged improvement %d and route %d at plot at (%d, %d)"
#      %(iOwner, pUnit.getName(), iImprovement, iRoute, iPlotX, iPlotY))

  def onUnitSpreadReligionAttempt(self, argsList):
    'Unit tries to spread religion to a city'
    pUnit, iReligion, bSuccess = argsList

    iX = pUnit.getX()
    iY = pUnit.getY()
    pPlot = CyMap().plot(iX, iY)
    pCity = pPlot.getPlotCity()

  def onUnitGifted(self, argsList):
    'Unit is gifted from one player to another'
    pUnit, iGiftingPlayer, pPlotLocation = argsList

  def onUnitBuildImprovement(self, argsList):
    'Unit begins enacting a Build (building an Improvement or Route)'
    pUnit, iBuild, bFinished = argsList

    # Sklaven koennen bei einem Bauprojekt sterben / Slaves can die during an improvment construction
    if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
      # Chance of unit dying 3%
      iRand = self.myRandom(33, None)
      if iRand == 1:
        iOwner = pUnit.getOwner()
        if gc.getPlayer(iOwner).isHuman():
          iRand = self.myRandom(10, None)
          CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DYING_SLAVES_"+str(iRand),(0,0)), 'AS2D_UNITCAPTURE', 2, 'Art/Interface/Buttons/Units/button_slave.dds', ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
        #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
        pUnit.kill(1,pUnit.getOwner())

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave gestorben (Zeile 3766)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Holzcamp entfernen, wenn Wald entfernt wurde
    if bFinished:
      if iBuild == gc.getInfoTypeForString("BUILD_REMOVE_JUNGLE") or iBuild == gc.getInfoTypeForString("BUILD_REMOVE_FOREST") or iBuild == gc.getInfoTypeForString("BUILD_REMOVE_FOREST_BURNT"):
        pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())
        if pPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP"):
          pPlot.setImprovementType(-1)


  def onGoodyReceived(self, argsList):
    'Goody received'
    iPlayer, pPlot, pUnit, iGoodyType = argsList
    if (not self.__LOG_GOODYRECEIVED):
      return
#    CvUtil.pyPrint('%s received a goody' %(gc.getPlayer(iPlayer).getCivilizationDescription(0)),)

  def onGreatPersonBorn(self, argsList):
  ## Platy WorldBuilder ##
    #if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Great Person Born'
    pUnit, iPlayer, pCity = argsList
    player = PyPlayer(iPlayer)
    pPlayer = gc.getPlayer(iPlayer)
    if pUnit.isNone() or pCity.isNone():
      return

    # Names for Great Generals / Feldherrenliste
    if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_GREAT_GENERAL"):

      listNamesStandard = ["Adiantunnus","Divico","Albion","Malorix","Inguiomer","Archelaos","Dorimachos","Helenos","Kerkidas","Mikythos","Philopoimen","Pnytagoras","Sophainetos","Theopomopos","Gylippos","Proxenos","Theseus","Balakros","Bar Kochba","Julian ben Sabar","Justasas","Patricius","Schimon bar Giora","Artaphernes","Harpagos","Atropates","Bahram Chobin","Datis","Schahin","Egnatius","Curius Aentatus","Antiochos II","Spartacus","Herodes I","Calgacus","Suebonius Paulinus","Maxentus","Sapor II","Alatheus","Saphrax","Honorius","Aetius","Achilles","Herodes","Heros","Odysseus","Anytos"]

      if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
        listNames = ["Agilo","Marellus","Flavius Theodosius","Flavius Merobaudes","Flavius Bauto","Flavius Saturnius","Flavius Fravitta","Sextus Pompeius","Publius Canidius Crassus","Marcus Claudius Marellus","Marcus Cato Censorius","Flavius Felix","Flavius Aetius","Gnaeus Pompeius Strabo","Ricimer","Flavius Ardaburius Aspar","Publius Quinctilius Varus","Marcus Vispanius Agrippa","Marcus Antonius Primus","Tiberius Gracchus","Petillius Cerialis","Gaius Suetonius Paulimius","Titus Labienus","Gnaeus Iulius Verus","Aulus Allienus","Marcellinus","Flavius Castinus","Lucius Fannius","Aulus Didius Gallus","Rufio","Publius Servilius Rullus","Papias"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
        listNames = ["Lars Tolumnius","Lucius Tarquinius Priscus","Arrunte Tarquinius","Celio Vibenna","Elbio Vulturreno","Arrunte Porsena","Tito Tarquinius","Aulus Caecina Alienus","Mezentius","Aulus Caecina Severerus","Sextus Tarquinius","Velthur Spurinna"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT"):
        listNames = ["Ortiagon","Adiatunnus","Boduognatus","Indutiomarus","Catuvolcus","Deiotaros","Viridomarus","Chiomara","Voccio","Kauaros","Komontorios"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GALLIEN"):
        listNames = ["Vergobret","Viridovix","Acco","Amandus","Camulogenus","Postumus","Aelianus","Capenus","Tibatto","Julias Classicus","Diviciacus"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
        listNames = ["Valamir","Athaulf ","Eurich","Sigerich","Walia","Julius Civilis","Malorix","Edekon","Vestralp","Chnodomar","Agenarich","Ardarich","Verritus","Thuidimir","Gundioch","Priarius","Kniva","Radagaisus","Alaviv","Athanarich","Hunulf","Hunimund","Rechiar","Rechila","Cannabaudes","Eriulf","Adovacrius","Gundomad","Hariobaud","Hortar","Suomar","Marcomer","Gennobaudes","Sunno","Merogaisus","Segimer","Inguiomer","Vadomar","Ascaricus","Ursicinus","Arbogast"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_DAKER"):
        listNames = ["Cotisone","Oroles","Duras","Rubobostes","Dromichaetes","Rholes","Zyraxes","Dapys","Fastida","Zenon"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"):
        listNames = ["Bardylis","Glaukias","Monunios II","Skerdilaidas","Bato I","Demetrios Pharos","Pleuratos I","Sirras","Bato II","Epulon","Longarus","Pinnes Pannonien","Cleitus","Bardylis II","Genthios"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE"):
        listNames = ["Adeimantos","Xenokleides","Timonides Leukas","Pyrrhias","Philopoimen","Milon","Leosthenes","Kineas","Dorimachos","Daochos I","Ameinias","Herakleides","Panares","Lasthenes","Onomarchus","Menon Pharsalos","Timoleon","Hermokrates","Archytas Tarent","Keridas"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS"):
        listNames = ["Konon","Miltiades","Perikles","Leon","Menon","Aristeides","Autokles","Chares","Eukrates","Hippokrates","Kallistratos","Thrasyllos","Timomachos","Xanthippos","Xenophon","Demosthenes","Anytos"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI"):
        listNames = ["Kleomenes Boeotarich","Pagondas","Pelopidas","Proxenos","Coeratadas","Gorgidas","Peisis Thespiai","Theagenes Boeotarich","Apollokrates","Polyxenos"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
        listNames = ["Brasidas","Eurybiades","Klearchos","Xanthippos","Mindaros","Peisander","Therimenes","Thibron","Agesilaos","Gylippos","Astyochos","Aiantides Milet","Antalkidas","Archidamos II","Aristodemos","Chalkideus","Derkylidas","Euryanax","Eurylochos","Hippokrates Sparta","Kallikratidas","Phoibidas","Cheirisophos"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
        listNames = ["Admetos","Attalos","Antipatros","Antigonos","Antigenes","Demetrios Althaimenes","Gorgias","Herakon","Karanos","Kleitos","Memnon","Nikanor","Parmenion","Philippos","Pleistarchos","Meleagros","Menidas","Menandros","Telesphoros","Demetrios I Poliorketes","Adaios Alektryon","Alexandros","Koinos","Zopyrion"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HETHIT"):
        listNames = ["Pithana","Anitta","Labarna","Mursili I","Hantili I","Arnuwanda II","Muwattalli II","Suppiluliuma II","Kantuzzili","Kurunta"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_LYDIA"):
        listNames = ["Ardys II","Sadyattes II","Gyges","Paktyes","Mazares","Myrsus","Lydus","Manes","Agron","Meles"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON"):
        listNames = ["Luli","Abdi-Milkutti","Straton I","Tabnit","Abd-Melqart","Azemilkos","Baal I","Ithobaal III","Elukaios","Baal II","Panam-muwa II","Esmun-ezer"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"):
        listNames = ["Adherbal","Bomilkar","Hannibal Gisko","Boodes","Hamilkar","Mago","Maharbal","Hanno","Himilkon","Gisco","Hannibal Bomilkars","Hasdrubal Cartagagena","Hasdrubal Barkas","Hasdrubal Hannos","Hasdrubal Gisco","Mago Barkas","Malchus"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL"):
        listNames = ["Bar Kochbar","Jonathan","Judas Makkabaeus","Justasas","Schimon bar Giora","Simon Makkabaeus","Johann Gischala","Barak","Patricius","Abner","Scheba","Jaobs","Benaja","Omri","Jeha","Goliath"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SUMERIA"):
        listNames = ["Agga","Ur-Nammu","Gudea","Eanatum","Amar-Sin","Sulgi","Utuhengal","Lugalbanda","Enuk-duanna","Rim-Anum","Ibbi-Sin"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON"):
        listNames = ["Sumu-abum","Sumulael","Sabium","Hammurapi","Eriba-Marduk","Burna-burias I","Neriglissar","Abi-esuh","Nergalscharrussar","Ulamburiasch","Musezib-Marduk","Bel-simanni","Agum III","Marduk-apla-iddina II","Nabu-nasir","Bel-ibni"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"):
        listNames = ["Dajan-Assur","Samsi-ilu","Sin-sumu-lisir","Assur-bela-ka-in","Bel-lu-Ballet","Nergal-ilaya","Nabu-da-inannil","Inurta-ilaya","Tustanu","Schanabuschu","Assur-dan I","Assur-nirari V","Eriba-Adad I","Assur-dan II","Sanherib","Asarhaddon"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
        listNames = ["Artaphernes","Artasyras","Shahrbaraz","Harpagos","Mardonios","Xenias Parrhasia","Otanes Sisamnes","Tissaphernes","Hydarnes,","Pharnabazos II","Tithraustes","Smerdomenes","Tritantaichmes","Tiribazos","Megabazos","Megabates","Artabozos I","Pharnabazos III","Pherendates","Abrokomas","Atropates","Datis","Satibarzanes","Oxyathres","Struthas"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
        listNames = ["Ahmose","Djehuti","Ahmose Pennechbet","Antef","Seti","Psammetich I","Sib-e","Ramses III","Psammetich III","Merenptah","Haremhab","Amasis","Amenemhab","Re-e","Djefaihap","Kanefer"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_NUBIA"):
        listNames = ["Kaschta","Pije","Schabaka","Schabataka","Tanotamun","Aspelta","Pekartror","Harsijotef","Charamadoye","Cheperkare"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_IBERER"):
        listNames = ["Mandonio","Caro Segeda","Megara","Olindico","Culcas","Gauson","Hilerno","Istolacio","Luxinio","Punico","Besadino","Budar","Edecon","Indortes"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"):
        listNames = ["Gauda","Gulussa","Matho","Tacfarinas","Syphax","Hiempsal I","Micipsa","Arabion","Suburra","Mastanabal"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BERBER"):
        listNames = ["Masties","Lusius Quietus","Firmus","Gildon","Quintus Lollius Urbicus","Sabalus","Bagas","Bogud","Bocchus II","Lucius Balbus Minor"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_LIBYA"):
        listNames = ["Osorkon II","Namilt I","Iupet","Osochor","Paschedbastet","Namilt II","Takelot II","Petubastis I","Osorkon III","Bakenntah"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"):
        listNames = ["Idanthyrsos","Maues","Satrakes","Skilurus","Scopasis","Palacus","Madius","Eunones","Octamasadas","Azes I"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HUNNEN"):
        listNames = ["Balamir","Dengizich","Ellac","Oktar","Rua","Uldin","Kursisch""Hormidac","Ernak","Charaton"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA"):
        listNames = ["Pushyamitra Shunga","Kujula Kadphises","Chandragupta II","Samudragupta","Kharavela","Skandagupta","Dhana Nanda","Vidudabha","Vishvamitra","Bimbisara","Ajatashatru","Bindusara","Kanishka","Vima Kadphises","Soter Megas"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BRITEN"):
        listNames = ["Cassivelanaunus","Cingetorix","Carvillius","Taximagulus","Segovax","Ambrosius Aurelius","Hengest","Horsa","Vortigern","Riothamus","Venutius","Togodumnus","Allectus","Nennius","Calgacus"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PARTHER"):
        listNames = ["Surena","Artabanus V","Vologase I","Vologase IV","Phraates IV","Osreos I","Phraates II","Pakoros I","Artabanus IV","Barzapharnes","Pharnapates"]
      elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_VANDALS"):
        listNames = ["Godigisel","Gunderich","Gunthamund","Gento","Thrasamund","Hoamer","Wisimar","Flavius Stilicho","Andevoto","Hilderich"]
      else: listNames = listNamesStandard

      GG_Name = ""
      i = 0
      listlength = len(listNames)
      while i < listlength:
        i += 1
        iRand = self.myRandom(listlength, None)
        if listNames[iRand] not in self.GG_UsedNames:
          GG_Name = listNames[iRand]
          self.GG_UsedNames.append(listNames[iRand])
          break

      if GG_Name == "":
        iRand = self.myRandom(len(listNamesStandard), None)
        GG_Name = listNamesStandard[iRand]

      if GG_Name != "":
        pUnit.setName(GG_Name)

        if pPlayer.isHuman():
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GREAT_GENERAL_BORN",(GG_Name,pCity.getName())), 'NONE', 2, pUnit.getButton(), ColorTypes(11), pUnit.getX(), pUnit.getY(), True, True)


    if (not self.__LOG_GREATPERSON):
      return
#    CvUtil.pyPrint('A %s was born for %s in %s' %(pUnit.getName(), player.getCivilizationName(), pCity.getName()))

  def onTechAcquired(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Tech Acquired'
    iTechType, iTeam, iPlayer, bAnnounce = argsList
    # Note that iPlayer may be NULL (-1) and not a refer to a player object

    # Show tech splash when applicable
    if (iPlayer > -1 and bAnnounce and not CyInterface().noTechSplash()):
      if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
        #if ((not gc.getGame().isNetworkMultiPlayer()) and (iPlayer == gc.getGame().getActivePlayer())):
        if gc.getPlayer(iPlayer).isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
          popupInfo.setData1(iTechType)
          popupInfo.setText(u"showTechSplash")
          popupInfo.addPopup(iPlayer)

    #-----------------------------
    # Tech und freie Einheit / Free Unit
    bNewUnit = False
    if iPlayer > -1:
      iUnit = -1
      # Religionen
      if   iTechType == gc.getInfoTypeForString("TECH_RELIGION_NORDIC"): iUnit = gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_CELTIC"): iUnit = gc.getInfoTypeForString("UNIT_CELTIC_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_SUMER"):  iUnit = gc.getInfoTypeForString("UNIT_SUMER_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_GREEK"):  iUnit = gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_EGYPT"):  iUnit = gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_PHOEN"):  iUnit = gc.getInfoTypeForString("UNIT_PHOEN_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_HINDU"):  iUnit = gc.getInfoTypeForString("UNIT_HINDU_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_ROME"):  iUnit = gc.getInfoTypeForString("UNIT_ROME_MISSIONARY")
      elif iTechType == gc.getInfoTypeForString("TECH_DUALISMUS"): iUnit = gc.getInfoTypeForString("UNIT_ZORO_MISSIONARY")
      # Kulte
      elif iTechType == gc.getInfoTypeForString("TECH_FRUCHTBARKEIT"): iUnit = gc.getInfoTypeForString("UNIT_EXECUTIVE_2")
      elif iTechType == gc.getInfoTypeForString("TECH_GLADIATOR"): iUnit = gc.getInfoTypeForString("UNIT_EXECUTIVE_5")

      # Einheit erstellen
      if iUnit > -1:
        pPlayer = gc.getPlayer(iPlayer)
        # Zufallsstadt auswaehlen
        lCities = PyPlayer(iPlayer).getCityList()
        if len(lCities) > 0:
          iRand = self.myRandom(len(lCities), None)
          iX = pPlayer.getCity(lCities[iRand].getID()).getX()
          iY = pPlayer.getCity(lCities[iRand].getID()).getY()
          NewUnit = pPlayer.initUnit(iUnit, iX, iY, UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
          bNewUnit = True

#      #freier Siedler
#      iUnit = -1
#      pPlayer = gc.getPlayer(iPlayer)
#      if not pPlayer.isHuman():
#          if iTechType == gc.getInfoTypeForString("TECH_GEOMETRIE"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_SCHIFFSBAU"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_DUALISMUS"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_CELTIC"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_NORDIC"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_COLONIZATION2"):
#              if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ASSYRIA") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_LYDIA") \
#              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
#                  iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_ROME"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#          elif iTechType == gc.getInfoTypeForString("TECH_PERSIAN_ROAD"):
#              iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
#
#      # Einheit erstellen
#      if iUnit > -1:
#        #pPlayer = gc.getPlayer(iPlayer)
#        pCapital = pPlayer.getCapitalCity()
#        if pCapital != None and not pCapital.isNone():
#          iX = pCapital.getX()
#          iY = pCapital.getY()
#          NewUnit = pPlayer.initUnit(iUnit, iX, iY, UnitAITypes.UNITAI_SETTLE, DirectionTypes.DIRECTION_SOUTH)

    # Matriarchist
    if bNewUnit and iTechType == gc.getInfoTypeForString("TECH_FRUCHTBARKEIT"):
       # Verschiedene Gottesanbeter
       if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_CELTS",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_GERMAN",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_ROME",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_EGYPT",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON"):
          text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_PHOEN",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
          text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_GREEK",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_BABYLON",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SUMERIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_SUMER",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HETHIT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_HITTI",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_PERSIA",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BERBER") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"):
          text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_BERBER",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_IBERER"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_IBERIA",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_DAKER"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_DACIA",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_SCYTHS",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_MATRIACHAT_ILLYRIA",("",))
       else: text = ""

       if text != "":
        text = text + " " + CyTranslator().getText("TXT_KEY_UNIT_KULT_FOLLOWER",("",))
        NewUnit.setName(text)

       # ***TEST***
       #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Matriachist bekommen (Zeile 2848)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Heroenkultist
    if bNewUnit and iTechType == gc.getInfoTypeForString("TECH_GLADIATOR"):
       # Verschiedene Gottesanbeter
       if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_CELTS",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_GERMAN",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_ROME",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_EGYPT",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON"):
          text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_PHOEN",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") \
        or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
          text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_ROME",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_BABYLON",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SUMERIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_SUMER",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HETHIT"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_HITTI",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_PERSIA",("",))
       elif pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"):
        text = CyTranslator().getText("TXT_KEY_UNIT_HEROEN_PHOEN",("",))
       else: text = ""

       if text != "":
        text = text + " " + CyTranslator().getText("TXT_KEY_UNIT_KULT_FOLLOWER",("",))
        NewUnit.setName(text)


    # Heresy ---------------------
    if iPlayer > -1 and iTechType == gc.getInfoTypeForString("TECH_HERESY"):
        pPlayer = gc.getPlayer(iPlayer)

        lCities = PyPlayer(iPlayer).getCityList()

        iRangeCities = len(lCities)
        for i in range(iRangeCities):
            pCity = pPlayer.getCity(lCities[i].getID())

            # Kulte
            iReliHindu = gc.getInfoTypeForString("RELIGION_HINDUISM")
            iCorpIndra = gc.getInfoTypeForString("CORPORATION_9")

            iRange = gc.getNumCorporationInfos()
            iRange2 = gc.getNumBuildingInfos()
            for iCorp in range(iRange):
              if pCity.isHasCorporation(iCorp):
                if not ( iCorp == iCorpIndra and pCity.isHasReligion(iReliHindu) ):
                  for i in range(iRange2):
                    if pCity.getNumBuilding(i) > 0:
                      thisBuilding = gc.getBuildingInfo(i)
                      if thisBuilding.getPrereqCorporation() == iCorp or thisBuilding.getFoundsCorporation() == iCorp:
                        pCity.setNumRealBuilding(i,0)
                  pCity.setHasCorporation(iCorp, 0, 0, 0)

            # Religionen
            ListRelis = []
            ListRelis.append(gc.getInfoTypeForString("RELIGION_HINDUISM"))
            ListRelis.append(gc.getInfoTypeForString("RELIGION_BUDDHISM"))
            ListRelis.append(gc.getInfoTypeForString("RELIGION_JUDAISM"))
            ListRelis.append(gc.getInfoTypeForString("RELIGION_CHRISTIANITY"))
            ListRelis.append(gc.getInfoTypeForString("RELIGION_JAINISMUS"))

            iRange = gc.getNumReligionInfos()
            iRange2 = gc.getNumBuildingInfos()
            for iReli in range(iRange):
              if iReli not in ListRelis:
                if pCity.isHasReligion(iReli) and not pCity.isHolyCityByType(iReli):
                  for i in range(iRange2):
                    if pCity.getNumBuilding(i) > 0:
                      thisBuilding = gc.getBuildingInfo(i)
                      if thisBuilding.getPrereqReligion() == iReli or thisBuilding.getHolyCity() == iReli:
                        pCity.setNumRealBuilding(i,0)
                  pCity.setHasReligion(iReli, 0, 0, 0)

        # Meldung (PopUp)
        if gc.getPlayer(iPlayer).isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HERESY_DARK_AGE_POPUP",("", )))
          popupInfo.addPopup(iPlayer)

    # ---------------------------------------------------------

    if (not self.__LOG_TECH):
      return
#    CvUtil.pyPrint('%s was finished by Team %d'
#      %(PyInfo.TechnologyInfo(iTechType).getDescription(), iTeam))

  def onTechSelected(self, argsList):
    'Tech Selected'
    iTechType, iPlayer = argsList
    if (not self.__LOG_TECH):
      return
#    CvUtil.pyPrint('%s was selected by Player %d' %(PyInfo.TechnologyInfo(iTechType).getDescription(), iPlayer))

  def onReligionFounded(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Religion Founded'
    iReligion, iFounder = argsList
    player = PyPlayer(iFounder)
    iCityId = gc.getGame().getHolyCity(iReligion).getID()

    # PAE - capital gets Holy City for certain religions
    lReligion = []
    lReligion.append(gc.getInfoTypeForString("RELIGION_CELTIC"))
    lReligion.append(gc.getInfoTypeForString("RELIGION_NORDIC"))
    lReligion.append(gc.getInfoTypeForString("RELIGION_PHOEN"))
    lReligion.append(gc.getInfoTypeForString("RELIGION_GREEK"))
    lReligion.append(gc.getInfoTypeForString("RELIGION_ROME"))
    lReligion.append(gc.getInfoTypeForString("RELIGION_JUDAISM"))

    if iReligion in lReligion:
      pCapitalCity = gc.getPlayer(iFounder).getCapitalCity()
      if pCapitalCity:
        if iCityId != pCapitalCity.getID():
          gc.getGame().getHolyCity(iReligion).setHasReligion(iReligion,0,0,0)
          gc.getGame().setHolyCity (iReligion, pCapitalCity, 0)
          iCityId = pCapitalCity.getID()

    # Christentum
    elif iReligion == gc.getInfoTypeForString("RELIGION_CHRISTIANITY"):
      iJudentum = gc.getInfoTypeForString("RELIGION_JUDAISM")
      # In der heiligen juedischen Stadt, wenn der Gruender der Besitzer ist
      pHolyCityJudentum = gc.getGame().getHolyCity(iJudentum)
      if pHolyCityJudentum.getOwner() == iFounder:
        if iCityId != pHolyCityJudentum.getID():
          gc.getGame().getHolyCity(iReligion).setHasReligion(iReligion,0,0,0)
          gc.getGame().setHolyCity (iReligion, pHolyCityJudentum, 0)
          iCityId = pHolyCityJudentum.getID()
      # in der groessten juedischen Stadt des Besitzers
      else:
        pNewCity = None
        iNewCityPop = 0
        pPlayer = gc.getPlayer(iFounder)
        iNumCities = pPlayer.getNumCities()
        for i in range (iNumCities):
          pCity = pPlayer.getCity(i)
          if pCity:
            if pCity.isHasReligion(iJudentum):
              iPop = pCity.getPopulation()
              if iPop > iNewCityPop:
                iNewCityPop = iPop
                pNewCity = pCity
        if pNewCity:
          if iCityId != pNewCity.getID():
            gc.getGame().getHolyCity(iReligion).setHasReligion(iReligion,0,0,0)
            gc.getGame().setHolyCity (iReligion, pNewCity, 0)
            iCityId = pNewCity.getID()

    # BTS
    if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
      if gc.getPlayer(iFounder).isHuman():
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
        popupInfo.setData1(iReligion)
        popupInfo.setData2(iCityId)
        popupInfo.setData3(1)
        popupInfo.setText(u"showWonderMovie")
        popupInfo.addPopup(iFounder)

    if (not self.__LOG_RELIGION):
      return
    CvUtil.pyPrint('Player %d Civilization %s has founded %s'
      %(iFounder, player.getCivilizationName(), gc.getReligionInfo(iReligion).getDescription()))

  def onReligionSpread(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Religion Has Spread to a City'
    iReligion, iOwner, pSpreadCity = argsList
    player = PyPlayer(iOwner)
    if (not self.__LOG_RELIGIONSPREAD):
      return
    CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
      %(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

  def onReligionRemove(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Religion Has been removed from a City'
    iReligion, iOwner, pRemoveCity = argsList
    player = PyPlayer(iOwner)
    if (not self.__LOG_RELIGIONSPREAD):
      return
    CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
      %(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

  def onCorporationFounded(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Corporation Founded'
    iCorporation, iFounder = argsList
    player = PyPlayer(iFounder)

    if (not self.__LOG_RELIGION):
      return
    CvUtil.pyPrint('Player %d Civilization %s has founded %s'
      %(iFounder, player.getCivilizationName(), gc.getCorporationInfo(iCorporation).getDescription()))

  def onCorporationSpread(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Corporation Has Spread to a City'
    iCorporation, iOwner, pSpreadCity = argsList
    player = PyPlayer(iOwner)
    if (not self.__LOG_RELIGIONSPREAD):
      return
    CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
      %(gc.getCorporationInfo(iCorporation).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

  def onCorporationRemove(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Corporation Has been removed from a City'
    iCorporation, iOwner, pRemoveCity = argsList
    player = PyPlayer(iOwner)
    if (not self.__LOG_RELIGIONSPREAD):
      return
    CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
      %(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))

  def onGoldenAge(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'Golden Age'
    iPlayer = argsList[0]
    player = PyPlayer(iPlayer)
    if (not self.__LOG_GOLDENAGE):
      return
    CvUtil.pyPrint('Player %d Civilization %s has begun a golden age'
      %(iPlayer, player.getCivilizationName()))

  def onEndGoldenAge(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'End Golden Age'
    iPlayer = argsList[0]
    player = PyPlayer(iPlayer)
    if (not self.__LOG_ENDGOLDENAGE):
      return
    CvUtil.pyPrint('Player %d Civilization %s golden age has ended'
      %(iPlayer, player.getCivilizationName()))

  def onChangeWar(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'War Status Changes'
    bIsWar = argsList[0]
    iTeam = argsList[1]
    iRivalTeam = argsList[2]
    if (not self.__LOG_WARPEACE):
      return
    if (bIsWar):
      strStatus = "declared war"
    else:
      strStatus = "declared peace"
    CvUtil.pyPrint('Team %d has %s on Team %d'
      %(iTeam, strStatus, iRivalTeam))

  def onChat(self, argsList):
    'Chat Message Event'
    chatMessage = "%s" %(argsList[0],)

  def onSetPlayerAlive(self, argsList):
    'Set Player Alive Event'
    iPlayerID = argsList[0]
    bNewValue = argsList[1]
    CvUtil.pyPrint("Player %d's alive status set to: %d" %(iPlayerID, int(bNewValue)))

  def onPlayerChangeStateReligion(self, argsList):
    'Player changes his state religion'
    iPlayer, iNewReligion, iOldReligion = argsList

  def onPlayerGoldTrade(self, argsList):
    'Player Trades gold to another player'
    iFromPlayer, iToPlayer, iGoldAmount = argsList

  def onCityBuilt(self, argsList):
    'City Built'
    city = argsList[0]
    if (city.getOwner() == gc.getGame().getActivePlayer()):
## AI AutoPlay ##
      if CyGame().getAIAutoPlay() == 0 and not CyGame().GetWorldBuilderMode():
        self.__eventEditCityNameBegin(city, False)
## AI AutoPlay ##
      #self.__eventEditCityNameBegin(city, False)
    CvUtil.pyPrint('City Built Event: %s' %(city.getName()))

    # Kolonie / Provinz ----------
    # Stadt bekommt automatisch das Koloniegebaeude
    self.doCheckCityState(city)
    # ----------------------------

  def onCityRazed(self, argsList):
    'City Razed'
    city, iPlayer = argsList
    pCity = city

#### Message - Wonder capturing ####
    if pCity.getNumWorldWonders() > 0:
      iRange = gc.getNumBuildingInfos()
      iRange2 = gc.getMAX_PLAYERS()
      for i in range(iRange):
        thisBuilding = gc.getBuildingInfo(i)
        if pCity.getNumBuilding(i) > 0:
          iBuildingClass = thisBuilding.getBuildingClassType()
          thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
          if thisBuildingClass.getMaxGlobalInstances() == 1:
            ConquerPlayer = gc.getPlayer(iPlayer)
            iConquerTeam = ConquerPlayer.getTeam()
            ConquerName = ConquerPlayer.getName()
            WonderName = thisBuilding.getDescription()
            iX = pCity.getX()
            iY = pCity.getY()
            for iAllPlayer in range (iRange2):
              ThisPlayer = gc.getPlayer(iAllPlayer)
              iThisPlayer = ThisPlayer.getID()
              iThisTeam = ThisPlayer.getTeam()
              ThisTeam = gc.getTeam(iThisTeam)
              if ThisTeam.isHasMet(iConquerTeam) and ThisPlayer.isHuman():
                if iThisPlayer == iPlayer:
                  CyInterface().addMessage(iThisPlayer,False,10,CyTranslator().getText("TXT_KEY_WONDER_RAZED_YOU",(ConquerName,WonderName)),'',0,thisBuilding.getButton(),ColorTypes(7), iX, iY, True,True)
                else:
                  CyInterface().addMessage(iThisPlayer,False,10,CyTranslator().getText("TXT_KEY_WONDER_RAZED",(ConquerName,WonderName)),'',0,thisBuilding.getButton(),ColorTypes(7), iX, iY, True,True)

# -- Owner auslesen
    iOwner = pCity.findHighestCulture()
    if iOwner == -1: iOwner = pCity.getOriginalOwner()

# - Slaves (iRand = City Population) + settled slaves and glads (Angesiedelte Sklaven und Gladiatoren erobern)
    iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
    iThisTeam = gc.getPlayer(iPlayer).getTeam()
    team = gc.getTeam(iThisTeam)
    if team.isHasTech(iTechEnslavement):
      iSlaves = city.getPopulation()
      for i in range(iSlaves):
        gc.getPlayer(iPlayer).initUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

      if gc.getPlayer(iPlayer).isHuman():
        if iSlaves == 1:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_1",(0,0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
        else:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_2",(iSlaves,0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
      elif gc.getPlayer(iOwner).isHuman():
        if iSlaves == 1:
          CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_3",(pCity.getName(),0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        else:
          CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_4",(pCity.getName(),iSlaves)), None, 2, None, ColorTypes(7), 0, 0, False, False)


    if gc.getPlayer(iOwner).isAlive():
      # - Nearest city revolts
      if iOwner > -1 and iOwner != iPlayer:
        self.doNextCityRevolt(pCity.getX(), pCity.getY(), iOwner, iPlayer)

# --- Partisans!
#    if pCity.canConscript():
    # Seek Plots
      rebelPlotArray = []
      PartisanPlot1 = []
      PartisanPlot2 = []
      for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
            if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
              if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                if loopPlot.isHills(): PartisanPlot1.append(loopPlot)
                else: PartisanPlot2.append(loopPlot)
      if len(PartisanPlot1) > 0: rebelPlotArray = PartisanPlot1
      else: rebelPlotArray = PartisanPlot2

      # Set Partisans
      if len(rebelPlotArray) > 0:
          # var team kommt slaves weiter oben
          #iThisTeam = gc.getPlayer(iPlayer).getTeam()
          #team = gc.getTeam(iThisTeam)
          if team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),0,0):   iUnitType = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
          elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN"),0,0): iUnitType = gc.getInfoTypeForString("UNIT_AXEMAN")
          elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG")):  iUnitType = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
          else: iUnitType = gc.getInfoTypeForString("UNIT_WARRIOR")

          # Number of Partisans
          iAnzahl = self.myRandom(pCity.getPopulation(), None) + 1

          for i in range(iAnzahl):
            iPlot = self.myRandom(len(rebelPlotArray), None)
            pUnit = gc.getPlayer(iOwner).initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            iDamage = self.myRandom(50, None)
            pUnit.setDamage( iDamage, iOwner )


# - Partisans!
#    if pCity.canConscript():
#      if iOwner != -1 and iPlayer != -1:
#        owner = gc.getPlayer(iOwner)
#        if not owner.isBarbarian() and owner.getNumCities() > 0:
#          if gc.getTeam(owner.getTeam()).isAtWar(gc.getPlayer(iPlayer).getTeam()):
#            if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#              iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_PARTISANS')
#              if iEvent != -1 and gc.getGame().isEventActive(iEvent) and owner.getEventTriggerWeight(iEvent) >= 0:
#                triggerData = owner.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iOwner, pCity.getID(), -1, -1, -1, -1)

    CvUtil.pyPrint("City Razed Event: %s" %(city.getName(),))

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadt razed (Zeile 3116)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  def onCityAcquired(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'City Acquired'
    iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
    CvUtil.pyPrint('City Acquired Event: %s' %(pCity.getName()))
    pPlayer = gc.getPlayer(iNewOwner)
    pPlot = CyMap().plot(pCity.getX(),pCity.getY())
    # Szenarien
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()

    # PAE Debug Mark
    #"""

    # +++++ Scenario: FirstPunicWar - Start
    if sScenarioScriptData == "FirstPunicWar":
      iCivRome = 0  # Capital: Rome
      iCivCarthage = 1 # Capital: Carthage
      sData = pCity.plot().getScriptData()
      if sData == "Rome" and iNewOwner != iCivRome or sData == "Carthage" and iNewOwner == iCivRome:

        # PAE Movie
        if gc.getPlayer(iNewOwner).isHuman():
          if iNewOwner == iCivRome: iMovie = 1
          else: iMovie = 2
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
          popupInfo.setData1(iMovie) # dynamicID in CvWonderMovieScreen
          popupInfo.setData2(0) # fix pCity.getID()
          popupInfo.setData3(3) # fix PAE Movie ID for victory movies
          popupInfo.setText(u"showWonderMovie")
          popupInfo.addPopup(iNewOwner)

        gc.getGame().setWinner(gc.getPlayer(iNewOwner).getTeam(),2)
    # +++++ Scenario: FirstPunicWar - End


# PAE triumph movies when city is reconquered
    if gc.getPlayer(iNewOwner).isHuman():
        if pCity.getOriginalOwner() == iNewOwner:

          if gc.getPlayer(iNewOwner).getCurrentEra() > 2: iVids = 3
          elif gc.getPlayer(iNewOwner).getCurrentEra() > 1: iVids = 2
          else: iVids = 1
          # GG dying movies starts at no 3 (CvWonderMovieScreen)
          iMovie = 1 + self.myRandom(iVids, None)

          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
          popupInfo.setData1(iMovie) # dynamicID in CvWonderMovieScreen
          popupInfo.setData2(-1) # fix pCity.getID()
          popupInfo.setData3(5) # fix PAE Movie ID for reconquering cities
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
        for j in range (iNumCities):
          lCityNames.append(pP.getCity(j).getName())

      NewCityName = ""
      # range a,b: a <= x < b (!)
      for i in range(1,138):
        if i < 10: zus = "0" + str(i)
        else: zus = str(i)

        BarbCityName = CyTranslator().getText("TXT_KEY_CITY_NAME_B" + zus,())
        if pCity.getName() == BarbCityName:
          NewCityName = CyTranslator().getText("TXT_KEY_CITY_NAME_C" + zus,())
          if NewCityName != "" and  NewCityName != "NONE":
            if NewCityName not in lCityNames:
              pCity.setName(NewCityName,0)
          break

      # Rename City to CityNameList when there is no B->C entry
      # Nicht bei Szenarien verwenden (sScenarioScriptData wird ganz oben initialisiert)
      if NewCityName == "" and sScenarioScriptData == "":
         pCity.setName(gc.getPlayer(iNewOwner).getNewCityName(),0)
# ---------------

# Provinzpalast muss raus
    iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
    if pCity.isHasBuilding(iBuilding):
       pCity.setNumRealBuilding(iBuilding,0)

# Palisade - Stadtmauer - Hohe/Breite Mauern
    iBuildingPalisade = gc.getInfoTypeForString("BUILDING_PALISADE")
    # prereq: BUILDINGCLASS_PALISADE
    iBuildingWalls1 = gc.getInfoTypeForString("BUILDING_WALLS")
    iBuildingWalls2 = gc.getInfoTypeForString("BUILDING_OPPIDUM")
    # prereq: BUILDINGCLASS_WALLS
    iBuildingHighWalls1 = gc.getInfoTypeForString("BUILDING_HIGH_WALLS")
    iBuildingHighWalls2 = gc.getInfoTypeForString("BUILDING_CELTIC_DUN")
    iBuildingHighWalls3 = gc.getInfoTypeForString("BUILDING_HIGH_WALLS_GRECO")
    if pCity.isHasBuilding(iBuildingHighWalls1) or pCity.isHasBuilding(iBuildingHighWalls2) or pCity.isHasBuilding(iBuildingHighWalls3):
      if not (pCity.isHasBuilding(iBuildingWalls1) and pCity.isHasBuilding(iBuildingWalls2)):
        iBuilding = gc.getCivilizationInfo(gc.getPlayer(iPreviousOwner).getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_WALLS"))
        pCity.setNumRealBuilding(iBuilding,1)
    if pCity.isHasBuilding(iBuildingWalls1) or pCity.isHasBuilding(iBuildingWalls2):
      if not pCity.isHasBuilding(iBuildingPalisade):
        pCity.setNumRealBuilding(iBuildingPalisade,1)

# Spezialgebaeude muessen raus, weil nicht die Building_X erobert werden, sondern die BuildingClass_X !!!
    for i in range(9):
     iBuilding = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_SPECIAL"+str(i+1)))
     if iBuilding != None and iBuilding != -1:
       if pCity.isHasBuilding(iBuilding):
         pCity.setNumRealBuilding(iBuilding,0)
# Andere Spezialgebaeude muessen raus
    iBuilding = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_SAEULE"))
    if iBuilding != None and iBuilding != -1:
       if pCity.isHasBuilding(iBuilding):
         pCity.setNumRealBuilding(iBuilding,0)

# Sklaven sollen aus Tempeln reduziert werden
    if (not bTrade or bConquest):
     TempleArray = []
     TempleArray.append(gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_ROME_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE"))
     TempleArray.append(gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE"))
     for iTemple in TempleArray:
      if pCity.isHasBuilding(iTemple):
        iCulture = pCity.getBuildingCommerceByBuilding(2, iTemple)
        if iCulture > 3: iCulture = int(iCulture/2)
        else: iCulture = 0
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iTemple).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)


# ------- Create partisans and slaves, catch great people (only during active war), nearest city riots
    if gc.getTeam(gc.getPlayer(iPreviousOwner).getTeam()).isAtWar(gc.getPlayer(iNewOwner).getTeam()):

# --- Partisans!
      if (not bTrade or bConquest) and not gc.getPlayer(iNewOwner).isBarbarian() and gc.getPlayer(iPreviousOwner).isAlive():
        # Seek Plots
        rebelPlotArray = []
        PartisanPlot1 = []
        PartisanPlot2 = []
        for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
            if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
              if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                if loopPlot.isHills(): PartisanPlot1.append(loopPlot)
                else: PartisanPlot2.append(loopPlot)
        if len(PartisanPlot1) > 0: rebelPlotArray = PartisanPlot1
        else: rebelPlotArray = PartisanPlot2

        # Set Partisans
        if len(rebelPlotArray) > 0:
          iThisTeam = gc.getPlayer(iPreviousOwner).getTeam()
          team = gc.getTeam(iThisTeam)
          if team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),0,0):
            iUnitType = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
          elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN"),0,0):
            iUnitType = gc.getInfoTypeForString("UNIT_AXEMAN")
          elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG")):
            iUnitType = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
          else: iUnitType = gc.getInfoTypeForString("UNIT_WARRIOR")

          # Number of Partisans
          iAnzahl = self.myRandom(pCity.getPopulation()/2, None) + 1

          for i in range(iAnzahl):
            iPlot = self.myRandom(len(rebelPlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            iDamage = self.myRandom(50, None)
            pUnit.setDamage( iDamage, iPreviousOwner )

          # PAE V: Reservisten
          iAnzahl = pCity.getFreeSpecialistCount(19)
          pCity.setFreeSpecialistCount(19,0)
          for i in range(iAnzahl):
            iPlot = self.myRandom(len(rebelPlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            iDamage = self.myRandom(25, None)
            pUnit.setDamage( iDamage, iPreviousOwner )
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

        #iOwner = pCity.findHighestCulture()
#        if iPreviousOwner != -1 and iNewOwner != -1:
#          owner = gc.getPlayer(iPreviousOwner)
#          if not owner.isBarbarian() and owner.getNumCities() > 0:
#            if gc.getTeam(owner.getTeam()).isAtWar(gc.getPlayer(iNewOwner).getTeam()):
#              if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#                iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_PARTISANS')
#                if iEvent != -1 and gc.getGame().isEventActive(iEvent) and owner.getEventTriggerWeight(iEvent) >= 0:
#                  triggerData = owner.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iPreviousOwner, pCity.getID(), -1, -1, -1, -1)
# --- Ende Partisans -------------------------

# --- Slaves (max num = City Population)
      iSlaves = self.myRandom(pCity.getPopulation()-1, None) + 1
      # Trait Aggressive: Slaves * 2
      if gc.getPlayer(iNewOwner).hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")): iSlaves *= 2
      iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
      iThisTeam = gc.getPlayer(iNewOwner).getTeam()
      team = gc.getTeam(iThisTeam)
      if team.isHasTech(iTechEnslavement):
        for i in range(iSlaves):
          gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        if gc.getPlayer(iNewOwner).isHuman():
          if iSlaves == 1:
            CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_1",(0,0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
          else:
            CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_2",(iSlaves,0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
        elif gc.getPlayer(iPreviousOwner).isHuman():
          if iSlaves == 1:
            CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_3",(pCity.getName(),0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
          else:
            CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_4",(pCity.getName(),iSlaves)), None, 2, None, ColorTypes(7), 0, 0, False, False)

      if gc.getPlayer(iNewOwner).hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")): iSlaves /= 2 # Trait Aggressive: Popverlust bleibt gleich / loss of pop remains the same
      iSetPop = pCity.getPopulation() - iSlaves
      if iSetPop < 1: iSetPop = 1
      pCity.setPopulation(iSetPop)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadt erobert (Zeile 3182)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ---- Settled slaves -> Freed Slaves (Befreite Sklaven)
      iCitySlaves = pCity.getFreeSpecialistCount(16) + pCity.getFreeSpecialistCount(17) + pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE = 15,17,18
      iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 16
      # Settled slaves => 0
      pCity.setFreeSpecialistCount(15,0)
      pCity.setFreeSpecialistCount(16,0)
      pCity.setFreeSpecialistCount(17,0)
      pCity.setFreeSpecialistCount(18,0)
      # Sklavenmarkt wird entfernt (PAE V Beta 2 Patch 7)
      #if iCitySlaves > 0:
      #  iBuildingSklavenmarkt = gc.getInfoTypeForString('BUILDING_SKLAVENMARKT')
      #  if pCity.isHasBuilding(iBuildingSklavenmarkt):
      #    pCity.setNumRealBuilding(iBuildingSklavenmarkt,0)

      iFreedSlaves = iCitySlaves + iCityGlads
      if iFreedSlaves > 0:
        for i in range(iFreedSlaves):
          iRand = self.myRandom(20, None)
          NewUnit = ""
          if iRand == 0:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_1",(0,0))
          elif iRand == 1:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_UNSTERBLICH'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_COUNTER, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_2",(0,0))
          elif iRand == 2:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_COMPOSITE_ARCHER'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_3",(0,0))
          elif iRand == 3:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_SPY'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_SPY, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_4",(0,0))
          elif iRand == 4:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_HOPLIT'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_5",(0,0))
          elif iRand == 5:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_ARCHER_KRETA'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_6",(0,0))
          elif iRand == 6:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_CELTIC_GALLIC_WARRIOR'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_7",(0,0))
          elif iRand == 7:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_BALEAREN'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_COUNTER, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_8",(0,0))
          elif iRand == 8:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_GERMANNE'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_9",(0,0))
          else:
            gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_FREED_SLAVE'),  pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_CITY_SPECIAL, DirectionTypes.DIRECTION_SOUTH)
            text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_0",(0,0))

          if gc.getPlayer(iNewOwner).isHuman():
            CyInterface().addMessage(iNewOwner, True, 12, text, None, 2, None, ColorTypes(8), 0, 0, False, False)

          iPromoCombat1 = gc.getInfoTypeForString("PROMOTION_COMBAT1")
          iPromoCombat2 = gc.getInfoTypeForString("PROMOTION_COMBAT2")
          if NewUnit:
            NewUnit.setHasPromotion(iPromoCombat1, True) # Combat 1
            NewUnit.setHasPromotion(iPromoCombat2, True) # Combat 2

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtsklaven befreit (Zeile 3237)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# --- Great People can be catched as unit to resettle
# --- gets captured: 50 % | can flee: 40 % | get killed: 10 %
      iCityGP1 = pCity.getFreeSpecialistCount(8) # SPECIALIST_GREAT_PRIEST
      iCityGP2 = pCity.getFreeSpecialistCount(9) # SPECIALIST_GREAT_ARTIST
      iCityGP3 = pCity.getFreeSpecialistCount(10) # SPECIALIST_GREAT_SCIENTIST
      iCityGP4 = pCity.getFreeSpecialistCount(11) # SPECIALIST_GREAT_MERCHANT
      iCityGP5 = pCity.getFreeSpecialistCount(12) # SPECIALIST_GREAT_ENGINEER
      iCityGP6 = pCity.getFreeSpecialistCount(13) # SPECIALIST_GREAT_GENERAL
      iCityGP7 = pCity.getFreeSpecialistCount(14) # SPECIALIST_GREAT_SPY
      # guenstigen Plot aussuchen
      # mit pCityPlot.getNearestLandPlot() ist es sonst immer der gleiche
      fleePlotArray = []
      for i in range(3):
        for j in range(3):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
          if None != loopPlot and not loopPlot.isNone() and not loopPlot.isCity():
            if not loopPlot.isPeak() and not loopPlot.isWater():
              if loopPlot.getNumUnits() > 0:
                iRange = loopPlot.getNumUnits()
                for n in range (iRange):
                  if loopPlot.getUnit(n).getOwner() == iPreviousOwner:
                    fleePlotArray.append(loopPlot)
                    break
              else:
                fleePlotArray.append(loopPlot)
      if len(fleePlotArray) == 0:
        pCityPlot = CyMap().plot(pCity.getX(), pCity.getY())
        fleePlotArray.append(pCityPlot.getNearestLandPlot())


      # Prophet
      if iCityGP1 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_PROPHET")
        for i in range(iCityGP1):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP1_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP1_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP1_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit, fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP1_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP1_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP1_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP1_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP1_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP1_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
      # Artist
      if iCityGP2 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_ARTIST")
        for i in range(iCityGP2):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP2_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP2_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP2_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP2_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP2_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP2_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP2_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP2_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP2_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
      # Scientist
      if iCityGP3 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_SCIENTIST")
        for i in range(iCityGP3):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP3_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP3_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP3_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP3_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP3_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP3_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP3_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP3_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP3_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
      # Merchant
      if iCityGP4 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_MERCHANT")
        for i in range(iCityGP4):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP4_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP4_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP4_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP4_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP4_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP4_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP4_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP4_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP4_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
      # Engineer
      if iCityGP5 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_ENGINEER")
        for i in range(iCityGP5):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = self.myRandom(3, None)
              if iRand == 0:   text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP5_1",(0,0))
              elif iRand == 1: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP5_2",(0,0))
              elif iRand == 2: text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP5_3",(0,0))
              CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(3, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP5_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(4, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP5_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
      # General
      if iCityGP6 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_GREAT_GENERAL")
        for i in range(iCityGP6):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(11, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP6_"+str(iRand),(0,0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(3, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP6_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(10, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP6_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
      # Spy
      if iCityGP7 > 0:
        iNewUnit = gc.getInfoTypeForString("UNIT_GREAT_SPY")
        for i in range(iCityGP7):
          iRand = self.myRandom(10, None)
          if iRand < 5:
            gc.getPlayer(iNewOwner).initUnit(iNewUnit,  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(4, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP7_"+str(iRand),(0,0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
          elif iRand < 9 and gc.getPlayer(iPreviousOwner).isAlive():
            iJump2Plot = self.myRandom(len(fleePlotArray), None)
            pUnit = gc.getPlayer(iPreviousOwner).initUnit(iNewUnit,  fleePlotArray[iJump2Plot].getX(), fleePlotArray[iJump2Plot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            #pUnit.jumpToNearestValidPlot()
            if gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(3, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP7_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
          elif gc.getPlayer(iNewOwner).isHuman():
              iRand = 1 + self.myRandom(4, None)
              CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP7_"+str(iRand),(0,0)), None, 2, None, ColorTypes(7), 0, 0, False, False)

      pCity.setFreeSpecialistCount(8,0)
      pCity.setFreeSpecialistCount(9,0)
      pCity.setFreeSpecialistCount(10,0)
      pCity.setFreeSpecialistCount(11,0)
      pCity.setFreeSpecialistCount(12,0)
      pCity.setFreeSpecialistCount(13,0)
      pCity.setFreeSpecialistCount(14,0)
# --- Great People Catch end --


# --- Nearest city revolts 33% chance
#       CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Conquest",int(bConquest))), None, 2, None, ColorTypes(10), 0, 0, False, False)
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Trade",int(bTrade))), None, 2, None, ColorTypes(10), 0, 0, False, False)

      if bConquest and iPreviousOwner != gc.getBARBARIAN_PLAYER() and gc.getPlayer(iPreviousOwner).isAlive():
        iRand = self.myRandom(3, None)
        if iRand == 1:
          self.doNextCityRevolt(pCity.getX(), pCity.getY(), iPreviousOwner, iNewOwner)
# ---- nearest city revolts end --

# --- Getting Technology when conquering (Forschungsbonus)
      if bConquest:
       bGetTech = False
       if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ARCHIVE")) or pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_LIBRARY")): bGetTech = True

       iRand = self.myRandom(3, None)
       if iRand == 1 or bGetTech:
        bGetTech = False # falls es keine Tech gibt, dann Forschungsbonus
        TechArray = []
        iTeamOld = gc.getPlayer(iPreviousOwner).getTeam()
        pTeamOld = gc.getTeam(iTeamOld)
        iTeamNew = gc.getPlayer(iNewOwner).getTeam()
        pTeamNew = gc.getTeam(iTeamNew)

        iTechNum = gc.getNumTechInfos()
        for i in range(iTechNum):
          if pTeamOld.isHasTech(i) and not pTeamNew.isHasTech(i):
            if gc.getTechInfo(i) != None:
              if gc.getTechInfo(i).isTrade():
                TechArray.append(i)

        if len(TechArray) > 0:
          bGetTech = True
          iTechRand = self.myRandom(len(TechArray), None)
          iTech = TechArray[iTechRand]

          if gc.getPlayer(iNewOwner).getCurrentResearch() == iTech:
            pTeamNew.setResearchProgress(iTech, gc.getTechInfo(iTech).getResearchCost()-1, gc.getPlayer(iNewOwner).getID())
          pTeamNew.setHasTech(iTech, 1, iNewOwner, 0, 1)

          if gc.getPlayer(iNewOwner).isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_POPUP_GETTING_TECH",(gc.getTechInfo(iTech).getDescription (), )))
            popupInfo.addPopup(iNewOwner)
          else: gc.getPlayer(iNewOwner).clearResearchQueue()

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Tech erhalten (Zeile 3465)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

       # Forschungsbonus auf derzeitige Forschung
       if not bGetTech:
         pOldOwner = gc.getPlayer(iPreviousOwner)
         iTechOld = pOldOwner.getCurrentResearch()
         iTeamOld = pOldOwner.getTeam()
         pTeamOld = gc.getTeam(iTeamOld)

         pNewOwner = gc.getPlayer(iNewOwner)
         iTechNew = pNewOwner.getCurrentResearch()
         iTeamNew = pNewOwner.getTeam()
         pTeamNew = gc.getTeam(iTeamNew)

         #iEraPercent = gc.getEraInfo(gc.getTechInfo(iTechNew).getEra()).getResearchPercent()

         # Beim Gewinner: Ein Drittel der Zeit verkuerzen
         # Beim Verlierer: Ein Viertel der Zeit verlaengern
         # Forschungkosten != reale Kosten (+% in Era und Schwierigkeitsgrad)
         if iTechNew != -1:
           iProgress = int(gc.getTechInfo(iTechNew).getResearchCost() / 4) + pCity.getPopulation() * 10

           # Halber Wert bei unterentwickelter CIV
           if pOldOwner.getTechScore() < pNewOwner.getTechScore(): iProgress = iProgress / 2

           # No auto-grant, so set to 1 less of full amount => stimmt nicht, weil bei Cost nicht +% von Era und Schw.grad miteinberechnet wird
           #if pTeamNew.getResearchProgress(iTechNew) + iProgress >= gc.getTechInfo(iTechNew).getResearchCost():
           #  iProgress = pTeamNew.getResearchProgress(iTechNew) + iProgress - gc.getTechInfo(iTechNew).getResearchCost() - 1
           pTeamNew.changeResearchProgress(iTechNew, iProgress, gc.getPlayer(iNewOwner).getID())

           if pNewOwner.isHuman():
             CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_CONQUER_RESEARCH_WINNER",(iProgress,)), None, 2, None, ColorTypes(8), 0, 0, False, False)


         if iTechOld != -1:
           iProgress = int(gc.getTechInfo(iTechOld).getResearchCost() / 4) + pCity.getPopulation() * 10

           # Halber Wert bei unterentwickelter CIV
           if pOldOwner.getTechScore() < pNewOwner.getTechScore(): iProgress = iProgress / 2

           pTeamOld.changeResearchProgress(iTechOld, -iProgress, iPreviousOwner)

           if pOldOwner.isHuman():
             CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_CONQUER_RESEARCH_LOSER",(iProgress,)), None, 2, None, ColorTypes(7), 0, 0, False, False)


# --- Getting goldkarren / treasure / Beutegold ------
      iBeute = int(pCity.getPopulation() / 2)
      if iBeute > 0:
        for i in range (iBeute):
          gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_GOLDKARREN'),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Beutegold erhalten (Zeile 3475)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# --- Bevoelkerungszuwachs bei Nachbarstaedten (50% Chance pro Stadt fuer + 1 Pop)
      for x in range(11):
        for y in range(11):
          loopPlot = gc.getMap().plot(pCity.getX() - 5 + x, pCity.getY() - 5 + y)
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isCity():
              loopCity = loopPlot.getPlotCity()
              if loopCity.getOwner() != iNewOwner and loopCity.getOwner() > -1:
                iRand = self.myRandom(2, None)
                if iRand == 1:
                  loopCity.changePopulation(1)
                  if gc.getPlayer(loopCity.getOwner()).isHuman():
                    CyInterface().addMessage(loopCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_POP",(pCity.getName(),loopCity.getName())), None, 2, "Art/Interface/Buttons/Units/button_emigrant.dds", ColorTypes(13), loopCity.getX(), loopCity.getY(), True, True)

                  # Kultur
                  iCulture = pCity.getCulture(loopCity.getOwner())
                  iPop = loopCity.getPopulation()
                  if iCulture > 1 and iPop > 0:
                    iChangeCulture = iCulture / iPop
                    loopCity.changeCulture(iPreviousOwner,iChangeCulture,0)

                  # PAE Provinzcheck
                  self.doCheckCityState(loopCity)

                  # ***TEST***
                  #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtpop gewachsen durch Krieg (Zeile 3493)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # PAE Provinzcheck
      self.doCheckCityState(pCity)

# -------------------------------------
# --- Vasallen-Feature / Vassal feature
      # iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
      if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES) and gc.getPlayer(iPreviousOwner).isAlive():
       pWinner = gc.getPlayer(iNewOwner)
       iWinnerTeam = pWinner.getTeam()
       pWinnerTeam = gc.getTeam(iWinnerTeam)

       # Der Gewinner muss die TECH Vassallentum erforscht haben
       iTechVasallentum = gc.getInfoTypeForString("TECH_VASALLENTUM")
       if pWinnerTeam.isHasTech(iTechVasallentum) and iNewOwner != gc.getBARBARIAN_PLAYER():

        pLoser = gc.getPlayer(iPreviousOwner)
        iLoserTeam = pLoser.getTeam()
        pLoserTeam = gc.getTeam(iLoserTeam)
        iLoserPowerWithVassals = pLoserTeam.getPower(True) # mit Vasallen
        iWinnerPower = pWinnerTeam.getPower(True) # mit Vasallen

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Winner Power",iWinnerPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Loser Power",iLoserPowerWithVassals)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Hegemon verliert eine Stadt, Vasallen werden gecheckt
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
         pPlayer = gc.getPlayer(i)
         iVassal = gc.getPlayer(i).getID()
         if pPlayer.isAlive():
          iTeam = pPlayer.getTeam()
          pTeam = gc.getTeam(iTeam)
          if pTeam.isVassal(pLoserTeam.getID()):
            iVassalPower = pTeam.getPower(True)

            iLoserPower = iLoserPowerWithVassals - iVassalPower

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Hegemon Power",iLoserPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Vasall Power",iVassalPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Wenn Vasall gemeinsam mit dem Feind staerker als Hegemon ist
            # weiters trotzdem loyal zum Hegemon 1:3
            if iVassalPower + iWinnerPower > iLoserPower and 10 > ( self.myRandom(30, None) + pPlayer.AI_getAttitude(iPreviousOwner) - pPlayer.AI_getAttitude(iNewOwner) ):

              # ***TEST***
              #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Vassal interaction",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

              # Initials
              iWinnerGold = pWinner.getGold()

              # 1/3 Gold, aber mind. > 300
              if iVassalPower > iLoserPower - iLoserPower/3 + 1:
                fGold = 0.33
                iMinGold = 300

              # 1/2 Gold, aber mind. > 400
              elif iVassalPower > iLoserPower / 2:
                fGold = 0.5
                iMinGold = 400

              # 2/3 Gold, aber mind. > 500
              else:
                fGold = 0.66
                iMinGold = 500


              # HI Vassal
              # ------------------------------
              if pPlayer.isHuman():
                # Wir sind staerker als der Hegemon
                if iVassalPower > iLoserPower:

                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09",(pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0),pPlayer.getCivilizationAdjective(3))) )
                    popupInfo.setData1(iNewOwner)
                    popupInfo.setData2(iPreviousOwner)
                    popupInfo.setData3(iVassal)
                    popupInfo.setOnClickedPythonCallback("popupVassal09") # EntryPoints/CvScreenInterface und CvGameUtils / 688
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_YES",(pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0))), "")
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_NO", (pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0))), "")
                    popupInfo.addPopup(iVassal)

                # Gemeinsam sind wir staerker als der Hegemon
                # HI-HI-Interaktion
                elif pWinner.isHuman() and iWinnerGold >= iMinGold:
                    iBribe = int(iWinnerGold * fGold)
                    if iMinGold > iBribe: iBribe = iMinGold

                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10",(pCity.getName(), pPlayer.getCivilizationAdjective(3), gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription() )) )
                    popupInfo.setData1(iNewOwner)
                    popupInfo.setData2(iPreviousOwner)
                    popupInfo.setData3(iVassal)
                    popupInfo.setFlags(iBribe)
                    popupInfo.setOnClickedPythonCallback("popupVassal10") # EntryPoints/CvScreenInterface und CvGameUtils / 689
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10_YES",(gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription(),iBribe)), "")
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10_NO", (gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription(),)), "")
                    popupInfo.addPopup(iNewOwner)


                # HI-KI Interaktion
                elif iWinnerGold >= iMinGold:
                  iBribe = int(iWinnerGold * fGold)
                  if iMinGold > iBribe: iBribe = iMinGold

                  # KI bietet zu 50% ein Angebot an
                  if 1 > self.myRandom(2, None):
                      popupInfo = CyPopupInfo()
                      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iBribe,pWinner.getCivilizationShortDescription(0))) )
                      popupInfo.setData1(iNewOwner)
                      popupInfo.setData2(iPreviousOwner)
                      popupInfo.setData3(iVassal)
                      popupInfo.setFlags(iBribe)
                      popupInfo.setOnClickedPythonCallback("popupVassal11") # EntryPoints/CvScreenInterface und CvGameUtils / 690
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription())), "")
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_NO",()), "")
                      iRand = 1 + self.myRandom(9, None)
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
                      popupInfo.addPopup(iVassal)

                  # Winner hat kein Interesse
                  # Vasall darf entscheiden, ob er Krieg erklaert
                  else:
                      popupInfo = CyPopupInfo()
                      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
                      popupInfo.setData1(iNewOwner)
                      popupInfo.setData2(iPreviousOwner)
                      popupInfo.setData3(iVassal)
                      popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
                      popupInfo.addPopup(iVassal)

                # Winner hat kein Gold
                # Vasall darf entscheiden, ob er Krieg erklaert
                else:
                      popupInfo = CyPopupInfo()
                      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_13",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
                      popupInfo.setData1(iNewOwner)
                      popupInfo.setData2(iPreviousOwner)
                      popupInfo.setData3(iVassal)
                      popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
                      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
                      popupInfo.addPopup(iVassal)

                # ------------------------------

              # HI Winner
              # ----------------------------
              elif pWinner.isHuman():
                iBribe = int(iWinnerGold * fGold)
                if iMinGold > iBribe: iBribe = iMinGold

                if iWinnerGold >= iBribe:
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08",(pPlayer.getCivilizationShortDescription(0),gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),iBribe)) )
                    popupInfo.setData1(iNewOwner)
                    popupInfo.setData2(iPreviousOwner)
                    popupInfo.setData3(iVassal)
                    popupInfo.setFlags(iBribe)
                    popupInfo.setOnClickedPythonCallback("popupVassal08") # EntryPoints/CvScreenInterface und CvGameUtils / 687
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08_YES",(pLoser.getCivilizationShortDescription(0),iBribe)), "")
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08_NO",()), "")
                    popupInfo.addPopup(iNewOwner)

              # KI Vassal
              # ------------------------------
              else:
                bDeclareWar = False
                if iVassalPower > iLoserPower:
                  # 2/3 Chance, dass Vasall dem Hegemon Krieg erklaert
                  if 2 > self.myRandom(3, None):
                    bDeclareWar = True

                # KI-KI-Interaktion
                # Winner hat mehr als das erforderte Gold, Akzeptanz: Winner: 50%, Loser: 100%
                if not bDeclareWar and iMinGold <= iWinnerGold * fGold:
                    if 1 > self.myRandom(2, None):
                      bDeclareWar = True
                      pPlayer.changeGold(int(iWinnerGold * fGold))
                      pWinner.changeGold(int(iWinnerGold * fGold) * (-1))

                # Winner hat das mindest geforderte Gold, Akzeptanz: Winner: 100%, Loser: 50%
                if not bDeclareWar and iWinnerGold >= iMinGold:
                    if 1 > self.myRandom(2, None):
                      bDeclareWar = True
                      pPlayer.changeGold(iMinGold)
                      pWinner.changeGold(iMinGold * (-1))

                if bDeclareWar:
                  #pHegemonTeam.freeVassal(iTeam)
                  pTeam.declareWar(iLoserTeam, 0, 4)
                  if pWinner.isHuman():
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_1",(pTeam.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pTeam.getLeaderType()).getDescription(),)) )
                    popupInfo.addPopup(iNewOwner)

        # Hegemon verliert Stadt Ende -----


        # ------------
        # Wenn man selbst eine Stadt verliert
        # Loser und Winner-Werte von oben
        # ------------

        # -------------------------------
        # Wird der Verlierer zum Vasall ?
        iMinimumCities = 5
        if pLoser.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")): iMinimumCities = 3

        if iLoserPowerWithVassals < iWinnerPower and pLoser.getNumCities() > 0 and pLoser.getNumCities() < iMinimumCities and iNewOwner != gc.getBARBARIAN_PLAYER() and iPreviousOwner != gc.getBARBARIAN_PLAYER():
         #Abfrage ob man als Gewinner den Schwaecheren zum Vasall nimmt
         # HI-HI
         if pWinner.isHuman() and pLoser.isHuman():
          self.VassalHItoHI (iNewOwner, iPreviousOwner, pCity)

         # KI bietet der HI Vasallenstatus an, 120% - 10% pro Stadt
         elif pWinner.isHuman():
          if 12 - pLoser.getNumCities() > self.myRandom(10, None):
              iGold = pLoser.getGold() / 2 + self.myRandom(pLoser.getGold() / 2, None)
              iGold = int(iGold)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0),iGold)) )
              popupInfo.setData1(iNewOwner)
              popupInfo.setData2(iPreviousOwner)
              popupInfo.setData3(iGold)
              popupInfo.setFlags(0) # to Loser
              popupInfo.setOnClickedPythonCallback("popupVassal01") # EntryPoints/CvScreenInterface und CvGameUtils / 671
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_YES",()), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_NO",()), "")
              iRand = 1 + self.myRandom(9, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
              popupInfo.addPopup(iNewOwner)

         # HI: Abfrage ob HI als Verlierer Vasall werden will
         elif pLoser.isHuman():
              iGold = pLoser.getGold() / 2 + self.myRandom(pLoser.getGold() / 2, None)
              iGold = int(iGold)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_02",(pCity.getName(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iGold)) )
              popupInfo.setData1(iNewOwner)
              popupInfo.setData2(iPreviousOwner)
              popupInfo.setData3(iGold)
              popupInfo.setFlags(1) # to Winner
              popupInfo.setOnClickedPythonCallback("popupVassal01") # EntryPoints/CvScreenInterface und CvGameUtils / 671
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_02_YES",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(), pWinner.getCivilizationShortDescription(0))), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_NO",()), "")
              iRand = 1 + self.myRandom(9, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
              popupInfo.addPopup(iPreviousOwner)

         # KI-KI Vasall, 120% - 10% pro Stadt
         else:
          if 12 - pLoser.getNumCities() > self.myRandom(10, None):
            pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
            self.VassalHegemonGetsVassal(iPreviousOwner) # Hegemon verliert seine Vasallen
            iGold = pLoser.getGold() / 2 + self.myRandom(pLoser.getGold() / 2, None)
            pWinner.changeGold(iGold)
            pLoser.changeGold(iGold * (-1))

# ---------------------------------------------
      # PAE Debug Mark
      #"""


  # Hegemon verliert seine Vasallen
  def VassalHegemonGetsVassal (self, iHegemon):
      pHegemon = gc.getPlayer(iHegemon)
      iHegemonTeam = pHegemon.getTeam()
      pHegemonTeam = gc.getTeam(iHegemonTeam)
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        pPlayer = gc.getPlayer(i)
        if pPlayer.isAlive():
          iTeam = pPlayer.getTeam()
          pTeam = gc.getTeam(iTeam)
          if pTeam.isVassal(pHegemonTeam.getID()):
            pTeam.assignVassal (-1, 0)


  def VassalHItoHI (self, iNewOwner, iPreviousOwner, pCity):
              pLoser = gc.getPlayer(iPreviousOwner)
              iLoserTeam = pLoser.getTeam()
              pLoserTeam = gc.getTeam(iLoserTeam)
              iLoserPower = pLoserTeam.getPower(False) # ohne Vasallen
              iLoserPowerWithVassals = pLoserTeam.getPower(True) # mit Vasallen
              pWinner = gc.getPlayer(iNewOwner)
              iWinnerTeam = pWinner.getTeam()
              pWinnerTeam = gc.getTeam(iWinnerTeam)
              iWinnerPower = pWinnerTeam.getPower(True) # mit Vasallen
              # HI-HI Interaktion
              # 1) Der Loser darf beginnen und sich als Vasall vorschlagen
              # 1a) Wenn negativ, dann soll Winner eine Meldung bekommen und dem Loser einen Vorschlag unterbreiten => 2
              # 1b) Der Winner darf entscheiden, ob der Vorschlag angenommen wird
              # 2) Der Loser darf entscheiden, ob er mit dem Angebot des Winners Vasall wird
              iGold1 = self.myRandom(pLoser.getGold() / 2, None)
              if iGold1 < pLoser.getGold() / 4: iGold1 = pLoser.getGold() / 4
              iGold2 = iGold1 * 2
              iGold1 = int(iGold1)
              iGold2 = int(iGold2)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              if iLoserPower < iWinnerPower / 2: szBuffer = "TXT_KEY_POPUP_VASSAL_03_A"
              elif iLoserPower < iWinnerPower - iWinnerPower / 3:
                # Gemeinsam mit unseren Vasallen
                if iLoserPower < iLoserPowerWithVassals: szBuffer = "TXT_KEY_POPUP_VASSAL_03_C"
                else: szBuffer = "TXT_KEY_POPUP_VASSAL_03_B"
              else: szBuffer = "TXT_KEY_POPUP_VASSAL_03_D"

              if pCity == None:
                CityName = ""
                szBuffer = "TXT_KEY_POPUP_VASSAL_03_E"
              else:
                CityName = pCity.getName()
              popupInfo.setText( CyTranslator().getText(szBuffer,(CityName,pWinner.getCivilizationAdjective(2),pWinner.getCivilizationShortDescription(0))) )
              popupInfo.setData1(iNewOwner)
              popupInfo.setData2(iPreviousOwner)
              popupInfo.setData3(iGold1)
              popupInfo.setFlags(iGold2)
              popupInfo.setOnClickedPythonCallback("popupVassal03") # EntryPoints/CvScreenInterface und CvGameUtils / 682
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_1",(pWinner.getCivilizationShortDescription(0),iGold1)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_2",(pWinner.getCivilizationShortDescription(0),iGold2)), "")
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_NO",()), "")
              popupInfo.addPopup(iPreviousOwner)

# ---------------------------------------------

  def onCityAcquiredAndKept(self, argsList):
    'City Acquired and Kept'
    iOwner,pCity = argsList

    # iOwner funktioniert nicht und ist immer 0 !!! Deshalb muss es aus pCity geholt werden
    iOwner = pCity.getOwner()

#### Message - Wonder capturing ####
    if pCity.getNumWorldWonders() > 0:
      iRange = gc.getNumBuildingInfos()
      iRange2 = gc.getMAX_PLAYERS()
      for i in range(iRange):
        thisBuilding = gc.getBuildingInfo(i)
        if pCity.getNumBuilding(i) > 0:
          iBuildingClass = thisBuilding.getBuildingClassType()
          thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
          if thisBuildingClass.getMaxGlobalInstances() == 1:
            ConquerPlayer = gc.getPlayer(iOwner)
            iConquerTeam = ConquerPlayer.getTeam()
            ConquerName = ConquerPlayer.getName()
            WonderName = thisBuilding.getDescription()
            iX = pCity.getX()
            iY = pCity.getY()
            for iAllPlayer in range (iRange2):
              ThisPlayer = gc.getPlayer(iAllPlayer)
              iThisPlayer = ThisPlayer.getID()
              iThisTeam = ThisPlayer.getTeam()
              ThisTeam = gc.getTeam(iThisTeam)
              if ThisTeam.isHasMet(iConquerTeam) and ThisPlayer.isHuman():
                if iThisPlayer == iOwner:
                  CyInterface().addMessage(iThisPlayer,False,10,CyTranslator().getText("TXT_KEY_WONDER_CAPTURE_YOU",(ConquerName,WonderName)),'',0,thisBuilding.getButton(),ColorTypes(8), iX, iY, True,True)
                else:
                  CyInterface().addMessage(iThisPlayer,False,10,CyTranslator().getText("TXT_KEY_WONDER_CAPTURE",(ConquerName,WonderName)),'',0,thisBuilding.getButton(),ColorTypes(7), iX, iY, True,True)
#### ----- ####

#    CvUtil.pyPrint('City Acquired and Kept Event: %s' %(pCity.getName()))

  def onCityLost(self, argsList):
    'City Lost'
    city = argsList[0]
    player = PyPlayer(city.getOwner())
    if (not self.__LOG_CITYLOST):
      return
    CvUtil.pyPrint('City %s was lost by Player %d Civilization %s'
      %(city.getName(), player.getID(), player.getCivilizationName()))

  def onCultureExpansion(self, argsList):
  ## Platy WorldBuilder ##
    if CyGame().GetWorldBuilderMode() and not CvPlatyBuilderScreen.bPython: return
  ## Platy WorldBuilder ##
    'City Culture Expansion'
    pCity = argsList[0]
    iPlayer = argsList[1]
    CvUtil.pyPrint("City %s's culture has expanded" %(pCity.getName(),))

  def onCityGrowth(self, argsList):
    'City Population Growth'
    pCity = argsList[0]
    iPlayer = argsList[1]
    pPlayer = gc.getPlayer(iPlayer)

    # AI soll zu 90% nicht mehr wachsen, wenn die Stadt ungluecklich wird
    # und zu 80% wenn ungesund wird
    # PAE V: dabei soll sie einen Getreidekarren erstellen
    bKarren = False
    if not pPlayer.isHuman():
      iChance = 0
      if pCity.goodHealth() < pCity.badHealth(False) - 1: iChance = 8
      if pCity.happyLevel() < pCity.unhappyLevel(0) - 1: iChance = 9
      if iChance > 0:
        if iChance > self.myRandom(10, None):
          pCity.changePopulation(-1)

          # Getreidekarren erstellen (20%)
          if 1 == self.myRandom(5, None):
            #Hegemon herausfinden
            pHegemon = pPlayer
            iTeam = pPlayer.getTeam()
            pTeam = gc.getTeam(iTeam)
            iRange = gc.getMAX_PLAYERS()
            for i in range(iRange):
              vPlayer = gc.getPlayer(i)
              if vPlayer.isAlive():
                iTeam = vPlayer.getTeam()
                vTeam = gc.getTeam(iTeam)
                if pTeam.isVassal(vTeam.getID()):
                  pHegemon = vPlayer
                  break

            iNewUnit = gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")
            NewUnit = pHegemon.initUnit(iNewUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            if pHegemon.isHuman():
              CyInterface().addMessage(pHegemon.getID(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GET_UNIT_SUPPLY_FOOD",(pCity.getName(),)), "AS2D_BUILD_GRANARY", 2, gc.getUnitInfo(iNewUnit).getButton(), ColorTypes(8), pCity.getX(), pCity.getY(), True, True)


#    CvUtil.pyPrint("%s has grown to size %i" %(pCity.getName(),pCity.getPopulation()))
    if pPlayer.isHuman():
       CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GROWTH",(pCity.getName(),pCity.getPopulation())), None, 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Kolonie / Provinz ----------
    self.doCheckCityState(pCity)
    # ----------------------------

    # Negatives Nahrungslager durch Stadtstatusgebaeude vermeiden (Flunky)
    if pCity.getFood() < 0: pCity.setFood(0)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadt wird Kolonie/Provinz (Zeile 3575)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  def onCityDoTurn(self, argsList):
    'City Production'
    pCity = argsList[0]
    iPlayer = argsList[1]
    # Fehlerhafter iPlayer Wert in args?
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iTeam = pPlayer.getTeam()
    pTeam = gc.getTeam(iTeam)
    pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
    popCity = pCity.getPopulation()
    iCityFoodDifference = pCity.foodDifference(True)
    iCityUnits = pCityPlot.getNumDefenders(iPlayer)

    CvAdvisorUtils.cityAdvise(pCity, iPlayer)

    # PAE Debug Mark
    #"""

    # PAE Provinzcheck
    bCheckCityState = False

    # MESSAGES: city growing
    if not gc.getGame().isHotSeat():
     if pPlayer.isHuman():
      if pCity.getFoodTurnsLeft() == 1  and pCity.foodDifference(True) > 0 and not pCity.isFoodProduction() and not pCity.AI_isEmphasize(5):
        # MESSAGE: city will grow / Stadt wird wachsen
        iPop = pCity.getPopulation() + 1
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_WILL_GROW",(pCity.getName(),iPop)), None, 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

        # MESSAGE: city gets/is unhappy / Stadt wird/ist unzufrieden
        if pCity.happyLevel() - pCity.unhappyLevel(0) <= 0:
          if pCity.happyLevel() - pCity.unhappyLevel(0) == 0:
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
          else:
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

        # MESSAGE: city gets/is unhealthy / Stadt wird/ist ungesund
        if pCity.goodHealth() - pCity.badHealth(False) <= 0:
          if pCity.goodHealth() - pCity.badHealth(False) == 0:
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
          else:
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

    # PAE V: Stadtversorgung / City supply: Troubles/Starvation because of unit maintenance in city (food)

    # NEW: Unit supply: Foodproduction * 2 (capital: *3)
    #if pCity.isCapital(): iFactor = 3
    #else: iFactor = 2
    iFactor = 1
    iMaintainUnits = iCityUnits - pCity.getYieldRate(0) * iFactor

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("YieldRate " + pCity.getName(),pCity.getYieldRate(0))), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iCityUnits",iCityUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iMaintainUnits",iMaintainUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # OLD: 1 Pop serves 2 Units
    # More units than pop: 2 units consume 1 food
    # Units - 2*Pop soll > sein als 2x FoodDiff
    #iFoodConsumption = (popCity * 2 - iCityUnits) / 2
    #iMaintainUnits = popCity * 2 + iCityFoodDifference * 2 - iCityUnits
    # Food consumption / city supply
    #if popCity > 1 and iFoodConsumption < 0: pCity.changeFood(iFoodConsumption)
    if iMaintainUnits > 0:

     # ab PAE Patch 3: nur HI
     # Handicap: 0 (Settler) - 8 (Deity) ; 5 = King
     if gc.getGame().getHandicapType() < 5 or pPlayer.isHuman():

      # choose units
      # calculate food supply from SUPPLY_WAGON
      iExtraSupply = 0
      lUnitsAll = []
      iRange = pCityPlot.getNumUnits()
      for i in range (iRange):
          if pCityPlot.getUnit(i).getUnitCombatType() != -1:
            if pCityPlot.getUnit(i).getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
               if pCityPlot.getUnit(i).getScriptData() != "":
                 iExtraSupply = int(pCityPlot.getUnit(i).getScriptData())
                 if iExtraSupply < iMaintainUnits:
                   iMaintainUnits -= iExtraSupply
                   iExtraSupply = 0
                 else:
                   iExtraSupply -= iMaintainUnits
                   iMaintainUnits = 0
                 # set new supply tickets
                 pCityPlot.getUnit(i).setScriptData(str(iExtraSupply))
            else:
              lUnitsAll.append(pCityPlot.getUnit(i))

          if iMaintainUnits == 0: break

      if iMaintainUnits > 0 and len(lUnitsAll) > 0:
        lUnits = []
        while iMaintainUnits > 0 and len(lUnitsAll) > 0:
          iRand = self.myRandom(len(lUnitsAll), None)
          lUnits.append(lUnitsAll[iRand])
          lUnitsAll.remove(lUnitsAll[iRand])
          iMaintainUnits -= 1


        # harm units
        if len(lUnits) > 0:

          # Betrifft Stadt
          # 20%: -1 Pop
          # 10%: FEATURE_SEUCHE
          iRand = self.myRandom(10, None)
          # - 1 Pop
          if iRand < 2 and popCity > 1:
            pCity.changePopulation(-1)
            bCheckCityState = True
            if pPlayer.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_2",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
          # Seuche
          elif iRand == 2:
            pCityPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_SEUCHE"),1)
            if pPlayer.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_3",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
          # less food
          else:
            # Warnung und -20% Food Storage
            iFoodStoreChange = pCity.getFood() / 100 * 20
            if pCity.getFood() > 10: pCity.changeFood(-iFoodStoreChange)
            if pPlayer.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_1",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
          # ------

          # Betrifft Einheiten
          iJumpedOut = 0
          for unit in lUnits:
             # Unit nicht mehr killen (Weihnachtsbonus :D ab 7.12.2012)
             iDamage = unit.getDamage()
             if iDamage < 70:
               unit.changeDamage(30,False)
               if gc.getPlayer(unit.getOwner()).isHuman():
                   CyInterface().addMessage(unit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_CITY",(pCity.getName(),unit.getName(),30)), None, 2, None, ColorTypes(12), unit.getX(), unit.getY(), True, True)
             else:
               iJumpedOut += 1
               if unit.getDamage() < 85: unit.setDamage(85,unit.getOwner())
               unit.jumpToNearestValidPlot()
               if gc.getPlayer(unit.getOwner()).isHuman():
                 CyInterface().addMessage(unit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4",(pCity.getName(),unit.getName())), None, 2, unit.getButton(), ColorTypes(12), unit.getX(), unit.getY(), True, True)

          # Wenn die Stadt durch Buildings stark heilt
          if iJumpedOut == 0:
               # Chance rauszuwerfen 33%
               if 1 == self.myRandom(3, None):
                 Einheiten = 1 + self.myRandom(len(lUnits), None)
                 while unit in lUnits and Einheiten > 0:
                   Einheiten -= 1
                   iRandUnit = self.myRandom(len(lUnits), None)

                   lUnits[iRandUnit].jumpToNearestValidPlot()
                   if pPlayer.isHuman():
                     CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4",(pCity.getName(),lUnits[iRandUnit].getName())), "AS2D_STRIKE", 2, lUnits[iRandUnit].getButton(), ColorTypes(7), lUnits[iRandUnit].getX(), lUnits[iRandUnit].getY(), True, True)
                    # Einheit aus dem Array werfen
                   lUnits.remove(lUnits[iRandUnit])


    # # ++++++++++++++++++++++++++++++++++++++++
    # # Buildings with prereq bonus gets checked : remove chance 10%
    # building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_BRONZE")
    # if pCity.isHasBuilding(building):
      # iRand = self.myRandom(10, None)
      # if iRand == 1:
        # bonus = gc.getInfoTypeForString("BONUS_COPPER")
        # bonus1 = gc.getInfoTypeForString("BONUS_COAL")
        # bonus2 = gc.getInfoTypeForString("BONUS_ZINN")
        # if not pCity.hasBonus(bonus) or not (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2)):
          # pCity.setNumRealBuilding(building,0)
          # # Welche Resi
          # if not pCity.hasBonus(bonus): szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1"
          # else: szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_2"
          # # Meldung
          # if pPlayer.isHuman():
            # CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText(szText,(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # popupInfo = CyPopupInfo()
            # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            # popupInfo.setText(CyTranslator().getText(szText,(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            # popupInfo.addPopup(pCity.getOwner())

    # building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_MESSING")
    # if pCity.isHasBuilding(building):
      # iRand = self.myRandom(10, None)
      # if iRand == 1:
        # bonus1 = gc.getInfoTypeForString("BONUS_COPPER")
        # bonus2 = gc.getInfoTypeForString("BONUS_ZINK")
        # if not pCity.hasBonus(bonus1) or not pCity.hasBonus(bonus2):
          # pCity.setNumRealBuilding(building,0)
          # # Welche Resi
          # if not pCity.hasBonus(bonus1): bonus = bonus1
          # elif not pCity.hasBonus(bonus2): bonus = bonus2
          # # Meldung
          # if pPlayer.isHuman():
            # CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # popupInfo = CyPopupInfo()
            # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            # popupInfo.addPopup(pCity.getOwner())

    # building = gc.getInfoTypeForString("BUILDING_BRAUSTAETTE")
    # if pCity.isHasBuilding(building):
      # iRand = self.myRandom(10, None)
      # if iRand == 1:
        # bonus1 = gc.getInfoTypeForString("BONUS_WHEAT")
        # bonus2 = gc.getInfoTypeForString("BONUS_GERSTE")
        # bonus3 = gc.getInfoTypeForString("BONUS_HAFER")
        # bonus4 = gc.getInfoTypeForString("BONUS_ROGGEN")
        # bonus5 = gc.getInfoTypeForString("BONUS_HIRSE")
        # if not (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2) or pCity.hasBonus(bonus3) or pCity.hasBonus(bonus4) or pCity.hasBonus(bonus5)):
          # pCity.setNumRealBuilding(building,0)
          # # Meldung
          # if pPlayer.isHuman():
            # CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3",(pCity.getName(),"",gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # popupInfo = CyPopupInfo()
            # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3",(pCity.getName(),"",gc.getBuildingInfo(building).getDescription())))
            # popupInfo.addPopup(pCity.getOwner())

    # building = gc.getInfoTypeForString("BUILDING_WINERY")
    # if pCity.isHasBuilding(building):
      # iRand = self.myRandom(10, None)
      # if iRand == 1:
        # bonus = gc.getInfoTypeForString("BONUS_GRAPES")
        # if not pCity.hasBonus(bonus):
          # pCity.setNumRealBuilding(building,0)
          # # Meldung
          # if pPlayer.isHuman():
            # CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # popupInfo = CyPopupInfo()
            # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            # popupInfo.addPopup(pCity.getOwner())

    # building = gc.getInfoTypeForString("BUILDING_PAPYRUSPOST")
    # if pCity.isHasBuilding(building):
      # iRand = self.myRandom(10, None)
      # if iRand == 1:
        # bonus = gc.getInfoTypeForString("BONUS_PAPYRUS")
        # if not pCity.hasBonus(bonus):
          # pCity.setNumRealBuilding(building,0)
          # # Meldung
          # if pPlayer.isHuman():
            # CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # popupInfo = CyPopupInfo()
            # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            # popupInfo.addPopup(pCity.getOwner())

    # ++++++++++++++++++++++++++++++++++++++++


    # Emigrants leave city when unhappy / Auswanderer verlassen die Stadt, wenn unzufrieden
    iTech = gc.getInfoTypeForString("TECH_COLONIZATION")
    if pTeam.isHasTech(iTech) and popCity > 3:
      iCityUnhappy = pCity.unhappyLevel(0) - pCity.happyLevel()
      iCityUnhealthy = pCity.badHealth(False) - pCity.goodHealth()
      if iCityUnhappy > 0 or iCityUnhealthy > 0:
        if iCityUnhappy < 0: iCityUnhappy = 0
        if iCityUnhealthy < 0: iCityUnhealthy = 0
        iChance = (iCityUnhappy + iCityUnhealthy) * 2 # * popCity
        iRand = self.myRandom(100, None)
        if iChance > iRand:
          iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
          NewUnit = gc.getPlayer(iPlayer).initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_SETTLE, DirectionTypes.DIRECTION_SOUTH)

          # Einheit die richtige Kultur geben
          iPlayerCulture = pCity.findHighestCulture()
          NewUnit.setScriptData(str(iPlayerCulture))
          # Kultur von der Stadt abziehen
          iCulture = pCity.getCulture(iPlayerCulture)
          pCity.changeCulture(iPlayerCulture,-(iCulture/5),1)

          popNeu = popCity - 2
          if popNeu < 1: popNeu = 1

          pCity.setPopulation(popNeu)
          self.doCheckCityState(pCity)

          if iPlayer > -1:
            if pPlayer.isHuman():
              if iCityUnhealthy > 0: text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_2",(pCity.getName(),popNeu,popCity))
              else: text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS",(pCity.getName(),popNeu,popCity))
              CyInterface().addMessage(pCity.getOwner(), True, 10, text,"AS2D_REVOLTSTART",InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Techs/button_brandschatzen.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
            else:
              self.doAIReleaseSlaves(pCity)
          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant verlaesst Stadt (Zeile 3624)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # LEPROSY (Lepra) and PLAGUE (Pest) , Lepra ab 5, Pest ab 9, CIV-Event Influenza (Grippe) ab 7
    iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')
    if pCity.isHasBuilding(iBuildingPlague): bDecline = True
    else: bDecline = False

    # Lepra ab 5
    if not bDecline and pCity.getPopulation() >= 5:

      if pCity.goodHealth() < pCity.badHealth(False):
        iRand = self.myRandom(100, None)
        iChance = 1 * (pCity.badHealth(False) - pCity.goodHealth())

        # PAE V: less chance for AI
        if not pPlayer.isHuman(): iChance = iChance / 3

        if iRand < iChance:
          iOldPop = pCity.getPopulation()

          # Leprakolonie nimmt nur 1 POP
          iBuilding = gc.getInfoTypeForString('BUILDING_LEPRAKOLONIE')
          if pCity.isHasBuilding(iBuilding):
            iNewPop = iOldPop - 1
            if pPlayer.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_LEBRA_1",(pCity.getName(), )), "AS2D_PLAGUE", 2, None, ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
          else:
            iRandPop = self.myRandom(int(round(pCity.getPopulation() / 2)), None) + 1
            iNewPop = iOldPop - iRandPop
            if iNewPop < 1: iNewPop = 1
            # City Revolt
            #pCity.setOccupationTimer(1)
            if pPlayer.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_LEBRA_2",(pCity.getName(), iNewPop, iOldPop)), "AS2D_PLAGUE", 2, None, ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

          pCity.setPopulation(iNewPop)
          bDecline = True

          if not pPlayer.isHuman(): self.doAIReleaseSlaves(pCity)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Lepra (Zeile 3660)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Pest ab 9
    if not bDecline and pCity.getPopulation() >= 9:
      if pCity.goodHealth() < pCity.badHealth(False):
        iRand = self.myRandom(100, None)
        iChance = 1 * (pCity.badHealth(False) - pCity.goodHealth())

        # PAE V: less chance for AI
        if not pPlayer.isHuman(): iChance = iChance / 3

        if iRand < iChance:
          iThisTeam = pPlayer.getTeam()
          team = gc.getTeam(iThisTeam)

          #iMedicine1 = gc.getInfoTypeForString("TECH_MEDICINE1")
          #iMedicine2 = gc.getInfoTypeForString("TECH_MEDICINE2")
          #iMedicine3 = gc.getInfoTypeForString("TECH_MEDICINE3")
          #iMedicine4 = gc.getInfoTypeForString("TECH_HEILKUNDE")

          # City Revolt
          #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4): pCity.setOccupationTimer(2)
          #else: pCity.setOccupationTimer(3)
          #pCity.setOccupationTimer(1)

          # message for all
          iRange = gc.getMAX_PLAYERS()
          for iPlayer2 in range(iRange):
            pSecondPlayer = gc.getPlayer(iPlayer2)
            iSecondPlayer = pSecondPlayer.getID()
            if (pSecondPlayer.isHuman()):
              iSecTeam = pSecondPlayer.getTeam()
              if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                if pSecondPlayer.isHuman():
                  CyInterface().addMessage(iSecondPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLOBAL",(pCity.getName(), 0)), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLOBAL",(pCity.getName(), 0)), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
          # end message

          # Plague building gets added into city
          pCity.setNumRealBuilding(iBuildingPlague,1)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pest (Zeile 3701)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Pest Auswirkungen

    # if city suffers from plague
    if pCity.isHasBuilding(iBuildingPlague):

      #iCulture = pCity.getBuildingCommerceByBuilding(2, iBuildingPlague)
      iCulture = pCity.getCulture (pPlayer.getID())

      # Calculation var
      iHappiness = pCity.getBuildingHappiness (iBuildingPlague)

      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Culture",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Happiness",iHappiness)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # Plots rundherum mit SeuchenFeature belasten
      if iHappiness == -5:
        feat_seuche = gc.getInfoTypeForString('FEATURE_SEUCHE')

        for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
            if None != loopPlot and not loopPlot.isNone():
              if not (loopPlot.isWater() or loopPlot.isPeak()) and loopPlot.getFeatureType() == -1:
                loopPlot.setFeatureType(feat_seuche,0)


      # Downgrade Improvements
      if iHappiness == -4 or iHappiness == -2:
        for i in range(5):
          for j in range(5):
            sPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)
            improv1 = gc.getInfoTypeForString('IMPROVEMENT_COTTAGE')
            improv2 = gc.getInfoTypeForString('IMPROVEMENT_HAMLET')
            improv3 = gc.getInfoTypeForString('IMPROVEMENT_VILLAGE')
            improv4 = gc.getInfoTypeForString('IMPROVEMENT_TOWN')
            iImprovement = sPlot.getImprovementType()
            # 50% chance of downgrading
            if iImprovement == improv2:
              iRand = self.myRandom(2, None)
              if iRand == 1: sPlot.setImprovementType(improv1)
            elif iImprovement == improv3:
              iRand = self.myRandom(2, None)
              if iRand == 1: sPlot.setImprovementType(improv2)
            elif iImprovement == improv4:
              iRand = self.myRandom(2, None)
              if iRand == 1: sPlot.setImprovementType(improv3)

      # decline City pop
      ThisPlayer = gc.getPlayer(iPlayer)
      iThisTeam = ThisPlayer.getTeam()
      team = gc.getTeam(iThisTeam)

      #iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
      #iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
      #iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
      #iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

      # Change City Pop
      iOldPop = pCity.getPopulation()
      # there is no medicine against plague :)
      #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4):
      # bis zu -2 pro turn
      iPopChange = 1 + self.myRandom(2, None)

      # Slaves and Glads
      iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 16
      iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE = 15
      iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD = 17
      iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD = 18

      # Pop
      iNewPop = iOldPop - iPopChange
      if iNewPop <= 1: iNewPop = 1

      # Message new Pop
      if pPlayer.isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST",(pCity.getName(), iNewPop, iOldPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

      pCity.setPopulation(iNewPop)
      # end decline city pop

      # Sklaven sterben
      # Prio: Haus, Food, Glads, Prod
      iSlaves = iCityGlads + iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
      while iSlaves > 0 and iPopChange > 0:
        if iCitySlavesHaus >= 1:
          pCity.changeFreeSpecialistCount(16, -1)
          iCitySlavesHaus -= 1
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_HAUS",(pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCitySlavesFood > 0:
          pCity.changeFreeSpecialistCount(17, -1)
          iCitySlavesFood -= 1
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_FOOD",(pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCityGlads > 0:
          pCity.changeFreeSpecialistCount(15, -1)
          iCityGlads -= 1
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLAD",(pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCitySlavesProd > 0:
          pCity.changeFreeSpecialistCount(18, -1)
          iCitySlavesProd -= 1
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_PROD",(pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        iSlaves -= 1
        iPopChange -= 1


      # Hurt and kill units
      lMessageOwners = []
      for i in range(3):
        for j in range(3):
          sPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
          iRange = sPlot.getNumUnits()
          if iRange > 0:
           for iUnit in range (iRange):
            iRand = self.myRandom(30, None) + 15

            if sPlot.getUnit(iUnit) != None:
              if sPlot.getUnit(iUnit).getDamage() + iRand < 100: sPlot.getUnit(iUnit).changeDamage(iRand, False)

              sOwner = sPlot.getUnit(iUnit).getOwner()

              if sPlot.getUnit(iUnit).getDamage() > 95:
                if gc.getPlayer(sOwner) != None:
                  if gc.getPlayer(sOwner).isHuman():
                    CyInterface().addMessage(sOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_KILL_UNIT",(sPlot.getUnit(iUnit).getName(), pCity.getName() )), None, 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(12), sPlot.getX(), sPlot.getY(), True, True)
                #sPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                sPlot.getUnit(iUnit).kill(1,sPlot.getUnit(iUnit).getOwner())

              if gc.getPlayer(sOwner) != None:
                if gc.getPlayer(sOwner).isHuman():
                  if sOwner not in lMessageOwners: lMessageOwners.append(sOwner)

      # Message
      if len(lMessageOwners) > 0:
        for i in lMessageOwners:
          CyInterface().addMessage(i, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_2",(pCity.getName(), 0)), None, 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(12), pCity.getX(),  pCity.getY(), True, True)

      # Change City Culture
      iCultureNew = iCulture - 50
      if iCultureNew > 0: pCity.setCulture (pPlayer.getID(), iCultureNew, 1)
      else: pCity.setCulture (pPlayer.getID(), 0, 0)

      # Calculation
      if iHappiness >= -1:
        # Building erneut initialisieren. CIV BUG.
        pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), 0)
        # Building entfernen
        pCity.setNumRealBuilding(iBuildingPlague,0)
        # Message
        if pPlayer.isHuman():
          CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_DONE",(pCity.getName(), iNewPop, iOldPop)), "AS2D_WELOVEKING", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(8), pCity.getX(),  pCity.getY(), True, True)

      else:
        # zum Gebaeude +1 Happiness addieren (-5,-4,..) - funkt leider nicht mit nur einer Zeile?!- Civ BUG?
        if iHappiness == -5: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +1)
        if iHappiness == -4: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +2)
        if iHappiness == -3: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +3)
        if iHappiness == -2: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +4)
        if iHappiness == -1: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +5)
        elif iHappiness < -5:
          pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), 0)
          pCity.setNumRealBuilding(iBuildingPlague,0)
          pCity.setNumRealBuilding(iBuildingPlague,1)


      # spread plague 10%
      iRand = self.myRandom(10, None)
      if iRand == 1: self.doSpreadPlague(pCity)
    # lepra end and plague end

########################################################################################

    # Slaves and gladiators (Angesiedelte Sklaven und Gladiatoren)
    iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE = 15
    iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD = 17
    iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD = 18
    iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 16
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
    pOwner = pPlayer

    # Slaves
    if iCitySlaves > 0:

      # Slaves -> Free citizen (chance 2% / 3%)
      if pOwner.isCivic(16) or pOwner.isCivic(17):
        iRand = 50
        if pOwner.isCivic(17): iRand = 33
        # Trait Philosophical: Doppelte Chance auf freie Buerger / chance of free citizens doubled
        if pOwner.hasTrait(gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL")): iRand /= 2

        if self.myRandom(iRand, None) == 1:
          pCity.changeFreeSpecialistCount(0, 1)  # Citizen = 0
          if iCitySlavesHaus > 0: pCity.changeFreeSpecialistCount(16, -1)
          elif iCitySlavesFood > 0: pCity.changeFreeSpecialistCount(17, -1)
          else: pCity.changeFreeSpecialistCount(18, -1)
          iCitySlaves -= 1
          if pOwner.isHuman():
            CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_CITIZEN",(pCity.getName(),"")),None,2,None,ColorTypes(14),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Buerger (Zeile 3828)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


      # Sklavenerhalt: Available slave (2%) - Schwaechung bei christlicher Religion
      # Wenn Sklave ansaessig ist oder bei nem Sklavenmarkt
      if iCitySlaves > 0 or pCity.getNumRealBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")) > 0:
        if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_TYRANNIS")): iChance = 30 # 3%
        else: iChance = 20 # 2% Grundwert

        iChance += iCitySlaves # pro Sklave 0.1% dazu
        if iChance > 35: iChance = 35 # 3.5%

        # Christentum:
        iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
        if pCity.isHasReligion(iReligion): iChance -= 10 # -1%
        if pOwner.getStateReligion() == iReligion: iChance -= 10 # -1%

        # For better AI
        if not pOwner.isHuman(): iChance += 5

        if self.myRandom(1000, None) < iChance:
          iUnitType = gc.getInfoTypeForString("UNIT_SLAVE")
          pOwner.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_WORKER, DirectionTypes.DIRECTION_SOUTH)
          if pOwner.isHuman():
            CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_SLAVE_BIRTH",(pCity.getName(),"")),None,2,",Art/Interface/Buttons/Civics/Slavery.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,8,2",ColorTypes(14),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Neuer Sklave verfuegbar (Zeile 3841)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Gladiators
    if iCityGlads > 0:

      # Free citizen (chance 2% / 3%)
      if pOwner.isCivic(16) or pOwner.isCivic(17):
        if pOwner.isCivic(17): iRand = self.myRandom(33, None)
        else: iRand = self.myRandom(50, None)

        if iRand == 1:
          pCity.changeFreeSpecialistCount(0, 1)  # Citizen = 0
          pCity.changeFreeSpecialistCount(15, -1) # Gladiator = 14
          iCityGlads = iCityGlads - 1
          if pOwner.isHuman():
            CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_2_CITIZEN",(pCity.getName(),"")),None,2,None,ColorTypes(14),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiator zu Buerger (Zeile 3860)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


      # Gladiator Unit (2% with gladiators)
      ThisPlayer = gc.getPlayer(iPlayer)
      iThisTeam = ThisPlayer.getTeam()
      team = gc.getTeam(iThisTeam)

      bTeamHasGladiators = False
      iTech = gc.getInfoTypeForString("TECH_GLADIATOR2")

      if iCityGlads > 0 and team.isHasTech(iTech):
        bTeamHasGladiators = True
        iRand = self.myRandom(50, None)
        if iRand == 1:
          iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")
          pOwner.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
          pCity.changeFreeSpecialistCount(15, -1)
          iCityGlads = iCityGlads - 1
          if pOwner.isHuman():
            CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_GLADIATOR",(pCity.getName(),"")),None,2,None,ColorTypes(14),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Gladiator (Zeile 3881)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


      # Gladiator is dying . pro Glad 1%., min 3%
      if iCityGlads > 0:
        if iCityGlads < 3: iChanceGlads = 3
        else: iChanceGlads = iCityGlads
        iRand = self.myRandom(100, None)
        if iChanceGlads > iRand:


          # PAE V: stehende Sklaven werden zugewiesen
          bErsatz = False
          # City Plot
          pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
          iRangeUnits = pCityPlot.getNumUnits()
          for iUnit in range (iRangeUnits):
              if pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                 #pCityPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                 pCityPlot.getUnit(iUnit).kill(1,pCityPlot.getUnit(iUnit).getOwner())
                 bErsatz = True
                 break

          if not bErsatz: pCity.changeFreeSpecialistCount(15, -1)

          if pOwner.isHuman():
            iBuilding1 = gc.getInfoTypeForString('BUILDING_COLOSSEUM')
            iBuilding2 = gc.getInfoTypeForString('BUILDING_BYZANTINE_HIPPODROME')

            iRand = self.myRandom(3, None)
            if iRand < 1 and pCity.isHasBuilding(iBuilding1):
              iRand = 1 + self.myRandom(5, None)
              CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_COL_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

            elif iRand < 1 and pCity.isHasBuilding(iBuilding2):
              iRand = 1 + self.myRandom(5, None)
              CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_HIP_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

            else:
              iRand = self.myRandom(14, None)
              CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

            if bErsatz:
              if bTeamHasGladiators:
                CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ2",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
              else:
                CyInterface().addMessage(pOwner.getID(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiator stirbt (Zeile 3977)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


########################################

    # Bordell / House of pleasure / Freudenhaus
    # chance of losing a slave (4%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
      if iCulture > 0:
        iRand = self.myRandom(25, None)
        if iRand == 1:
          iCulture -= 1
          pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
          if pOwner.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_BORDELL_SLAVES",(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Builds/button_bordell.dds",ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Freudemaus verschwunden (Zeile 3927)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Schule
    # chance of losing a slave (3%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_RESEARCH, iBuilding1)
      if iCulture > 0:
        iRand = self.myRandom(33, None)
        if iRand == 1:
          iCulture -= 1
          pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
          if pOwner.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SCHULE_SLAVES",(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Builds/button_schule.dds",ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Lehrer verschwunden (Zeile 3944)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Manufaktur
    # chance of losing a slave (4%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
      iFood = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0)
      iProd = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1)
      if iProd > 0 or iFood > 0:
        iRand = self.myRandom(25, None)
        if iRand == 1:
          if iProd > 0:
            iProd = iProd - 1
            pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1, iProd)
            if pOwner.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MANUFAKTUR_SLAVES_PROD",(pCity.getName(),"Art/Interface/Buttons/Corporations/button_manufaktur.dds")),None,2,"",ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
          else:
            iFood = iFood - 1
            pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0, iFood)
            if pOwner.isHuman():
              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MANUFAKTUR_SLAVES_FOOD",(pCity.getName(),"Art/Interface/Buttons/Corporations/button_manufaktur.dds")),None,2,"",ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Manufakturist draufgegangen (Zeile 3968)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Palast
    # chance of losing a slave (2%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
      if iCulture > 2:
        iRand = self.myRandom(50, None)
        if iRand < 1:
          iCulture -= 1
          pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
          if pOwner.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2PALACE_LOST",(pCity.getName(),"")),None,2,gc.getBuildingInfo(iBuilding1).getButton(),ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palastsklave verschwunden (Zeile 5016)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Tempel
    # chance of losing a slave (3%)
    iBuilding1 = gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE")
    iBuilding2 = gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE")
    iBuilding3 = gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE")
    iBuilding4 = gc.getInfoTypeForString("BUILDING_ROME_TEMPLE")
    iBuilding5 = gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE")
    iBuilding6 = gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE")
    iBuilding7 = gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE")
    iBuilding8 = gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
    if pCity.isHasBuilding(iBuilding1) or pCity.isHasBuilding(iBuilding2) or pCity.isHasBuilding(iBuilding3) \
    or pCity.isHasBuilding(iBuilding4) or pCity.isHasBuilding(iBuilding5) or pCity.isHasBuilding(iBuilding6) \
    or pCity.isHasBuilding(iBuilding7) or pCity.isHasBuilding(iBuilding8):
      TempleArray = []
      if pCity.isHasBuilding(iBuilding1) and pCity.getBuildingCommerceByBuilding(2, iBuilding1) > 2: TempleArray.append(iBuilding1)
      if pCity.isHasBuilding(iBuilding2) and pCity.getBuildingCommerceByBuilding(2, iBuilding2) > 2: TempleArray.append(iBuilding2)
      if pCity.isHasBuilding(iBuilding3) and pCity.getBuildingCommerceByBuilding(2, iBuilding3) > 2: TempleArray.append(iBuilding3)
      if pCity.isHasBuilding(iBuilding4) and pCity.getBuildingCommerceByBuilding(2, iBuilding4) > 2: TempleArray.append(iBuilding4)
      if pCity.isHasBuilding(iBuilding5) and pCity.getBuildingCommerceByBuilding(2, iBuilding5) > 2: TempleArray.append(iBuilding5)
      if pCity.isHasBuilding(iBuilding6) and pCity.getBuildingCommerceByBuilding(2, iBuilding6) > 2: TempleArray.append(iBuilding6)
      if pCity.isHasBuilding(iBuilding7) and pCity.getBuildingCommerceByBuilding(2, iBuilding7) > 2: TempleArray.append(iBuilding7)
      if pCity.isHasBuilding(iBuilding8) and pCity.getBuildingCommerceByBuilding(2, iBuilding8) > 2: TempleArray.append(iBuilding8)

      if len(TempleArray) > 0:
        if self.myRandom(33, None) < 1:
          iBuilding = self.myRandom(len(TempleArray), None)
          iCulture = pCity.getBuildingCommerceByBuilding(2, TempleArray[iBuilding])
          iCulture -= 2
          pCity.setBuildingCommerceChange(gc.getBuildingInfo(TempleArray[iBuilding]).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
          if pOwner.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2TEMPLE_LOST",(pCity.getName(),"")),None,2,gc.getBuildingInfo(TempleArray[iBuilding]).getButton(),ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Tempelsklave verschwunden (Zeile 5051)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Feuerwehr
    # chance of losing a slave (3%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_FEUERWEHR')
    if pCity.isHasBuilding(iBuilding1):
      iHappyiness = pCity.getBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType())
      if iHappyiness > 0:
        iRand = self.myRandom(33, None)
        if iRand == 1:
          iHappyiness -= 1
          pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), iHappyiness)
          if pOwner.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2FEUERWEHR_LOST",(pCity.getName(),"")),None,2,gc.getBuildingInfo(iBuilding1).getButton(),ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palastsklave verschwunden (Zeile 5016)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


########################################

    # City Rebellion
    bRebellion = False
#    iNumCities = gc.getPlayer(iPlayer).getNumCities()
#    iDistance = plotDistance(gc.getPlayer(iPlayer).getCapitalCity().getX(), gc.getPlayer(iPlayer).getCapitalCity().getY(), pCity.getX(), pCity.getY())
#
#    # Ab Klassik, wo es eine Hauptstadt geben sollte!
#    if pCity.getPopulation() > 4 and gc.getGame().getGameTurn() % 4 == 0 and ( gc.getPlayer(iPlayer).getCurrentEra() >= 3 and iDistance > 10 or (pCity.getOriginalOwner() != iPlayer and pCity.getGameTurnAcquired() + 100 > gc.getGame().getGameTurn() ) ):
#     iBuilding1 = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
#     if not (pCity.isHasBuilding(iBuilding1) or pCity.isCapital()):
#
#      pPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
##      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pCity.getName(),iDistance)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#
#      iChanceOfRebellion = pPlayer.getNumCities() * 2
#
#      iChanceOfRebellion += iDistance * 2
#
#      if pCity.isHasBuilding(gc.getInfoTypeForString('BUILDING_COURTHOUSE')): iChanceOfRebellion -= 10
#
#      iChanceOfRebellion -= pCity.getNumNationalWonders() * 10
#
#      iChanceOfRebellion -= pCity.getNumWorldWonders() * 10
#
#      iChanceOfRebellion += ( pCity.unhappyLevel(0) - pCity.happyLevel() ) * 10
#
#      iChanceOfRebellion += pPlayer.getAnarchyTurns() * 10
#
#      iChanceOfRebellion += pCity.foodDifference(1) * 10
#
#      iChanceOfRebellion -= pPlot.getNumUnits() * 10
#
#      if not pCity.isConnectedToCapital(iPlayer): iChanceOfRebellion += 30
#
#      if pCity.getOccupationTimer() > 0: iChanceOfRebellion += pCity.getOccupationTimer() * 10
#
#      if gc.getPlayer(iPlayer).getCapitalCity().getOccupationTimer() > 0: iChanceOfRebellion += pCity.getOccupationTimer() * 20
#
#      if not pCity.isHasReligion(pPlayer.getStateReligion()): iChanceOfRebellion += 20
#
      # Erbrecht 1, Militaerstaat 2, Staatseigen 18: +1
      # Dezentralisierung 16: +2
      # Repraes 3, Wahlrecht 4: -2
      # Erbrecht + Senat 9 : +1
      # Wahlrecht + Koenigl. Hof 8: +1
      # Organ. Reli 24 + Senat: +1
      # Freie Buerger 14 + Staatseigentum 18: +1
      # Freie Buerger + (Erbrecht or Militaerstaat): +1
      # Freie Buerger + (Fr. Markt 17 or Handelszentren 19): -1
#      if pPlayer.isCivic(1)  or   pPlayer.isCivic(2): iChanceOfRebellion += 10
#      if pPlayer.isCivic(16): iChanceOfRebellion += 20
#      if pPlayer.isCivic(18): iChanceOfRebellion += 10
#      if pPlayer.isCivic(3)  or   pPlayer.isCivic(4) : iChanceOfRebellion -= 20
#      if pPlayer.isCivic(1)  and  pPlayer.isCivic(9) : iChanceOfRebellion += 10
#      if pPlayer.isCivic(4)  and  pPlayer.isCivic(8) : iChanceOfRebellion += 10
#      if pPlayer.isCivic(24) and  pPlayer.isCivic(9) : iChanceOfRebellion += 10
#      if pPlayer.isCivic(14) and  pPlayer.isCivic(18): iChanceOfRebellion += 10
#      if pPlayer.isCivic(14) and (pPlayer.isCivic(1)  or pPlayer.isCivic(2)) : iChanceOfRebellion += 10
#      if pPlayer.isCivic(14) and (pPlayer.isCivic(17) or pPlayer.isCivic(19)): iChanceOfRebellion -= 20
#
#      if pPlayer.getCommercePercent(0) > 50: iChanceOfRebellion += pPlayer.getCommercePercent(0) - 50
#
#      # da nur jede 4te runde geprueft wird, etwas verstaerken
#      iChanceOfRebellion = iChanceOfRebellion * 3
#
#      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Chance of Rebellion",iChanceOfRebellion)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#
#      iRand = self.myRandom(1000, "City rebellion")
#
##      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebellion",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#
#
#      if iRand < iChanceOfRebellion:
#        bRebellion = True
#
#        # 2te ueberpruefung treue, loyale Einheiten gegenueber unzufriedene Bevoelkerung
#        iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
#        iLoyalUnits = 0
#        for iUnit in range (pPlot.getNumUnits()):
#          # Promotion Loyality = Nr 0
#          if pPlot.getUnit(iUnit).isHasPromotion(iPromoLoyal): iLoyalUnits += 1
#
#        if iLoyalUnits * 2 > pCity.unhappyLevel(0):
#
#          pCity.setOccupationTimer(int(pCity.unhappyLevel(0)/2))
#          pCity.changePopulation(-1)
#          if gc.getPlayer(iPlayer).isHuman():
#            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REBELLION_3",(pCity.getName(),pCity.getName())), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
#
#        else:
######### Stadt laeuft ueber
#          if pCity.getOriginalOwner() != iPlayer:
#            if gc.getTeam(iPlayer).isAtWar(gc.getPlayer(pCity.getOriginalOwner()).getTeam()):
#              iNewOwner = pCity.getOriginalOwner()
#            elif gc.getGame().countCivPlayersAlive() < 18 or gc.getPlayer(pCity.getOriginalOwner()).isAlive():
#              iNewOwner = pCity.getOriginalOwner()
#            else:
#              iNewOwner = gc.getBARBARIAN_PLAYER()
#          else:
#            iNewOwner = gc.getBARBARIAN_PLAYER()
#
#          if gc.getPlayer(iPlayer).isHuman():
#            if iNewOwner == gc.getBARBARIAN_PLAYER():
#              CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REBELLION",(pCity.getName(),pCity.getName())), "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
#              popupInfo = CyPopupInfo()
#              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
#              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REBELLION",(pCity.getName(),pCity.getName())))
#              popupInfo.addPopup(iPlayer)
#            elif iNewOwner == pCity.getOriginalOwner():
#              CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REBELLION_2",(pCity.getName(),gc.getPlayer(iNewOwner).getCivilizationAdjective(1))), "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
#              popupInfo = CyPopupInfo()
#              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
#              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REBELLION_2",(pCity.getName(),gc.getPlayer(iNewOwner).getCivilizationAdjective(1))))
#              popupInfo.addPopup(iPlayer)
#
#          # Goldvergabe
#          if gc.getPlayer(iPlayer).getNumCities() > 0:
#            iGold = int(gc.getPlayer(iPlayer).getGold() / gc.getPlayer(iPlayer).getNumCities())
#            gc.getPlayer(iPlayer).changeGold(-iGold)
#            gc.getPlayer(iNewOwner).changeGold(iGold)
#            if gc.getPlayer(iNewOwner).isHuman():
#              CyInterface().addMessage(iNewOwner, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_1",("",iGold)), None, 2, None, ColorTypes(8), 0, 0, False, False)
#            elif gc.getPlayer(iPlayer).isHuman():
#              CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_2",("",iGold)), None, 2, None, ColorTypes(7), 0, 0, False, False)
#
#
#          self.doRenegadeCity(pCity, iNewOwner, -1, -1, -1)
#
#          # Rebellen oder Freiheitskaempfer entstehen lassen
#          pCity = pPlot.getPlotCity()
#          if gc.getGame().getCurrentEra() >= 3: iUnitType = gc.getInfoTypeForString('UNIT_FREEDOM_FIGHTER')
#          else: iUnitType = gc.getInfoTypeForString('UNIT_REBELL')
#
#          for i in range(pCity.getPopulation()*2):
#            gc.getPlayer(iNewOwner).initUnit(iUnitType, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
#          iNewPop = int(pCity.getPopulation() / 2)
#          if iNewPop < 1: iNewPop = 1
#          pCity.setPopulation(iNewPop)
# --- Ende city rebellion

##### City Revolts / Stadt Revolten

    if pCity.getOccupationTimer() > 0: bCityIsInRevolt = True
    else: bCityIsInRevolt = False

    if not bRebellion and bCityIsInRevolt and pCity.getPopulation() > 1:
      iRand = self.myRandom(10, None)
      if iRand < 5:
        pCity.changePopulation(-1)
        bCheckCityState = True
        if pPlayer.isHuman():
          CyInterface().addMessage(iPlayer,False,25,CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLT_SHRINK",(pCity.getName(),)),"AS2D_REVOLTSTART",InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Techs/button_brandschatzen.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtpop sinkt wegen Revolte (Zeile 4126)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    if not (bRebellion or bCityIsInRevolt) and pCity.getPopulation() > 3:
      pPlot = gc.getMap().plot(pCity.getX(), pCity.getY())

      # Conquered city (% culture / 10)
      if pCity.getOriginalOwner() != iPlayer and gc.getPlayer(pCity.getOriginalOwner()).isAlive():
        iForeignCulture = pCity.plot().calculateTeamCulturePercent(gc.getPlayer(pCity.getOriginalOwner()).getTeam())
        if iForeignCulture > 19:
          # Pro Einheit 1% Bonus
          iRand = self.myRandom(100, None)
          if iRand + pPlot.getNumDefenders(iPlayer) < iForeignCulture / 10:
            bCityIsInRevolt = True
            iCityRevoltTurns = 4
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_YEARNING"
      # Nation is in anarchy (20%, AI 5%)
      if pPlayer.getAnarchyTurns() > 0:
        if pPlayer.isHuman(): iTmp = 5
        else: iTmp = 20
        iRand = self.myRandom(iTmp, None)
        if iRand < 1:
          bCityIsInRevolt = True
          iCityRevoltTurns = pPlayer.getAnarchyTurns()
          text = "TXT_KEY_MESSAGE_CITY_REVOLT_ANARCHY"
      # city has no state religion (3%, AI 1%)
      if pPlayer.getStateReligion() != -1:
       if not pCity.isHasReligion(pPlayer.getStateReligion()):
        iBuilding = gc.getInfoTypeForString("BUILDING_STADT")
        if pCity.isHasBuilding(iBuilding):
          if pPlayer.isHuman(): iTmp = 30
          else: iTmp = 100
          iRand = self.myRandom(iTmp, None)
          if iRand < 1:
            bCityIsInRevolt = True
            iCityRevoltTurns = 4
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_RELIGION"
      # city is unhappy (3%, AI 1%)
      if pCity.unhappyLevel(0) > pCity.happyLevel():
        if pPlayer.isHuman(): iTmp = 30
        else: iTmp = 100
        iRand = self.myRandom(iTmp, None)
        if iRand < 1:
          bCityIsInRevolt = True
          iCityRevoltTurns = 4
          text = "TXT_KEY_MESSAGE_CITY_REVOLT_UNHAPPINESS"
      # high taxes
      # PAE V: not for AI
      if pPlayer.getCommercePercent(0) > 50 and pPlayer.isHuman():
        iChance = int( (pPlayer.getCommercePercent(0) - 50) / 5 )
        # Pro Happy Citizen 5% Nachlass
        iChance = iChance - pCity.happyLevel() + pCity.unhappyLevel(0)
        if iChance > 0:
          iRand = self.myRandom(100, None)
          if iRand < iChance:
            bCityIsInRevolt = True
            iCityRevoltTurns = iChance
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_TAXES"


      # City Revolt PopUp / Human and AI
      if bCityIsInRevolt:

        # Einheiten senken Dauer
        if pPlot.getNumUnits() > pCity.getPopulation(): iCityRevoltTurns = 2

        # Human PopUp 675
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer,True,10,CyTranslator().getText(text,(pCity.getName(),)),"AS2D_REVOLTSTART",2,"Art/Interface/Buttons/Techs/button_brandschatzen.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText(text,(pCity.getName(),)))
            popupInfo.setData1(iPlayer)
            popupInfo.setData2(pCity.getID())
            popupInfo.setData3(iCityRevoltTurns)
            popupInfo.setOnClickedPythonCallback("popupRevoltPayment")
            iGold = pCity.getPopulation()*10
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_1",(iGold,)), "")
            iGold = pCity.getPopulation()*5
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_2",(iGold,)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_CANCEL",()), "")
            popupInfo.addPopup(iPlayer)

        # AI ----
        else:
          # AI will pay (90%) if they have the money
          iRand = self.myRandom(100, None)
          if iRand < 90:

            if pPlayer.getGold() > pCity.getPopulation() * 10:
              iBetrag = pCity.getPopulation() * 10
              iChance = 20
            elif pPlayer.getGold() > pCity.getPopulation() * 5:
              iBetrag = pCity.getPopulation() * 5
              iChance = 50
            else:
              iBetrag = 0
              iChance = 100

            pPlayer.changeGold(iBetrag)
            # even though, there is a chance of revolting
            iRand = self.myRandom(100, None)
            if iRand < iChance:
              #pCity.setOccupationTimer(iCityRevoltTurns)
              self.doCityRevolt (pCity,iCityRevoltTurns)

          else:
            #pCity.setOccupationTimer(iCityRevoltTurns)
            self.doCityRevolt (pCity,iCityRevoltTurns)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtrevolte PopUp (Zeile 4222)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# -- end city revolts

#### Judenaufstand Judentum: 2%, ab 200 BC
    bRevolt = False
    iReligionType = gc.getInfoTypeForString("RELIGION_JUDAISM")
    iRangeMaxPlayers = gc.getMAX_PLAYERS()

    if pCity.isHolyCityByType(iReligionType) and gc.getGame().getGameTurnYear() > -200:
     iPlayer = pCity.getOwner()
     pPlayer = gc.getPlayer(iPlayer)
     if pPlayer.getStateReligion() != iReligionType:

      if pCity.happyLevel() < pCity.unhappyLevel(0): iChance = 3
      else: iChance = 1
      iRand = self.myRandom(50, None)


      if iRand < iChance:

        #CivIsrael = CvUtil.findInfoTypeNum(gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_ISRAEL')
        CivIsrael = gc.getInfoTypeForString("CIVILIZATION_ISRAEL")
        bIsraelAlive = False

        for i in range(iRangeMaxPlayers):
          loopPlayer = gc.getPlayer(i)
          # Israeliten sollen nur dann auftauchen, wenn es nicht bereits Israeliten gibt
          if loopPlayer.getCivilizationType() == CivIsrael and loopPlayer.isAlive():
            bIsraelAlive = True
            break

        # Israel versuchen zu erstellen
        iCivID = -1
        if not bIsraelAlive:
            if gc.getGame().countCivPlayersAlive() < 18:
              # freie PlayerID herausfinden
              for i in range(18):
                loopPlayer = gc.getPlayer(i)
                if not loopPlayer.isEverAlive():
                  iCivID = i
                  break
              # wenn keine nagelneue ID frei ist, dann eine bestehende nehmen
              if iCivID == -1:
                for i in range(18):
                  j = 17-i
                  loopPlayer = gc.getPlayer(j)
                  if not loopPlayer.isAlive():
                    iCivID = j
                    break
            # Israel-ID erstellen

        pCityPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
        if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_REVOLTSTART')

        # Einen guenstigen Plot auswaehlen
        rebelPlotArray = []
        for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
            if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
              if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                rebelPlotArray.append(loopPlot)

        if len(rebelPlotArray) == 0:
                for i in range(3):
                  for j in range(3):
                    loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                    if None != loopPlot and not loopPlot.isNone() and not loopPlot.isUnit():
                      if not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()) and loopPlot.getOwner() == iPlayer:
                        rebelPlotArray.append(loopPlot)

        # es kann rebelliert werden
        if len(rebelPlotArray) > 0:

            if iCivID > -1:

              # Israel erstellen
              if self.myRandom(2, None) == 0: CivLeader = gc.getInfoTypeForString("LEADER_SALOMO")
              else: CivLeader = gc.getInfoTypeForString("LEADER_DAVID")
              gc.getGame().addPlayer(iCivID,CivLeader,CivIsrael)
              newPlayer = gc.getPlayer(iCivID)
              newTeam = gc.getTeam(newPlayer.getTeam())

              # Techs geben
              xTeam = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
              iTechNum = gc.getNumTechInfos()
              for iTech in range(iTechNum):
                if gc.getTechInfo(iTech) != None:
                  if xTeam.isHasTech(iTech):
                    if gc.getTechInfo(iTech).isTrade():
                      newTeam.setHasTech(iTech, 1, iCivID, 0, 0)

              iTech = gc.getInfoTypeForString("TECH_MILIT_STRAT")
              if not newTeam.isHasTech(iTech): newTeam.setHasTech(iTech, 1, iCivID, 0, 0)

            else: newPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())

            bRevolt = True

            # Rebells x 1.5 of city pop
            iNumRebels = pCity.getPopulation() + pCity.getPopulation() / 2

            # City Revolt
            #pCity.setOccupationTimer(iNumRebelx)
            # City Defender damage
            self.doCityRevolt (pCity, pCity.getPopulation() / 2)

            # Krieg erklaeren
            pPlayer.AI_changeAttitudeExtra(iCivID,-4)
            pTeam = gc.getTeam(pPlayer.getTeam())
            pTeam.declareWar(newPlayer.getTeam(), 0, 6)

            newPlayer.setCurrentEra(3)
            newPlayer.setGold(500)

            rebellTypeArray = []
            rebellTypeArray.append(gc.getInfoTypeForString("UNIT_FREEDOM_FIGHTER"))
            rebellTypeArray.append(gc.getInfoTypeForString("UNIT_ARCHER"))
            rebellTypeArray.append(gc.getInfoTypeForString("UNIT_SPEARMAN"))
            rebellTypeArray.append(gc.getInfoTypeForString("UNIT_MACCABEE"))

            for i in range(iNumRebels):
                  iPlot = self.myRandom(len(rebelPlotArray), None)
                  iUnitType = self.myRandom(len(rebellTypeArray), None)
                  newPlayer.initUnit(rebellTypeArray[iUnitType], rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

            for iAllPlayer in range (iRangeMaxPlayers):
                  ThisPlayer = gc.getPlayer(iAllPlayer)
                  iThisPlayer = ThisPlayer.getID()
                  iThisTeam = ThisPlayer.getTeam()
                  ThisTeam = gc.getTeam(iThisTeam)
                  if ThisTeam.isHasMet(gc.getPlayer(iPlayer).getTeam()) and ThisPlayer.isHuman():
                    if iThisPlayer == iPlayer: iColor = 7
                    else: iColor = 10
                    CyInterface().addMessage(iThisPlayer, True, 5, CyTranslator().getText("TXT_KEY_JEWISH_REVOLT",(gc.getPlayer(iPlayer).getCivilizationAdjective(1),pCity.getName())),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,'Art/Interface/Buttons/Units/button_freedom_fighter.dds',ColorTypes(iColor),pCity.getX(),pCity.getY(),True,True)
                    if ThisPlayer.getStateReligion() == iReligionType:
                      ThisPlayer.AI_changeAttitudeExtra(iCivID,2)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Juedische Freiheitskaempfer (Zeile 4284)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ---- Israeliten Ende ------------


# -------- Provinz Tributzahlung Statthalter
# --- Alle 30 Runden soll Tribut gefordert werden = PAE III
# --- Ca 3% pro Runde = PAE IV
    iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
    if not bRevolt and pCity.isHasBuilding(iBuilding):
      iPlayer = pCity.getOwner()
      pPlayer = gc.getPlayer(iPlayer)

      # PAE III
      #iCityIntervall = gc.getGame().getGameTurn() - pCity.getGameTurnFounded()
      #if iCityIntervall > 0 and iCityIntervall % 30 == 0 and iPlayer != -1:

      # PAE IV: 33 (3%), PAE V: 50 (2%)
      if self.myRandom(50, None) < 1:

          iGold = pPlayer.getGold()

          iTribut = pCity.getPopulation() * 10 + self.myRandom(pCity.getPopulation()*10/2, None)
          iTribut2 = iTribut / 2

          # Human PopUp
          if gc.getPlayer(iPlayer).isHuman():
              iRand = self.myRandom(11, None)
              szBuffer = CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_DEMAND_"+str(iRand),(pCity.getName(),iTribut))
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText(szBuffer)
              popupInfo.setData1(iPlayer)
              popupInfo.setData2(pCity.getID())
              popupInfo.setData3(iTribut)
              popupInfo.setOnClickedPythonCallback("popupProvinzPayment")

              if iGold >= iTribut:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_1",(iTribut,)), "")
              if iGold >= iTribut2:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_2",(iTribut2,)), "")
              if iGold > 0 and iGold < iTribut2:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_2_1",(iGold,)), "")
              iRand = 1 + self.myRandom(10, None)
              popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_3_"+str(iRand),()), "")

              popupInfo.addPopup(iPlayer)
          else:
            # AI
            # Wenn iGold > iTribut * 3: 1 - 20%, 2 - 80%, 3 - 0%
            # Wenn iGold > iTribut * 2: 1 - 10%, 2 - 80%, 3 - 10%
            # Wenn iGold >= iTribut:    1 -  0%, 2 - 80%, 3 - 20%
            # Wenn iGold >= iTribut2:   1 -  0%, 2 - 70%, 3 - 30%
            # Wenn iGold > 0:           1 -  0%, 2 - 60%, 3 - 40%
            iAddHappiness = -1
            iRand = self.myRandom(10, None)
            iRandRebellion = self.myRandom(100, None)
            bDoRebellion = False
            bPaid = False

            if iGold > iTribut * 3:
              if iRand < 2:
                pPlayer.changeGold(-iTribut)
                iAddHappiness = 2
              else:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
              bPaid = True

            elif iGold > iTribut * 2:
              if iRand == 0:
                pPlayer.changeGold(-iTribut)
                iAddHappiness = 2
              elif iRand < 9:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
              bPaid = True

            elif iGold >= iTribut:
              if iRand < 8:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
                bPaid = True

            elif iGold >= iTribut2:
              if iRand < 7:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
                bPaid = True

            elif iGold >= 0:
              if iRand < 6:
                pPlayer.setGold(0)
                iAddHappiness = 0


            # Happiness setzen (Bug bei CIV, Man muss immer den aktuellen Wert + die Aenderung setzen)
            iBuildingHappiness = pCity.getBuildingHappiness(iBuilding)
            pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding).getBuildingClassType(), iBuildingHappiness + iAddHappiness)


            # Chance einer Rebellion: Unhappy Faces * Capital Distance
            iCityHappiness = pCity.happyLevel() - pCity.unhappyLevel(0)
            if iCityHappiness < 0:
              # Abstand zur Hauptstadt
              if not pPlayer.getCapitalCity().isNone() and pPlayer.getCapitalCity() != None:
                iDistance = plotDistance(pPlayer.getCapitalCity().getX(), pPlayer.getCapitalCity().getY(), pCity.getX(), pCity.getY())
              else: iDistance = 20
              iChance = iCityHappiness * (-1) * iDistance
              if iChance > iRandRebellion: bDoRebellion = True


            if bDoRebellion == True: self.doProvinceRebellion(pCity)
            elif bPaid:
              # 1 Unit as gift:
              lGift = []
              lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR")))
              iUnit2 = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
              if pCity.canTrain(iUnit2,0,0): lGift.append(iUnit2)
              # Food
              lGift.append(gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"))
              # Slave
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
              # Mounted
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_CHARIOT"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),0,0): lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
              # Elefant
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))

              iRand = self.myRandom(len(lGift), None)
              pPlayer.initUnit(lGift[iRand], pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Provinz-HS Tribut-PopUp (Zeile 4367)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Christentum und Haeresie (Heresy) ----------------------------
    iTech = gc.getInfoTypeForString("TECH_HERESY")
    if not bRevolt and not pTeam.isHasTech(iTech) and gc.getGame().getGameTurn() % 3 == 0:
      iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
      if gc.getGame().isReligionFounded(iReligion):
        # zum Christentum konvertieren
        if not pCity.isHasReligion(iReligion):

          # nicht bei Judentum, Hindu, Buddh und Jain
          if not pCity.isHasReligion(gc.getInfoTypeForString("RELIGION_JUDAISM")) and not \
                 pCity.isHasReligion(gc.getInfoTypeForString("RELIGION_HINDUISM")) and not \
                 pCity.isHasReligion(gc.getInfoTypeForString("RELIGION_BUDDHISM")) and not \
                 pCity.isHasReligion(gc.getInfoTypeForString("RELIGION_JAINISMUS")):

            if pCity.isCapital(): iChance = 40 # 2.5%
            elif pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_PROVINZPALAST")): iChance = 50 # 2%
            elif pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")):
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): iChance = 50 # 2%
              else: iChance = 75 # 1.5%
            else:
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): iChance = 40 # 2.5%
              else: iChance = 75 # 1.5%

            # bei folgenden Civics Chance verringern
            if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_THEOCRACY")): iChance += 25
            if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_AMPHIKTIONIE")): iChance += 25

            if 1 == self.myRandom(iChance, None):
              pCity.setHasReligion(iReligion, 1, 1, 0)
              if gc.getPlayer(iPlayer).isHuman():
                iRand = 1 + self.myRandom(3, None)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_HERESY_2CHRIST_"+str(iRand),(pCity.getName(),0)), None, 2,"Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(11), pCity.getX(), pCity.getY(), True, True)

        # Bei christlich beeinflussten Staedten - Kulte und Religionen langsam raus (alle!)
        else:
          if self.myRandom(75, None) == 1: # 1.5%

            # Kult
            lCorp = []
            iRange = gc.getNumCorporationInfos()
            for i in range(iRange):
              if pCity.isHasCorporation(i): lCorp.append(i)

            # Religion
            lReli = []
            iRange = gc.getNumReligionInfos()
            for i in range(iRange):
              if pCity.isHasReligion(i) and i != iReligion: lReli.append(i)

            # Kult oder Religion entfernen
            text = ""
            bUndoCorp = False
            if len(lCorp) > 0 and len(lReli) > 0:
              if self.myRandom(2, None) == 1:
                bUndoCorp = True

            # Kult
            if len(lCorp) > 0 or bUndoCorp:
              iRand = self.myRandom(len(lCorp), None)
              iRange = gc.getNumBuildingInfos()
              for i in range(iRange):
                if pCity.getNumBuilding(i) > 0:
                  thisBuilding = gc.getBuildingInfo(i)
                  if thisBuilding.getPrereqCorporation() == lCorp[iRand]:
                    # Akademien (Corp7)
                    if thisBuilding.getType() != gc.getInfoTypeForString("BUILDING_ACADEMY_2") and thisBuilding.getType() != gc.getInfoTypeForString("BUILDING_ACADEMY_3") and thisBuilding.getType() != gc.getInfoTypeForString("BUILDING_ACADEMY_4"):
                      pCity.setNumRealBuilding(i,0)
              pCity.setHasCorporation(lCorp[iRand], 0, 0, 0)
              text = gc.getCorporationInfo( lCorp[iRand] ).getText()

            # Religion
            elif len(lReli) > 0:
              iRand = self.myRandom(len(lReli), None)
              iRange = gc.getNumBuildingInfos()
              for i in range(iRange):
                if pCity.getNumBuilding(i) > 0:
                  thisBuilding = gc.getBuildingInfo(i)
                  if thisBuilding.getPrereqReligion() == lReli[iRand]:
                    # Holy City
                    if thisBuilding.getHolyCity() == -1:
                      pCity.setNumRealBuilding(i,0)
              pCity.setHasReligion(lReli[iRand], 0, 0, 0)
              text = gc.getReligionInfo( lReli[iRand] ).getText()

            # Meldung
            if gc.getPlayer(iPlayer).isHuman() and text != "":
              iRand = 1 + self.myRandom(3, None)
              CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_HERESY_CULTS_"+str(iRand),(text,pCity.getName())), None, 2,"Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(11), pCity.getX(), pCity.getY(), True, True)

    # Christentum und Haeresie (Heresy) end ----------------------------

    # Die Stadt wird ueberprueft, ob es ansaessige Sklaven gibt (Sklavenmarkt)
    # deactivated (PAE V Beta 2 Patch 7) = Sklavenmarkt ist nun baubar
    #iCitySlaves = pCity.getFreeSpecialistCount(16) + pCity.getFreeSpecialistCount(17) + pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE = 16,17,18
    #iBuildingSklavenmarkt = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
    #if iCitySlaves < 1:
    # if pCity.isHasBuilding(iBuildingSklavenmarkt): pCity.setNumRealBuilding(iBuildingSklavenmarkt,0)
    #else:
    # if not pCity.isHasBuilding(iBuildingSklavenmarkt): pCity.setNumRealBuilding(iBuildingSklavenmarkt,1)

    # PAE Provinzcheck
    if bCheckCityState:
      self.doCheckCityState(pCity)

    # PAE Debug Mark
    #"""
#########################################

  def onCityBuildingUnit(self, argsList):
    'City begins building a unit'
    pCity = argsList[0]
    iUnitType = argsList[1]
    if (not self.__LOG_CITYBUILDING):
      return
    CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getUnitInfo(iUnitType).getDescription()))

  def onCityBuildingBuilding(self, argsList):
    'City begins building a Building'
    pCity = argsList[0]
    iBuildingType = argsList[1]
    if (not self.__LOG_CITYBUILDING):
      return
    CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getBuildingInfo(iBuildingType).getDescription()))

  def onCityRename(self, argsList):
    'City is renamed'
    pCity = argsList[0]
    if (pCity.getOwner() == gc.getGame().getActivePlayer()):
      self.__eventEditCityNameBegin(pCity, True)

  def onCityHurry(self, argsList):
    'City is renamed'
    pCity = argsList[0]
    iHurryType = argsList[1]

    # Kolonie / Provinz ----------
    self.doCheckCityState(pCity)
    # ----------------------------

  def onVictory(self, argsList):
    'Victory'
    iTeam, iVictory = argsList
    if (iVictory >= 0 and iVictory < gc.getNumVictoryInfos()):
      victoryInfo = gc.getVictoryInfo(int(iVictory))
      CvUtil.pyPrint("Victory!  Team %d achieves a %s victory"
        %(iTeam, victoryInfo.getDescription()))

  def onVassalState(self, argsList):
    'Vassal State'
    iMaster, iVassal, bVassal = argsList

    if (bVassal):
      CvUtil.pyPrint("Team %d becomes a Vassal State of Team %d"
        %(iVassal, iMaster))
    else:
      CvUtil.pyPrint("Team %d revolts and is no longer a Vassal State of Team %d"
        %(iVassal, iMaster))

  def onGameUpdate(self, argsList):
    'sample generic event, called on each game turn slice'
    genericArgs = argsList[0][0]  # tuple of tuple of my args
    turnSlice = genericArgs[0]

    # Added by Gerikes for OOS logging.
    OOSLogger.doGameUpdate()
    # End added by Gerikes for OOS logging.

  def onMouseEvent(self, argsList):
    'mouse handler - returns 1 if the event was consumed'
    eventType,mx,my,px,py,interfaceConsumed,screens = argsList
    if ( px!=-1 and py!=-1 ):
      if ( eventType == self.EventLButtonDown ):
        if (self.bAllowCheats and self.bCtrl and self.bAlt and CyMap().plot(px,py).isCity() and not interfaceConsumed):
          # Launch Edit City Event
          self.beginEvent( CvUtil.EventEditCity, (px,py) )
          return 1

        elif (self.bAllowCheats and self.bCtrl and self.bShift and not interfaceConsumed):
          # Launch Place Object Event
          self.beginEvent( CvUtil.EventPlaceObject, (px, py) )
          return 1

    if ( eventType == self.EventBack ):
      return CvScreensInterface.handleBack(screens)
    elif ( eventType == self.EventForward ):
      return CvScreensInterface.handleForward(screens)

    return 0


#################### TRIGGERED EVENTS ##################

## BTS Original
  def __eventPlaceObjectBegin(self, argsList):
    'Place Object Event'
    CvDebugTools.CvDebugTools().initUnitPicker(argsList)

  def __eventPlaceObjectApply(self, playerID, userData, popupReturn):
    'Place Object Event Apply'
    if (getChtLvl() > 0):
      CvDebugTools.CvDebugTools().applyUnitPicker( (popupReturn, userData) )

  def __eventAwardTechsAndGoldBegin(self, argsList):
    'Award Techs & Gold Event'
    CvDebugTools.CvDebugTools().cheatTechs()

  def __eventAwardTechsAndGoldApply(self, playerID, netUserData, popupReturn):
    'Award Techs & Gold Event Apply'
    if (getChtLvl() > 0):
      CvDebugTools.CvDebugTools().applyTechCheat( (popupReturn) )

  def __eventShowWonderBegin(self, argsList):
    'Show Wonder Event'
    CvDebugTools.CvDebugTools().wonderMovie()

  def __eventShowWonderApply(self, playerID, netUserData, popupReturn):
    'Wonder Movie Apply'
    if (getChtLvl() > 0):
      CvDebugTools.CvDebugTools().applyWonderMovie( (popupReturn) )

# BTS Original: auskommendiert wegen Platys WorldBuilder ------
  """
  def __eventEditCityNameBegin(self, city, bRename):
    popup = PyPopup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
    popup.setUserData((city.getID(), bRename))
    popup.setHeaderString(localText.getText("TXT_KEY_NAME_CITY", ()))
    popup.setBodyString(localText.getText("TXT_KEY_SETTLE_NEW_CITY_NAME", ()))
    popup.createEditBox(city.getName())
    popup.setEditBoxMaxCharCount(15)
    popup.launch()

  def __eventEditCityNameApply(self, playerID, userData, popupReturn):
    'Edit City Name Event'
    iCityID = userData[0]
    bRename = userData[1]
    player = gc.getPlayer(playerID)
    city = player.getCity(iCityID)
    cityName = popupReturn.getEditBoxString(0)
    if (len(cityName) > 30):
      cityName = cityName[:30]
    city.setName(cityName, not bRename)

  def __eventEditCityBegin(self, argsList):
    'Edit City Event'
    px,py = argsList
    CvWBPopups.CvWBPopups().initEditCity(argsList)

  def __eventEditCityApply(self, playerID, userData, popupReturn):
    'Edit City Event Apply'
    if (getChtLvl() > 0):
      CvWBPopups.CvWBPopups().applyEditCity( (popupReturn, userData) )

  def __eventEditUnitNameBegin(self, argsList):
    pUnit = argsList
    popup = PyPopup.PyPopup(CvUtil.EventEditUnitName, EventContextTypes.EVENTCONTEXT_ALL)
    popup.setUserData((pUnit.getID(),))
    popup.setBodyString(localText.getText("TXT_KEY_RENAME_UNIT", ()))
    popup.createEditBox(pUnit.getNameNoDesc())
    popup.setEditBoxMaxCharCount(25)
    popup.launch()

  def __eventEditUnitNameApply(self, playerID, userData, popupReturn):
    'Edit Unit Name Event'
    iUnitID = userData[0]
    unit = gc.getPlayer(playerID).getUnit(iUnitID)
    newName = popupReturn.getEditBoxString(0)
    if (len(newName) > 25):
      newName = newName[:25]
    unit.setName(newName)

  def __eventWBAllPlotsPopupBegin(self, argsList):
    CvScreensInterface.getWorldBuilderScreen().allPlotsCB()
    return
  def __eventWBAllPlotsPopupApply(self, playerID, userData, popupReturn):
    if (popupReturn.getButtonClicked() >= 0):
      CvScreensInterface.getWorldBuilderScreen().handleAllPlotsCB(popupReturn)
    return

  def __eventWBLandmarkPopupBegin(self, argsList):
    CvScreensInterface.getWorldBuilderScreen().setLandmarkCB("")
    #popup = PyPopup.PyPopup(CvUtil.EventWBLandmarkPopup, EventContextTypes.EVENTCONTEXT_ALL)
    #popup.createEditBox(localText.getText("TXT_KEY_WB_LANDMARK_START", ()))
    #popup.launch()
    return

  def __eventWBLandmarkPopupApply(self, playerID, userData, popupReturn):
    if (popupReturn.getEditBoxString(0)):
      szLandmark = popupReturn.getEditBoxString(0)
      if (len(szLandmark)):
        CvScreensInterface.getWorldBuilderScreen().setLandmarkCB(szLandmark)
    return

  def __eventWBScriptPopupBegin(self, argsList):
    popup = PyPopup.PyPopup(CvUtil.EventWBScriptPopup, EventContextTypes.EVENTCONTEXT_ALL)
    popup.setHeaderString(localText.getText("TXT_KEY_WB_SCRIPT", ()))
    popup.createEditBox(CvScreensInterface.getWorldBuilderScreen().getCurrentScript())
    popup.launch()
    return

  def __eventWBScriptPopupApply(self, playerID, userData, popupReturn):
    if (popupReturn.getEditBoxString(0)):
      szScriptName = popupReturn.getEditBoxString(0)
      CvScreensInterface.getWorldBuilderScreen().setScriptCB(szScriptName)
    return

  def __eventWBStartYearPopupBegin(self, argsList):
    popup = PyPopup.PyPopup(CvUtil.EventWBStartYearPopup, EventContextTypes.EVENTCONTEXT_ALL)
    popup.createSpinBox(0, "", gc.getGame().getStartYear(), 1, 5000, -5000)
    popup.launch()
    return

  def __eventWBStartYearPopupApply(self, playerID, userData, popupReturn):
    iStartYear = popupReturn.getSpinnerWidgetValue(int(0))
    CvScreensInterface.getWorldBuilderScreen().setStartYearCB(iStartYear)
    return
  """

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
    gc.getPlayer(userData[0]).setScriptData(CvUtil.convertToStr(sScript))
    WBPlayerScreen.WBPlayerScreen().placeScript()
    return

  def __eventWBCityScriptPopupApply(self, playerID, userData, popupReturn):
    sScript = popupReturn.getEditBoxString(0)
    pCity = gc.getPlayer(userData[0]).getCity(userData[1])
    pCity.setScriptData(CvUtil.convertToStr(sScript))
    WBCityEditScreen.WBCityEditScreen().placeScript()
    return

  def __eventWBUnitScriptPopupApply(self, playerID, userData, popupReturn):
    sScript = popupReturn.getEditBoxString(0)
    pUnit = gc.getPlayer(userData[0]).getUnit(userData[1])
    pUnit.setScriptData(CvUtil.convertToStr(sScript))
    WBUnitScreen.WBUnitScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
    return

  def __eventWBScriptPopupBegin(self):
    return

  def __eventWBGameScriptPopupApply(self, playerID, userData, popupReturn):
    sScript = popupReturn.getEditBoxString(0)
    CyGame().setScriptData(CvUtil.convertToStr(sScript))
    WBGameDataScreen.WBGameDataScreen(CvPlatyBuilderScreen.CvWorldBuilderScreen()).placeScript()
    return

  def __eventWBPlotScriptPopupApply(self, playerID, userData, popupReturn):
    sScript = popupReturn.getEditBoxString(0)
    pPlot = CyMap().plot(userData[0], userData[1])
    pPlot.setScriptData(CvUtil.convertToStr(sScript))
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
    if len(sScript):
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

  # Provinz Rebellion / Statthalter
  def doProvinceRebellion(self, pCity):

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Provinzrebellion (Zeile 4578)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
    #if self.myRandom(3, "Choose Province Rebells") == 0:
    #  iDeriCiv = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getDerivativeCiv()
    #  if iDeriCiv != -1:
    #    DeriCiv = gc.getCivilizationInfo(iDeriCiv)
    #    NumLeaders = CurCiv.getNumLeaders ()
    #    Checken, ob es diese Civ schon gibt
    #    for i in range(gc.getMAX_PLAYERS()):
    #      player = gc.getPlayer(i)
    #      if player.isAlive() and player.getName() == gc.getCivilizationInfo(iDeriCiv.getDescription()):
    #        iNewOwner = gc.getBARBARIAN_PLAYER()
    #        break
    #else:
    iNewOwner = gc.getBARBARIAN_PLAYER()

    # iNewOwner herausfinden
    # 1. Moeglichkeit: gab es einen Vorbesitzer
    if iNewOwner == gc.getBARBARIAN_PLAYER() and pCity.getOriginalOwner() != iPlayer:
      #if gc.getPlayer(pCity.getOriginalOwner()).isAlive():
      #if gc.getTeam(iPlayer).isAtWar(gc.getPlayer(pCity.getOriginalOwner()).getTeam()): iNewOwner = pCity.getOriginalOwner()
      if gc.getGame().countCivPlayersAlive() < 18 or gc.getPlayer(pCity.getOriginalOwner()).isAlive(): iNewOwner = pCity.getOriginalOwner()
    # 2. Moeglichkeit: Spieler mit hoechster Kultur heraussuchen
    if iNewOwner == gc.getBARBARIAN_PLAYER():
      iPlayerHC = pCity.findHighestCulture()
      if iPlayerHC != iPlayer and iPlayerHC != -1:
        if gc.getPlayer(iPlayerHC).isAlive(): iNewOwner = iPlayerHC
    # 3. Moeglichkeit: weitere Spieler mit Fremdkultur
    if iNewOwner == gc.getBARBARIAN_PLAYER():
      PlayerArray = []
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        if gc.getPlayer(i).isAlive():
         if i != iPlayer and pCity.getCulture(i) > 0:
           PlayerArray.append(i)
      if len(PlayerArray) > 0:
       iRand = self.myRandom(len(PlayerArray), None)
       iNewOwner = PlayerArray[iRand]
    # ----------------

    # Radius 5x5 Plots und dessen Staedte checken
    for i in range (11):
      for j in range (11):
        loopPlot = gc.getMap().plot(pCity.getX() - 5 + i, pCity.getY() - 5 + j)
        if loopPlot != None and not loopPlot.isNone():
          if loopPlot.isCity():
            loopCity = loopPlot.getPlotCity()

            if pCity.getID() != loopCity.getID() and not loopCity.isHasBuilding(iBuilding) and not pCity.isCapital() and loopCity.getOwner() == iPlayer:
              iChance = 100
              for i2 in range (11):
                if iChance == 0: break
                for j2 in range (11):
                  loopPlot2 = gc.getMap().plot(loopCity.getX() - 5 + i2, loopCity.getY() - 5 + j2)
                  if loopPlot2 != None and not loopPlot2.isNone():
                    if loopPlot2.isCity():
                      loopCity2 = loopPlot2.getPlotCity()
                      if pCity.getID() != loopCity2.getID():
                        if loopCity2.isCapital():
                          iChance = 0
                          break
                        elif loopCity2.isHasBuilding(iBuilding): iChance = 50

              if iChance > 0:
                if self.myRandom(100, None) < iChance: self.doRenegadeCity(loopCity, iNewOwner, -1, -1, -1)

    # Provinzhauptstadt
    if not pCity.isCapital(): self.doRenegadeCity(pCity, iNewOwner, -1, -1, -1)


  # ueberlaufende Stadt / City renegade
  # When Unit gets attacked: LoserUnitID (must not get killed automatically) , no unit = -1
  def doRenegadeCity(self, pCity, iNewOwner, LoserUnitID, iWinnerX, iWinnerY):

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Renegade City (Zeile 4637)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        iUnitType1 = gc.getInfoTypeForString("UNIT_REBELL")
        iUnitType2 = gc.getInfoTypeForString("UNIT_FREEDOM_FIGHTER")

        if iNewOwner == -1: iNewOwner = gc.getBARBARIAN_PLAYER()

        iX = pCity.getX()
        iY = pCity.getY()
        pPlot = gc.getMap().plot( iX, iY )
        iOldOwner = pCity.getOwner()

        # TEST
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 1 - iNewOwner",iNewOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        # TEST
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 2 - iOldOwner",iOldOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Kultur auslesen
        iCulture = pCity.getCulture(iOldOwner)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iOldCulture",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)


        # Einheiten auslesen bevor die Stadt ueberlaeuft
        UnitArray = []
        j = 0
        iRange = pPlot.getNumUnits()
        iRangePromos = gc.getNumPromotionInfos()
        for iUnit in range (iRange):

          # Nicht die Einheit, die gerade gekillt wird killen, sonst Error
          if LoserUnitID != pPlot.getUnit(iUnit).getID():
            # Freiheitskaempfer, Rebellen oder Unsichtbare rauswerfen
            if pPlot.getUnit(iUnit).getUnitType() == iUnitType1 or pPlot.getUnit(iUnit).getUnitType() == iUnitType2 or pPlot.getUnit(iUnit).getInvisibleType() > -1:
               pPlot.getUnit(iUnit).jumpToNearestValidPlot()
            elif pPlot.getUnit(iUnit).getOwner() == iOldOwner:
              # Einige Einheiten bleiben loyal und fliehen
              # Promotion Loyality = Nr 0
              # Check its promotions
              bLoyal = False
              if pPlot.getUnit(iUnit).isHasPromotion(0): bLoyal = True
              if bLoyal: iChance = 4
              else: iChance = 8

              iRand = self.myRandom(10, None)
              if iRand < iChance:

                UnitArray.append(range(7))
                UnitArray[j][0] = pPlot.getUnit(iUnit).getUnitType()
                UnitArray[j][1] = pPlot.getUnit(iUnit).getUnitAIType()
                UnitArray[j][2] = pPlot.getUnit(iUnit).getName()
                UnitArray[j][3] = pPlot.getUnit(iUnit).getUnitCombatType()
                if UnitArray[j][3] != -1:
                  UnitArray[j][4] = pPlot.getUnit(iUnit).getExperience()
                  UnitArray[j][5] = pPlot.getUnit(iUnit).getLevel()
                  # Bei eroberbaren Einheiten keinen Schaden verursachen, sonst werden sie nicht erzeugt
                  if pPlot.getUnit(iUnit).getCaptureUnitType(gc.getPlayer(iOldOwner).getCivilizationType()) > -1: UnitArray[j][6] = 0
                  else: UnitArray[j][6] = pPlot.getUnit(iUnit).getDamage()
                  # Check its promotions

                  for i in range(iRangePromos):
                    if pPlot.getUnit(iUnit).isHasPromotion(i):
                      UnitArray[j].append(i)

                # Nicht die Einheit, die gerade gekillt wird killen, sonst Error
                if LoserUnitID != pPlot.getUnit(iUnit).getID():
                  #pPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                  pPlot.getUnit(iUnit).kill(1,pPlot.getUnit(iUnit).getOwner())
                else:
                  # Wenn eroberte Einheit eine Capture Unit ist, dann kann man die neuen Einheiten nicht auf diesen Plot erzeugen
                  if pPlot.getUnit(iUnit).getCaptureUnitType(gc.getPlayer(iOldOwner).getCivilizationType()) > -1:
                    iX = iWinnerX
                    iY = iWinnerY

                j += 1
              # else: Einheit kann sich noch aus dem Staub machen
              else:
                pPlot.getUnit(iUnit).jumpToNearestValidPlot()
            else:
              pPlot.getUnit(iUnit).jumpToNearestValidPlot()

        # Eine nochmale Sicherheitsschleife 3.5.12
        while pPlot.getNumUnits() > 1:
          for iUnit in range (pPlot.getNumUnits()):
            # Nicht die Einheit, die gerade gekillt wird killen, sonst Error
            if LoserUnitID != pPlot.getUnit(iUnit).getID():
              pPlot.getUnit(iUnit).jumpToNearestValidPlot()
        # --- Einheiten ---

        # Stadt laeuft automatisch ueber (CyCity pCity, BOOL bConquest, BOOL bTrade)
        gc.getPlayer(iNewOwner).acquireCity(pCity,0,1)
        pAcquiredCity = pPlot.getPlotCity()


        # Einheiten generieren
        iRange = len(UnitArray)
        for iUnit in range (iRange):
          iUnitOwner = iNewOwner

          # TEST
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 3 - iUnitOwner",iUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          # UnitAIType -1 (NO_UNITAI) -> UNITAI_UNKNOWN = 0 , ATTACK = 4, City Defense = 10
          # happened: Emigrant = 4 !
          if UnitArray[iUnit][1] == -1 or UnitArray[iUnit][1] == 0 or UnitArray[iUnit][1] == 4:
            if   UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_SLAVE'): UnitArray[iUnit][1] = 0
            elif UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_FREED_SLAVE'): UnitArray[iUnit][1] = 12
            elif UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_EMIGRANT'): UnitArray[iUnit][1] = 2
            elif UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_TRADE_MERCHANT'): UnitArray[iUnit][1] = 19
            elif UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_TRADE_MERCHANTMAN'): UnitArray[iUnit][1] = 19
            else: UnitArray[iUnit][1] = 0

          # Slaves will be freed, nur wenn dessen Besitzer neu ist
          if UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_SLAVE'): UnitArray[iUnit][0] = gc.getInfoTypeForString('UNIT_FREED_SLAVE')

          # Create a new unit
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(PyInfo.UnitInfo(UnitArray[iUnit][0]).getDescription(),UnitArray[iUnit][0])), None, 2, None, ColorTypes(10), 0, 0, False, False)
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Unit Typ",UnitArray[iUnit][1])), None, 2, None, ColorTypes(10), 0, 0, False, False)

          if UnitArray[iUnit][0] > -1:
            NewUnit = gc.getPlayer(iNewOwner).initUnit(UnitArray[iUnit][0], iX, iY, UnitAITypes(UnitArray[iUnit][1]), DirectionTypes.DIRECTION_SOUTH)

            # Emigrant und dessen Kultur
            if UnitArray[iUnit][0] == gc.getInfoTypeForString('UNIT_EMIGRANT'): NewUnit.setScriptData(str(iOldOwner))

            #NewUnit.setName(UnitArray[iUnit][2])
            if UnitArray[iUnit][2] != gc.getUnitInfo(UnitArray[iUnit][0]).getText():
              UnitName = UnitArray[iUnit][2]
              UnitName = re.sub(" \(.*?\)","",UnitName)
              NewUnit.setName(UnitName)

            if UnitArray[iUnit][3] != -1:
             NewUnit.setExperience(UnitArray[iUnit][4], -1)
             NewUnit.setLevel(UnitArray[iUnit][5])
             if UnitArray[iUnit][6]: NewUnit.setDamage(UnitArray[iUnit][6], -1)

             # Check its promotions
             iRange2 = len(UnitArray[iUnit])
             if iRange2 > 7:
              for i in range (iRange2):
                if i > 6:
                  NewUnit.setHasPromotion(UnitArray[iUnit][i], True)

             # PAE V: Trait-Promotions
             # 1. Agg und Protect Promos weg
             # 2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten
             if not gc.getPlayer(iNewOwner).hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
                    iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")
                    if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)
             #if not gc.getPlayer(iNewOwner).hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
             #       iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_PROTECTIVE")
             #       if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)

        # --- Einheiten ---


        if iNewOwner == gc.getBARBARIAN_PLAYER():
           gc.getPlayer(iNewOwner).initUnit(iUnitType2,  iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
           gc.getPlayer(iNewOwner).initUnit(iUnitType2,  iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
           gc.getPlayer(iNewOwner).initUnit(iUnitType2,  iX, iY, UnitAITypes(4), DirectionTypes.DIRECTION_SOUTH)

        # Kultur regenerieren - funkt net
        if iCulture > 0: pAcquiredCity.changeCulture(gc.getPlayer(iNewOwner).getID(),iCulture,1)

        # Stadtgroesse kontrollieren
        iPop = pAcquiredCity.getPopulation()
        if iPop < 1:
          pAcquiredCity.setPopulation(1)

        # Kolonie/Provinz checken
        self.doCheckCityState(pAcquiredCity)

  # --- renegading city

  # A nearby city of pCity will revolt
  def doNextCityRevolt(self, iX, iY, iOwner, iAttacker):

    if iOwner != -1:

      pOwner = gc.getPlayer(iOwner)
      if iOwner != gc.getBARBARIAN_PLAYER() and pOwner.getNumCities() > 1:

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Next City Revolt (Zeile 4766)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Stadtentfernung messen und naeheste Stadt definieren / die Stadt soll innerhalb 10 Plots entfernt sein.
        iRevoltCity = -1
        iCityCheck  = -1
        # City with forbidden palace shall not revolt
        iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
        iRange = pOwner.getNumCities()
        for i in range (iRange):
          if not pOwner.getCity(i).isNone():
            if not pOwner.getCity(i).isCapital() and pOwner.getCity(i).getOccupationTimer() < 1 and not pOwner.getCity(i).isHasBuilding(iBuilding) and pOwner.getCity(i).getOwner() != iAttacker:
              tmpX = pOwner.getCity(i).getX()
              tmpY = pOwner.getCity(i).getY()

              iBetrag = (iX - tmpX) * (iX - tmpX) + (iY - tmpY) * (iY - tmpY)

              if iBetrag > 0 and iBetrag < 11 and iCityCheck == -1:
                iCityCheck = iBetrag
                iRevoltCity = i
              elif iBetrag > 0 and iBetrag < 11 and iCityCheck > iBetrag:
                iCityCheck = iBetrag
                iRevoltCity = i

#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City",i)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Betrag",iBetrag)), None, 2, None, ColorTypes(10), 0, 0, False, False)

#        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Revolt",iRevoltCity)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Stadt soll revoltieren: 3 Runden
        if iRevoltCity != -1:
          pCity = pOwner.getCity(iRevoltCity)
          #pCity.setOccupationTimer(3)
          self.doCityRevolt (pCity,4)

          # Message for the other city revolt
          if (gc.getPlayer(iAttacker).isHuman()):
            iRand = 1 + self.myRandom(6, None)
            CyInterface().addMessage(iAttacker, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_1_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
          elif (gc.getPlayer(iOwner).isHuman()):
            iRand = 1 + self.myRandom(6, None)
            CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_2_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # --- next city revolt

  # Spreading Plague -------------------------
  def doSpreadPlague(self, pCity):
    pCityOrig = pCity
    CityX = pCity.getX()
    CityY = pCity.getY()
    iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')
    bSpread = False

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pestausbreitung (Zeile 4818)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Umkreis von 5 Feldern
    for i in range(11):
      for j in range(11):
        sPlot = gc.getMap().plot(pCity.getX() + i - 5, pCity.getY() + j - 5)

        if sPlot.isCity():
          sCity = sPlot.getPlotCity()
          if sCity.isConnectedTo(pCity) and not sCity.isHasBuilding(iBuildingPlague) and sCity.getPopulation() > 3:
            tmpX = sCity.getX()
            tmpY = sCity.getY()

            iBetrag = (CityX - tmpX) * (CityX - tmpX) + (CityY - tmpY) * (CityY - tmpY)

            if iBetrag > 0 and not bSpread:
              iCityCheck = iBetrag
              PlagueCity = sPlot.getPlotCity()
              bSpread = True
            elif iBetrag > 0 and iCityCheck > iBetrag:
              iCityCheck = iBetrag
              PlagueCity = sPlot.getPlotCity()
              bSpread = True

    # Handelsstaedte dieser Stadt
    if not bSpread:
      iTradeRoutes = pCity.getTradeRoutes()
      for i in range(iTradeRoutes):
        sCity = pCity.getTradeCity(i)
        if not sCity.isHasBuilding(iBuildingPlague) and sCity.getPopulation() > 3:
          PlagueCity = sCity
          bSpread = True
          break

    # Ausbreiten
    if bSpread == True:
          pCity = PlagueCity
          iPlayer = PlagueCity.getOwner()
          pPlayer = gc.getPlayer(iPlayer)
          iThisTeam = pPlayer.getTeam()
          team = gc.getTeam(iThisTeam)

          #iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
          #iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
          #iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
          #iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

          # City Revolt
          #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4): pCity.setOccupationTimer(2)
          #else: pCity.setOccupationTimer(3)

          # message for all
          iRange = gc.getMAX_PLAYERS()
          for iPlayer2 in range(iRange):
            pSecondPlayer = gc.getPlayer(iPlayer2)
            iSecondPlayer = pSecondPlayer.getID()
            if (pSecondPlayer.isHuman()):
              iSecTeam = pSecondPlayer.getTeam()
              if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                if pSecondPlayer.isHuman():
                  CyInterface().addMessage(iSecondPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD",(pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

          if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD",(pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
          # end message

          # Plague building gets added into city => culture -50
          pCity.setNumRealBuilding(iBuildingPlague,1)
  # --- plague spread


# Begin Inquisition -------------------------------

  def doInquisitorPersecution(self, pCity, pUnit):
    pPlayer = gc.getPlayer( pCity.getOwner( ) )
    iPlayer = pPlayer.getID( )

    iNumReligions = gc.getNumReligionInfos()
    # HI soll PopUp bekommen
    if pPlayer.isHuman():
       popupInfo = CyPopupInfo()
       popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
       popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_INQUISITION",(pCity.getName(), )) )
       popupInfo.setData1(iPlayer)
       popupInfo.setData2(pCity.getID())
       popupInfo.setData3(pUnit.getID())
       popupInfo.setOnClickedPythonCallback("popupReliaustreibung") # EntryPoints/CvScreenInterface und CvGameUtils / 704
       for iReligion in range(iNumReligions):
         if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
           popupInfo.addPythonButton(gc.getReligionInfo(iReligion).getText(), gc.getReligionInfo(iReligion).getButton())
       popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_INQUISITION_CANCEL",("", )), "Art/Interface/Buttons/General/button_alert_new.dds")
       popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
       popupInfo.addPopup(iPlayer)

    ## AI
    #else:
       #ReligionArray = []
       #for iReligion in range(iRange):
         #if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
           #ReligionArray.append(iReligion)

       #if len(ReligionArray) > 0:
         #iRand = self.myRandom(len(ReligionArray), None)
         #self.doInquisitorPersecution2(iPlayer, pCity.getID(), -1, ReligionArray[iRand], pUnit.getID())

    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
    #pUnit.kill(1,pUnit.getOwner())
  # -------------

  def doInquisitorPersecution2(self, iPlayer, iCity, iButton, iReligion, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pCity = pPlayer.getCity(iCity)
    szButton = gc.getUnitInfo(gc.getInfoTypeForString("UNIT_INQUISITOR")).getButton()
    iStateReligion = pPlayer.getStateReligion()
    iNumReligions = gc.getNumReligionInfos()
    # gets a list of all religions in the city except state religion
    lCityReligions = []
    for iReligionLoop in range(iNumReligions):
      if pCity.isHasReligion( iReligionLoop ):
        if pCity.isHolyCityByType(iReligionLoop) == 0 and iReligionLoop != iStateReligion:
          lCityReligions.append( iReligionLoop )

    # Wenn die Religion ueber PopUp kommt, muss sie mittels Buttonreihenfolge gefunden werden
    if iReligion == -1:
       iReligion = lCityReligions[iButton]


    if iReligion != -1:

       if iReligion != iStateReligion: iHC = -25
       else: iHC = 15

       # Does Persecution succeed
       iRandom = self.myRandom(100, None)
       if (iRandom < 95 - (len(lCityReligions) * 5) + iHC):

            pCity.setHasReligion(iReligion, 0, 0, 0)

            if pPlayer.isHuman():
              CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # remove its buildings
            iRange = gc.getNumBuildingInfos()
            for iBuildingLoop in range(iRange):
              if (pCity.isHasBuilding( iBuildingLoop )):
                pBuilding = gc.getBuildingInfo( iBuildingLoop )
                iRequiredReligion = pBuilding.getPrereqReligion( )
                # Wunder sollen nicht betroffen werden
                iBuildingClass = pBuilding.getBuildingClassType()
                thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
                if iRequiredReligion == iReligion and thisBuildingClass.getMaxGlobalInstances() != 1:
                  pCity.setNumRealBuilding (iBuildingLoop,0)
                  #if pPlayer.isHuman():
                                        ##Meldung dass das Gebaeude zerstoert wurde
                                        #CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_Bildersturm",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # increasing Anger or Sympathy for an AI
            iRange = gc.getMAX_PLAYERS()
            for iPlayer2 in range(iRange):
              pSecondPlayer = gc.getPlayer(iPlayer2)
              iSecondPlayer = pSecondPlayer.getID()
              pReligion = gc.getReligionInfo( iReligion )

              # increases Anger for all AIs which have this religion as State Religion
              if (iReligion == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                pSecondPlayer.AI_changeAttitudeExtra(iPlayer,-2)
              # increases Sympathy for all AIs which have the same State Religion as the inquisitor
              elif (pPlayer.getStateReligion() == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                pSecondPlayer.AI_changeAttitudeExtra(iPlayer,+1)

              # info for all
              if (pSecondPlayer.isHuman()):
                iSecTeam = pSecondPlayer.getTeam()
                if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                  CyInterface().addMessage(iSecondPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(10),pCity.getX(),pCity.getY(),True,True)

            # info for the player
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_NEG",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_POS",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # decrease population by 1, even if mission fails
            if pCity.getPopulation() > 1:
              pCity.changePopulation(-1)
              self.doCheckCityState(pCity)

       # Persecution fails
       elif pPlayer.isHuman():
         CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_FAIL",(pCity.getName(),)),"AS2D_SABOTAGE",2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


    # City Revolt
    pCity.changeOccupationTimer(1)
  # ------

# end Inquisition / Religionsaustreibung


  # Horse down
  def doHorseDown(self, pPlot, pUnit):
    iUnitType = pUnit.getUnitType()
    iOwner = pUnit.getOwner()
    iX = pUnit.getX()
    iY = pUnit.getY()
    iNewUnitType = -1

    if iUnitType == gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"):

      if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME") or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
         iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_ROME")
      elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
         iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON")
      else:
         iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR")

    elif iUnitType == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"): iNewUnitType = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
    elif iUnitType == gc.getInfoTypeForString('UNIT_PRAETORIAN_RIDER'): iNewUnitType = gc.getInfoTypeForString('UNIT_PRAETORIAN')
    elif iUnitType == gc.getInfoTypeForString('UNIT_PRAETORIAN2_RIDER'): iNewUnitType = gc.getInfoTypeForString('UNIT_PRAETORIAN2')
    elif iUnitType == gc.getInfoTypeForString('UNIT_MOUNTED_SACRED_BAND_CARTHAGE'): iNewUnitType = gc.getInfoTypeForString('UNIT_SACRED_BAND_CARTHAGE')
    elif iUnitType == gc.getInfoTypeForString('UNIT_MOUNTED_SCOUT'):
      if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE"):
         iNewUnitType = gc.getInfoTypeForString("UNIT_SCOUT_GREEK")
      else:
         iNewUnitType = gc.getInfoTypeForString("UNIT_SCOUT")

    if iNewUnitType != -1:
     # Create horse unit
     NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(gc.getInfoTypeForString("UNIT_HORSE"), iX, iY, UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
     NewUnit.changeMoves(90)
     # Create a new unit
     NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnitType, iX, iY, UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
     NewUnit.setExperience(pUnit.getExperience(), -1)
     NewUnit.setLevel(pUnit.getLevel())
     NewUnit.setDamage(pUnit.getDamage(), -1)
     if pUnit.getName() != gc.getUnitInfo(iUnitType).getText():
       UnitName = pUnit.getName()
       UnitName = re.sub(" \(.*?\)","",UnitName)
       NewUnit.setName(UnitName)
     # Check its promotions
     iRange = gc.getNumPromotionInfos()
     for iPromotion in range(iRange):
      # init all promotions the unit had
      if (pUnit.isHasPromotion(iPromotion)):
       NewUnit.setHasPromotion(iPromotion, True)
     pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
     #pUnit.kill(1,pUnit.getOwner())

     # ***TEST***
     #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Horse Down (Zeile 5014)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse down

  # Horse up
  def doHorseUp(self, pPlot, pUnit):
    iUnitType = pUnit.getUnitType()
    iOwner = pUnit.getOwner()
    iX = pUnit.getX()
    iY = pUnit.getY()
    iNewUnitType = -1

    # Pferd suchen und killen
    UnitHorse = gc.getInfoTypeForString('UNIT_HORSE')
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
     if pPlot.getUnit(iUnit).getUnitType() == UnitHorse:
      pPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pPlot.getUnit(iUnit).kill(1,pPlot.getUnit(iUnit).getOwner())
      break

    lUnitAuxiliar = []
    lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR"))
    lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"))
    lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON"))

    if iUnitType in lUnitAuxiliar: iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
    elif iUnitType == gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"): iNewUnitType = gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN")
    elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN"): iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER")
    elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2"): iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN2_RIDER")
    elif iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"): iNewUnitType = gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE")
    elif iUnitType == gc.getInfoTypeForString("UNIT_SCOUT") or iUnitType == gc.getInfoTypeForString("UNIT_SCOUT_GREEK"):
       iNewUnitType = gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT")

    if iNewUnitType != -1:
     # Create a new unit
     NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnitType, iX, iY, UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
     NewUnit.setExperience(pUnit.getExperience(), -1)
     NewUnit.setLevel(pUnit.getLevel())
     NewUnit.changeMoves(-60)
     NewUnit.setDamage(pUnit.getDamage(), -1)
     if pUnit.getName() != gc.getUnitInfo(iUnitType).getText():
       UnitName = pUnit.getName()
       UnitName = re.sub("( \(.*?\))","",UnitName)
       NewUnit.setName(UnitName)
     # Check its promotions
     iRange = gc.getNumPromotionInfos()
     for iPromotion in range(iRange):
      # init all promotions the unit had
      if (pUnit.isHasPromotion(iPromotion)):
       NewUnit.setHasPromotion(iPromotion, True)
     pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
     #pUnit.kill(1,pUnit.getOwner())

     # ***TEST***
     #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Horse Up (Zeile 5057)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse up

  # Slave -> Bordell
  def doSlave2Bordell(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
      iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())
      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Bordell (Zeile 5070)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  # Slave -> Schule
  def doSlave2Schule(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(1, iBuilding1)
      iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 School (Zeile 5083)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Library / Bibliothek
  def doSlave2Library(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(1, iBuilding1)
      iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

  # Slave -> Gladiator
  def doSlave2Gladiator(self, pCity, pUnit):
    pCity.changeFreeSpecialistCount(15, 1) # Gladiator Specialist ID = 15
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
    #pUnit.kill(1,pUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Gladiator (Zeile 5092)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Theatre
  def doSlave2Theatre(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_THEATER')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
      iCulture -= 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Theater (Zeile 5178)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Manufaktur , iDo: 0 = Nahrung; 1 = Produktion
  def doSlave2Manufaktur(self, pCity, pUnit, iDo):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
      if iDo == 1:
        iProd = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1)
        iProd += 1
        pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1, iProd)
      else:
        iProd = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0)
        iProd += 1
        pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0, iProd)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Manufaktur (Zeile 5196)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Palace
  def doSlave2Palace(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
      #iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Palace (Zeile 6252)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Temple
  def doSlave2Temple(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE")
    iBuilding2 = gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE")
    iBuilding3 = gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE")
    iBuilding4 = gc.getInfoTypeForString("BUILDING_ROME_TEMPLE")
    iBuilding5 = gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE")
    iBuilding6 = gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE")
    iBuilding7 = gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE")
    iBuilding8 = gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
    TempleArray = []
    if pCity.isHasBuilding(iBuilding1): TempleArray.append(iBuilding1)
    if pCity.isHasBuilding(iBuilding2): TempleArray.append(iBuilding2)
    if pCity.isHasBuilding(iBuilding3): TempleArray.append(iBuilding3)
    if pCity.isHasBuilding(iBuilding4): TempleArray.append(iBuilding4)
    if pCity.isHasBuilding(iBuilding5): TempleArray.append(iBuilding5)
    if pCity.isHasBuilding(iBuilding6): TempleArray.append(iBuilding6)
    if pCity.isHasBuilding(iBuilding7): TempleArray.append(iBuilding7)
    if pCity.isHasBuilding(iBuilding8): TempleArray.append(iBuilding8)

    if len(TempleArray) > 0:
      iBuilding = self.myRandom(len(TempleArray), None)
      iCulture = 1
      # Trait Creative: +2 Kultur pro Sklave / +2 culture per slave
      if gc.getPlayer(pCity.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")): 
        iCulture += 2
      pCity.changeBuildingCommerceChange(gc.getBuildingInfo(TempleArray[iBuilding]).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Temple (Zeile 6282)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Slave -> Feuerwehr
  def doSlave2Feuerwehr(self, pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString("BUILDING_FEUERWEHR")
    if pCity.isHasBuilding(iBuilding1):
      iHappyiness = pCity.getBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType())
      iHappyiness += 1
      pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), iHappyiness)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Feuerwehr (Zeile 6356)",iHappyiness)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # Trojanisches Pferd
  def doTrojanHorse(self, pCity, pUnit):
    pPlayerCity = gc.getPlayer(pCity.getOwner())
    pPlayerUnit = gc.getPlayer(pUnit.getOwner())

    iDamage = pCity.getDefenseModifier(0)
    pCity.changeDefenseDamage(iDamage)

    if pPlayerCity != None and pPlayerUnit != None:
      if pPlayerCity.isHuman():
        CyInterface().addMessage(pCity.getOwner(),False,25,CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY",(pCity.getName(),pPlayerUnit.getCivilizationAdjective(2))),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,pUnit.getButton(),ColorTypes(11),pCity.getX(),pCity.getY(),True,True)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY",(pCity.getName(),pPlayerUnit.getCivilizationAdjective(1) )))
        popupInfo.addPopup(pCity.getOwner())
      if pPlayerUnit.isHuman():
        CyInterface().addMessage(pUnit.getOwner(),False,25,CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",(pCity.getName(),pPlayerCity.getCivilizationAdjective(2))),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,pUnit.getButton(),ColorTypes(11),pCity.getX(),pCity.getY(),True,True)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",(pCity.getName(),pPlayerCity.getCivilizationAdjective(1) )))
        popupInfo.addPopup(pUnit.getOwner())

      if pCity.getOwner() == gc.getGame().getActivePlayer() or pUnit.getOwner() == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_THEIRDECLAREWAR")

      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Trojanisches Pferd (Zeile 9497)",0)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  # Emigrant -----------------
  def doEmigrant(self, pCity, pUnit):
    pPlot = CyMap().plot(pCity.getX(), pCity.getY())
    # Kultur auslesen
    txt = pUnit.getScriptData()
    if txt != "": iPlayerCulture = int(txt)
    else: iPlayerCulture = pUnit.getOwner()
    # Kultur = 100*Pop, max. 1000
    iCulture = pCity.getPopulation() * 100
    if iCulture > 1000: iCulture = 1000
    # Stadt Kultur geben
    pPlot.changeCulture(iPlayerCulture,iCulture,1)
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
    #pUnit.kill(1,pUnit.getOwner())

    pCity.changePopulation(1)
    # PAE Provinzcheck
    self.doCheckCityState(pCity)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant 2 City (Zeile 6458)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  # disband city
  def doDisbandCity(self, pCity, pUnit, pPlayer):
    iRand = self.myRandom(10, None)
    if iRand < 5:
      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_OK",(pCity.getName(),)), "AS2D_PILLAGE", 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), False, False)
      pPlayer.disband(pCity)
      #iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
      #pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
    else:
      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_NOT_OK",(pCity.getName(),)), "AS2D_CITY_REVOLT", 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), False, False)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant disbands/shrinks City (Zeile 6474)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


  # City Revolt
  # iTurns = deaktiv
  def doCityRevolt(self, pCity, iTurns):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = CyMap().plot(pCity.getX(), pCity.getY())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City Revolt (Zeile 6485)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Strafe verschaerfen
    #iTurns = iTurns * 2

    # Einheiten stilllegen
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
      pPlot.getUnit(iUnit).setDamage(60, -1)
      if 1 == self.myRandom(2, None):
        pPlot.getUnit(iUnit).setImmobileTimer(iTurns)

    #Stadtaufruhr
    pCity.changeHurryAngerTimer (iTurns)

    iTurns = int (iTurns / 2)
    if iTurns < 2: iTurns = 2
    #pCity.changeOccupationTimer (iTurns)
    pCity.setOccupationTimer(iTurns)

#    if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#       iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_DESPOT_REVOLT')
#       if iEvent != -1 and gc.getGame().isEventActive(iEvent):
#          triggerData = pPlayer.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iPlayer, pCity.getID(), -1, -1, -1, -1)
#       else: pCity.setOccupationTimer(2)
#    else: pCity.setOccupationTimer(2)


# ----------- Unit kill from GameUtils
#  def doKillUnitFromGameUtils (self, pUnit):



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++ Naturkatastrophen / Disasters +++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def doSandsturm(self):

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_desertstorm = gc.getInfoTypeForString('FEATURE_FALLOUT')

      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
      terr_coast = gc.getInfoTypeForString('TERRAIN_COAST')

      improv1 = gc.getInfoTypeForString('IMPROVEMENT_FORT')
      improv2 = gc.getInfoTypeForString('IMPROVEMENT_FORT2')
      improv3 = gc.getInfoTypeForString('IMPROVEMENT_TURM2')

      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      elif iMapSize < 5: iMax = 3
      else: iMax = 5

      # 20 Versuche max. iMax Sandstuerme zu kreieren
      for i in range (20):

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_oasis and pPlot.getFeatureType() != feat_flood_plains and pPlot.getTerrainType() == terr_desert and not pPlot.isPeak():
            OwnerArray = []
            iMaxEffect += 1
            for i in range(3):
              for j in range(5):
                # An den aeusseren Sturmgrenzen etwas auflockern
                if j == 0 or j == 4: iSetStorm = self.myRandom(2, None)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if (not (loopPlot.isWater() or loopPlot.isPeak()) and loopPlot.getTerrainType() == terr_desert and loopPlot.getFeatureType() != feat_oasis and loopPlot.getFeatureType() != feat_flood_plains) or loopPlot.getTerrainType() == terr_coast:
                      if loopPlot.getImprovementType() != improv1 and loopPlot.getImprovementType() != improv2 and loopPlot.getImprovementType() != improv3:
                        if loopPlot.getRouteType() == 0 and not loopPlot.isCity(): loopPlot.setRouteType(-1)
                        if loopPlot.getImprovementType() != gc.getInfoTypeForString('IMPROVEMENT_MINE'): loopPlot.setImprovementType(-1)
                      loopPlot.setFeatureType(feat_desertstorm,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_DESERTSTORM",("",)),None,2,gc.getFeatureInfo(feat_desertstorm).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

        # Maximal iMax Stuerme
        if iMaxEffect == iMax: break

  def doGrasshopper(self):

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_grasshopper = gc.getInfoTypeForString('FEATURE_GRASSHOPPER')

      lFeatures = []
      lFeatures.append(gc.getInfoTypeForString('FEATURE_JUNGLE'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_SAVANNA'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FOREST'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_DICHTERWALD'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FOREST_BURNT'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_OASIS'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_SWAMP'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_SEUCHE'))

      terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
      terr_plains = gc.getInfoTypeForString('TERRAIN_PLAINS')

      improv1 = gc.getInfoTypeForString('IMPROVEMENT_FORT')
      improv2 = gc.getInfoTypeForString('IMPROVEMENT_FORT2')
      improv3 = gc.getInfoTypeForString('IMPROVEMENT_TURM2')

      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      elif iMapSize < 5: iMax = 2
      else: iMax = 4

      # 10 Versuche max. 4 Heuschreckenplagen zu kreieren
      for i in range (10):

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() not in lFeatures and not pPlot.isPeak() \
          and (pPlot.getTerrainType() == terr_desert or pPlot.getTerrainType() == terr_plains):
            OwnerArray = []
            iMaxEffect += 1
            for i in range(3):
              for j in range(5):
                # An den aeusseren Grenzen etwas auflockern
                if j == 0 or j == 4: iSetStorm = self.myRandom(2, None)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if not (loopPlot.isWater() or loopPlot.isPeak()) and loopPlot.getFeatureType() not in lFeatures \
                    and (loopPlot.getTerrainType() == terr_desert or loopPlot.getTerrainType() == terr_plains):
                      if loopPlot.getImprovementType() != improv1 and loopPlot.getImprovementType() != improv2 and loopPlot.getImprovementType() != improv3:
                        if loopPlot.getImprovementType() != gc.getInfoTypeForString("IMPROVEMENT_MINE") and loopPlot.getImprovementType() != gc.getInfoTypeForString("IMPROVEMENT_QUARRY"):
                          loopPlot.setImprovementType(-1)
                      loopPlot.setFeatureType(feat_grasshopper,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_GRASSHOPPERS",("",)),None,2,gc.getFeatureInfo(feat_grasshopper).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

        # Maximal iMax Heuschreckenplagen
        if iMaxEffect == iMax: break

  def doNebel(self):

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_nebel = gc.getInfoTypeForString('FEATURE_NEBEL')
      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')

      terr_ocean = gc.getInfoTypeForString('TERRAIN_OCEAN')
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      else: iMax = 3

      # 10 Versuche max. iMax Nebel zu kreieren
      for i in range (10):

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_ice and pPlot.getTerrainType() == terr_ocean:
            OwnerArray = []
            iMaxEffect += 1
            for i in range(10):
              for j in range(7):
                # An den aeusseren Grenzen etwas auflockern
                if i == 0 or i == 9 or j == 0 or j == 6: iSetStorm = self.myRandom(3, None)
                elif i == 1 or i == 8 or j == 1 or j == 5: iSetStorm = self.myRandom(2, None)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
                      loopPlot.setFeatureType(feat_nebel,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_NEBEL",("",)),None,2,gc.getFeatureInfo(feat_nebel).getButton(),ColorTypes(14),iRandX,iRandY,True,True)

        # Maximal 3 Nebeldecken
        if iMaxEffect == iMax: break

  def doSeesturm(self):

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_seesturm = gc.getInfoTypeForString('FEATURE_SEESTURM')
      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')

      terr_coast = gc.getInfoTypeForString('TERRAIN_COAST')
      terr_ocean = gc.getInfoTypeForString('TERRAIN_OCEAN')
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize == 0: iMax = 1
      elif iMapSize == 1: iMax = 2
      elif iMapSize == 2: iMax = 2
      elif iMapSize == 3: iMax = 3
      elif iMapSize == 4: iMax = 3
      elif iMapSize == 5: iMax = 4
      else: iMax = 5

      # 20 Versuche max. iMax Seestuerme zu kreieren
      for i in range (20):

        # Maximal 5 Seestuerme
        if iMaxEffect == iMax: break

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_ice and pPlot.getTerrainType() == terr_coast or pPlot.getTerrainType() == terr_ocean:
            OwnerArray = []
            iMaxEffect += 1
            for i in range(8):
              for j in range(5):
                # An den aeusseren Grenzen etwas auflockern
                if i == 0 or i == 7 or j == 0 or j == 4: iSetStorm = self.myRandom(2, None)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_coast or loopPlot.getTerrainType() == terr_ocean:
                      if loopPlot.getImprovementType() > -1:
                        loopPlot.setImprovementType(-1)
                        if loopPlot.getOwner() > -1:
                          if gc.getPlayer(loopPlot.getOwner()).isHuman():
                            CyInterface().addMessage(gc.getPlayer(loopPlot.getOwner()).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_SEESTURM_FISCHERBOOT",("",)),None,2,gc.getFeatureInfo(feat_seesturm).getButton(),ColorTypes(7),loopPlot.getX(),loopPlot.getY(),True,True)
                      loopPlot.setFeatureType(feat_seesturm,0)
                      self.doKillUnits(pPlot, 10)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_SEESTURM",("",)),None,2,gc.getFeatureInfo(feat_seesturm).getButton(),ColorTypes(7),iRandX,iRandY,True,True)


  def doTornado(self):
    iMaxEffect = 0

    feat_tornado = gc.getInfoTypeForString('FEATURE_TORNADO')
    feat_sturm = gc.getInfoTypeForString('FEATURE_STURM')
    feat_seesturm = gc.getInfoTypeForString('FEATURE_SEESTURM')

    feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
    feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
    iMapSize = gc.getMap().getWorldSize()
    if iMapSize == 0: iMax = 1
    elif iMapSize == 1: iMax = 2
    elif iMapSize == 2: iMax = 3
    elif iMapSize == 3: iMax = 4
    elif iMapSize == 4: iMax = 5
    elif iMapSize == 5: iMax = 6
    else: iMax = 7

    # 10 Versuche fuer max. iMax Tornados
    for i in range (10):

        # Maximal iMax Effekte
        if iMaxEffect == iMax: break

        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)
        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

         if pPlot.getFeatureType() == iDarkIce: continue
         if not pPlot.isPeak():
          if pPlot.getFeatureType() != feat_swamp and pPlot.getFeatureType() != feat_flood_plains and pPlot.getFeatureType() != feat_oasis:
            iMaxEffect += 1
            if not pPlot.isCity(): pPlot.setRouteType(-1)
            pPlot.setImprovementType(-1)
            pPlot.setFeatureType(feat_tornado,0)

            iPlayer = pPlot.getOwner()
            pOwner = gc.getPlayer(iPlayer)

            if iPlayer != -1:

              if pPlot.isVisibleToWatchingHuman(): CyCamera().JustLookAtPlot(pPlot)

              if gc.getPlayer(iPlayer).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_TORNADO",("", )))
                popupInfo.addPopup(iPlayer)
                CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO",("",)),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

            if pPlot.isCity():
              pCity = pPlot.getPlotCity()
              iPop_alt = pCity.getPopulation()
              iPop_neu = int(pCity.getPopulation() / 2)
              if iPop_neu < 1: iPop_neu = 1
              pCity.setPopulation(iPop_neu)
              if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman() and pPlot.isVisibleToWatchingHuman():
                  if gc.getPlayer(iPlayer).isHuman():
                    CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
                  else:
                    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO_CITY_OTHER",(pOwner.getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(2),iRandX,iRandY,True,True)
              # City, Wahrscheinlichkeit in %
              self.doDestroyCityBuildings(pCity,25)
              self.doKillUnits(pPlot, 10)
              self.doCheckCityState(pCity)

            # rundherum Sturm kreieren
            for i in range(3):
              for j in range(3):
                loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
                if None != loopPlot and not loopPlot.isNone():
                  if loopPlot.getFeatureType() == iDarkIce: continue
                  if loopPlot.getFeatureType() == -1 and not loopPlot.isPeak():
                    if loopPlot.isWater(): loopPlot.setFeatureType(feat_seesturm,0)
                    else: loopPlot.setFeatureType(feat_sturm,0)


  def doErdbeben(self, iX, iY):
    # Effekt
    earthquakeEffect = gc.getInfoTypeForString("EFFECT_RES_BOMB")
    bonusPlotArray = []

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    # Effekt beim Vulkanausbruch
    if iX > 0 and iY > 0:
      CyEngine().triggerEffect( earthquakeEffect, gc.getMap().plot(iX, iY).getPoint() )

    else:

      feat_erdbeben = gc.getInfoTypeForString('FEATURE_ERDBEBEN')
      feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

      feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
      feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
      feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
      feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
      terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')

      # Staerkegrad des Erdbebens 6 - 9
      # 6 - Radius 1: Modernisierungen 60%, Stadt: Gebaeude 15%, Units 10%
      # 7 - Radius 1: Modernisierungen 70%, Stadt: Gebaeude 30%, Units 30%, -2 Pop, Land: Units 10%
      # 8 - Radius 2: Modernisierungen 80%
      #               Epi + 1:  Stadt: Gebaeude 50%, Units 50%, Pop / 2,   Land: Units 20%
      #               Radius 2: Stadt: Gebaeude 30%, Units 30%, Pop - 1/3, Land: Units 10%
      # 9 - Radius 3: Modernisierungen 90%
      #               Epi + 1: Pop < 6: Stadt und Units 100%,
      #                        Pop > 5: 3/4 Pop weg, Gebaeude 80%, Wunder 50%, Units 80%
      #                        Land: Units 40%
      #               Radius 2: Pop / 2, Stadt:   Gebaeude 60%, Units 60%, Land: Units 30%
      #               Radius 3: Pop - 1/3, Stadt: Gebaeude 40%, Units 40%, Land: Units 20%
      iSkala = 6 + self.myRandom(4, None)

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      # Plot soll nicht ganz am Rand sein
      iRandX = 3 + self.myRandom(iMapW - 3, None)
      iRandY = 3 + self.myRandom(iMapH - 3, None)
      pPlot = gc.getMap().plot(iRandX, iRandY)
      iPlayer = pPlot.getOwner()

      if None != pPlot and not pPlot.isNone():

       if not pPlot.isWater() and pPlot.getFeatureType() != iDarkIce:

        if pPlot.isVisibleToWatchingHuman(): CyCamera().JustLookAtPlot(pPlot)

        # ERDBEBEN 6, 7
        if iSkala < 8:

          if iPlayer != -1:
            if gc.getPlayer(iPlayer).isHuman():
              # Message: Ein gewaltiges Erdbeben der Staerke %d erschuettert Euer Land!
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_6_OR_7",(iSkala,0)))
              popupInfo.addPopup(iPlayer)
              CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_6_OR_7",(iSkala,0)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  pCity.setFood(0)
                  if iSkala == 6:
                    self.doDestroyCityBuildings(pCity, 15)
                    self.doKillUnits(loopPlot, 10)
                  else:
                    self.doDestroyCityBuildings(pCity, 30)
                    self.doKillUnits(loopPlot, 30)
                    iPopAlt = pCity.getPopulation()
                    iPopNeu = 0
                    if iPopAlt > 4: iPopNeu = iPopAlt - 2
                    elif iPopAlt > 2: iPopNeu = iPopAlt - 1
                    else: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)

                    if iPopNeu and iPlayer != -1:
                      if gc.getPlayer(iPlayer).isHuman():
                        # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                        CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  self.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = self.myRandom(10, None)
                  if iSkala == 6:
                    iLimit = 6
                  else:
                    iLimit = 7
                    self.doKillUnits(loopPlot, 10)
                  if iRand < iLimit:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                      if self.myRandom(3, None) == 1: loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)

        # ERDBEBEN 8
        elif iSkala == 8:

          if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
            if pPlot.isVisibleToWatchingHuman():
              CyCamera().JustLookAtPlot(pPlot)
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte das Land.
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8",("",)))
              popupInfo.addPopup(gc.getGame().getActivePlayer())
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            else:
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte ein fernes Land.
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(5):
            for j in range(5):
              loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPopAlt = pCity.getPopulation()
                  if iBetrag < 2:
                    self.doDestroyCityBuildings(pCity, 50)
                    self.doKillUnits(loopPlot, 50)
                    iPopNeu = int(iPopAlt / 2)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    self.doDestroyCityBuildings(pCity, 30)
                    self.doKillUnits(loopPlot, 30)
                    iPopNeu = iPopAlt - int(iPopAlt / 3)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  self.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = self.myRandom(10, None)
                  if iRand < 8:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                      if self.myRandom(2, None) == 1: loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: self.doKillUnits(loopPlot, 20)
                  else: self.doKillUnits(loopPlot, 10)

        # ERDBEBEN 9
        elif iSkala > 8:

          if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
            if pPlot.isVisibleToWatchingHuman():
              CyCamera().JustLookAtPlot(pPlot)
              # Message: Ein katastrophales Erdbeben der Staerke 9 erschuetterte das Land.
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9",("",)))
              popupInfo.addPopup(gc.getGame().getActivePlayer())
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            else:
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte ein fernes Land.
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(7):
            for j in range(7):
              loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPopAlt = pCity.getPopulation()
                  if iBetrag < 2:
                    if iPopAlt < 6:
                      self.doDestroyCityWonders(pCity, 100, feat_erdbeben)
                      self.doKillUnits(loopPlot, 100)
                      pCity.kill()
                      if gc.getPlayer(iPlayer).isHuman():
                        # Message: Die Stadt %s und dessen Bevoelkerung wurde in ihren Truemmern begraben....
                        CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_CITY_DESTROYED",(pCity.getName(),)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)
                    else:
                      self.doDestroyCityWonders(pCity, 50, feat_erdbeben)
                      self.doDestroyCityBuildings(pCity, 80)
                      self.doKillUnits(loopPlot, 80)
                      iPopNeu = int(iPopAlt / 4)
                      pCity.setPopulation(iPopNeu)
                  elif iBetrag < 3:
                    self.doDestroyCityBuildings(pCity, 60)
                    self.doKillUnits(loopPlot, 60)
                    iPopNeu = int(iPopAlt / 2)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    self.doDestroyCityBuildings(pCity, 40)
                    self.doKillUnits(loopPlot, 40)
                    iPopNeu = iPopAlt - int(iPopAlt / 3)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)


                  if not pCity.isNone() and iPlayer != -1:
                    pCity.setFood(0)
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  self.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = self.myRandom(100, None)
                  if iRand < 90:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: self.doKillUnits(loopPlot, 40)
                  elif iBetrag < 3: self.doKillUnits(loopPlot, 30)
                  else: self.doKillUnits(loopPlot, 20)


        # Vergabe einer Bonus Resource 20%
        if len(bonusPlotArray) > 0:
          if 2 > self.myRandom(10, None):
            lBonus = []
            lBonus.append(gc.getInfoTypeForString("BONUS_GEMS"))
            lBonus.append(gc.getInfoTypeForString("BONUS_COPPER"))
            lBonus.append(gc.getInfoTypeForString("BONUS_IRON"))
            lBonus.append(gc.getInfoTypeForString("BONUS_MARBLE"))
            lBonus.append(gc.getInfoTypeForString("BONUS_STONE"))
            lBonus.append(gc.getInfoTypeForString("BONUS_OBSIDIAN"))
            lBonus.append(gc.getInfoTypeForString("BONUS_MAGNETIT"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ZINK"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ZINN"))
            lBonus.append(gc.getInfoTypeForString("BONUS_COAL"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ELEKTRON"))
            lBonus.append(gc.getInfoTypeForString("BONUS_GOLD"))
            lBonus.append(gc.getInfoTypeForString("BONUS_SILVER"))
            lBonus.append(gc.getInfoTypeForString("BONUS_SALT"))
            iRand = self.myRandom(len(lBonus), None)
            iBonus = lBonus[iRand]

            iRandPlot = self.myRandom(len(bonusPlotArray), None)
            bonusPlotArray[iRandPlot].setBonusType(iBonus)
            if bonusPlotArray[iRandPlot].getOwner() > -1:
              if gc.getPlayer(bonusPlotArray[iRandPlot].getOwner()).isHuman():
                CyInterface().addMessage(bonusPlotArray[iRandPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iBonus).getDescription(),)), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(14), bonusPlotArray[iRandPlot].getX(), bonusPlotArray[iRandPlot].getY(), True, True)


        # Zusaetzliche Gefahren durch das Erdbeben

        # Vulkan
        if pPlot.isPeak() and iSkala > 7:
          self.doVulkan(iRandX, iRandY, iSkala)

       # Unterwassererdbeben
       elif iSkala > 8:

         # Testen ob es ein Ozean ist
         iNumWaterTiles = 0
         for i in range(5):
           for j in range(5):
             loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
             if None != loopPlot and not loopPlot.isNone():
               if loopPlot.getFeatureType() == iDarkIce: continue
               if loopPlot.isWater(): iNumWaterTiles += 1
         # Statt dem Erbeben wird ein Tsunami zum Leben erweckt
         if iNumWaterTiles > 9:
           self.doTsunami(iRandX, iRandY)


  def doVulkan(self, iX, iY, iSkala):

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    # iX, iY und iSkala vom Feature Erbeben: iSkala 8 oder 9
    # Wenn das nicht gegeben ist, einen eigenen Vulkanausbruch erzeugen
    if iSkala == 0:
      iSkala = 8 + self.myRandom(2, None)

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      # 10 Versuche einen Berg ausfindig zu machen
      for i in range (10):
        # Plot soll nicht ganz am Rand sein
        iRandX = 3 + self.myRandom(iMapW - 3, None)
        iRandY = 3 + self.myRandom(iMapH - 3, None)
        if gc.getMap().plot(iRandX, iRandY).isPeak():
          iX = iRandX
          iY = iRandY
          break

    if iX > 0 and iY > 0:
      pPlot = gc.getMap().plot(iX, iY)

      terr_peak   = gc.getInfoTypeForString("TERRAIN_PEAK")
      terr_tundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
      terr_coast  = gc.getInfoTypeForString("TERRAIN_COAST")
      feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")
      feat_brand  = gc.getInfoTypeForString("FEATURE_SMOKE")
      feat_saurer_regen = gc.getInfoTypeForString("FEATURE_SAURER_REGEN")

      feat_swamp = gc.getInfoTypeForString("FEATURE_SWAMP")
      feat_flood_plains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

      feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
      feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
      feat_jungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
      feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

      bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
      bonus_obsidian = gc.getInfoTypeForString("BONUS_OBSIDIAN")
      bonusPlotArray = []

      if pPlot.isPeak():
        pPlot.setPlotType (PlotTypes.PLOT_LAND,True,True)
        pPlot.setTerrainType(terr_tundra,1,1)

      pPlot.setFeatureType(feat_vulkan,0)

      # Meldungen -----
      # Staerke 1
      if iSkala == 8:
        if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
          if pPlot.isVisibleToWatchingHuman():
            CyCamera().JustLookAtPlot(pPlot)
            # Message: Ein verheerender Vulkanausbruch legt das Land in Schutt und Asche.
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_1",("",)))
            popupInfo.addPopup(gc.getGame().getActivePlayer())
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_1",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

      # Staerke 2
      else:
        if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
          if pPlot.isVisibleToWatchingHuman():
            CyCamera().JustLookAtPlot(pPlot)
            # Message: Ein katastrophaler Vulkanausbruch legt das Land in Schutt und Asche.
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2",("",)))
            popupInfo.addPopup(gc.getGame().getActivePlayer())
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
          else:
            # Message: Ein katastrophaler Vulkanausbruch legt ein fernes Land in Schutt und Asche.
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

      # Staerke 1 (iSkala 8): 1 Plot Radius
      #   Stadt: Pop / 2, Gebaeude 50%, Units 50%
      #   Land:  Units 25%
      #   Feature: Sauerer Regen: Umkreis von 5 Plots

      # Staerke 2 (iSkala 9): 2 Plots Radius
      #   Radius 1:
      #     Stadt: Pop = 1/4, Gebaeude 75%, Units 75%
      #     Land:  Units 50%
      #   Radius 2:
      #     Stadt: Pop / 2, Gebaeude 50%, Units 50%
      #     Land:  Units 25%
      #   Feature: Sauerer Regen: Umkreis von 1 Plot, Ellipse nach Osten oder Westen: 15 Plots

      iRandX = iX
      iRandY = iY

      # Effekt
      earthquakeEffect = gc.getInfoTypeForString("EFFECT_RES_BOMB")
      volcanoEffect = gc.getInfoTypeForString("EFFECT_OMEN_HORSEMAN")
      CyEngine().triggerEffect( volcanoEffect, pPlot.getPoint() )

      PlayerPopUpFood = []

      # Staerke 1
      if iSkala == 8:

          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater() and i != 1 and j != 1: CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPlayer = pCity.getOwner()
                  iPopAlt = pCity.getPopulation()

                  self.doDestroyCityBuildings(pCity, 50)
                  self.doKillUnits(loopPlot, 50)
                  iPopNeu = int(iPopAlt / 2)
                  if iPopNeu < 2: iPopNeu = 1
                  pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  self.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                else:
                  loopPlot.setRouteType(-1)
                  loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isWater() and not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_vulkan and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else: loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  self.doKillUnits(loopPlot, 25)

                # Plot fuer Bonus checken
                # Vergabe ganz unten
                if not loopPlot.isWater() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1 and loopPlot.isHills():
                  bonusPlotArray.append(loopPlot)

                # Dem Plot +1 Nahrung geben (25%)
                if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and not (i==1 and j==1):
                 if loopPlot.getFeatureType != feat_vulkan and loopPlot.getTerrainType() != terr_tundra:
                  if self.myRandom(4, None) == 1:
                    gc.getGame().setPlotExtraYield(iRandX - 2 + i, iRandY - 2 + j, 0, 1) # x,y,YieldType,iChange
                    iOwner = loopPlot.getOwner()
                    if iOwner != -1:
                     if gc.getPlayer(iOwner).isHuman():
                      CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)
                      # fuer spaeteres popup
                      if gc.getPlayer(iOwner).getID() not in PlayerPopUpFood: PlayerPopUpFood.append(gc.getPlayer(iOwner).getID())

                # Verbreitbare Resi vernichten
                if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                  self.doEraseBonusFromDisaster(loopPlot)

          # Sauerer Regen
          for i in range(7):
            for j in range(7):
              loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                #loopPlot.setRouteType(-1)
                if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                and loopPlot.getFeatureType() != feat_brand and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak():
                  if loopPlot.getFeatureType() != feat_forest_burnt:
                    loopPlot.setFeatureType(feat_saurer_regen,0)


      # Staerke 2
      else:

          for i in range(5):
            for j in range(5):
              loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater() and i != 2 and j != 2: CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Entfernung zum Vulkan berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPlayer = pCity.getOwner()
                  iPopAlt = pCity.getPopulation()

                  if iBetrag < 2:
                    self.doDestroyCityBuildings(pCity, 75)
                    self.doKillUnits(loopPlot, 75)
                    iPopNeu = int(iPopAlt / 4)
                    if iPopNeu < 1: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    self.doDestroyCityBuildings(pCity, 50)
                    self.doKillUnits(loopPlot, 50)
                    iPopNeu = iPopAlt - int(iPopAlt / 2)
                    if iPopNeu < 1: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  self.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                else:
                  loopPlot.setRouteType(-1)
                  loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isWater() and loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains \
                  and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak() and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else: loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: self.doKillUnits(loopPlot, 50)
                  else: self.doKillUnits(loopPlot, 25)

                # Plot fuer Bonus checken
                # Nur 1 Plot rund um den Vulkan
                # Vergabe ganz unten
                if i > 0 and i < 4 and j > 0 and j < 4:
                  if not loopPlot.isWater() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1 and loopPlot.isHills():
                    bonusPlotArray.append(loopPlot)

                # Dem Plot +1 Nahrung geben (25%)
                if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and not (i==2 and j==2):
                 if loopPlot.getFeatureType != feat_vulkan and loopPlot.getTerrainType() != terr_tundra:
                  if self.myRandom(4, None) == 1:
                    gc.getGame().setPlotExtraYield(iRandX - 2 + i, iRandY - 2 + j, 0, 1) # x,y,YieldType,iChange
                    iOwner = loopPlot.getOwner()
                    if iOwner != -1:
                     if gc.getPlayer(iOwner).isHuman():
                      CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)
                      # fuer spaeteres popup
                      if gc.getPlayer(iOwner).getID() not in PlayerPopUpFood: PlayerPopUpFood.append(gc.getPlayer(iOwner).getID())

                # Verbreitbare Resi vernichten
                if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                  self.doEraseBonusFromDisaster(loopPlot)

          # Sauerer Regen
          # Ellipse nach Osten oder Westen: 15 Plots
          iRand_W_O = self.myRandom(2, None)
          for i in range(20):
            for j in range(11):

              if iRand_W_O == 1:
                loopPlot = gc.getMap().plot(iRandX + i, iRandY - 5 + j)
              else:
                loopPlot = gc.getMap().plot(iRandX - i, iRandY - 5 + j)

              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak():
                  bDraw = False
                  if   (i == 0 or i == 19) and j > 3 and j < 8: bDraw = True
                  elif (i == 1 or i == 18) and j > 2 and j < 8: bDraw = True
                  elif (i == 2 or i == 17) and j > 1 and j < 9: bDraw = True
                  elif (i == 3 or i == 4 or i == 15 or i == 16) and j > 0 and j < 10: bDraw = True
                  elif (i > 4 and i < 15): bDraw = True
                  if bDraw:
                    #loopPlot.setRouteType(-1)
                    bSetRegen = False
                    if loopPlot.getFeatureType() == -1: bSetRegen = True
                    elif loopPlot.getFeatureType() != feat_forest_burnt:
                      if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                        if self.myRandom(2, None) == 1: bSetRegen = True

                    if bSetRegen:
                      loopPlot.setFeatureType(feat_saurer_regen,0)



          # Vulkan wird zu Wasser, wenn auf einer (Halb)Insel
          # Sprengt sich weg (somit keine Vulkan-Feature-Grafik notwendig)
          iNumWaterTiles = 0
          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if loopPlot.isWater(): iNumWaterTiles += 1
          # Statt dem Erbeben wird ein Tsunami zum Leben erweckt
          if iNumWaterTiles > 3:
            pPlot.setFeatureType(-1,0)
            pPlot.setTerrainType(terr_coast,1,1)
            pPlot.setPlotType(PlotTypes.PLOT_OCEAN,True,True)
            self.doTsunami(iRandX,iRandY)


      # Message: PopUp wegen +1 Food
      iRange = len(PlayerPopUpFood)
      if iRange > 0:
        for i in range (iRange):
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD_POPUP",("",)))
          popupInfo.addPopup(PlayerPopUpFood[i])

      # Chance einer Magnetit und Obsidian Bonus Resource jeweils 50%
      iRange = len(bonusPlotArray)
      if iRange > 0:
        iRand = self.myRandom(3, None)
        iBonus = -1
        if iRand == 1: iBonus = bonus_magnetit
        elif iRand == 2: iBonus = bonus_obsidian

        if iBonus != -1:
          for iLoopPlot in range(iRange):
            iRand = self.myRandom(100, None)
            if iRand < 100 / (iLoopPlot+1):
              bonusPlotArray[iLoopPlot].setBonusType(iBonus)
              if bonusPlotArray[iLoopPlot].getOwner() > -1:
                if gc.getPlayer(bonusPlotArray[iLoopPlot].getOwner()).isHuman():
                  CyInterface().addMessage(bonusPlotArray[iLoopPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iBonus).getDescription(),)), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(14), bonusPlotArray[iLoopPlot].getX(), bonusPlotArray[iLoopPlot].getY(), True, True)



  def undoVulkan(self):

    terr_peak = gc.getInfoTypeForString("TERRAIN_PEAK")
    feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for i in range (iMapW):
      for j in range (iMapH):
        pPlot = CyMap().plot(i, j)

        if pPlot.getFeatureType() == feat_vulkan:
          #iYield = pPlot.getYield(0)
          #if iYield > 0: gc.getGame().setPlotExtraYield(i, j, 0, -iYield) # x,y,YieldType,iChange
          # Reihenfolge einhalten! wichtig!!!
          pPlot.setFeatureType(-1,0)
          pPlot.setTerrainType(terr_peak,1,1)
          pPlot.setPlotType(PlotTypes.PLOT_PEAK,True,True)

  # --------- Ende Vulkan / Volcano ------------

  def doTsunami(self, iX, iY):

    feat_seuche = gc.getInfoTypeForString("FEATURE_SEUCHE")
    feat_saurer_regen = gc.getInfoTypeForString("FEATURE_SAURER_REGEN")

    feat_swamp = gc.getInfoTypeForString("FEATURE_SWAMP")
    feat_flood_plains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
    feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")
    feat_tsunami = gc.getInfoTypeForString("FEATURE_TSUNAMI")

    iBuildingPalisade = gc.getInfoTypeForString('BUILDING_PALISADE')
    iBuildingWalls = gc.getInfoTypeForString('BUILDING_WALLS')
    iBuildingHW1 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS')
    iBuildingHW2 = gc.getInfoTypeForString('BUILDING_CELTIC_DUN')
    iBuildingHW3 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS_GRECO')

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    # Der Tsunamieffekt muss im 2ten Wasserfeld vor der Kueste (Land) gestartet werden
    # Der Schaden soll bis einschliesslich 4 Landplots reingehen
    # Der Einschlag/Das Epizentrum darf maximal 3 Felder ausserhalb der Kueste (Land) sein, sonst unwirksam
    # Huegel und Berge stoppen den Schaden an weiteren Feldern
    # Plot 1: Stadt: Pop - 1/2, Units 15%, Gebaeude 10%, Mods + Streets
    # Plot 2: Stadt: Pop - 1/3, Units 10%, Gebaeude  5%, Mods + Streets
    #         Ausgenommen: Stadt auf Huegel mit Stadtmauer: Pop - 1/4, Units und Gebaeude 0%
    # Plot 3: Stadt: Pop - 1/4, Units  5%, Mods + Streets
    #         Ausgenommen: Stadt auf Huegel mit Stadtmauer: Sicher
    # Plot 4: Nur Modernisierungen
    # Stadtmauer 50%, Palisade 100% und Hohe Mauer 20% weg

    for iHimmelsrichtung in range(4):
      iDamageMaxPlots = 4
      bEffectDone = False
      bDoTsunami = False

      # 3 Plots dicke Flutkatastrophe
      for d in range(3):
       # Checken ob innerhalb von 4 Feldern Land ist
       for i in range(4):
         if iHimmelsrichtung == 0:   loopPlot = CyMap().plot(iX - 1 + d, iY + i) # Norden
         elif iHimmelsrichtung == 1: loopPlot = CyMap().plot(iX - 1 - d, iY - i) # Sueden
         elif iHimmelsrichtung == 2: loopPlot = CyMap().plot(iX + i, iY - 1 + d) # Osten
         elif iHimmelsrichtung == 3: loopPlot = CyMap().plot(iX - i, iY - 1 + d) # Westen
         if None != loopPlot and not loopPlot.isNone():
           if loopPlot.getFeatureType() == iDarkIce: continue
           if not loopPlot.isWater(): bDoTsunami = True

      if bDoTsunami == True:

       for d in range(3):
         iDamagePlots = 0

         if iHimmelsrichtung == 0:   iRange = iMapH - iY
         elif iHimmelsrichtung == 1: iRange = iY
         elif iHimmelsrichtung == 2: iRange = iMapW - iX
         elif iHimmelsrichtung == 3: iRange = iX

         for i in range(iRange):

          if iHimmelsrichtung == 0:   loopPlot = CyMap().plot(iX - 1 + d, iY + i)
          elif iHimmelsrichtung == 1: loopPlot = CyMap().plot(iX - 1 + d, iY - i)
          elif iHimmelsrichtung == 2: loopPlot = CyMap().plot(iX + i, iY - 1 + d)
          elif iHimmelsrichtung == 3: loopPlot = CyMap().plot(iX - i, iY - 1 + d)

          # 0: Einschlag/Epizentrum
          # Ende bei Max Plots
          if iDamagePlots >= iDamageMaxPlots: break
          # Ende bei DarkIce
          if loopPlot.getFeatureType() == iDarkIce: break
          # Ende bei Berg oder aktivem Vulkan
          if loopPlot.isPeak() or loopPlot.getFeatureType() == feat_vulkan: break
          # Ende wenn es ein Landstrich ist
          if iDamagePlots > 0 and loopPlot.isWater(): break

          # Land
          if i > 0 and not loopPlot.isWater():
           iDamagePlots += 1

           # Effekt
           if not bEffectDone and d == 1:
             if iHimmelsrichtung == 0:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_N")
               pEffectPlot = CyMap().plot(iX, iY + i - 2)
             elif iHimmelsrichtung == 1:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_S")
               pEffectPlot = CyMap().plot(iX, iY - i + 2)
             elif iHimmelsrichtung == 2:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_E")
               pEffectPlot = CyMap().plot(iX + i - 2, iY)
             elif iHimmelsrichtung == 3:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_W")
               pEffectPlot = CyMap().plot(iX - i + 2, iY)
             CyEngine().triggerEffect( iEffect, pEffectPlot.getPoint() )
             bEffectDone = True

             if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
               if pEffectPlot.isVisibleToWatchingHuman():
                 CyCamera().JustLookAtPlot(pEffectPlot)
                 # Message: Eine gigantische Flutwelle trifft die Kueste und versetzt das Land in aergste Not!
                 popupInfo = CyPopupInfo()
                 popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                 popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_TSUNAMI",("",)))
                 popupInfo.addPopup(gc.getGame().getActivePlayer())
                 CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_TSUNAMI",("",)), "AS2D_TSUNAMI", 2, gc.getFeatureInfo(feat_tsunami).getButton(), ColorTypes(7), pEffectPlot.getX(), pEffectPlot.getY(), True, True)


           # Stadt
           if loopPlot.isCity():
             pCity = loopPlot.getPlotCity()
             iPlayer = pCity.getOwner()
             iPopAlt = pCity.getPopulation()
             iPopNeu = iPopAlt

             if iDamagePlots == 0:
               self.doDestroyCityBuildings(pCity, 10)
               self.doKillUnits(loopPlot, 15)
               iPopNeu = iPopAlt - int(iPopAlt / 2)
               if iPopNeu < 1: iPopNeu = 1
               pCity.setPopulation(iPopNeu)
             elif iDamagePlots == 1:
               # Stadt mit Stadtmauern und Huegel
               if loopPlot.isHills() and (pCity.isHasBuilding(iBuildingWalls) or pCity.isHasBuilding(iBuildingHW1) or pCity.isHasBuilding(iBuildingHW2) or pCity.isHasBuilding(iBuildingHW3) ):
                 iPopNeu = iPopAlt - int(iPopAlt / 4)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
               else:
                 self.doDestroyCityBuildings(pCity, 5)
                 self.doKillUnits(loopPlot, 10)
                 iPopNeu = iPopAlt - int(iPopAlt / 3)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
             elif iDamagePlots == 2:
               # Stadt mit Stadtmauern und Huegel
               if loopPlot.isHills() and (pCity.isHasBuilding(iBuildingWalls) or pCity.isHasBuilding(iBuildingHW1) or pCity.isHasBuilding(iBuildingHW2) or pCity.isHasBuilding(iBuildingHW3) ):
                 break
               else:
                 self.doKillUnits(loopPlot, 5)
                 iPopNeu = iPopAlt - int(iPopAlt / 4)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
             pCity.setFood(0)

             # Stadtmauern zerstoeren
             self.doDestroyWalls(pCity)

             if iPlayer != -1 and iPopNeu != iPopAlt:
               if gc.getPlayer(iPlayer).isHuman():
                 # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                 CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_tsunami).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

             self.doCheckCityState(pCity)

           # Land
           else:
             if iDamagePlots + 1 < iDamageMaxPlots: loopPlot.setRouteType(-1)
             loopPlot.setImprovementType(-1)
             if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains \
             and loopPlot.getFeatureType() != feat_saurer_regen and loopPlot.getFeatureType() != feat_oasis:
               loopPlot.setFeatureType(feat_seuche,0)
             self.doKillUnits(loopPlot, 30)

           # Bei Huegel Tsunami stoppen
           if loopPlot.isHills(): iDamagePlots = iDamageMaxPlots

# ----------- Ende Tsunami ------------

  def doMeteorites(self):

    feat_meteor = gc.getInfoTypeForString('FEATURE_METEORS')
    feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

    feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
    feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

    feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
    feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
    feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

    feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
    terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")

    bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
    bonus_oreichalkos = gc.getInfoTypeForString("BONUS_OREICHALKOS")
    bonusPlotArray = []

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
    iMaxEffect = 0
    iMapSize = gc.getMap().getWorldSize()
    if iMapSize == 0: iMax = 1
    elif iMapSize == 1: iMax = 2
    elif iMapSize == 2: iMax = 4
    elif iMapSize == 3: iMax = 6
    elif iMapSize == 4: iMax = 8
    elif iMapSize == 5: iMax = 10
    else: iMax = 12

    # 20 Chancen fuer max. iMax Meteorstrikes
    for i in range (20):

        # Maximal iMax Effekte
        if iMaxEffect == iMax: break

        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()

        iRandX = self.myRandom(iMapW, None)
        iRandY = self.myRandom(iMapH, None)
        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

            if pPlot.getFeatureType() == iDarkIce: continue
            iMaxEffect += 1

            # Modernisierung und Strasse entfernen
            if not pPlot.isCity():
               pPlot.setRouteType(-1)
               pPlot.setImprovementType(-1)

            iPlayer = pPlot.getOwner()

            if pPlot.isVisibleToWatchingHuman():
              CyCamera().JustLookAtPlot(pPlot)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_METEORITES",("",)))
              popupInfo.addPopup(gc.getGame().getActivePlayer())
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES",("",)),"AS2D_METEORSTRIKE",2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(7),iRandX,iRandY,True,True)


            # Effekt
            iEffect = gc.getInfoTypeForString("EFFECT_METEORS")
            CyEngine().triggerEffect( iEffect, pPlot.getPoint() )

            # Stadt
            if pPlot.isCity():
              pCity = pPlot.getPlotCity()
              iPop_alt = pCity.getPopulation()
              iPop_neu = int(pCity.getPopulation() / 2)
              if iPop_neu < 2: iPop_neu = 1
              pCity.setPopulation(iPop_neu)
              pCity.setFood(0)
              if iPlayer != -1:
                if pPlot.isVisibleToWatchingHuman():
                  if iPlayer == gc.getGame().getActivePlayer():
                    CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
                  else:
                    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES_CITY_OTHER",(gc.getPlayer(pCity.getOwner()).getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(2),iRandX,iRandY,True,True)

              # City, Wahrscheinlichkeit in %
              self.doKillUnits(pPlot,10)
              self.doDestroyCityBuildings(pCity,33)
              # Stadtmauern zerstoeren
              self.doDestroyWalls(pCity)
              self.doCheckCityState(pCity)

            # rundherum Brand generieren und dabei 50:50 Modernis und Strassen entfernen
            for i in range(3):
              for j in range(3):
                loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
                if None != loopPlot and not loopPlot.isNone():
                  if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() \
                  and not loopPlot.isWater() and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                    if loopPlot.getImprovementType() == iImpType1: loopPlot.setImprovementType(-1)

                  if self.myRandom(2, None) == 1:
                    if not loopPlot.isCity():
                      loopPlot.setRouteType(-1)
                      loopPlot.setImprovementType(-1)
                  self.doKillUnits(loopPlot,20)

                # Plot fuer Magnetit/Oreichalkos Bonus checken
                if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1:
                  bonusPlotArray.append(loopPlot)

                # Verbreitbare Resi vernichten
                if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                  self.doEraseBonusFromDisaster(loopPlot)


    # Chance einer neuen Bonus Resource, 25% - danach 50:50 - Magnetit:Oreichalkos
    if len(bonusPlotArray) > 0:
        iRand = self.myRandom(8, None)
        if iRand < 2:
          if iRand == 0: iNewBonus = bonus_magnetit
          else: iNewBonus = bonus_oreichalkos
          iRandPlot = self.myRandom(len(bonusPlotArray), None)
          bonusPlotArray[iRandPlot].setBonusType(iNewBonus)
          if bonusPlotArray[iRandPlot].getOwner() > -1:
            if gc.getPlayer(bonusPlotArray[iRandPlot].getOwner()).isHuman():
              CyInterface().addMessage(bonusPlotArray[iRandPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iNewBonus).getDescription(),)), None, 2, gc.getBonusInfo(iNewBonus).getButton(), ColorTypes(14), bonusPlotArray[iRandPlot].getX(), bonusPlotArray[iRandPlot].getY(), True, True)


  def doComet(self):

    feat_comet = gc.getInfoTypeForString('FEATURE_COMET')
    feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

    feat_swamp = gc.getInfoTypeForString('FEATURE_SWAMP')
    feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

    feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
    feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
    feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

    feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
    terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")

    bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
    bonus_oreichalkos = gc.getInfoTypeForString("BONUS_OREICHALKOS")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    iRangeMaxPlayers = gc.getMAX_PLAYERS()

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
    iMaxEffect = 0
    iMapSize = gc.getMap().getWorldSize()
    if iMapSize < 3: iMax = 1
    elif iMapSize < 5: iMax = 2
    else: iMax = 3

    # iMax Kometen
    for i in range (iMax):

     # Soll nicht ganz am Rand sein
     iRandX = 3 + self.myRandom(iMapW - 3, None)
     iRandY = 3 + self.myRandom(iMapH - 3, None)
     pPlot = gc.getMap().plot(iRandX, iRandY)
     if None != pPlot and not pPlot.isNone():

      if pPlot.getFeatureType() == iDarkIce: continue

      # Modernisierung und Strasse entfernen
      if not pPlot.isCity():
        pPlot.setRouteType(-1)
        pPlot.setImprovementType(-1)

      iPlayer = pPlot.getOwner()

      if pPlot.isVisibleToWatchingHuman():
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET",("",)),"AS2D_BOMBARD",2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
        CyCamera().JustLookAtPlot(pPlot)

      # Effekt
      if pPlot.isWater():
        CyEngine().triggerEffect( gc.getInfoTypeForString("EFFECT_COMET_WATER"), pPlot.getPoint() )
        # Loest Tsunami aus
        self.doTsunami(iRandX,iRandY)
      else:
        CyEngine().triggerEffect( gc.getInfoTypeForString("EFFECT_COMET"), pPlot.getPoint() )

        # Stadt
        if pPlot.isCity():
              pCity = pPlot.getPlotCity()
              iPop_alt = pCity.getPopulation()
              iPop_neu = int(pCity.getPopulation() / 6)
              if iPop_neu < 2: iPop_neu = 1
              pCity.setPopulation(iPop_neu)
              pCity.setFood(0)

              # Messages
              for iPlayer2 in range(iRangeMaxPlayers):
                pSecondPlayer = gc.getPlayer(iPlayer2)
                iSecondPlayer = pSecondPlayer.getID()
                if pSecondPlayer.isHuman():
                  iSecTeam = pSecondPlayer.getTeam()
                  if pPlot.isVisible(iSecTeam, 0) and pSecondPlayer.isHuman():
                    if iPlayer == iSecondPlayer:
                      popupInfo = CyPopupInfo()
                      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                      popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY",(pCity.getName(),iPop_neu,iPop_alt)))
                      popupInfo.addPopup(iPlayer)
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
                    else:
                      # Message an alle
                      CyInterface().addMessage(iSecondPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY_OTHER",(pOwner.getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(2),iRandX,iRandY,True,True)

              # City, Wahrscheinlichkeit in %
              self.doKillUnits(pPlot,100)
              self.doDestroyCityBuildings(pCity,80)
              self.doDestroyCityWonders(pCity,25,feat_comet)
              self.doCheckCityState(pCity)

        # rundherum Brand generieren und dabei 50:50 Modernis und Strassen entfernen
        for i in range(7):
          for j in range(7):
                loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
                if None != loopPlot and not loopPlot.isNone():
                  if loopPlot.getFeatureType() == iDarkIce: continue
                  if loopPlot.getFeatureType() != feat_swamp and loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                  and not loopPlot.isPeak() and not loopPlot.isWater():
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                    if loopPlot.getImprovementType() == iImpType1: loopPlot.setImprovementType(-1)

                  if self.myRandom(2, None) == 1:
                    if not loopPlot.isCity():
                      loopPlot.setRouteType(-1)
                      loopPlot.setImprovementType(-1)
                  # Entfernung zum Einschlag berechnen
                  iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())
                  if iBetrag == 1:
                    self.doKillUnits(loopPlot,50)
                    if loopPlot.isCity(): self.doDestroyCityBuildings(loopPlot.getPlotCity(),50)
                  elif iBetrag == 2:
                    self.doKillUnits(loopPlot,25)
                    if loopPlot.isCity(): self.doDestroyCityBuildings(loopPlot.getPlotCity(),25)
                  elif iBetrag == 3:
                    self.doKillUnits(loopPlot,10)
                    if loopPlot.isCity(): self.doDestroyCityBuildings(loopPlot.getPlotCity(),10)

                # Stadtmauern zerstoeren
                if loopPlot.isCity(): self.doDestroyWalls(loopPlot.getPlotCity())

                # Verbreitbare Resi vernichten (nur Radius 2)
                if i>0 and i<6 and j>1 and j<6:
                  if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                    self.doEraseBonusFromDisaster(loopPlot)

        # Chance einer neuen Bonus Resource fix auf pPlot
        # Chance 50% - danach 50:50 - Magnetit:Oreichalkos
        if not pPlot.isWater() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1 and pPlot.getBonusType(-1) == -1:
          iRand = self.myRandom(4, None)
          if iRand < 2:
            if iRand == 0: iNewBonus = bonus_magnetit
            else: iNewBonus = bonus_oreichalkos
            pPlot.setBonusType(iNewBonus)
            if pPlot.getOwner() > -1:
              if gc.getPlayer(pPlot.getOwner()).isHuman():
                CyInterface().addMessage(pPlot.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iNewBonus).getDescription(),)), None, 2, gc.getBonusInfo(iNewBonus).getButton(), ColorTypes(14), pPlot.getX(), pPlot.getY(), True, True)



  # ------------------- Anfang Gebaeude, Wunder und Einheiten Damage  -----------------


  # iChance = Wahrscheinlichkeit, dass ein Gebaeude zerstoert wird
  def doDestroyCityBuildings(self, pCity, iChance):
    iOwner = pCity.getOwner()
    lIgnoreBuildings = []
    lIgnoreBuildings.append(gc.getInfoTypeForString("BUILDING_SIEDLUNG"))
    lIgnoreBuildings.append(gc.getInfoTypeForString("BUILDING_KOLONIE"))
    lIgnoreBuildings.append(gc.getInfoTypeForString("BUILDING_STADT"))
    lIgnoreBuildings.append(gc.getInfoTypeForString("BUILDING_PROVINZ"))
    lIgnoreBuildings.append(gc.getInfoTypeForString("BUILDING_METROPOLE"))
    # PAE IV Update: Palast darf zerstoert werden... hehe ;)
    #iBuildingPalace = gc.getInfoTypeForString('BUILDING_PALACE')


    if pCity.getNumBuildings() > 0:
      iRange = gc.getNumBuildingInfos()
      for iBuilding in range(iRange):
        pBuilding = gc.getBuildingInfo(iBuilding)
        if pCity.getNumBuilding(iBuilding):
          if iBuilding not in lIgnoreBuildings and not isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType()):
            iRand = self.myRandom(100, None)
            if iRand < iChance:
              pCity.setNumRealBuilding(iBuilding,0)
              if iOwner != -1:
                if gc.getPlayer(iOwner).isHuman():
                  CyInterface().addMessage(gc.getPlayer(iOwner).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


  # iChance = Wahrscheinlichkeit, dass ein Wunder zerstoert wird
  # iFeatureType = Art der Katastrophe
  def doDestroyCityWonders(self, pCity, iChance, iFeatureType):
    iOwner = pCity.getOwner()
    iFeature_Erdbeben = gc.getInfoTypeForString("FEATURE_ERDBEBEN")
    iFeature_Komet = gc.getInfoTypeForString("FEATURE_COMET")

    iRangeMaxPlayers = gc.getMAX_PLAYERS()

    if pCity.getNumBuildings() > 0:
      iRange = gc.getNumBuildingInfos()
      for iBuilding in range(iRange):
        pBuilding = gc.getBuildingInfo(iBuilding)
        if pCity.getNumBuilding(iBuilding):
          if isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType()):
            iRand = self.myRandom(100, None)
            if iRand < iChance:
              pCity.setNumRealBuilding(iBuilding,0)

              # Messages
              pOwner = gc.getPlayer(iOwner)
              iOwnerTeam = pOwner.getTeam()
              for iAllPlayer in range (iRangeMaxPlayers):
                ThisPlayer = gc.getPlayer(iAllPlayer)
                iThisPlayer = ThisPlayer.getID()
                iThisTeam = ThisPlayer.getTeam()
                ThisTeam = gc.getTeam(iThisTeam)
                if ThisTeam.isHasMet(iOwnerTeam) and ThisPlayer.isHuman():

                  if iFeatureType == iFeature_Erdbeben:
                    CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER_ERDBEBEN",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_EARTHQUAKE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
                  elif iFeatureType == iFeature_Komet:
                    CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER_KOMET",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_PLAGUE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
                  else:
                    CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_PLAGUE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


  # iChance = Wahrscheinlichkeit, dass eine Unit gekillt wird
  def doKillUnits(self, pPlot, iChance):
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
      pUnit = pPlot.getUnit(iUnit)
      if pUnit != None:
        iRand = self.myRandom(100, None)
        if iRand < iChance:

          # Wenn ein General draufgeht hat das Auswirkungen
          if pUnit.getLeaderUnitType() > -1:
            self.doDyingGeneral(pUnit)

          if pUnit.getOwner() > -1:
            if gc.getPlayer(pUnit.getOwner()).isHuman():
              # Message: Eure Einheit %s hat diese schreckliche Naturgewalt nicht ueberlebt!
              CyInterface().addMessage( pUnit.getOwner(), True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_UNIT_KILLED",(pPlot.getUnit(iUnit).getName(),0)), "AS2D_PLAGUE", 2, pPlot.getUnit(iUnit).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

          # VOID kill (BOOL bDelay, INT PlayerType ePlayer)
          #pPlot.getUnit(iUnit).kill(1,pPlot.getUnit(iUnit).getOwner())
          pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

        else:
          pPlot.getUnit(iUnit).setDamage(60, -1)
          pPlot.getUnit(iUnit).setImmobileTimer(1)


  def doDestroyWalls(self, pCity):
    iPlayer = pCity.getOwner()
    iBuildingPalisade = gc.getInfoTypeForString('BUILDING_PALISADE')
    iBuildingWalls = gc.getInfoTypeForString('BUILDING_WALLS')
    iBuildingHW1 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS')
    iBuildingHW2 = gc.getInfoTypeForString('BUILDING_CELTIC_DUN')
    iBuildingHW3 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS_GRECO')

    # Stadtmauern zerstoeren
    if pCity.isHasBuilding(iBuildingPalisade):
              pBuilding = gc.getBuildingInfo(iBuildingPalisade)
              pCity.setNumRealBuilding(iBuildingPalisade,0)
              if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman():
                  CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

    if pCity.isHasBuilding(iBuildingWalls):
              if self.myRandom(100, None) < 50:
               pBuilding = gc.getBuildingInfo(iBuildingWalls)
               pCity.setNumRealBuilding(iBuildingWalls,0)
               if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman():
                 CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

    if pCity.isHasBuilding(iBuildingHW1):
              if self.myRandom(100, None) < 20:
               pBuilding = gc.getBuildingInfo(iBuildingHW1)
               pCity.setNumRealBuilding(iBuildingHW1,0)
               if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman():
                 CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

    if pCity.isHasBuilding(iBuildingHW2):
              if self.myRandom(100, None) < 20:
               pBuilding = gc.getBuildingInfo(iBuildingHW2)
               pCity.setNumRealBuilding(iBuildingHW2,0)
               if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman():
                 CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

    if pCity.isHasBuilding(iBuildingHW3):
              if self.myRandom(100, None) < 20:
               pBuilding = gc.getBuildingInfo(iBuildingHW3)
               pCity.setNumRealBuilding(iBuildingHW3,0)
               if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman():
                 CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


  # Naturkatastrophen vernichten verbreitbare Bonusresourcen
  # Nur bei Vulkan, Meteoriten und Kometen
  def doEraseBonusFromDisaster(self, pPlot):
    # Inits (von doBonusCityGetPlot)
    lGetreide = []
    lGetreide.append(gc.getInfoTypeForString("BONUS_WHEAT"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_GERSTE"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_HAFER"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_ROGGEN"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_HIRSE"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_RICE"))
    lVieh1 = []
    lVieh1.append(gc.getInfoTypeForString("BONUS_COW"))
    lVieh1.append(gc.getInfoTypeForString("BONUS_PIG"))
    lVieh1.append(gc.getInfoTypeForString("BONUS_SHEEP"))
    lSpice = []
    lSpice.append(gc.getInfoTypeForString("BONUS_OLIVES"))
    lSpice.append(gc.getInfoTypeForString("BONUS_DATTELN"))
    lTier1 = []
    lTier1.append(gc.getInfoTypeForString("BONUS_CAMEL"))

    # known bonus or unknown bonus(?)
    iPlayer = pPlot.getOwner()
    iBonus = pPlot.getBonusType(iPlayer)
    if iBonus == -1: iBonus = pPlot.getBonusType(-1)

    if iBonus > -1:
      if iBonus in lGetreide or iBonus in lVieh1 or iBonus in lSpice or iBonus in lTier1:
        pPlot.setBonusType(-1)
        if iPlayer > -1:
          if gc.getPlayer(iPlayer).isHuman():
            if iBonus in lGetreide:
              CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS1",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
            elif iBonus in lVieh1 or iBonus in lTier1:
              CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS2",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
            elif iBonus in lSpice:
              CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS3",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)


# ++++++++++++++++++ ENDE Naturkatastrophen / Disasters +++++++++++++++++++++++++++++


# New Seewind-Feature together with Elwood (ideas) and the TAC-Team (diagonal arrows)
  def doSeewind (self):

    terr_ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
    feat_ice = gc.getInfoTypeForString("FEATURE_ICE")
    feat_wind_n = gc.getInfoTypeForString("FEATURE_WIND_N")
    feat_wind_e = gc.getInfoTypeForString("FEATURE_WIND_E")
    feat_wind_s = gc.getInfoTypeForString("FEATURE_WIND_S")
    feat_wind_w = gc.getInfoTypeForString("FEATURE_WIND_W")
    feat_wind_ne = gc.getInfoTypeForString("FEATURE_WIND_NE")
    feat_wind_nw = gc.getInfoTypeForString("FEATURE_WIND_NW")
    feat_wind_se = gc.getInfoTypeForString("FEATURE_WIND_SE")
    feat_wind_sw = gc.getInfoTypeForString("FEATURE_WIND_SW")
    iWindplots = 6 # amount of wind arrows (plots) per wind
    OceanPlots = []
    lDirection = []

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    # get all ocean plots
    for i in range (iMapW):
      for j in range (iMapH):
        loopPlot = gc.getMap().plot(i, j)
        if loopPlot != None and not loopPlot.isNone():
          if loopPlot.getFeatureType() == iDarkIce: continue
          if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean: OceanPlots.append(loopPlot)

    if len(OceanPlots) > 0:
#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE

##entweder groessenabhaengig, oder genau 1
     iMaxEffects = (gc.getMap().getWorldSize() + 1) * 2

     #iMaxEffects = 1

     for i in range (iMaxEffects):

      # get first ocean plot
      iRand = self.myRandom(len(OceanPlots), None)
      iX = OceanPlots[iRand].getX()
      iY = OceanPlots[iRand].getY()

      # First direction
      iDirection = self.myRandom(8, None)
      bFirst = True

      # Start Windplots
      for j in range (iWindplots):

        loopPlot = gc.getMap().plot(iX, iY)
        if loopPlot != None and not loopPlot.isNone():
         if loopPlot.getFeatureType() == iDarkIce: continue
         if iX > 0 and iX < iMapW and iY > 0 and iY < iMapH:
          if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:

            if bFirst:
              if iDirection == 0:   loopPlot.setFeatureType(feat_wind_n,0)
              elif iDirection == 1: loopPlot.setFeatureType(feat_wind_ne,0)
              elif iDirection == 2: loopPlot.setFeatureType(feat_wind_e,0)
              elif iDirection == 3: loopPlot.setFeatureType(feat_wind_se,0)
              elif iDirection == 4: loopPlot.setFeatureType(feat_wind_s,0)
              elif iDirection == 5: loopPlot.setFeatureType(feat_wind_sw,0)
              elif iDirection == 6: loopPlot.setFeatureType(feat_wind_w,0)
              elif iDirection == 7: loopPlot.setFeatureType(feat_wind_nw,0)
              bFirst = False
            else:
              iRand = self.myRandom(3, None)
              if lDirection[iRand] == feat_wind_n:
                loopPlot.setFeatureType(feat_wind_n,0)
                iDirection = 0
              elif lDirection[iRand] == feat_wind_ne:
                loopPlot.setFeatureType(feat_wind_ne,0)
                iDirection = 1
              elif lDirection[iRand] == feat_wind_e:
                loopPlot.setFeatureType(feat_wind_e,0)
                iDirection = 2
              elif lDirection[iRand] == feat_wind_se:
                loopPlot.setFeatureType(feat_wind_se,0)
                iDirection = 3
              elif lDirection[iRand] == feat_wind_s:
                loopPlot.setFeatureType(feat_wind_s,0)
                iDirection = 4
              elif lDirection[iRand] == feat_wind_sw:
                loopPlot.setFeatureType(feat_wind_sw,0)
                iDirection = 5
              elif lDirection[iRand] == feat_wind_w:
                loopPlot.setFeatureType(feat_wind_w,0)
                iDirection = 6
              elif lDirection[iRand] == feat_wind_nw:
                loopPlot.setFeatureType(feat_wind_nw,0)
                iDirection = 7

            # set next possible directions
            if iDirection == 0:
              lDirection = [feat_wind_nw,feat_wind_n,feat_wind_ne]
              iY -= 1
            elif iDirection == 1:
              lDirection = [feat_wind_n,feat_wind_ne,feat_wind_e]
              iX -= 1
              iY -= 1
            elif iDirection == 2:
              lDirection = [feat_wind_ne,feat_wind_e,feat_wind_se]
              iX -= 1
            elif iDirection == 3:
              lDirection = [feat_wind_e,feat_wind_se,feat_wind_s]
              iX -= 1
              iY += 1
            elif iDirection == 4:
              lDirection = [feat_wind_sw,feat_wind_s,feat_wind_se]
              iY += 1
            elif iDirection == 5:
              lDirection = [feat_wind_w,feat_wind_sw,feat_wind_s]
              iX += 1
              iY += 1
            elif iDirection == 6:
              lDirection = [feat_wind_nw,feat_wind_w,feat_wind_sw]
              iX += 1
            elif iDirection == 7:
              lDirection = [feat_wind_w,feat_wind_nw,feat_wind_n]
              iX += 1
              iY -= 1




# ++++++++++++++++++++++++++++++++ Ranged Strike ++++++++++++++++++++++++++++++++++++++++++++++++++++
  def doRangedStrike(self, pCity, pCityUnit, pPlot, bCityDefense):
    pPlayer = gc.getPlayer(pCityUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Player",pCityUnit.getOwner())), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("X",pPlot.getX())), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Y",pPlot.getY())), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # BTS: funkt nicht, wohl nur bei AIR Units (in dll)?!
    # ich probiers noch einmal und geb dem ne weitere Chance
    pSelectionGroup = pCityUnit.getGroup() # MISSION_BOMBARD
    pSelectionGroup.pushMission (MissionTypes.MISSION_RANGE_ATTACK,0,0,0,False,False,MissionAITypes.NO_MISSIONAI,pPlot,pCityUnit)

    """
    CyEngine().triggerEffect( gc.getInfoTypeForString("EFFECT_CANNON_HIT_SMALL01"), pPlot.getPoint() )

    maxCollateralUnits = pCityUnit.airCombatLimit()
    UnitsStriked = 0
    iRange = pPlot.getNumUnits()
    for i in range (iRange):
      iOwner = pPlot.getUnit(i).getOwner()
      if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(iOwner).getTeam()):

        # Normaler Schaden (betrifft erste Einheit)
        # 1+ weil sein kann, dass airCombatLimit = 0 ist
        if UnitsStriked < 1+maxCollateralUnits:
            # Berechnung Air Strike Damage

            # Erste Einheit
            if i == 0:
              if gc.getPlayer(iOwner).isHuman():
                if bCityDefense:
                  CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RANGED_STRIKE",(pCity.getName(),0)), None, 2, pCityUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                else:
                  CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RANGED_STRIKE_2",(pCity.getName(),0)), None, 2, pCityUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

              if pPlot.getUnit(i) != None and pCityUnit != None:
                iDamagePercent = pCityUnit.airCombatDamage(pPlot.getUnit(i)) + self.myRandom(5, None)

            # Collateral
            else:
              if pPlot.getUnit(i) != None:
                iDamagePercent = pCityUnit.airCombatDamage(pPlot.getUnit(i)) / 2

            iCollateralProtectionPercent = pPlot.getUnit(i).getCollateralDamageProtection()
            iDamagePercent = iDamagePercent * (100 - iCollateralProtectionPercent)/100
            iUnitDamage = 100 - pPlot.getUnit(i).getDamage()
            iUnitDamage = iUnitDamage * (100 - iDamagePercent)/100
            iUnitDamage = max(iUnitDamage, pCityUnit.airCombatLimit())
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iDamage",iUnitDamage)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            pPlot.getUnit(i).setDamage(100-iUnitDamage, pPlot.getUnit(i).getOwner())
            UnitsStriked += 1
        else:
            break

    pCityUnit.changeMoves(-60)
    pCityUnit.finishMoves()
    """

# ++++++++++++++++++ Historische Texte ++++++++++++++++++++++++++++++++++++++++++++++

  def doHistory(self, iGameTurn):
    # iGameTurn brauchma im Moment nicht
    iGameYear = gc.getGame().getGameTurnYear()
    txts = 0

    if iGameYear == -3480: txts = 4
    elif iGameYear == -3000: txts = 5
    elif iGameYear == -2680: txts = 4
    elif iGameYear == -2000: txts = 6
    elif iGameYear == -1680: txts = 5
    elif iGameYear == -1480: txts = 7
    elif iGameYear == -1280: txts = 5
    elif iGameYear == -1200: txts = 6
    elif iGameYear == -1000: txts = 5
    elif iGameYear == -800: txts = 6
    elif iGameYear == -750: txts = 3
    elif iGameYear == -700: txts = 6
    elif iGameYear == -615: txts = 5
    elif iGameYear == -580: txts = 5
    elif iGameYear == -540: txts = 4
    elif iGameYear == -510: txts = 5
    elif iGameYear == -490: txts = 5
    elif iGameYear == -450: txts = 4
    elif iGameYear == -400: txts = 5
    elif iGameYear == -350: txts = 7
    elif iGameYear == -330: txts = 4
    elif iGameYear == -260: txts = 3
    elif iGameYear == -230: txts = 5
    elif iGameYear == -215: txts = 4
    elif iGameYear == -200: txts = 4
    elif iGameYear == -150: txts = 5
    elif iGameYear == -120: txts = 2
    elif iGameYear == -100: txts = 2
    elif iGameYear == -70: txts = 3
    elif iGameYear == -50: txts = 2
    elif iGameYear == -30: txts = 2
    elif iGameYear == -20: txts = 2
    elif iGameYear == -10: txts = 3
    elif iGameYear == 10: txts = 3
    elif iGameYear == 60: txts = 4
    elif iGameYear == 90: txts = 3
    elif iGameYear == 130: txts = 3
    elif iGameYear == 210: txts = 3
    elif iGameYear == 250: txts = 2
    elif iGameYear == 280: txts = 2
    elif iGameYear == 370: txts = 2
    elif iGameYear == 400: txts = 2
    elif iGameYear == 440: txts = 3

    if txts > 0:
     iRand = self.myRandom(txts, None)

     # iRand 0 bedeutet keinen Text anzeigen. Bei mehr als 2 Texte immer einen einblenden
     if txts > 2: iRand += 1

     if iRand > 0:
       text = "TXT_KEY_HISTORY_"
       if iGameYear < 0:
         text = text + str(iGameYear * (-1)) + "BC_" + str(iRand)
       else:
         text = text + str(iGameYear) + "AD_" + str(iRand)

       text = CyTranslator().getText("TXT_KEY_HISTORY",("",)) + " " + CyTranslator().getText(text,("",))
       CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 15, text, None, 2, None, ColorTypes(14), 0, 0, False, False)

# Next Unit after NetMessage
  def doGoToNextUnit(self, pPlayer, pUnit):
    # go to and select next Unit

    #pUnit.getGroup().setActivityType(ActivityTypes.ACTIVITY_HOLD)

    #(unit, iter) = pPlayer.firstUnit(false)
    #(unit, iter) = pPlayer.nextUnit(iter, false)

    pPlot = gc.getMap().plot(pUnit.getX(),pUnit.getY())
    pUnit.getGroup().pushMission (MissionTypes.MISSION_SKIP,0,0,0,False,False,MissionAITypes.NO_MISSIONAI,pPlot,pUnit)

# AI Torture Mercenary Commission (cheaper for AI)
  def doAIMercTorture(self, iPlayer, iMercenaryCiv):
      pPlayer = gc.getPlayer(iPlayer)
      iGold = pPlayer.getGold()

      if iGold >= 550:
        if 1 == self.myRandom(2, None):
          pPlayer.changeGold(-50)
          pPlayer.AI_changeAttitudeExtra(iMercenaryCiv,-2)
          self.doAIPlanAssignMercenaries(iMercenaryCiv)
          # nochmal, wenn AI in Geld schwimmt
          if pPlayer.getGold() >= 500: self.doAIPlanAssignMercenaries(iMercenaryCiv)
      elif iGold >= 350:
        if 1 == self.myRandom(2, None):
          pPlayer.changeGold(-50)
          pPlayer.AI_changeAttitudeExtra(iMercenaryCiv,-2)
          self.doAIPlanAssignMercenaries(iMercenaryCiv)

# AI Mercenary Commissions
  def doAIPlanAssignMercenaries(self, iPlayer):
      pPlayer = gc.getPlayer(iPlayer)
      iFaktor = 0
      iCost = 0
      iSize = 0

      # Check neighbours
      # ATTITUDE_FRIENDLY
      # ATTITUDE_PLEASED
      # ATTITUDE_CAUTIOUS
      # ATTITUDE_ANNOYED
      # ATTITUDE_FURIOUS
      Neighbors = []
      iRangeMaxPlayers = gc.getMAX_PLAYERS()
      for iAllPlayer in range (iRangeMaxPlayers):
         ThisPlayer = gc.getPlayer(iAllPlayer)
         if iAllPlayer != gc.getBARBARIAN_PLAYER() and iAllPlayer != iPlayer:
           if ThisPlayer.isAlive():
             if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
               Att = pPlayer.AI_getAttitude(iAllPlayer)
               if Att == AttitudeTypes.ATTITUDE_ANNOYED or Att == AttitudeTypes.ATTITUDE_FURIOUS:

                 # Check: Coastal cities for naval mercenary units
                 iAttackAtSea = 0
                 iCoastalCities = 0
                 iLandCities = 0
                 iNumCities = ThisPlayer.getNumCities()
                 for i in range (iNumCities):
                   if ThisPlayer.getCity(i).isCoastal(6): iCoastalCities += 1
                   else: iLandCities += 1

                 if iCoastalCities > 0:
                   if iCoastalCities >= iLandCities:
                     if 1 == self.myRandom(2, None): iAttackAtSea = 1
                   else:
                     iChance = iNumCities - iCoastalCities
                     if 0 == self.myRandom(iChance, None): iAttackAtSea = 1

                 Neighbors.append((iAllPlayer,iAttackAtSea))

      # iFaktor: 1111 - 4434
      # ---- inter/national
      # urban 200+    iFaktor: +1
      # own 300+      iFaktor: +2
      #internat 400+  iFaktor: +3
      #elite 500+     iFaktor: +4

      # ---- size
      #small +0      iFaktor: +10
      #medium +150   iFaktor: +20
      #big +300      iFaktor: +30
      #huge +400     iFaktor: +40

      # ---- type
      #defense      iFaktor: +100
      #ranged       iFaktor: +200
      #offense      iFaktor: +300
      #city         iFaktor: +400
      #naval        iFaktor: +500

      # ---- siege
      #0           iFaktor: +1000
      #2 +50       iFaktor: +2000
      #4 +90       iFaktor: +3000
      #6 +120      iFaktor: +4000

      if len(Neighbors) > 0:
        iRand = self.myRandom(len(Neighbors), None)
        iTargetPlayer = Neighbors[iRand][0]
        iTargetAtSea = Neighbors[iRand][1]
        iGold = pPlayer.getGold()

        # inter/national
        if pPlayer.getTechScore() > gc.getPlayer(iTargetPlayer).getTechScore():
          if iGold > 1000:
            if 1 == self.myRandom(3, None):
              iFaktor += 3
              iCost += 400
            else:
              iFaktor += 2
              iCost += 300
          elif iGold > 500:
            iFaktor += 2
            iCost += 300
          else:
            iFaktor += 1
            iCost += 200
        else:
          if iGold > 1000:
            if 1 == self.myRandom(3, None):
              iFaktor += 3
              iCost += 400
            else:
              iFaktor += 1
              iCost += 200
          else:
            iFaktor += 1
            iCost += 200

        # size
        if pPlayer.getPower() > gc.getPlayer(iTargetPlayer).getPower():
          if iGold > iCost + 150:
            if 1 == self.myRandom(3, None):
              iFaktor += 10
              iSize = 1
            else:
              iFaktor += 20
              iCost += 150
              iSize = 2
          else:
            iFaktor += 10
            iSize = 1
        else:
          if iGold > iCost + 150:
            if 1 != self.myRandom(3, None):
              iFaktor += 10
              iSize = 1
            else:
              iFaktor += 20
              iCost += 150
              iSize = 2
          else:
            iFaktor += 10
            iSize = 1

        # type
        if iTargetAtSea == 1: iType = 5
        else: iType = 1 + self.myRandom(4, None)
        iFaktor += iType * 100

        # siege units
        if iType == 4:
          if iSize == 1: iFaktor += 1000
          else:
            if pPlayer.getPower() > gc.getPlayer(iTargetPlayer).getPower():
              if iGold > iCost + 50: iFaktor += 2000
              else: iFaktor += 1000
            else:
              if iGold > iCost + 90: iFaktor += 3000
              elif iGold > iCost + 50: iFaktor += 2000
              else: iFaktor += 1000
        else: iFaktor += 1000

        if iTargetPlayer != -1:
          self.doComissionMercenaries(iTargetPlayer, iFaktor, iPlayer)


# Commission Mercenaries
  def doComissionMercenaries(self, iTargetPlayer, iFaktor, iPlayer):
       #  iTargetPlayer, iFaktor, iPlayer
       # iFaktor: 1111 - 4534
       # Naval attack: sFaktor[1] = 5
       pPlayer = gc.getPlayer(iPlayer)
       sFaktor = str(iFaktor)
       iCost = 0
       iSize = 0


       # siege units
       iSiegeUnitAnz = 0
       if sFaktor[0]   == "2": iCost +=  50
       elif sFaktor[0] == "3": iCost +=  90
       elif sFaktor[0] == "4": iCost += 120

       # size
       if sFaktor[2]   == "2": iCost += 150
       elif sFaktor[2] == "3": iCost += 300
       elif sFaktor[2] == "4": iCost += 400

       # inter/national/elite units
       if sFaktor[3]   == "1": iCost += 200
       elif sFaktor[3] == "2": iCost += 300
       elif sFaktor[3] == "3": iCost += 400
       elif sFaktor[3] == "4": iCost += 500
       # ----------

       if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM")):
         iCost -= iCost/4

       if pPlayer.getGold() < iCost:
         if gc.getPlayer(iPlayer).isHuman():
           CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           popupInfo = CyPopupInfo()
           popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
           popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
           popupInfo.addPopup(iPlayer)
       else:
         pPlayer.changeGold(-iCost)
         gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)

         # Siege Units
         iAnzSiege = 0
         iUnitSiege = -1
         if sFaktor[0] == "2":   iAnzSiege = 2
         elif sFaktor[0] == "3": iAnzSiege = 4
         elif sFaktor[0] == "4": iAnzSiege = 6

         if iAnzSiege > 0:
           if gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_MECHANIK")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_BATTERING_RAM2")
           elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_WEHRTECHNIK")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_BATTERING_RAM")
           elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_BELAGERUNG")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_RAM")
         # --------

         #  Techs for inter/national units
         Neighbors = []
         # on-site
         if sFaktor[3] == "1": Neighbors.append(gc.getPlayer(iTargetPlayer))
         # national (own)
         elif sFaktor[3] == "2": Neighbors.append(pPlayer)
         # international or elite
         elif sFaktor[3] == "3" or sFaktor[3] == "4":
           iRangeMaxPlayers = gc.getMAX_PLAYERS()
           for iAllPlayer in range (iRangeMaxPlayers):
             ThisPlayer = gc.getPlayer(iAllPlayer)
             # Nachbarn inkludieren
             if ThisPlayer.isAlive():
               if gc.getTeam(ThisPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
                 Neighbors.append(ThisPlayer)
         # ------------------

         # Unit initials
         # size and types
         iAnzSpear = 0
         iAnzAxe = 0
         iAnzSword = 0
         iAnzArcher = 0
         iAnzSlinger = 0
         iAnzShip1 = 0
         iAnzShip2 = 0
         if sFaktor[2] == "1":
           if sFaktor[1] == "1":
             iAnzSpear = 2
             iAnzAxe = 1
             iAnzSword = 0
             iAnzArcher = 1
             iAnzSlinger = 0
           elif sFaktor[1] == "2":
             iAnzSpear = 1
             iAnzAxe = 1
             iAnzSword = 0
             iAnzArcher = 2
             iAnzSlinger = 0
           elif sFaktor[1] == "3":
             iAnzSpear = 1
             iAnzAxe = 2
             iAnzSword = 0
             iAnzArcher = 1
             iAnzSlinger = 0
           elif sFaktor[1] == "4":
             iAnzSpear = 0
             iAnzAxe = 0
             iAnzSword = 2
             iAnzArcher = 2
             iAnzSlinger = 0
           elif sFaktor[1] == "5":
             iAnzShip1 = 1 # weak
             iAnzShip2 = 1 # strong

         elif sFaktor[2] == "2":
           if sFaktor[1] == "1":
             iAnzSpear = 3
             iAnzAxe = 2
             iAnzSword = 0
             iAnzArcher = 3
             iAnzSlinger = 0
           elif sFaktor[1] == "2":
             iAnzSpear = 1
             iAnzAxe = 2
             iAnzSword = 0
             iAnzArcher = 4
             iAnzSlinger = 1
           elif sFaktor[1] == "3":
             iAnzSpear = 2
             iAnzAxe = 4
             iAnzSword = 0
             iAnzArcher = 2
             iAnzSlinger = 0
           elif sFaktor[1] == "4":
             iAnzSpear = 1
             iAnzAxe = 1
             iAnzSword = 2
             iAnzArcher = 3
             iAnzSlinger = 1
           elif sFaktor[1] == "5":
             iAnzShip1 = 2
             iAnzShip2 = 2

         elif sFaktor[2] == "3":
           if sFaktor[1] == "1":
             iAnzSpear = 4
             iAnzAxe = 3
             iAnzSword = 0
             iAnzArcher = 4
             iAnzSlinger = 1
           elif sFaktor[1] == "2":
             iAnzSpear = 2
             iAnzAxe = 2
             iAnzSword = 0
             iAnzArcher = 5
             iAnzSlinger = 3
           elif sFaktor[1] == "3":
             iAnzSpear = 2
             iAnzAxe = 5
             iAnzSword = 0
             iAnzArcher = 2
             iAnzSlinger = 3
           elif sFaktor[1] == "4":
             iAnzSpear = 2
             iAnzAxe = 1
             iAnzSword = 4
             iAnzArcher = 3
             iAnzSlinger = 2
           elif sFaktor[1] == "5":
             iAnzShip1 = 3
             iAnzShip2 = 2

         elif sFaktor[2] == "4":
           if sFaktor[1] == "1":
             iAnzSpear = 5
             iAnzAxe = 5
             iAnzSword = 0
             iAnzArcher = 5
             iAnzSlinger = 1
           elif sFaktor[1] == "2":
             iAnzSpear = 3
             iAnzAxe = 3
             iAnzSword = 0
             iAnzArcher = 7
             iAnzSlinger = 3
           elif sFaktor[1] == "3":
             iAnzSpear = 3
             iAnzAxe = 7
             iAnzSword = 0
             iAnzArcher = 4
             iAnzSlinger = 2
           elif sFaktor[1] == "4":
             iAnzSpear = 2
             iAnzAxe = 2
             iAnzSword = 6
             iAnzArcher = 4
             iAnzSlinger = 2
           elif sFaktor[1] == "5":
             iAnzShip1 = 3
             iAnzShip2 = 3

         if pPlayer.getCurrentEra() > 2:
           iAnzSword += iAnzAxe
           iAnzAxe = 0
         # ----------

         # Set units

         # Elite
         lEliteUnits = []

         # UNIT_LIGHT_SPEARMAN: TECH_SPEERSPITZEN
         # UNIT_AXEWARRIOR: TECH_BEWAFFNUNG
         # UNIT_AXEMAN: TECH_BEWAFFNUNG2 + Bronze or Iron
         # UNITCLASS_KURZSCHWERT: TECH_BEWAFFNUNG3 + Bronze or Iron
         # UNIT_SPEARMAN: TECH_ARMOR + Bronze or Iron
         # UNIT_SCHILDTRAEGER: TECH_BEWAFFNUNG4 + Bronze or Iron
         # UNIT_SWORDSMAN: TECH_BEWAFFNUNG5 + Iron

         iUnitSpear   =  gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN")
         iUnitAxe     =  gc.getInfoTypeForString("UNIT_AXEWARRIOR")
         iUnitArcher  = gc.getInfoTypeForString("UNIT_ARCHER")
         iUnitSlinger = gc.getInfoTypeForString("UNIT_PELTIST")
         iUnitSword   = -1
         bLongsword = False

         iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
         iBonus2 = gc.getInfoTypeForString("BONUS_IRON")
         for Neighbor in Neighbors:

           # elite units
           if sFaktor[3] == "4":
             lNeighborUnits = []
             NeighborCapital = Neighbor.getCapitalCity()

             # Naval units
             if sFaktor[1] == "5":
               lNeighborUnits.append ( gc.getInfoTypeForString("UNIT_CARVEL_WAR") )
               lNeighborUnits.append ( gc.getInfoTypeForString("UNIT_QUINQUEREME") )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KONTERE")) ) # Gaulos
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL2")) ) # Quadrireme
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE1")) ) # Decareme

             # Land units
             else:
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL1")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL2")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL3")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL4")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL5")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE1")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE2")) )
               lNeighborUnits.append ( gc.getCivilizationInfo(Neighbor.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE3")) )
               lNeighborUnits.append ( gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER") )
               lNeighborUnits.append ( gc.getInfoTypeForString("UNIT_SWORDSMAN") )

             for iUnitElite in lNeighborUnits:
               if iUnitElite != None and iUnitElite != -1:
                 # Naval units
                 if sFaktor[1] == "5" and gc.getUnitInfo(iUnitElite).getDomainType() == DomainTypes.DOMAIN_SEA:
                     if NeighborCapital.canTrain(iUnitElite,0,0):
                       lEliteUnits.append(iUnitElite)
                 # Land units
                 elif gc.getUnitInfo(iUnitElite).getDomainType() != DomainTypes.DOMAIN_SEA:
                     if NeighborCapital.canTrain(iUnitElite,0,0):
                       lEliteUnits.append(iUnitElite)

           # normal units
           # else: Falls es keine Elite gibt, sollen normale Einheiten einspringen

           # Naval units
           if sFaktor[1] == "5":

               # UNIT_KONTERE: TECH_COLONIZATION2
               # UNIT_BIREME:  TECH_RUDERER2
               # UNIT_TRIREME: TECH_RUDERER3
               # UNIT_LIBURNE: TECH_WARSHIPS2
               # iAnzShip1 = weak
               # iAnzShip2 = strong
               iShip1 = -1
               iShip2 = -1
               if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WARSHIPS2")):
                  iShip1 = gc.getInfoTypeForString("UNIT_TRIREME")
                  iShip2 = gc.getInfoTypeForString("UNIT_LIBURNE")
               elif gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_RUDERER3")):
                  iShip1 = gc.getInfoTypeForString("UNIT_BIREME")
                  iShip2 = gc.getInfoTypeForString("UNIT_TRIREME")
               elif gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_RUDERER2")):
                  iShip1 = gc.getInfoTypeForString("UNIT_KONTERE")
                  iShip2 = gc.getInfoTypeForString("UNIT_BIREME")
               elif gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_COLONIZATION2")):
                  iShip1 = gc.getInfoTypeForString("UNIT_KONTERE")
                  iShip2 = gc.getInfoTypeForString("UNIT_KONTERE")

           # Land units
           # PAE V Patch 3: nun auch fuer Besatzung der Schiffe
           #else:
           #if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY3")): iUnitArcher = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
           if Neighbor.hasBonus(iBonus1) or Neighbor.hasBonus(iBonus2):
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARMOR")): iUnitSpear = gc.getInfoTypeForString("UNIT_SPEARMAN")
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): iUnitAxe = gc.getInfoTypeForString("UNIT_AXEMAN2")
                 elif gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")): iUnitAxe = gc.getInfoTypeForString("UNIT_AXEMAN")
                 if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")): iUnitSword = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
                 if iUnitSword == -1:
                   if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG3")): iUnitSword = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT"))
           if not bLongsword:
                 if Neighbor.hasBonus(iBonus2):
                   if gc.getTeam(Neighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG5")): bLongsword = True

         # for neighbors

         # wenns schon langschwert gibt
         if bLongsword: iUnitSword = gc.getInfoTypeForString("UNIT_SWORDSMAN")

         # wenns noch keine Schwerter gibt
         if iUnitSword == -1:
           iAnzAxe += iAnzSword
           iAnzSword = 0

         # Choose plots
         # Initialise CIV cultural plots
         iMapW = gc.getMap().getGridWidth()
         iMapH = gc.getMap().getGridHeight()
         iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

         CivPlots = []
         for x in range(iMapW):
           for y in range(iMapH):
             loopPlot = gc.getMap().plot(x,y)
             if loopPlot != None and not loopPlot.isNone():
               if loopPlot.getFeatureType() == iDarkIce: continue
               if loopPlot.getOwner() == iTargetPlayer:
                 if not loopPlot.isPeak() and not loopPlot.isCity() and loopPlot.getNumUnits() == 0:

                   # Naval units
                   if sFaktor[1] == "5":
                     # Nicht auf Seen
                     if loopPlot.isWater() and not loopPlot.isLake():
                       CivPlots.append(loopPlot)

                   # Land units
                   elif not loopPlot.isWater():

                     # Nicht auf Inseln
                     iLandPlots = 0
                     for x2 in range(3):
                       for y2 in range(3):
                         loopPlot2 = gc.getMap().plot(x-1+x2,y-1+y2)
                         if loopPlot2 != None and not loopPlot2.isNone():
                           if not loopPlot2.isWater(): iLandPlots += 1

                         # earlier break
                         if x2 == 1 and y2 > 0 and iLandPlots <= 1:
                           break

                       # earlier breaks
                       if iLandPlots >= 5:
                         CivPlots.append(loopPlot)
                         break
                       elif x2 == 2 and iLandPlots <= 2:
                         break

         # Big stacks and elite only on border plots
         if sFaktor[2] == "4" or sFaktor[3] == "4":
           if len(CivPlots) > 0:
             NewCivPlots = []
             x2=0
             y2=0
             for loopPlot in CivPlots:
               bDone = false
               for x2 in range(3):
                 if bDone: break
                 for y2 in range(3):
                   loopPlot2 = gc.getMap().plot(loopPlot.getX()-1+x2,loopPlot.getY()-1+y2)
                   if loopPlot2 == None or loopPlot2.isNone() or loopPlot2.getOwner() != loopPlot.getOwner():
                       NewCivPlots.append(loopPlot)
                       bDone = true
                       break

             if len(NewCivPlots) > 0:
               CivPlots = NewCivPlots

         # set units
         if len(CivPlots) > 0:
           iPlot = self.myRandom(len(CivPlots), None)
           iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
           # Loyality disabled for elite units
           iPromo2 = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
           iMinRanking = 0
           iMaxRanking = 4 # 4 = Veteran

           # instead of UnitAITypes.NO_UNITAI
           if sFaktor[1] == "4": UnitAI_Type = UnitAITypes.UNITAI_ATTACK_CITY
           else: UnitAI_Type = UnitAITypes.UNITAI_ATTACK

           # prevents CtD in MP
           #UnitAI_Type = UnitAITypes.NO_UNITAI

           ScriptUnit = []
           # set units
           # elite
           if sFaktor[3] == "4" and len(lEliteUnits) > 0:

             # Naval units
             if sFaktor[1] == "5":
               if sFaktor[2] == "1": iAnz = 2
               elif sFaktor[2] == "2": iAnz = 3
               elif sFaktor[2] == "3": iAnz = 4
               else: iAnz = 5
             # Land units
             else:
               if sFaktor[2] == "1": iAnz = 4
               elif sFaktor[2] == "2": iAnz = 8
               elif sFaktor[2] == "3": iAnz = 10
               else: iAnz = 12

             for i in range(iAnz):
                 iRand = self.myRandom (len(lEliteUnits), None)
                 NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lEliteUnits[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                 if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                 if NewUnit.isHasPromotion(iPromo2): NewUnit.setHasPromotion(iPromo2, False)
                 # Unit Rang / Unit ranking
                 self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                 NewUnit.setImmobileTimer(1)
                 ScriptUnit.append(NewUnit)
             # Goldkarren
             gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

           # standard units
           else:
            if iAnzSpear > 0:
              for i in range(iAnzSpear):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSpear, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)
                ScriptUnit.append(NewUnit)
            if iAnzAxe > 0:
              for i in range(iAnzAxe):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitAxe, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)
                ScriptUnit.append(NewUnit)
            if iAnzSword > 0 and iUnitSword != -1:
              for i in range(iAnzSword):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSword, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)
                ScriptUnit.append(NewUnit)
            if iAnzArcher > 0:
              for i in range(iAnzArcher):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitArcher, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)
            if iAnzSlinger > 0:
              for i in range(iAnzSlinger):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSlinger, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)
            if iAnzSiege > 0 and iUnitSiege != -1:
              for i in range(iAnzSiege):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSiege, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_CITY, DirectionTypes.DIRECTION_SOUTH)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)

            # Vessels / Naval units : get land unit
            if iAnzShip1 > 0 or iAnzShip2 > 0:
              lUnit = []
              lUnit.append(iUnitSpear)
              lUnit.append(iUnitAxe)
              if iUnitSword != -1: lUnit.append(iUnitSword)

            if iAnzShip1 > 0 and iShip1 != -1:
              for i in range(iAnzShip1):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iShip1, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)

                # Cargo
                iRand = self.myRandom(len(lUnit), None)
                NewLandUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lUnit[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                NewLandUnit.setTransportUnit(NewUnit)

            if iAnzShip2 > 0 and iShip2 != -1:
              for i in range(iAnzShip2):
                NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iShip2, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)
                if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
                # Unit Rang / Unit ranking
                self.doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
                NewUnit.setImmobileTimer(1)

                # Cargo
                iRand = self.myRandom(len(lUnit), None)
                NewLandUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lUnit[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
                NewLandUnit.setTransportUnit(NewUnit)

            # Goldkarren bei Landeinheiten
            if not CivPlots[iPlot].isWater():
              gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)


           # Plot anzeigen
           CivPlots[iPlot].setRevealed (gc.getPlayer(iPlayer).getTeam(),1,0,-1)

           # Eine Einheit bekommt iPlayer als Auftraggeber
           if len(ScriptUnit) > 0:
              iRand = self.myRandom(len(ScriptUnit), None)
              ScriptUnit[iRand].setScriptData("MercFromCIV=" + str(iPlayer))

           # Meldungen
           if gc.getPlayer(iPlayer).isHuman():
             CyCamera().JustLookAtPlot(CivPlots[iPlot])
             if CivPlots[iPlot].isWater(): szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_3",(gc.getPlayer(iTargetPlayer).getCivilizationDescription(0),))
             else: szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_1",(gc.getPlayer(iTargetPlayer).getCivilizationDescription(0),))
             CyInterface().addMessage(iPlayer, True, 10, szText, None, 2, None, ColorTypes(8), 0, 0, False, False)
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
             popupInfo.setText(szText)
             popupInfo.addPopup(iPlayer)
           if gc.getPlayer(iTargetPlayer).isHuman():
             CyCamera().JustLookAtPlot(CivPlots[iPlot])
             if CivPlots[iPlot].isWater(): szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_4",("",))
             else: szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_2",("",))
             CyInterface().addMessage(iTargetPlayer, True, 15, szText, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), True, True)
             popupInfo = CyPopupInfo()
             popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
             popupInfo.setText(szText)
             popupInfo.addPopup(iTargetPlayer)

           # TEST
           #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Plots",len(CivPlots))), None, 2, None, ColorTypes(10), 0, 0, False, False)
           #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Plots",int(sFaktor[1]))), None, 2, None, ColorTypes(10), 0, 0, False, False)


  # Failed Mercenary Torture (from 716 and 717)
  def doFailedMercenaryTortureMessage(self, iPlayer):
      iRand = self.myRandom(8, None) + 1
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_FAILED_0",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_FAILED_" + str(iRand),("", )))
      popupInfo.addPopup(iPlayer)

  # Upgrade Veteran Unit to Elite Unit - Belobigung
      # CommandUpgrade geht nur, wenn
      # - die Einheit auch wirklich zu dieser Einheit laut XML upgegradet werden kann
      # - alle Vorraussetzungen fuer die neuen Einheit erfuellt sind
      # - im eigenen Territorium
      #pUnit.doCommand (CommandTypes.COMMAND_UPGRADE, gc.getInfoTypeForString("UNIT_TRIARII2"), 0)
  def doUpgradeVeteran( self, pUnit, iNewUnit):
    if pUnit != None:
      pUnitOwner = gc.getPlayer(pUnit.getOwner())

      iPromoCombat3 = gc.getInfoTypeForString("PROMOTION_COMBAT3")
      iPromoCombat4 = gc.getInfoTypeForString("PROMOTION_COMBAT4")
      iPromoCombat5 = gc.getInfoTypeForString("PROMOTION_COMBAT5")
      iPromoCombat6 = gc.getInfoTypeForString("PROMOTION_COMBAT6")

      NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

      forbiddenPromos = []
      if pUnit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH1"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH2"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH3"))
      else:
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"))

      if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4"))
        forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5"))

      iRange = gc.getNumPromotionInfos()
      for j in range(iRange):
        if j not in forbiddenPromos:
          if pUnit.isHasPromotion(j):
            NewUnit.setHasPromotion(j, True)

      # Einheit: Rang -2
      if NewUnit.isHasPromotion(iPromoCombat6):
        NewUnit.setHasPromotion(iPromoCombat6, False)
        NewUnit.setHasPromotion(iPromoCombat5, False)
      elif NewUnit.isHasPromotion(iPromoCombat5):
        NewUnit.setHasPromotion(iPromoCombat5, False)
        NewUnit.setHasPromotion(iPromoCombat4, False)
      elif NewUnit.isHasPromotion(iPromoCombat4):
        NewUnit.setHasPromotion(iPromoCombat4, False)
        NewUnit.setHasPromotion(iPromoCombat3, False)
      NewUnit.setExperience(pUnit.getExperience(), -1)
      NewUnit.setLevel(pUnit.getLevel())

      UnitName = pUnit.getName()
      #if UnitName != "" and UnitName != NewUnit.getName(): NewUnit.setName(UnitName)
      if UnitName != gc.getUnitInfo(pUnit.getUnitType()).getText():
        UnitName = re.sub(" \(.*?\)","",UnitName)
        NewUnit.setName(UnitName)

      # if unit was a general  (PROMOTION_LEADER)
      if pUnit.getLeaderUnitType() > -1:
        NewUnit.setLeaderUnitType(pUnit.getLeaderUnitType())
        pUnit.setLeaderUnitType(-1) # avoids ingame message "GG died in combat"


      NewUnit.setDamage(pUnit.getDamage(), -1)
      #NewUnit.changeMoves(100)
      NewUnit.setImmobileTimer(1)

      #pUnit.kill(1,pUnit.getOwner())
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

  # PAE City status --------------------------
  # Check City colony or province after events
  # once getting a province: keep being a province
  # Methode auch in CvWorldBuilderScreen.py - immer beide aendern
  def doCheckCityState(self, pCity):

    iBuildingSiedlung = gc.getInfoTypeForString("BUILDING_SIEDLUNG")
    iBuildingKolonie = gc.getInfoTypeForString("BUILDING_KOLONIE")
    iBuildingCity = gc.getInfoTypeForString("BUILDING_STADT")
    iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
    iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")
	    # PAE Debug mark
    #"""
#    if gc.getPlayer(pCity.getOwner()).isHuman():
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("X",iBuildingSiedlung)), None, 2, None, ColorTypes(10), 0, 0, False, False)
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Y",pPlot.getY())), None, 2, None, ColorTypes(10), 0, 0, False, False)

    if pCity.getNumRealBuilding(iBuildingSiedlung) == 0:
      pCity.setNumRealBuilding(iBuildingSiedlung,1)

    if pCity.getPopulation() > 2 and pCity.getNumRealBuilding(iBuildingKolonie) == 0:
      pCity.setNumRealBuilding(iBuildingKolonie,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_1",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingKolonie).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    if pCity.getPopulation() > 5 and pCity.getNumRealBuilding(iBuildingCity) == 0:
      pCity.setNumRealBuilding(iBuildingCity,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_2",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Wachstum: Meldungen von kleinerem Status beginnend
    if pCity.getPopulation() > 9 and pCity.getNumRealBuilding(iBuildingProvinz) == 0:
      pCity.setNumRealBuilding(iBuildingProvinz,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_3",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() > 17 and pCity.getNumRealBuilding(iBuildingMetropole) == 0:
      pCity.setNumRealBuilding(iBuildingMetropole,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_5",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingMetropole).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Bev.rueckgang: Meldungen von hoeheren Status beginnend
    if pCity.getPopulation() <= 17 and pCity.getNumRealBuilding(iBuildingMetropole) == 1:
      pCity.setNumRealBuilding(iBuildingMetropole,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_6",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() <= 9 and pCity.getNumRealBuilding(iBuildingProvinz) == 1:
      pCity.setNumRealBuilding(iBuildingProvinz,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_4",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # AI and its slaves
    if not gc.getPlayer(pCity.getOwner()).isHuman():
       self.doAIReleaseSlaves(pCity)

  # PAE UNIT FORMATIONS ------------------------------
  def canDoFormation (self, pUnit, iFormation):
      if not pUnit.canMove(): return False
      if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")): return False

      lMelee = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN")]
      lArcher = [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]

      iUnitType = pUnit.getUnitType()
      iUnitCombatType = pUnit.getUnitCombatType()
      pPlayer = gc.getPlayer(pUnit.getOwner())
      pTeam = gc.getTeam(pPlayer.getTeam())

      # Naval
      if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL") or iFormation == gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"):
          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_WORKBOAT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KILIKIEN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_BIREME"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"))
                      if iUnitType not in UnitArray: return True


      # Mounted mit Fernangriff
      elif iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):

        # Fourage
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"):
          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
                    UnitArray = []
                    UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
                    if iUnitType not in UnitArray: return True

        # Partherschuss oder Kantabrischer Kreis
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER") or iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
                UnitArray = []
                #UnitArray.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_BAKTRIEN"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                if iUnitType in UnitArray:
                  # Partherschuss
                  if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                      CivArray = []
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HETHIT"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PHON"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ISRAEL"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PERSIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BABYLON"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SUMERIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PARTHER"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HUNNEN"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_INDIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BARBARIAN"))
                      if pUnit.getCivilizationType() in CivArray:
                        return True
                  # Kantabrischer Kreis
                  elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                      return True

        # Keil (fuer schwere Kavallerie)
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_EQUITES"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2_RIDER"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))
                      if iUnitType in UnitArray:
                        return True


      # Melee and Spear
      elif iUnitCombatType in lMelee:

        # Fortress
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") and pUnit.baseMoves() == 1: return True
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") and pUnit.baseMoves() > 1: return True

        # Schildwall
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"):
          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_WARRIOR"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KURZSCHWERT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_AXEMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_GALLIER_GILDE"))
                      if iUnitType not in UnitArray:
                        return True


        # Drill: Manipel, Phalanx, ...
        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
          # Roman Legion (Kohorte)
          if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"):
            if iUnitType == gc.getInfoTypeForString("UNIT_LEGION") or iUnitType == gc.getInfoTypeForString("UNIT_LEGION2") or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2"):
              return True
          # Treffen-Taktik
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
              return True
          # Manipel
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
              return True
          # Phalanx-Arten (nur Speer)
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"):
            if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                return True
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"):
            if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                return True
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"):
            if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                return True
          # Geschlossene Formation (alle Melee)
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
              return True
          # Testudo
          elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                        UnitArray = []
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_GILDE"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN3"))
                        if iUnitType in UnitArray:
                          return True
        # -- Drill end

        # Keil
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
              return True
        # Zangenangriff
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
              return True
        # Flankenschutz (nur Speer)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"):
          if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
              return True
        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
              return True


      # Archers
      elif iUnitCombatType in lArcher:

        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
            return True


      # Flucht
      if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"):
        if pUnit.getDamage() >= 70:
                  UnitCombatArray = []
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_MELEE"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_ARCHER"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"))
                  if iUnitCombatType in UnitCombatArray:
                    if pUnit.baseMoves() == 1:
                      return True

      return False
  # can do Formationen / Formations End ------

  # PAE UNIT FORMATIONS ------------------------------
  def doUnitFormation (self, pUnit, iNewFormation):
    pPlayer = gc.getPlayer(pUnit.getOwner())

    FormationArray = []
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))    # TECH_CLOSED_FORM
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))        # TECH_PHALANX
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))       # TECH_PHALANX2
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))         # TECH_PHALANX2
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))        # TECH_MANIPEL
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))        # TECH_TREFFEN
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))        # TECH_MARIAN_REFORM
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))           # TECH_HUFEISEN
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))  # TECH_HORSEBACK_RIDING_2
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))  # TECH_TREFFEN
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))          # TECH_GEOMETRIE2
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))        # TECH_MARIAN_REFORM
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))        # TECH_BRANDSCHATZEN
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))     # TECH_LOGIK
    FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))    # TECH_LOGIK

    # Human
    if pPlayer.isHuman():
      # stehende Fortress-Einheiten sollen fuer die KI stehend bleiben
      FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"))
      FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"))

      # Fuer alle Einheiten dieser Gruppe
      pPlot = pUnit.plot()

      iNumUnits = pPlot.getNumUnits()
      for i in range (iNumUnits):
        loopUnit = pPlot.getUnit(i)
        if loopUnit.IsSelected():
          # Formation geben
          if iNewFormation != -1:
            if self.canDoFormation (loopUnit, iNewFormation):
              # Formationen auf NULL setzen
              for j in FormationArray:
                #if loopUnit.isHasPromotion(j):
                loopUnit.setHasPromotion(j, False)
              # Formation geben
              loopUnit.setHasPromotion(iNewFormation, True)
          # Formationen entfernen
          else:
            # Formationen auf NULL setzen
            for j in FormationArray:
              #if loopUnit.isHasPromotion(j):
              loopUnit.setHasPromotion(j, False)
    # AI
    else:
              # Formationen auf NULL setzen
              for j in FormationArray:
                #if loopUnit.isHasPromotion(j):
                pUnit.setHasPromotion(j, False)
              # Formation geben
              if iNewFormation != -1:
                pUnit.setHasPromotion(iNewFormation, True)

    # Unit den Fortify Modus erzwingen - hat keinen effekt?!
    #if iNewFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"):
    #  pPlot = gc.getMap().plot( pUnit.getX(), pUnit.getY() )
    #  #pUnit.getGroup().setActivityType (ActivityTypes.ACTIVITY_SLEEP)
    #  pUnit.getGroup().pushMission (MissionTypes.MISSION_FORTIFY,0,0,0,False,False,MissionAITypes.NO_MISSIONAI,pPlot,pUnit)


  def doAIPlotFormations (self, pPlot, iPlayer):
    bContinue = False
    bSupplyUnit = False
    bCity = False
    bElefant = False
    lPlayerUnits = []
    lMountedUnits = []
    iCountDamage = 0
    iStackStatus = 0
    # 0: > 75% stength: 80% offensive
    # 1: > 50% strength: 50% offensive
    # 2: > 25% strength: 10% offensive
    # 3: < 25% strength: flight

    # Naval or Land
    if pPlot.isWater():
      if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
        bContinue = True
    else:
      if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
        bContinue = True

    if bContinue:

      # City
      for x in range(3):
        for y in range(3):
          loopPlot = gc.getMap().plot(pPlot.getX() + x - 1, pPlot.getY() + y - 1)
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isCity():
              pCity = loopPlot.getPlotCity()
              if pCity.getOwner() != iPlayer:
                if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
                  bCity = True

      lUnitTypes = []
      #lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_MELEE"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_ARCHER"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"))
      lUnitTypes.append(gc.getInfoTypeForString("UNITCOMBAT_NAVAL"))

      # Init Units
      iRange = pPlot.getNumUnits()
      for i in range (iRange):
        if pPlot.getUnit(i).getOwner() == iPlayer:
          if pPlot.getUnit(i).getUnitCombatType() in lUnitTypes:
            lPlayerUnits.append(pPlot.getUnit(i))
            # Supply
            if not bSupplyUnit:
              if pPlot.getUnit(i).isHasPromotion(gc.getInfoTypeForString("PROMOTION_MEDIC2")):
                bSupplyUnit = True
            iCountDamage += pPlot.getUnit(i).getDamage()

      # StackStatus
      iCountUnits = len(lPlayerUnits)
      iLimit = 0
      if iCountUnits > 0:
        if iCountUnits * 100 - iCountDamage > iCountUnits * 75:
          iStackStatus = 0
          iLimit = iCountUnits / 10 * 8
        elif iCountUnits * 100 - iCountDamage > iCountUnits * 50:
          iStackStatus = 1
          iLimit = iCountUnits / 2
        elif iCountUnits * 100 - iCountDamage > iCountUnits * 25:
          iStackStatus = 2
          iLimit = iCountUnits / 10
        else: iStackStatus = 3

        if iStackStatus == 3:
          # deactivated
          i = 0
          for unit in lPlayerUnits:
            if unit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
              self.doUnitFormation(unit, gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"))
        else:
          i = 0
          for unit in lPlayerUnits:
            if not bSupplyUnit:
              if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                UnitArray = []
                UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
                if unit.getUnitType() not in UnitArray:
                  lMountedUnits.append(unit)
            if i <= iLimit: self.doAIUnitFormations (unit, True, bCity, bElefant)
            else: self.doAIUnitFormations (unit, False, bCity, bElefant)
            i += 1

          # Fourage - Supply
          if not bSupplyUnit:
           if len(lMountedUnits):
            iLevel = 10
            if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
              pUnit = lMountedUnits[0]
              for unit in lMountedUnits:
                if unit.getLevel() < iLevel:
                  pUnit = unit
                  iLevel = unit.getLevel()
              self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))


  def doAIUnitFormations (self, pUnit, bOffensive, bCity, bElefant):
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")): return
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")): return
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")): return
    if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL: return

    iUnitType = pUnit.getUnitType()
    pUnitOwner = gc.getPlayer(pUnit.getOwner())
    pTeam = gc.getTeam(pUnitOwner.getTeam())

    lMelee  = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN")]
    lArcher = [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]

    # Naval
    if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
        UnitArray = []
        UnitArray.append(gc.getInfoTypeForString("UNIT_KILIKIEN"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_BIREME"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"))
        if pUnit.getUnitType() not in UnitArray:
          # Keil oder Zange
          if bOffensive:
            self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))
          else:
            self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))


    # Wald, Schild, Zange, Phalanx, Keil
    #pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())

    # Formation im Wald
    #iFeatType1 = gc.getInfoTypeForString("FEATURE_FOREST")
    #iFeatType2 = gc.getInfoTypeForString("FEATURE_JUNGLE")
    #iFeatType3 = gc.getInfoTypeForString("FEATURE_DICHTERWALD")
    #if pPlot.getFeatureType() == iFeatType1 or pPlot.getFeatureType() == iFeatType2 or pPlot.getFeatureType() == iFeatType3:

    # Mounted
    elif pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                  UnitArray = []
                  #UnitArray.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_BAKTRIEN"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                  if iUnitType in UnitArray:
                    CivArray = []
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HETHIT"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PHON"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ISRAEL"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PERSIA"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BABYLON"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SUMERIA"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PARTHER"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HUNNEN"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_INDIA"))
                    CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BARBARIAN"))
                    if pUnit.getCivilizationType() in CivArray and pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                      self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
                      return
                    elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                      self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
                      return

                  if bOffensive:
                    # Keil (auch weiter unten fuer Melee)
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_EQUITES"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2_RIDER"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))
                      if pUnit.getUnitType() in UnitArray:
                        self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))
                        return

    # Melee and Spear
    elif pUnit.getUnitCombatType() in lMelee:

            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):

              # Testudo
              if bCity:
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_GILDE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN3"))
                      if pUnit.getUnitType() in UnitArray and self.myRandom(2, None) == 0:
                        self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))
                        return

              # Kohorte / Legion
              if iUnitType == gc.getInfoTypeForString("UNIT_LEGION") or iUnitType == gc.getInfoTypeForString("UNIT_LEGION2") or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2"):
                self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))
                return

            # Elefantengasse
            if bElefant:
                if self.myRandom(4, None) == 0:
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                    self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
                    return


            # Offensive
            if bOffensive:

                  if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):

                    # Treffen-Taktik ersetzt Manipel
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                        self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))
                        return

                    # Manipel ersetzt Phalanx, Manipular-Phalanx und Schiefe Phalanx
                    elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
                        self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))
                        return

                    # Phalanx-Arten und Geschlossene Formation
                    else:

                      # Phalanx nur Speer
                      if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):

                        # Manipular-Phalanx und Schiefe Phalanx ersetzt Phalanx
                        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):

                          # Schiefe Schlachtordnung
                          if self.myRandom(2, None) == 0:
                            self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))
                            return
                          # Manipular-Phalanx
                          else:
                            self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))
                            return

                        # Phalanx
                        elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                            self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))
                            return

                    # Geschlossene Formation (alle Melee mit Drill)
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
                      self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))
                      return

            # Defensive
            else:
                  # Flankenschutz (nur Speer)
                  if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                      self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))
                      return
                  # Zangenangriff (dem Keil vorziehen)
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
                    self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))
                    return

            # Restlichen Units, falls oben nix draus wurde
            # Schildwall
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
                  UnitArray = []
                  UnitArray.append(gc.getInfoTypeForString("UNIT_WARRIOR"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_KURZSCHWERT"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_AXEMAN"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"))
                  UnitArray.append(gc.getInfoTypeForString("UNIT_GALLIER_GILDE"))

                  if pUnit.getUnitType() not in UnitArray:
                    self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
                    return

    # Archer, vor allem Skirmisher
    elif bElefant and pUnit.getUnitCombatType() in lArcher:

            # Elefantengasse
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
              #if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
              self.doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))

  # PAE UNIT FORMATIONS END ------------------------------


  # PAE UNIT BATTLE PROMOTION
  def doUnitGetsPromo (self, pUnitTarget, pUnitSource, pPlot, bMadeAttack):
    # Unit promos --------------------
    # UNITCOMBAT_ARCHER: PROMOTION_COVER1
    # UNITCOMBAT_SKIRMISHER: PROMOTION_PARADE_SKIRM1
    # UNITCOMBAT_AXEMAN: PROMOTION_PARADE_AXE1
    # UNITCOMBAT_SWORDSMAN: PROMOTION_PARADE_SWORD1
    # UNITCOMBAT_SPEARMAN: PROMOTION_PARADE_SPEAR1

    # UNITCOMBAT_CHARIOT: PROMOTION_FORMATION1
    # UNITCOMBAT_MOUNTED: PROMOTION_FORMATION2
    # UNITCOMBAT_ELEPHANT: PROMOTION_FORMATION3
    # UNITCOMBAT_SIEGE: PROMOTION_CHARGE
    # Terrain promos -----------------
    # isHills: PROMOTION_GUERILLA1 - 5
    # FEATURE_FOREST, FEATURE_DICHTERWALD: PROMOTION_WOODSMAN1 - 5
    # FEATURE_JUNGLE: PROMOTION_JUNGLE1 - 5
    # FEATURE_SWAMP: PROMOTION_SUMPF1 - 5
    # TERRAIN_DESERT: PROMOTION_DESERT1 - 5
    # Extra promos -------------------
    # City Attack: PROMOTION_CITY_RAIDER1 - 5
    # City Defense: PROMOTION_CITY_GARRISON1 - 5
    # isRiverSide(): PROMOTION_AMPHIBIOUS

    # pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT")
    # pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST")
    # pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MELEE")

    iNewPromo = -1

    if pPlot.isCity(): bCity = True
    else: bCity = False

    lFirstPromos = []
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_WOODSMAN1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_GUERILLA1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_DESERT1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_JUNGLE1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_SUMPF1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"))

    iFirstPromos = 0
    for i in lFirstPromos:
      if pUnitTarget.isHasPromotion(i): iFirstPromos += 1

    iDivisor = 1
    # PAEInstanceFightingModifier for wins in the same turn
    if (pUnitTarget.getOwner(),pUnitTarget.getID()) in self.PAEInstanceFightingModifier: iDivisor = 5

    # Chances
    iChanceCityAttack = 20 / iDivisor
    iChanceCityDefense = 20 / iDivisor
    # Trait Conqueror / Eroberer: iChanceCityAttack*2
    if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")): iChanceCityAttack *= 2
    iChanceUnitType = 10 / iDivisor
    iChanceTerrain = 30 / (iFirstPromos*2 + 1) / iDivisor
    # Static chance of Promo 2-5 of a terrain
    iChanceTerrain2 = 5 / iDivisor


    # 1. chance: Either City or Open Field
    # City
    if bCity:
      iRand = self.myRandom(100, None)
      if bMadeAttack:
        # Attacker
        if iChanceCityAttack > iRand:
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")):
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
            iChanceUnitType = iChanceUnitType / 2
            # Trait Conquereror / Eroberer: Automatische Heilung bei Stadtangriffs-Promo / auto-healing when receiving city raider promo
            if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")): 
              pUnitTarget.setDamage(0, -1)
        # Defender
      else:
        if iChanceCityDefense > iRand:
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")):
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
            iChanceUnitType = iChanceUnitType / 2
            # Trait Protective: Automatische Heilung bei Stadtverteidigungs-Promo / auto-healing when receiving city garrison promo
            if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")): 
              pUnitTarget.setDamage(0, -1)

    # on open field
    else:
      iRandTerrain = self.myRandom(100, None)
      if iChanceTerrain > iRandTerrain:
        # either hill, terrain or feature, river

        # init unit promos and terrains
        lTerrain = []
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA5")) and pPlot.isHills():
          lTerrain.append("Hills")

        # thx to Dertuek:
        if bMadeAttack and pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")):
            pPlotAtt=pUnitTarget.plot()
            pPlotDef=pUnitSource.plot()
            if pPlotAtt.isWater() and not pPlotDef.isWater():
              lTerrain.append("River")
            elif pPlotAtt.isRiverSide():
              iDiffX=pPlotDef.getX()-pPlotAtt.getX()
              iDiffY=pPlotDef.getY()-pPlotAtt.getY()

              iDir = -1
              if iDiffX == 0 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTH
              elif iDiffX == 1 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTHEAST
              elif iDiffX == 1 and iDiffY == 0:
                iDir=DirectionTypes.DIRECTION_EAST
              elif iDiffX == 1 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTHEAST
              elif iDiffX == 0 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTH
              elif iDiffX == -1 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTHWEST
              elif iDiffX == -1 and iDiffY == 0:
                iDir=DirectionTypes.DIRECTION_WEST
              elif iDiffX == -1 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTHWEST

              if iDir > -1:
                if pPlotAtt.isRiverCrossing(iDir):
                  lTerrain.append("River")

        # old source code
        #if pPlot.isRiverSide() and bMadeAttack:
        #  if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")):
        #    if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
        #      lTerrain.append("River")

        if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"):
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT5")):
            lTerrain.append("Desert")

        # Forest, Jungle and Swamp nicht fuer Mounted
        if not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE") :
          if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST") or pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN5")):
              lTerrain.append("Forest")
          elif pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE5")):
              lTerrain.append("Jungle")
          elif pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_SWAMP"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF5")):
              lTerrain.append("Swamp")

        if len(lTerrain) > 0:
          iChanceUnitType = iChanceUnitType / 2
          iRand = self.myRandom(len(lTerrain), None)
          if lTerrain[iRand] == "River":
            iNewPromo = gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")
          elif lTerrain[iRand] == "Hills":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA1")
          elif lTerrain[iRand] == "Forest":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN1")
          elif lTerrain[iRand] == "Jungle":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE1")
          elif lTerrain[iRand] == "Swamp":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF1")
          elif lTerrain[iRand] == "Desert":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT1")

          # Chances of Promos 2-5
          if iNewPromo not in lFirstPromos and iRandTerrain >= iChanceTerrain2: iNewPromo = -1


    if iNewPromo > -1:

      # naechste Chance verringern
      iChanceUnitType = iChanceUnitType / 2

      pUnitTarget.setHasPromotion(iNewPromo, True)
      self.PAEInstanceFightingModifier.append((pUnitTarget.getOwner(),pUnitTarget.getID()))
      if gc.getPlayer(pUnitTarget.getOwner()).isHuman():
        CyInterface().addMessage(pUnitTarget.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION",(pUnitTarget.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)

    # 2. chance: enemy combat type
    iNewPromo = -1
    iRand = self.myRandom(100, None)
    if iChanceUnitType > iRand:

      if pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")

      #elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MELEE"):
      #  if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK2")):  iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK2")
      #  elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION1")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION2")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION3")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CHARGE")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_CHARGE")

      if iNewPromo > -1:
        pUnitTarget.setHasPromotion(iNewPromo, True)
        self.PAEInstanceFightingModifier.append((pUnitTarget.getOwner(),pUnitTarget.getID()))
        if gc.getPlayer(pUnitTarget.getOwner()).isHuman():
          CyInterface().addMessage(pUnitTarget.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION",(pUnitTarget.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)


    # isHills: PROMOTION_GUERILLA1
    # FEATURE_FOREST, FEATURE_DICHTERWALD: PROMOTION_WOODSMAN1
    # FEATURE_JUNGLE: PROMOTION_JUNGLE1
    # FEATURE_SWAMP: PROMOTION_SUMPF1
    # TERRAIN_DESERT: PROMOTION_DESERT1
    # City Attack: PROMOTION_CITY_RAIDER1
    # City Defense: PROMOTION_CITY_GARRISON1
    # isRiverSide: PROMOTION_AMPHIBIOUS

  # PAE CITY builds UNIT -> auto promotions (land units)
  def doCityUnitPromotions (self, pCity, pUnit):
    # check city radius (r): 1 plot = 3, 2 plots = 5
    r = 3
    initChanceCity = 1  # ab Stadt: Chance * City Pop
    initChance = 5      # Chance * Plots
    #initChanceRiver = 2 # for PROMOTION_AMPHIBIOUS only
    # --------------
    iCityAttack = 0
    iCityDefense = 0
    iHills = 0
    iForest = 0
    iJungle = 0
    iSwamp = 0
    iDesert = 0
    iRiver = 0
    if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")): bProvinz = true
    else: bProvinz = false
    iX = pCity.getX()
    iY = pCity.getY()

    # not for rams
    lRams = []
    lRams.append(gc.getInfoTypeForString("UNIT_RAM"))
    lRams.append(gc.getInfoTypeForString("UNIT_BATTERING_RAM"))
    lRams.append(gc.getInfoTypeForString("UNIT_BATTERING_RAM2"))
    if pUnit.getUnitType() in lRams: return

    # Start seeking plots for promos
    for x in range(r):
      for y in range(r):
          loopPlot = gc.getMap().plot(iX + x - ((r-1)/2), iY + y - ((r-1)/2))
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isCity() and bProvinz:
              lTypes = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN")]
              if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"): iCityDefense = 1
              elif pUnit.getUnitCombatType() in lTypes: iCityAttack = 1
            else:
              if loopPlot.isHills() or loopPlot.isPeak(): iHills += 1
              #if loopPlot.isRiverSide(): iRiver += 1
              if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"): iDesert += 1
              if loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"): iForest += 1
              elif loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"): iForest += 1
              elif loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_SWAMP"): iSwamp += 1
              elif loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"): iJungle += 1

    # City
    if iCityDefense > 0:
      iRand = self.myRandom(100, None)
      if pCity.getPopulation() * initChanceCity > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")): self.doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"),pCity)
    elif iCityAttack > 0:
      iRand = self.myRandom(100, None)
      if pCity.getPopulation() * initChanceCity > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")): self.doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"),pCity)

    # River - deactivated
    #if iRiver > 0:
    #  iRand = self.myRandom(100, None)
    #  if iRiver * initChanceRiver > iRand:
    #    if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")): self.doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS"),pCity)


    # PAE V Patch 7: nur 1 Terrain Promo soll vergeben werden
    lPossiblePromos = []

    # Hills
    if iHills > 0:
      iRand = self.myRandom(100, None)
      if iHills * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA1")): lPossiblePromos.append(gc.getInfoTypeForString("PROMOTION_GUERILLA1"))

    # Desert
    if iDesert > 0:
      iRand = self.myRandom(100, None)
      if iDesert * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT1")): lPossiblePromos.append(gc.getInfoTypeForString("PROMOTION_DESERT1"))

    # Forest
    if iForest > 0:
      iRand = self.myRandom(100, None)
      if iForest * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN1")): lPossiblePromos.append(gc.getInfoTypeForString("PROMOTION_WOODSMAN1"))

    # Swamp
    if iSwamp > 0:
      iRand = self.myRandom(100, None)
      if iSwamp * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF1")): lPossiblePromos.append(gc.getInfoTypeForString("PROMOTION_SUMPF1"))

    # Jungle
    if iJungle > 0:
      iRand = self.myRandom(100, None)
      if iJungle * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE1")): lPossiblePromos.append(gc.getInfoTypeForString("PROMOTION_JUNGLE1"))

    # only 1 of the pot
    if len(lPossiblePromos) > 0:
      iPromo = self.myRandom(len(lPossiblePromos), None)
      self.doGiveUnitPromo(pUnit,lPossiblePromos[iPromo],pCity)


  # PAE CITY builds UNIT -> auto promotions (ships)
  def doCityUnitPromotions4Ships (self, pCity, pUnit):
    # check city radius (1 plot = 3, 2 plots = 5), chance per water plot (ocean, coast, lake): 20%
    r = 3
    initChance = 2
    # --------------

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iWater = 0
    iX = pCity.getX()
    iY = pCity.getY()
    for x in range(r):
      for y in range(r):
          loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.getFeatureType() == iDarkIce: continue
            if loopPlot.isWater(): iWater += 1

    if iWater > 0:
      iRand = self.myRandom(10, None)
      if iWater * initChance > iRand:
        if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION1")): self.doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_NAVIGATION1"),pCity)


  def doGiveUnitPromo (self, pUnit, iNewPromo, pCity):
      pUnit.setHasPromotion(iNewPromo, True)
      if gc.getPlayer(pUnit.getOwner()).isHuman():
        if iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1") or iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"):
          CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_3",(pUnit.getName(),gc.getPromotionInfo(iNewPromo).getDescription(),pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
        else:
          CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_2",(pUnit.getName(),gc.getPromotionInfo(iNewPromo).getDescription(),pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
  # --------------------------------


  def doRetireVeteran (self, pUnit):
    lPromos = []
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT4"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT5"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT6"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG1"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG5"))
    #lPromos.append(gc.getInfoTypeForString("PROMOTION_HERO"))
    for iPromo in lPromos:
      if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)

    # Reduce XP
    pUnit.setExperience(pUnit.getExperience() / 2, -1)
    # Reduce Lvl: deactivated
    #if pUnit.getLevel() > 3:
    #  pUnit.setLevel(pUnit.getLevel() - 3)
    #else:
    #  pUnit.setLevel(1)


  # PAE V: Bonusverbreitung 726
  def doBonusCityGetPlot (self, pCity, iBonus):
    iPlayer = pCity.getOwner()

    # Check if bonus is available
    # pCity.hasBonus(iBonus)
    # pCity.getNumBonuses(iBonus)
    # pPlayer.getNumAvailableBonuses(iBonus)
    # pPlayer.countOwnedBonuses(iBonus) = alle (auch unverbundene Boni) im Einflussgebiet
    if not pCity.hasBonus(iBonus): return None,0

    # Standardchance
    iChance = 80
    # Stadtkoordinaten
    iX = pCity.getX()
    iY = pCity.getY()

    """
    # Kartengroesse
    iMapH = gc.getMap().getGridHeight()
    iMapW = gc.getMap().getGridWidth()

    # Richtwert fuer Breitengrad definieren
    iRichtwertBreitengrad = iMapH/2
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    if sScenarioScriptData != "":
      if sScenarioScriptData == "Hellas":   iRichtwertBreitengrad = iMapH
      elif sScenarioScriptData == "Orient": iRichtwertBreitengrad = iMapH

    # 1. Ausnahmen (iY)
    #if iBonus == gc.getInfoTypeForString("BONUS_RICE"):
    #  if iNumJungle == 0: return
    # Getreide
    if iBonus == gc.getInfoTypeForString("BONUS_WHEAT"):
      # Generell 100%, Sueden besser als Norden
      iChance = 100 - (iY * 100/iMapH)
    elif iBonus == gc.getInfoTypeForString("BONUS_ROGGEN") or iBonus == gc.getInfoTypeForString("BONUS_HAFER"):
      # Norden, kalt und feucht
      if iY < iRichtwertBreitengrad: return None,0
      else:
        # Norden besser als Sueden
        iChance += (iY - iMapH) * iChance/iRichtwertBreitengrad
    elif iBonus == gc.getInfoTypeForString("BONUS_GERSTE"):
      # Sueden, trocken
      if iY > iRichtwertBreitengrad: return None,0
      else:
        # Sueden besser als Norden
        iChance -= iY * iChance/iRichtwertBreitengrad
    # ----------
    """


    # Inits, auch in:
    # -) iData1 == 726
    # -) doEraseBonusFromDisaster
    # -) GameUtils: doBonusverbreitung_AI
    lGetreide = []
    lGetreide.append(gc.getInfoTypeForString("BONUS_WHEAT"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_GERSTE"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_HAFER"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_ROGGEN"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_HIRSE"))
    lGetreide.append(gc.getInfoTypeForString("BONUS_RICE"))
    lVieh1 = []
    lVieh1.append(gc.getInfoTypeForString("BONUS_COW"))
    lVieh1.append(gc.getInfoTypeForString("BONUS_PIG"))
    lVieh1.append(gc.getInfoTypeForString("BONUS_SHEEP"))
    lSpice = []
    lSpice.append(gc.getInfoTypeForString("BONUS_OLIVES"))
    lSpice.append(gc.getInfoTypeForString("BONUS_DATTELN"))
    lTier1 = []
    lTier1.append(gc.getInfoTypeForString("BONUS_CAMEL"))

    # Wenn ueberwiegend Wueste (>=50%)
    lNotNextDeserts = []
    lNotNextDeserts.append(gc.getInfoTypeForString("BONUS_COW"))
    lNotNextDeserts.append(gc.getInfoTypeForString("BONUS_PIG"))
    lNotNextDeserts.append(gc.getInfoTypeForString("BONUS_SHEEP"))

    # For Rice (no more)
    #iNumJungle = 0 # not in use
    # For Olives
    iNumPlains = 0
    # Desert
    iNumDesert = 0

    iTerrainPlains = gc.getInfoTypeForString("TERRAIN_PLAINS")
    iTerrainGrass  = gc.getInfoTypeForString("TERRAIN_GRASS")
    iTerrainDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
    iFeatureJunge  = gc.getInfoTypeForString("FEATURE_JUNGLE")
    iFeatureFlood  = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
    iFeatureSumpf  = gc.getInfoTypeForString("FEATURE_SWAMP")
    iDorf = gc.getInfoTypeForString("IMPROVEMENT_VILLAGE")
    iGemeinde = gc.getInfoTypeForString("IMPROVEMENT_TOWN")
    iFarm = gc.getInfoTypeForString("IMPROVEMENT_FARM")
    lImprovements = []
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_CAMP"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_PASTURE"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5"))

    # Aufplopp-Prio:
    # Kuh, Schwein, Datteln: nur auf Ebenen
    # -- Kuh Prio: Weide (Fluss), Weide, Gras, Plains
    # -- Schwein Prio: Sumpf (Weide), Weide, Fluss, Gras, Plains
    # -- Datteln: Desert
    # Schafe, Wild und Kamele: nur auf Hills (Prio: Grass, Plains)
    # -- Kamel: Desert
    # Getreide: nur auf Ebenen mit FreshWater (Prio: Schwemmland, Plains, Gras)
    # Reis (zus. zum Getreide): nur auf Ebenen, Fluss und Gras
    # Spices: nur auf Plains oder Gras (Prio: Plains, Gras)
    lPlotPrio1 = []
    lPlotPrio2 = []
    lPlotPrio3 = []
    lPlotPrio4 = []
    pCurrentPlot = None

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    # Fruchtbare Plots holen
    for x in range(3):
      for y in range(3):
        loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)

        if loopPlot.getFeatureType() == iDarkIce: continue

        # nicht auf Wasserplots oder dem Stadtplot
        if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak():

         # Klimazonen
         if loopPlot.getTerrainType() == iTerrainPlains: iNumPlains += 1
         if loopPlot.getTerrainType() == iTerrainDesert: iNumDesert += 1
         #if loopPlot.getFeatureType() == iFeatureJunge : iNumJungle += 1

         # nicht auf ausgewachsenen Huetten
         if loopPlot.getImprovementType() != iDorf and loopPlot.getImprovementType() != iGemeinde:
          iPlotBonus = loopPlot.getBonusType(iPlayer)
          # Unerforschte Resource?
          if iPlotBonus == -1: iPlotBonus = loopPlot.getBonusType(-1)

          # Plot hat bereits ne Bonusresi
          if iPlotBonus != -1:
            if iPlotBonus in lGetreide:
              if iBonus in lGetreide: pCurrentPlot = loopPlot
            elif iPlotBonus in lVieh1:
              if iBonus in lVieh1: pCurrentPlot = loopPlot
            elif iPlotBonus in lSpice:
              if iBonus in lSpice: pCurrentPlot = loopPlot
            elif iPlotBonus in lTier1:
              if iBonus in lTier1: pCurrentPlot = loopPlot

          # leerer Plot
          else:

            if loopPlot.getImprovementType() == -1: bImproved = False
            else: bImproved = True

            # Getreide und Reis: Nur auf Ebenen und FreshWater
            if iBonus in lGetreide:
              if not loopPlot.isHills() and not loopPlot.isPeak() and loopPlot.isFreshWater():
                # Rice: Fluss und Gras
                if iBonus == gc.getInfoTypeForString("BONUS_RICE"):
                  if loopPlot.isRiver() and loopPlot.getTerrainType() == iTerrainGrass:
                    if loopPlot.getImprovementType() == iFarm: lPlotPrio1.append(loopPlot)
                    elif not bImproved: lPlotPrio2.append(loopPlot)
                    else: lPlotPrio3.append(loopPlot)
                # Getreide Prio: Schwemmland, Ebene, Gras
                else:
                  if loopPlot.getFeatureType() == iFeatureFlood:
                    if loopPlot.getImprovementType() == iFarm: lPlotPrio1.append(loopPlot)
                    elif not bImproved: lPlotPrio2.append(loopPlot)
                    else: lPlotPrio4.append(loopPlot)
                  elif loopPlot.getTerrainType() == iTerrainPlains:
                    if loopPlot.getImprovementType() == iFarm: lPlotPrio2.append(loopPlot)
                    elif not bImproved: lPlotPrio3.append(loopPlot)
                    else: lPlotPrio4.append(loopPlot)
                  elif loopPlot.getTerrainType() == iTerrainGrass:
                    if loopPlot.getImprovementType() == iFarm: lPlotPrio2.append(loopPlot)
                    elif not bImproved: lPlotPrio3.append(loopPlot)
                    else: lPlotPrio4.append(loopPlot)

            # Kuh, Schwein und Schaf
            if iBonus in lVieh1:
                # nur auf Gras oder Plains
                if loopPlot.getTerrainType() == iTerrainGrass or loopPlot.getTerrainType() == iTerrainPlains:

                 # Hills: Schaf
                 if loopPlot.isHills():
                  if iBonus == gc.getInfoTypeForString("BONUS_SHEEP"):
                    if loopPlot.getImprovementType() in lImprovements: lPlotPrio1.append(loopPlot)
                    elif loopPlot.getTerrainType() == iTerrainGrass: lPlotPrio2.append(loopPlot)
                    else: lPlotPrio3.append(loopPlot)

                 # Flachland: Kuh und Schwein
                 else:
                  if iBonus == gc.getInfoTypeForString("BONUS_COW"):
                    if loopPlot.isFreshWater():
                      if loopPlot.getImprovementType() in lImprovements: lPlotPrio1.append(loopPlot)
                      elif loopPlot.getTerrainType() == iTerrainGrass:
                        if not bImproved: lPlotPrio2.append(loopPlot)
                        else: lPlotPrio4.append(loopPlot)
                      else:
                        if not bImproved: lPlotPrio3.append(loopPlot)
                        else: lPlotPrio4.append(loopPlot)
                    elif loopPlot.getImprovementType() in lImprovements: lPlotPrio2.append(loopPlot)
                    else:
                      if not bImproved: lPlotPrio3.append(loopPlot)
                      else: lPlotPrio4.append(loopPlot)

                  elif iBonus == gc.getInfoTypeForString("BONUS_PIG"):
                    if loopPlot.getFeatureType() == iFeatureSumpf:
                      if loopPlot.getImprovementType() in lImprovements: lPlotPrio1.append(loopPlot)
                      elif not bImproved: lPlotPrio2.append(loopPlot)
                      else: lPlotPrio4.append(loopPlot)
                    elif loopPlot.getImprovementType() in lImprovements: lPlotPrio2.append(loopPlot)
                    else:
                      if not bImproved: lPlotPrio3.append(loopPlot)
                      else: lPlotPrio4.append(loopPlot)

            # Oliven, Datteln und Gewuerze
            if iBonus in lSpice:
              # Oliven: Plains, Kueste
              if iBonus == gc.getInfoTypeForString("BONUS_OLIVES"):
                if loopPlot.getTerrainType() == iTerrainPlains:
                  if loopPlot.isCoastalLand():
                    if loopPlot.isHills():
                      if not bImproved: lPlotPrio1.append(loopPlot)
                      else: lPlotPrio3.append(loopPlot)
                    else:
                      if not bImproved: lPlotPrio2.append(loopPlot)
                      else: lPlotPrio4.append(loopPlot)
              # Datteln
              elif iBonus == gc.getInfoTypeForString("BONUS_DATTELN"):
                if loopPlot.getTerrainType() == iTerrainDesert: lPlotPrio1.append(loopPlot)
              # Spices: Plains, Grass
              else:
                if loopPlot.getTerrainType() == iTerrainPlains:
                  if not bImproved: lPlotPrio1.append(loopPlot)
                  else: lPlotPrio3.append(loopPlot)
                elif loopPlot.getTerrainType() == iTerrainGrass:
                  if not bImproved: lPlotPrio2.append(loopPlot)
                  else: lPlotPrio4.append(loopPlot)

            # Kamel
            if iBonus in lTier1:
              # nicht auf Hills
              if not loopPlot.isHills():
                if iBonus == gc.getInfoTypeForString("BONUS_CAMEL"):
                  # Desert (eben)
                  if loopPlot.getTerrainType() == iTerrainDesert:
                    if loopPlot.isFreshWater():
                      if not bImproved: lPlotPrio1.append(loopPlot)
                      else: lPlotPrio3.append(loopPlot)
                    else:
                      if not bImproved: lPlotPrio2.append(loopPlot)
                      else: lPlotPrio4.append(loopPlot)


    # Weitere Ausnahmen ------------------
    # zuviel Wueste
    if iNumDesert > 0:
      if iBonus in lNotNextDeserts: iChance -= iNumDesert * 45
      if iBonus in lGetreide: iChance -= iNumDesert * 20

    # Getreide
    if iBonus == gc.getInfoTypeForString("BONUS_ROGGEN") or iBonus == gc.getInfoTypeForString("BONUS_HAFER"):
      # kalt und feucht
      iChance -= iNumPlains * 40
    elif iBonus == gc.getInfoTypeForString("BONUS_GERSTE"):
      # trocken
      if iNumPlains == 0: return None,0

    # Bei zu geringer Chance
    if iChance <= 0: return None,0

    # Plot selektieren
    # Wenn bereits ne gruppengleiche Resi drauf is
    if pCurrentPlot != None:
      if pCurrentPlot.getOwner() != iPlayer: return None,0
      else:
        # Wenn es keinen erlaubten Plot gibt
        #if len(lPlotPrio1) == 0 and len(lPlotPrio2) == 0 and len(lPlotPrio3) == 0 and len(lPlotPrio4) == 0: return None,0
        #else:
        return pCurrentPlot, iChance

    # andere Plots und deren Prioritaeten
    if len(lPlotPrio1) > 0:
      iRand = self.myRandom(len(lPlotPrio1), None)
      return lPlotPrio1[iRand], iChance
    elif len(lPlotPrio2) > 0:
      iRand = self.myRandom(len(lPlotPrio2), None)
      return lPlotPrio2[iRand], iChance
    elif len(lPlotPrio3) > 0:
      iRand = self.myRandom(len(lPlotPrio3), None)
      return lPlotPrio3[iRand], iChance
    elif len(lPlotPrio4) > 0:
      iRand = self.myRandom(len(lPlotPrio4), None)
      return lPlotPrio4[iRand], iChance
    else: return None,0

  # --------------------------------

  # PAE Feature: Auswirkungen, wenn ein General stirbt
  def doDyingGeneral (self, pUnit):
        # Inits
        iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
        iPlayer = pUnit.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        pPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
        iNumLeadersOnPlot = 1

        # Anzahl der Generals des Spielers
        iLeader = 0
        iNumUnits = pPlayer.getNumUnits()
        i=0
        for i in range(iNumUnits):
          if pPlayer.getUnit(i).getLeaderUnitType() > -1:
            if pPlayer.getUnit(i).getID() != pUnit.getID():
              iLeader += 1

        # Units: bekommen Mercenary-Promo
        iNumUnits = pPlot.getNumUnits()
        # 1. Check Generals im Stack
        i=0
        for i in range(iNumUnits):
          if pPlot.getUnit(i).getOwner() == iPlayer:
            if pPlot.getUnit(i).getLeaderUnitType() > -1:
              if pPlot.getUnit(i).getID() != pUnit.getID():
                iNumLeadersOnPlot += 1
        # 2. Vergabe der Promo
        i=0
        for i in range(iNumUnits):
          if pPlot.getUnit(i).getOwner() == iPlayer:
            if i % iNumLeadersOnPlot == 0:
              pPlot.getUnit(i).setHasPromotion(iPromoMercenary, True)

        # Cities: Stadtaufruhr
#        iTeam = pPlayer.getTeam()
#        pTeam = gc.getTeam(iTeam)
#        lCities = PyPlayer(iPlayer).getCityList()
#
#        iRange = len(lCities)
#        i=0
#        for i in range(iRange):
#
#          if 0 == self.myRandom(iLeader, None):
#            loopCity = pPlayer.getCity(lCities[i].getID())
#            iRand = 2 + self.myRandom(3, None)
#            loopCity.changeHurryAngerTimer (iRand)
#            # 2 bis 4 Runden Aufstand!
#            iRand = 2 + self.myRandom(3, None)
#            loopCity.setOccupationTimer(iRand)
#            if pPlayer.isHuman():
#               CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MAIN_CITY_RIOT",(loopCity.getName(),)), "AS2D_REVOLTSTART", 2, ",Art/Interface/Buttons/Promotions/Combat5.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,5,10", ColorTypes(7), loopCity.getX(), loopCity.getY(), True, True)
#
        # PopUp
        if pPlayer.isHuman():
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Text PopUp only!
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_GENERALSTOD",(pUnit.getName(),)) )
          popupInfo.addPopup(iPlayer)

  # --------------------------------

  # AI: Release slaves when necessary (eg city shrinks)
  def doAIReleaseSlaves (self, pCity):
      # Inits
      iCityPop = pCity.getPopulation()
      iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
      iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
      iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
      iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
      iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

      if iCityPop >= iCityGlads + iCitySlaves: return
      else:
        # Inits
        pPlayer = gc.getPlayer(pCity.getOwner())

        # First prio: glads
        if iCityGlads > 0:
          while iCityGlads > 0 and iCityPop < iCityGlads + iCitySlaves:
            # Create slave unit
            NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            # Decrease specialist
            pCity.changeFreeSpecialistCount(15, -1)
            iCityGlads -= 1

        # check for return
        if iCityPop >= iCityGlads + iCitySlaves: return

        # Second prio: slaves
        if iCitySlaves > 0:
          # 1st prio: research
          while iCitySlavesHaus > 0 and iCityPop < iCitySlaves:
            NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            pCity.changeFreeSpecialistCount(16, -1)
            iCitySlavesHaus -= 1
            iCitySlaves -= 1
          # 2nd prio: prod
          while iCitySlavesProd > 0 and iCityPop < iCitySlaves:
            NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            pCity.changeFreeSpecialistCount(18, -1)
            iCitySlavesProd -= 1
            iCitySlaves -= 1
          # 3rd prio: food
          while iCitySlavesFood > 0 and iCityPop < iCitySlaves:
            NewUnit = pPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            pCity.changeFreeSpecialistCount(17, -1)
            iCitySlavesFood -= 1
            iCitySlaves -= 1

  # --- Mission: automated merchant
  def doAutomateMerchant (self, pUnit):
      iPlayer = pUnit.getOwner()
      pPlayer = gc.getPlayer(iPlayer)
      pPlot = pUnit.plot()

      # Handel ausfuehren
      if pPlot.isCity() and pPlot.getOwner() != -1 and pPlot.getOwner() != iPlayer and pPlot.getOwner() != gc.getBARBARIAN_PLAYER():
        pUnit.getGroup().pushMission(MissionTypes.MISSION_TRADE, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pPlot, pUnit)

      # Stadt auswaehlen
      else:
        if pUnit.getDomainType() == DomainTypes.DOMAIN_LAND: bLandUnit = true
        else: bLandUnit = false

        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)

        lNeighbors = []

        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

        # friedliche Nachbarn raussuchen
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
         loopPlayer = gc.getPlayer(i)
         if loopPlayer.isAlive() and i != iPlayer:
           if pTeam.isHasMet(loopPlayer.getTeam()):
             if pTeam.isOpenBorders (loopPlayer.getTeam()):
             #if not pTeam.isAtWar(loopPlayer.getTeam()):
               # Distanz mittels Abstand zur Hauptstadt herausfinden
               if not loopPlayer.getCity(0).isNone():
                 iDistanz = CyMap().calculatePathDistance(pPlot, loopPlayer.getCity(0).plot())
                 if iDistanz != -1: lNeighbors.append([iDistanz,loopPlayer])

        if len(lNeighbors):
          # Nach Distanz sortieren
          lNeighbors.sort()

          # Bestimmte Anzahl an Nachbarn raussuchen
          iMaxNeighbors = 4
          n = 0

          pSeekCity = None
          iDistanz = 0

          i = 0
          iRange = len(lNeighbors)
          for i in range(iRange):
            if n >= iMaxNeighbors: break
            n += 1

            iNumCities = lNeighbors[i][1].getNumCities()
            for j in range (iNumCities):
              loopCity = lNeighbors[i][1].getCity(j)
              if not loopCity.isNone():

               if pUnit.canMoveInto (loopCity.plot(), 0, 0, 0):

                # Fuer Landeinheiten alle cities
                # Fuer Schiffe nur coastal cities
                if bLandUnit or loopCity.isCoastal(4):

                  # Weil calculatePathDistance bei Schiffen nur auf Wasserplots funktioniert:
                  pPlot1 = None
                  pPlot2 = None
                  if bLandUnit:
                    pPlot1 = pPlot
                    pPlot2 = loopCity.plot()
                  else:
                    iX=pPlot.getX()
                    iY=pPlot.getY()
                    x=0
                    y=0
                    for x in range(3):
                      if pPlot1 != None: break
                      for y in range(3):
                        loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
                        if loopPlot != None and not loopPlot.isNone():
                          if loopPlot.getFeatureType() == iDarkIce: continue
                          if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_COAST"):
                            pPlot1 = loopPlot
                            break

                    iX=loopCity.plot().getX()
                    iY=loopCity.plot().getY()
                    x=0
                    y=0
                    for x in range(3):
                      if pPlot2 != None: break
                      for y in range(3):
                        loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
                        if loopPlot != None and not loopPlot.isNone():
                          if loopPlot.getFeatureType() == iDarkIce: continue
                          if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_COAST"):
                            pPlot2 = loopPlot
                            break


                  # Distanz berechnen
                  if pPlot1 != None and pPlot2 != None:
                    d = CyMap().calculatePathDistance(pPlot1, pPlot2)
                    if d > -1:
                      if iDistanz == 0 or iDistanz > d:
                        iDistanz = d
                        pSeekCity = loopCity


          # TEST
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pSeekCity.getName(),iDistanz)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          # Es wurde eine Stadt gewaehlt
          if pSeekCity != None and not pSeekCity.isNone():
             pUnit.getGroup().pushMoveToMission (pSeekCity.getX(), pSeekCity.getY())
             #if not pPlayer.isHuman():
             pUnit.getGroup().pushMission(MissionTypes.MISSION_TRADE, 0, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pSeekCity.plot(), pUnit)
             return True

  # Einheiten einen Zufallsrang vergeben (max. Elite)
  def doMercenaryRanking (self, pUnit, iMinRang, iMaxRang):
    iRang = self.myRandom(iMaxRang+1, None)
    if iRang < iMinRang: iRang = iMinRang
    if iRang >= 1:
      pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
      if iRang >= 2: pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
      if iRang >= 3: pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
      if iRang >= 4: pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)
      if iRang >= 5: pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5"), True)
      pUnit.setLevel(iRang)

  # Feldsklaven und Minensklaven checken
  def doCheckSlavesAfterPillage(self,pUnit,pPlot):
    pCity = pPlot.getWorkingCity()

    if pCity != None:

        # PAE V ab Patch 3: Einheiten mobilisieren
        if pCity.isCapital():
          self.doMobiliseFortifiedArmy(pCity.getOwner())

        # TEST
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pCity.getName(),0)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
        iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
        iUnitSlave = gc.getInfoTypeForString("UNIT_SLAVE")

        bFarms = False
        lFarms = []
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_PASTURE"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_FARM"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"))
        lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5"))

        bMines = False
        lMines = []
        lMines.append(gc.getInfoTypeForString("IMPROVEMENT_MINE"))
        lMines.append(gc.getInfoTypeForString("IMPROVEMENT_QUARRY"))

        iX = pCity.getX()
        iY = pCity.getY()
        for x in range(5):
          for y in range(5):
            loopPlot = gc.getMap().plot(iX + x - 2, iY + y - 2)
            if loopPlot != None and not loopPlot.isNone():

              if not loopPlot.isWater():

                # Plot besetzt?
                if pCity.canWork(loopPlot):
                  if loopPlot.getImprovementType() in lFarms: bFarms = True
                  elif loopPlot.getImprovementType() in lMines: bMines = True


          # Schleife vorzeitig beenden
          if bFarms and bMines: break



        iSlaves = 0
        # Feldsklaven checken
        if iCitySlavesFood > 0 and not bFarms:
          iSlaves += iCitySlavesFood
          pCity.setFreeSpecialistCount(17,0)

        # Bergwerkssklaven checken
        if iCitySlavesProd > 0 and not bMines:
          iSlaves += iCitySlavesProd
          pCity.setFreeSpecialistCount(18,0)

        # Spezialisten von der Stadt auf 0 setzen. Fluechtende Sklaven rund um den verheerenden Plot verteilen
        if iSlaves > 0:
          lFluchtPlots = []
          iX = pPlot.getX()
          iY = pPlot.getY()
          x = 0
          y = 0
          for x in range(3):
            for y in range(3):
              loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
              if loopPlot != None and not loopPlot.isNone():
                if not loopPlot.isWater() and not loopPlot.isPeak() :
                  if loopPlot.getNumUnits() == 0: lFluchtPlots.append(loopPlot)
          if len(lFluchtPlots) == 0: lFluchtPlots.append(pCity)

          for i in range(iSlaves):
            iRand = self.myRandom(len(lFluchtPlots), None)
            # gc.getBARBARIAN_PLAYER() statt pCity.getOwner()
            gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSlave, lFluchtPlots[iRand].getX(), lFluchtPlots[iRand].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          # Meldung
          if pUnit.getOwner() == gc.getGame().getActivePlayer() or pCity.getOwner() == gc.getGame().getActivePlayer():
            szButton = ",Art/Interface/Buttons/Actions/Pillage.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,8,2"
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_PILLAGE_SLAVES",(pCity.getName(),)), None, 2, szButton, ColorTypes(10), pPlot.getX(), pPlot.getY(), True, True)

  # -----------------------------------
  # PAE V ab Patch 3: Wenn Hauptstadt angegriffen wird, sollen alle Einheiten in Festungen remobilisiert werden (Promo FORTRESS)
  def doMobiliseFortifiedArmy(self,iOwner):
      pPlayer = gc.getPlayer(iOwner)
      pCity = pPlayer.getCapitalCity()
      if pCity != None:
        iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
        iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
        iNumUnits = pPlayer.getNumUnits()
        for i in range(iNumUnits):
          pPlayer.getUnit(i).setHasPromotion(iPromoFort, False)
          pPlayer.getUnit(i).setHasPromotion(iPromoFort2, False)

  # Handelsposten errichten
  def doBuildHandelsposten(self, pUnit):
      pPlot = pUnit.plot()
      pPlot.setRouteType(0)
      pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"))
      pPlot.setScriptData(str(pUnit.getOwner()))
      pPlot.setCulture(pUnit.getOwner(),1,True)
      pPlot.setOwner(pUnit.getOwner())
      gc.getPlayer(pUnit.getOwner()).changeGold(-30)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)

  # PAE Statthalter Tribut
  def getPAEStatthalterTribut(self):
    return self.PAEStatthalterTribut