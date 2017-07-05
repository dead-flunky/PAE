# Trade and Cultivation feature
# From Flunky

### Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil

### Defines
gc = CyGlobalContext()
localText = CyTranslator()
### Globals
bInitialised = False # Whether global variables are already initialised

### Constants
iSchoolResearch = 2
iMaxSchoolResearch = 10
iLibraryResearch = 2
iMaxLibraryResearch = 10
iBordellCulture = 2
iMaxBordellCulture = 10
iTheatreCulture = 2
iMaxTheatreCulture = 10
iManufakturProd = 2
iMaxManufakturProd = 10
iManufakturFood = 2
iMaxManufakturFood = 10
iPalaceCulture = 1
iTempleCulture = 1
iTempleCultureKRE = 1
iFeuerwehrHappy = 1
iMaxFeuerwehrHappy = 3

def onModNetMessage(iData1, iData2, iData3, iData4, iData5):
    pPlot = CyMap().plot(iData2, iData3)
    pCity = pPlot.getPlotCity()
    pPlayer = gc.getPlayer(iData4)
    pUnit = pPlayer.getUnit(iData5)
    # Slave -> Bordell
    if iData1 == 668:
        doSlave2Bordell(pCity, pUnit)
    # Slave -> Gladiator
    elif iData1 == 669:
        doSlave2Gladiator(pCity, pUnit)
    # Slave -> Theatre
    elif iData1 == 670:
        doSlave2Theatre(pCity, pUnit)
    # Slave -> Schule
    elif iData1 == 679:
        doSlave2Schule(pCity, pUnit)
    # Slave -> Manufaktur Nahrung
    elif iData1 == 680:
        doSlave2Manufaktur(pCity, pUnit, 0)
    # Slave -> Manufaktur Produktion
    elif iData1 == 681:
        doSlave2Manufaktur(pCity, pUnit, 1)
    # Sklaven -> Palast
    elif iData1 == 692:
        doSlave2Palace(pCity, pUnit)
    # Sklaven -> Tempel
    elif iData1 == 693:
        doSlave2Temple(pCity, pUnit)
    # Sklaven -> Feuerwehr
    elif iData1 == 696:
        doSlave2Feuerwehr(pCity, pUnit)


def doSlave2Gladiator(pCity, pUnit):
    'Slave -> Gladiator'
    pCity.changeFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_GLADIATOR"), 1)
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
    pUnit = None


def doSlave2Schule(pCity, pUnit):
    'Slave -> Schule'
    iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iResearch = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH)
        if iResearch < iMaxSchoolResearch:
            iResearch += iSchoolResearch
            pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH, iResearch)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False


def doSlave2Library(pCity, pUnit):
    'Slave -> Library / Bibliothek'
    iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iResearch = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH)
        if iResearch < iMaxLibraryResearch:
            iResearch += iLibraryResearch
            pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH, iResearch)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False


def doSlave2Bordell(pCity, pUnit):
    'Slave -> Bordell'
    iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        if iCulture < iMaxBordellCulture:
            iCulture += iBordellCulture
            pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Bordell (Zeile 5070)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


def doSlave2Theatre(pCity, pUnit):
    'Slave -> Theatre'
    iBuilding1 = gc.getInfoTypeForString('BUILDING_THEATER')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        if iCulture < iMaxTheatreCulture:
            iCulture += iTheatreCulture
            pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Theater (Zeile 5178)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Manufaktur , doProduction: 0 = Nahrung; 1 = Produktion
def doSlave2Manufaktur(pCity, pUnit, doProduction):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        if doProduction == 1:
            eYield = YieldTypes.YIELD_PRODUCTION
            iMax = iMaxManufakturProd
            iIncr = iManufakturProd
        else:
            eYield = YieldTypes.YIELD_FOOD
            iMax = iMaxManufakturFood
            iIncr = iManufakturFood
        iBonus = pCity.getBuildingYieldChange(eBuildingClass, eYield)
        if iBonus < iMax:
            iBonus += iIncr
            pCity.setBuildingYieldChange(eBuildingClass, eYield, iBonus)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False

      # ***TEST***
      #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Manufaktur (Zeile 5196)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Slave -> Palace
