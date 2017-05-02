## Sid Meier's Civilization 4
## Copyright Firaxis Games 2006
##
## CvEventManager
## This class is passed an argsList from CvAppInterface.onEvent
## The argsList can contain anything from mouse location to key info
## The EVENTLIST that are being notified can be found
## ---------------------
## Edited by Pie, Austria since 2010

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

# PAE River Tiles / navigable rivers (Ramk)
import CvRiverUtil
# Trade and cultivation (Pie, Boggy, Flunky)
import PAE_Trade
# Christian Events
import PAE_Christen
# Barbaren
import PAE_Barbaren
import PAE_Mercenaries
import PAE_City
import PAE_Unit
import PAE_Sklaven
import PAE_Vassal
import PAE_Disasters
# rundenbezogene Features
import PAE_Turn_Features

# Flunky: Scenario files
import PeloponnesianWar
import PeloponnesianWarKeinPferd
import Schmelz
import FirstPunicWar

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

###################################################
class CvEventManager:
  def __init__(self):
    #################### ON EVENT MAP ######################
    #print "EVENTMANAGER INIT"

    # PAE - Great General Names
    self.GG_UsedNames = []

    # PAE - Show message which player is on turn
    self.bPAE_ShowMessagePlayerTurn = False
    self.iPAE_ShowMessagePlayerHumanID = 0

    # PAE - River tiles
    """ The plot tiles require some initialisation at
    game startup, but the setup fails if it will be
    done into onLoadGame. Use same solution like
    FinalFrontier. Comment about this flag/issue in FF:
    Used when loading, since the order is wonky and trying to update display in onLoad 'splodes
    """
    self.bRiverTiles_NeedUpdate = False
    self.bRiverTiles_WaitOnMainInterface = False
    # PAE - River tiles end


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
              self.iPAE_ShowMessagePlayerHumanID = gc.getGame().getActivePlayer()
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
    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("onModNetMessage: ",iData1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    print("Modder's net message!")
    CvUtil.pyPrint( 'onModNetMessage' )

    #iData1 = iMessageID (!)

    # Inquisitor
    if iData1 == 665:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      PAE_City.doInquisitorPersecution(pCity, pUnit)
    # Horse down
    elif iData1 == 666:
      pPlot = CyMap().plot(iData2, iData3)
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      PAE_Unit.doHorseDown(pPlot, pUnit)
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
      pUnit.kill(1,pUnit.getOwner())
      CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_HUNS_PAID",()), None, 2, None, ColorTypes(14), 0, 0, False, False)
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
        else: iChance = 10
      elif iData5 == 1:
        if pPlayer.getGold() >= pCity.getPopulation() * 5:
          pPlayer.changeGold(pCity.getPopulation() * (-5))
          iChance = 5
        else: iChance = 10
      else: iChance = 10

      iRand = self.myRandom(10, None)
      if iRand < iChance:
        if pPlot.getNumUnits() > pCity.getPopulation(): iData4 = 2
        PAE_City.doCityRevolt (pCity,iData4)
        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_1",(pCity.getName(),)), None, 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
      else:
        CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_REVOLT_DONE_2",(pCity.getName(),)), None, 2, None, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

    # 676 vergeben (Tech - Unit)

    # 677 Goldkarren / Beutegold / Treasure zw 80 und 150
    elif iData1 == 677:
      pPlot = CyMap().plot(iData2, iData3)
      pCity = pPlot.getPlotCity()
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      iGold = 80 + self.myRandom(71, None)
      pPlayer.changeGold(iGold)
      pUnit.kill(1,pUnit.getOwner())
      CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GOLDKARREN_ADD_GOLD",(iGold,)), "AS2D_BUILD_BANK", 2, None, ColorTypes(8), 0, 0, False, False)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Beutegold eingesackt (Zeile 444)",150)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Provinzhauptstadt Statthalter Tribut
    elif iData1 == 678:
      # iData2 = iPlayer, iData3 = CityID, iData4 = Antwort [0,1,2] , iData5 = Tribut
      pPlayer = gc.getPlayer(iData2)
      pCity = pPlayer.getCity(iData3)
      iTribut = iData5
      iTribut2 = iData5 / 2

      iGold = pPlayer.getGold()
      bDoRebellion = False
      iAddHappiness = -1
      bPaid = False
      iRandRebellion = self.myRandom(100, None)

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
        PAE_City.doProvinceRebellion(pCity)
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
        # Kamel
        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")):
          lGift.append(gc.getInfoTypeForString("UNIT_CARAVAN"))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
          if pCity.canTrain(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"),0,0): lGift.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))

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

    elif (iData1 >= 668 and iData1 <= 670) or (iData1 >= 679 and iData1 <= 682) or (iData1 >= 692 and iData1 <= 693) or iData1 == 696:
      PAE_Sklaven.onModNetMessage(iData1, iData2, iData3, iData4, iData5)

    elif iData1 == 671 or (iData1 >= 682 and iData1 <= 691):
      PAE_Vassal.onModNetMessage(iData1, iData2, iData3, iData4, iData5)

    # Sklave wird verkauft (am Sklavenmarkt)
    elif iData1 == 694:
      PAE_Sklaven.doSell(iData2, iData3)

    # Unit wird verkauft (beim Soeldnerposten) - Sell unit
    elif iData1 == 695:
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
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_WILDLIFE"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_LOYALITAT"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_MERCENARY"))


        # +3 Gold pro Promotion
        iRange = gc.getNumPromotionInfos()
        for j in range(iRange):
          if "_FORM_" in gc.getPromotionInfo(j).getType(): continue
          if "_RANG_" in gc.getPromotionInfo(j).getType(): continue
          if "_MORAL_" in gc.getPromotionInfo(j).getType(): continue
          if "_TRAIT_" in gc.getPromotionInfo(j).getType(): continue
          if pUnit.isHasPromotion(j) and j not in FormationArray: iGold += 3

        pPlayer.changeGold(iGold)
        gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
        if pPlayer.isHuman():
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_UNIT_SOLD",(iGold,)),None,2,None,ColorTypes(8),0,0,False,False)
        pUnit.kill(1,pUnit.getOwner())


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
          if loopPlot != None and not loopPlot.isNone():
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
      if iCost < 0: iCost * (-1)
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
      pUnit.getGroup().setActivityType(-1) # to reload the map!
      pUnit.finishMoves()
      PAE_Unit.doGoToNextUnit(pUnit)

    # Unit bekommt Wellen-Oil
    elif iData1 == 701:
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
      do703(iData2, iData3, iData4, iData5)

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

          # set city and temple slaves => 0
          PAE_Sklaven.doEnslaveCity(pCity)

      elif iData5 == 2:
        if pCity != None:
          # --- Getting goldkarren / treasure / Beutegold ------
          iBeute = int(pCity.getPopulation() / 2) + 1
          ##if iBeute > 0: das ist >=1
          for _ in itertools.repeat(None, iBeute):
            pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

          pPlayer.disband(pCity)


    # Hire or Commission Mercenary Menu
    elif (iData1 >= 707 and iData1 <= 717):
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

       pCity.setNumRealBuilding(iData3,1)
       pUnit.kill(1,pUnit.getOwner())

    # Legendary unit can become a Great General (Feldherr)
    elif iData1 == 720:
       # 720, 0, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pUnit = pPlayer.getUnit(iData5)
       pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GREAT_GENERAL2"), pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
       PAE_Unit.doRetireVeteran(pUnit)

    # Elefantenstall
    elif iData1 == 721:
       # 721, iCityID, (1 = Elefantenstall | 2 = Kamellager), iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       if   iData3 == 1:
         pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE"),1)
         self.onBuildingBuilt([pCity, gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")])
       elif iData3 == 2:
         pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE"),1)
         self.onBuildingBuilt([pCity, gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")])
       pUnit.kill(1,pUnit.getOwner())

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
       for i in range(-iVisible, iVisible+1):
         for j in range(-iVisible, iVisible+1):
           loopPlot = plotXY(iX, iY, i, j)
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
         pUnit.kill(1,pUnit.getOwner())

        # changeMoves
       else:
         CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE3",("",)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(11), pUnit.getX() + i - iVisible, pUnit.getY() + j - iVisible, True, True)

    # iData1 723: EspionageMission Info im TechChooser

    # Veteran -> Reservist
    elif iData1 == 724:
       # 724, iCityID, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.changeFreeSpecialistCount(19, 1) # SPECIALIST_RESERVIST
       pUnit.kill(1,pUnit.getOwner())

    # Reservist -> Veteran
    elif iData1 == 725:
       # iData1, iData2, ... iData5
       # First:  725, iCityID, iPlayer, -1, 0
       # Second: 725, iCityID, iPlayer, iButtonID (Typ), 0
       pPlayer = gc.getPlayer(iData3)
       pCity = pPlayer.getCity(iData2)
       iTeam = pPlayer.getTeam()
       pTeam = gc.getTeam(iTeam)

       iReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST

       # Units
       bUnit1 = True
       bUnit2 = True
       bUnit3 = True
       bUnit4 = True

       # Unit 1
       iUnit1 = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
       if not pCity.canTrain(iUnit1,0,0): bUnit1 = False
       # Unit 2
       iUnit2 = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
       if not pCity.canTrain(iUnit2,0,0):
          bUnit2 = False
          iUnit2 = gc.getInfoTypeForString("UNIT_ARCHER")
       # Unit 3
       iUnit3 = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
       if not pTeam.isHasTech(gc.getUnitInfo(iUnit3).getPrereqAndTech()): bUnit3 = False
       # Unit 4
       iUnit4 = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
       if not (pTeam.isHasTech(gc.getUnitInfo(iUnit4).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE"))): bUnit4 = False

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

##    # Alte Bonusverbreitung UNIT_SUPPLY_FOOD (Obsolete)
##    if iData1 == 726:  frei

    # Getreidelieferung UNIT_SUPPLY_FOOD
    elif iData1 == 727:
       # 727, iCityID, 0, iPlayer, iUnitID
       pPlayer = gc.getPlayer(iData4)
       pCity = pPlayer.getCity(iData2)
       pUnit = pPlayer.getUnit(iData5)

       pCity.changeFood(50)
       pUnit.kill(1,pUnit.getOwner())

    # Karte zeichnen
    if iData1 == 728:
       # 728, iPage/iButtonId, -1, iPlayer, iUnitID
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
         popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_KARTE_ZEICHNEN_4",(iGold,iChance))+txtBonus, "Art/Interface/Buttons/Buildings/button_city_metropole.dds")

         # Metropolen: 600 G/90% TRAIT_EXPANSIVE
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
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             pPlayer.changeGold(-iGold)
             bRemoveUnit = True
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
             bRemoveUnit = True
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
             bRemoveUnit = True
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
             bRemoveUnit = True
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

         # Metropolen: 600 G/90% TRAIT_EXPANSIVE
         elif iData2 == 4:
           iChance = 90
           iGold = 600
           if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EXPANSIVE")):
             iGold = int(iGold * .75)
           if pPlayer.getGold() < iGold:
             CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
           else:
             bRemoveUnit = True
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
             bRemoveUnit = True
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
             bRemoveUnit = True
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
           pUnit.kill(1,pUnit.getOwner())


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
      #Flunky: was ist hiermit?
      # for iReligion in range(gc.getNumReligionInfos()):
        # if gc.getUnitInfo(pUnit.getUnitType()).getReligionSpreads(iReligion): break

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
        bCanSpread = False
        iNumCities = pPlayer.getNumCities()
        for i in range (iNumCities):
          pCity = pPlayer.getCity(i)
          if not pCity.isNone():
            if not pCity.isHasReligion(iReligion):
              pUnit.getGroup().pushMoveToMission (pCity.getX(), pCity.getY())
              pUnit.getGroup().pushMission(MissionTypes.MISSION_SPREAD, iReligion, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
              bCanSpread = True

        if not bCanSpread:
          CyInterface().addMessage(iData4, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SPREAD_RELIGION_NEG",(gc.getReligionInfo(iReligion).getDescription(),"")), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Obsolete (Boggy)
##    # Trade Mission: send and submit merchant into next foreign city
##    if iData1 == 732:
##      # 732, -1, -1, iPlayer, iUnitID
##      pPlayer = gc.getPlayer(iData4)
##      pUnit = pPlayer.getUnit(iData5)
##      self.doAutomateMerchant(pUnit)

    # Build Limes PopUp
    elif iData1 == 733:
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
    elif iData1 == 734:
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
      pUnit.kill(1,pUnit.getOwner())

    # Salae oder Dezimierung
    elif iData1 == 735:
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
        PAE_Unit.doGoToNextUnit(pUnit)


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
            reservePlotArray = []
            iRange = 1
            iX = pCity.getX()
            iY = pCity.getY()
            for i in range(-iRange, iRange+1):
                for j in range(-iRange, iRange+1):
                    loopPlot = plotXY(iX, iY, i, j)
                    if loopPlot != None and not loopPlot.isNone() and not loopPlot.isUnit():
                        if loopPlot.isHills() and loopPlot.getOwner() == iPlayer:
                            rebelPlotArray.append(loopPlot)
                        if loopPlot.getOwner() == iPlayer and not (loopPlot.isWater() or loopPlot.isImpassable() or loopPlot.isCity()):
                            reservePlotArray.append(loopPlot)

            if len(rebelPlotArray) == 0:
                rebelPlotArray = reservePlotArray


            if len(rebelPlotArray) > 0:
                iPlot = self.myRandom(len(rebelPlotArray), None)
                pPlot = rebelPlotArray[iPlot]
                NewUnit = gc.getBARBARIAN_PLAYER().initUnit(pUnit.getUnitType(), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

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
                pUnit.kill(1,pUnit.getOwner())
            else:
                CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_OUT",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
                pUnit.kill(1,pUnit.getOwner())

        # Decimatio ist erfolgreich
        elif iRand < iChance+5:
          # Unit verletzen
          pUnit.changeDamage(10,False)


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

          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_POS",(gc.getPromotionInfo(iPromo).getDescription(),)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)
          pUnit.finishMoves()
          PAE_Unit.doGoToNextUnit(pUnit)

        # Keine Auswirkung
        else:
          CyInterface().addMessage(iData4, True, 8, CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_NEG",("",)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Actions/button_action_dezimierung.dds",ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
          pUnit.finishMoves()
          PAE_Unit.doGoToNextUnit(pUnit)

    # Handelsposten errichten
    elif iData1 == 736:
      # 736, 0, 0, iPlayer, iUnitID
      pUnit = gc.getPlayer(iData4).getUnit(iData5)
      PAE_Unit.doBuildHandelsposten(pUnit)

    # Statthalter / Tribut
    elif iData1 == 737:
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
           iRand = 1 + self.myRandom(3, None)
           if iRand >= 1: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
           if iRand >= 2: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
           if iRand >= 3: NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
           NewUnit.setImmobileTimer(1)
         # Getreide
         elif iData5 == 2:
           pCity.changeExtraHappiness(-iUnhappy3)
           NewUnit = pPlayer.initUnit(iUnit3, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           NewUnit.setImmobileTimer(1)
         # Sklaven
         elif iData5 == 3:
           pCity.changeExtraHappiness(-iUnhappy4)
           NewUnit = pPlayer.initUnit(iUnit4, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
           NewUnit.setImmobileTimer(1)

         if iData5 > -1:
           if iData3 == gc.getGame().getActivePlayer():
             CyAudioGame().Play2DSound("AS2D_UNIT_BUILD_UNIT")

    # 738-743: Cultivation feature / Bonusverbreitung ( Cultivation / Trade / Boggy )
    # 744-748: Automated trade routes

    #~ # 738: Create popup for bonus cultivation
    #~ if iData1 == 738:
        #~ pPlayer = gc.getPlayer(iData2)
        #~ pUnit = pPlayer.getUnit(iData3)
        #~ # iData4 = int von iIsCity
        #~ PAE_Trade.doPopupChooseBonusForCultivation(pUnit, iData4)

    # 738, iPlayer, iUnit, iIsCity
    # Cultivate bonus.
    if iData1 == 738:
        pPlayer = gc.getPlayer(iData2)
        pUnit = pPlayer.getUnit(iData3)
        eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
        if eBonus != -1:
            pPlot = pUnit.plot()
            if pPlot.isCity():
                pPlot = PAE_Trade.getCityCultivationPlot(pPlot.getPlotCity(), eBonus)
            PAE_Trade.doCultivateBonus(pPlot, pUnit, eBonus)


    # Collect bonus from plot
    elif iData1 == 739:
        pPlayer = gc.getPlayer(iData4)
        pUnit = pPlayer.getUnit(iData5)
        if iData2 == -1:
            # Kaufen
            if iData3 == 1: PAE_Trade.doPopupChooseBonus4Cultivation(pUnit)
            # Collect
            elif iData3 == 0: PAE_Trade.doCollectBonus4Cultivation(pUnit)
        # im Popup ausgewaehlt, iData2 = BonusType
        else: PAE_Trade.doBuyBonus4Cultivation(pUnit, iData2)

    # Create popup for buying bonus (in city)
    elif iData1 == 740:
        pPlayer = gc.getPlayer(iData4)
        pUnit = pPlayer.getUnit(iData5)
        pCity = CyMap().plot(iData2,iData3).getPlotCity()
        PAE_Trade.doPopupChooseBonus(pUnit, pCity)

    # Sell bonus (in city)
    elif iData1 == 741:
        pPlayer = gc.getPlayer(iData4)
        pUnit = pPlayer.getUnit(iData5)
        pCity = CyMap().plot(iData2,iData3).getPlotCity()
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
            #if pUnit.canMove():
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
       PAE_Unit.doUpgradeRang(iData4,iData5)

    # 752: bless units
    elif iData1 == 752:
       # iData1, iData2, ... , iData5
       # 752, iX, iY, iPlayer, iUnitID
       PAE_Unit.doBlessUnits(iData2,iData3,iData4,iData5)

    # Slave -> Latifundium
    elif iData1 == 753:
      # 733, -1 oder iButtonID, -1, iPlayer, iUnitID
      pPlayer = gc.getPlayer(iData4)
      pUnit = pPlayer.getUnit(iData5)
      pPlot = pUnit.plot()
      pPlot.changeUpgradeProgress(10)
      pUnit.kill(1,pUnit.getOwner())

    # 754: Obsolete Unit text in Tech Screen

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

  def onInit(self, argsList):
    'Called when Civ starts up'
    CvUtil.pyPrint( 'OnInit' )

  def onUpdate(self, argsList):
    'Called every frame'
    fDeltaTime = argsList[0]

    # allow camera to be updated
    CvCameraControls.g_CameraControls.onUpdate( fDeltaTime )

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

    # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
    gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), False)

    # PAE - River tiles
    self.bRiverTiles_WaitOnMainInterface = True

    # PAE_Trade needs to be initialised
    PAE_Trade.init()

    PAE_Christen.init()

    # ---------------- Schmelzen 2/4 (BoggyB) --------
    # Beim Neuladen (Felder aus 3/4 bleiben nicht gespeichert)
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName == "SchmelzEuro" or sScenarioName == "SchmelzWelt":
      Schmelz.onLoadGame(sScenarioName)

    # --------- BTS --------
    CvAdvisorUtils.resetNoLiberateCities()
    return 0

  # +++++ PAE Debug: disband/delete things (for different reasons: CtD or OOS)
  def onGameStartAndKickSomeAss(self):

    iRange = gc.getMAX_PLAYERS()
    """
    for iPlayer in range(iRange):
      # Units
      pPlayer = gc.getPlayer(iPlayer)
      if pPlayer.isAlive():
        #iNumUnits = pPlayer.getNumUnits()
        #for j in range(iNumUnits):
        (pUnit, iter) = pPlayer.firstUnit(False)
        while pUnit:
        #  if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT") \
        #  or pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_MERCHANT"):
           pUnit.kill(1,pUnit.getOwner())
           (pUnit, iter) = pPlayer.nextUnit(iter, False)
        # City buildings
        iNumCities = pPlayer.getNumCities()
        for iCity in range (iNumCities):
          pCity = pPlayer.getCity(iCity)
          if not pCity.isNone():
            iRange2 = gc.getNumBuildingInfos()
            for iBuilding in range (iRange2):
                pCity.setNumRealBuilding(iBuilding,0)
    """

    """
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for x in range(iMapW):
      for y in range(iMapH):
        loopPlot = gc.getMap().plot(x,y)
        #if loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_MINE"):
        loopPlot.setImprovementType(-1)
    """



  def onGameStart(self, argsList):
    'Called at the start of the game'

    # +++++ PAE Debug: disband/delete things to check CtD reasons)
    #self.onGameStartAndKickSomeAss()

    # force deactivation, otherwise CtD when choosing a religion with forbidden tech require
    gc.getGame().setOption(gc.getInfoTypeForString("GAMEOPTION_PICK_RELIGION"), False)

    # PAE - River tiles
    self.bRiverTiles_WaitOnMainInterface = True

    # PAE_Trade needs to be initialised
    PAE_Trade.init()

    PAE_Christen.init()

    ### Starting points part 2 ###
    MapName = CyMap().getMapScriptName ()
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START) and gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR"):
      MapName = ""
      bPlaceCivs = True
      bPlaceBarbs = True
      # PAE Maps
      if sScenarioName == "EuropeStandard": MapName = "StartingPoints_EuropeStandard.xml"
      elif sScenarioName == "EuropeMini": MapName = "StartingPoints_EuropeMini.xml"
      elif sScenarioName == "EuropeMedium": MapName = "StartingPoints_EuropeMedium.xml"
      elif sScenarioName == "EuropeLarge": MapName = "StartingPoints_EuropeLarge.xml"
      elif sScenarioName == "EuropeSmall": MapName = "StartingPoints_EuropeSmall.xml"
      elif sScenarioName == "SchmelzEuro": MapName = "StartingPoints_EuropeLarge.xml"
      elif sScenarioName == "EuropeXL": MapName = "StartingPoints_EuropeXL.xml"
      elif sScenarioName == "Eurasia": MapName = "StartingPoints_Eurasia.xml"
      #elif sScenarioName == "EasternMed":
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
         StartingPointsUtil.ReadMyFile(MyFile,Debugging,AddPositionsToMap,bPlaceCivs,bPlaceBarbs)
         MyFile.close()
    # --------------------------------

    # +++++ Special dawn of man texts for Szenario Maps in PAE in CvDawnOfMan.py ++++++++++++++++++++++++++++++++
    #if (gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR") and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
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
        ##Flunky: (unit, iter) statt for range
        # +++++ Correct naming for units (not available in BTS)
        (unit, iter) = player.firstUnit(False)
        while unit:
          UnitText = unit.getName()
          if UnitText[:7] == "TXT_KEY":
            sz = UnitText.split()
            sTranslatedName = CyTranslator().getText(str(sz[0]),("",))
            unit.setName(sTranslatedName)
          #PAE Debug: delete certain units
          #if player.getUnit(j).getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
          #   player.getUnit(j).kill(1,player.getUnit(j).getOwner())

          # Handelskarren CityID eintragen
          #if unit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"):
          #   pPlot = unit.plot()
          #   if pPlot.isCity():
          #     #unit.setScriptData(str(pPlot.getPlotCity().getID()))
          #     CvUtil.addScriptData(unit, "c", pPlot.getPlotCity().getID()) # CityID

          (unit, iter) = player.nextUnit(iter, False)

        ##Flunky: Einrueckung angepasst
        # Trait-Gebaeude ueberpruefen
        PAE_City.doCheckGlobalTraitBuildings(iPlayer)

        ##Flunky: (city, iter) statt for range
        # +++++ Check city status
        # und Trait-Gebaeude / trait buildings
        (city,iter) = player.firstCity(False)
        while city:
          PAE_City.doCheckCityState(city)
          PAE_City.doCheckTraitBuildings(city)
          (city,iter) = player.nextCity(iter, False)
        ##/Flunky

        #Start in spaeterer Aera -> unerforschbare und Relitechs entfernen
        #Start in later era -> remove unresearchable and religious techs
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

    #for x in range(iMapW):
    #  for y in range(iMapH):
    #    loopPlot = gc.getMap().plot(x,y)
    #    #if loopPlot != None and not loopPlot.isNone():
    #    if loopPlot.getFeatureType() == iDarkIce: continue
    #    if loopPlot.getBonusType(-1) == bonus_zedern and loopPlot.getFeatureType() != feat_forest:
    #       loopPlot.setFeatureType(feat_forest,1)
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
    PAE_Turn_Features.doHistory()

  # global
  def onEndGameTurn(self, argsList):
    'Called at the end of the end of each turn'
    iGameTurn = argsList[0]

    # Special Scripts for PAE Scenarios
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName != "":
        if sScenarioName == "PeloponnesianWar":
            PeloponnesianWar.onEndGameTurn(iGameTurn)

      # ---------------- Schmelzen 3/4 (BoggyB) --------
        if sScenarioName == "SchmelzEuro" or sScenarioName == "SchmelzWelt":
            Schmelz.onEndGameTurn(iGameTurn, sScenarioName)

        if sScenarioName == "PeloponnesianWarKeinpferd":
            PeloponnesianWarKeinpferd.onEndGameTurn(iGameTurn)

    ## Goody-Doerfer erstellen (goody-huts / GoodyHuts / Goodies / Villages) ##
    # PAE V: Treibgut erstellen
    # PAE V: Barbarenfort erstellen
    # PAE Trade Cities Special Bonus
    if gc.getGame().getGameTurnYear() > -2400:
        if iGameTurn % 20 == 0:
            PAE_Turn_Features.setGoodyHuts()
            PAE_Trade.addCityWithSpecialBonus(iGameTurn)

        PAE_Trade.doUpdateCitiesWithSpecialBonus(iGameTurn)

    # -- PAE V: Treibgut -> Strandgut
    PAE_Turn_Features.doStrandgut()

    # -- PAE Disasters / Katastrophen
    # Permanent Alliances entspricht = Naturkatastrophen (PAE)
    if not (gc.getGame().isOption(GameOptionTypes.GAMEOPTION_PERMANENT_ALLIANCES) or gc.getGame().isGameMultiPlayer()):
        PAE_Disasters.doGenerateDisaster(iGameTurn)

    # -- Seewind / Fair wind ----
    if iGameTurn % 15 == 0: PAE_Turn_Features.doSeewind()

    # PAE Debug Mark
    #"""
# Seevoelker erschaffen: Langboot + Axtkrieger oder Axtkaempfer | -1500 bis -800
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
      if iGameTurn % 5 == 0 and gc.getGame().getGameTurnYear() > -1400 and gc.getGame().getGameTurnYear() < -800:
        PAE_Barbaren.doSeevoelker()
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Seevoelker erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Wikinger erschaffen: Langboot + Berserker | ab 400 AD
    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
      if iGameTurn % 5 == 0 and gc.getGame().getGameTurnYear() >= 400:
        PAE_Barbaren.doVikings()
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Wikinger erstellt",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Handelskarren erschaffen: -1800 bis 0
    if iGameTurn % 20 == 0 and gc.getGame().getGameTurnYear() > -1800 and gc.getGame().getGameTurnYear() < 0:
      PAE_Barbaren.doHandelskarren()
      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barb. Handelskarren erschaffen",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# -- Huns | Hunnen erschaffen: Hunnischer Reiter | ab 250 AD  ---------
    PAE_Barbaren.doHuns(iGameTurn)

# ------ Handelsposten erzeugen Kultur (PAE V Patch 3: und wieder Forts/Festungen)
# ------ Berberloewen erzeugen
# ------ Wildpferde, Wildelefanten, Wildkamele ab PAE V
# ------ Barbarenfort beleben (PAE V Patch 4)
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

    # --- Automated trade routes for HI (Boggy)
    if pPlayer.isHuman():
        (pLoopUnit, iter) = pPlayer.firstUnit(False)
        while pLoopUnit:
            iUnitType = pLoopUnit.getUnitType()
            if iUnitType in PAE_Trade.lTradeUnits:
                bTradeRouteActive = int(CvUtil.getScriptData(pLoopUnit, ["autA","t"], 0))
                if bTradeRouteActive and pLoopUnit.getGroup().getLengthMissionQueue() == 0:
                    PAE_Trade.doAutomateMerchant(pLoopUnit, False)
                    #pLoopUnit.finishMoves()
                    # Falls Haendler in Stadt zieht und noch Fortbewegung hat, soll direkt ge-/verkauft werden
                    #if pLoopUnit.canMove(): PAE_Trade.doAutomateMerchant(pLoopUnit, False)
            (pLoopUnit, iter) = pPlayer.nextUnit(iter, False)

    # ------- Scenario PeloponnesianWarKeinpferd Events Poteidaia, Megara, Plataiai, Syrakus
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName == "PeloponnesianWarKeinpferd":
        PeloponnesianWarKeinPferd.onBeginPlayerTurn(iGameTurn, pPlayer)

# -- TESTMESSAGE

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
     lHealerPlots = []
     lFormationPlots = []
     iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
     iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")

     (sUnit, iter) = pPlayer.firstUnit(False)
     while sUnit:
       # tmpA: OBJECTS (tmpPlot) KANN MAN NICHT mit NOT IN in einer Liste pruefen!
       tmpA = [sUnit.getX(),sUnit.getY()]
       tmpPlot = sUnit.plot()
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

        # AI Formations
       if not pPlayer.isHuman():
         if tmpPlot.getNumUnits() > 2:
           if tmpA not in lFormationPlots:
             lFormationPlots.append(tmpA)
         else:
          # more than 50% damage -> go defensive
           if sUnit.getDamage() > 50: PAE_Unit.doAIUnitFormations (sUnit, False, False, False)

         # Missing fort on a plot
         if sUnit.isHasPromotion(iPromoFort) or sUnit.isHasPromotion(iPromoFort2):
            iImp = tmpPlot.getImprovementType()
            if iImp > -1:
               if gc.getImprovementInfo(iImp).getDefenseModifier() < 10 or tmpPlot.getOwner() != sUnit.getOwner(): PAE_Unit.doUnitFormation (sUnit, -1)
            else: PAE_Unit.doUnitFormation (sUnit, -1)

       (sUnit, iter) = pPlayer.nextUnit(iter, False)
     # while end

     if len(lFormationPlots) > 0:
       for h in lFormationPlots:
         loopPlot = gc.getMap().plot(h[0],h[1])
         if not loopPlot.isCity(): PAE_Unit.doAIPlotFormations (loopPlot, iPlayer)

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
           eDruide = gc.getInfoTypeForString("UNIT_DRUIDE")
           eBrahmane = gc.getInfoTypeForString("UNIT_BRAHMANE")
           for loopUnit in lHealer:
                if iSupplyChange <= 0: break
                iSupplyChange = PAE_Unit.fillSupply(loopUnit, iSupplyChange)


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
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("UNITCOMBAT_MELEE",iMelee)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("UNITCOMBAT_HEALER",len(lHealer))), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Plot properties
            bDesert = loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT")

            # 1. Versorgen
            for loopUnit in lHealer:
                if iMounted <= 0 and iMelee <= 0: break
                (iSupplyValue, _) = PAE_Unit.getSupply(loopUnit)

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
                    PAE_Unit.setSupply(loopUnit,iSupplyValue)

               # ***TEST***
               #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Supply Unit changed",iSupplyValue)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # 2. Units verletzen
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
              PAE_City.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())

            # grosse Rebellion (+ Generalseinheit)
            else:
              if pPlayer.isHuman():
                text = CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_2",("Units",iNumUnits))
                CyInterface().addMessage(iPlayer, True, 5, text, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), sPlot.getX(), sPlot.getY(), True, True)

              listNamesStandard = ["Adiantunnus","Divico","Albion","Malorix","Inguiomer","Archelaos","Dorimachos","Helenos","Kerkidas","Mikythos","Philopoimen","Pnytagoras","Sophainetos","Theopomopos","Gylippos","Proxenos","Theseus","Balakros","Bar Kochba","Julian ben Sabar","Justasas","Patricius","Schimon bar Giora","Artaphernes","Harpagos","Atropates","Bahram Chobin","Datis","Schahin","Egnatius","Curius Aentatus","Antiochos II","Spartacus","Herodes I","Calgacus","Suebonius Paulinus","Maxentus","Sapor II","Alatheus","Saphrax","Honorius","Aetius","Achilles","Herodes","Heros","Odysseus","Anytos"]
              iName = self.myRandom(len(listNamesStandard), None)

              iUnitType = gc.getInfoTypeForString("UNIT_GREAT_GENERAL2")
              unit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitType, rebelPlotArray[iRebelPlot].getX(), rebelPlotArray[iRebelPlot].getY(), UnitAITypes.UNITAI_GENERAL, DirectionTypes.DIRECTION_SOUTH)
              unit.setName(listNamesStandard[iName])
              PAE_City.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())
              PAE_City.doNextCityRevolt(sPlot.getX(), sPlot.getY(), iPlayer, gc.getBARBARIAN_PLAYER())

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
              pUnit = sPlot.getUnit(iRand)
              pUnit.kill(1,pUnit.getOwner())
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
            #pUnit = sPlot.getUnit(seekUnit)
            #pUnit.kill(1,pUnit.getOwner())

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

          # Sklavensterben
          elif iTyp != -1:

            # PAE V: stehende Sklaven werden zugewiesen
            bErsatz = False
            # City Plot
            pCityPlot = pCity.plot()
            iRangePlotUnits = pCityPlot.getNumUnits()
            for iUnit in range (iRangePlotUnits):
              if pCityPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                 pUnit = pCityPlot.getUnit(iUnit)
                 pUnit.kill(1,pUnit.getOwner())
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
              # A) Standard Sklavensterben
              # B) Tech Patronat: Hausklaven werden freie Buerger
              iRand = 0
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PATRONAT")): iRand = 2

              # Dying
              if self.myRandom(iRand, None) == 0:
                if not bErsatz:
                  pCity.changeFreeSpecialistCount(16, -1)
                  iCitySlavesHaus -= 1
                if pPlayer.isHuman():
                  iRand = 1 + self.myRandom(14, None)
                  CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_HAUS_"+str(iRand),(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
              # Patronat
              else:
                bErsatz = False
                pCity.changeFreeSpecialistCount(16, -1)
                iCitySlaves -= 1
                pCity.changeFreeSpecialistCount(0, +1) # SPECIALIST_CITIZEN2
                if pPlayer.isHuman():
                  iRand = 1 + self.myRandom(2, None)
                  CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_PATRONAT_"+str(iRand),(pCity.getName(),"")),None,2,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(8),pCity.getX(),pCity.getY(),True,True)


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
                      pUnit = pCityPlot.getUnit(iUnit)
                      pUnit.kill(1,pUnit.getOwner())
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
                PAE_City.doCityRevolt (pCity,iNumRebels+1)

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
                  PAE_Sklaven.doAIReleaseSlaves(pCity)


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
                      pUnit = pCityPlot.getUnit(iUnit)
                      pUnit.kill(1,pUnit.getOwner())
                      iDone = iDone + 1

                iNumRebels = iNumRebels + iNumRebels2

                iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")

                for i in range(iNumRebels):
                  iPlot = self.myRandom(len(rebelPlotArray), None)
                  barbPlayer.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiatorenaufstand (Zeile 1188)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)



                # City Revolt
                PAE_City.doCityRevolt (pCity,iNumRebels+1)
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
              PAE_City.doCityRevolt (pCity,4)
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


# ------ Anarchie wenn mehr als die Haelfte der Staedte revoltieren (mehr als 1 Stadt) oder von der Pest heimgesucht werden - 33 %
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

          if iCityRevolt > 1 and iNumCities <= iCityRevolt * 2:
            pPlayer.changeAnarchyTurns(3)
            if pPlayer.isHuman():
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_PLAYER_ANARCHY_FROM_REVOLTS",("", )))
              popupInfo.addPopup(iPlayer)

          elif iNumCities <= iCityPlague * 2:
            pPlayer.changeAnarchyTurns(2)
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
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName == "FirstPunicWar":
      FirstPunicWar.onEndPlayerTurn(iPlayer, iGameTurn)
    elif sScenarioName == "PeloponnesianWarKeinpferd":
      PeloponnesianWarKeinpferd.onEndPlayerTurn(iPlayer, iGameTurn)

# +++++ MAP Reveal to black fog - Kriegsnebel - Fog of War (FoW) - Karte schwarz zurueckfaerben
# AI auch, aber nur alle iPlayer-Runden
# AI wird wieder reingenommen -> wenn nur alle x Runden wahrscheinlich weniger Einheitenbewegung! -> no MAFs
    if pPlayer != None:
      iTeam = pPlayer.getTeam()
      pTeam = gc.getTeam(iTeam)
      # Human oder KI alle x Runden, aber unterschiedliche Civs pro Runde fuer optimale Rundenzeiten
      if pPlayer.isHuman() or (iGameTurn % 10 == iPlayer % 10 and pTeam.isMapTrading()):
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
          iRange = CyMap().numPlots()
          for iI in range(iRange):
              pPlot = CyMap().plotByIndex(iI)
              if not pPlot.isVisible (iTeam, 0):
                bGoBlack = True
                # fully black or standard fog of war
                if pPlot.isCity():
                  pCity = pPlot.getPlotCity()
                  if bShowCoasts and pCity.isCapital(): bGoBlack = False
                  elif pCity.getNumWorldWonders() > 0: bGoBlack = False
                # Holy Mountain Quest
                if bGoBlack:
                  if CvUtil.getScriptData(pPlot,["H","t"]) == "X": bGoBlack = False
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


# -- AI Commissions Mercenaries (AI Mercenaries)
    # not in first turn (scenarios)
    if not pPlayer.isHuman():
     if iGameTurn > 1 and iGameTurn % 10 == 0:
      if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SOELDNERTUM")):

       iGold = pPlayer.getGold()

       if iGold > 400:
         bDoIt = False

         if iGold > 800: iChance = 20
         else: iChance = 10
         if iChance > self.myRandom(100, None): bDoIt = True

         if bDoIt:
           PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)
           # 20% gleich nochmal
           if 0 == self.myRandom(5, None):
             PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)
             # 10% ein drittes Mal damits interessant wird ;)
             if 0 == self.myRandom(10, None): PAE_Mercenaries.doAIPlanAssignMercenaries(iPlayer)

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
    if (gc.getGame().getElapsedGameTurns() == 1):
      if (gc.getPlayer(iPlayer).isHuman()):
        if (gc.getPlayer(iPlayer).canRevolution(0)):
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
      if showPlayer >= gc.getMAX_PLAYERS(): showPlayer = 0
      while (not gc.getPlayer(showPlayer).isAlive()):
        showPlayer += 1
        if showPlayer >= gc.getMAX_PLAYERS(): showPlayer = 0

      thisPlayer = gc.getPlayer(showPlayer).getCivilizationDescription(0)
      if (self.bAllowCheats):
            CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN",(thisPlayer,"")), None, 2, None, ColorTypes(14), 0, 0, False, False)
      else:
            iThisTeam = gc.getPlayer(showPlayer).getTeam()
            if gc.getTeam(iThisTeam).isHasMet(pPlayer.getTeam()):
              CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN",(thisPlayer,"")), None, 2, None, ColorTypes(14), 0, 0, False, False)
            else:
              CyInterface().addMessage(self.iPAE_ShowMessagePlayerHumanID, True, 3, CyTranslator().getText("TXT_KEY_MESSAGE_PAE_CIV_TURN2",("",)), None, 2, None, ColorTypes(14), 0, 0, False, False)


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
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName == "FirstPunicWar":
      FirstPunicWar.onCombatResult(pWinner, pLoser)


# Weil bSuicide in XML scheinbar so funktioniert, dass auf jeden Fall der Gegner stirbt (was ich nicht will)
    if pWinner.getUnitType() == gc.getInfoTypeForString("UNIT_BURNING_PIGS"):
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
        PAE_Unit.doAIPlotFormations (pPlot, pLoser.getOwner())

# --------- Feature - Automated Unit Ranking via Promotions: Trained, Experienced, Seasoned, Veteran, Elite, Legendary
# ---- Trainiert, Kampferfahren, Routiniert, Veteran, Elite, Legende
    # Each promotion gives +x% Strength
    # Animal Attack brings only 1st Ranking

    if not bUnitDone and (pWinner.isMilitaryHappiness() or pWinner.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL")):
      PAE_Unit.doAutomatedRanking(pWinner, pLoser)


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
    bNavalUnit = False
    if pWinner.getDomainType() == DomainTypes.DOMAIN_SEA:
      bNavalUnit = True
      pWinner.changeMoves((pWinner.maxMoves()-pWinner.getMoves())/2)

########################################################
# ---- SEA: Schiffe sollen Treibgut erzeugen
# ---- LAND: Player can earn gold by winning a battle
    iCost = unitY.getProductionCost()

    # Ausnahmen
    UnitArray = [
    gc.getInfoTypeForString("UNIT_WORKBOAT"),
    gc.getInfoTypeForString("UNIT_TREIBGUT"),
    gc.getInfoTypeForString("UNIT_GAULOS"),
    gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN"),
    gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
    gc.getInfoTypeForString("UNIT_KAMPFHUND"),
    gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
    gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
    gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
    gc.getInfoTypeForString("UNIT_BURNING_PIGS"),
    gc.getInfoTypeForString("UNIT_HORSE"),
    gc.getInfoTypeForString("UNIT_CAMEL"),
    gc.getInfoTypeForString("UNIT_ELEFANT")
    ]

    AnimalArray = [
    gc.getInfoTypeForString("UNIT_WILD_HORSE"),
    gc.getInfoTypeForString("UNIT_WILD_CAMEL"),
    gc.getInfoTypeForString("UNIT_ELEFANT")
    ]

    WildAnimals = [
    gc.getInfoTypeForString("UNIT_LION"),
    gc.getInfoTypeForString("UNIT_BEAR"),
    gc.getInfoTypeForString("UNIT_PANTHER"),
    gc.getInfoTypeForString("UNIT_WOLF"),
    gc.getInfoTypeForString("UNIT_BOAR"),
    gc.getInfoTypeForString("UNIT_TIGER"),
    gc.getInfoTypeForString("UNIT_LEOPARD"),
    gc.getInfoTypeForString("UNIT_DEER"),
    gc.getInfoTypeForString("UNIT_UR"),
    gc.getInfoTypeForString("UNIT_BERGZIEGE")
    ]

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
    if pWinner.isMadeAttack() and pWinner.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL and pWinner.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
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



        # Attacks not against animals
        if pLoser.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL and pLoser.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
            pPlayer = gc.getPlayer(pWinner.getOwner())

            # PAE Feature 3: Unit Rang Promos (Unit Ranks, Unit Ranking)
            # ROM Pedes
            if pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_1")):
                if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_20")):
                    iNumPromos = gc.getNumPromotionInfos()-1
                    iPromo = iNumPromos
                    for iPromo in xrange(iNumPromos,0,-1):
                        iPromoType = gc.getPromotionInfo(iPromo).getType()
                        if "_TRAIT_" in iPromoType: break
                        if "_RANG_ROM_LATE" in iPromoType: continue
                        if "_RANG_ROM_EQUES" in iPromoType: continue
                        if "_RANG_ROM_" in iPromoType:
                            if pWinner.isHasPromotion(iPromo):
                                if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_5") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_9") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_14"):
                                    # Auxiliar nur bis Promo V
                                    if pWinner.getUnitType() != gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"):
                                       CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                                else:
                                    pWinner.setHasPromotion(iNewPromo, True)
                                    # Der Kommandant Eurer Einheit (%s1) hat nun den Rang: %s2!
                                    if pPlayer.isHuman():
                                        CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG",(pWinner.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                                break
                            else:
                                iNewPromo = iPromo
            # ROM Eques
            elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_1")):
                if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_5")):
                    # Chance: 1:4
                    if self.myRandom(4, None) == 1:
                        iNumPromos = gc.getNumPromotionInfos()-1
                        iPromo = iNumPromos
                        for iPromo in xrange(iNumPromos,0,-1):
                            iPromoType = gc.getPromotionInfo(iPromo).getType()
                            if "_TRAIT_" in iPromoType: break
                            if "_RANG_ROM_EQUES" in iPromoType:
                                if pWinner.isHasPromotion(iPromo):
                                    if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_3"):
                                        CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                                    else:
                                        pWinner.setHasPromotion(iNewPromo, True)
                                        # Der Kommandant Eurer Einheit (%s1) hat nun den Rang: %s2!
                                        if pPlayer.isHuman():
                                            CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG",(pWinner.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                                    break

                                else:
                                    iNewPromo = iPromo
            # ROM Late Antike
            elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_1")):
                if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_15")):
                    iNumPromos = gc.getNumPromotionInfos()-1
                    iPromo = iNumPromos
                    for iPromo in xrange(iNumPromos,0,-1):
                        iPromoType = gc.getPromotionInfo(iPromo).getType()
                        if "_TRAIT_" in iPromoType: break
                        if "_RANG_ROM_LATE" in iPromoType:
                            if pWinner.isHasPromotion(iPromo):
                                if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_5") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_10"):
                                    CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                                else:
                                    pWinner.setHasPromotion(iNewPromo, True)
                                    # Der Kommandant Eurer Einheit (%s1) hat nun den Rang eines %s2!
                                    if pPlayer.isHuman():
                                        CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG",(pWinner.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                                break

                            else:
                                iNewPromo = iPromo


            # Ab Kriegerethos
            if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_KRIEGERETHOS")):
                # Kelten, Germanen, Gallier, etc.
                lGermanen = [
                    gc.getInfoTypeForString("CIVILIZATION_GERMANEN"),
                    gc.getInfoTypeForString("CIVILIZATION_CELT"),
                    gc.getInfoTypeForString("CIVILIZATION_GALLIEN"),
                    gc.getInfoTypeForString("CIVILIZATION_DAKER"),
                    gc.getInfoTypeForString("CIVILIZATION_BRITEN"),
                    gc.getInfoTypeForString("CIVILIZATION_VANDALS")
                ]
                if pPlayer.getCivilizationType() in lGermanen:
                    if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_GER3")):
                        iRand = self.myRandom(10, None)
                        if iRand == 1:
                            iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER1")
                            if pWinner.isHasPromotion(iNewPromo): iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER2")
                            if pWinner.isHasPromotion(iNewPromo): iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER3")
                            pWinner.setHasPromotion(iNewPromo, True)
                            if pPlayer.isHuman():
                                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG",(pWinner.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                    else:
                        CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                # Hunnen
                if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HUNNEN"):
                    if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_HUN")):
                        iRand = self.myRandom(30, None)
                        if iRand == 1:
                            iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_HUN")
                            pWinner.setHasPromotion(iNewPromo, True)
                            if pPlayer.isHuman():
                                CyInterface().addMessage(pWinner.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG",(pWinner.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)

         # Ende Rang Promos ----------------
        # end if attacks not against animals
    # end if pWinner.isMadeAttack

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
            pWinner.kill(1,pWinner.getOwner())
            bUnitDone = True

# ------- Flucht / Escape

    # Flucht der Einheit / Escape of units --------
    # Defending unit only (inaktiv)
    # Nur wenn die Einheit nicht desertiert hat: bUnitDone
    #if not bUnitDone and not pLoser.isAttacking():
    # PAE V: defending units in cities gets flight (hiding behind walls) with max 70%. units kept on the city plot
    bUnitFlucht = False
    if not bUnitDone:

        # Eine einzelne kaperbare Unit darf nicht fluechten
        #if pLoser.getCaptureUnitType(pLoser.getOwner()) > -1 and gc.getMap().plot(pLoser.getX(), pLoser.getY()).getNumUnits() > 1:
        if pLoser.getCaptureUnitType(pLoser.getCivilizationType()) == -1:

          bIsCity = False
          pLoserPlot = gc.getMap().plot(pLoser.getX(), pLoser.getY())
          if pLoserPlot.isCity():
            iChance = pLoserPlot.getPlotCity().getPopulation()
            if iChance > 7: iChance = 7
            bIsCity = True
            iMaxHealth = 30 # max 30%
          else:
            iPromoFlucht1 = gc.getInfoTypeForString("PROMOTION_FLUCHT1")
            iPromoFlucht2 = gc.getInfoTypeForString("PROMOTION_FLUCHT2")
            iPromoFlucht3 = gc.getInfoTypeForString("PROMOTION_FLUCHT3")
            if pLoser.isHasPromotion(iPromoFlucht3):
              iChance = 8 # Flucht 3 - 80%
              iMaxHealth = 20 # max 20%
            elif pLoser.isHasPromotion(iPromoFlucht2):
              iChance = 6 # Flucht 2 - 60%
              iMaxHealth = 15 # max 15%
            elif pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
              bIsCity = True
              iChance = 5
              iMaxHealth = 12 # max 12%
            elif pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE") \
            or pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE_HILL"):
              bIsCity = True
              iChance = 5
              iMaxHealth = 10 # max 10%
            elif pLoser.isHasPromotion(iPromoFlucht1):
              iChance = 4 # Flucht 1 - 40%
              iMaxHealth = 10 # max 10%
            elif pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:
              if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 2:
                iChance = 8
                iMaxHealth = 50
              else:
                iChance = 3
                iMaxHealth = 25
            else:
              iChance = 2
              iMaxHealth = 5 # max 5%

          # Bei Schiffen eine Extra-Berechnung
          if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
              if pWinner.getDamage() >= 50:
                iChance = 10 # 100%: somit muss man womoeglich ein Schiff 2x angreifen, bevor es sinkt
                iMaxHealth = 20
              else:
                iChance += 1
                iMaxHealth += 5

          # Berittene nochmal +10%, except in cities -10%
          iCombatMounted = gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")
          if pLoser.getUnitCombatType() == iCombatMounted:
            if bIsCity: iChance -= 1
            else: iChance += 1

          iRand = 1+self.myRandom(10, None)

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Fluchtchance (Zeile 2924)",iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Max Health (Zeile 2925)",iMaxHealth)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          if iRand < iChance:

            # Create a new unit
            #pPlot = pLoser.plot()
            #if pPlot.getNumUnits() == 1: pLoser.jumpToNearestValidPlot()
            NewUnit = gc.getPlayer(pLoser.getOwner()).initUnit(pLoser.getUnitType(),  pLoser.getX(), pLoser.getY(), UnitAITypes(pLoser.getUnitAIType()), DirectionTypes.DIRECTION_SOUTH)
            if pLoser.isMadeAttack(): NewUnit.finishMoves()

            if pLoser.getUnitCombatType() != -1 or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:

             iRandHealth = 1+self.myRandom(iMaxHealth, None)

             NewUnit.setDamage(100-iRandHealth,-1) # Max Health
             NewUnit.setExperience(pLoser.getExperience(), -1)
             NewUnit.setLevel(pLoser.getLevel())

             # Check its promotions
             iRange = gc.getNumPromotionInfos()
             for iPromotion in range(iRange):
               # init all promotions the unit had
               if pLoser.isHasPromotion(iPromotion):
                 NewUnit.setHasPromotion(iPromotion, True)

            #if UnitName != "" and UnitName != NewUnit.getName(): NewUnit.setName(UnitName)
            UnitName = pLoser.getName()
            if UnitName != gc.getUnitInfo(pLoser.getUnitType()).getText():
               UnitName = re.sub(" \(.*?\)","",UnitName)
               NewUnit.setName(UnitName)


            if not bIsCity: NewUnit.jumpToNearestValidPlot()
            if gc.getPlayer(pLoser.getOwner()).isHuman():
              CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE",(NewUnit.getName(),0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            if gc.getPlayer(pWinner.getOwner()).isHuman():
              CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE_2",(NewUnit.getName(),0)), None, 2, None, ColorTypes(13), 0, 0, False, False)

            bUnitDone = True
            bUnitFlucht = True

            # if Unit was a leader (PROMOTION_LEADER)
            if pLoser.getLeaderUnitType() > -1:
              NewUnit.setLeaderUnitType(pLoser.getLeaderUnitType())
              pLoser.setLeaderUnitType(-1) # avoids ingame message "GG died in combat"

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Einheit fluechtet (Zeile 2774)",iChance)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# ---- Blessed Units
    # Blessed promo only helps one time
    iPromo = gc.getInfoTypeForString("PROMOTION_BLESSED")
    if pWinner.isHasPromotion(iPromo): pWinner.setHasPromotion(iPromo, False)
    if pLoser.isHasPromotion(iPromo): pLoser.setHasPromotion(iPromo, False)


