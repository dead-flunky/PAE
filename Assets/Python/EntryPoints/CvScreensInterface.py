## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
import CvMainInterface
import CvDomesticAdvisor
import CvTechChooser
#import CvForeignAdvisor
import CvExoticForeignAdvisor
import CvMilitaryAdvisor
import CvFinanceAdvisor
import CvReligionScreen
import CvCorporationScreen
import CvCivicsScreen
import CvVictoryScreen
import CvEspionageAdvisor
import CvTradeRouteAdvisor

import CvOptionsScreen
import CvReplayScreen
import CvHallOfFameScreen
import CvDanQuayle
import CvUnVictoryScreen

import CvDawnOfMan
import CvTechSplashScreen
import CvTopCivs
import CvInfoScreen

import CvIntroMovieScreen
import CvVictoryMovieScreen
import CvWonderMovieScreen
import CvEraMovieScreen
import CvSpaceShipScreen

import CvPediaMain
import CvPediaHistory

#import CvWorldBuilderScreen
#import CvWorldBuilderDiplomacyScreen

import CvDebugTools
import CvDebugInfoScreen
#import CvDiplomacy

import CvUtil
import CvEventInterface
import CvPopupInterface
import CvScreenUtilsInterface
import ScreenInput as PyScreenInput
import random
from CvScreenEnums import *
from CvPythonExtensions import *

import PAE_Trade
import PAE_Unit

gc = CyGlobalContext()

g_bIsScreenActive = -1

## World Builder ##
import CvPlatyBuilderScreen
import WBPlotScreen
import WBRiverScreen
import WBEventScreen
import WBBuildingScreen
import WBCityDataScreen
import WBCityEditScreen
import WBTechScreen
import WBProjectScreen
import WBTeamScreen
import WBPlayerScreen
import WBUnitScreen
import WBPromotionScreen
import WBDiplomacyScreen
import WBGameDataScreen
import WBPlayerUnits
import WBReligionScreen
import WBCorporationScreen
import WBInfoScreen
import WBTradeScreen

def toggleSetNoScreens():
        global g_bIsScreenActive
        print "SCREEN OFF"
        g_bIsScreenActive = -1

def toggleSetScreenOn(argsList):
        global g_bIsScreenActive
        print "%s SCREEN TURNED ON" %(argsList[0],)
        g_bIsScreenActive = argsList[0]

#diplomacyScreen = CvDiplomacy.CvDiplomacy()

mainInterface = CvMainInterface.CvMainInterface()
def showMainInterface():
        mainInterface.interfaceScreen()

def numPlotListButtons():
        return mainInterface.numPlotListButtons()

techChooser = CvTechChooser.CvTechChooser()
def showTechChooser():
        if CyGame().getActivePlayer() > -1:
                techChooser.interfaceScreen()

hallOfFameScreen = CvHallOfFameScreen.CvHallOfFameScreen(HALL_OF_FAME)
def showHallOfFame(argsList):
        hallOfFameScreen.interfaceScreen(argsList[0])

civicScreen = CvCivicsScreen.CvCivicsScreen()
def showCivicsScreen():
        if CyGame().getActivePlayer() > -1:
                civicScreen.interfaceScreen()

religionScreen = CvReligionScreen.CvReligionScreen()
def showReligionScreen():
        if CyGame().getActivePlayer() > -1:
                religionScreen.interfaceScreen()

corporationScreen = CvCorporationScreen.CvCorporationScreen()
def showCorporationScreen():
        if CyGame().getActivePlayer() > -1:
                corporationScreen.interfaceScreen()

optionsScreen = CvOptionsScreen.CvOptionsScreen()
def showOptionsScreen():
        optionsScreen.interfaceScreen()

#foreignAdvisor = CvForeignAdvisor.CvForeignAdvisor()
foreignAdvisor = CvExoticForeignAdvisor.CvExoticForeignAdvisor()
def showForeignAdvisorScreen(argsList):
        if CyGame().getActivePlayer() > -1:
                foreignAdvisor.interfaceScreen(argsList[0])

financeAdvisor = CvFinanceAdvisor.CvFinanceAdvisor()
def showFinanceAdvisor():
        if CyGame().getActivePlayer() > -1:
                financeAdvisor.interfaceScreen()

domesticAdvisor = CvDomesticAdvisor.CvDomesticAdvisor()
def showDomesticAdvisor(argsList):
        if CyGame().getActivePlayer() > -1:
                domesticAdvisor.interfaceScreen()

traderouteAdvisor = CvTradeRouteAdvisor.CvTradeRouteAdvisor()
def showTradeRouteAdvisor(argsList):
        if CyGame().getActivePlayer() > -1:
                traderouteAdvisor.interfaceScreen()

militaryAdvisor = CvMilitaryAdvisor.CvMilitaryAdvisor(MILITARY_ADVISOR)
def showMilitaryAdvisor():
        if CyGame().getActivePlayer() > -1:
                militaryAdvisor.interfaceScreen()

espionageAdvisor = CvEspionageAdvisor.CvEspionageAdvisor()
def showEspionageAdvisor():
        if CyGame().getActivePlayer() > -1:
                espionageAdvisor.interfaceScreen()

dawnOfMan = CvDawnOfMan.CvDawnOfMan(DAWN_OF_MAN)
def showDawnOfMan(argsList):
        dawnOfMan.interfaceScreen()

introMovie = CvIntroMovieScreen.CvIntroMovieScreen()
def showIntroMovie(argsList):
        introMovie.interfaceScreen()

victoryMovie = CvVictoryMovieScreen.CvVictoryMovieScreen()
def showVictoryMovie(argsList):
        victoryMovie.interfaceScreen(argsList[0])

wonderMovie = CvWonderMovieScreen.CvWonderMovieScreen()
def showWonderMovie(argsList):
        wonderMovie.interfaceScreen(argsList[0], argsList[1], argsList[2])

eraMovie = CvEraMovieScreen.CvEraMovieScreen()
def showEraMovie(argsList):
        eraMovie.interfaceScreen(argsList[0])

spaceShip = CvSpaceShipScreen.CvSpaceShipScreen()
def showSpaceShip(argsList):
        if CyGame().getActivePlayer() > -1:
                spaceShip.interfaceScreen(argsList[0])

replayScreen = CvReplayScreen.CvReplayScreen(REPLAY_SCREEN)
def showReplay(argsList):
        if argsList[0] > -1:
                CyGame().saveReplay(argsList[0])
        replayScreen.showScreen(argsList[4])

danQuayleScreen = CvDanQuayle.CvDanQuayle()
def showDanQuayleScreen(argsList):
        danQuayleScreen.interfaceScreen()

unVictoryScreen = CvUnVictoryScreen.CvUnVictoryScreen()
def showUnVictoryScreen(argsList):
        unVictoryScreen.interfaceScreen()

topCivs = CvTopCivs.CvTopCivs()
def showTopCivs():
        topCivs.showScreen()

infoScreen = CvInfoScreen.CvInfoScreen(INFO_SCREEN)
def showInfoScreen(argsList):
        if CyGame().getActivePlayer() > -1:
                iTabID = argsList[0]
                iEndGame = argsList[1]
                infoScreen.showScreen(-1, iTabID, iEndGame)

debugInfoScreen = CvDebugInfoScreen.CvDebugInfoScreen()
def showDebugInfoScreen():
        debugInfoScreen.interfaceScreen()

techSplashScreen = CvTechSplashScreen.CvTechSplashScreen(TECH_SPLASH)
def showTechSplash(argsList):
        techSplashScreen.interfaceScreen(argsList[0])

victoryScreen = CvVictoryScreen.CvVictoryScreen(VICTORY_SCREEN)
def showVictoryScreen():
        if CyGame().getActivePlayer() > -1:
           victoryScreen.interfaceScreen()

#################################################
## Civilopedia
#################################################
pediaMainScreen = CvPediaMain.CvPediaMain()
def linkToPedia(argsList):
        pediaMainScreen.link(argsList[0])

def pediaShow():
        return pediaMainScreen.pediaShow()

def pediaBack():
        return pediaMainScreen.back()

def pediaForward():
        pediaMainScreen.forward()

def pediaMain(argsList):
        pediaMainScreen.pediaJump(PEDIA_MAIN, argsList[0], True)

def pediaJumpToTech(argsList):
        pediaMainScreen.pediaJump(PEDIA_TECH, argsList[0], True)

def pediaJumpToUnit(argsList):
        pediaMainScreen.pediaJump(PEDIA_UNIT, argsList[0], True)

def pediaJumpToBuilding(argsList):
        pediaMainScreen.pediaJump(PEDIA_BUILDING, argsList[0], True)

def pediaJumpToProject(argsList):
        pediaMainScreen.pediaJump(PEDIA_PROJECT, argsList[0], True)

def pediaJumpToReligion(argsList):
        pediaMainScreen.pediaJump(PEDIA_RELIGION, argsList[0], True)

def pediaJumpToCorporation(argsList):
        pediaMainScreen.pediaJump(PEDIA_CORPORATION, argsList[0], True)

def pediaJumpToPromotion(argsList):
        pediaMainScreen.pediaJump(PEDIA_PROMOTION, argsList[0], True)

def pediaJumpToUnitChart(argsList):
        pediaMainScreen.pediaJump(PEDIA_UNIT_CHART, argsList[0], True)

def pediaJumpToBonus(argsList):
        pediaMainScreen.pediaJump(PEDIA_BONUS, argsList[0], True)

def pediaJumpToTerrain(argsList):
        pediaMainScreen.pediaJump(PEDIA_TERRAIN, argsList[0], True)

def pediaJumpToFeature(argsList):
        pediaMainScreen.pediaJump(PEDIA_FEATURE, argsList[0], True)

def pediaJumpToImprovement(argsList):
        pediaMainScreen.pediaJump(PEDIA_IMPROVEMENT, argsList[0], True)

def pediaJumpToCivic(argsList):
        pediaMainScreen.pediaJump(PEDIA_CIVIC, argsList[0], True)

def pediaJumpToCiv(argsList):
        pediaMainScreen.pediaJump(PEDIA_CIVILIZATION, argsList[0], True)

def pediaJumpToLeader(argsList):
        pediaMainScreen.pediaJump(PEDIA_LEADER, argsList[0], True)

def pediaJumpToSpecialist(argsList):
        pediaMainScreen.pediaJump(PEDIA_SPECIALIST, argsList[0], True)

def pediaShowHistorical(argsList):
        iEntryId = pediaMainScreen.pediaHistorical.getIdFromEntryInfo(argsList[0], argsList[1])
        pediaMainScreen.pediaJump(PEDIA_HISTORY, iEntryId, True)
        return

