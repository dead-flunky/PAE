# Trade and Cultivation feature
# From Flunky

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random

### Defines
gc = CyGlobalContext()
### Globals
bInitialised = False # Whether global variables are already initialised

def myRandom (num):
    #return gc.getGame().getMapRandNum(num, None)
    if num <= 1: return 0
    else: return random.randint(0, num-1)

def onModNetMessage(iData1, iData2, iData3, iData4, iData5):
  # Slave -> Bordell
  if iData1 == 668:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Bordell(pCity, pUnit)
  # Slave -> Gladiator
  elif iData1 == 669:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Gladiator(pCity, pUnit)
  # Slave -> Theatre
  elif iData1 == 670:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Theatre(pCity, pUnit)

  # Slave -> Schule
  elif iData1 == 679:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Schule(pCity, pUnit)

  # Slave -> Manufaktur Nahrung
  elif iData1 == 680:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Manufaktur(pCity, pUnit, 0)

  # Slave -> Manufaktur Produktion
  elif iData1 == 681:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Manufaktur(pCity, pUnit, 1)

  # Sklaven -> Palast
  elif iData1 == 692:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Palace(pCity, pUnit)

  # Sklaven -> Tempel
  elif iData1 == 693:
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    doSlave2Temple(pCity, pUnit)

  # Sklaven -> Feuerwehr
  elif iData1 == 696:
    # pPlot = CyMap().plot(iData2, iData3)
    # pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    pCity = pUnit.plot().getPlotCity()
    PAE_Sklaven.doSlave2Feuerwehr(pCity, pUnit)

# Slave -> Bordell
def doSlave2Bordell(pCity, pUnit):
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
def doSlave2Schule(pCity, pUnit):
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
def doSlave2Library(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
    if pCity.isHasBuilding(iBuilding1):
      iCulture = pCity.getBuildingCommerceByBuilding(1, iBuilding1)
      iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

# Slave -> Gladiator
def doSlave2Gladiator(pCity, pUnit):
    pCity.changeFreeSpecialistCount(15, 1) # Gladiator Specialist ID = 15
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
    #pUnit.kill(1,pUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Gladiator (Zeile 5092)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Theatre
def doSlave2Theatre(pCity, pUnit):
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
def doSlave2Manufaktur(pCity, pUnit, iDo):
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
def doSlave2Palace(pCity, pUnit):
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
def doSlave2Temple(pCity, pUnit):
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
      iBuilding = myRandom(len(TempleArray))
      iCulture = pCity.getBuildingCommerceByBuilding(2, TempleArray[iBuilding])
      # Trait Creative: 3 Kultur pro Sklave / 3 culture per slave
      if gc.getPlayer(pCity.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")): iCulture += 2
      #iCulture += 1
      pCity.setBuildingCommerceChange(gc.getBuildingInfo(TempleArray[iBuilding]).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Temple (Zeile 6282)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Feuerwehr
def doSlave2Feuerwehr(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString("BUILDING_FEUERWEHR")
    if pCity.isHasBuilding(iBuilding1):
      iHappyiness = pCity.getBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType())
      iHappyiness += 1
      pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), iHappyiness)
      pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #pUnit.kill(1,pUnit.getOwner())

def doReleaseSlaves(pPlayer, pCity, iData5):

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
  if iData5 > -1 or bPopUp:
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

# Entferne Sklaven aus der Stadt / unset city slaves
def doEnslaveCity(pCity):
  # temple slaves => 0
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

  # slave market
  iBuilding = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
  if pCity.isHasBuilding(iBuilding): pCity.setNumRealBuilding(iBuilding,0)

  # Settled glads(15) and slaves(16,17,18) => 0
  pCity.setFreeSpecialistCount(15,0)
  pCity.setFreeSpecialistCount(16,0)
  pCity.setFreeSpecialistCount(17,0)
  pCity.setFreeSpecialistCount(18,0)

  # Settled Great People => 0
  pCity.setFreeSpecialistCount(8,0)
  pCity.setFreeSpecialistCount(9,0)
  pCity.setFreeSpecialistCount(10,0)
  pCity.setFreeSpecialistCount(11,0)
  pCity.setFreeSpecialistCount(12,0)
  pCity.setFreeSpecialistCount(13,0)
  pCity.setFreeSpecialistCount(14,0)
  # -----------------

def doSell(iPlayer, iUnit):
  pPlayer = gc.getPlayer(iPlayer)
  pUnit = pPlayer.getUnit(iUnit)
  iGold = myRandom(31) + 10
  pPlayer.changeGold(iGold)
  gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
  if pPlayer.isHuman():
    CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_SLAVE_SOLD",(iGold,)),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Units/button_slave.dds",ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)
  # New kill / neuer Kill befehl
  pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
  #pUnit.kill(1,pUnit.getOwner())