def doSlave2Palace(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        iCulture += iPalaceCulture
        pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit = None
        return True
    return False
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
        iBuilding = TempleArray[CvUtil.myRandom(len(TempleArray), "temple_slave")]
        eBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        # Trait Creative: 3 Kultur pro Sklave / 3 culture per slave
        if gc.getPlayer(pCity.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")):
            iCulture += iTempleCultureKRE
        else:
            iCulture += iTempleCulture
        pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)
        pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit = None
        return True
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Slave 2 Temple (Zeile 6282)",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return False

# Slave -> Feuerwehr
def doSlave2Feuerwehr(pCity, pUnit):
    iBuilding1 = gc.getInfoTypeForString("BUILDING_FEUERWEHR")
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iHappyiness = pCity.getBuildingHappyChange(eBuildingClass)
        if iHappyiness < iMaxFeuerwehrHappy:
            iHappyiness += iFeuerwehrHappy
            pCity.setBuildingHappyChange(eBuildingClass, iHappyiness)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit = None
            return True
    return False


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
            iRand = CvUtil.myRandom(25, "dyingBuildingSlaveBUILDING_BORDELL")
            if iRand == 1:
                iCulture -= iBordellCulture
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
        iResearch = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH)
        if iResearch > 0:
            iRand = CvUtil.myRandom(33, "dyingBuildingSlaveBUILDING_SCHULE")
            if iRand == 1:
                iResearch -= iSchoolResearch
                pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_RESEARCH, iResearch)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SCHULE_SLAVES", (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Builds/button_schule.dds", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Lehrer verschwunden (Zeile 3944)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


    # Manufaktur
    # chance of losing a slave (4%)
    iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
    if pCity.isHasBuilding(iBuilding1):
        eBuildingClass = gc.getBuildingInfo(iBuilding1).getBuildingClassType()
        iFood = pCity.getBuildingYieldChange(eBuildingClass, YieldTypes.YIELD_FOOD)
        iProd = pCity.getBuildingYieldChange(eBuildingClass, YieldTypes.YIELD_PRODUCTION)
        if iProd > 0 or iFood > 0:
            iRand = CvUtil.myRandom(25, "dyingBuildingSlaveBUILDING_CORP3")
            if iRand == 1:
                if iProd > 0:
                    iProd -= iManufakturProd
                    pCity.setBuildingYieldChange(eBuildingClass, YieldTypes.YIELD_PRODUCTION, iProd)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MANUFAKTUR_SLAVES_PROD", (pCity.getName(), "Art/Interface/Buttons/Corporations/button_manufaktur.dds")), None, 2, "", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
                else:
                    iFood -= iManufakturFood
                    pCity.setBuildingYieldChange(eBuildingClass, YieldTypes.YIELD_FOOD, iFood)
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
            iRand = CvUtil.myRandom(50, "dyingBuildingSlaveBUILDING_PALACE")
            if iRand < 1:
                iCulture -= iPalaceCulture
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
    # Trait Creative: 3 Kultur pro Sklave / 3 culture per slave
    if gc.getPlayer(pCity.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_CREATIVE")):
        iCultureSlave = iTempleCultureKRE
    else:
        iCultureSlave = iTempleCulture

    for iTemple in lAllTemple:
        if pCity.isHasBuilding(iTemple):
            eBuildingClass = gc.getBuildingInfo(iTemple).getBuildingClassType()
            if pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE) >= iCultureSlave:
                TempleArray.append(iBuilding1)

    if TempleArray and CvUtil.myRandom(33, "dyingBuildingSlaveBUILDING_TEMPLE") < 1:
        iBuilding = TempleArray[CvUtil.myRandom(len(TempleArray), "which temple")]
        eBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
        iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
        iCulture -= iCultureSlave
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
        if iHappiness > 0:
            if CvUtil.myRandom(33, "dyingBuildingSlaveBUILDING_Feuerwehr") == 1:
                iHappiness -= iFeuerwehrHappy
                pCity.setBuildingHappyChange(eBuildingClass, iHappiness)
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE2FEUERWEHR_LOST", (pCity.getName(), "")), None, 2, gc.getBuildingInfo(iBuilding1).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

              # ***TEST***
              #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Palastsklave verschwunden (Zeile 5016)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def doReleaseSlaves(pPlayer, pCity, iData5):
    eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
    eSpecialistHouse = gc.getInfoTypeForString("SPECIALIST_SLAVE")
    eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
    eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")

    iCityGlads = pCity.getFreeSpecialistCount(eSpecialistGlad)
    iCitySlavesHaus = pCity.getFreeSpecialistCount(eSpecialistHouse)
    iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood)
    iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd)
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

    bPopUp = False
    eRemoveSpec = None
    if iData5 == -1:
        # wenn es nur Gladiatoren gibt, automatisch einen abziehen
        if iCityGlads >= 1 and iCitySlaves == 0:
            eRemoveSpec = eSpecialistGlad
            iCityGlads -= 1
        elif iCitySlaves >= 1:
            # wenns nur Haussklaven gibt
            if iCityGlads == 0 and iCitySlaves == iCitySlavesHaus:
                eRemoveSpec = eSpecialistHouse
                iCitySlavesHaus -= 1
                iCitySlaves -= 1
            # wenns nur Feldsklaven gibt
            elif iCityGlads == 0 and iCitySlaves == iCitySlavesFood:
                eRemoveSpec = eSpecialistFood
                iCitySlavesFood -= 1
                iCitySlaves -= 1
            # wenns nur Bergwerksklaven gibt
            elif iCityGlads == 0 and iCitySlaves == iCitySlavesProd:
                eRemoveSpec = eSpecialistProd
                iCitySlavesProd -= 1
                iCitySlaves -= 1
            # wenns verschiedene angesiedelte Sklaven gibt -> PopUP
            else:
                bPopUp = True

    # Sklaven abziehen
    else:
        if iData5 == 0 and iCityGlads >= 1:
            eRemoveSpec = eSpecialistGlad
            iCityGlads -= 1
        elif iData5 == 1 and iCitySlavesHaus >= 1:
            eRemoveSpec = eSpecialistHouse
            iCitySlavesHaus -= 1
            iCitySlaves -= 1
        elif iData5 == 2 and iCitySlavesFood >= 1:
            eRemoveSpec = eSpecialistFood
            iCitySlavesFood -= 1
            iCitySlaves -= 1
        elif iData5 == 3 and iCitySlavesProd >= 1:
            eRemoveSpec = eSpecialistProd
            iCitySlavesProd -= 1
            iCitySlaves -= 1

    if eRemoveSpec != None:
        pCity.changeFreeSpecialistCount(eRemoveSpec, -1)
        iUnitSlave = gc.getInfoTypeForString("UNIT_SLAVE")
        NewUnit = pPlayer.initUnit(iUnitSlave, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()
    # PopUp
    if iData5 != -1 or bPopUp:
        # PopUp
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_RELEASE_SLAVES", (pCity.getName(), iCityGlads + iCitySlaves)))
        popupInfo.setData1(pCity.getID()) # CityID
        popupInfo.setData2(pCity.getOwner()) # iPlayer
        popupInfo.setOnClickedPythonCallback("popupReleaseSlaves")

        # Button 0: Gladiatoren
        szText = localText.getText("TXT_KEY_UNIT_GLADIATOR", ()) + " (" + str(iCityGlads) + ")"
        popupInfo.addPythonButton(szText, gc.getSpecialistInfo(eSpecialistGlad).getButton())
        # Button 1: Haussklaven
        szText = localText.getText("TXT_KEY_UNIT_SLAVE_HAUS", ()) + " (" + str(iCitySlavesHaus) + ")"
        popupInfo.addPythonButton(szText, gc.getSpecialistInfo(eSpecialistHouse).getButton())
        # Button 2: Feldsklaven
        szText = localText.getText("TXT_KEY_UNIT_SLAVE_FOOD", ()) + " (" + str(iCitySlavesFood) + ")"
        popupInfo.addPythonButton(szText, gc.getSpecialistInfo(eSpecialistFood).getButton())
        # Button 3: Bergwerksklaven
        szText = localText.getText("TXT_KEY_UNIT_SLAVE_PROD", ()) + " (" + str(iCitySlavesProd) + ")"
        popupInfo.addPythonButton(szText, gc.getSpecialistInfo(eSpecialistProd).getButton())

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
            eBuildingClass = gc.getBuildingInfo(iTemple).getBuildingClassType()
            iCulture = pCity.getBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE)
            if iCulture > 3:
                iCulture = int(iCulture/2)
            else:
                iCulture = 0
            pCity.setBuildingCommerceChange(eBuildingClass, CommerceTypes.COMMERCE_CULTURE, iCulture)

    # slave market
    iBuilding = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
    if pCity.isHasBuilding(iBuilding):
        pCity.setNumRealBuilding(iBuilding, 0)

    # Settled glads and slaves => 0
    pCity.setFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_GLADIATOR"), 0)
    pCity.setFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE"), 0)
    pCity.setFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD"), 0)
    pCity.setFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD"), 0)

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
    pUnit = None


  ##############
