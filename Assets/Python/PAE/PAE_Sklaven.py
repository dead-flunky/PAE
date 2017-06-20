# Trade and Cultivation feature
# From Flunky

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil

import PAE_Unit

### Defines
gc = CyGlobalContext()
localText = CyTranslator()
### Globals
bInitialised = False # Whether global variables are already initialised

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
        doSlave2Feuerwehr(pCity, pUnit)

# Slave -> Bordell
def doSlave2Bordell(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
    if pCity.isHasBuilding(iBuilding1):
        iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
        iCulture += 2
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Bordell (Zeile 5070)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Schule
def doSlave2Schule(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
    if pCity.isHasBuilding(iBuilding1):
        iCulture = pCity.getBuildingCommerceByBuilding(1, iBuilding1)
        iCulture += 2
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 School (Zeile 5083)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Library / Bibliothek
def doSlave2Library(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
    if pCity.isHasBuilding(iBuilding1):
        iCulture = pCity.getBuildingCommerceByBuilding(1, iBuilding1)
        iCulture += 2
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

# Slave -> Gladiator
def doSlave2Gladiator(pCity, pUnit):
    pCity.changeFreeSpecialistCount(15, 1) # Gladiator Specialist ID = 15
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Gladiator (Zeile 5092)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Theatre
def doSlave2Theatre(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_THEATER')
    if pCity.isHasBuilding(iBuilding1):
        iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
        iCulture += 2
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Theater (Zeile 5178)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Manufaktur , iDo: 0 = Nahrung; 1 = Produktion
def doSlave2Manufaktur(pCity, pUnit, iDo):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
        if iDo == 1:
            iProd = pCity.getBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1)
            iProd += 2
            pCity.setBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1, iProd)
        else:
            iProd = pCity.getBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0)
            iProd += 2
            pCity.setBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0, iProd)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Manufaktur (Zeile 5196)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Palace
def doSlave2Palace(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
    if pCity.isHasBuilding(iBuilding1):
        iCulture = pCity.getBuildingCommerceByBuilding(2, iBuilding1)
        #iCulture += 1
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Palace (Zeile 6252)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Temple
def doSlave2Temple(pCity, pUnit):
    lAllTemple = [
        gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_ROME_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
    ]
    TempleArray = []
    for iTemple in lAllTemple:
        if pCity.isHasBuilding(iTemple):
            TempleArray.append(iTemple)

    if TempleArray:
        iBuilding = CvUtil.myRandom(len(TempleArray), "temple_slave")
        iCulture = pCity.getBuildingCommerceByBuilding(2, TempleArray[iBuilding])
        # Trait Creative: 3 Kultur pro Sklave / 3 culture per slave
        if gc.getPlayer(pCity.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")):
            iCulture += 2
        #iCulture += 1
        pCity.setBuildingCommerceChange(gc.getBuildingInfo(TempleArray[iBuilding]).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Temple (Zeile 6282)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Feuerwehr
def doSlave2Feuerwehr(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString("BUILDING_FEUERWEHR")
    if pCity.isHasBuilding(iBuilding1):
        iHappyiness = pCity.getBuildingHappyChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType())
        iHappyiness += 1
        pCity.setBuildingHappyChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), iHappyiness)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)

def doReleaseSlaves(pPlayer, pCity, iData5):

    iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
    iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
    iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
    iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

    bPopUp = False

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
                bPopUp = True


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
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_RELEASE_SLAVES", (pCity.getName(), iCityGlads + iCitySlaves)))
        popupInfo.setData1(pCity.getID()) # CityID
        popupInfo.setData2(pCity.getOwner()) # iPlayer
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
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(pCity.getOwner())

# Entferne Sklaven aus der Stadt / unset city slaves
def doEnslaveCity(pCity):
    # temple slaves => 0
    TempleArray = [
        gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_ROME_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
    ]
    for iTemple in TempleArray:
        if pCity.isHasBuilding(iTemple):
            iCulture = pCity.getBuildingCommerceByBuilding(2, iTemple)
            if iCulture > 3:
                iCulture = int(iCulture/2)
            else:
                iCulture = 0
            pCity.setBuildingCommerceChange(gc.getBuildingInfo(iTemple).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)

    # slave market
    iBuilding = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
    if pCity.isHasBuilding(iBuilding):
        pCity.setNumRealBuilding(iBuilding, 0)

    # Settled glads(15) and slaves(16,17,18) => 0
    pCity.setFreeSpecialistCount(15, 0)
    pCity.setFreeSpecialistCount(16, 0)
    pCity.setFreeSpecialistCount(17, 0)
    pCity.setFreeSpecialistCount(18, 0)

    # Settled Great People => 0
    pCity.setFreeSpecialistCount(8, 0)
    pCity.setFreeSpecialistCount(9, 0)
    pCity.setFreeSpecialistCount(10, 0)
    pCity.setFreeSpecialistCount(11, 0)
    pCity.setFreeSpecialistCount(12, 0)
    pCity.setFreeSpecialistCount(13, 0)
    pCity.setFreeSpecialistCount(14, 0)
    # -----------------