# ---- Script DATAs in Units
    UnitText = CvUtil.getScriptData(pLoser, ["U", "t"])
    if not bUnitFlucht and UnitText != "":

       # Commissioned Mercenary  (MercFromCIV=CivID)
       if UnitText[:11] == "MercFromCIV":
          iMercenaryCiv = int(UnitText[12:])

          if not gc.getPlayer(pWinner.getOwner()).isHuman():
            # Ein minimaler Vorteil fuer die KI
            if pWinner.getOwner() != iMercenaryCiv:
              PAE_Mercenaries.doAIMercTorture(pWinner.getOwner(),iMercenaryCiv)
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


# ------- Feature 1: Held Promo + 3 XP wenn Stier (Ur) oder Tier mit mehr als 3 Level erlegt wird
# ---------------- nur wenn Einheit nicht schon ein Held ist
# ---------------- und wenn Combat ST Sieger < als Combat ST vom Gegner
# ---------------- iPromoHero wird oben (Generalsfeature) init
# ------- Feature 2: Ab Tech Kriegerethos bekommen Sieger + XP
    if not bUnitDone:
      if pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:
        if gc.getUnitInfo(pWinner.getUnitType()).getCombat() < gc.getUnitInfo(pLoser.getUnitType()).getCombat():
          if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 4:
            txtPopUpHero = ""

            if pLoser.getDamage() >= 100:
              if not pWinner.isHasPromotion(iPromoHero):
                 pWinner.setHasPromotion(iPromoHero, True)
                 pWinner.changeExperience(3, -1, 1, 0, 0)
                 if gc.getPlayer(pWinner.getOwner()).isHuman():
                   txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_5",(pWinner.getName(),pLoser.getName()))
                   CyInterface().addMessage(pWinner.getOwner(), True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)

            if txtPopUpHero != "":
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Text PopUp only!
              popupInfo.setText(txtPopUpHero)
              popupInfo.addPopup(pWinner.getOwner())
      else:
         # PAE Feature: Kriegerethos
         iTech = gc.getInfoTypeForString("TECH_KRIEGERETHOS")
         pWinnerPlayer = gc.getPlayer(pWinner.getOwner())
         pWinnerTeam = gc.getTeam(pWinnerPlayer.getTeam())
         if pWinnerTeam.isHasTech(iTech):
            iXP = 1
            if pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")) or pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")):
              iXP = 2
            pWinner.changeExperience(iXP, -1, 0, 0, 0)


