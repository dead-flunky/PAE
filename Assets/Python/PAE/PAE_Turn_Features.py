# Plot features and events per turn

### Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil
import PAE_Barbaren
import PAE_Lists as L

import PyHelpers
### Defines
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer

bMultiPlayer = False
bGoodyHuts = True
bBarbForts = True
bRageBarbs = False
if gc.getGame().isGameMultiPlayer():
    bMultiPlayer = True
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS):
    bGoodyHuts = False
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
    bBarbForts = False
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_RAGING_BARBARIANS):
    bRageBarbs = True

lNumHistoryTexts = {
    -3480: 4,
    -3000: 5,
    -2680: 4,
    -2000: 6,
    -1680: 5,
    -1480: 7,
    -1280: 5,
    -1200: 6,
    -1000: 5,
    -800: 6,
    -750: 3,
    -700: 6,
    -615: 5,
    -580: 5,
    -540: 4,
    -510: 5,
    -490: 5,
    -450: 4,
    -400: 5,
    -350: 7,
    -330: 4,
    -260: 3,
    -230: 5,
    -215: 4,
    -200: 4,
    -150: 5,
    -120: 2,
    -100: 2,
    -70: 3,
    -50: 2,
    -30: 2,
    -20: 2,
    -10: 3,
    10: 3,
    60: 4,
    90: 3,
    130: 3,
    210: 3,
    250: 2,
    280: 2,
    370: 2,
    400: 2,
    440: 3,
}