#################################################
## Worldbuilder
#################################################
# Platy's
worldBuilderScreen = CvPlatyBuilderScreen.CvWorldBuilderScreen()
def getWorldBuilderScreen():
  return worldBuilderScreen

def showWorldBuilderScreen():
  worldBuilderScreen.interfaceScreen()

def hideWorldBuilderScreen():
  worldBuilderScreen.killScreen()

def WorldBuilderToggleUnitEditCB():
  worldBuilderScreen.toggleUnitEditCB()

def WorldBuilderEraseCB():
  worldBuilderScreen.eraseCB()

def WorldBuilderLandmarkCB():
  worldBuilderScreen.landmarkModeCB()

def WorldBuilderExitCB():
  worldBuilderScreen.Exit()

def WorldBuilderToggleCityEditCB():
  worldBuilderScreen.toggleCityEditCB()

def WorldBuilderNormalPlayerTabModeCB():
  worldBuilderScreen.normalPlayerTabModeCB()

def WorldBuilderNormalMapTabModeCB():
  worldBuilderScreen.normalMapTabModeCB()

def WorldBuilderRevealTabModeCB():
  worldBuilderScreen.revealTabModeCB()

def WorldBuilderDiplomacyModeCB():
  WBDiplomacyScreen.WBDiplomacyScreen().interfaceScreen(CyGame().getActivePlayer(), False)

def WorldBuilderRevealAllCB():
  worldBuilderScreen.revealAll(True)

def WorldBuilderUnRevealAllCB():
  worldBuilderScreen.revealAll(False)

def WorldBuilderGetHighlightPlot(argsList):
  return worldBuilderScreen.getHighlightPlot(argsList)

def WorldBuilderOnAdvancedStartBrushSelected(argsList):
  iList,iIndex,iTab = argsList;
  print("WB Advanced Start brush selected, iList=%d, iIndex=%d, type=%d" %(iList,iIndex,iTab))
  if (iTab == worldBuilderScreen.m_iASTechTabID):
    showTechChooser()
  elif (iTab == worldBuilderScreen.m_iASCityTabID and iList == worldBuilderScreen.m_iASAutomateListID):
    CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE, worldBuilderScreen.m_iCurrentPlayer, -1, -1, -1, true)

  if (worldBuilderScreen.setCurrentAdvancedStartIndex(iIndex)):
    if (worldBuilderScreen.setCurrentAdvancedStartList(iList)):
      return 1
  return 0

def WorldBuilderGetASUnitTabID():
  return worldBuilderScreen.getASUnitTabID()

def WorldBuilderGetASCityTabID():
  return worldBuilderScreen.getASCityTabID()

def WorldBuilderGetASCityListID():
  return worldBuilderScreen.getASCityListID()

def WorldBuilderGetASBuildingsListID():
  return worldBuilderScreen.getASBuildingsListID()

def WorldBuilderGetASAutomateListID():
  return worldBuilderScreen.getASAutomateListID()

def WorldBuilderGetASImprovementsTabID():
  return worldBuilderScreen.getASImprovementsTabID()

def WorldBuilderGetASRoutesListID():
  return worldBuilderScreen.getASRoutesListID()

def WorldBuilderGetASImprovementsListID():
  return worldBuilderScreen.getASImprovementsListID()

def WorldBuilderGetASVisibilityTabID():
  return worldBuilderScreen.getASVisibilityTabID()

def WorldBuilderGetASTechTabID():
  return worldBuilderScreen.getASTechTabID()

# BTS Original -----------------------------
"""
worldBuilderScreen = CvWorldBuilderScreen.CvWorldBuilderScreen()
def getWorldBuilderScreen():
        return worldBuilderScreen

def showWorldBuilderScreen():
        worldBuilderScreen.interfaceScreen()

def hideWorldBuilderScreen():
        worldBuilderScreen.killScreen()

def WorldBuilderToggleUnitEditCB():
        worldBuilderScreen.toggleUnitEditCB()

def WorldBuilderAllPlotsCB():
        CvEventInterface.beginEvent(CvUtil.EventWBAllPlotsPopup)

def WorldBuilderEraseCB():
        worldBuilderScreen.eraseCB()

def WorldBuilderLandmarkCB():
        worldBuilderScreen.landmarkModeCB()

def WorldBuilderExitCB():
        worldBuilderScreen.Exit()

def WorldBuilderToggleCityEditCB():
        worldBuilderScreen.toggleCityEditCB()

def WorldBuilderNormalPlayerTabModeCB():
        worldBuilderScreen.normalPlayerTabModeCB()

def WorldBuilderNormalMapTabModeCB():
        worldBuilderScreen.normalMapTabModeCB()

def WorldBuilderRevealTabModeCB():
        worldBuilderScreen.revealTabModeCB()

def WorldBuilderDiplomacyModeCB():
        worldBuilderScreen.diplomacyModeCB()

def WorldBuilderRevealAllCB():
        worldBuilderScreen.revealAll(True)

def WorldBuilderUnRevealAllCB():
        worldBuilderScreen.revealAll(False)

def WorldBuilderHandleUnitCB( argsList ):
        worldBuilderScreen.handleUnitCB(argsList)

def WorldBuilderHandleTerrainCB( argsList ):
        worldBuilderScreen.handleTerrainCB(argsList)

def WorldBuilderHandleFeatureCB(argsList):
        worldBuilderScreen.handleFeatureCB(argsList)

def WorldBuilderHandleBonusCB( argsList ):
        worldBuilderScreen.handleBonusCB(argsList)

def WorldBuilderHandleImprovementCB(argsList):
        worldBuilderScreen.handleImprovementCB(argsList)

def WorldBuilderHandleTerritoryCB(argsList):
        worldBuilderScreen.handleTerritoryCB(argsList)

def WorldBuilderHandlePlotTypeCB( argsList ):
        worldBuilderScreen.handlePlotTypeCB(argsList)

def WorldBuilderHandleAllPlotsCB( argsList ):
        worldBuilderScreen.handleAllPlotsCB(argsList)

def WorldBuilderHandleUnitEditExperienceCB( argsList ):
        worldBuilderScreen.handleUnitEditExperienceCB(argsList)

def WorldBuilderHandleUnitEditLevelCB( argsList ):
        worldBuilderScreen.handleUnitEditLevelCB(argsList)

def WorldBuilderHandleUnitEditNameCB( argsList ):
        worldBuilderScreen.handleUnitEditNameCB(argsList)

def WorldBuilderHandleCityEditPopulationCB( argsList ):
        worldBuilderScreen.handleCityEditPopulationCB(argsList)

def WorldBuilderHandleCityEditCultureCB( argsList ):
        worldBuilderScreen.handleCityEditCultureCB(argsList)

def WorldBuilderHandleCityEditGoldCB( argsList ):
        worldBuilderScreen.handleCityEditGoldCB(argsList)

def WorldBuilderHandleCityEditAddScriptCB( argsList ):
        worldBuilderScreen.getCityScript()

def WorldBuilderHandleUnitEditAddScriptCB( argsList ):
        worldBuilderScreen.getUnitScript()

def WorldBuilderHandleCityEditNameCB( argsList ):
        worldBuilderScreen.handleCityEditNameCB(argsList)

def WorldBuilderHandleLandmarkTextCB( argsList ):
        worldBuilderScreen.handleLandmarkTextCB(argsList)

def WorldBuilderHandleUnitEditPullDownCB( argsList ):
        worldBuilderScreen.handleUnitEditPullDownCB(argsList)

def WorldBuilderHandleUnitAITypeEditPullDownCB( argsList ):
        worldBuilderScreen.handleUnitAITypeEditPullDownCB(argsList)

def WorldBuilderHandlePlayerEditPullDownCB( argsList ):
        worldBuilderScreen.handlePlayerEditPullDownCB(argsList)

def WorldBuilderHandlePlayerUnitPullDownCB( argsList ):
        worldBuilderScreen.handlePlayerUnitPullDownCB(argsList)

def WorldBuilderHandleSelectTeamPullDownCB( argsList ):
        worldBuilderScreen.handleSelectTeamPullDownCB(argsList)

def WorldBuilderHandlePromotionCB( argsList ):
        worldBuilderScreen.handlePromotionCB(argsList)

def WorldBuilderHandleBuildingCB( argsList ):
        worldBuilderScreen.handleBuildingCB(argsList)

def WorldBuilderHandleTechCB( argsList ):
        worldBuilderScreen.handleTechCB(argsList)

def WorldBuilderHandleRouteCB( argsList ):
        worldBuilderScreen.handleRouteCB(argsList)

def WorldBuilderHandleEditCityBuildingCB( argsList ):
        worldBuilderScreen.handleEditCityBuildingCB(argsList)

def WorldBuilderHandleBrushWidthCB( argsList ):
        worldBuilderScreen.handleBrushWidthCB(argsList)

def WorldBuilderHandleBrushHeightCB( argsList ):
        worldBuilderScreen.handleBrushHeightCB(argsList)

def WorldBuilderHandleLandmarkCB( argsList ):
        worldBuilderScreen.handleLandmarkCB(argsList)

def WorldBuilderHandleFlyoutMenuCB( argsList ):
        worldBuilderScreen.handleFlyoutMenuCB(argsList)

def WorldBuilderGetHighlightPlot(argsList):
        return worldBuilderScreen.getHighlightPlot(argsList)

def WorldBuilderOnAdvancedStartBrushSelected(argsList):
        iList,iIndex,iTab = argsList;
        print("WB Advanced Start brush selected, iList=%d, iIndex=%d, type=%d" %(iList,iIndex,iTab))
        if (iTab == worldBuilderScreen.m_iASTechTabID):
                showTechChooser()
        elif (iTab == worldBuilderScreen.m_iASCityTabID and iList == worldBuilderScreen.m_iASAutomateListID):
                CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE, worldBuilderScreen.m_iCurrentPlayer, -1, -1, -1, true)

        if (worldBuilderScreen.setCurrentAdvancedStartIndex(iIndex)):
                if (worldBuilderScreen.setCurrentAdvancedStartList(iList)):
                        return 1
        return 0

def WorldBuilderOnNormalPlayerBrushSelected(argsList):
        iList,iIndex,iTab = argsList;
        print("WB brush selected, iList=%d, iIndex=%d, type=%d" %(iList,iIndex,iTab))
        if (worldBuilderScreen.setCurrentNormalPlayerIndex(iIndex)):
                return 1
        return 0

def WorldBuilderOnNormalMapBrushSelected(argsList):
        iList,iIndex,iTab = argsList;
        print("WB brush selected, iList=%d, iIndex=%d, type=%d" %(iList,iIndex,iTab))
        if (worldBuilderScreen.setCurrentNormalMapIndex(iIndex)):
                if (worldBuilderScreen.setCurrentNormalMapList(iList)):
                        return 1
        return 0

def WorldBuilderOnWBEditBrushSelected(argsList):
        iList,iIndex,iTab = argsList;
        if (worldBuilderScreen.setEditButtonClicked(iIndex)):
                return 1
        return 0

def WorldBuilderOnWBEditReligionSelected(argsList):
        iList,iIndex,iTab = argsList;
        if (worldBuilderScreen.setEditReligionSelected(iIndex)):
                return 1
        return 0

def WorldBuilderOnWBEditHolyCitySelected(argsList):
        iList,iIndex,iTab = argsList;
        if (worldBuilderScreen.setEditHolyCitySelected(iIndex)):
                return 1
        return 0

def WorldBuilderOnWBEditCorporationSelected(argsList):
        iList,iIndex,iTab = argsList;
        if (worldBuilderScreen.setEditCorporationSelected(iIndex)):
                return 1
        return 0

def WorldBuilderOnWBEditHeadquartersSelected(argsList):
        iList,iIndex,iTab = argsList;
        if (worldBuilderScreen.setEditHeadquartersSelected(iIndex)):
                return 1
        return 0

def WorldBuilderOnAllPlotsBrushSelected(argsList):
        if (worldBuilderScreen.handleAllPlotsCB(argsList)):
                return 1
        return 0

def WorldBuilderGetASUnitTabID():
        return worldBuilderScreen.getASUnitTabID()

def WorldBuilderGetASCityTabID():
        return worldBuilderScreen.getASCityTabID()

def WorldBuilderGetASCityListID():
        return worldBuilderScreen.getASCityListID()

def WorldBuilderGetASBuildingsListID():
        return worldBuilderScreen.getASBuildingsListID()

def WorldBuilderGetASAutomateListID():
        return worldBuilderScreen.getASAutomateListID()

def WorldBuilderGetASImprovementsTabID():
        return worldBuilderScreen.getASImprovementsTabID()

def WorldBuilderGetASRoutesListID():
        return worldBuilderScreen.getASRoutesListID()

def WorldBuilderGetASImprovementsListID():
        return worldBuilderScreen.getASImprovementsListID()

def WorldBuilderGetASVisibilityTabID():
        return worldBuilderScreen.getASVisibilityTabID()

def WorldBuilderGetASTechTabID():
        return worldBuilderScreen.getASTechTabID()

def WorldBuilderGetUnitTabID():
        return worldBuilderScreen.getUnitTabID()

def WorldBuilderGetBuildingTabID():
        return worldBuilderScreen.getBuildingTabID()

def WorldBuilderGetTechnologyTabID():
        return worldBuilderScreen.getTechnologyTabID()

def WorldBuilderGetImprovementTabID():
        return worldBuilderScreen.getImprovementTabID()

def WorldBuilderGetBonusTabID():
        return worldBuilderScreen.getBonusTabID()

def WorldBuilderGetImprovementListID():
        return worldBuilderScreen.getImprovementListID()

def WorldBuilderGetBonusListID():
        return worldBuilderScreen.getBonusListID()

def WorldBuilderGetTerrainTabID():
        return worldBuilderScreen.getTerrainTabID()

def WorldBuilderGetTerrainListID():
        return worldBuilderScreen.getTerrainListID()

def WorldBuilderGetFeatureListID():
        return worldBuilderScreen.getFeatureListID()

def WorldBuilderGetPlotTypeListID():
        return worldBuilderScreen.getPlotTypeListID()

def WorldBuilderGetRouteListID():
        return worldBuilderScreen.getRouteListID()

def WorldBuilderGetTerritoryTabID():
        return worldBuilderScreen.getTerritoryTabID()

def WorldBuilderGetTerritoryListID():
        return worldBuilderScreen.getTerritoryListID()

def WorldBuilderHasTech(argsList):
        iTech = argsList[0]
        return worldBuilderScreen.hasTech(iTech)

def WorldBuilderHasPromotion(argsList):
        iPromotion = argsList[0]
        return worldBuilderScreen.hasPromotion(iPromotion)

def WorldBuilderHasBuilding(argsList):
        iBuilding = argsList[0]
        return worldBuilderScreen.getNumBuilding(iBuilding)

def WorldBuilderHasReligion(argsList):
        iReligion = argsList[0]
        return worldBuilderScreen.hasReligion(iReligion)

def WorldBuilderHasHolyCity(argsList):
        iReligion = argsList[0]
        return worldBuilderScreen.hasHolyCity(iReligion)

def WorldBuilderHasCorporation(argsList):
        iCorporation = argsList[0]
        return worldBuilderScreen.hasCorporation(iCorporation)

def WorldBuilderHasHeadquarters(argsList):
        iCorporation = argsList[0]
        return worldBuilderScreen.hasHeadquarters(iCorporation)

def WorldBuilderHandleDiploPlayerDropdownCB( argsList ):
        worldBuilderScreen.handleDiploPlayerDropdownCB(argsList)

##### WORLDBUILDER DIPLOMACY SCREEN #####

worldBuilderDiplomacyScreen = CvWorldBuilderDiplomacyScreen.CvWorldBuilderDiplomacyScreen()
def showWorldBuilderDiplomacyScreen():
        worldBuilderDiplomacyScreen.interfaceScreen()

def hideWorldBuilderDiplomacyScreen():
        worldBuilderDiplomacyScreen.killScreen()

def handleWorldBuilderDiplomacyPlayerPullDownCB(argsList):
        worldBuilderDiplomacyScreen.handlePlayerPullDownCB(int(argsList[0]))

def handleWorldBuilderDiplomacyVassalPullDownCB(argsList):
        worldBuilderDiplomacyScreen.handleVassalPullDownCB(int(argsList[0]))

def handleWorldBuilderDiplomacyAtWarPullDownCB(argsList):
        worldBuilderDiplomacyScreen.handleAtWarPullDownCB(argsList)

def handleWorldBuilderDiplomacyAIWeightPullDownCB(argsList):
        worldBuilderDiplomacyScreen.handleAIWeightPullDownCB(argsList)

def handleWorldBuilderDiplomacyAIWeightResetAllCB(argsList):
        worldBuilderDiplomacyScreen.handleAIWeightResetAll()

def handleWorldBuilderDiplomacyExitCB(argsList):
        worldBuilderDiplomacyScreen.killScreen()
"""