# --------- Jagd - Feature ----------------------
# Ab Tech Jagd (Hunting) bringen Tiere Essen in nahegelegene Stadt
    bAnimal = False
    if not bUnitDone:
     if pWinner.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL and \
     ( pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitType() in AnimalArray ) and \
     pWinner.getUnitType() not in WildAnimals and pLoser.getUnitType() in WildAnimals:
      bAnimal = True
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
        PAE_Unit.doDyingGeneral(pLoser)

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
       PAE_Unit.doMobiliseFortifiedArmy(pCity.getOwner())

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
        PAE_City.doRenegadeCity(pCity, iWinner, pLoser.getID(), pWinner.getX(), pWinner.getY())

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


########################################################
# --------- if unit will renegade ----------------------
    bUnitRenegades = False
    if not bUnitDone and not bCityRenegade:
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
       elif pWinner.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE: bUnitRenegades = False
       elif pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE: bUnitRenegades = False
       elif pLoser.getUnitType() in UnitArray: bUnitRenegades = False
       elif pLoser.getUnitType() in AnimalArray: bUnitRenegades = False
       elif pWinner.getUnitType() in WildAnimals: bUnitRenegades = False
       elif pLoser.getUnitType() in WildAnimals: bUnitRenegades = False
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
      if iRand < iUnitRenegadeChance:
       # Winner gets Loser Unit
       if self.myRandom(3, None) == 0:

        # Piratenschiffe werden normale Schiffe
        iNewUnitType = pLoser.getUnitType()
        if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
          if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"): iNewUnitType = gc.getInfoTypeForString("UNIT_KONTERE")
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_BIREME"): iNewUnitType = gc.getInfoTypeForString("UNIT_BIREME")
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"): iNewUnitType = gc.getInfoTypeForString("UNIT_TRIREME")
          elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"): iNewUnitType = gc.getInfoTypeForString("UNIT_LIBURNE")

        # Create a new unit
        NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(iNewUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()

        if pLoser.getUnitCombatType() != -1:
          NewUnit.setDamage(90, -1)
          NewUnit.setExperience(pLoser.getExperience(), -1)
          NewUnit.setLevel(pLoser.getLevel())
          # Check its promotions
          iRange = gc.getNumPromotionInfos()
          for iPromotion in range(iRange):
            # init all promotions of the loser unit
            if pLoser.isHasPromotion(iPromotion):
              NewUnit.setHasPromotion(iPromotion, True)

          # PAE V: Loyal weg, Mercenary dazu
          if NewUnit.isHasPromotion(iPromoLoyal): NewUnit.setHasPromotion(iPromoLoyal, False)
          if not NewUnit.isHasPromotion(iPromoMercenary): NewUnit.setHasPromotion(iPromoMercenary, True)

          # Remove formations
          PAE_Unit.doUnitFormation (NewUnit, -1)

          # PAE V: Trait-Promotions
          # 1. Agg und Protect Promos weg
          # (2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten) Stimmt nicht, sie erhalten die Promo bei initUnit() sowieso
          if not gc.getPlayer(pWinner.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
            iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")
            if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)
         # if not gc.getPlayer(pWinner.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
         #   iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_PROTECTIVE")
         #   if NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, False)

        if gc.getPlayer(pWinner.getOwner()).isHuman():
          CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_DESERTION_1",(unitY.getDescription(),0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        elif gc.getPlayer(pLoser.getOwner()).isHuman():
          CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_DESERTION_2",(unitY.getDescription(),0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
        bUnitDone = True

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gewinner (" + str(pWinner.getOwner()) + ") bekommt Verlierer (" + str(pLoser.getOwner()) + ")",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


       # Winner gets Slave
       elif pWinner.getDomainType() == DomainTypes.DOMAIN_LAND:

        # Ausnahmen
        UnitArray = []
        UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))

        if pLoser.getUnitType() not in UnitArray:
          iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
          iThisTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
          team = gc.getTeam(iThisTeam)
          if team.isHasTech(iTechEnslavement):
            # Create a slave unit
            NewUnit = gc.getPlayer(pWinner.getOwner()).initUnit(gc.getInfoTypeForString("UNIT_SLAVE"),  pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.finishMoves()
            if gc.getPlayer(pWinner.getOwner()).isHuman():
              CyInterface().addMessage(pWinner.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_1",(unitY.getDescription(),0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
            elif gc.getPlayer(pLoser.getOwner()).isHuman():
              CyInterface().addMessage(pLoser.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_2",(unitY.getDescription(),0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
            bUnitDone = True

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gewinner bekommt Sklave (Zeile 2627)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# ------- End Unit renegades / desertiert -----------

# LOSER: Mounted -> Melee or Horse
# Nur wenn die Einheit nicht desertiert hat: bUnitDone
    if not bUnitDone and (pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED") or pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT")):

        bDoIt = False
        iNewUnitType = -1
        if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_FOEDERATI")
          bDoIt = True
        elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"):
          iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN")
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


# ------- Unit gets certain promotion PAE V Beta 2 Patch 7
# ------- pPlot is also used for improvment destruction below
    if pLoser.getUnitCombatType() != -1 and not bAnimal:
      if pWinner.isMadeAttack() and gc.getPlayer(pWinner.getOwner()).isTurnActive():
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pLoser.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        PAE_Unit.doUnitGetsPromo(pWinner,pLoser,pLoser.plot(),True)
      else:
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("pWinner.plot",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        PAE_Unit.doUnitGetsPromo(pWinner,pLoser,pWinner.plot(),False)

    if not bCityRenegade and bUnitFlucht:
      PAE_Unit.doUnitGetsPromo(pLoser,pWinner,pLoser.plot(),False)


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
      bFortress = False
      if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT") or iImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT2"):
        iChance = 2
        bFortress = True

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
       if gc.getPlayer(pWinner.getOwner()).canResearch(iTech, False):
          iCost = gc.getTechInfo(iTech).getResearchCost()
          iCost = iCost/10
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
    #if cdDefender.eOwner == cdDefender.eVisualOwner:
    #  szDefenderName = gc.getPlayer(cdDefender.eOwner).getNameKey()
    #else:
    #  szDefenderName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())
    #if cdAttacker.eOwner == cdAttacker.eVisualOwner:
    #  szAttackerName = gc.getPlayer(cdAttacker.eOwner).getNameKey()
    #else:
    #  szAttackerName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())
    #
    #if (iIsAttacker == 0):
    #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szDefenderName, cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
    #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #  if (cdDefender.iCurrHitPoints <= 0):
    #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szAttackerName, cdAttacker.sUnitName, szDefenderName, cdDefender.sUnitName))
    #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #elif (iIsAttacker == 1):
    #  combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szAttackerName, cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
    #  CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #  CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
    #  if (cdAttacker.iCurrHitPoints <= 0):
    #    combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szDefenderName, cdDefender.sUnitName, szAttackerName, cdAttacker.sUnitName))
    #    CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
    #    CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

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
      iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
      pCity.setNumRealBuilding(iBuilding,0)
      iBuilding = gc.getInfoTypeForString("BUILDING_PRAEFECTUR")
      pCity.setNumRealBuilding(iBuilding,0)
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
      terrain_swamp = gc.getInfoTypeForString('TERRAIN_SWAMP')
      terrain_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      for i in range(3):
        for j in range(3):
          loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
          if None != loopPlot and not loopPlot.isNone():
            if loopPlot.getTerrainType() == terrain_swamp:
              loopPlot = loopPlot.setTerrainType(terrain_grass,1,1)
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
      terr_swamp = gc.getInfoTypeForString('TERRAIN_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      bonus_grapes = gc.getInfoTypeForString('BONUS_GRAPES')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_FARM")
      iImpType5 = gc.getInfoTypeForString("IMPROVEMENT_MINE")
      iImpType6 = gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")

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
           if loopPlot.getTerrainType() != terr_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak():
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
      terr_swamp = gc.getInfoTypeForString('TERRAIN_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      iBonus = gc.getInfoTypeForString('BONUS_HORSE')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      #iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_WATERMILL")
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
            if loopPlot.getTerrainType() != terr_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

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
              #if loopPlot.getImprovementType() == iImpType4: PlotPrio8.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType5: PlotPrio9.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType6: PlotPrio10.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType7: PlotPrio11.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7
      #elif len(PlotPrio8) > 0: correctPlotArray = PlotPrio8
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

    # KAMEL - FEATURE ---------------------
    # Kamelverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_CAMEL_STABLE'):
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      iBonus = gc.getInfoTypeForString('BONUS_CAMEL')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CAMP")

      PlotPrio1 = []
      PlotPrio2 = []
      PlotPrio3 = []
      PlotPrio4 = []
      PlotPrio5 = []
      correctPlotArray = []
      bCityHasBonus = False

      for i in range(5):
        if bCityHasBonus: break
        for j in range(5):
          if i==0 and j==0 or i==4 and j==0 or i==0 and j==4 or i==4 and j==4: continue
          loopPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)

          # die beste position finden:
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isHills() or loopPlot.isPeak(): continue
            if loopPlot.isCity(): continue
            if loopPlot.getBonusType(loopPlot.getOwner()) == iBonus:
               bCityHasBonus = True
               break
            if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_desert) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

              # 1. nach Improvements selektieren
              if loopPlot.getImprovementType() == iImpType1: PlotPrio1.append(loopPlot)
              # 2. desert, unworked
              elif loopPlot.getTerrainType() == terr_desert and loopPlot.getImprovementType() == -1: PlotPrio2.append(loopPlot)
              # 3. plains, unworked
              elif loopPlot.getTerrainType() == terr_plain and loopPlot.getImprovementType() == -1: PlotPrio3.append(loopPlot)
              # 4. irgendeinen passenden ohne Improvement
              elif loopPlot.getImprovementType() == -1: PlotPrio4.append(loopPlot)
              else: PlotPrio5.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio4) > 0: correctPlotArray = PlotPrio4
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5

      # Bonus setzen
      if len(correctPlotArray) > 0 and not bCityHasBonus:
        iPlot = self.myRandom(len(correctPlotArray), None)
        sPlot = correctPlotArray[iPlot]
        # Feature (Wald) entfernen
        #sPlot.setFeatureType(-1,0)
        # Bonus adden
        sPlot.setBonusType(iBonus)
        # Improvement adden
        sPlot.setImprovementType(iImpType1)

    # KAMEL - FEATURE - ENDE ---------------------

    # ELEFANT - FEATURE ---------------------
    # Elefantverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_ELEPHANT_STABLE'):
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      feat_jungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
      feat_savanna = gc.getInfoTypeForString('FEATURE_SAVANNA')
      iBonus = gc.getInfoTypeForString('BONUS_IVORY')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CAMP")

      PlotPrio1 = []
      PlotPrio2 = []
      PlotPrio3 = []
      PlotPrio4 = []
      PlotPrio5 = []
      PlotPrio6 = []
      PlotPrio7 = []
      correctPlotArray = []
      bCityHasBonus = False

      for i in range(5):
        if bCityHasBonus: break
        for j in range(5):
          if i==0 and j==0 or i==4 and j==0 or i==0 and j==4 or i==4 and j==4: continue
          loopPlot = gc.getMap().plot(pCity.getX() + i - 2, pCity.getY() + j - 2)

          # die beste position finden:
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isHills() or loopPlot.isPeak(): continue
            if loopPlot.isCity(): continue
            if loopPlot.getBonusType(loopPlot.getOwner()) == iBonus:
               bCityHasBonus = True
               break
            if loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

              # 1. jungle, unworked
              if loopPlot.getFeatureType() == feat_jungle and loopPlot.getImprovementType() == -1: PlotPrio1.append(loopPlot)
              # 2. savanna, unworked
              elif loopPlot.getFeatureType() == feat_savanna and loopPlot.getImprovementType() == -1: PlotPrio2.append(loopPlot)
              # 3. nach Improvements selektieren
              elif loopPlot.getImprovementType() == iImpType1: PlotPrio3.append(loopPlot)
              # 4. grass, unworked
              elif loopPlot.getTerrainType() == terr_grass and loopPlot.getImprovementType() == -1: PlotPrio4.append(loopPlot)
              # 5. plains, unworked
              elif loopPlot.getTerrainType() == terr_plain and loopPlot.getImprovementType() == -1: PlotPrio5.append(loopPlot)
              # 6. irgendeinen passenden ohne Improvement
              elif loopPlot.getImprovementType() == -1: PlotPrio6.append(loopPlot)
              else: PlotPrio7.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio4) > 0: correctPlotArray = PlotPrio4
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7

      # Bonus setzen
      if len(correctPlotArray) > 0 and not bCityHasBonus:
        iPlot = self.myRandom(len(correctPlotArray), None)
        sPlot = correctPlotArray[iPlot]
        # Feature (Wald) entfernen
        #sPlot.setFeatureType(-1,0)
        # Bonus adden
        sPlot.setBonusType(iBonus)
        # Improvement adden
        sPlot.setImprovementType(iImpType1)

    # ELEFANT - FEATURE - ENDE ---------------------

    # HUNDE - FEATURE ---------------------
    # Hundeverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_HUNDEZUCHT'):
      terr_plain = gc.getInfoTypeForString('TERRAIN_PLAINS')
      terr_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
      terr_swamp = gc.getInfoTypeForString('TERRAIN_SWAMP')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      iBonus = gc.getInfoTypeForString('BONUS_HUNDE')

      # Improvements fuer Prioritaet
      iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS")
      iImpType2 = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
      iImpType3 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
      #iImpType4 = gc.getInfoTypeForString("IMPROVEMENT_WATERMILL")
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
            if loopPlot.getTerrainType() != terr_swamp and loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and (loopPlot.getTerrainType() == terr_plain or loopPlot.getTerrainType() == terr_grass) and (loopPlot.getOwner() == pCity.getOwner() or loopPlot.getOwner() == -1):

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
              #if loopPlot.getImprovementType() == iImpType4: PlotPrio8.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType5: PlotPrio9.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType6: PlotPrio10.append(loopPlot)
              if loopPlot.getImprovementType() == iImpType7: PlotPrio11.append(loopPlot)

      if len(PlotPrio1) > 0: correctPlotArray = PlotPrio1
      elif len(PlotPrio2) > 0: correctPlotArray = PlotPrio2
      elif len(PlotPrio3) > 0: correctPlotArray = PlotPrio3
      elif len(PlotPrio5) > 0: correctPlotArray = PlotPrio5
      elif len(PlotPrio6) > 0: correctPlotArray = PlotPrio6
      elif len(PlotPrio7) > 0: correctPlotArray = PlotPrio7
      #elif len(PlotPrio8) > 0: correctPlotArray = PlotPrio8
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

    # Wonder: 10 Gebote => adds 1 prophet and 10 jewish cities
    iBuilding = gc.getInfoTypeForString('BUILDING_10GEBOTE')
    if iBuildingType == iBuilding:
      pPlayer = gc.getPlayer(pCity.getOwner())
      iUnitType = gc.getInfoTypeForString("UNIT_PROPHET")
      NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_PROPHET, DirectionTypes.DIRECTION_SOUTH)
      NewUnit.setName("Moses")

      # converts up to 10 local cities to judaism (PAE V Patch 4)
      iReligion = gc.getInfoTypeForString("RELIGION_JUDAISM")
      Cities = []
      iNumCities = pPlayer.getNumCities()
      for i in range (iNumCities):
                   ThisCity = pPlayer.getCity(i)
                   if not ThisCity.isNone():
                     if not ThisCity.isHasReligion(iReligion):
                       Cities.append(ThisCity)

      a = 10
      iCities = len(Cities)
      if iCities < a: iAnz = iCities
      else: iAnz = a
      while iCities > 0 and a > 0:
        iRand = self.myRandom(iCities, None)
        Cities[iRand].setHasReligion(iReligion,1,1,0)
        Cities.pop(iRand)
        a -= 1
        iCities -= 1

      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_10GEBOTE",(iAnz,)), None, 2, None, ColorTypes(14), 0, 0, False, False)


      #iUnitType = gc.getInfoTypeForString("UNIT_JEWISH_MISSIONARY")
      #Names = ["Sarah","Abraham","Isaak","Jakob","Pinchas","Aaron","Miriam","Josua","Bileam","Jesaja"]
      #for i in range(10):
      #  NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
      #  NewUnit.setName(Names[i])

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

    # Project : Bibel / Bible
    if iProjectType == gc.getInfoTypeForString("PROJECT_BIBEL"):
      # converts up to 12 global cities to christianity (PAE V Patch 4)
      iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
      Cities = []
      iRangeMaxPlayers = gc.getMAX_PLAYERS()
      for iPlayer in range (iRangeMaxPlayers):
         ThisPlayer = gc.getPlayer(iPlayer)
         if iPlayer != gc.getBARBARIAN_PLAYER():
           if ThisPlayer.isAlive():
                 iNumCities = ThisPlayer.getNumCities()
                 for i in range (iNumCities):
                   ThisCity = ThisPlayer.getCity(i)
                   if not ThisCity.isNone():
                     if not ThisCity.isHasReligion(iReligion):
                       Cities.append(ThisCity)

      a = 12
      iCities = len(Cities)
      while iCities > 0 and a > 0:
        iRand = self.myRandom(iCities, None)
        pLoopCity = Cities.pop(iRand)
        pLoopCity.setHasReligion(iReligion,1,1,0)
        CyInterface().addMessage(pLoopCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_BIBEL",(pLoopCity.getName(),)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        a -= 1
        iCities -= 1

      # adds 12 christian missionaries (until PAE V Patch 3)
      #pPlayer = gc.getPlayer(pCity.getOwner())
      #iUnitType = gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY")
      #Names = ["Petrus","Andreas","Jakobus","Johannes","Philippus","Bartholomaeus","Thomas","Matthaeus","Jakobus","Thaddaeus","Simon","Judas"]
      #for i in range(12):
      #  NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
      #  NewUnit.setName(Names[i])

  def onSelectionGroupPushMission(self, argsList):
    'selection group mission'
    eOwner = argsList[0]
    eMission = argsList[1]
    iNumUnits = argsList[2]
    listUnitIds = argsList[3]

    # Handel (nur Meldung mit der gewonnenen Geldsumme)
    if eMission == MissionTypes.MISSION_TRADE:
      pUnit = gc.getPlayer(eOwner).getUnit(listUnitIds[0])
      pPlot = pUnit.plot()
      pCity = pPlot.getPlotCity()
      if pUnit.canMove():
        if gc.getPlayer(eOwner).isHuman():
          if eOwner == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
          iProfit = pUnit.getTradeGold(pPlot)
          CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_AUTOMATE_MERCHANT_DONE",(pCity.getName(),iProfit)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # Normaler Handel - Handelsstrasse bauen: Chance 2%
        if self.myRandom(100, None) < 2:
          scriptCityId = CvUtil.getScriptData(pUnit, ["c","t"])  # CityID
          if scriptCityId != "": pSource = gc.getPlayer(eOwner).getCity(int(scriptCityId)).plot()
          else: pSource = gc.getPlayer(eOwner).getCapitalCity().plot()
          pSourceCity = pSource.getPlotCity()
          pPlotTradeRoad = PAE_Trade.getPlotTradingRoad(pSource, pUnit.plot(), 0)
          if pPlotTradeRoad != None:
            pPlotTradeRoad.setRouteType(gc.getInfoTypeForString("ROUTE_TRADE_ROAD"))
            if gc.getPlayer(eOwner).isHuman():
              CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT",(gc.getPlayer(eOwner).getName(),gc.getPlayer(eOwner).getCivilizationShortDescriptionKey(),pCity.getName(),pSourceCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)



    # Fernangriff / Fernkampfkosten
    # Nur 1x Fernangriff danach nur bewegen => GlobalDefines RANGED_ATTACKS_USE_MOVES=0
    if eMission == MissionTypes.MISSION_RANGE_ATTACK:
      pPlayer = gc.getPlayer(eOwner)

      lSkirmishType = []
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_BALEAREN"))
      lSkirmishType.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"))
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
            if iUnitClass == gc.getInfoTypeForString("UNITCLASS_HUNTER"): iGold += 0
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_LIGHT_ARCHER"): iGold += 0
            elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_ARCHER"): iGold += 1
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_COMPOSITE_ARCHER") or iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_KRETA"): iGold += 2
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER") or iUnitClass == gc.getInfoTypeForString("UNITCLASS_ARCHER_LEGION"): iGold += 2
            elif iUnitType == gc.getInfoTypeForString("UNIT_INDIAN_LONGBOW") or iUnitType == gc.getInfoTypeForString("UNIT_LIBYAN_AMAZON"): iGold += 3
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_PELTIST") or iUnitType == gc.getInfoTypeForString("UNIT_BALEAREN"): iGold += 2
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_SKIRMISHER"): iGold += 2
            #elif iUnitType == gc.getInfoTypeForString("UNIT_THRAKIEN_PELTAST"): iGold += 2
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_CHARIOT_ARCHER") or iUnitType == gc.getInfoTypeForString("UNIT_HETHIT_WARCHARIOT"): iGold += 2
            #elif iUnitType == gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS") or iUnitType == gc.getInfoTypeForString("UNIT_BAKTRIEN"): iGold += 2
            #elif iUnitClass == gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER") or iUnitClass == gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER"): iGold += 2
            #elif iUnitType == gc.getInfoTypeForString("UNIT_BALLISTA"): iGold += 2
            elif iUnitCombat == gc.getInfoTypeForString("UNITCOMBAT_SIEGE"): iGold += 3
            elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_DECAREME"): iGold += 4
            else: iGold += 2

          if iGold > 0:
             pPlayer.changeGold(-iGold)
             CyInterface().addMessage(eOwner, True, 10, CyTranslator().getText("TXT_KEY_MISSION_RANGE_ATTACK_COSTS",(iGold,)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Ranged Attack - Owner",eOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      #(unit, iter) = pPlayer.firstUnit(False)
      #(unit, iter) = pPlayer.nextUnit(iter, False)


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

    # Trade (Boggy): If merchant moves from ship to land, land plot is saved as unloadedPlotX/Y
    # This has already become obsolete before publishing, I think.
##    eUnitType = pUnit.getUnitType()
##    if eUnitType in PAE_Trade.lTradeUnits and pUnit.getDomainType() == 2: # 2 = DOMAIN_LAND
##        if pOldPlot.isWater() and not pPlot.isWater(): # merchant has moved from water to land
##            CvUtil.addScriptData(pUnit, "unloadedPlotX", pPlot.getX())
##            CvUtil.addScriptData(pUnit, "unloadedPlotY", pPlot.getY())

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
# ----------- Beladene Schiffe sollen ebenfalls um 0.25 langsamer werden
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
      if iCargo > 0: pUnit.changeMoves(iCargo*10)

      # Workboats sink in unknown terrain (neutral or from other team): Chance 1:6
      if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_WORKBOAT"):
        if pPlot.getOwner() != pUnit.getOwner():
          if 1 == self.myRandom(6, None):
            if gc.getPlayer(pUnit.getOwner()).isHuman():
              CyInterface().addMessage(pUnit.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SINKING_SHIP",(pUnit.getName(),)), "AS2D_SINKING_W0RKBOAT", 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
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
          pUnit.kill(1,pUnit.getOwner())
          return
          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Leeres Seevoelkerschiff gekillt (Zeile 2456)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        else:
          if pOldPlot.getOwner() == -1 and pPlot.getOwner() > -1:
            if gc.getPlayer(pPlot.getOwner()).isHuman():
              CyInterface().addMessage(pPlot.getOwner(), True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_SEEVOLK_ALERT",()), None, 2, pUnit.getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

      # Barbarische Tiere sollen keine Stadt betreten / Barbarian animals will be disbanded when moving into a city
      if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL:
        if pPlot.isCity():
          pUnit.kill(1,pUnit.getOwner())

# --------------------------------------------------------------------- #


    # Handelskarren - Merchant can be robbed and killed
    if pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_TRADE_MERCHANT") and not pUnit.isBarbarian():
      if pPlot.getNumUnits() == 1 and pUnit.getOwner() != pPlot.getOwner() and not pPlot.isCity():

        barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
        iBarbCities = barbPlayer.getNumCities()
        # Chance in %
        iMinimumChance = 2
        if iBarbCities > 10: iChance = 4
        elif iBarbCities > 4: iChance = 3
        else: iChance = iMinimumChance

        iCalcChance = int(100/iChance)

        iRand = self.myRandom(iCalcChance, None)
        if iRand == 1:
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

          # Generelle Info zur Chance
          text = CyTranslator().getText("TXT_KEY_MESSAGE_MERCHANT_ROBBERY_INFO",(iChance,iMinimumChance))
          CyInterface().addMessage(iPlayer, True, 5, text, None, 2, None, ColorTypes(13), 0, 0, False, False)

          # PAE Trade: Einheit leeren
          CvUtil.removeScriptData(pUnit, "b")

          # Einheit killen
          #pUnit.kill(1,pUnit.getOwner())
          # Merchants gets barbarian: 50:50
          #if pPlot.getNumUnits() == 0:
          #  iRand = self.myRandom(2, None)
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
                  pUnit.kill(1,pUnit.getOwner())
              else:
                gc.getPlayer(iPlayer).changeGold(-100)
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
      #PAE_Unit.doUnitFormation (pUnit, -1)

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
            #PAE_Unit.doUnitFormation (pUnit, -1)

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
                  PAE_Unit.doUnitFormation (pUnit, iPromo)

      # Keine Formation in bestimmte Features
      #iFeat = pPlot.getFeatureType()
      #if iFeat > -1:
      #  if iFeat == gc.getInfoTypeForString("FEATURE_FOREST") or iFeat == gc.getInfoTypeForString("FEATURE_DICHTERWALD") or iFeat == gc.getInfoTypeForString("FEATURE_JUNGLE"):
      #    PAE_Unit.doUnitFormation (pUnit, -1)

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
    if not pPlayer.isHuman():

      # PAE V: Pirate feature - disabled cause of possible OOS when too many active AI pirates
      # if unit.getDomainType() == gc.getInfoTypeForString("DOMAIN_SEA"):
        # if self.myRandom(4, None) == 1:
            # if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PIRACY")):
                # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_KONTERE"):
                    # iUnitType = gc.getInfoTypeForString("UNIT_PIRAT_KONTERE")
                # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_BIREME"):
                    # iUnitType = gc.getInfoTypeForString("UNIT_PIRAT_BIREME")
                # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_TRIREME"):
                    # iUnitType = gc.getInfoTypeForString("UNIT_PIRAT_TRIREME")
                # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_LIBURNE"):
                    # iUnitType = gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE")
                # unit.kill(1,unit.getOwner())
                # unit = pPlayer.initUnit(iUnitType, city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

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
        PAE_Unit.doAIUnitFormations (unit, True, False, False)

      # Handicap: 0 (Settler) - 8 (Deity) ; 5 = King
      iHandicap = gc.getGame().getHandicapType()
      # -----------------------

      # 2nd Settler for AI (Immortal, Deity) (PAE V)
      if iHandicap >= 7 and unit.getUnitType() == gc.getInfoTypeForString("UNIT_SETTLER"):
        pPlayer.initUnit(unit.getUnitType(),  city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

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
        PAE_Unit.initSupply(unit)

    # ++++ Getreidekarren
    # if unit.getUnitType() == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"):
      # city.setFood(city.getFood()/2)

    # ++++ Auswanderer (Emigrants), die die Stadtbevoelkerung senken
    if unit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
      pPlot = city.plot()
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
      CvUtil.addScriptData(unit, "p", iPlayerCulture)
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

    # ++++ Bronze-Feature / Wald roden / Waldrodung / Abholzung / Desertifizierung / betrifft nicht die Barbarenstaedte
    if city.getOwner() != gc.getBARBARIAN_PLAYER():
        PAE_City.doDesertification(city, unit)
    # --------------------------------------------

    # PAE Provinzcheck
    if bCheckCityState:
        PAE_City.doCheckCityState(city)

    # PAE Unit Auto Promotions
    if gc.getUnitInfo(unit.getUnitType()).getCombat() > 0:
      if unit.getDomainType() == DomainTypes.DOMAIN_SEA:
            if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                PAE_Unit.doCityUnitPromotions4Ships(city,unit)
      else:
        PAE_Unit.doCityUnitPromotions(city,unit)
        # PAE Waffenmanufakturen - adds a second unit (PAE V Patch 4)
        if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"):
           if city.isHasBuilding(gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_SCHWERT")):
              pPlayer.initUnit(unit.getUnitType(), city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        elif unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"):
           if city.isHasBuilding(gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_AXT")):
              pPlayer.initUnit(unit.getUnitType(), city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        elif unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
           if city.isHasBuilding(gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_BOGEN")):
              pPlayer.initUnit(unit.getUnitType(), city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        elif unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN") or \
             unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
           if city.isHasBuilding(gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_SPEER")):
              pPlayer.initUnit(unit.getUnitType(), city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)


    # PAE V: Mercenary promotion
    if city.getOwner() != city.getOriginalOwner():
      if city.getPopulation() < 9:
        if city.plot().calculateCulturePercent(city.getOwner()) < 75:
          if unit.isMilitaryHappiness() or unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
             unit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY"), True)

    # Blessed Units
    iBuilding = gc.getInfoTypeForString("BUILDING_CHRISTIAN_CATHEDRAL")
    if city.isHasBuilding(iBuilding):
      # Chance: 25% a unit gets blessed
      if self.myRandom(4, None) == 1:
        unit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_BLESSED"), True)

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
    CvUtil.pyPrint(u'Player %d Civilization %s Unit %s was killed by Player %d'
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
        lSupplyBonus = {
            gc.getInfoTypeForString("IMPROVEMENT_FARM"): 50,
            gc.getInfoTypeForString("IMPROVEMENT_PASTURE"): 50,
            gc.getInfoTypeForString("IMPROVEMENT_PLANTATION"): 30,
            gc.getInfoTypeForString("IMPROVEMENT_BRUNNEN"): 20,
            gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"): 10,
            gc.getInfoTypeForString("IMPROVEMENT_HAMLET"): 15,
            gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"): 20,
            gc.getInfoTypeForString("IMPROVEMENT_TOWN"): 25,
            gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"): 25,
            gc.getInfoTypeForString("IMPROVEMENT_FORT"): 30,
            gc.getInfoTypeForString("IMPROVEMENT_FORT2"): 40
        }

        iSupplyChange = lSupplyBonus.get(iImprovement, 0)
        for loopUnit in lHealer:
            if iSupplyChange <= 0: break
            iSupplyChange = PAE_Unit.fillSupply(pUnit, iSupplyChange)

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
        PAE_Sklaven.doCheckSlavesAfterPillage(pUnit,pPlot)

      # Handelsposten: Plot-ScriptData leeren
      if iImprovement == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):
        CvUtil.removeScriptData(pPlot, "p")

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

    # ----------------------------------
    # Trait Creative: Bei Alphabet in jede Stadt Trait-Gebaeude setzen
    if iTechType == gc.getInfoTypeForString("TECH_ALPHABET") and gc.getPlayer(iPlayer).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")) and iPlayer > -1:
      lCities = PyPlayer(iPlayer).getCityList()
      pPlayer = gc.getPlayer(iPlayer)
      iRangeCities = len(lCities)
      iBuilding = gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_LOCAL")
      for iCity in range(iRangeCities):
        pCity = pPlayer.getCity(lCities[iCity].getID())
        pCity.setNumRealBuilding(iBuilding, 1)
    #-----------------------------

    # freier Siedler fuer die KI ab Emperor
    if iPlayer > -1 and gc.getGame().getHandicapType() > 5:
      iUnit = -1
      pPlayer = gc.getPlayer(iPlayer)
      if not pPlayer.isHuman():
          if iTechType == gc.getInfoTypeForString("TECH_GEOMETRIE"): iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_SCHIFFSBAU"): iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_DUALISMUS"):  iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_CELTIC"): iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_NORDIC"): iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_COLONIZATION2"):
              if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ASSYRIA") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_LYDIA") \
              or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA") or pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
                 iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_RELIGION_ROME"): iUnit = gc.getInfoTypeForString("UNIT_SETTLER")
          elif iTechType == gc.getInfoTypeForString("TECH_PERSIAN_ROAD"):  iUnit = gc.getInfoTypeForString("UNIT_SETTLER")

      # Einheit erstellen
      if iUnit > -1:
        #pPlayer = gc.getPlayer(iPlayer)
        pCapital = pPlayer.getCapitalCity()
        if pCapital != None and not pCapital.isNone():
          iX = pCapital.getX()
          iY = pCapital.getY()
          NewUnit = pPlayer.initUnit(iUnit, iX, iY, UnitAITypes.UNITAI_SETTLE, DirectionTypes.DIRECTION_SOUTH)

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
      elif iTechType == gc.getInfoTypeForString("TECH_MANUFAKTUREN"): iUnit = gc.getInfoTypeForString("UNIT_EXECUTIVE_3")
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
    #if iPlayer > -1 and iTechType == gc.getInfoTypeForString("TECH_HERESY"):
    """
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
    """
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

    # Clear cult headquarter
    CyGame().clearHeadquarters(iCorporation)

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
        PAE_City.doNextCityRevolt(pCity.getX(), pCity.getY(), iOwner, iPlayer)

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
    pPlot = pCity.plot()

    # PAE Debug Mark
    #"""

    # Trait-Gebaeude anpassen
    PAE_City.doCheckTraitBuildings(pCity)
    PAE_City.doCheckGlobalTraitBuildings(iNewOwner, pCity, iPreviousOwner)

    # Assimilation Tech (PAE V Patch 4)
    bAssimilation = gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ASSIMILATION"))

    # Szenarien
    sScenarioName = CvUtil.getScriptData(CyMap().plot(0, 0), ["S","t"])
    if sScenarioName == "FirstPunicWar":
        FirstPunicWar.onCityAcquired(pCity, iNewOwner)


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
      # Nicht bei Szenarien verwenden (sScenarioName wird ganz oben initialisiert)
      if NewCityName == "" and sScenarioName == "":
         pCity.setName(gc.getPlayer(iNewOwner).getNewCityName(),0)
# ---------------

# Provinzpalast und Praefectur muss raus, Bischofssitz kann bleiben
    iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
    if pCity.isHasBuilding(iBuilding): pCity.setNumRealBuilding(iBuilding,0)
    iBuilding = gc.getInfoTypeForString("BUILDING_PRAEFECTUR")
    if pCity.isHasBuilding(iBuilding): pCity.setNumRealBuilding(iBuilding,0)

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
      if not pCity.isHasBuilding(iBuildingPalisade): pCity.setNumRealBuilding(iBuildingPalisade,1)

# Spezialgebaeude muessen raus, weil nicht die Building_X erobert werden, sondern die BuildingClass_X !!!
    for i in range(9):
     iBuilding = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_SPECIAL"+str(i+1)))
     if iBuilding != None and iBuilding != -1:
       if pCity.isHasBuilding(iBuilding):
         pCity.setNumRealBuilding(iBuilding,0)

# ------- Create partisans and slaves, catch great people (only during active war), nearest city riots
    if gc.getTeam(gc.getPlayer(iPreviousOwner).getTeam()).isAtWar(gc.getPlayer(iNewOwner).getTeam()):

# --- Partisans!
      if not bAssimilation and (not bTrade or bConquest) and not gc.getPlayer(iNewOwner).isBarbarian() and gc.getPlayer(iPreviousOwner).isAlive():
        # Seek Plots
        rebelPlotArray = []
        PartisanPlot1 = []
        PartisanPlot2 = []
        iRange = 1
        iX = pCity.getX()
        iY = pCity.getY()
        for i in range(-iRange, iRange+1):
            for j in range(-iRange, iRange+1):
                loopPlot = plotXY(iX, iY, i, j)
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
      if not bAssimilation:
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
      if bAssimilation:
        iCitySlaves = 0
        iCityGlads = 0
      else:
        iCitySlaves = pCity.getFreeSpecialistCount(16) + pCity.getFreeSpecialistCount(17) + pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE = 16,17,18
        iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 15

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
      if bAssimilation:
        iCityGP1 = 0
        iCityGP2 = 0
        iCityGP3 = 0
        iCityGP4 = 0
        iCityGP5 = 0
        iCityGP6 = 0
        iCityGP7 = 0
      else:
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

# --- Great People Catch end --


# --- Nearest city revolts 33% chance
#       CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Conquest",int(bConquest))), None, 2, None, ColorTypes(10), 0, 0, False, False)
#      CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Trade",int(bTrade))), None, 2, None, ColorTypes(10), 0, 0, False, False)

      if bConquest and iPreviousOwner != gc.getBARBARIAN_PLAYER() and gc.getPlayer(iPreviousOwner).isAlive():
        iRand = self.myRandom(3, None)
        if iRand == 1:
          PAE_City.doNextCityRevolt(pCity.getX(), pCity.getY(), iPreviousOwner, iNewOwner)
# ---- nearest city revolts end --

# --- Getting Technology when conquering (Forschungsbonus)
# --- PAE V Patch4: nur ab Pop 3 (sonst exploit)
      if bConquest and (bAssimilation or pCity.getPopulation() > 2):
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
# --- PAE V Patch4: ab Pop 3 (sonst exploit)
# --- Kein Goldkarren bei Assimilierung
      if not bAssimilation and pCity.getPopulation() > 2:
        iBeute = int(pCity.getPopulation() / 2)
        if iBeute > 0:
          for i in range (iBeute):
            gc.getPlayer(iNewOwner).initUnit(gc.getInfoTypeForString('UNIT_GOLDKARREN'),  pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Beutegold erhalten (Zeile 3475)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# --- Bevoelkerungszuwachs bei Nachbarstaedten (50% Chance pro Stadt fuer + 1 Pop)
# --- PAE V Patch4: ab Pop 3 (sonst exploit)
      if not bAssimilation and pCity.getPopulation() > 2:
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
                  PAE_City.doCheckCityState(loopCity)

                  # ***TEST***
                  #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtpop gewachsen durch Krieg (Zeile 3493)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

      # PAE Provinzcheck
      PAE_City.doCheckCityState(pCity)

      # set city slaves to null
      if not bAssimilation and not bTrade:
        PAE_Sklaven.doEnslaveCity(pCity)

      # Ab Tech Assimilation soll die Stadtpop mind. 5 sein (PAE V Patch 4)
      if bAssimilation and pCity.getPopulation() < 5: pCity.setPopulation(5)

    # --- Vasallen-Feature / Vassal feature
      # iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
      if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES) and gc.getPlayer(iPreviousOwner).isAlive():
        PAE_Vassal.onCityAcquired(pCity, iNewOwner, iPreviousOwner)


      # PAE Debug Mark
      #"""


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
    PAE_City.doCheckGlobalTraitBuildings(city.getOwner())
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
    PAE_City.doCheckCityState(pCity)
    # ----------------------------

    # Negatives Nahrungslager durch Stadtstatusgebaeude vermeiden (Flunky)
    if pCity.getFood() < 0: pCity.setFood(0)

    # ***TEST***
    #


  def onCityDoTurn(self, argsList):
    'City Production'
    pCity = argsList[0]
    iPlayer = argsList[1]

    pPlayer = gc.getPlayer(iPlayer)
    iTeam = pPlayer.getTeam()
    pTeam = gc.getTeam(iTeam)
    pCityPlot = pCity.plot()
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

    # ++++++++++++++++++++++++++++++++++++++++
    # Buildings with prereq bonus gets checked : remove chance 10%
    building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_BRONZE")
    if pCity.isHasBuilding(building):
      iRand = self.myRandom(10, None)
      if iRand == 1:
        bonus = gc.getInfoTypeForString("BONUS_COPPER")
        bonus1 = gc.getInfoTypeForString("BONUS_COAL")
        bonus2 = gc.getInfoTypeForString("BONUS_ZINN")
        if not pCity.hasBonus(bonus) or not (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2)):
          pCity.setNumRealBuilding(building,0)
          # Welche Resi
          if not pCity.hasBonus(bonus): szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1"
          else: szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_2"
          # Meldung
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText(szText,(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText(szText,(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            popupInfo.addPopup(pCity.getOwner())

    building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_MESSING")
    if pCity.isHasBuilding(building):
      iRand = self.myRandom(10, None)
      if iRand == 1:
        bonus1 = gc.getInfoTypeForString("BONUS_COPPER")
        bonus2 = gc.getInfoTypeForString("BONUS_ZINK")
        if not pCity.hasBonus(bonus1) or not pCity.hasBonus(bonus2):
          pCity.setNumRealBuilding(building,0)
          # Welche Resi
          if not pCity.hasBonus(bonus1): bonus = bonus1
          elif not pCity.hasBonus(bonus2): bonus = bonus2
          # Meldung
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            popupInfo.addPopup(pCity.getOwner())

    building = gc.getInfoTypeForString("BUILDING_BRAUSTAETTE")
    if pCity.isHasBuilding(building):
      iRand = self.myRandom(10, None)
      if iRand == 1:
        bonus1 = gc.getInfoTypeForString("BONUS_WHEAT")
        bonus2 = gc.getInfoTypeForString("BONUS_GERSTE")
        bonus3 = gc.getInfoTypeForString("BONUS_HAFER")
        bonus4 = gc.getInfoTypeForString("BONUS_ROGGEN")
        bonus5 = gc.getInfoTypeForString("BONUS_HIRSE")
        if not (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2) or pCity.hasBonus(bonus3) or pCity.hasBonus(bonus4) or pCity.hasBonus(bonus5)):
          pCity.setNumRealBuilding(building,0)
          # Meldung
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3",(pCity.getName(),"",gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3",(pCity.getName(),"",gc.getBuildingInfo(building).getDescription())))
            popupInfo.addPopup(pCity.getOwner())

    building = gc.getInfoTypeForString("BUILDING_WINERY")
    if pCity.isHasBuilding(building):
      iRand = self.myRandom(10, None)
      if iRand == 1:
        bonus = gc.getInfoTypeForString("BONUS_GRAPES")
        if not pCity.hasBonus(bonus):
          pCity.setNumRealBuilding(building,0)
          # Meldung
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            popupInfo.addPopup(pCity.getOwner())

    building = gc.getInfoTypeForString("BUILDING_PAPYRUSPOST")
    if pCity.isHasBuilding(building):
      iRand = self.myRandom(10, None)
      if iRand == 1:
        bonus = gc.getInfoTypeForString("BONUS_PAPYRUS")
        if not pCity.hasBonus(bonus):
          pCity.setNumRealBuilding(building,0)
          # Meldung
          if pPlayer.isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1",(pCity.getName(),gc.getBonusInfo(bonus).getDescription(),gc.getBuildingInfo(building).getDescription())))
            popupInfo.addPopup(pCity.getOwner())

    # ++++++++++++++++++++++++++++++++++++++++


    # Emigrants leave city when unhappy / Auswanderer verlassen die Stadt, wenn unzufrieden
    iTech = gc.getInfoTypeForString("TECH_COLONIZATION")
    if pTeam.isHasTech(iTech) and popCity > 3:
      iCityUnhappy = pCity.unhappyLevel(0) - pCity.happyLevel()
      iCityUnhealthy = pCity.badHealth(False) - pCity.goodHealth()
      if iCityUnhappy > 0 or iCityUnhealthy > 0:
        if iCityUnhappy < 0: iCityUnhappy = 0
        if iCityUnhealthy < 0: iCityUnhealthy = 0
        iChance = (iCityUnhappy + iCityUnhealthy) * 4 # * popCity
        iRand = self.myRandom(100, None)
        if iChance > iRand:
          iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
          NewUnit = gc.getPlayer(iPlayer).initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_SETTLE, DirectionTypes.DIRECTION_SOUTH)

          # Einheit die richtige Kultur geben
          iPlayerCulture = pCity.findHighestCulture()
          if iPlayerCulture == -1 or iPlayerCulture == "NO_PLAYER": iPlayerCulture = pCity.getOwner()
          CvUtil.addScriptData(NewUnit, "p", iPlayerCulture)
          # Kultur von der Stadt abziehen
          iCulture = pCity.getCulture(iPlayerCulture)
          pCity.changeCulture(iPlayerCulture,-(iCulture/5),1)

          popNeu = popCity - 2
          if popNeu < 1: popNeu = 1

          pCity.setPopulation(popNeu)
          PAE_City.doCheckCityState(pCity)

          if iPlayer > -1:
            if pPlayer.isHuman():
              if iCityUnhealthy > 0: text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_2",(pCity.getName(),popNeu,popCity))
              else: text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS",(pCity.getName(),popNeu,popCity))
              CyInterface().addMessage(pCity.getOwner(), True, 10, text,"AS2D_REVOLTSTART",InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Techs/button_brandschatzen.dds",ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
            else:
              PAE_Sklaven.doAIReleaseSlaves(pCity)
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

          if not pPlayer.isHuman(): PAE_Sklaven.doAIReleaseSlaves(pCity)

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
      # Prio: Haus (min 1 bleibt), Food, Glads, Prod
      iSlaves = iCityGlads + iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
      while iSlaves > 0 and iPopChange > 0:
        if iCitySlavesHaus > 1:
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
          sPlot = plotXY(pCity.getX(), pCity.getY(), i, j)
          iRange = sPlot.getNumUnits()
          for iUnit in range (iRange):
            iRand = self.myRandom(30, None) + 15
            pLoopUnit = sPlot.getUnit(iUnit)
            if pLoopUnit != None:
              if pLoopUnit.getDamage() + iRand < 100: pLoopUnit.changeDamage(iRand, False)

              sOwner = pLoopUnit.getOwner()

              if pLoopUnit.getDamage() > 95:
                if gc.getPlayer(sOwner) != None:
                  if gc.getPlayer(sOwner).isHuman():
                    CyInterface().addMessage(sOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_KILL_UNIT",(pLoopUnit.getName(), pCity.getName() )), None, 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(12), sPlot.getX(), sPlot.getY(), True, True)
                pLoopUnit.kill(1,pLoopUnit.getOwner())

              if gc.getPlayer(sOwner) != None and gc.getPlayer(sOwner).isHuman():
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
      if iRand == 1: PAE_City.doSpreadPlague(pCity)
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
        if not pOwner.isHuman(): iChance += 10

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
              pLoopUnit = pCityPlot.getUnit(iUnit)
              if pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                 pLoopUnit.kill(1,pLoopUnit.getOwner())
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
      iRel = pPlayer.getStateReligion()
      if iRel != -1:
       if not pCity.isHasReligion(iRel):
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
              PAE_City.doCityRevolt (pCity,iCityRevoltTurns)

          else:
            #pCity.setOccupationTimer(iCityRevoltTurns)
            PAE_City.doCityRevolt (pCity,iCityRevoltTurns)

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
              # nach einer bestehenden ISRAEL ID suchen
              for i in range(iRangeMaxPlayers):
                loopPlayer = gc.getPlayer(i)
                if loopPlayer.getCivilizationType() == CivIsrael and loopPlayer.isEverAlive():
                  iCivID = i
                  break
              # freie PlayerID herausfinden
              if iCivID == -1:
                for i in range(iRangeMaxPlayers):
                  loopPlayer = gc.getPlayer(i)
                  if not loopPlayer.isEverAlive():
                    iCivID = i
                    break
              # wenn keine nagelneue ID frei ist, dann eine bestehende nehmen
              if iCivID == -1:
                for i in range(iRangeMaxPlayers):
                  loopPlayer = gc.getPlayer(i)
                  if not loopPlayer.isAlive():
                    iCivID = i
                    break

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
            PAE_City.doCityRevolt (pCity, pCity.getPopulation() / 2)

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
      if not gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString('TECH_POLYARCHY')) and self.myRandom(50, None) < 1:

          iGold = pPlayer.getGold()

          iTribut = pCity.getPopulation() * 10 + self.myRandom(pCity.getPopulation()*10/2, None)
          iTribut2 = iTribut / 2

          iBuildingHappiness = pCity.getBuildingHappiness(iBuilding)

          # Human PopUp
          if gc.getPlayer(iPlayer).isHuman():
              iRand = self.myRandom(11, None)
              szText = CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_DEMAND_"+str(iRand),(pCity.getName(),iTribut))
              szText += localText.getText("[NEWLINE][NEWLINE]", ()) + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG",())
              szText += u": %d " % (abs(iBuildingHappiness))
              if iBuildingHappiness < 0: szText += localText.getText("[ICON_UNHAPPY]", ())
              else: szText += localText.getText("[ICON_HAPPY]", ())

              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
              popupInfo.setText(szText)
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


            if bDoRebellion == True: PAE_City.doProvinceRebellion(pCity)
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
    if not bRevolt and gc.getGame().getGameTurnYear() > 0 and gc.getGame().getGameTurn() % 5 == 0:
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
            elif pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")):
              if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")): iChance = 30 # 3%
              else: iChance = 50 # 2%
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
          if self.myRandom(10, None) == 1: # 10%

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

    # PAE Provinzcheck
    if bCheckCityState:
      PAE_City.doCheckCityState(pCity)

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
    PAE_City.doCheckCityState(pCity)
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