# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvRandomEventInterface.py
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
import CvUtil
from CvPythonExtensions import *
import CvEventInterface

gc = CyGlobalContext()
localText = CyTranslator()


######## HOLY MOUNTAIN ###########

def getHelpHolyMountain1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  szHelp = ""

  map = gc.getMap()
  iMinPoints = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers() / 2

  iBuilding = -1
  iReligion = gc.getPlayer(kTriggeredData.ePlayer).getStateReligion()

  if (-1 != iReligion):
    for i in range(gc.getNumBuildingInfos()):
      if (gc.getBuildingInfo(i).getSpecialBuildingType() == CvUtil.findInfoTypeNum(gc.getSpecialBuildingInfo, gc.getNumSpecialBuildingInfos(), "SPECIALBUILDING_TEMPLE")):
        if (gc.getBuildingInfo(i).getReligionType() == iReligion):
          iBuilding = i
          break

    if iBuilding != -1:
      szHelp = localText.getText("TXT_KEY_EVENT_HOLY_MOUNTAIN_HELP", ( gc.getBuildingInfo(iBuilding).getTextKey(), gc.getBuildingInfo(iBuilding).getTextKey(), iMinPoints))

  return szHelp

def canTriggerHolyMountain(argsList):
  kTriggeredData = argsList[0]
  map = gc.getMap()

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  if (plot.getOwner() == -1):
    return True

  return False

def expireHolyMountain1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  if (plot == None):
    return True

  if (plot.getOwner() != kTriggeredData.ePlayer and plot.getOwner() != -1):
    # for PAE and the black fog of war
    CvUtil.removeScriptData(plot,"H")
    return True

  return False

def canTriggerHolyMountainDone(argsList):

  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

  if (kOrigTriggeredData == None):
    return False

  plot = gc.getMap().plot(kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY)
  if (plot == None):
    return False

  if (plot.getOwner() != kTriggeredData.ePlayer):
    return False

  # for PAE and the black fog of war
  CvUtil.removeScriptData(plot,"H")

  return True

def canTriggerHolyMountainRevealed(argsList):

  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

  if (kOrigTriggeredData == None):
    return False

  iNumPoints = 0

  for i in range(gc.getNumBuildingInfos()):
    if (gc.getBuildingInfo(i).getReligionType() == kOrigTriggeredData.eReligion):
      #if (gc.getBuildingInfo(i).getSpecialBuildingType() == CvUtil.findInfoTypeNum(gc.getSpecialBuildingInfo,gc.getNumSpecialBuildingInfos(),"SPECIALBUILDING_CHRISTIAN_MONASTERY")):
      #  iNumPoints += 2 * player.countNumBuildings(i)
      if (gc.getBuildingInfo(i).getSpecialBuildingType() == CvUtil.findInfoTypeNum(gc.getSpecialBuildingInfo,gc.getNumSpecialBuildingInfos(),"SPECIALBUILDING_TEMPLE")):
        iNumPoints += player.countNumBuildings(i)

  if player.countNumBuildings(gc.getInfoTypeForString("BUILDING_ORACLE2")) > 0: iNumPoints = iNumPoints * 2
  if player.countNumBuildings(gc.getInfoTypeForString("BUILDING_ORACLE")) > 0: iNumPoints = iNumPoints * 2

  if iNumPoints < gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() / 2:
    return False

  plot = gc.getMap().plot(kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY)
  if (plot == None):
    return False

  plot.setRevealed(player.getTeam(), True, True, -1)
  # for PAE and the black fog of war
  CvUtil.addScriptData(plot,"H","X")

  if (kTriggeredData.ePlayer == gc.getGame().getActivePlayer()):
    CyCamera().JustLookAtPlot( CyMap().plot( kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY ) )

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.iPlotX = kOrigTriggeredData.iPlotX
  kActualTriggeredDataObject.iPlotY = kOrigTriggeredData.iPlotY

  return True

def doHolyMountainRevealed(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  if (kTriggeredData.ePlayer == gc.getGame().getActivePlayer()):
    CyCamera().JustLookAtPlot( CyMap().plot( kTriggeredData.iPlotX, kTriggeredData.iPlotY ) )

  return 1

######## MARATHON ###########

def canTriggerMarathon(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  team = gc.getTeam(player.getTeam())

  if (team.AI_getAtWarCounter(otherPlayer.getTeam()) == 1):
    (loopUnit, iter) = otherPlayer.firstUnit(False)
    while( loopUnit ):
      plot = loopUnit.plot()
      if (not plot.isNone()):
        if (plot.getOwner() == kTriggeredData.ePlayer):
          return True
      (loopUnit, iter) = otherPlayer.nextUnit(iter, False)

  return False

######## WEDDING FEUD ###########

def doWeddingFeud2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  (loopCity, iter) = player.firstCity(False)

  while(loopCity):
    if loopCity.isHasReligion(kTriggeredData.eReligion):
      loopCity.changeHappinessTimer(30)
    (loopCity, iter) = player.nextCity(iter, False)

  return 1

def getHelpWeddingFeud2(argsList):
  iEvent = argsList[0]
  event = gc.getEventInfo(iEvent)
  kTriggeredData = argsList[1]
  religion = gc.getReligionInfo(kTriggeredData.eReligion)

  szHelp = localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_2_HELP", (gc.getDefineINT("TEMP_HAPPY"), 30, religion.getChar()))

  return szHelp

def canDoWeddingFeud3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getGold() - 10 * player.getNumCities() < 0:
    return False

  return True


def doWeddingFeud3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iLoopPlayer)
    if loopPlayer.isAlive() and loopPlayer.getStateReligion() == player.getStateReligion():
      loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
      player.AI_changeAttitudeExtra(iLoopPlayer, 1)

  if gc.getTeam(destPlayer.getTeam()).canDeclareWar(player.getTeam()):
    if destPlayer.isHuman():
      # this works only because it's a single-player only event
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
      popupInfo.setText(localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_OTHER_3", (gc.getReligionInfo(kTriggeredData.eReligion).getAdjectiveKey(), player.getCivilizationShortDescriptionKey())))
      popupInfo.setData1(kTriggeredData.eOtherPlayer)
      popupInfo.setData2(kTriggeredData.ePlayer)
      popupInfo.setPythonModule("CvRandomEventInterface")
      popupInfo.setOnClickedPythonCallback("weddingFeud3Callback")
      popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
      popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
      popupInfo.addPopup(kTriggeredData.eOtherPlayer)
    else:
      gc.getTeam(destPlayer.getTeam()).declareWar(player.getTeam(), False, WarPlanTypes.WARPLAN_LIMITED)

  return 1


def weddingFeud3Callback(argsList):
  iButton = argsList[0]
  iData1 = argsList[1]
  iData2 = argsList[2]
  iData3 = argsList[3]
  szText = argsList[4]
  bOption1 = argsList[5]
  bOption2 = argsList[6]

  if iButton == 0:
    destPlayer = gc.getPlayer(iData1)
    player = gc.getPlayer(iData2)
    gc.getTeam(destPlayer.getTeam()).declareWar(player.getTeam(), False, WarPlanTypes.WARPLAN_LIMITED)

  return 0

def getHelpWeddingFeud3(argsList):
  iEvent = argsList[0]
  event = gc.getEventInfo(iEvent)
  kTriggeredData = argsList[1]
  religion = gc.getReligionInfo(kTriggeredData.eReligion)

  szHelp = localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_3_HELP", (1, religion.getChar()))

  return szHelp

######## SPICY ###########

def canTriggerSpicy(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSpice = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_SPICES')
  iHappyBonuses = 0
  bSpices = False
  for i in range(gc.getNumBonusInfos()):
    bonus = gc.getBonusInfo(i)
    iNum = player.getNumAvailableBonuses(i)
    if iNum > 0 :
      if bonus.getHappiness() > 0:
        iHappyBonuses += 1
        if iHappyBonuses > 4:
          return False
      if i == iSpice:
        return False

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  if not plot.canHaveBonus(iSpice, False):
    return False

  return True

def doSpicy2(argsList):
#  need this because plantations are notmally not allowed unless there are already spices
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if not plot.isNone():
    plot.setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_PLANTATION'))

  return 1

def getHelpSpicy2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iPlantation = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_PLANTATION')
  szHelp = localText.getText("TXT_KEY_EVENT_IMPROVEMENT_GROWTH", ( gc.getImprovementInfo(iPlantation).getTextKey(), ))

  return szHelp

######## BABY BOOM ###########

def canTriggerBabyBoom(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  team = gc.getTeam(player.getTeam())

  if team.getAtWarCount(True) > 0:
    return False

  for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
    if iLoopTeam != player.getTeam():
      if team.AI_getAtPeaceCounter(iLoopTeam) == 1:
        return True

  return False

######## BARD TALE ###########

def applyBardTale3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  player.changeGold(-10 * player.getNumCities())

def canApplyBardTale3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getGold() - 10 * player.getNumCities() < 0:
    return False

  return True


def getHelpBardTale3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  szHelp = localText.getText("TXT_KEY_EVENT_GOLD_LOST", (10 * player.getNumCities(), ))

  return szHelp

######## BROTHERS IN NEED ###########

def canTriggerBrothersInNeed(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  if not player.canTradeNetworkWith(kTriggeredData.eOtherPlayer):
    return False

  listResources = []
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_COPPER'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IRON'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_HORSE'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IVORY'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_ZINN'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_BRONZE'))

  bFound = False
  for iResource in listResources:
    if (player.getNumTradeableBonuses(iResource) > 1 and otherPlayer.getNumAvailableBonuses(iResource) <= 0):
      bFound = True
      break

  if not bFound:
    return False

  for iTeam in range(gc.getMAX_CIV_TEAMS()):
    if iTeam != player.getTeam() and iTeam != otherPlayer.getTeam() and gc.getTeam(iTeam).isAlive():
      if gc.getTeam(iTeam).isAtWar(otherPlayer.getTeam()) and not gc.getTeam(iTeam).isAtWar(player.getTeam()):
        return True

  return False

def canDoBrothersInNeed1(argsList):
  kTriggeredData = argsList[1]
  newArgs = (kTriggeredData, )

  return canTriggerBrothersInNeed(newArgs)

######## HURRICANE ###########

def canTriggerHurricaneCity(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iCity = argsList[2]

  player = gc.getPlayer(ePlayer)
  city = player.getCity(iCity)

  if city.isNone():
    return False

  if not city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
    return False

  if city.plot().getLatitude() <= 0:
    return False

  if city.getPopulation() < 2:
    return False

  return True

def canApplyHurricane1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  city = player.getCity(kTriggeredData.iCityId)

  listBuildings = []
  for iBuilding in range(gc.getNumBuildingInfos()):
    if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
      listBuildings.append(iBuilding)

  return (len(listBuildings) > 0)

def canApplyHurricane2(argsList):
  return (not canApplyHurricane1(argsList))


def applyHurricane1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  city = player.getCity(kTriggeredData.iCityId)

  listCheapBuildings = []
  listExpensiveBuildings = []
  for iBuilding in range(gc.getNumBuildingInfos()):
    if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() <= 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
      listCheapBuildings.append(iBuilding)
    if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() > 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
      listExpensiveBuildings.append(iBuilding)

  if len(listCheapBuildings) > 0:
    iBuilding = listCheapBuildings[gc.getGame().getSorenRandNum(len(listCheapBuildings), "Hurricane event cheap building destroyed")]
    szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getBuildingInfo(iBuilding).getTextKey(), ))
    CyInterface().addMessage(kTriggeredData.ePlayer, False, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBuildingInfo(iBuilding).getButton(), gc.getInfoTypeForString("COLOR_RED"), city.getX(), city.getY(), True, True)
    city.setNumRealBuilding(iBuilding, 0)

  if len(listExpensiveBuildings) > 0:
    iBuilding = listExpensiveBuildings[gc.getGame().getSorenRandNum(len(listExpensiveBuildings), "Hurricane event expensive building destroyed")]
    szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getBuildingInfo(iBuilding).getTextKey(), ))
    CyInterface().addMessage(kTriggeredData.ePlayer, False, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBuildingInfo(iBuilding).getButton(), gc.getInfoTypeForString("COLOR_RED"), city.getX(), city.getY(), True, True)
    city.setNumRealBuilding(iBuilding, 0)