#################################################
## Utility Functions (can be overridden by CvScreenUtilsInterface
#################################################

def movieDone(argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().movieDone(argsList)):
                return

        if (argsList[0] == INTRO_MOVIE_SCREEN):
                introMovie.hideScreen()

        if (argsList[0] == VICTORY_MOVIE_SCREEN):
                victoryMovie.hideScreen()

def leftMouseDown (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().leftMouseDown(argsList)):
                return

        if ( argsList[0] == WORLDBUILDER_SCREEN ):
                worldBuilderScreen.leftMouseDown(argsList[1:])
                return 1
        return 0

def rightMouseDown (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().rightMouseDown(argsList)):
                return

        if ( argsList[0] == WORLDBUILDER_SCREEN ):
                worldBuilderScreen.rightMouseDown(argsList)
                return 1
        return 0

def mouseOverPlot (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().mouseOverPlot(argsList)):
                return

        if (WORLDBUILDER_SCREEN == argsList[0]):
                worldBuilderScreen.mouseOverPlot(argsList)

def handleInput (argsList):
        ' handle input is called when a screen is up '
        inputClass = PyScreenInput.ScreenInput(argsList)

        # allows overides for mods
        ret = CvScreenUtilsInterface.getScreenUtils().handleInput( (inputClass.getPythonFile(),inputClass) )

        # get the screen that is active from the HandleInputMap Dictionary
        screen = HandleInputMap.get( inputClass.getPythonFile() )

        # call handle input on that screen
        if ( screen and not ret):
                return screen.handleInput(inputClass)
        return 0

def update (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().update(argsList)):
                return

        if (HandleInputMap.has_key(argsList[0])):
                screen = HandleInputMap.get(argsList[0])
                screen.update(argsList[1])

def onClose (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().onClose(argsList)):
                return

        if (HandleCloseMap.has_key(argsList[0])):
                screen = HandleCloseMap.get(argsList[0])
                screen.onClose()

# Forced screen update
def forceScreenUpdate (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().forceScreenUpdate(argsList)):
                return

        # Tech chooser update (forced from net message)
        if ( argsList[0] == TECH_CHOOSER ):
                techChooser.updateTechRecords(false)
        # Main interface Screen
        elif ( argsList[0] == MAIN_INTERFACE ):
                mainInterface.updateScreen()
        # world builder Screen
        elif ( argsList[0] == WORLDBUILDER_SCREEN ):
                worldBuilderScreen.updateScreen()

        # BTS Original
        # world builder diplomacy Screen
        #elif ( argsList[0] == WORLDBUILDER_DIPLOMACY_SCREEN ):
        #        worldBuilderDiplomacyScreen.updateScreen()

# Forced redraw
def forceScreenRedraw (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().forceScreenRedraw(argsList)):
                return

        # Main Interface Screen
        if ( argsList[0] == MAIN_INTERFACE ):
                mainInterface.redraw()
        # BTS Original
        #elif ( argsList[0] == WORLDBUILDER_SCREEN ):
        #        worldBuilderScreen.redraw()
        #elif ( argsList[0] == WORLDBUILDER_DIPLOMACY_SCREEN ):
        #        worldBuilderDiplomacyScreen.redraw()
        elif ( argsList[0] == TECH_CHOOSER ):
                techChooser.updateTechRecords(true)


def minimapClicked (argsList):
        # allows overides for mods
        if (CvScreenUtilsInterface.getScreenUtils().minimapClicked(argsList)):
                return

        if (MILITARY_ADVISOR == argsList[0]):
                militaryAdvisor.minimapClicked()
        return

############################################################################
## Misc Functions
############################################################################

def handleBack(screens):
        for iScreen in screens:
                if (HandleNavigationMap.has_key(iScreen)):
                        screen = HandleNavigationMap.get( iScreen )
                        screen.back()
        print "Mouse BACK"
        return 0

def handleForward(screens):
        for iScreen in screens:
                if (HandleNavigationMap.has_key(iScreen)):
                        screen = HandleNavigationMap.get( iScreen )
                        screen.forward()
        print "Mouse FWD"
        return 0