# AI: Release slaves when necessary (eg city shrinks)
def doAIReleaseSlaves(pCity):
    # Inits
    iCityPop = pCity.getPopulation()
    eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
    eSpecialistHouse = gc.getInfoTypeForString("SPECIALIST_SLAVE")
    eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
    eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")
    iCityGlads = pCity.getFreeSpecialistCount(eSpecialistGlad) # SPECIALIST_GLADIATOR
    iCitySlavesHaus = pCity.getFreeSpecialistCount(eSpecialistHouse) # SPECIALIST_SLAVE
    iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood) # SPECIALIST_SLAVE_FOOD
    iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd) # SPECIALIST_SLAVE_PROD
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
            iSpezi = eSpecialistGlad
            iCityGlads -= 1
        # 1st prio: research
        elif iCitySlavesHaus > 0:
            iSpezi = eSpecialistHouse
            iCitySlavesHaus -= 1
        # 2nd prio: prod
        elif iCitySlavesProd > 0:
            iSpezi = eSpecialistProd
            iCitySlavesProd -= 1
        # 3rd prio: food
        else: #iCitySlavesFood > 0:
            iSpezi = eSpecialistFood
            iCitySlavesFood -= 1

        NewUnit = pPlayer.initUnit(iUnitSlave, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()
        pCity.changeFreeSpecialistCount(iSpezi, -1)
        iCitySlaves -= 1



# Feldsklaven und Minensklaven checken
def doCheckSlavesAfterPillage(pUnit, pPlot):
    pCity = pPlot.getWorkingCity()

    if pCity is not None:
        # TEST
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(pCity.getName(),0)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
        eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")
        iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood)
        iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd)
        iUnitSlave = gc.getInfoTypeForString("UNIT_SLAVE")

        bFarms = False
        lFarms = [
            gc.getInfoTypeForString("IMPROVEMENT_PASTURE"),
            gc.getInfoTypeForString("IMPROVEMENT_FARM"),
            gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"),
            gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"),
            gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"),
            gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"),
            gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5")
        ]

        bMines = False
        lMines = [
            gc.getInfoTypeForString("IMPROVEMENT_MINE"),
            gc.getInfoTypeForString("IMPROVEMENT_QUARRY")
        ]

        for iI in range(gc.getNUM_CITY_PLOTS()):
            loopPlot = pCity.getCityIndexPlot(iI)
            # die beste position finden:
            if loopPlot is not None and not loopPlot.isNone():
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

        iSlaves = 0
        # Feldsklaven checken
        if iCitySlavesFood > 0 and not bFarms:
            iSlaves += iCitySlavesFood
            pCity.setFreeSpecialistCount(eSpecialistFood, 0)

        # Bergwerkssklaven checken
        if iCitySlavesProd > 0 and not bMines:
            iSlaves += iCitySlavesProd
            pCity.setFreeSpecialistCount(eSpecialistProd, 0)

        # Spezialisten von der Stadt auf 0 setzen. Fluechtende Sklaven rund um den verheerenden Plot verteilen
        if iSlaves > 0:
            lFluchtPlots = []
            iX = pPlot.getX()
            iY = pPlot.getY()
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
                if loopPlot is not None and not loopPlot.isNone():
                    if not loopPlot.isWater() and not loopPlot.isPeak() and not loopPlot.isUnit():
                        lFluchtPlots.append(loopPlot)
            if not lFluchtPlots:
                lFluchtPlots = [pCity]

            pBarbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
            for _ in range(iSlaves):
                iRand = CvUtil.myRandom(len(lFluchtPlots), "flee_slaves")
                # gc.getBARBARIAN_PLAYER() statt pCity.getOwner()
                CvUtil.spawnUnit(iUnitSlave, lFluchtPlots[iRand], pBarbPlayer)

            # Meldung
            if pUnit.getOwner() == gc.getGame().getActivePlayer() or pCity.getOwner() == gc.getGame().getActivePlayer():
                szButton = ",Art/Interface/Buttons/Actions/Pillage.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,8,2"
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_PILLAGE_SLAVES", (pCity.getName(),)), None, 2, szButton, ColorTypes(10), pPlot.getX(), pPlot.getY(), True, True)