# ------ Handelsposten erzeugen Kultur (PAE V Patch 3: und wieder Forts/Festungen)
# ------ Berberloewen erzeugen
# ------ Wildpferde, Wildelefanten, Wildkamele ab PAE V
# ------ Barbarenfort beleben (PAE V Patch 4)
def doPlotFeatures():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    eHandelsposten = gc.getInfoTypeForString('IMPROVEMENT_HANDELSPOSTEN')
    lImpForts = []
    lImpForts.append(eHandelsposten)
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT'))
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT2'))

    impBarbFort = gc.getInfoTypeForString("IMPROVEMENT_BARBARENFORT")

    bonus_lion = gc.getInfoTypeForString('BONUS_LION')
    bonus_horse = gc.getInfoTypeForString('BONUS_HORSE')
    bonus_camel = gc.getInfoTypeForString('BONUS_CAMEL')
    bonus_ivory = gc.getInfoTypeForString('BONUS_IVORY')
    iDarkIce = gc.getInfoTypeForString('FEATURE_DARK_ICE')
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for x in range(iMapW):
        for y in range(iMapH):
            loopPlot = gc.getMap().plot(x, y)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce:
                    continue
                if not loopPlot.isWater() and not loopPlot.isPeak():
                    iPlotOwner = loopPlot.getOwner()
                    # nur ausserhalb von Staedten
                    if not loopPlot.isCity():
                        # Handelsposten und Forts
                        if iPlotOwner == -1:
                            if loopPlot.getImprovementType() in lImpForts:
                                # Init
                                iOwner = -1
                                # Handelsposten
                                if loopPlot.getImprovementType() == eHandelsposten:
                                    iOwner = int(CvUtil.getScriptData(loopPlot, ["p", "t"], loopPlot.getOwner()))
                                # Forts
                                elif loopPlot.getNumUnits() > 0:
                                    # Besitzer ist der mit den meisten Einheiten drauf
                                    OwnerArray = {}
                                    iNumUnits = loopPlot.getNumUnits()
                                    for i in range(iNumUnits):
                                        if loopPlot.getUnit(i).isMilitaryHappiness():
                                            iOwner = loopPlot.getUnit(i).getOwner()
                                            if iOwner in OwnerArray:
                                                OwnerArray[iOwner] += 1
                                            else:
                                                OwnerArray[iOwner] = 1

                                    my_decorated = [(OwnerArray.get(x), x) for x in OwnerArray]
                                    iOwner = max(my_decorated or [(0, -1)])[1]

                                iRange = gc.getMAX_PLAYERS()
                                for i in range(iRange):
                                    iPlayerID = gc.getPlayer(i).getID()
                                    if iPlayerID == iOwner:
                                        loopPlot.setCulture(iPlayerID, 1, True)
                                        loopPlot.setOwner(iPlayerID)
                                    else:
                                        # TODO: das macht hidden culture in ehemals besiedeltem Gebiet kaputt.
                                        loopPlot.setCulture(iPlayerID, 0, True)

                            # Lion - 2% Appearance
                            elif loopPlot.getBonusType(-1) == bonus_lion and loopPlot.getImprovementType() == -1:
                                if loopPlot.getNumUnits() < 3:
                                    if CvUtil.myRandom(50, "lion") == 1:
                                        iUnitType = gc.getInfoTypeForString("UNIT_LION")
                                        pBarbPlayer.initUnit(iUnitType, x, y, UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                                        # ***TEST***
                                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barb. Atlasloewe erschaffen",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                        # Barbarenforts/festungen (erzeugt barbarische Einheiten alle x Runden)
                        elif loopPlot.getImprovementType() == impBarbFort:
                            if iPlotOwner == -1 or iPlotOwner == iBarbPlayer:
                                if loopPlot.getNumUnits() == 0:
                                    # Verteidiger setzen
                                    PAE_Barbaren.setFortDefence(loopPlot)
                                elif pBarbPlayer.getCurrentEra() > 0 and gc.getGame().getGameTurn() % 5 == 0:
                                    # Einheiten) setzen
                                    PAE_Barbaren.createBarbUnit(loopPlot)
                        # Handelsposten entfernen, wenn der Plot in einem fremden Kulturkreis liegt
                        elif loopPlot.getImprovementType() == eHandelsposten:
                            iOwner = int(CvUtil.getScriptData(loopPlot, ["p", "t"], loopPlot.getOwner()))
                            if iOwner != iPlotOwner:
                                loopPlot.setImprovementType(-1)
                                if gc.getPlayer(iOwner).isHuman():
                                    szText = CyTranslator().getText("TXT_KEY_INFO_CLOSED_TRADEPOST", ("",))
                                    CyInterface().addMessage(iOwner, True, 15, szText, "AS2D_UNIT_BUILD_UNIT", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)
                    # end if --- nur ausserhalb von Staedten

                    # Bei jedem Plot:
                    if loopPlot.getBonusType(iPlotOwner) != -1:
                        # Horse - 1.5% Appearance
                        if loopPlot.getBonusType(iPlotOwner) == bonus_horse:
                            iUnitType = gc.getInfoTypeForString("UNIT_WILD_HORSE")
                            iUnitTypeDom = gc.getInfoTypeForString("UNIT_HORSE")
                            iTechDom = gc.getInfoTypeForString("TECH_PFERDEZUCHT")
                            sTextDom = "TXT_KEY_INFO_DOM_HORSE"
                            if loopPlot.getNumUnits() == 0:
                                if CvUtil.myRandom(75, "horse") == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1 and iPlotOwner != iBarbPlayer:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(iTechDom):
                                            iNewUnitOwner = iPlotOwner
                                            iUnitType = iUnitTypeDom
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText(sTextDom, ("",)), None, 2, gc.getBonusInfo(bonus_horse).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                        # Camel - 1.5% Appearance
                        elif loopPlot.getBonusType(iPlotOwner) == bonus_camel:
                            iUnitType = gc.getInfoTypeForString("UNIT_WILD_CAMEL")
                            iUnitTypeDom = gc.getInfoTypeForString("UNIT_CAMEL")
                            iTechDom = gc.getInfoTypeForString("TECH_KAMELZUCHT")
                            sTextDom = "TXT_KEY_INFO_DOM_CAMEL"
                            if loopPlot.getNumUnits() == 0:
                                if CvUtil.myRandom(75, "camel") == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(iTechDom):
                                            iNewUnitOwner = iPlotOwner
                                            iUnitType = iUnitTypeDom
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText(sTextDom, ("",)), None, 2, gc.getBonusInfo(bonus_camel).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                        # Elefant - 1.5% Appearance (ab Eisenzeit)
                        elif loopPlot.getBonusType(iPlotOwner) == bonus_ivory and pBarbPlayer.getCurrentEra() >= 2:
                            iUnitType = gc.getInfoTypeForString("UNIT_ELEFANT")
                            if loopPlot.getNumUnits() == 0:
                                if CvUtil.myRandom(75, "ele") == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
                                            iNewUnitOwner = iPlotOwner
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_INFO_DOM_ELEFANT", ("",)), None, 2, gc.getBonusInfo(bonus_ivory).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

# --------- Strandgut -----------
# -- PAE V: Treibgut -> Strandgut
def doStrandgut():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    iTreibgut = gc.getInfoTypeForString("UNIT_TREIBGUT")
    iStrandgut = gc.getInfoTypeForString("UNIT_STRANDGUT")
    iGoldkarren = gc.getInfoTypeForString("UNIT_GOLDKARREN")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    eCoast = gc.getInfoTypeForString("TERRAIN_COAST")

    lUnits = PyPlayer(iBarbPlayer).getUnitsOfType(iTreibgut)
    for loopUnit in lUnits:
        pPlot = loopUnit.plot()
        if pPlot.getTerrainType() == eCoast:
            lPlots = []
            iX = pPlot.getX()
            iY = pPlot.getY()
            # iRange = 1
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
            # for i in range(-iRange, iRange+1):
                # for j in range(-iRange, iRange+1):
                    # loopPlot = plotXY(iX, iY, i, j)
                if loopPlot is not None and not loopPlot.isNone():
                    if not loopPlot.isWater():
                        if not loopPlot.isPeak() and not loopPlot.isUnit() and loopPlot.getFeatureType() != iDarkIce:
                            lPlots.append(loopPlot)

            if lPlots:
                pPlot = lPlots[CvUtil.myRandom(len(lPlots), "strandgut")]
                # Create Strandgut
                CvUtil.spawnUnit(iStrandgut, pPlot, pBarbPlayer)
                iPlotOwner = pPlot.getOwner()
                if iPlotOwner != -1 and gc.getPlayer(iPlotOwner).isHuman():
                    CyInterface().addMessage(iPlotOwner, True, 15, CyTranslator().getText("TXT_KEY_TREIB2STRANDGUT", ()), None, 2, None, ColorTypes(gc.getInfoTypeForString("COLOR_YIELD_FOOD")), pPlot.getX(), pPlot.getY(), False, False)
                # Disband Treibgut
                # loopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                loopUnit.kill(True, -1)  # RAMK_CTD
                loopUnit = None
        elif pPlot.isCity():
            # Create Goldkarren
            CvUtil.spawnUnit(iGoldkarren, pPlot, pBarbPlayer)
            # Disband Treibgut
            # loopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            loopUnit.kill(True, -1)  # RAMK_CTD
            loopUnit = None
     # --------- Strandgut -----------

##### Goody-Doerfer erstellen (goody-huts / GoodyHuts / Goodies / Villages) ####
# PAE V: Treibgut erstellen
# PAE V: Barbarenfort erstellen
def setGoodyHuts():
    # Keine extra GoodyHuts bei MultiBarbPlayer
    # Keine Festungen mit deaktvierten Barbaren
    if not bMultiPlayer or bBarbForts:
        iBarbPlayer = gc.getBARBARIAN_PLAYER()
        pBarbPlayer = gc.getPlayer(iBarbPlayer)
        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()
        iNumSetGoodies = 0
        iNumSetFlotsam = 0

        impGoody = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
        impBarbFort = gc.getInfoTypeForString("IMPROVEMENT_BARBARENFORT")
        # Treibgut spaeter wenn jeder Schiffe hat, die auf Ozean fahren koennen (Bireme)
        iUnit = gc.getInfoTypeForString("UNIT_TREIBGUT")
        iTech = gc.getInfoTypeForString("TECH_RUDERER2")

        terrOzean = gc.getInfoTypeForString("TERRAIN_OCEAN")

        bFlot = gc.getTeam(pBarbPlayer.getTeam()).isHasTech(iTech)

        #  0 = WORLDSIZE_DUEL
        #  1 = WORLDSIZE_TINY
        #  2 = WORLDSIZE_SMALL
        #  3 = WORLDSIZE_STANDARD
        #  4 = WORLDSIZE_LARGE
        #  5 = WORLDSIZE_HUGE
        iMapSize = gc.getMap().getWorldSize()
        if iMapSize == 0:
            iMaxHuts = 3
        elif iMapSize == 1:
            iMaxHuts = 6
        elif iMapSize == 2:
            iMaxHuts = 9
        elif iMapSize == 3:
            iMaxHuts = 12
        elif iMapSize == 4:
            iMaxHuts = 15
        elif iMapSize == 5:
            iMaxHuts = 18
        else:
            iMaxHuts = 20

        iMaxFlot = iMaxHuts / 2

        # TODO: geht das nicht schneller?
        # Bis zu iNumTries soll versucht werden, ein Dorf zu erstellen
        iNumTries = iMaxHuts
        for _ in range(iNumTries):
            iX = CvUtil.myRandom(iMapW, "W_hut")
            iY = CvUtil.myRandom(iMapH, "H_hut")

            if iNumSetGoodies >= iMaxHuts:
                break

            # Terrain checken
            loopPlot = gc.getMap().plot(iX, iY)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce:
                    continue
                if not loopPlot.isWater():
                    if not loopPlot.isPeak() and loopPlot.getImprovementType() == -1 and loopPlot.getNumUnits() == 0 and not loopPlot.isActiveVisible(0):
                        if loopPlot.getOwner() == -1 or loopPlot.getOwner() == iBarbPlayer:
                            bSet = True
                            iRange = 5
                            # Im Umkreis von 5 Feldern soll kein weiteres Goody oder City sein
                            for x in range(-iRange, iRange+1):
                                for y in range(-iRange, iRange+1):
                                    loopPlot2 = plotXY(iX, iY, x, y)
                                    if loopPlot2 is not None and not loopPlot2.isNone():
                                        if loopPlot2.isGoody() or loopPlot2.isCity():
                                            bSet = False
                                            break
                                if not bSet:
                                    break
                            if not bSet:
                                break

                            # Goody setzen oder Barbarenfort
                            # No extra Goody Huts in Multiplayer Mode
                            if bMultiPlayer:
                                imp = -1
                            else:
                                imp = impGoody

                            # Barbarian Forts nur mit aktivierten Barbaren
                            if bBarbForts:
                                randFort = CvUtil.myRandom(2, "barbFort")
                                if bRageBarbs:
                                    if loopPlot.isHills() or randFort == 1:
                                        imp = impBarbFort
                                elif loopPlot.isHills() and randFort == 1:
                                    imp = impBarbFort
                            loopPlot.setImprovementType(imp)
                            iNumSetGoodies += 1
                            #loopPlot.isActiveVisible(0)

                            # Einheit in die Festung setzen
                            if imp == impBarbFort:
                                PAE_Barbaren.setFortDefence(loopPlot)

                            # ***TEST***
                            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Goody Dorf/Festung/Nix gesetzt",imp)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                # isWater
                elif bFlot:
                    if not bMultiPlayer:
                        if loopPlot.getOwner() == -1:
                            if loopPlot.getTerrainType() == terrOzean:
                                if iNumSetFlotsam < iMaxFlot:
                                    # Treibgut setzen
                                    CvUtil.spawnUnit(iUnit, loopPlot, pBarbPlayer)
                                    iNumSetFlotsam += 1


# New Seewind-Feature together with Elwood (ideas) and the TAC-Team (diagonal arrows)
def doSeewind():
    terr_ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
    feat_ice = gc.getInfoTypeForString("FEATURE_ICE")

    iNumDirection = 8
    iWindplots = 6 # amount of wind arrows (plots) per wind
    OceanPlots = []
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    # get all ocean plots
    for i in range(iMapW):
        for j in range(iMapH):
            loopPlot = gc.getMap().plot(i, j)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.getTerrainType() == terr_ocean:
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getFeatureType() != iDarkIce:
                        OceanPlots.append(loopPlot)

    if OceanPlots:
        #  0 = WORLDSIZE_DUEL
        #  1 = WORLDSIZE_TINY
        #  2 = WORLDSIZE_SMALL
        #  3 = WORLDSIZE_STANDARD
        #  4 = WORLDSIZE_LARGE
        #  5 = WORLDSIZE_HUGE
        iMaxEffects = (gc.getMap().getWorldSize() + 1) * 2
        for i in range(iMaxEffects):
            # get first ocean plot
            iRand = CvUtil.myRandom(len(OceanPlots), "doSeewind1")
            loopPlot = OceanPlots[iRand]
            # First direction
            iDirection = CvUtil.myRandom(iNumDirection, "doSeewind2")

            # Start Windplots
            for j in range(iWindplots):
                if loopPlot is not None and not loopPlot.isNone():
                    if loopPlot.getFeatureType() == iDarkIce:
                        continue
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
                        loopPlot.setFeatureType(L.LSeewind[iDirection], 0)
                        iDirection = (iDirection+CvUtil.myRandom(3, "doSeewind3")-1)%iNumDirection
                        loopPlot = plotDirection(loopPlot.getX(), loopPlot.getY(), DirectionTypes(iDirection))


def doHistory():
    """++++++++++++++++++ Historische Texte ++++++++++++++++++++++++++++++++++++++++++++++"""
    iGameYear = gc.getGame().getGameTurnYear()
    # txts = 0
    if iGameYear in lNumHistoryTexts:
        txts = lNumHistoryTexts[iGameYear]
    # if txts > 0:
        iRand = CvUtil.myRandom(txts, "doHistory")

        # iRand 0 bedeutet keinen Text anzeigen. Bei mehr als 2 Texte immer einen einblenden
        if txts > 2:
            iRand += 1

        if iRand > 0:
            text = "TXT_KEY_HISTORY_"
            if iGameYear < 0:
                text = text + str(iGameYear * (-1)) + "BC_" + str(iRand)
            else:
                text = text + str(iGameYear) + "AD_" + str(iRand)

            text = CyTranslator().getText("TXT_KEY_HISTORY", ("",)) + " " + CyTranslator().getText(text, ("",))
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 15, text, None, 2, None, ColorTypes(14), 0, 0, False, False)