######## CYCLONE ###########

def canTriggerCycloneCity(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iCity = argsList[2]

  player = gc.getPlayer(ePlayer)
  city = player.getCity(iCity)

  if city.isNone():
    return False

  if not city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
    return False

  if city.plot().getLatitude() >= 0:
    return False

  return True

######## MONSOON ###########

def canTriggerMonsoonCity(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iCity = argsList[2]

  player = gc.getPlayer(ePlayer)
  city = player.getCity(iCity)

  if city.isNone():
    return False

  if city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
    return False

  iJungleType = CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(),'FEATURE_JUNGLE')

  for iDX in range(-3, 4):
    for iDY in range(-3, 4):
      pLoopPlot = plotXY(city.getX(), city.getY(), iDX, iDY)
      if not pLoopPlot.isNone() and pLoopPlot.getFeatureType() == iJungleType:
        return True

  return False

######## CHAMPION ###########

def canTriggerChampion(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  team = gc.getTeam(player.getTeam())

  if team.getAtWarCount(True) > 0:
    return False

  return True

def canTriggerChampionUnit(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iUnit = argsList[2]

  player = gc.getPlayer(ePlayer)
  unit = player.getUnit(iUnit)

  if unit.isNone():
    return False

  if unit.getDamage() > 0:
    return False

  if unit.getExperience() < 3:
    return False

  iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')
  if unit.isHasPromotion(iLeadership):
    return False

  return True

def applyChampion(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')

  unit.setHasPromotion(iLeadership, True)

def getHelpChampion(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')

  szHelp = localText.getText("TXT_KEY_EVENT_CHAMPION_HELP", (unit.getNameKey(), gc.getPromotionInfo(iLeadership).getTextKey()))

  return szHelp

######## GOLD RUSH ###########

def canTriggerGoldRush(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  iIndustrial = CvUtil.findInfoTypeNum(gc.getEraInfo,gc.getNumEraInfos(),'ERA_MEDIEVAL')

  if player.getCurrentEra() != iIndustrial:
    return False

  return True

######## INFLUENZA ###########

def canTriggerInfluenza(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  team = gc.getTeam(player.getTeam())

  iKlassik = CvUtil.findInfoTypeNum(gc.getEraInfo,gc.getNumEraInfos(),'ERA_MEDIEVAL')

  if player.getCurrentEra() <= iKlassik:
    return False

#  iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
#  iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
#  iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
  iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

  if team.isHasTech(iMedicine4):
    szBuffer = localText.getText("TXT_KEY_EVENT_INFLUENZA_TEAM_HEILKUNDE", ("", ))
    CyInterface().addMessage(kTriggeredData.ePlayer, False, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, None, gc.getInfoTypeForString("COLOR_GREEN"), 0, 0, False, False)
    return False

  return True

def applyInfluenza2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  eventCity = player.getCity(kTriggeredData.iCityId)

  iMaxCities = player.getNumCities()

  iNumCities = 2 + gc.getGame().getSorenRandNum(iMaxCities, "Influenza event number of cities")

  listCities = []
  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if loopCity.getPopulation() > 2:
      iDistance = plotDistance(eventCity.getX(), eventCity.getY(), loopCity.getX(), loopCity.getY())
      if iDistance > 0:
        listCities.append((iDistance, loopCity))
    (loopCity, iter) = player.nextCity(iter, False)

  listCities.sort()

  if iNumCities > len(listCities):
    iNumCities = len(listCities)

  for i in range(iNumCities):
    (iDist, loopCity) = listCities[i]
    loopCity.changePopulation(-2)
    szBuffer = localText.getText("TXT_KEY_EVENT_INFLUENZA_HIT_CITY", (loopCity.getNameKey(), ))
    CyInterface().addMessage(kTriggeredData.ePlayer, False, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, None, gc.getInfoTypeForString("COLOR_RED"), loopCity.getX(), loopCity.getY(), True, True)


def getHelpInfluenza2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_INFLUENZA_HELP_2", (2, ))

  return szHelp

######## ANTELOPE ###########

def canTriggerAntelope(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iDeer = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_DEER')
  iHappyBonuses = 0
  bDeer = False
  for i in range(gc.getNumBonusInfos()):
    bonus = gc.getBonusInfo(i)
    iNum = player.getNumAvailableBonuses(i)
    if iNum > 0 :
      if bonus.getHappiness() > 0:
        iHappyBonuses += 1
        if iHappyBonuses > 5:
          return False
      if i == iDeer:
        return False

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  if not plot.canHaveBonus(iDeer, False):
    return False

  return True

def doAntelope2(argsList):
#  Need this because camps are not normally allowed unless there is already deer.
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if not plot.isNone():
    plot.setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_CAMP'))

  return 1

def getHelpAntelope2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iCamp = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_CAMP')
  szHelp = localText.getText("TXT_KEY_EVENT_IMPROVEMENT_GROWTH", ( gc.getImprovementInfo(iCamp).getTextKey(), ))

  return szHelp

######## HIYOSILVER ###########

def canTriggerHiyoSilver(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSilver = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_SILVER')
  iHappyBonuses = 0
  bSilver = False
  for i in range(gc.getNumBonusInfos()):
    bonus = gc.getBonusInfo(i)
    iNum = player.getNumAvailableBonuses(i)
    if iNum > 0 :
      if bonus.getHappiness() > 0:
        iHappyBonuses += 1
        if iHappyBonuses > 5:
          return False
      if i == iSilver:
        return False

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  if not plot.canHaveBonus(iSilver, False):
    return False

  return True

######## WININGMONKS ###########

def canTriggerWiningMonks(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getNumAvailableBonuses(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_WINE')) > 0:
    return False

  return True


def doWiningMonks2(argsList):
#  Need this because wineries are not normally allowed unless there is already wine.
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if not plot.isNone():
    plot.setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_WINERY'))

  return 1

def getHelpWiningMonks2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iImp = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_WINERY')
  szHelp = localText.getText("TXT_KEY_EVENT_IMPROVEMENT_GROWTH", ( gc.getImprovementInfo(iImp).getTextKey(), ))

  return szHelp

######## ANCIENT OLYMPICS ###########

def doAncientOlympics2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  for j in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(j)
    if j != kTriggeredData.ePlayer and loopPlayer.isAlive() and not loopPlayer.isMinorCiv():

      for i in range(map.numPlots()):
        plot = map.plotByIndex(i)
        if not plot.isWater() and plot.getOwner() == kTriggeredData.ePlayer and plot.isAdjacentPlayer(j, True):
          loopPlayer.AI_changeMemoryCount(kTriggeredData.ePlayer, MemoryTypes.MEMORY_EVENT_GOOD_TO_US, 1)
          break

  return 1

def getHelpAncientOlympics2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_ANCIENTOLYMPICS_HELP_2", ( 1, ))

  return szHelp

######## HEROIC_GESTURE ###########

def canTriggerHeroicGesture(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  if not gc.getTeam(destPlayer.getTeam()).canChangeWarPeace(player.getTeam()):
    return False

  if gc.getTeam(destPlayer.getTeam()).AI_getWarSuccess(player.getTeam()) <= 0:
    return False

  if gc.getTeam(player.getTeam()).AI_getWarSuccess(destPlayer.getTeam()) <= 0:
    return False

  return True

def doHeroicGesture2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if destPlayer.isHuman():
    # this works only because it's a single-player only event
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText(localText.getText("TXT_KEY_EVENT_HEROIC_GESTURE_OTHER_3", (player.getCivilizationAdjectiveKey(), )))
    popupInfo.setData1(kTriggeredData.eOtherPlayer)
    popupInfo.setData2(kTriggeredData.ePlayer)
    popupInfo.setPythonModule("CvRandomEventInterface")
    popupInfo.setOnClickedPythonCallback("heroicGesture2Callback")
    popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
    popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
    popupInfo.addPopup(kTriggeredData.eOtherPlayer)
  else:
    destPlayer.forcePeace(kTriggeredData.ePlayer)
    destPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
    player.AI_changeAttitudeExtra(kTriggeredData.eOtherPlayer, 1)

  return

def heroicGesture2Callback(argsList):
  iButton = argsList[0]
  iData1 = argsList[1]
  iData2 = argsList[2]
  iData3 = argsList[3]
  szText = argsList[4]
  bOption1 = argsList[5]
  bOption2 = argsList[6]

  if iButton == 0:
    destPlayer = gc.getPlayer(iData1)
    player = gc.getPlayer(iData2)
    destPlayer.forcePeace(iData2)
    destPlayer.AI_changeAttitudeExtra(iData2, 1)
    player.AI_changeAttitudeExtra(iData1, 1)

  return 0

def getHelpHeroicGesture2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  # Get help text
  szHelp = localText.getText("TXT_KEY_EVENT_ATTITUDE_GOOD", (1, destPlayer.getNameKey()));

  return szHelp

######## GREAT_MEDIATOR ###########

def canTriggerGreatMediator(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  if not gc.getTeam(player.getTeam()).canChangeWarPeace(destPlayer.getTeam()):
    return False

  if gc.getTeam(player.getTeam()).AI_getAtWarCounter(destPlayer.getTeam()) < 10:
    return False

  return True

def doGreatMediator2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if destPlayer.isHuman():
    # this works only because it's a single-player only event
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText(localText.getText("TXT_KEY_EVENT_GREAT_MEDIATOR_OTHER_3", (player.getCivilizationAdjectiveKey(), )))
    popupInfo.setData1(kTriggeredData.eOtherPlayer)
    popupInfo.setData2(kTriggeredData.ePlayer)
    popupInfo.setPythonModule("CvRandomEventInterface")
    popupInfo.setOnClickedPythonCallback("greatMediator2Callback")
    popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
    popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
    popupInfo.addPopup(kTriggeredData.eOtherPlayer)
  else:
    gc.getTeam(player.getTeam()).makePeace(destPlayer.getTeam())
    destPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
    player.AI_changeAttitudeExtra(kTriggeredData.eOtherPlayer, 1)

  return

def greatMediator2Callback(argsList):
  iButton = argsList[0]
  iData1 = argsList[1]
  iData2 = argsList[2]
  iData3 = argsList[3]
  szText = argsList[4]
  bOption1 = argsList[5]
  bOption2 = argsList[6]

  if iButton == 0:
    destPlayer = gc.getPlayer(iData1)
    player = gc.getPlayer(iData2)
    gc.getTeam(destPlayer.getTeam()).makePeace(player.getTeam())
    destPlayer.AI_changeAttitudeExtra(iData2, 1)
    player.AI_changeAttitudeExtra(iData1, 1)

  return 0

def getHelpGreatMediator2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  # Get help text
  szHelp = localText.getText("TXT_KEY_EVENT_ATTITUDE_GOOD", (1, destPlayer.getNameKey()));

  return szHelp

######## ANCIENT_TEXTS ###########

def doAncientTexts2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive() and iPlayer != kTriggeredData.ePlayer:
      loopTeam = gc.getTeam(loopPlayer.getTeam())
      if loopTeam.isHasMet(gc.getPlayer(kTriggeredData.ePlayer).getTeam()):
        loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)

  return

def getHelpAncientTexts2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_TRIGGER_ANCIENT_TEXTS_1", (1, ))

  return szHelp

######## THE_HUNS ###########

def canTriggerTheHuns(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Horseback Riding.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_HORSEBACK_RIDING_3')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

  """
  # Can we build the counter unit?
  iCounterUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_SPEARMAN')
  iCounterUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iCounterUnitClass)
  if iCounterUnit == -1:
    return False

  (loopCity, iter) = player.firstCity(False)
  bFound = False
  while(loopCity):
    if (loopCity.canTrain(iCounterUnit, False, False)):
      bFound = True
      break

    (loopCity, iter) = player.nextCity(iter, False)

  if not bFound:
    return False
  """

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpTheHuns1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THE_HUNS_HELP_1", ())

  return szHelp


def applyTheHuns1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Hun event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 2
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 3
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 5
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 6
  else:
    iNumUnits  = 7

  iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_HORSE_ARCHER_SCYTHS')
  iUnitType2 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_MONGOL_KESHIK')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType1, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)
    barbPlayer.initUnit(iUnitType2, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)

######## THE_VANDALS ###########

def canTriggerTheVandals(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Buergersoldaten.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_BUERGERSOLDATEN')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

  # Can we build the counter unit?
  iCounterUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_AXEMAN')
  iCounterUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iCounterUnitClass)
  if iCounterUnit == -1:
    return False

  (loopCity, iter) = player.firstCity(False)
  bFound = False
  while(loopCity):
    if (loopCity.canTrain(iCounterUnit, False, False)):
      bFound = True
      break

    (loopCity, iter) = player.nextCity(iter, False)

  if not bFound:
    return False

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpTheVandals1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THE_VANDALS_HELP_1", ())

  return szHelp


def applyTheVandals1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Vandal event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 8
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 10
  else:
    iNumUnits  = 12

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_CELTIC_GALLIC_WARRIOR')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)


######## THE_GOTHS ###########

def canTriggerTheGoths(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Mathematics.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_MATHEMATICS')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#   At least one civ on the board must know Iron Working.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_KETTENPANZER')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpTheGoths1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THE_GOTHS_HELP_1", ())

  return szHelp


def applyTheGoths1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Goth event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 8
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 10
  else:
    iNumUnits  = 12

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_STAMMESFUERST')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)


######## THE_PHILISTINES ###########

def canTriggerThePhilistines(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Monotheism.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_MONOTHEISM')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#   At least one civ on the board must know Breitschwert und Schild.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_BEWAFFNUNG4')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

  # Can we build the counter unit?
  iCounterUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_AXEMAN')
  iCounterUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iCounterUnitClass)
  if iCounterUnit == -1:
    return False

  (loopCity, iter) = player.firstCity(False)
  bFound = False
  while(loopCity):
    if (loopCity.canTrain(iCounterUnit, False, False)):
      bFound = True
      break

    (loopCity, iter) = player.nextCity(iter, False)

  if not bFound:
    return False

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpThePhilistines1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THE_PHILISTINES_HELP_1", ())

  return szHelp


def applyThePhilistines1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Philistine event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 8
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 10
  else:
    iNumUnits  = 12

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PHILISTER')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)


######## THE_VEDIC_ARYANS ###########

def canTriggerTheVedicAryans(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Polytheism.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_VASALLENTUM')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#   At least one civ on the board must know Archery.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_ARMOR')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

  # Can we build the counter unit?
  iCounterUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_ARCHER')
  iCounterUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iCounterUnitClass)
  if iCounterUnit == -1:
    return False

  (loopCity, iter) = player.firstCity(False)
  bFound = False
  while(loopCity):
    if (loopCity.canTrain(iCounterUnit, False, False)):
      bFound = True
      break

    (loopCity, iter) = player.nextCity(iter, False)

  if not bFound:
    return False

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpTheVedicAryans1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THE_VEDIC_ARYANS_HELP_1", ())

  return szHelp


def applyTheVedicAryans1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Vedic Aryan event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 6
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 8
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 10
  else:
    iNumUnits  = 12

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_RADSCHA')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)

######## SECURITY_TAX ###########

def canTriggerSecurityTax(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iWalls = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_WALLS')
  if player.getNumCities() > player.getBuildingClassCount(iWalls):
    return False

  return True


######## LITERACY ###########

def canTriggerLiteracy(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iLibrary = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_LIBRARY')
  if player.getNumCities() > player.getBuildingClassCount(iLibrary):
    return False

  return True

######## HORSE WHISPERING ###########

def canTriggerHorseWhispering(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True

def getHelpHorseWhispering1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iNumStables = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers()
  szHelp = localText.getText("TXT_KEY_EVENT_HORSE_WHISPERING_HELP", (iNumStables, ))

  return szHelp

def canTriggerHorseWhisperingDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iStable = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_STABLE')
  if gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() > player.getBuildingClassCount(iStable):
    return False

  return True

def getHelpHorseWhisperingDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iNumUnits = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers()
  szHelp = localText.getText("TXT_KEY_EVENT_HORSE_WHISPERING_DONE_HELP_1", (iNumUnits, ))

  return szHelp

def applyHorseWhisperingDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  map = gc.getMap()
  plot = map.plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  iNumUnits = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers()
  iUnitClassType = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_HORSE_ARCHER')
  iUnitType = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iUnitClassType)

  if iUnitType != -1:
    for i in range(iNumUnits):
      player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

######## CLASSIC LITERATURE ###########

def canTriggerClassicLiterature(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True

def getHelpClassicLiterature1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iLibrariesRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()

  szHelp = localText.getText("TXT_KEY_EVENT_CLASSIC_LITERATURE_HELP_1", (iLibrariesRequired, ))

  return szHelp


def canTriggerClassicLiteratureDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iLibrary = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_LIBRARY')
  iBuildingsRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()
  if iBuildingsRequired > player.getBuildingClassCount(iLibrary):
    return False

  return True

def getHelpClassicLiteratureDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_CLASSIC_LITERATURE_DONE_HELP_2", ( ))

  return szHelp

def canApplyClassicLiteratureDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iEraAncient = CvUtil.findInfoTypeNum(gc.getEraInfo, gc.getNumEraInfos(), 'ERA_MEDIEVAL')

  for iTech in range(gc.getNumTechInfos()):
    if gc.getTechInfo(iTech).getEra() == iEraAncient and player.canResearch(iTech, False):
      return True

  return False

def applyClassicLiteratureDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iEraAncient = CvUtil.findInfoTypeNum(gc.getEraInfo, gc.getNumEraInfos(), 'ERA_MEDIEVAL')

  listTechs = []
  for iTech in range(gc.getNumTechInfos()):
    if gc.getTechInfo(iTech).getEra() == iEraAncient and player.canResearch(iTech, False):
      listTechs.append(iTech)

  if len(listTechs) > 0:
    iTech = listTechs[gc.getGame().getSorenRandNum(len(listTechs), "Classic Literature Event Tech selection")]
    gc.getTeam(player.getTeam()).setHasTech(iTech, True, kTriggeredData.ePlayer, True, True)

def getHelpClassicLiteratureDone3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSpecialist = CvUtil.findInfoTypeNum(gc.getSpecialistInfo, gc.getNumSpecialistInfos(), 'SPECIALIST_SCIENTIST', )
  iGreatLibrary = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_LIBRARY')

  szCityName = u""
  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iGreatLibrary)):
      szCityName = loopCity.getNameKey()
      break

    (loopCity, iter) = player.nextCity(iter, False)

  szHelp = localText.getText("TXT_KEY_EVENT_FREE_SPECIALIST", (1, gc.getSpecialistInfo(iSpecialist).getTextKey(), szCityName))

  return szHelp

def canApplyClassicLiteratureDone3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iGreatLibrary = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_LIBRARY')

  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iGreatLibrary)):
      return True

    (loopCity, iter) = player.nextCity(iter, False)

  return False

def applyClassicLiteratureDone3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSpecialist = CvUtil.findInfoTypeNum(gc.getSpecialistInfo, gc.getNumSpecialistInfos(), 'SPECIALIST_SCIENTIST', )
  iGreatLibrary = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_LIBRARY')

  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iGreatLibrary)):
      loopCity.changeFreeSpecialistCount(iSpecialist, 1)
      return

    (loopCity, iter) = player.nextCity(iter, False)

######## MASTER BLACKSMITH ###########

def canTriggerMasterBlacksmith(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True

def getHelpMasterBlacksmith1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()

  szHelp = localText.getText("TXT_KEY_EVENT_MASTER_BLACKSMITH_HELP_1", (iRequired, player.getCity(kTriggeredData.iCityId).getNameKey()))

  return szHelp

def expireMasterBlacksmith1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  city = player.getCity(kTriggeredData.iCityId)
  if city == None or city.getOwner() != kTriggeredData.ePlayer:
    return True

  return False

def canTriggerMasterBlacksmithDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iForge = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_FORGE')
  iBuildingsRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()
  if iBuildingsRequired > player.getBuildingClassCount(iForge):
    return False

  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

  city = player.getCity(kOrigTriggeredData.iCityId)
  if city == None or city.getOwner() != kTriggeredData.ePlayer:
    return False

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.iCityId = kOrigTriggeredData.iCityId

  return True

def canApplyMasterBlacksmithDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iBonus = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_COPPER')
  city = player.getCity(kTriggeredData.iCityId)

  if city == None:
    return False

  map = gc.getMap()
  iBestValue = map.getGridWidth() + map.getGridHeight()
  bestPlot = None
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == kTriggeredData.ePlayer and plot.canHaveBonus(iBonus, False)):
      iValue = plotDistance(city.getX(), city.getY(), plot.getX(), plot.getY())
      if iValue < iBestValue:
        iBestValue = iValue
        bestPlot = plot

  if bestPlot == None:
    return False

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.iPlotX = bestPlot.getX()
  kActualTriggeredDataObject.iPlotY = bestPlot.getY()

  return True

def applyMasterBlacksmithDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  city = player.getCity(kTriggeredData.iCityId)

  iBonus = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_COPPER')
  plot.setBonusType(iBonus)

  szBuffer = localText.getText("TXT_KEY_MISC_DISCOVERED_NEW_RESOURCE", (gc.getBonusInfo(iBonus).getTextKey(), city.getNameKey()))
  CyInterface().addMessage(kTriggeredData.ePlayer, False, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_DISCOVERBONUS", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, gc.getBonusInfo(iBonus).getButton(), gc.getInfoTypeForString("COLOR_WHITE"), plot.getX(), plot.getY(), True, True)

def canApplyMasterBlacksmithDone3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getStateReligion() == -1:
    return False

  return True

######## NATIONAL SPORTS LEAGUE ###########

def canTriggerSportsLeague(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True
def getHelpSportsLeague1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()
  iBuilding = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_STATUE_OF_ZEUS')

  szHelp = localText.getText("TXT_KEY_EVENT_SPORTS_LEAGUE_HELP_1", (iRequired, gc.getBuildingInfo(iBuilding).getTextKey()))

  return szHelp

def canTriggerSportsLeagueDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iCastle = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_HIPPODROME')
  iBuildingsRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()
  if iBuildingsRequired > player.getBuildingClassCount(iCastle):
    return False

  return True

def canApplySportsLeagueDone3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iZeus = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_STATUE_OF_ZEUS')

  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iZeus)):
      return True

    (loopCity, iter) = player.nextCity(iter, False)

  return False

######## SECRET_KNOWLEDGE ###########

def getHelpSecretKnowledge2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  szHelp = localText.getText("TXT_KEY_EVENT_YIELD_CHANGE_BUILDING", (gc.getBuildingInfo(kTriggeredData.eBuilding).getTextKey(), u"+4[ICON_CULTURE]"))

  return szHelp

def applySecretKnowledge2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  city = player.getCity(kTriggeredData.iCityId)
  city.setBuildingCommerceChange(gc.getBuildingInfo(kTriggeredData.eBuilding).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, 4)

######## EXPERIENCED_CAPTAIN ###########

def canTriggerExperiencedCaptain(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  if unit.isNone():
    return False

  if unit.getExperience() < 7:
    return False

  return True

######## GREED ###########

def canTriggerGreed(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  if not gc.getTeam(player.getTeam()).canChangeWarPeace(otherPlayer.getTeam()):
    return False

  listBonuses = []
  iIron = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IRON')
  if 0 == player.getNumAvailableBonuses(iIron):
    listBonuses.append(iIron)
  iHorse = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_HORSE')
  if 0 == player.getNumAvailableBonuses(iHorse):
    listBonuses.append(iHorse)
  iCopper = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_COPPER')
  if 0 == player.getNumAvailableBonuses(iCopper):
    listBonuses.append(iCopper)
  iZinn = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_ZINN')
  if 0 == player.getNumAvailableBonuses(iZinn):
    listBonuses.append(iZinn)

  map = gc.getMap()
  bFound = False
  listPlots = []
  for iBonus in listBonuses:
    for i in range(map.numPlots()):
      loopPlot = map.plotByIndex(i)
      if loopPlot.getOwner() == kTriggeredData.eOtherPlayer and loopPlot.getBonusType(player.getTeam()) == iBonus and loopPlot.isRevealed(player.getTeam(), False) and not loopPlot.isWater():
        listPlots.append(loopPlot)
        bFound = True
    if bFound:
      break

  if not bFound:
    return False

  plot = listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Greed event plot selection")]

  if -1 == getGreedUnit(player, plot):
    return False

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.iPlotX = plot.getX()
  kActualTriggeredDataObject.iPlotY = plot.getY()

  return True

def getHelpGreed1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  iBonus = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY).getBonusType(player.getTeam())

  iTurns = gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGrowthPercent()

  szHelp = localText.getText("TXT_KEY_EVENT_GREED_HELP_1", (otherPlayer.getCivilizationShortDescriptionKey(), gc.getBonusInfo(iBonus).getTextKey(), iTurns))

  return szHelp

def expireGreed1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if plot.getOwner() == kTriggeredData.ePlayer or plot.getOwner() == -1:
    return False

  if gc.getGame().getGameTurn() >= kTriggeredData.iTurn + gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGrowthPercent():
    return True

  if plot.getOwner() != kTriggeredData.eOtherPlayer:
    return True

  return False

def canTriggerGreedDone(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))
  plot = gc.getMap().plot(kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY)

  if plot.getOwner() != kOrigTriggeredData.ePlayer:
    return False

  if -1 == getGreedUnit(player, plot):
    return False

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.iPlotX = kOrigTriggeredData.iPlotX
  kActualTriggeredDataObject.iPlotY = kOrigTriggeredData.iPlotY
  kActualTriggeredDataObject.eOtherPlayer = kOrigTriggeredData.eOtherPlayer

  return True

def getGreedUnit(player, plot):
  iBonus = plot.getBonusType(player.getTeam())
  iBestValue = 0
  iBestUnit = -1
  for iUnitClass in range(gc.getNumUnitClassInfos()):
    iUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iUnitClass)
    if -1 != iUnit and player.canTrain(iUnit, False, False) and (gc.getUnitInfo(iUnit).getDomainType() == DomainTypes.DOMAIN_LAND):
      iValue = 0
      if gc.getUnitInfo(iUnit).getPrereqAndBonus() == iBonus:
        iValue = player.AI_unitValue(iUnit, UnitAITypes.UNITAI_ATTACK, plot.area())
      else:
        for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
          if (gc.getUnitInfo(iUnit).getPrereqOrBonuses(j) == iBonus):
            iValue = player.AI_unitValue(iUnit, UnitAITypes.UNITAI_ATTACK, plot.area())
            break
      if iValue > iBestValue:
        iBestValue = iValue
        iBestUnit = iUnit

  return iBestUnit


def getHelpGreedDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() / 2 + 1
  iUnitType = getGreedUnit(player, plot)

  if iUnitType != -1:
    szHelp = localText.getText("TXT_KEY_EVENT_GREED_DONE_HELP_1", (iNumUnits, gc.getUnitInfo(iUnitType).getTextKey()))

  return szHelp

def applyGreedDone1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iUnitType = getGreedUnit(player, plot)
  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() / 2 + 1

  if iUnitType != -1:
    for i in range(iNumUnits):
      player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)


######## WAR CHARIOTS ###########

def canTriggerWarChariots(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.eReligion = ReligionTypes(player.getStateReligion())

  return True

def getHelpWarChariots1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 1
  szHelp = localText.getText("TXT_KEY_EVENT_WAR_CHARIOTS_HELP_1", (iNumUnits, ))

  return szHelp

def canTriggerWarChariotsDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 1
  iUnitClassType1 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_CHARIOT')
  iUnitClassType2 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_CHARIOT_ARCHER')
  iUnitClassType3 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_WAR_CHARIOT')
  if player.getUnitClassCount(iUnitClassType1) + player.getUnitClassCount(iUnitClassType2) + player.getUnitClassCount(iUnitClassType3) < iNumUnits:
    return False

  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))
  kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
  kActualTriggeredDataObject.eReligion = kOrigTriggeredData.eReligion

  return True

def getHelpWarChariotsDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSpecialist = CvUtil.findInfoTypeNum(gc.getSpecialistInfo, gc.getNumSpecialistInfos(), 'SPECIALIST_GREAT_GENERAL', )
  iPferdezucht = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_PFERDEZUCHT')

  szCityName = u""
  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iPferdezucht)):
      szCityName = loopCity.getNameKey()
      break

    (loopCity, iter) = player.nextCity(iter, False)

  szHelp = localText.getText("TXT_KEY_EVENT_FREE_SPECIALIST", (1, gc.getSpecialistInfo(iSpecialist).getTextKey(), szCityName))

  return szHelp

def canApplyWarChariotsDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iPferdezucht = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_PFERDEZUCHT')

  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iPferdezucht)):
      return True

    (loopCity, iter) = player.nextCity(iter, False)

  return False

def applyWarChariotsDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iSpecialist = CvUtil.findInfoTypeNum(gc.getSpecialistInfo, gc.getNumSpecialistInfos(), 'SPECIALIST_GREAT_GENERAL', )
  iPferdezucht = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_PFERDEZUCHT')

  (loopCity, iter) = player.firstCity(False)
  while(loopCity):
    if (loopCity.isHasBuilding(iPferdezucht)):
      loopCity.changeFreeSpecialistCount(iSpecialist, 1)
      return

    (loopCity, iter) = player.nextCity(iter, False)

######## ELITE SWORDSMEN ###########

def getHelpEliteSwords1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 1
  szHelp = localText.getText("TXT_KEY_EVENT_ELITE_SWORDS_HELP_1", (iNumUnits, ))

  return szHelp

def canTriggerEliteSwordsDone(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 1
  iUnitClassType1 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_KURZSCHWERT')
  iUnitClassType2 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_SCHILDTRAEGER')
  iUnitClassType3 = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_SWORDSMAN')
  iUnits = player.getUnitClassCount(iUnitClassType1) + player.getUnitClassCount(iUnitClassType2) + player.getUnitClassCount(iUnitClassType3)
  if iUnits < iNumUnits:
    return False

  return True


def canApplyEliteSwordsDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iCivic = CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_ROYAL')

  if not player.isCivic(iCivic):
    return False

  return True

######## WARSHIPS ###########

def canTriggerWarships(argsList):
  kTriggeredData = argsList[0]

  map = gc.getMap()
  iNumWater = 0

  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)

    if plot.isWater():
      iNumWater += 1

    if 100 * iNumWater >= 20 * map.numPlots():
      return True

  return False

def getHelpWarships1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()

  iBuilding = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_LIGHTHOUSE')
  szHelp = localText.getText("TXT_KEY_EVENT_WARSHIPS_HELP_1", (iNumUnits, gc.getBuildingInfo(iBuilding).getTextKey()))

  return szHelp

def canTriggerWarshipsDone(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()
  iUnitClassType = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_TRIREME')

  if player.getUnitClassCount(iUnitClassType) < iNumUnits:
    return False

  return True


def canApplyWarshipsDone2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iBuilding = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_LIGHTHOUSE')
  if player.getBuildingClassCount(gc.getBuildingInfo(iBuilding).getBuildingClassType()) == 0:
    return False

  return True

######## Great Beast ########

def doGreatBeast3(argsList):
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  (loopCity, iter) = player.firstCity(False)

  while(loopCity):
    if loopCity.isHasReligion(kTriggeredData.eReligion):
      loopCity.changeHappinessTimer(40)
    (loopCity, iter) = player.nextCity(iter, False)

def getHelpGreatBeast3(argsList):
  kTriggeredData = argsList[1]
  religion = gc.getReligionInfo(kTriggeredData.eReligion)

  szHelp = localText.getText("TXT_KEY_EVENT_GREAT_BEAST_3_HELP", (gc.getDefineINT("TEMP_HAPPY"), 40, religion.getChar()))

  return szHelp

####### Immigrants ########

def canTriggerImmigrantCity(argsList):
  ePlayer = argsList[1]
  iCity = argsList[2]

  player = gc.getPlayer(ePlayer)
  city = player.getCity(iCity)

  if city.isNone():
    return False

  if ((city.happyLevel() - city.unhappyLevel(0) < 1) or (city.goodHealth() - city.badHealth(True) < 1)):
    return False

  if (city.getCommerceRateTimes100(CommerceTypes.COMMERCE_CULTURE) < 5500):
    return False

####### Controversial Philosopher ######

def canTriggerControversialPhilosopherCity(argsList):
  ePlayer = argsList[1]
  iCity = argsList[2]

  player = gc.getPlayer(ePlayer)
  city = player.getCity(iCity)

  if city.isNone():
    return False
  if (not city.isCapital()):
    return False
  if (city.getCommerceRateTimes100(CommerceTypes.COMMERCE_RESEARCH) < 3500):
    return False

  return True

######## Preaching Researcher #######

def canTriggerPreachingResearcherCity(argsList):
  iCity = argsList[2]

  player = gc.getPlayer(argsList[1])
  city = player.getCity(iCity)

  if city.isHasBuilding(gc.getInfoTypeForString("BUILDING_GYMNASION")) or city.isHasBuilding(gc.getInfoTypeForString("BUILDING_SCHULE")):
    return True
  return False

######## Dissident Priest (Egyptian event) #######

def canTriggerDissidentPriestCity(argsList):
  iCity = argsList[2]

  player = gc.getPlayer(argsList[1])
  city = player.getCity(iCity)

  if city.isGovernmentCenter():
    return False
  if (city.getCommerceRateTimes100(CommerceTypes.COMMERCE_CULTURE) < 3000):
    return False
  if (player.getStateReligion() != -1):
    return False

  return True

######## ABRAHAM ###########

def canTriggerAbraham(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if (player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL")):
    return True
  return False

######## GROSSESAQUEDUCT ###########

import CvUtil
from CvPythonExtensions import *

gc = CyGlobalContext()
localText = CyTranslator()


def canTriggerGrossesAqueduct(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True

def getHelpGrossesAqueduct1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iNumGrossesAqueduct = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers()
  szHelp = localText.getText("TXT_KEY_EVENT_GROSSES_AQUEDUCT_HELP", (iNumGrossesAqueduct, ))

  return szHelp

def canTriggerGrossesAqueductDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iGrossesAqueduct = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_AQUEDUCT')
  if gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() > player.getBuildingClassCount(iGrossesAqueduct):
    return False

  return True

######## HUNTER ###########

def canTriggerHunterUnit(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iUnit = argsList[2]

  player = gc.getPlayer(ePlayer)
  unit = player.getUnit(iUnit)

  if unit.isNone():
    return False

  iSentry = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SENTRY')
  if unit.isHasPromotion(iSentry):
    return False

  iWildlife = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_WILDLIFE')
  if unit.isHasPromotion(iWildlife):
    return True

  return False

def applyHunter(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iSentry = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SENTRY')

  unit.setHasPromotion(iSentry, True)

def getHelpHunter(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iSentry = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SENTRY')

  szHelp = localText.getText("TXT_KEY_EVENT_HUNTER_HELP", (unit.getNameKey(), gc.getPromotionInfo(iSentry).getTextKey()))

  return szHelp

######## KILIKIEN ###########

def canTriggerKilikien(argsList):

        kTriggeredData = argsList[0]
        pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
        map = gc.getMap()

#   If Barbarians are disabled in this game, this event will not occur.
        if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
                return False

#   At least one civ on the board must know Sailing.
        bFoundValid = false
        iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_WARSHIPS2')
        for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
                loopPlayer = gc.getPlayer(iPlayer)
                if loopPlayer.isAlive():
                        if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
                                bFoundValid = true
                                break

        if not bFoundValid:
                return False

#        Find an eligible plot
        map = gc.getMap()
        for i in range(map.numPlots()):
                plot = map.plotByIndex(i)
                if (plot.getOwner() == -1 and plot.isWater() and not plot.isImpassable() and not plot.getNumUnits() > 0 and not plot.isLake() and plot.isAdjacentPlayer(kTriggeredData.ePlayer, true)):
                        return True

        return False

def getHelpKilikien1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        szHelp = localText.getText("TXT_KEY_EVENT_KILIKIEN_HELP_1", ())

        return szHelp

def applyKilikien1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        pPlayer = gc.getPlayer(kTriggeredData.ePlayer)

        listPlots = []
        map = gc.getMap()
        for i in range(map.numPlots()):
                plot = map.plotByIndex(i)
                if (plot.getOwner() == -1 and plot.isWater() and not plot.isImpassable() and not plot.getNumUnits() > 0 and not plot.isLake() and plot.isAdjacentPlayer(kTriggeredData.ePlayer, true)):
                        listPlots.append(i)

        if 0 == len(listPlots):
                return

        plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Kilikien event location")])

        if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
                iNumUnit1  = 1
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
                iNumUnit1  = 1
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
                iNumUnit1  = 1
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
                iNumUnit1  = 2
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
                iNumUnit1  = 3
        else:
                iNumUnit1  = 3

        iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_KILIKIEN')
        barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
        for i in range(iNumUnit1):
                barbPlayer.initUnit(iUnitType1, plot.getX(), plot.getY(), UnitAITypes.UNITAI_PIRATE_SEA, DirectionTypes.DIRECTION_SOUTH)

######## MOOR ###########

def canTriggerMoor(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  if unit.isNone():
    return False

  iSumpf = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SUMPF1')
  if unit.isHasPromotion(iSumpf):
    return False

  return True

######## MOORPROMO ###########

def canTriggerMoorPromo(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  if unit.isNone():
    return False

  if unit.getExperience() < 5:
    return False

  iSumpf = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SUMPF1')
  if unit.isHasPromotion(iSumpf):
    return False

  return True

def canTriggerMoorPromoUnit(argsList):
  eTrigger = argsList[0]
  ePlayer = argsList[1]
  iUnit = argsList[2]

  player = gc.getPlayer(ePlayer)
  unit = player.getUnit(iUnit)

  if unit.isNone():
    return False

  if unit.getExperience() < 7:
    return False

  iSumpf = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SUMPF1')
  if unit.isHasPromotion(iSumpf):
    return False

  return True

def applyMoorPromo(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iSumpf = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SUMPF1')

  unit.setHasPromotion(iSumpf, True)

def getHelpMoorPromo(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  iSumpf = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_SUMPF1')

  szHelp = localText.getText("TXT_KEY_EVENT_MOORPROMO_HELP", (unit.getNameKey(), gc.getPromotionInfo(iSumpf).getTextKey()))

  return szHelp

######## Leprakolo ###########

def canTriggerLeprakolo(argsList):
  kTriggeredData = argsList[0]

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  return True

def getHelpLeprakolo1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iNumLeprakolo = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers()
  szHelp = localText.getText("TXT_KEY_EVENT_LEPRAKOLO_HELP", (iNumLeprakolo, ))

  return szHelp

def canTriggerLeprakoloDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iLeprakolo = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_LEPRAKOLONIE')
  if gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() > player.getBuildingClassCount(iLeprakolo):
    return False

  return True

######## PIRATEN ###########

def canTriggerPiraten(argsList):

        kTriggeredData = argsList[0]
        pPlayer = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
        if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
                return False

#   At least one civ on the board must know Piracy.
        bFoundValid = false
        iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_PIRACY')
        for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
                loopPlayer = gc.getPlayer(iPlayer)
                if loopPlayer.isAlive():
                        if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
                                bFoundValid = true
                                break

        if not bFoundValid:
                return False

#   Find an eligible plot
        map = gc.getMap()
        for i in range(map.numPlots()):
                plot = map.plotByIndex(i)
                if (plot.getOwner() == -1 and plot.isWater() and not plot.isImpassable() and not plot.getNumUnits() > 0 and not plot.isLake() and plot.isAdjacentPlayer(kTriggeredData.ePlayer, true)):
                        return True

        return False

def getHelpPiraten1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        szHelp = localText.getText("TXT_KEY_EVENT_PIRATEN_HELP_1", ())

        return szHelp

def applyPiraten1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        pPlayer = gc.getPlayer(kTriggeredData.ePlayer)

        listPlots = []
        map = gc.getMap()
        for i in range(map.numPlots()):
                plot = map.plotByIndex(i)
                if (plot.getOwner() == -1 and plot.isWater() and not plot.isImpassable() and not plot.getNumUnits() > 0 and not plot.isLake() and plot.isAdjacentPlayer(kTriggeredData.ePlayer, true)):
                        listPlots.append(i)

        if 0 == len(listPlots):
                return

        plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Piraten event location")])

        if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
                iNumUnit1  = 2
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
                iNumUnit1  = 2
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
                iNumUnit1  = 3
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
                iNumUnit1  = 4
        elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
                iNumUnit1  = 5
        else:
                iNumUnit1  = 5

        iTech1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_RUDERER2')
        iTech2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_RUDERER3')
        iTech3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_WARSHIPS2')
        if gc.getTeam(pPlayer.getTeam()).isHasTech(iTech3):
          iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PIRAT_LIBURNE')
        elif gc.getTeam(pPlayer.getTeam()).isHasTech(iTech2):
          iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PIRAT_TRIREME')
        elif gc.getTeam(pPlayer.getTeam()).isHasTech(iTech1):
          iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PIRAT_BIREME')
        else:
          iUnitType1 = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PIRAT_KONTERE')

        barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
        for i in range(iNumUnit1):
                barbPlayer.initUnit(iUnitType1, plot.getX(), plot.getY(), UnitAITypes.UNITAI_PIRATE_SEA, DirectionTypes.DIRECTION_SOUTH)

######## Spartacus ###########

def canTriggerSpartacus(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Mathematics.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_GLADIATOR2')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#  Find an eligible plot
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == kTriggeredData.ePlayer and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False

def getHelpSpartacus1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_SPARTACUS_HELP_1", ())

  return szHelp

def applySpartacus1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == kTriggeredData.ePlayer and not plot.isWater() and not plot.isImpassable() and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Spartacus event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 2
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 2
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 2
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 3
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 4
  else:
    iNumUnits  = 5

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GLADIATOR')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)

######## TROJA ###########

def doTroja2(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iLoopPlayer)
    if loopPlayer.isAlive() and loopPlayer.getStateReligion() == player.getStateReligion():
      loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
      player.AI_changeAttitudeExtra(iLoopPlayer, 2)

  return 1

def getHelpTroja2(argsList):
  iEvent = argsList[0]
  event = gc.getEventInfo(iEvent)
  kTriggeredData = argsList[1]
  religion = gc.getReligionInfo(kTriggeredData.eReligion)

  szHelp = localText.getText("TXT_KEY_EVENT_TROJA_HELP_2", (1, religion.getChar()))

  return szHelp

def doTroja3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iLoopPlayer)
    if loopPlayer.isAlive() and loopPlayer.getStateReligion() == player.getStateReligion():
      loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 3)
      player.AI_changeAttitudeExtra(iLoopPlayer, 3)

  return 1

def getHelpTroja3(argsList):
  iEvent = argsList[0]
  event = gc.getEventInfo(iEvent)
  kTriggeredData = argsList[1]
  religion = gc.getReligionInfo(kTriggeredData.eReligion)

  szHelp = localText.getText("TXT_KEY_EVENT_TROJA_HELP_3", (1, religion.getChar()))

  return szHelp

######## ZAUBERTRANK ###########

def canTriggerZaubertrank(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if (player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT")):
      return True
  if (player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GALLIEN")):
      return True
  return False

######## OREICHALKOS ###########

def canTriggerOreichalkos(argsList):

        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        iOreichalkos = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_OREICHALKOS')
        if player.getNumAvailableBonuses(iOreichalkos) > 0:
                return false

        return true

def doOreichalkos2(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
        city = player.getCity(kTriggeredData.iCityId)

        iOreichalkos = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_OREICHALKOS')
        plot.setBonusType(iOreichalkos)

        szBuffer = localText.getText("TXT_KEY_MISC_DISCOVERED_NEW_RESOURCE", (gc.getBonusInfo(iOreichalkos).getTextKey(), city.getNameKey()))
        CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_DISCOVERBONUS", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, gc.getBonusInfo(iOreichalkos).getButton(), gc.getInfoTypeForString("COLOR_WHITE"), plot.getX(), plot.getY(), true, true)

def getHelpOreichalkos2(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        iBonus = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_OREICHALKOS')
        szHelp = localText.getText("TXT_KEY_EVENT_GET_BONUS_HELP", (gc.getBonusInfo(iBonus).getTextKey(),""))

        return szHelp

######## MAGNETIT ###########

def canTriggerMagnetit(argsList):

        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        iMagnetit = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_MAGNETIT')
        if player.getNumAvailableBonuses(iMagnetit) > 0:
                return false

        return true

def doMagnetit2(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
        city = player.getCity(kTriggeredData.iCityId)

        iMagnetit = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_MAGNETIT')
        plot.setBonusType(iMagnetit)

        szBuffer = localText.getText("TXT_KEY_MISC_DISCOVERED_NEW_RESOURCE", (gc.getBonusInfo(iMagnetit).getTextKey(), city.getNameKey()))
        CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_DISCOVERBONUS", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, gc.getBonusInfo(iMagnetit).getButton(), gc.getInfoTypeForString("COLOR_WHITE"), plot.getX(), plot.getY(), true, true)

def getHelpMagnetit2(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        iBonus = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_MAGNETIT')
        szHelp = localText.getText("TXT_KEY_EVENT_GET_BONUS_HELP", (gc.getBonusInfo(iBonus).getTextKey(),""))

        return szHelp

######## FRAUENHAAR ###########

def canTriggerFrauenhaar(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if (player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT")):
      return True
  if (player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GALLIEN")):
      return True
  return False

######## ARCHER ###########

def getHelpArcher1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5
  szHelp = localText.getText("TXT_KEY_EVENT_ARCHER_HELP_1", (iNumUnits, ))

  return szHelp

def canTriggerArcherDone(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5
  iUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_REFLEX_ARCHER')
  iUnits = player.getUnitClassCount(iUnitClass)
  if iUnits < iNumUnits:
    return False

  return True

######## ELEFANTEN ###########

def getHelpElefanten1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5
  szHelp = localText.getText("TXT_KEY_EVENT_ELEFANTEN_HELP_1", (iNumUnits, ))

  return szHelp

def canTriggerElefantenDone(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iNumUnits = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5
  iUnitClass = CvUtil.findInfoTypeNum(gc.getUnitClassInfo, gc.getNumUnitClassInfos(), 'UNITCLASS_WAR_ELEPHANT')
  iUnits = player.getUnitClassCount(iUnitClass)
  if iUnits < iNumUnits:
    return False

  return True

#### PROVINZHS ####

def canTriggerProvinzHS(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  if player.getNumCities() < 10:
    return False

  return True

def getHelpProvinzHS1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iNumProvinzHS = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers() / 2
  szHelp = localText.getText("TXT_KEY_EVENT_PROVINZHS_HELP", (iNumProvinzHS, ))

  return szHelp

def canTriggerProvinzHSDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iProvinzHS = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_PROVINZPALAST')
  iProvinzHSRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() / 2
  if iProvinzHSRequired > player.getBuildingClassCount(iProvinzHS):
    return False

  return True

#### KASTELL ####

def canTriggerKastell(argsList):
  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and player.isHuman(): return False

  if player.getNumCities() > 10:
    if player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"): return True
    if player.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"): return True

  return False

def getHelpKastell1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  map = gc.getMap()

  iKastellRequired = gc.getWorldInfo(map.getWorldSize()).getDefaultPlayers() / 2
  szHelp = localText.getText("TXT_KEY_EVENT_KASTELL_HELP", (iKastellRequired, ))

  return szHelp

def canTriggerKastellDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  iKastell = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_SPECIAL1')
  iKastellRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() / 2
  if iKastellRequired > player.getBuildingClassCount(iKastell):
    return False

  return True

######## Isis ###########

def canTriggerIsis(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        city = player.getCity(kTriggeredData.iCityId)

        #city = gc.getGame().getHeadquarters(kTriggeredData.eCorporation)
        #if None == city or city.isNone():
        #        return false

        # Hack to remember the number of cities you already have with the Corporation
        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.iOtherPlayerCityId = gc.getGame().countCorporationLevels(kTriggeredData.eCorporation)
        kActualTriggeredDataObject.iCityId = city.getID()
        kActualTriggeredDataObject.iPlotX = city.getX()
        kActualTriggeredDataObject.iPlotY = city.getY()

        bFound = false
        for iBuilding in range(gc.getNumBuildingInfos()):
                if gc.getBuildingInfo(iBuilding).getFoundsCorporation() == kTriggeredData.eCorporation:
                        kActualTriggeredDataObject.eBuilding = BuildingTypes(iBuilding)
                        bFound = true
                        break

        if not bFound:
                return false

        return true

def expireIsis1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        city = player.getCity(kTriggeredData.iCityId)
        if None == city or city.isNone():
                return true

        return false

def getHelpIsis1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        iNumCities = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5

        szHelp = localText.getText("TXT_KEY_EVENT_ISIS_HELP_1", (gc.getCorporationInfo(kTriggeredData.eCorporation).getTextKey(), iNumCities))

        return szHelp

def canTriggerIsisDone(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
        kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

        iNumCitiesRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5 + kOrigTriggeredData.iOtherPlayerCityId

        if iNumCitiesRequired > gc.getGame().countCorporationLevels(kOrigTriggeredData.eCorporation):
                return false


        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.eCorporation = kOrigTriggeredData.eCorporation
        kActualTriggeredDataObject.eBuilding = kOrigTriggeredData.eBuilding
        kActualTriggeredDataObject.iCityId = kOrigTriggeredData.iCityId
        kActualTriggeredDataObject.iPlotX = kOrigTriggeredData.iPlotX
        kActualTriggeredDataObject.iPlotY = kOrigTriggeredData.iPlotY

        return true

######## Mithras ###########

def canTriggerMithras(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        city = player.getCity(kTriggeredData.iCityId)

        #city = gc.getGame().getHeadquarters(kTriggeredData.eCorporation)
        #if None == city or city.isNone():
        #        return false

        # Hack to remember the number of cities you already have with the Corporation
        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.iOtherPlayerCityId = gc.getGame().countCorporationLevels(kTriggeredData.eCorporation)
        kActualTriggeredDataObject.iCityId = city.getID()
        kActualTriggeredDataObject.iPlotX = city.getX()
        kActualTriggeredDataObject.iPlotY = city.getY()

        bFound = false
        for iBuilding in range(gc.getNumBuildingInfos()):
                if gc.getBuildingInfo(iBuilding).getFoundsCorporation() == kTriggeredData.eCorporation:
                        kActualTriggeredDataObject.eBuilding = BuildingTypes(iBuilding)
                        bFound = true
                        break

        if not bFound:
                return false

        return true

def expireMithras1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        city = player.getCity(kTriggeredData.iCityId)
        if None == city or city.isNone():
                return true

        return false

def getHelpMithras1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        iNumCities = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5

        szHelp = localText.getText("TXT_KEY_EVENT_MITHRAS_HELP_1", (gc.getCorporationInfo(kTriggeredData.eCorporation).getTextKey(), iNumCities))

        return szHelp

def canTriggerMithrasDone(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
        kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

        iNumCitiesRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 5 + kOrigTriggeredData.iOtherPlayerCityId

        if iNumCitiesRequired > gc.getGame().countCorporationLevels(kOrigTriggeredData.eCorporation):
                return false


        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.eCorporation = kOrigTriggeredData.eCorporation
        kActualTriggeredDataObject.eBuilding = kOrigTriggeredData.eBuilding
        kActualTriggeredDataObject.iCityId = kOrigTriggeredData.iCityId
        kActualTriggeredDataObject.iPlotX = kOrigTriggeredData.iPlotX
        kActualTriggeredDataObject.iPlotY = kOrigTriggeredData.iPlotY

        return true

######## Helle ###########

def canTriggerHelle(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        city = player.getCity(kTriggeredData.iCityId)

        #city = gc.getGame().getHeadquarters(kTriggeredData.eCorporation)
        #if None == city or city.isNone():
        #        return false

        # Hack to remember the number of cities you already have with the Corporation
        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.iOtherPlayerCityId = gc.getGame().countCorporationLevels(kTriggeredData.eCorporation)
        kActualTriggeredDataObject.iCityId = city.getID()
        kActualTriggeredDataObject.iPlotX = city.getX()
        kActualTriggeredDataObject.iPlotY = city.getY()

        bFound = false
        for iBuilding in range(gc.getNumBuildingInfos()):
                if gc.getBuildingInfo(iBuilding).getFoundsCorporation() == kTriggeredData.eCorporation:
                        kActualTriggeredDataObject.eBuilding = BuildingTypes(iBuilding)
                        bFound = true
                        break

        if not bFound:
                return false

        return true

def expireHelle1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]
        player = gc.getPlayer(kTriggeredData.ePlayer)

        city = player.getCity(kTriggeredData.iCityId)
        if None == city or city.isNone():
                return true

        return false

def getHelpHelle1(argsList):
        iEvent = argsList[0]
        kTriggeredData = argsList[1]

        iNumCities = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 7

        szHelp = localText.getText("TXT_KEY_EVENT_HELLE_HELP_1", (gc.getCorporationInfo(kTriggeredData.eCorporation).getTextKey(), iNumCities))

        return szHelp

def canTriggerHelleDone(argsList):
        kTriggeredData = argsList[0]
        player = gc.getPlayer(kTriggeredData.ePlayer)
        trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
        kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))

        iNumCitiesRequired = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers() + 7 + kOrigTriggeredData.iOtherPlayerCityId

        if iNumCitiesRequired > gc.getGame().countCorporationLevels(kOrigTriggeredData.eCorporation):
                return false


        kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
        kActualTriggeredDataObject.eCorporation = kOrigTriggeredData.eCorporation
        kActualTriggeredDataObject.eBuilding = kOrigTriggeredData.eBuilding
        kActualTriggeredDataObject.iCityId = kOrigTriggeredData.iCityId
        kActualTriggeredDataObject.iPlotX = kOrigTriggeredData.iPlotX
        kActualTriggeredDataObject.iPlotY = kOrigTriggeredData.iPlotY

        return true

######## MEUTEREI ###########

def canTriggerMeuterei(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  unit = player.getUnit(kTriggeredData.iUnitId)

  if unit.isNone():
    return False

  iLoyal = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LOYALITAT')
  if unit.isHasPromotion(iLoyal):
    return False

  return True

def applyMeuterei(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_KONTERE')
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_PIRATE_SEA, DirectionTypes.DIRECTION_SOUTH)

######## KARAWANE ###########

def applyKarawane(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_MERCHANT')
  player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_MERCHANT, DirectionTypes.DIRECTION_SOUTH)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_CARAVAN')
  player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_MERCHANT, DirectionTypes.DIRECTION_SOUTH)
  player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_MERCHANT, DirectionTypes.DIRECTION_SOUTH)

######## BALEAREN und KRETA ###########

def canTriggerBalearen(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and gc.getPlayer(kTriggeredData.ePlayer).isHuman():
    return False

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if plot.getOwner() > -1 and plot.getOwner() != gc.getBARBARIAN_PLAYER():
    return False

  return True

def doBalearenRevealed(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  player = gc.getPlayer(kTriggeredData.ePlayer)

  plot.setRevealed(player.getTeam(), True, True, -1)
  # for PAE and the black fog of war
  CvUtil.addScriptData(plot,"H","X")
  if (kTriggeredData.ePlayer == gc.getGame().getActivePlayer()):
    CyCamera().JustLookAtPlot( CyMap().plot( kTriggeredData.iPlotX, kTriggeredData.iPlotY ) )

  return 1

def getHelpBalearen1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  iTurns = gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGrowthPercent() / 2

  szHelp = localText.getText("TXT_KEY_EVENT_BALEAREN_HELP_1", (iTurns, ))

  return szHelp

def expireBalearen1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if gc.getGame().getGameTurn() >= kTriggeredData.iTurn + gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGrowthPercent() / 2:
    return True

  if plot.getOwner() != kTriggeredData.ePlayer and plot.getOwner() != gc.getBARBARIAN_PLAYER() and plot.getOwner() != -1:
    # for PAE and the black fog of war
    CvUtil.removeScriptData(plot,"H")
    return True

  return False

def canTriggerBalearenDone(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)
  kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))
  plot = gc.getMap().plot(kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY)

  if (plot.getOwner() != kTriggeredData.ePlayer):
    return False

  # for PAE and the black fog of war
  CvUtil.removeScriptData(plot,"H")

  return True

def applyKretaDone(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 1
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 1
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 2
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 3
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 3
  else:
    iNumUnits  = 4

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_ARCHER_KRETA')

  for i in range(iNumUnits):
    player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

def applyBalearenDone(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  if gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 1
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 1
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 2
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 3
  elif gc.getMap().getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 3
  else:
    iNumUnits  = 4

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_BALEAREN')

  for i in range(iNumUnits):
    player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

######## Soeldner ###########

def canTriggerSoeldner(argsList):
  kTriggeredData = argsList[0]
  trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
  player = gc.getPlayer(kTriggeredData.ePlayer)
  otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

  if not player.canTradeNetworkWith(kTriggeredData.eOtherPlayer):
    return False

  listResources = []
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_CELTIC'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_ROMAN'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_NUMID'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_NUBIA'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_GREEK'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_PERSIA'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_GERMAN'))
  listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_INDIA'))

  bFound = False
  for iResource in listResources:
    if (player.getNumTradeableBonuses(iResource) > 1 and otherPlayer.getNumAvailableBonuses(iResource) <= 0):
      bFound = True
      break

  if not bFound:
    return False

  for iTeam in range(gc.getMAX_CIV_TEAMS()):
    if iTeam != player.getTeam() and iTeam != otherPlayer.getTeam() and gc.getTeam(iTeam).isAlive():
      if gc.getTeam(iTeam).isAtWar(otherPlayer.getTeam()) and not gc.getTeam(iTeam).isAtWar(player.getTeam()):
        return True

  return False

def canDoSoeldner1(argsList):
  kTriggeredData = argsList[1]
  newArgs = (kTriggeredData, )

  return canTriggerSoeldner(newArgs)

######## THORGAL ###########

def applyThorgal(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_VIKING_2')
  NewUnit = player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

  NewUnit.setName("Thorgal")

def getHelpRome_Religion_3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_THORGAL", ())

  return szHelp

######## BEDUINEN ###########

def canTriggerBeduinen(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

#   If Barbarians are disabled in this game, this event will not occur.
  if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    return False

#   At least one civ on the board must know Sattel.
  bFoundValid = False
  iTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), 'TECH_HORSEBACK_RIDING_2')
  for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
    loopPlayer = gc.getPlayer(iPlayer)
    if loopPlayer.isAlive():
      if gc.getTeam(loopPlayer.getTeam()).isHasTech(iTech):
        bFoundValid = True
        break

  if not bFoundValid:
    return False

#  Find an eligible plot
  map = gc.getMap()
  terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.getTerrainType() == terr_desert and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      return True

  return False


def getHelpBeduinen1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_BEDUINEN_HELP_1", ())

  return szHelp


def applyBeduinen1(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  listPlots = []
  map = gc.getMap()
  terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
  for i in range(map.numPlots()):
    plot = map.plotByIndex(i)
    if (plot.getOwner() == -1 and not plot.isWater() and not plot.isImpassable() and plot.getTerrainType() == terr_desert and plot.area().getCitiesPerPlayer(kTriggeredData.ePlayer) > 0 and plot.isAdjacentPlayer(kTriggeredData.ePlayer, True)):
      listPlots.append(i)

  if 0 == len(listPlots):
    return

  plot = map.plotByIndex(listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Beduinen event location")])

  if map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_DUEL'):
    iNumUnits  = 3
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_TINY'):
    iNumUnits  = 3
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_SMALL'):
    iNumUnits  = 4
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_STANDARD'):
    iNumUnits  = 5
  elif map.getWorldSize() == CvUtil.findInfoTypeNum(gc.getWorldInfo, gc.getNumWorldInfos(), 'WORLDSIZE_LARGE'):
    iNumUnits  = 6
  else:
    iNumUnits  = 7

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_BEDUINE')

  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  for i in range(iNumUnits):
    barbPlayer.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)

######## BIER ###########

def canTriggerBier(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  team = gc.getTeam(player.getTeam())

  iGaerung = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_GAERUNG')

  if team.isHasTech(iGaerung):
    return False

  return True

def applyBier(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  iTeam = player.getTeam()
  pTeam = gc.getTeam(iTeam)

  iGaerung = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_GAERUNG')

  pTeam.setHasTech(iGaerung, 1, kTriggeredData.ePlayer, 0, 1)

#######  Waldbrand ########

def applyForest_Fire (argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
  iVerbrannterWald = gc.getInfoTypeForString("FEATURE_FOREST_BURNT")

  plot.setFeatureType(iVerbrannterWald,1)

###### Reflexbogen #######

def canTriggerReflex(argsList):
  kTriggeredData = argsList[0]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  team = gc.getTeam(player.getTeam())

  iReflex = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_REFLEXBOGEN')

  if team.isHasTech(iReflex):
    return False

  return True

def applyReflex(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  iTeam = player.getTeam()
  pTeam = gc.getTeam(iTeam)

  iReflex = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_REFLEXBOGEN')

  pTeam.setHasTech(iReflex, 1, kTriggeredData.ePlayer, 0, 1)

######## Rome_Religion_3 ###########

def applyRome_Religion_3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PROPHET')
  NewUnit = player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

  NewUnit.setName("Pontifex Maximus")

def getHelpEvent_Prophet(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  szHelp = localText.getText("TXT_KEY_EVENT_PROPHET", ())

  return szHelp

######## Zoro_3 ###########

def applyZoro_3(argsList):
  iEvent = argsList[0]
  kTriggeredData = argsList[1]

  player = gc.getPlayer(kTriggeredData.ePlayer)
  plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)

  iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_PROPHET')
  NewUnit = player.initUnit(iUnitType, plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

  NewUnit.setName("Zarathustra")

######## KEIN_WEIN ###########

def canTriggerKeinWein(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getNumAvailableBonuses(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_WINE')) > 0:
    return False

  return True

######## KEINE_OLIVEN ###########

def canTriggerKeineOliven(argsList):

  kTriggeredData = argsList[0]
  player = gc.getPlayer(kTriggeredData.ePlayer)

  if player.getNumAvailableBonuses(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_OLIVES')) > 0:
    return False

  return True