def freeSlaves(pCity, pPlayer):
    iCitySlaves = pCity.getFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE")) + pCity.getFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")) + pCity.getFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD"))
    iCityGlads = pCity.getFreeSpecialistCount(gc.getInfoTypeForString("SPECIALIST_GLADIATOR"))

    iFreedSlaves = iCitySlaves + iCityGlads
    if iFreedSlaves > 0:
        text = ""
        lUnits = [
            [gc.getInfoTypeForString('UNIT_AXEMAN'), UnitAITypes.UNITAI_ATTACK],
            [gc.getInfoTypeForString('UNIT_UNSTERBLICH'), UnitAITypes.UNITAI_CITY_COUNTER],
            [gc.getInfoTypeForString('UNIT_COMPOSITE_ARCHER'), UnitAITypes.UNITAI_CITY_DEFENSE],
            [gc.getInfoTypeForString('UNIT_SPY'), UnitAITypes.UNITAI_SPY],
            [gc.getInfoTypeForString('UNIT_HOPLIT'), UnitAITypes.UNITAI_ATTACK],
            [gc.getInfoTypeForString('UNIT_ARCHER_KRETA'), UnitAITypes.UNITAI_CITY_DEFENSE],
            [gc.getInfoTypeForString('UNIT_CELTIC_GALLIC_WARRIOR'), UnitAITypes.UNITAI_ATTACK],
            [gc.getInfoTypeForString('UNIT_BALEAREN'), UnitAITypes.UNITAI_CITY_COUNTER],
            [gc.getInfoTypeForString('UNIT_GERMANNE'), UnitAITypes.UNITAI_ATTACK]
        ]
        iPromoCombat1 = gc.getInfoTypeForString("PROMOTION_COMBAT1")
        iPromoCombat2 = gc.getInfoTypeForString("PROMOTION_COMBAT2")
        iX = pCity.getX()
        iY = pCity.getY()
        for i in range(iFreedSlaves):
            iRand = CvUtil.myRandom(20, "freedSlaveType")
            NewUnit = None
            if iRand < len(lUnits):
                NewUnit = pPlayer.initUnit(lUnits[iRand][0], iX, iY, lUnits[iRand][1], DirectionTypes.DIRECTION_SOUTH)
                text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_"+str(iRand+1), (0, 0))
            else:
                CvUtil.spawnUnit(gc.getInfoTypeForString('UNIT_FREED_SLAVE'), pCity.plot(), pPlayer)
                text = CyTranslator().getText("TXT_KEY_MESSAGE_FREED_SLAVES_0", (0, 0))

            if NewUnit:
                NewUnit.setHasPromotion(iPromoCombat1, True)  # Combat 1
                NewUnit.setHasPromotion(iPromoCombat2, True)  # Combat 2

            if pPlayer.isHuman():
                CyInterface().addMessage(pPlayer.getID(), True, 12, text, None, 2, None, ColorTypes(8), 0, 0, False, False)
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtsklaven befreit (Zeile 3237)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def freeCitizen(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)

    eSpecialistFreeCitizen = gc.getInfoTypeForString("SPECIALIST_CITIZEN2")
    eSpecialistHouse = gc.getInfoTypeForString("SPECIALIST_SLAVE")
    eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
    eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")
    iCitySlavesHaus = pCity.getFreeSpecialistCount(eSpecialistHouse)
    iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood)
    iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd)
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

    eCivicBuergerrecht = gc.getInfoTypeForString("CIVIC_BUERGERRECHT")
    eCivicVoelkerrecht = gc.getInfoTypeForString("CIVIC_VOELKERRECHT")

    if iCitySlaves > 0:
        # Slaves -> Free citizen (chance 2% / 3%)
        if pPlayer.isCivic(eCivicBuergerrecht) or pPlayer.isCivic(eCivicVoelkerrecht):
            iRand = 50
            if pPlayer.isCivic(eCivicVoelkerrecht):
                iRand = 33
            # Trait Philosophical: Doppelte Chance auf freie Buerger / chance of free citizens doubled
            if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL")):
                iRand /= 2

            if CvUtil.myRandom(iRand, "Free Citizen") == 1:
                pCity.changeFreeSpecialistCount(eSpecialistFreeCitizen, 1)  # Citizen = 0
                if iCitySlavesHaus > 0:
                    pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                elif iCitySlavesFood > 0:
                    pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                else:
                    pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                iCitySlaves -= 1
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_CITIZEN", (pCity.getName(), "")), None, 2, None, ColorTypes(14), pCity.getX(), pCity.getY(), True, True)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sklave zu Buerger (Zeile 3828)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return iCitySlaves

