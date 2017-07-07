# Barbarian features and events

### Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil
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


# leere Festung mit barbarischen Einheiten belegen
def setFortDefence(pPlot):
    # inits
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    eCiv = gc.getCivilizationInfo(pBarbPlayer.getCivilizationType())

    iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") # Moves -1
    iPromo2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") # Moves -2

    iAnz = 1
    if bRageBarbs:
        iAnz += 2

    # Einheit herausfinden
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER")),
        # UNITCLASS_COMPOSITE_ARCHER ist garnicht baubar
        # eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_COMPOSITE_ARCHER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ARCHER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_LIGHT_ARCHER"))
    ]
    iUnit = -1
    for iUnit in lTempUnit:
        if iUnit != -1 and pBarbPlayer.canTrain(iUnit, 0, 0):
            break
    if iUnit != -1:
        # Einheit setzen
        for _ in range(iAnz):
            pUnit = pBarbPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
            if pUnit.getMoves() > 1:
                pUnit.setHasPromotion(iPromo2, True)
            else:
                pUnit.setHasPromotion(iPromo, True)
            pUnit.finishMoves()

# Barbarische Einheit erzeugen
def createBarbUnit(pPlot):
    if not bBarbForts:
        return

    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    eCiv = gc.getCivilizationInfo(pBarbPlayer.getCivilizationType())

    iAnz = 1
    if bRageBarbs:
        iAnz += 1

    lUnits = []
    # Bogen
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_COMPOSITE_ARCHER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ARCHER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNIT_LIGHT_ARCHER"))
    ]
    iUnit = -1
    for iUnit in lTempUnit:
        if pBarbPlayer.canTrain(iUnit, 0, 0):
            break
    if iUnit != -1:
        lUnits.append(iUnit)

    # Speer
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPEARMAN")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_LIGHT_SPEARMAN"))
    ]
    for iUnit in lTempUnit:
        if pBarbPlayer.canTrain(iUnit, 0, 0):
            lUnits.append(iUnit)
            break

    # Axt
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_WURFAXT")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AXEMAN2")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AXEMAN")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AXEWARRIOR"))
    ]
    for iUnit in lTempUnit:
        if pBarbPlayer.canTrain(iUnit, 0, 0):
            lUnits.append(iUnit)
            break

    # Schwert
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SWORDSMAN")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SCHILDTRAEGER")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT"))
    ]
    for iUnit in lTempUnit:
        if pBarbPlayer.canTrain(iUnit, 0, 0):
            lUnits.append(iUnit)
            break

    # Reiter
    lTempUnit = [
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CATAPHRACT")),
        eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSEMAN"))
    ]
    for iUnit in lTempUnit:
        if pBarbPlayer.canTrain(iUnit, 0, 0):
            lUnits.append(iUnit)
            break
    iUnit = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER"))
    if pBarbPlayer.canTrain(iUnit, 0, 0):
        lUnits.append(iUnit)
    iUnit = eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CLIBANARII"))
    if pBarbPlayer.canTrain(iUnit, 0, 0):
        lUnits.append(iUnit)

    lUnitAIs = [UnitAITypes.UNITAI_ATTACK, UnitAITypes.UNITAI_PILLAGE, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING]
    # Einheit setzen
    for _ in range(iAnz):
        iUnit = lUnits[CvUtil.myRandom(len(lUnits), "createBarbUnit")]
        iUnitAI = lUnitAIs[CvUtil.myRandom(len(lUnitAIs), "createBarbUnit_AI")]
        pUnit = pBarbPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), iUnitAI, DirectionTypes.DIRECTION_SOUTH)
        pUnit.finishMoves()