def refreshMilitaryAdvisor (argsList):
        if (1 == argsList[0]):
                militaryAdvisor.refreshSelectedGroup(argsList[1])
        elif (2 == argsList[0]):
                militaryAdvisor.refreshSelectedLeader(argsList[1])
        elif (3 == argsList[0]):
                militaryAdvisor.drawCombatExperience()
        elif (argsList[0] <= 0):
                militaryAdvisor.refreshSelectedUnit(-argsList[0], argsList[1])

def updateMusicPath (argsList):
    szPathName = argsList[0]
    optionsScreen.updateMusicPath(szPathName)

def refreshOptionsScreen():
        optionsScreen.refreshScreen()

def cityWarningOnClickedCallback(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]
        city = CyGlobalContext().getPlayer(CyGlobalContext().getGame().getActivePlayer()).getCity(iData1)
        if (not city.isNone()):
                if (iButtonId == 0):
                        if (city.isProductionProcess()):
                                CyMessageControl().sendPushOrder(iData1, iData2, iData3, False, False, False)
                        else:
                                CyMessageControl().sendPushOrder(iData1, iData2, iData3, False, True, False)
                elif (iButtonId == 2):
                        CyInterface().selectCity(city, False)

def cityWarningOnFocusCallback(argsList):
        CyInterface().playGeneralSound("AS2D_ADVISOR_SUGGEST")
        CyInterface().lookAtCityOffset(argsList[0])
        return 0

def liberateOnClickedCallback(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]
        city = CyGlobalContext().getPlayer(CyGlobalContext().getGame().getActivePlayer()).getCity(iData1)
        if (not city.isNone()):
                if (iButtonId == 0):
                        CyMessageControl().sendDoTask(iData1, TaskTypes.TASK_LIBERATE, 0, -1, False, False, False, False)
                elif (iButtonId == 2):
                        CyInterface().selectCity(city, False)

def colonyOnClickedCallback(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]
        city = CyGlobalContext().getPlayer(CyGlobalContext().getGame().getActivePlayer()).getCity(iData1)
        if (not city.isNone()):
                if (iButtonId == 0):
                        CyMessageControl().sendEmpireSplit(CyGlobalContext().getGame().getActivePlayer(), city.area().getID())
                elif (iButtonId == 2):
                        CyInterface().selectCity(city, False)