def freeCitizenGlad(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)

    eSpecialistFreeCitizen = gc.getInfoTypeForString("SPECIALIST_CITIZEN2")
    eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
    eCivicBuergerrecht = gc.getInfoTypeForString("CIVIC_BUERGERRECHT")
    eCivicVoelkerrecht = gc.getInfoTypeForString("CIVIC_VOELKERRECHT")
    iCityGlads = pCity.getFreeSpecialistCount(eSpecialistGlad)

    if iCityGlads > 0:
        # Free citizen (chance 2% / 3%)
        if pPlayer.isCivic(eCivicBuergerrecht) or pPlayer.isCivic(eCivicVoelkerrecht):
            iChance = 2
            if pPlayer.isCivic(eCivicVoelkerrecht):
                iChance = 3

            if CvUtil.myRandom(100, "Free citizen glad") < iChance:
                pCity.changeFreeSpecialistCount(eSpecialistFreeCitizen, 1)  # Citizen = 0
                pCity.changeFreeSpecialistCount(eSpecialistGlad, -1) # Gladiator = 14
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

    if CvUtil.myRandom(1000, "spawnSlave") < iChance:
        iUnitType = gc.getInfoTypeForString("UNIT_SLAVE")
        CvUtil.spawnUnit(iUnitType, pCity.plot(), pPlayer)
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_BIRTH", (pCity.getName(), "")), None, 2, ",Art/Interface/Buttons/Civics/Slavery.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,8,2", ColorTypes(14), pCity.getX(), pCity.getY(), True, True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Neuer Sklave verfuegbar (Zeile 3841)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def spawnGlad(pCity, iCityGlads):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if CvUtil.myRandom(50, "spawnGlad") == 1:
        iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")
        eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
        CvUtil.spawnUnit(iUnitType, pCity.plot(), pPlayer)
        pCity.changeFreeSpecialistCount(eSpecialistGlad, -1)
        iCityGlads -= 1
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_SLAVE_2_GLADIATOR", (pCity.getName(), "")), None, 2, None, ColorTypes(14), pCity.getX(), pCity.getY(), True, True)
    return iCityGlads