# ------ Camp/Kriegslager Einheit setzen (PAE V Patch 4)
def createCampUnit(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    eCiv = gc.getCivilizationInfo(pPlayer.getCivilizationType())

    if not pPlayer.isAlive():
        return
    if pPlayer.getUnitClassCount(gc.getInfoTypeForString("UNITCLASS_SPECIAL1")) > 0:
        # Terrain
        eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
        eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
        eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
        eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
        # Feature
        eDichterWald = gc.getInfoTypeForString("FEATURE_DICHTERWALD")

        eCamp = gc.getInfoTypeForString("UNIT_CAMP")

        lUnits = PyPlayer(pPlayer.getID()).getUnitsOfType(eCamp)
        for pUnit in lUnits:
            if pUnit is not None and not pUnit.isNone():
                #pUnit.NotifyEntity(MissionTypes.MISSION_FOUND)
                pPlot = pUnit.plot()
                iUnit = -1

                # Tundra
                if pPlot.getTerrainType() == eTundra:
                    # Ebene
                    if pPlot.getFeatureType() == -1:
                        if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"), 0, 0):
                            iUnit = gc.getInfoTypeForString("UNIT_MONGOL_KESHIK")
                    # Wald
                    elif pPlayer.canTrain(gc.getInfoTypeForString("UNIT_REFLEX_ARCHER"), 0, 0):
                        iUnit = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
                    else:
                        iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")

                # Wald
                elif pPlot.getFeatureType() != -1:
                    if pPlot.getFeatureType() == eDichterWald:
                        if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN2"), 0, 0):
                            iUnit = gc.getInfoTypeForString("UNIT_AXEMAN2")
                    elif pPlot.isHills():
                        if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_SWORDSMAN"), 0, 0):
                            iUnit = gc.getInfoTypeForString("UNIT_SWORDSMAN")
                        elif pPlayer.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"), 0, 0):
                            iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
                        else:
                            iUnit = gc.getInfoTypeForString("UNIT_KURZSCHWERT")
                    else:
                        iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")

                # Open Grass
                elif pPlot.getTerrainType() == eGras:
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"), 0, 0):
                        iUnit = gc.getInfoTypeForString("UNIT_HORSE_ARCHER")

                # Open Plains
                elif pPlot.getTerrainType() == eEbene:
                    lUnits = []
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"), 0, 0):
                        lUnits.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_CATAPHRACT"), 0, 0):
                        lUnits.append(gc.getInfoTypeForString("UNIT_CATAPHRACT"))
                    if not lUnits and pPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSEMAN"), 0, 0):
                        lUnits.append(gc.getInfoTypeForString("UNIT_HORSEMAN"))
                    if lUnits:
                        iUnit = lUnits[CvUtil.myRandom(len(lUnits), "barbplains")]

                # Desert
                elif pPlot.getTerrainType() == eDesert:
                    lUnits = []
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"), 0, 0):
                        lUnits.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"), 0, 0):
                        lUnits.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))
                    if lUnits:
                        iUnit = lUnits[CvUtil.myRandom(len(lUnits), "barbdesert")]

                # Reserve Einheit, die immer geht
                if iUnit == -1:
                    iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")

                # AI: Einheit autom, verkaufen (Soeldnerposten), falls Geldprobleme
                if not pPlayer.isHuman() and pPlayer.AI_isFinancialTrouble():
                    pPlayer.changeGold(50)
                elif iUnit != -1:
                    # Einheit erstellen
                    CvUtil.spawnUnit(iUnit, pPlot, pPlayer)

