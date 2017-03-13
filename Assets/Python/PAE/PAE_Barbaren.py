# Barbarian features and events

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random
import itertools
### Defines
gc = CyGlobalContext()

bMultiPlayer = False
bGoodyHuts = True
bBarbForts = True
bRageBarbs = False
if gc.getGame().isGameMultiPlayer(): bMultiPlayer = True
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS): bGoodyHuts = False
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS): bBarbForts = False
if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_RAGING_BARBARIANS): bRageBarbs = True

def myRandom (num):
    if num <= 1: return 0
    else: return random.randint(0, num-1)

# leere Festung mit barbarischen Einheiten belegen
def setFortDefence(pPlot):
    # inits
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)

    iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") # Moves -1
    iPromo2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") # Moves -2

    iAnz = 1
    if bRageBarbs: iAnz += 2

    # Einheit herausfinden
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_REFLEX_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_ARCHER")
    else: iUnit = gc.getInfoTypeForString("UNIT_LIGHT_ARCHER")

    # Einheit setzen
    for i in range(iAnz):
      pUnit = pBarbPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
      if pUnit.getMoves() > 1: pUnit.setHasPromotion(iPromo2, True)
      else: pUnit.setHasPromotion(iPromo, True)
      pUnit.finishMoves()

# Barbarische Einheit erzeugen
def createBarbUnit(pPlot):
    if not bBarbForts: return

    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)

    iAnz = 1
    if bRageBarbs: iAnz += 1

    lUnits = []
    # Bogen
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_REFLEX_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_ARCHER")
    else: iUnit = gc.getInfoTypeForString("UNIT_LIGHT_ARCHER")
    lUnits.append(iUnit)

    # Speer
    iUnit = -1
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_SPEARMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN")
    if iUnit != -1: lUnits.append(iUnit)

    # Axt
    iUnit = -1
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_WURFAXT"),0,0): iUnit = gc.getInfoTypeForString("UNIT_WURFAXT")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN2"),0,0): iUnit = gc.getInfoTypeForString("UNIT_AXEMAN2")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_AXEMAN")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_AXEWARRIOR"),0,0): iUnit = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
    if iUnit != -1: lUnits.append(iUnit)

    # Schwert
    iUnit = -1
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_SWORDSMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_SWORDSMAN")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_KURZSCHWERT"),0,0):
     lUnits.append(gc.getInfoTypeForString("UNIT_KURZSCHWERT"))
     if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"))
    if iUnit != -1: lUnits.append(iUnit)

    # Reiter
    iUnit = -1
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_CATAPHRACT"),0,0): iUnit = gc.getInfoTypeForString("UNIT_CATAPHRACT")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSEMAN_LANCIER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_HORSEMAN_LANCIER")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSEMAN_SKYTHEN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_HORSEMAN_SKYTHEN")
    elif pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSEMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_HORSEMAN")
    if iUnit != -1: lUnits.append(iUnit)

    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
    if pBarbPlayer.canTrain(gc.getInfoTypeForString("UNIT_CLIBANARII"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_CLIBANARII"))

    lUnitAIs = [UnitAITypes.UNITAI_ATTACK,UnitAITypes.UNITAI_PILLAGE,UnitAITypes.UNITAI_ATTACK_CITY_LEMMING]
    # Einheit setzen
    for i in range(iAnz):
      iUnit = lUnits[myRandom(len(lUnits))]
      pUnit = pBarbPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), lUnitAIs[myRandom(len(lUnitAIs))], DirectionTypes.DIRECTION_SOUTH)
      pUnit.finishMoves()