def dyingGlad(pCity, iCityGlads, bTeamHasGladiators):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iChanceGlads = max(3, iCityGlads)

    if CvUtil.myRandom(100, "dyingGlad") < iChanceGlads:
        eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
        # PAE V: stehende Sklaven werden zugewiesen
        bErsatz = False
        # City Plot
        pCityPlot = pCity.plot()
        iRangeUnits = pCityPlot.getNumUnits()
        for iUnit in range(iRangeUnits):
            pLoopUnit = pCityPlot.getUnit(iUnit)
            if pLoopUnit.getOwner() == iPlayer and pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                pLoopUnit = None
                bErsatz = True
                break

        if not bErsatz:
            pCity.changeFreeSpecialistCount(eSpecialistGlad, -1)

        if pPlayer.isHuman():
            iBuilding1 = gc.getInfoTypeForString('BUILDING_COLOSSEUM')
            iBuilding2 = gc.getInfoTypeForString('BUILDING_BYZANTINE_HIPPODROME')

            iRand = CvUtil.myRandom(3, "dyingGlad2")
            if iRand < 1 and pCity.isHasBuilding(iBuilding1):
                iRand = 1 + CvUtil.myRandom(5, "dyingGlad3")
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_COL_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
            elif iRand < 1 and pCity.isHasBuilding(iBuilding2):
                iRand = 1 + CvUtil.myRandom(5, "dyingGlad4")
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_HIP_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)
            else:
                iRand = CvUtil.myRandom(14, "dyingGlad5")
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_GLADIATOR_DEATH_"+str(iRand),(pCity.getName(),"")),None,2,None,ColorTypes(13),pCity.getX(),pCity.getY(),True,True)

            if bErsatz:
                if bTeamHasGladiators:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ2",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
                else:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_GLADS_ERSATZ",("",)),None,2,None,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Gladiator stirbt (Zeile 3977)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