def featAccomplishedOnClickedCallback(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        if (iButtonId == 1):
                if (iData1 == FeatTypes.FEAT_TRADE_ROUTE):
                        showDomesticAdvisor(())
                elif ((iData1 >= FeatTypes.FEAT_UNITCOMBAT_ARCHER) and (iData1 <= FeatTypes.FEAT_UNIT_SPY)):
                        showMilitaryAdvisor()
                elif ((iData1 >= FeatTypes.FEAT_COPPER_CONNECTED) and (iData1 <= FeatTypes.FEAT_FOOD_CONNECTED)):
                        showForeignAdvisorScreen([0])
                elif ((iData1 == FeatTypes.FEAT_NATIONAL_WONDER)):
                  # 2 is for the wonder tab...
                        showInfoScreen([2, 0])
                elif ((iData1 >= FeatTypes.FEAT_POPULATION_HALF_MILLION) and (iData1 <= FeatTypes.FEAT_POPULATION_2_BILLION)):
                  # 1 is for the demographics tab...
                        showInfoScreen([1, 0])
                elif iData1 == FeatTypes.FEAT_CORPORATION_ENABLED:
                        showCorporationScreen()

def featAccomplishedOnFocusCallback(argsList):
        iData1 = argsList[0]
        iData2 = argsList[1]
        iData3 = argsList[2]
        iData4 = argsList[3]
        szText = argsList[4]
        bOption1 = argsList[5]
        bOption2 = argsList[6]

        CyInterface().playGeneralSound("AS2D_FEAT_ACCOMPLISHED")
        if ((iData1 >= FeatTypes.FEAT_UNITCOMBAT_ARCHER) and (iData1 <= FeatTypes.FEAT_FOOD_CONNECTED)):
                CyInterface().lookAtCityOffset(iData2)

        return 0

def popupHunsPayment(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        if iButtonId == 1: # = YES - NetID , iPlayer , unitID
          CyMessageControl().sendModNetMessage( 674, iData1, iData2, 0, 0 )

def popupRevoltPayment(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]
        #  NetID , iPlayer , City ID , RevoltTurns , 0 | 1 | 2
        CyMessageControl().sendModNetMessage( 675, iData1, iData2, iData3, iButtonId )

def popupProvinzPayment(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # NetID , iPlayer, CityID , ButtonID
        CyMessageControl().sendModNetMessage( 678, iData1, iData2, iButtonId, iData3 )

# Sell unit (Mercenary post)
# iOwner, iUnitID
def popupSellUnit(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # NetID , confirm = 1, nix , iPlayer, iUnitID
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 695, 1, 0, iData1, iData2 )

# Vasallen - Feature +++++++++++++++++++++++++
def popupVassal01(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, iGold
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 671, iData1, iData2, iData3, 0 )
        # Kill Botschafter 0 to Loser / 1 to Winner
        elif iButtonId == 2:
          CyMessageControl().sendModNetMessage( 671, iData1, iData2, -1, iData4 )

def popupVassal03(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, iGold1, iGold2
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 682, iData1, iData2, iData3, 0 )
        elif iButtonId == 1:
          CyMessageControl().sendModNetMessage( 682, iData1, iData2, iData4, 0 )
        else:
          CyMessageControl().sendModNetMessage( 682, iData1, iData2, -1, 0 )

def popupVassal04(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, iGold1, iGold2
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 683, iData1, iData2, iData3, 0 )
        elif iButtonId == 1:
          CyMessageControl().sendModNetMessage( 683, iData1, iData2, iData4, 0 )

def popupVassal05(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, iGold1
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 684, iData1, iData2, iData3, 0 ) # YES
        if iButtonId == 1:
          CyMessageControl().sendModNetMessage( 684, iData1, iData2, 0, 0 ) # NO
        else:
          CyMessageControl().sendModNetMessage( 684, iData1, iData2, -1, 0 ) # KILL

def popupVassal06(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, iGold1
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 685, iData1, iData2, iData3, 0 ) # YES
        if iButtonId == 1:
          CyMessageControl().sendModNetMessage( 685, iData1, iData2, 0, 0 ) # NO
        else:
          CyMessageControl().sendModNetMessage( 685, iData1, iData2, -1, 0 ) # KILL

def popupVassal07(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3] # 0/1
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser, 0 , 0/1 (Loser/Winnerauswahl)
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 686, iData1, iData2, iData3, iData4 ) # YES

def popupVassal08(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # = YES - NetID , iWinner , iLoser (Hegemon), iVassal , iGold
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 687, iData1, iData2, iData3, iData4 ) # YES

def popupVassal09(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # iWinner , iLoser (Hegemon), iVassal , 0=Yes,1=No
        CyMessageControl().sendModNetMessage( 688, iData1, iData2, iData3, iButtonId ) # Yes or No

def popupVassal10(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # iWinner , iLoser (Hegemon), iVassal , iGold
        # NO: Kein Interesse: Gold=0
        if iButtonId == 1: iData4 = 0
        CyMessageControl().sendModNetMessage( 689, iData1, iData2, iData3, iData4 ) # Yes or No

def popupVassal11(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # iWinner , iLoser (Hegemon), iVassal , iGold
        # iButton:
        # Yes:  0
        # NO:   1 Kein Interesse, keine Auswirkungen. Ende.
        # KILL: 2
        if iButtonId != 1:
         if iButtonId == 2: iData4 = -1 # KILL
         CyMessageControl().sendModNetMessage( 690, iData1, iData2, iData3, iData4 ) # Yes or Kill

def popupVassal12(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        if iButtonId == 0:
         CyMessageControl().sendModNetMessage( 691, iData1, iData2, iData3, iData4 ) # Yes

def popupVassalTech(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # iHegemon (HI) , iVassal, iTech , iTechCost
        # iButton:
        # Yes   0: Tech, +1 Beziehung
        # Money 1: Tech mit Geld, keine anderen Auswirkungen
        # NO:   2: Keine Tech, -1 Beziehung
        if iButtonId == 0: iData4 = -1
        elif iButtonId == 2: iData3 = -1
        CyMessageControl().sendModNetMessage( 702, iData1, iData2, iData3, iData4 )

def popupVassalTech2(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # iHegemon (HI) , iVassal, iTech , iTechCost
        # iButton:
        # Yes 0: Tech kaufen
        # NO  1: Tech nicht kaufen
        if iButtonId == 1: iData4 = -1
        CyMessageControl().sendModNetMessage( 703, iData1, iData2, iData3, iData4 )

def popupReliaustreibung(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]
        # iPlayer, iCity, iUnit , iCancelButton
        if iButtonId != iData4:
          CyMessageControl().sendModNetMessage( 704, iData1, iData2, iButtonId, iData3 )

def popupRenegadeCity(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iWinner , pCity.getID , iLoser
        # iButtonId: Keep | Enslave | Raze
        CyMessageControl().sendModNetMessage( 706, iData1, iData2, iData3, iButtonId )

# Mercenaries -----------
def popupMercenariesMain(argsList):
        # iData1 (cityID), iData2 (iPlayer)
        iButtonId = argsList[0]
        iCity = argsList[1]
        iPlayer = argsList[2]
        #~ iData3 = argsList[3]
        iButtonCancel = argsList[4]

        # Hire (0) or Assign (1) mercenaries
        if iButtonId != iButtonCancel:
          if iButtonId == 0: CyMessageControl().sendModNetMessage( 708, iCity, -1, -1, iPlayer )
          elif iButtonId == 1: CyMessageControl().sendModNetMessage( 709, -1, -1, -1, iPlayer )

def popupMercenariesHire(argsList):
        # iData1 (cityID), iData2 = iUnitClassTyp, iData3 = iPlayer
        # iButtonID = iUnitClassTyp
        iButtonId = argsList[0]
        iCity = argsList[1]
        iData2 = argsList[2]
        iPlayer = argsList[3]
        iButtonCancel = argsList[4]

        # no back button between hire and assign
        # if iButtonId == iButtonCancel-1 and iData2 != -1: iButtonId = -1

        # Archers (0), Spearmen (1), Melee (2), Eles (3), Ships (4)
        if iButtonId != iButtonCancel:
          CyMessageControl().sendModNetMessage( 708, iCity, iButtonId, -1, iPlayer )

def popupMercenariesHireUnits(argsList):
        # iData1 (cityID), iData2 = iUnitClassTyp, iData3 = iPlayer
        # iButtonID = Unit
        iButtonId = argsList[0]
        iCity = argsList[1]
        iTypeButton = argsList[2]
        iPlayer = argsList[3]
        iButtonCancel = argsList[4]

        # back button
        if iButtonId == iButtonCancel-1: iTypeButton = -1

        # iData2 = Archers (0), Melee (1), Mounted (2), Eles (3), Ships (4)
        # iButtonID = Unit
        if iButtonId != iButtonCancel:
          CyMessageControl().sendModNetMessage( 708, iCity, iTypeButton, iButtonId, iPlayer )

# Assign mercenaries ------

def popupMercenariesAssign1(argsList):
        # iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = CIV
        if iButtonId != iData4:
          CyMessageControl().sendModNetMessage( 709, iButtonId, -1, -1, iData3 )
        # von 709 geht es direkt weiter zu 710

def popupMercenariesAssign2(argsList):
        # iData1 = iTargetCIV, iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = Inter/nationality
        if iButtonId != iData4:
          iFaktor = iButtonId + 1
          CyMessageControl().sendModNetMessage( 711, iData1, iFaktor, -1, iData3 )

def popupMercenariesAssign3(argsList):
        # iData1 = iTargetCIV, iData2 = iFaktor, iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = mercenary groups size
        if iButtonId != iData4:
          iFaktor = iData2 + (iButtonId + 1) * 10
          CyMessageControl().sendModNetMessage( 712, iData1, iFaktor, -1, iData3 )

def popupMercenariesAssign4(argsList):
        # iData1 = iTargetCIV, iData2 = iFaktor, iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = unit types (offensive/defensive/naval)
        if iButtonId != iData4:
          iFaktor = iData2 + (iButtonId + 1) * 100
          # Naval units (ignore next window: siege units)
          if iButtonId == 4:
            iFaktor += 1000
            CyMessageControl().sendModNetMessage( 714, iData1, iFaktor, -1, iData3 )
          # Land units
          else:
            CyMessageControl().sendModNetMessage( 713, iData1, iFaktor, -1, iData3 )

def popupMercenariesAssign5(argsList):
        # iData1 = iTargetCIV, iData2 = iFaktor, iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = siege units
        if iButtonId != iData4:
          iFaktor = iData2 + (iButtonId + 1) * 1000
          CyMessageControl().sendModNetMessage( 714, iData1, iFaktor, -1, iData3 )

def popupMercenariesAssign6(argsList):
        # iData1 = iTargetCIV, iData2 = iFaktor, iData3 = iPlayer, iData4 = Cancel
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonId = confirmation
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 715, iData1, iData2, -1, iData3 )

def popupMercenaryTorture(argsList):
        # iData1 (iMercenaryCiv), iData2 (iPlayer)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # Begin Torture (0)
        if iButtonId == 0: CyMessageControl().sendModNetMessage( 716, iData1, iData2, -1, -1 )

def popupMercenaryTorture2(argsList):
        # iData1 (iMercenaryCiv), iData2 (iPlayer)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # Begin Torture (0)
        if iButtonId <= 2: CyMessageControl().sendModNetMessage( 717, iData1, iData2, iButtonId, -1 )

def popupReservists(argsList):
        # iData1 (iCityID), iData2 (iPlayer)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonID = Unit
        if iButtonId != iData4:
           CyMessageControl().sendModNetMessage( 725, iData1, iData2, iButtonId, 0 )

def popupBonusverbreitung(argsList):
        # iData1 (iPlayer), iData2 (iUnitId), iData3 (Page)
        # Page: 0: First Page, 1: Getreide, 2: Vieh, ...)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonID = Bonus (First: bonus types)
        if iButtonId != iData4:
          # back button
          if iData3 != -1 and iButtonId == 0:
            CyMessageControl().sendModNetMessage( 726, -1, -1, iData1, iData2 )
          # first page (bonus types)
          elif iData3 == -1:
            CyMessageControl().sendModNetMessage( 726, iButtonId, -1, iData1, iData2 )
          # pages
          else:
            CyMessageControl().sendModNetMessage( 726, iData3, iButtonId, iData1, iData2 )

# Cultivation / Trade / Boggy
# Called when player has selected bonus to buy
def popupTradeChooseBonus(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    pPlayer = gc.getPlayer(iUnitOwner)
    pUnit = pPlayer.getUnit(iUnitId)
    # Since CyPopup can only store 3 values, the city needs to be identified by the merchant's position...
    pCity = CyMap().plot(pUnit.getX(), pUnit.getY()).getPlotCity()
    lGoods = PAE_Trade.getCitySaleableGoods(pCity, iUnitOwner)
    if iButtonId < len(lGoods): # Otherwise: Cancel button
        CyMessageControl().sendModNetMessage( 742, lGoods[iButtonId], pCity.getOwner(), iUnitOwner, iUnitId )

# Cultivation / Trade / Boggy
# Called when player has selected cultivation bonus to buy
def popupTradeChooseBonus4Cultivation(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    pPlayer = gc.getPlayer(iUnitOwner)
    pUnit = pPlayer.getUnit(iUnitId)
    # Since CyPopup can only store 3 values, the city needs to be identified by the merchant's position...
    pCity = CyMap().plot(pUnit.getX(), pUnit.getY()).getPlotCity()
    lGoods = PAE_Trade.getCollectableGoods4Cultivation(pUnit)
    if iButtonId < len(lGoods): # Otherwise: Cancel button
        CyMessageControl().sendModNetMessage( 739, lGoods[iButtonId], 0, iUnitOwner, iUnitId )

# Called when player has selected civ to trade with. Next step: Select city.
def popupTradeRouteChooseCiv(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    bFirst = argsList[3]
    pUnit = gc.getPlayer(iUnitOwner).getUnit(iUnitId)
    lCivList = PAE_Trade.getPossibleTradeCivs(iUnitOwner)
    if iButtonId < len(lCivList):
        #CyMessageControl().sendModNetMessage( 745, lCivList[iButtonId], -1, iUnitOwner, iUnitId )
        # Next step: if bFirst: choose city 1, else: choose city 2
        if bFirst: iNewType = 2
        else: iNewType = 5
        PAE_Trade.doPopupAutomatedTradeRoute(pUnit, iNewType, lCivList[iButtonId], -1)

# Called when player has selected city to trade with. Next step: Select bonus.
def popupTradeRouteChooseCity1(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    iCityOwner = argsList[3]
    pUnit = gc.getPlayer(iUnitOwner).getUnit(iUnitId)
    bWater = False
    if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA: bWater = True
    lCityList = PAE_Trade.getPossibleTradeCitiesForCiv(iUnitOwner, iCityOwner, bWater)
    if iButtonId < len(lCityList):
        CyMessageControl().sendModNetMessage( 745, iCityOwner, lCityList[iButtonId].getID(), iUnitOwner, iUnitId )

# Same as above, but for second city in trade route. Two functions are needed bc. popupInfo only stores 4 values (5 needed)
def popupTradeRouteChooseCity2(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    iCityOwner = argsList[3]
    pUnit = gc.getPlayer(iUnitOwner).getUnit(iUnitId)
    bWater = False
    if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA: bWater = True
    lCityList = PAE_Trade.getPossibleTradeCitiesForCiv(iUnitOwner, iCityOwner, bWater)
    if iButtonId < len(lCityList):
        CyMessageControl().sendModNetMessage( 746, iCityOwner, lCityList[iButtonId].getID(), iUnitOwner, iUnitId )

# Called when has selected bonus to buy in city. Next step: Select civ 2 or start trade route (if finished)
def popupTradeRouteChooseBonus(argsList):
    iButtonId = argsList[0]
    iUnitOwner = argsList[1]
    iUnitId = argsList[2]
    bFirst = argsList[3]
    pUnit = gc.getPlayer(iUnitOwner).getUnit(iUnitId)
    if bFirst:
        iX = int(CvUtil.getScriptData(pUnit, ["autX1"], -1))
        iY = int(CvUtil.getScriptData(pUnit, ["autY1"], -1))
    else:
        iX = int(CvUtil.getScriptData(pUnit, ["autX2"], -1))
        iY = int(CvUtil.getScriptData(pUnit, ["autY2"], -1))


    pCity = CyMap().plot(iX, iY).getPlotCity()
    lGoods = PAE_Trade.getCitySaleableGoods(pCity, -1)
    lGoods.append(-1)
    if iButtonId < len(lGoods):
      CyMessageControl().sendModNetMessage( 747, lGoods[iButtonId], bFirst, iUnitOwner, iUnitId )

# --- End of cultivation / trade

def popupKartenzeichnungen(argsList):
        # iData1 (iPlayer), iData2 (iUnitId)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        if iButtonId != iData4:
          CyMessageControl().sendModNetMessage( 728, iButtonId, -1, iData1, iData2 )

def popupReleaseSlaves(argsList):
        # iData1 (iCityID), iData2 (iPlayer)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonID = type of slave
        if iButtonId != iData4:
           CyMessageControl().sendModNetMessage( 730, iData1, 0, iData2, iButtonId )

def popupBuildLimes(argsList):
        # iData1 (iPlayer), iData2 (iUnitID)
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # iButtonID = type of limes
        if iButtonId != iData4:
           CyMessageControl().sendModNetMessage( 733, iButtonId, 0, iData1, iData2 )

# Sold/Salae/Decimatio
# iOwner, iUnitID, Typ: Salae(1) or Decimatio(2)
def popupActionSalaeDecimatio(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]
        szText = argsList[5]
        bOption1 = argsList[6]
        bOption2 = argsList[7]

        # NetID , Typ, confirm = 1, iPlayer, iUnitID
        if iButtonId == 0:
          CyMessageControl().sendModNetMessage( 735, iData3, 1, iData1, iData2 )

# Provinzstatthalter / Tribut
# iCityID, iOwner, iTyp (-1, 0 = Einfluss, 1 = Tribut)
def popupStatthalterTribut(argsList):
        iButtonId = argsList[0]
        iData1 = argsList[1]
        iData2 = argsList[2]
        iData3 = argsList[3]
        iData4 = argsList[4]

        # NetID , iCity, iOwner, iButton, -1
        if iData3 == -1:
          CyMessageControl().sendModNetMessage( 737, iData1, iData2, iButtonId, -1 )
        # NetID, iCity, iOwner, iTyp, iButton
        elif iButtonId != iData4:
          CyMessageControl().sendModNetMessage( 737, iData1, iData2, iData3, iButtonId )




##############################################################
####################### for scenarios ########################
##############################################################

# ----- Scenario Peloponnesian War ----------------
def peloponnesianWarKeinpferd_Poteidaia1(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        iKorinth = 2
        iMakedonien = 10
        iNordIonien = 12
        pPlotPoteidaia = gc.getMap().plot(56,46)
        pCityPoteidaia = pPlotPoteidaia.getPlotCity()
        bIsHuman = gc.getPlayer(iAthen).isHuman()
        if iButtonId == 0:
            iGold = 500
            gc.getPlayer(iAthen).changeGold(iGold)
            gc.getPlayer(iNordIonien).AI_changeAttitudeExtra(iAthen,-3)
            pCityPoteidaia.changeHurryAngerTimer(pCityPoteidaia.hurryAngerLength(0)*3)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_1_OUTCOME",()))
              popupInfo.addPopup(iAthen)
        elif iButtonId == 1:
            pCityPoteidaia.changeOccupationTimer(6)
            for i in range(gc.getMAX_PLAYERS()):
                if i != iKorinth: pPlotPoteidaia.setCulture(i, 0, True)
            gc.getPlayer(iKorinth).AI_changeAttitudeExtra(iAthen,-3)
            gc.getPlayer(iAthen).AI_changeAttitudeExtra(iKorinth,-3)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_2_OUTCOME",()))
              popupInfo.addPopup(iAthen)
        elif iButtonId == 2:
            gc.getPlayer(iKorinth).AI_changeAttitudeExtra(iAthen,-5)
            gc.getPlayer(iAthen).AI_changeAttitudeExtra(iKorinth,-3)
            gc.getTeam(iKorinth).signDefensivePact(iMakedonien)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_3_OUTCOME",()))
              popupInfo.addPopup(iAthen)

def peloponnesianWarKeinpferd_Poteidaia2(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        pAthen = gc.getPlayer(iAthen)
        iKorinth = 2
        iMakedonien = 10
        pMakedonien = gc.getPlayer(iMakedonien)
        iThrakien = 11
        bIsHuman = pAthen.isHuman()
        if iButtonId == 0:
            if gc.getTeam(iAthen).canDeclareWar(iKorinth): gc.getTeam(iAthen).declareWar(iKorinth, 0, 5) #WARPLAN_TOTAL
            if gc.getTeam(iAthen).canDeclareWar(iMakedonien): gc.getTeam(iAthen).declareWar(iMakedonien, 0, 4) #WARPLAN_LIMITED
            iGold = pAthen.getGold()
            if iGold <= 5000: pAthen.setGold(0)
            else: pAthen.changeGold(-5000)
            iX = 55
            iY = 45
            eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
            eProdromoi = gc.getInfoTypeForString("UNIT_HORSEMAN_MACEDON")
            eSupply = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
            eSkirmish = gc.getInfoTypeForString("UNIT_SKIRMISHER")
            eTrireme = gc.getInfoTypeForString("UNIT_TRIREME")
            for i in range(2): pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(3):
                pUnit = pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                if i == 0: pUnit.setName("Pausanias")
                elif i == 1: pUnit.setName("Archestartos")
            pAthen.initUnit(eProdromoi, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pSupply = pAthen.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            PAE_Unit.setSupply(pUnit,200)
            pAthen.initUnit(eSkirmish, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            # 500 Gold pro Hoplit+Trireme, 2 Triremen erhaelt man immer -> iPay beginnt bei 1000 und man benoetigt mind. 1500, um mehr zu erhalten
            # Maximal 10 Triremen
            iPay = 1000
            for i in range(8):
                iPay += 500
                if iPay > iGold: break
                pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              if iGold < 2000: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_1_OUTCOME_LOW",()))
              elif iGold < 3500: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_1_OUTCOME_MEDIUM",()))
              else: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_1_OUTCOME_HIGH",()))
              popupInfo.addPopup(iAthen)
        elif iButtonId == 1:
            pThrakien = gc.getPlayer(iThrakien)
            bDefPact = gc.getTeam(iMakedonien).isDefensivePact(iKorinth)
            if gc.getTeam(iAthen).canDeclareWar(iKorinth): gc.getTeam(iAthen).declareWar(iKorinth, 0, 5) #WARPLAN_TOTAL
            pThrakien.AI_changeAttitudeExtra(iAthen,3)
            pMakedonien.AI_changeAttitudeExtra(iThrakien,-3)
            pAthen.changeGold(-250)
            pThrakien.changeGold(250)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              if not bDefPact: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_2_OUTCOME_SUCCESS",()))
              else: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_2_OUTCOME_FAILED",()))
              popupInfo.addPopup(iAthen)
        elif iButtonId == 2:
            if gc.getTeam(iAthen).canDeclareWar(iKorinth): gc.getTeam(iAthen).declareWar(iKorinth, 0, 5) #WARPLAN_TOTAL
            if gc.getTeam(iAthen).canDeclareWar(iMakedonien): gc.getTeam(iAthen).declareWar(iMakedonien, 0, 4) #WARPLAN_LIMITED
            # General in Athen
            pGeneral = pAthen.initUnit(gc.getInfoTypeForString("UNIT_GREAT_GENERAL"), 57, 30, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pGeneral.setName("Kallias")
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_3_OUTCOME",()))
              popupInfo.addPopup(iAthen)

def peloponnesianWarKeinpferd_Poteidaia3(argsList):
        iButtonId = argsList[0]
        iKorinth = 2
        pKorinth = gc.getPlayer(iKorinth)
        bIsHuman = pKorinth.isHuman()
        if iButtonId == 0:
          iX = 53
          iY = 30
          iGold = pKorinth.getGold()
          if iGold <= 2000: pKorinth.setGold(0)
          else: pKorinth.changeGold(-2000)
          eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
          eHorseman = gc.getInfoTypeForString("UNIT_HORSEMAN")
          eSkirmisher = gc.getInfoTypeForString("UNIT_SKIRMISHER")
          eSupply = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
          pKorinth.initUnit(eHorseman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pSupply = pKorinth.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          PAE_Unit.setSupply(pUnit,200)
          pKorinth.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pKorinth.initUnit(eSkirmisher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          # 250 Gold pro Hoplit+Skirmisher, jeweils 1 erhaelt man immer -> iPay beginnt bei 250 und man benoetigt mind. 500, um mehr zu erhalten
          # Maximal 8 Hopliten und Skirmisher (insgesamt)
          iPay = 250
          for i in range(7):
              iPay += 250
              if iPay > iGold: break
              pKorinth.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              pKorinth.initUnit(eSkirmisher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            if iGold < 750: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_1_OUTCOME_LOW",()))
            elif iGold < 1500: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_1_OUTCOME_MEDIUM",()))
            else: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_KORINTH_1_OUTCOME_HIGH",()))
            popupInfo.addPopup(iKorinth)
        elif iButtonId == 1:
          pKorinth.changeGold(-150)
          iX = 36
          iY = 48
          eGallier = gc.getInfoTypeForString("UNIT_HOPLIT")
          pKorinth.initUnit(eGallier, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_2_OUTCOME",()))
            popupInfo.addPopup(iKorinth)
        elif iButtonId == 2:
          pKorinth.changeGold(-250)
          iX = 55
          iY = 46
          eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
          eProdromoi = gc.getInfoTypeForString("UNIT_HORSEMAN_MACEDON")
          eSkirmish = gc.getInfoTypeForString("UNIT_SKIRMISHER")
          eSupply = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
          eGeneral = gc.getInfoTypeForString("UNIT_GREAT_GENERAL")
          eTrireme = gc.getInfoTypeForString("UNIT_TRIREME")
          for i in range(2): pKorinth.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          for i in range(2): pKorinth.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pKorinth.initUnit(eProdromoi, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pKorinth.initUnit(eSkirmish, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pSupply = pKorinth.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          PAE_Unit.setSupply(pUnit,200)
          pGeneral = pKorinth.initUnit(eGeneral, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          pGeneral.setName("Iolaos")
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_3_OUTCOME",()))
            popupInfo.addPopup(iKorinth)

def peloponnesianWarKeinpferd_Megara1(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        iSparta = 1
        iKorinth = 2
        iTheben = 4
        iNordIonien = 12
        iSuedIonien = 13
        bIsHuman = gc.getPlayer(iAthen).isHuman()
        bNordIsVassal = gc.getTeam(iNordIonien).isVassal(iAthen)
        bSuedIsVassal = gc.getTeam(iSuedIonien).isVassal(iAthen)
        if iButtonId == 0:
          # Verschlechterung der Beziehungen zwischen Athen und ionischen Vasallen um -2 (nur wenn sie noch Vasallen sind)
          if bNordIsVassal: gc.getPlayer(iNordIonien).AI_changeAttitudeExtra(iAthen, -2)
          if bSuedIsVassal: gc.getPlayer(iSuedIonien).AI_changeAttitudeExtra(iAthen, -2)
          # Verringerte Ertraege in Markt und Hafen fuer Athen und Ionier (verschwindet langsam)
          iVerlust = -5
          eHafen = gc.getInfoTypeForString("BUILDING_HARBOR")
          eMarkt = gc.getInfoTypeForString("BUILDING_MARKET")
          eHafenClass = gc.getBuildingInfo(eHafen).getBuildingClassType()
          eMarktClass = gc.getBuildingInfo(eMarkt).getBuildingClassType()
          lPlayer = [iAthen]
          if bNordIsVassal: lPlayer.append(iNordIonien)
          if bSuedIsVassal: lPlayer.append(iSuedIonien)
          for iPlayer in lPlayer:
            pPlayer = gc.getPlayer(iPlayer)
            iNumCities = pPlayer.getNumCities()
            for iCity in range(iNumCities):
              pCity = pPlayer.getCity(iCity)
              if pCity != None and not pCity.isNone():
                if pCity.isHasBuilding(eHafen):
                  iStandard = pCity.getBuildingCommerceByBuilding(0, eHafen) # 0 = Gold
                  pCity.setBuildingCommerceChange(eHafenClass, 0, iStandard + iVerlust)
                if pCity.isHasBuilding(eMarkt):
                  iStandard = pCity.getBuildingCommerceByBuilding(0, eMarkt) # 0 = Gold
                  pCity.setBuildingCommerceChange(eMarktClass, 0, iStandard + iVerlust)
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_1_OUTCOME",()))
            popupInfo.addPopup(iAthen)
          if gc.getPlayer(iNordIonien).isHuman() and bNordIsVassal:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_1_OUTCOME_UPPER_IONIEN",()))
            popupInfo.addPopup(iNordIonien)
          if gc.getPlayer(iSuedIonien).isHuman() and bSuedIsVassal:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_1_OUTCOME_LOWER_IONIEN",()))
            popupInfo.addPopup(iSuedIonien)
        elif iButtonId == 1:
          # Kultur fuer Athen in Megara
          pPlotMegara = gc.getMap().plot(55,30)
          pPlotMegara.changeCulture(iAthen, 500, 1)
          # Verbesserung der Beziehungen
          gc.getPlayer(iKorinth).AI_changeAttitudeExtra(iAthen, 2)
          gc.getPlayer(iAthen).AI_changeAttitudeExtra(iKorinth, 2)
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_2_OUTCOME",()))
            popupInfo.addPopup(iAthen)
          if gc.getPlayer(iKorinth).isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_2_OUTCOME_KORINTH",()))
            popupInfo.addPopup(iKorinth)
        elif iButtonId == 2:
          # Verschlechterung der Beziehungen zu Sparta und Theben
          gc.getPlayer(iSparta).AI_changeAttitudeExtra(iAthen, -6)
          gc.getPlayer(iTheben).AI_changeAttitudeExtra(iAthen, -6)
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_3_OUTCOME",()))
            popupInfo.addPopup(iAthen)

def peloponnesianWarKeinpferd_Megara2(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        iSparta = 1
        iKorinth = 2
        iTheben = 4
        pSparta = gc.getPlayer(iSparta)
        bIsHuman = pSparta.isHuman()
        if iButtonId == 0:
          iRand = random.randint(0, 2)
          if not gc.getTeam(iSparta).canDeclareWar(iAthen):
            if bIsHuman:
              # Kein Krieg moeglich -> Kein Gold/Bronze
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1_NO_WAR_POSSIBLE",()))
              popupInfo.addPopup(iSparta)
          # Wenig Gold
          elif iRand == 0:
              pSparta.changeGold(200)
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1_OUTCOME_LOW",()))
                popupInfo.addPopup(iSparta)
          # Viel Gold
          elif iRand == 1:
              pSparta.changeGold(1000)
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1_OUTCOME_HIGH",()))
                popupInfo.addPopup(iSparta)
          # 10 Bronze
          else:
              # 10 freie Bronze in der Hauptstadt -> in allen Staedten am Handelsnetz verfuegbar
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              iNumCities = pSparta.getNumCities()
              eBronze = gc.getInfoTypeForString("BONUS_BRONZE")
              pCapital = pSparta.getCapitalCity()
              pCapital.changeFreeBonus(eBronze, 10)
              if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1_OUTCOME_BRONZE",()))
                popupInfo.addPopup(iSparta)
        elif iButtonId == 1:
          iRand = random.randint(0, 1)
          if not gc.getTeam(iTheben).canDeclareWar(iAthen): iRand = 1 # Theben kann nicht
          # Theben ist einverstanden -> Krieg
          if iRand == 0:
            if gc.getTeam(iSparta).canDeclareWar(iAthen):
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              gc.getTeam(iTheben).declareWar(iAthen, 0, 5)
              if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2_OUTCOME_SUCCESS",()))
                popupInfo.addPopup(iSparta)
              if gc.getTeam(iTheben).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2_OUTCOME_SUCCESS_THEBEN",()))
                popupInfo.addPopup(iTheben)
            elif bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2_NO_WAR_POSSIBLE",()))
                popupInfo.addPopup(iSparta)
          else:
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2_OUTCOME_FAILED",()))
              popupInfo.addPopup(iSparta)
        elif iButtonId == 2:
          gc.getPlayer(iKorinth).AI_changeAttitudeExtra(iSparta, -3)
          if gc.getTeam(iSparta).canDeclareWar(iAthen):
            # Sparta und Theben ziehen gemeinsam in den Krieg
            if gc.getTeam(iTheben).canDeclareWar(iAthen):
              gc.getTeam(iTheben).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5)
              if gc.getTeam(iTheben).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_OUTCOME_THEBEN",()))
                popupInfo.addPopup(iTheben)
              if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_OUTCOME_SPARTA",()))
                popupInfo.addPopup(iSparta)
              if gc.getTeam(iKorinth).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_OUTCOME_KORINTH",()))
                popupInfo.addPopup(iKorinth)
            # Theben hat Friedensvertrag mit Athen
            elif gc.getTeam(iSparta).canDeclareWar(iAthen):
              gc.getTeam(iSparta).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
              if gc.getTeam(iSparta).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_OUTCOME_SPARTA_NO_THEBEN",()))
                popupInfo.addPopup(iSparta)
              if gc.getTeam(iKorinth).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_OUTCOME_KORINTH_NO_THEBEN",()))
                popupInfo.addPopup(iKorinth)
          elif bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3_NO_WAR_POSSIBLE",()))
              popupInfo.addPopup(iSparta)


def peloponnesianWarKeinpferd_Plataiai1(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        iTheben = 4
        pTheben = gc.getPlayer(iTheben)
        iX = 55
        iY = 33
        pPlotPlataiai = CyMap().plot(iX, iY)
        bIsHuman = pTheben.isHuman()
        bAthenIsHuman = gc.getPlayer(iAthen).isHuman()
        # Unabhaengig von Auswahloption wird Krieg erklaert
        bWar = False
        if gc.getTeam(iTheben).canDeclareWar(iAthen):
            gc.getTeam(iTheben).declareWar(iAthen, 0, 5) # WARPLAN_TOTAL
            bWar = True
        # Wird kein Krieg erklaert, passiert nichts
        if bWar:
         if iButtonId == 0:
          iRand = random.randint(0,2)
          # Klein
          if iRand == 0:
            iCultTheben = pPlotPlataiai.getCulture(iTheben)
            iCultAthen = pPlotPlataiai.getCulture(iAthen)
            # Garantieren, dass Theben den Plot besitzt
            pPlotPlataiai.changeCulture(iTheben, iCultAthen, 1)
            eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
            pTheben.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_LOW",()))
                popupInfo.addPopup(iTheben)
            if bAthenIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_LOW_ATHEN",()))
                popupInfo.addPopup(iAthen)
          # Mittel
          elif iRand == 1:
            # Athen erhaelt Plot und 1 Hoplit
            eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
            iCultTheben = pPlotPlataiai.getCulture(iTheben)
            iCultAthen = pPlotPlataiai.getCulture(iAthen)
            pPlotPlataiai.changeCulture(iAthen, iCultTheben, 1)
            gc.getPlayer(iAthen).initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            eSkirmisher = gc.getInfoTypeForString("UNIT_SKIRMISHER")
            eHorseman = gc.getInfoTypeForString("UNIT_HORSEMAN")
            for i in range(5): pTheben.initUnit(eHoplit, iX-1, iY-1, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(3): pTheben.initUnit(eSkirmisher, iX-1, iY-1, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pTheben.initUnit(eHorseman, iX-1, iY-1, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_MEDIUM",()))
                popupInfo.addPopup(iTheben)
            if bAthenIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_MEDIUM_ATHEN",()))
                popupInfo.addPopup(iAthen)
          elif iRand == 2:
            # Theben erhaelt Plot und grosse Armee
            iCultTheben = pPlotPlataiai.getCulture(iTheben)
            iCultAthen = pPlotPlataiai.getCulture(iAthen)
            pPlotPlataiai.changeCulture(iTheben, iCultAthen, 1)
            eSkirmisher = gc.getInfoTypeForString("UNIT_SKIRMISHER")
            eHorseman = gc.getInfoTypeForString("UNIT_HORSEMAN")
            eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
            eSupply = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
            eGeneral = gc.getInfoTypeForString("UNIT_GREAT_GENERAL")
            for i in range(10): pTheben.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(5): pTheben.initUnit(eSkirmisher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(4): pTheben.initUnit(eHorseman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(2): pTheben.initUnit(eGeneral, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pUnit = pTheben.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            PAE_Unit.setSupply(pUnit,200)
            if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_HIGH",()))
                popupInfo.addPopup(iTheben)
            if bAthenIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_1_OUTCOME_HIGH_ATHEN",()))
                popupInfo.addPopup(iAthen)
         elif iButtonId == 1:
            # Athen erhaelt Plot und 1 Hoplit
            eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
            iCultTheben = pPlotPlataiai.getCulture(iTheben)
            iCultAthen = pPlotPlataiai.getCulture(iAthen)
            pPlotPlataiai.changeCulture(iAthen, iCultTheben, 1)
            gc.getPlayer(iAthen).initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if bIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_2_OUTCOME",()))
                popupInfo.addPopup(iTheben)
            if bAthenIsHuman:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_2_OUTCOME_ATHEN",()))
                popupInfo.addPopup(iAthen)
         elif iButtonId == 2:
            iAthenX = 57
            iAthenY = 30
            pAthenCity = CyMap().plot(iAthenX, iAthenY)
            if not pAthenCity.isNone() and pAthenCity != None:
              if pAthenCity.getOwner == iAthen:
                # Fluechtlinge
                pAthenCity.changePopulation(1)
                if bIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME",()))
                  popupInfo.addPopup(iTheben)
                if bAthenIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME_ATHEN",()))
                  popupInfo.addPopup(iAthen)
              else:
                if bIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME_NO_ATHEN",()))
                  popupInfo.addPopup(iTheben)
                if bAthenIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME_NO_ATHEN_ATHEN",()))
                  popupInfo.addPopup(iAthen)
            else:
                if bIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME_NO_ATHEN",()))
                  popupInfo.addPopup(iTheben)
                if bAthenIsHuman:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_OPTION_3_OUTCOME_NO_ATHEN_ATHEN",()))
                  popupInfo.addPopup(iAthen)
        else:
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_NO_WAR",()))
            popupInfo.addPopup(iTheben)

def peloponnesianWarKeinpferd_Syra1(argsList):
        iButtonId = argsList[0]
        iAthen = 0
        pAthen = gc.getPlayer(iAthen)
        iSyrakus = 16
        bIsHuman = pAthen.isHuman()
        bWar = gc.getTeam(iAthen).canDeclareWar(iSyrakus)
        eTrireme = gc.getInfoTypeForString("UNIT_TRIREME")
        eBireme = gc.getInfoTypeForString("UNIT_BIREME")
        eHoplit = gc.getInfoTypeForString("UNIT_HOPLIT")
        eHippeus = gc.getInfoTypeForString("UNIT_ELITE_HOPLIT")
        eSupply = gc.getInfoTypeForString("UNIT_SUPPLY_WAGON")
        eRam = gc.getInfoTypeForString("UNIT_BATTERING_RAM")
        eArcher = gc.getInfoTypeForString("UNIT_ARCHER")
        eSpy = gc.getInfoTypeForString("UNIT_SPY")
        eHorseman = gc.getInfoTypeForString("UNIT_HORSEMAN")
        eRang1 = gc.getInfoTypeForString("PROMOTION_COMBAT1")
        eRang2 = gc.getInfoTypeForString("PROMOTION_COMBAT2")
        eRang3 = gc.getInfoTypeForString("PROMOTION_COMBAT3")
        eRang4 = gc.getInfoTypeForString("PROMOTION_COMBAT4")
        eRang5 = gc.getInfoTypeForString("PROMOTION_COMBAT5")
        eCityRaid1 = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
        eFlank1 = gc.getInfoTypeForString("PROMOTION_FLANKING1")
        eFlank2 = gc.getInfoTypeForString("PROMOTION_FLANKING2")
        eHero = gc.getInfoTypeForString("PROMOTION_HERO")
        iX = 57
        iY = 30
        if bWar:
          gc.getTeam(iAthen).declareWar(iSyrakus, 0, 5) #WARPLAN_LIMITED
          if iButtonId == 0:
            iGold = pAthen.getGold()
            # Mind. 2500 Gold, max. 5000 Gold
            if iGold <= 2500: pAthen.changeGold(-2500)
            elif iGold <= 5000: pAthen.setGold(0)
            else: pAthen.changeGold(-5000)
            # Einheiten, die man immer erhaelt
            for i in range(12): pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(1):
                pUnit = pAthen.initUnit(eHippeus, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eRang1, True)
                pUnit.setHasPromotion(eRang2, True)
                pUnit.setHasPromotion(eRang3, True)
                pUnit.setHasPromotion(eRang4, True)
                pUnit.setHasPromotion(eRang5, True)
                pUnit.setHasPromotion(eHero, True)
                pUnit.setHasPromotion(eCityRaid1, True)
                pUnit.setName("Nikias")
            for i in range(8):
                pUnit = pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eRang1, True)
                pUnit.setHasPromotion(eRang2, True)
                pUnit.setHasPromotion(eRang3, True)
            for i in range(8): pAthen.initUnit(eArcher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(12): pAthen.initUnit(eRam, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(4):
                pUnit = pAthen.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                PAE_Unit.setSupply(pUnit,200)
            for i in range(2):
                pUnit = pAthen.initUnit(eHorseman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eFlank1, True)
                pUnit.setHasPromotion(eFlank2, True)
            for i in range(1): pAthen.initUnit(eSpy, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            # Ab 2500 zusaetzliche Einheiten fuer je 500 Gold (max. 5000 Gold)
            iPay = 2500
            for i in range(5):
                iPay += 500
                if iPay > iGold: break
                for i in range(2): pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                for i in range(1): pAthen.initUnit(eBireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                for i in range(3):
                    pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    pUnit.setHasPromotion(eRang1, True)
                    pUnit.setHasPromotion(eRang2, True)
                    pUnit.setHasPromotion(eRang3, True)
                for i in range(2): pAthen.initUnit(eArcher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                for i in range(1):
                    pUnit = pAthen.initUnit(eHorseman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    pUnit.setHasPromotion(eFlank1, True)
                    pUnit.setHasPromotion(eFlank2, True)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              if iGold < 3000: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_1_OUTCOME_LOW",()))
              elif iGold < 4000: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_1_OUTCOME_MEDIUM",()))
              else: popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_1_OUTCOME_HIGH",()))
              popupInfo.addPopup(iAthen)
          elif iButtonId == 1:
            pAthen.changeGold(-2000)
            for i in range(9): pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(8):
                pUnit = pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eRang1, True)
                pUnit.setHasPromotion(eRang2, True)
            for i in range(8): pAthen.initUnit(eArcher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(6): pAthen.initUnit(eRam, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(2):
                pUnit = pAthen.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                PAE_Unit.setSupply(pUnit,200)
            for i in range(2):
                pUnit = pAthen.initUnit(eHorseman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eFlank1, True)
                pUnit.setHasPromotion(eFlank2, True)
            for i in range (1): pAthen.initUnit(eSpy, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_2_OUTCOME",()))
              popupInfo.addPopup(iAthen)
          elif iButtonId == 2:
            pAthen.changeGold(-1000)
            for i in range(4): pAthen.initUnit(eTrireme, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(5):
                pUnit = pAthen.initUnit(eHoplit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                pUnit.setHasPromotion(eRang1, True)
            for i in range(4): pAthen.initUnit(eArcher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(2): pAthen.initUnit(eRam, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for i in range(1):
                pUnit = pAthen.initUnit(eSupply, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                PAE_Unit.setSupply(pUnit,200)
            if bIsHuman:
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_3_OUTCOME",()))
              popupInfo.addPopup(iAthen)
        else:
          if bIsHuman:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_NO_WAR",()))
            popupInfo.addPopup(iAthen)

# --------------------

#######################################################################################
## Handle Close Map
#######################################################################################
HandleCloseMap = {  DAWN_OF_MAN : dawnOfMan,
                    SPACE_SHIP_SCREEN : spaceShip,
                    TECH_CHOOSER : techChooser,
                    # add new screens here
                 }

#######################################################################################
## Handle Input Map
#######################################################################################
HandleInputMap = {  MAIN_INTERFACE : mainInterface,
                                        DOMESTIC_ADVISOR : domesticAdvisor,
                                        RELIGION_SCREEN : religionScreen,
                                        CORPORATION_SCREEN : corporationScreen,
                                        CIVICS_SCREEN : civicScreen,
                                        TECH_CHOOSER : techChooser,
                                        FOREIGN_ADVISOR : foreignAdvisor,
                                        FINANCE_ADVISOR : financeAdvisor,
                                        MILITARY_ADVISOR : militaryAdvisor,
                                        DAWN_OF_MAN : dawnOfMan,
                                        WONDER_MOVIE_SCREEN : wonderMovie,
                                        ERA_MOVIE_SCREEN : eraMovie,
                                        SPACE_SHIP_SCREEN : spaceShip,
                                        INTRO_MOVIE_SCREEN : introMovie,
                                        OPTIONS_SCREEN : optionsScreen,
                                        INFO_SCREEN : infoScreen,
                                        TECH_SPLASH : techSplashScreen,
                                        REPLAY_SCREEN : replayScreen,
                                        VICTORY_SCREEN : victoryScreen,
                                        TOP_CIVS : topCivs,
                                        HALL_OF_FAME : hallOfFameScreen,
                                        VICTORY_MOVIE_SCREEN : victoryMovie,
                                        ESPIONAGE_ADVISOR : espionageAdvisor,
                                        DAN_QUAYLE_SCREEN : danQuayleScreen,

                                        PEDIA_MAIN : pediaMainScreen,
                                        PEDIA_TECH : pediaMainScreen,
                                        PEDIA_UNIT : pediaMainScreen,
                                        PEDIA_BUILDING : pediaMainScreen,
                                        PEDIA_PROMOTION : pediaMainScreen,
                                        PEDIA_PROJECT : pediaMainScreen,
                                        PEDIA_UNIT_CHART : pediaMainScreen,
                                        PEDIA_BONUS : pediaMainScreen,
                                        PEDIA_IMPROVEMENT : pediaMainScreen,
                                        PEDIA_TERRAIN : pediaMainScreen,
                                        PEDIA_FEATURE : pediaMainScreen,
                                        PEDIA_CIVIC : pediaMainScreen,
                                        PEDIA_CIVILIZATION : pediaMainScreen,
                                        PEDIA_LEADER : pediaMainScreen,
                                        PEDIA_RELIGION : pediaMainScreen,
                                        PEDIA_CORPORATION : pediaMainScreen,
                                        PEDIA_HISTORY : pediaMainScreen,
                                        WORLDBUILDER_SCREEN : worldBuilderScreen,
                                        #WORLDBUILDER_DIPLOMACY_SCREEN : worldBuilderDiplomacyScreen,

                                        DEBUG_INFO_SCREEN : debugInfoScreen,

                                        ## World Builder ##
                                        WB_PLOT : WBPlotScreen.WBPlotScreen(),
                                        WB_PLOT_RIVER : WBRiverScreen.WBRiverScreen(),
                                        WB_EVENT: WBEventScreen.WBEventScreen(),
                                        WB_BUILDING : WBBuildingScreen.WBBuildingScreen(),
                                        WB_CITYDATA : WBCityDataScreen.WBCityDataScreen(),
                                        WB_CITYEDIT : WBCityEditScreen.WBCityEditScreen(),
                                        WB_TECH : WBTechScreen.WBTechScreen(),
                                        WB_PROJECT : WBProjectScreen.WBProjectScreen(),
                                        WB_TEAM : WBTeamScreen.WBTeamScreen(),
                                        WB_PLAYER : WBPlayerScreen.WBPlayerScreen(),
                                        WB_UNIT : WBUnitScreen.WBUnitScreen(worldBuilderScreen),
                                        WB_PROMOTION : WBPromotionScreen.WBPromotionScreen(),
                                        WB_DIPLOMACY : WBDiplomacyScreen.WBDiplomacyScreen(),
                                        WB_GAMEDATA : WBGameDataScreen.WBGameDataScreen(worldBuilderScreen),
                                        WB_UNITLIST : WBPlayerUnits.WBPlayerUnits(),
                                        WB_RELIGION : WBReligionScreen.WBReligionScreen(),
                                        WB_CORPORATION : WBCorporationScreen.WBCorporationScreen(),
                                        WB_INFO : WBInfoScreen.WBInfoScreen(),
                                        WB_TRADE : WBTradeScreen.WBTradeScreen(),

                                        TRADEROUTE_ADVISOR : traderouteAdvisor,

                                }

#######################################################################################
## Handle Navigation Map
#######################################################################################
HandleNavigationMap = {
                                        MAIN_INTERFACE : mainInterface,
                                        PEDIA_MAIN : pediaMainScreen,
                                        PEDIA_TECH : pediaMainScreen,
                                        PEDIA_UNIT : pediaMainScreen,
                                        PEDIA_BUILDING : pediaMainScreen,
                                        PEDIA_PROMOTION : pediaMainScreen,
                                        PEDIA_PROJECT : pediaMainScreen,
                                        PEDIA_UNIT_CHART : pediaMainScreen,
                                        PEDIA_BONUS : pediaMainScreen,
                                        PEDIA_IMPROVEMENT : pediaMainScreen,
                                        PEDIA_TERRAIN : pediaMainScreen,
                                        PEDIA_FEATURE : pediaMainScreen,
                                        PEDIA_CIVIC : pediaMainScreen,
                                        PEDIA_CIVILIZATION : pediaMainScreen,
                                        PEDIA_LEADER : pediaMainScreen,
                                        PEDIA_HISTORY : pediaMainScreen,
                                        PEDIA_RELIGION : pediaMainScreen,
                                        PEDIA_CORPORATION : pediaMainScreen

                                # add new screens here
                                }