def doRevoltAnarchy(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    iRand = CvUtil.myRandom(3, "getAnarchyTurns")
    if iRand == 1:
        iBuilding = gc.getInfoTypeForString("BUILDING_PLAGUE")
        iNumCities = pPlayer.getNumCities()
        iCityPlague = 0
        iCityRevolt = 0
        (loopCity, pIter) = pPlayer.firstCity(False)
        while loopCity:
            if not loopCity.isNone() and loopCity.getOwner() == iPlayer: #only valid cities
                if loopCity.isHasBuilding(iBuilding):
                    iCityPlague += 1
                if loopCity.getOccupationTimer() > 1: # Flunky: changed 0->1, because the counter is not yet updated from the previous round.
                    iCityRevolt += 1
            (loopCity, pIter) = pPlayer.nextCity(pIter, False)

        if iCityRevolt > 1 and iNumCities <= iCityRevolt * 2:
            pPlayer.changeAnarchyTurns(3)
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_PLAYER_ANARCHY_FROM_REVOLTS", ("", )))
                popupInfo.addPopup(iPlayer)

        elif iNumCities <= iCityPlague * 2:
            pPlayer.changeAnarchyTurns(2)
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_PLAYER_ANARCHY_FROM_PLAGUE", ("", )))
                popupInfo.addPopup(iPlayer)