def doSell(iPlayer, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pUnit = pPlayer.getUnit(iUnit)
    iGold = CvUtil.myRandom(31, "sell_slave") + 10
    pPlayer.changeGold(iGold)
    gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iGold)
    if pPlayer.isHuman():
        CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_BUTTON_SELL_SLAVE_SOLD", (iGold,)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO,"Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(8), pUnit.getX(), pUnit.getY(), True, True)
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)


  ##############
# AI: Release slaves when necessary (eg city shrinks)
def doAIReleaseSlaves(pCity):
    # Inits
    iCityPop = pCity.getPopulation()
    iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
    iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
    iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
    iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd + iCityGlads

    if iCityPop >= iCitySlaves:
        return

    iUnitSlave = gc.getInfoTypeForString("UNIT_SLAVE")
    iX = pCity.getX()
    iY = pCity.getY()

    pPlayer = gc.getPlayer(pCity.getOwner())

    while iCitySlaves > 0 and iCityPop < iCitySlaves:
        # First prio: glads
        if iCityGlads > 0:
            iSpezi = 15
            iCityGlads -= 1
        # 1st prio: research
        elif iCitySlavesHaus > 0:
            iSpezi = 16
            iCitySlavesHaus -= 1
        # 2nd prio: prod
        elif iCitySlavesProd > 0:
            iSpezi = 18
            iCitySlavesProd -= 1
        # 3rd prio: food
        else: #iCitySlavesFood > 0:
            iSpezi = 17
            iCitySlavesFood -= 1

        NewUnit = pPlayer.initUnit(iUnitSlave, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()
        pCity.changeFreeSpecialistCount(iSpezi, -1)
        iCitySlaves -= 1



# Feldsklaven und Minensklaven checken
def doCheckSlavesAfterPillage(pUnit, pPlot):
    pCity = pPlot.getWorkingCity()

    if pCity != None:
        # PAE V ab Patch 3: Einheiten mobilisieren
        # Flunky: was hat das hier zu suchen?
        if pCity.isCapital():
            PAE_Unit.doMobiliseFortifiedArmy(pCity.getOwner())

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
                loopPlot = plotXY(iX, iY, x - 2, y - 2)
                if loopPlot != None and not loopPlot.isNone():
                    if not loopPlot.isWater():
                        # Plot besetzt?
                        if pCity.canWork(loopPlot):
                            if loopPlot.getImprovementType() in lFarms:
                                bFarms = True
                            elif loopPlot.getImprovementType() in lMines:
                                bMines = True
                # Schleife vorzeitig beenden
                if bFarms and bMines:
                    break
            # Schleife vorzeitig beenden
            if bFarms and bMines:
                break



        iSlaves = 0
        # Feldsklaven checken
        if iCitySlavesFood > 0 and not bFarms:
            iSlaves += iCitySlavesFood
            pCity.setFreeSpecialistCount(17, 0)

        # Bergwerkssklaven checken
        if iCitySlavesProd > 0 and not bMines:
            iSlaves += iCitySlavesProd
            pCity.setFreeSpecialistCount(18, 0)

        # Spezialisten von der Stadt auf 0 setzen. Fluechtende Sklaven rund um den verheerenden Plot verteilen
        if iSlaves > 0:
            lFluchtPlots = []
            iX = pPlot.getX()
            iY = pPlot.getY()
            for x in range(3):
                for y in range(3):
                    loopPlot = plotXY(iX, iY, x - 1, y - 1)
                    if loopPlot != None and not loopPlot.isNone():
                        if not loopPlot.isWater() and not loopPlot.isPeak():
                            if loopPlot.getNumUnits() == 0:
                                lFluchtPlots.append(loopPlot)
            if not lFluchtPlots:
                lFluchtPlots.append(pCity)

            for _ in range(iSlaves):
                iRand = CvUtil.myRandom(len(lFluchtPlots), "flee_slaves")
                # gc.getBARBARIAN_PLAYER() statt pCity.getOwner()
                gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSlave, lFluchtPlots[iRand].getX(), lFluchtPlots[iRand].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            # Meldung
            if pUnit.getOwner() == gc.getGame().getActivePlayer() or pCity.getOwner() == gc.getGame().getActivePlayer():
                szButton = ",Art/Interface/Buttons/Actions/Pillage.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,8,2"
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_PILLAGE_SLAVES", (pCity.getName(),)), None, 2, szButton, ColorTypes(10), pPlot.getX(), pPlot.getY(), True, True)

def freeCitizen(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE = 15
    iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD = 17
    iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD = 18
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
    
    if iCitySlaves > 0:
        # Slaves -> Free citizen (chance 2% / 3%)
        if pPlayer.isCivic(16) or pPlayer.isCivic(17):
            iRand = 50
            if pPlayer.isCivic(17):
                iRand = 33
            # Trait Philosophical: Doppelte Chance auf freie Buerger / chance of free citizens doubled
            if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL")):
                iRand /= 2

            if CvUtil.myRandom(iRand) == 1:
                pCity.changeFreeSpecialistCount(0, 1)  # Citizen = 0
                if iCitySlavesHaus > 0:
                    pCity.changeFreeSpecialistCount(16, -1)
                elif iCitySlavesFood > 0:
                    pCity.changeFreeSpecialistCount(17, -1)
                else:
                    pCity.changeFreeSpecialistCount(18, -1)
                iCitySlaves -= 1
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_CITIZEN", (pCity.getName(), "")), None, 2, None, ColorTypes(14), pCity.getX(), pCity.getY(), True, True)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Buerger (Zeile 3828)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return iCitySlaves
    
def freeCitizenGlad(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 16
    
    if iCityGlads > 0:
        # Free citizen (chance 2% / 3%)
        if pPlayer.isCivic(16) or pPlayer.isCivic(17):
            iChance = 2
            if pPlayer.isCivic(17):
                iChance = 3

            if CvUtil.myRandom(100) < iChance:
                pCity.changeFreeSpecialistCount(0, 1)  # Citizen = 0
                pCity.changeFreeSpecialistCount(15, -1) # Gladiator = 14
                iCityGlads -= 1
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_2_CITIZEN", (pCity.getName(), "")), None, 2, None, ColorTypes(14), pCity.getX(), pCity.getY(), True, True)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiator zu Buerger (Zeile 3860)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return iCityGlads

def spawnSlave(pCity, iCitySlaves):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iChance = 20 # 2% Grundwert

    if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_TYRANNIS")):
        iChance += 10 # 3%

    iChance += iCitySlaves # pro Sklave 0.1% dazu

    iChance = min(iChance, 35)

    # Christentum:
    iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
    if pCity.isHasReligion(iReligion):
        iChance -= 10 # -1%
    if pPlayer.getStateReligion() == iReligion:
        iChance -= 10 # -1%

    # For better AI
    if not pPlayer.isHuman():
        iChance += 10

    if CvUtil.myRandom(1000) < iChance:
        iUnitType = gc.getInfoTypeForString("UNIT_SLAVE")
        CvUtil.spawnUnit(iUnitType, pCity.plot(), pPlayer)
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_BIRTH", (pCity.getName(), "")), None, 2, ",Art/Interface/Buttons/Civics/Slavery.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,8,2", ColorTypes(14), pCity.getX(), pCity.getY(), True, True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Neuer Sklave verfuegbar (Zeile 3841)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def spawnGlad(pCity, iCityGlads):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if CvUtil.myRandom(50) == 1:
        iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")
        CvUtil.spawnUnit(iUnitType, pCity.plot(), pPlayer)
        pCity.changeFreeSpecialistCount(15, -1)
        iCityGlads -= 1
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_GLADIATOR", (pCity.getName(), "")), None, 2, None, ColorTypes(14), pCity.getX(), pCity.getY(), True, True)
    return iCityGlads

def dyingGlad(pCity, iCityGlads, bTeamHasGladiators):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iChanceGlads = max(3, iCityGlads)

    if CvUtil.myRandom(100) < iChanceGlads:
        # PAE V: stehende Sklaven werden zugewiesen
        bErsatz = False
        # City Plot
        pCityPlot = pCity.plot()
        iRangeUnits = pCityPlot.getNumUnits()
        for iUnit in range(iRangeUnits):
            pLoopUnit = pCityPlot.getUnit(iUnit)
            if pLoopUnit.getOwner() == iPlayer and pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                bErsatz = True
                break

        if not bErsatz:
            pCity.changeFreeSpecialistCount(15, -1)

        if pPlayer.isHuman():
            iBuilding1 = gc.getInfoTypeForString('BUILDING_COLOSSEUM')
            iBuilding2 = gc.getInfoTypeForString('BUILDING_BYZANTINE_HIPPODROME')

            iRand = CvUtil.myRandom(3)
            if iRand < 1 and pCity.isHasBuilding(iBuilding1):
                iRand = 1 + CvUtil.myRandom(5)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_COL_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
            elif iRand < 1 and pCity.isHasBuilding(iBuilding2):
                iRand = 1 + CvUtil.myRandom(5)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_HIP_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
            else:
                iRand = CvUtil.myRandom(14)
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

            if bErsatz:
                if bTeamHasGladiators:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ2",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
                else:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiator stirbt (Zeile 3977)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def dyingBuildingSlave(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    # Bordell / House of pleasure / Freudenhaus
    # chance of losing a slave (4%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        if iCulture > 0:
            iRand = CvUtil.myRandom(25)
            if iRand == 1:
                iCulture -= 1
                pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_BORDELL_SLAVES", (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Builds/button_bordell.dds", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Freudemaus verschwunden (Zeile 3927)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Schule
    # chance of losing a slave (3%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH)
        if iCulture > 0:
            iRand = CvUtil.myRandom(33)
            if iRand == 1:
                iCulture -= 1
                pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH, iCulture)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SCHULE_SLAVES", (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Builds/button_schule.dds", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Lehrer verschwunden (Zeile 3944)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Manufaktur
    # chance of losing a slave (4%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iFood = pCity.getBuildingYieldChange(eBuildingClass, 0)
        iProd = pCity.getBuildingYieldChange(eBuildingClass, 1)
        if iProd > 0 or iFood > 0:
            iRand = CvUtil.myRandom(25)
            if iRand == 1:
                if iProd > 0:
                    iProd -= 1
                    pCity.setBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1, iProd)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MANUFAKTUR_SLAVES_PROD", (pCity.getName(), "Art/Interface/Buttons/Corporations/button_manufaktur.dds")), None, 2, "", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                else:
                    iFood -= 1
                    pCity.setBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0, iFood)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MANUFAKTUR_SLAVES_FOOD", (pCity.getName(), "Art/Interface/Buttons/Corporations/button_manufaktur.dds")), None, 2, "", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Manufakturist draufgegangen (Zeile 3968)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Palast
    # chance of losing a slave (2%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        if iCulture > 0:
            iRand = CvUtil.myRandom(50)
            if iRand < 1:
                iCulture -= 1
                pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2PALACE_LOST", (pCity.getName(), "")), None, 2, gc.getBuildingInfo(iBuilding1).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palastsklave verschwunden (Zeile 5016)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Tempel
    # chance of losing a slave (3%)
    TempleArray = []
    lAllTemple = [
        gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_ROME_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
    ]
    for iTemple in lAllTemple:
        if pCity.isHasBuilding(iTemple):
            eBuildingClass = gc.getBuildingInfo(iTemple).getBuildingClassType()
            if pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE) >= 2:
                TempleArray.append(iBuilding1)

    if TempleArray and CvUtil.myRandom(33) < 1:
        iBuilding = TempleArray[CvUtil.myRandom(len(TempleArray))]
        eBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        iCulture -= 2
        pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2TEMPLE_LOST", (pCity.getName(), "")), None, 2, gc.getBuildingInfo(iBuilding).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Tempelsklave verschwunden (Zeile 5051)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Feuerwehr
    # chance of losing a slave (3%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_FEUERWEHR')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iHappiness = pCity.getBuildingHappyChange(eBuildingClass)
        if iHappiness > 0 and CvUtil.myRandom(33) == 1:
            iHappiness -= 1
            pCity.setBuildingHappyChange(eBuildingClass, iHappiness)
            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2FEUERWEHR_LOST", (pCity.getName(), "")), None, 2, gc.getBuildingInfo(iBuilding1).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

              # ***TEST***
              #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palastsklave verschwunden (Zeile 5016)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