def doSeevoelker():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)

    iUnitTypeShip = gc.getInfoTypeForString("UNIT_SEEVOLK")
    iUnitTypeWarrior1 = gc.getInfoTypeForString("UNIT_SEEVOLK_2")
    iUnitTypeWarrior2 = gc.getInfoTypeForString("UNIT_SEEVOLK_3")

    # Handicap: 0 (Settler) - 8 (Deity)
    # Worldsize: 0 (Duell) - 5 (Huge)
    iRange = 1 + gc.getMap().getWorldSize() + gc.getGame().getHandicapType()

    for _ in range(iRange):
        # Wird geaendert zu einem Mittelmeerstreifen: x: 5 bis (X-5), y: 5 bis letztes Drittel von Y
        iMapX = gc.getMap().getGridWidth() - 5
        iMapY = int(gc.getMap().getGridHeight() / 3 * 2)
        iRandX = 5 + CvUtil.myRandom(iMapX, "X")
        iRandY = 5 + CvUtil.myRandom(iMapY, "Y")

        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Plot soll ein Ozean sein
        terr_ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
        feat_ice = gc.getInfoTypeForString("FEATURE_ICE")
        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getFeatureType() == iDarkIce:
                continue
            if not loopPlot.isUnit() and not loopPlot.isOwned() and loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
                # Schiffe erstellen
                if gc.getGame().getGameTurnYear() > -1000:
                    iAnz = 3
                elif gc.getGame().getGameTurnYear() > -1200:
                    iAnz = 2
                else:
                    iAnz = 1
                for _ in range(iAnz):
                    CvUtil.spawnUnit(iUnitTypeShip, loopPlot, pBarbPlayer)
                    CvUtil.spawnUnit(iUnitTypeWarrior1, loopPlot, pBarbPlayer)
                    CvUtil.spawnUnit(iUnitTypeWarrior2, loopPlot, pBarbPlayer)


def doVikings():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    iUnitTypeShip = gc.getInfoTypeForString("UNIT_VIKING_1")
    iUnitTypeUnit = gc.getInfoTypeForString("UNIT_VIKING_2")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for _ in range(4):
        iRandX = iMapH - CvUtil.myRandom(5, "H")
        iRandY = CvUtil.myRandom(iMapW, "W")
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Es soll auch ein 2tes Feld Wasser sein
        loopPlot2 = gc.getMap().plot(iRandX+1, iRandY)
        if loopPlot is not None and not loopPlot.isNone() and loopPlot2 is not None and not loopPlot2.isNone():
            if loopPlot.getFeatureType() == iDarkIce or loopPlot2.getFeatureType() == iDarkIce:
                continue
            if not loopPlot.isUnit() and loopPlot.isWater() and loopPlot2.isWater() and not loopPlot.isOwned():
                # Wikinger erstellen
                CvUtil.spawnUnit(iUnitTypeShip, loopPlot, pBarbPlayer)
                for _ in range(4):
                    CvUtil.spawnUnit(iUnitTypeUnit, loopPlot, pBarbPlayer)