# ------ Camp/Kriegslager Einheit setzen (PAE V Patch 4)
def createCampUnit(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)

    if pPlayer.isAlive():
       if pPlayer.getUnitClassCount(gc.getInfoTypeForString("UNITCLASS_SPECIAL1")) > 0:

          # Terrain
          eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
          eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
          eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
          eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
          # Feature
          eDichterWald = gc.getInfoTypeForString("FEATURE_DICHTERWALD")

          eCamp = gc.getInfoTypeForString("UNIT_CAMP")

          (pUnit, iter) = pPlayer.firstUnit(false)
          while pUnit:
              if pUnit.getUnitType() == eCamp:
                 #pUnit.NotifyEntity(MissionTypes.MISSION_FOUND)
                 pPlot = pUnit.plot()
                 iUnit = -1

                 # Tundra
                 if pPlot.getTerrainType() == eTundra:
                    # Ebene
                    if pPlot.getFeatureType() == -1:
                       if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),0,0): iUnit = gc.getInfoTypeForString("UNIT_MONGOL_KESHIK")
                    # Wald
                    else:
                       if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_REFLEX_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
                       else: iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")

                 # Wald
                 elif pPlot.getFeatureType() != -1:
                    if pPlot.getFeatureType() == eDichterWald:
                       if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN2"),0,0): iUnit = gc.getInfoTypeForString("UNIT_AXEMAN2")
                    else:
                       if pPlot.isHills():
                          if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_SWORDSMAN"),0,0): iUnit = gc.getInfoTypeForString("UNIT_SWORDSMAN")
                          elif pPlayer.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
                          else: iUnit = gc.getInfoTypeForString("UNIT_KURZSCHWERT")
                       else: iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")

                 # Open Grass
                 elif pPlot.getTerrainType() == eGras:
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),0,0): iUnit = gc.getInfoTypeForString("UNIT_HORSE_ARCHER")

                 # Open Plains
                 elif pPlot.getTerrainType() == eEbene:
                    lUnits = []
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_CATAPHRACT"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_CATAPHRACT"))
                    if len(lUnits) == 0 and pPlayer.canTrain(gc.getInfoTypeForString("UNIT_HORSEMAN"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_HORSEMAN"))
                    if len(lUnits):
                       iUnit = lUnit[myRandom(len(lUnits))]

                 # Desert
                 elif pPlot.getTerrainType() == eDesert:
                    lUnits = []
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                    if pPlayer.canTrain(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"),0,0): lUnits.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))
                    if len(lUnits):
                       iUnit = lUnit[myRandom(len(lUnits))]

                 # Reserve Einheit, die immer geht
                 if iUnit == -1: iUnit = gc.getInfoTypeForString("UNIT_SPEARMAN")

                 # AI: Einheit autom, verkaufen (Soeldnerposten), falls Geldprobleme
                 if not pPlayer.isHuman():
                    if pPlayer.AI_isFinancialTrouble():
                       pPlayer.changeGold(50)
                       iUnit = -1

                 # Einheit erstellen
                 if iUnit != -1: pPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

              (pUnit, iter) = pPlayer.nextUnit(iter, false)
          # while end
    # if alive
    return

def doSeevoelker():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)

    iUnitTypeShip = gc.getInfoTypeForString("UNIT_SEEVOLK")
    iUnitTypeWarrior1 = gc.getInfoTypeForString("UNIT_SEEVOLK_2")
    iUnitTypeWarrior2 = gc.getInfoTypeForString("UNIT_SEEVOLK_3")

    # Handicap: 0 (Settler) - 8 (Deity)
    # Worldsize: 0 (Duell) - 5 (Huge)
    iRange = 1 + gc.getMap().getWorldSize() + gc.getGame().getHandicapType()

    for i in range (iRange):
      # Wird geaendert zu einem Mittelmeerstreifen: x: 5 bis (X-5), y: 5 bis letztes Drittel von Y
      iMapX = gc.getMap().getGridWidth() - 5
      iMapY = int(gc.getMap().getGridHeight() / 3 * 2)
      iRandX = 5 + myRandom(iMapX)
      iRandY = 5 + myRandom(iMapY)

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
            pBarbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
            pBarbPlayer.initUnit(iUnitTypeWarrior1, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            pBarbPlayer.initUnit(iUnitTypeWarrior2, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doVikings():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    iUnitTypeShip = gc.getInfoTypeForString("UNIT_VIKING_1")
    iUnitTypeUnit = gc.getInfoTypeForString("UNIT_VIKING_2")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    for i in range (4):
        iRandX = iMapH - myRandom(5)
        iRandY = myRandom(iMapW)
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        # Es soll auch ein 2tes Feld Wasser sein
        loopPlot2 = gc.getMap().plot(iRandX+1, iRandY)
        if None != loopPlot and not loopPlot.isNone() and None != loopPlot2 and not loopPlot2.isNone():
          if loopPlot.getFeatureType() == iDarkIce or loopPlot2.getFeatureType() == iDarkIce: continue
          if not loopPlot.isUnit() and loopPlot.isWater() and loopPlot2.isWater() and not loopPlot.isOwned():
            # Wikinger erstellen
            pBarbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
            for j in range (4):
              pBarbPlayer.initUnit(iUnitTypeUnit, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doHandelskarren():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    iUnitTypeMerchant1 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANT")
    iUnitTypeMerchant2 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    for i in range (4):
        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        if None != loopPlot and not loopPlot.isNone():
            if loopPlot.getFeatureType() != iDarkIce:
                if not loopPlot.isUnit() and not loopPlot.isOwned():
                    if loopPlot.isWater()  and gc.getGame().getGameTurnYear() > -600:
                        if loopPlot.area().getNumTiles() >= gc.getMIN_WATER_SIZE_FOR_OCEAN():
                            pBarbPlayer.initUnit(iUnitTypeMerchant2, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    elif not loopPlot.isWater() and not loopPlot.isPeak():
                        if loopPlot.area().getNumTiles() >= 5:
                            pBarbPlayer.initUnit(iUnitTypeMerchant1, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doHuns(iGameTurn):
  iHuns = 0
  if gc.getGame().getGameTurnYear() == 250: iHuns = 20
  elif gc.getGame().getGameTurnYear() == 255: iHuns = 24
  elif gc.getGame().getGameTurnYear() == 260: iHuns = 28
  elif gc.getGame().getGameTurnYear() >= 270 and gc.getGame().getGameTurnYear() <= 400 and iGameTurn % 10 == 0: iHuns = 28  # Diesen Wert auch unten bei der Meldung angeben!

  if iHuns > 0:

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
        iRandX = iMapW - 15 + myRandom(15)
        iRandY = iMapH - 15 + myRandom(15)
        loopPlot = gc.getMap().plot(iRandX, iRandY)
        if None != loopPlot and not loopPlot.isNone():
          if loopPlot.getFeatureType() != iDarkIce:
            if not loopPlot.isUnit() and not loopPlot.isWater() and not loopPlot.isOwned() and not loopPlot.isPeak():
              bPlot = True
              break

      iX = loopPlot.getX()
      iY = loopPlot.getY()
      # wenn ein Plot gefunden wurde
      if bPlot:
        # Hunnen versuchen zu erstellen  1 == 2: Ausgeschaltet!
        if gc.getGame().getGameTurnYear() >= 250 and gc.getGame().countCivPlayersAlive() < iMaxPlayers and 1 == 2:
          # freie PlayerID herausfinden
          iHunsID = 0
          for i in range(iMaxPlayers):
            pPlayer = gc.getPlayer(i)
            if not pPlayer.isEverAlive():
              iHunsID = i
              break
          # wenn keine nagelneue ID frei ist, dann eine bestehende nehmen
          if iHunsID == 0:
            for i in range(iMaxPlayers):
              j = iMaxPlayers-i-1
              pPlayer = gc.getPlayer(j)
              if not pPlayer.isAlive():
                iHunsID = j
                break

          if iHunsID > 0:
            # Hunnen erstellen
            LeaderHuns = gc.getInfoTypeForString("LEADER_ATTILA")
            gc.getGame().addPlayer(iHunsID,LeaderHuns,CivHuns)
            pPlayer = gc.getPlayer(iHunsID)

            iUnitSettler = gc.getInfoTypeForString("UNIT_SETTLER")
            iUnitSpearman = gc.getInfoTypeForString("UNIT_SPEARMAN")
            iUnitWorker = gc.getInfoTypeForString("UNIT_WORKER")
            iUnitKeshik = gc.getInfoTypeForString("UNIT_MONGOL_KESHIK")
            iUnitArcher = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
            iUnitHorse = gc.getInfoTypeForString("UNIT_HORSE")
            for _ in range(3):
                pPlayer.initUnit(iUnitSettler, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for _ in range(4):
                pPlayer.initUnit(iUnitSpearman, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for _ in range(6):
                pPlayer.initUnit(iUnitWorker, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for _ in range(8):
                pPlayer.initUnit(iUnitKeshik, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for _ in range(9):
                pPlayer.initUnit(iUnitArcher, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            for _ in range(9):
                pPlayer.initUnit(iUnitHorse, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

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
            for _ in range(iHuns):
                barbPlayer.initUnit(iUnitType, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