def doHuns(iGameTurn):
    iHuns = 0
    if gc.getGame().getGameTurnYear() == 250:
        iHuns = 20
    elif gc.getGame().getGameTurnYear() == 255:
        iHuns = 24
    elif gc.getGame().getGameTurnYear() == 260:
        iHuns = 28
    elif gc.getGame().getGameTurnYear() >= 270 and gc.getGame().getGameTurnYear() <= 400 and iGameTurn % 10 == 0:
        iHuns = 28  # Diesen Wert auch unten bei der Meldung angeben!

    if iHuns == 0:
        return

    CivHuns = gc.getInfoTypeForString("CIVILIZATION_HUNNEN")
    bHunsAlive = False

    iMaxPlayers = gc.getMAX_PLAYERS()
    for iPlayer in range(iMaxPlayers):
        pPlayer = gc.getPlayer(iPlayer)
        # Hunnen sollen nur auftauchen, wenn es nicht bereits Hunnen gibt
        if pPlayer.getCivilizationType() == CivHuns and pPlayer.isAlive():
            bHunsAlive = True
            break

    if not bHunsAlive:
        for iPlayer in range(iMaxPlayers):
            pPlayer = gc.getPlayer(iPlayer)

            # Message PopUps
            if iHuns < 28 and pPlayer.isAlive() and pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                if iHuns == 2:
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_1", ("", )))
                elif iHuns == 4:
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_2", ("", )))
                else:
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_HUNNEN_3", ("", )))
                popupInfo.addPopup(pPlayer.getID())
                CyAudioGame().Play2DSound('AS2D_THEIRDECLAREWAR')

        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()
        iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

        # 15 Versuche einen Plot zu finden
        bPlot = False
        for _ in range(15):
            # Diese Koordinaten entsprechen Nord-Osten
            iRandX = iMapW - 15 + CvUtil.myRandom(15, "W2")
            iRandY = iMapH - 15 + CvUtil.myRandom(15, "H2")
            loopPlot = gc.getMap().plot(iRandX, iRandY)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.getFeatureType() != iDarkIce and not loopPlot.isUnit() and not loopPlot.isWater() and not loopPlot.isOwned() and not loopPlot.isPeak():
                    bPlot = True
                    break

        if not bPlot:
            return

        # Hunnen versuchen zu erstellen  False: Ausgeschaltet!
        if gc.getGame().getGameTurnYear() >= 250 and gc.getGame().countCivPlayersAlive() < iMaxPlayers and False:
            # freie PlayerID herausfinden
            iHunsID = 0
            for i in range(iMaxPlayers):
                j = iMaxPlayers-i-1
                pPlayer = gc.getPlayer(j)
                if not pPlayer.isAlive():
                    iHunsID = j
                    break

            if iHunsID == 0:
                return

            # Hunnen erstellen
            LeaderHuns = gc.getInfoTypeForString("LEADER_ATTILA")
            gc.getGame().addPlayer(iHunsID, LeaderHuns, CivHuns)
            pPlayer = gc.getPlayer(iHunsID)

            iUnitSettler = gc.getInfoTypeForString("UNIT_SETTLER")
            iUnitSpearman = gc.getInfoTypeForString("UNIT_SPEARMAN")
            iUnitWorker = gc.getInfoTypeForString("UNIT_WORKER")
            iUnitKeshik = gc.getInfoTypeForString("UNIT_MONGOL_KESHIK")
            iUnitArcher = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
            iUnitHorse = gc.getInfoTypeForString("UNIT_HORSE")
            for _ in range(3):
                CvUtil.spawnUnit(iUnitSettler, loopPlot, pPlayer)
            for _ in range(4):
                CvUtil.spawnUnit(iUnitSpearman, loopPlot, pPlayer)
            for _ in range(6):
                CvUtil.spawnUnit(iUnitWorker, loopPlot, pPlayer)
            for _ in range(8):
                CvUtil.spawnUnit(iUnitKeshik, loopPlot, pPlayer)
            for _ in range(9):
                CvUtil.spawnUnit(iUnitArcher, loopPlot, pPlayer)
            for _ in range(9):
                CvUtil.spawnUnit(iUnitHorse, loopPlot, pPlayer)

            pPlayer.setCurrentEra(3)
            pPlayer.setGold(300)

            # increasing Anger to all other CIVs
            # and looking for best tech player
            pTeam = gc.getTeam(pPlayer.getTeam())
            iPlayerBestTechScore = -1
            iTechScore = 0
            for i in range(iMaxPlayers):
                pSecondPlayer = gc.getPlayer(i)
                # increases Anger for all AIs
                if pSecondPlayer.getID() != pPlayer.getID() and pSecondPlayer.isAlive():
                    # Haltung aendern
                    pPlayer.AI_changeAttitudeExtra(i, -5)
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
                    if gc.getTechInfo(iTech) is not None and xTeam.isHasTech(iTech) and not pTeam.isHasTech(iTech) and gc.getTechInfo(iTech).isTrade():
                        pTeam.setHasTech(iTech, 1, iHunsID, 0, 0)

        else:
            iUnitType = gc.getInfoTypeForString('UNIT_MONGOL_KESHIK')
            pBarbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
            for _ in range(iHuns):
                CvUtil.spawnUnit(iUnitType, loopPlot, pBarbPlayer)
