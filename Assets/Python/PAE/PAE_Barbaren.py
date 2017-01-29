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

iBarbPlayer = gc.getBARBARIAN_PLAYER()
pBarbPlayer = gc.getPlayer(iBarbPlayer)

def myRandom (num):
    if num <= 1: return 0
    else: return random.randint(0, num-1)

# ------ Handelsposten erzeugen Kultur (PAE V Patch 3: und wieder Forts/Festungen)
# ------ Berberloewen erzeugen
# ------ Wildpferde, Wildelefanten, Wildkamele ab PAE V
# ------ Barbarenfort beleben (PAE V Patch 4)
def doPlotFeatures():
    lImpForts = []
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_HANDELSPOSTEN'))
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT'))
    lImpForts.append(gc.getInfoTypeForString('IMPROVEMENT_FORT2'))

    impBarbFort = gc.getInfoTypeForString("IMPROVEMENT_BARBARENFORT")

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
        if not loopPlot.isWater() and not loopPlot.isPeak():

          iPlotOwner = loopPlot.getOwner()

          # nur ausserhalb von Staedten
          if not loopPlot.isCity():

            # Handelsposten und Forts
            if iPlotOwner == -1 and loopPlot.getImprovementType() in lImpForts:
              # Init
              iOwner = -1

              # Handelsposten
              if loopPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):
                  txt = CvUtil.getScriptData(loopPlot,["p","t"])
                  if txt != "": iOwner = int(txt)
                  else: iOwner = loopPlot.getOwner()

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


            # Lion - 2% Appearance
            elif iPlotOwner == -1 and loopPlot.getBonusType(-1) == bonus_lion:
              if loopPlot.getImprovementType() == -1:
                if loopPlot.getNumUnits() < 3:
                  if myRandom(50) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_LION")
                    pBarbPlayer.initUnit(iUnitType, x, y, UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Barb. Atlasloewe erschaffen",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


            # Barbarenforts/festungen (erzeugt barbarische Einheiten alle x Runden)
            elif loopPlot.getImprovementType() == impBarbFort:
              if iPlotOwner == -1 or iPlotOwner == iBarbPlayer:
                if loopPlot.getNumUnits() == 0:
                  # Verteidiger setzen
                  setFortDefence(loopPlot)
                else:
                  if pBarbPlayer.getCurrentEra() > 0 and gc.getGame().getGameTurn() % 5 == 0:
                    # Einheit(en) setzen
                    createBarbUnit(loopPlot)


          # end if --- nur ausserhalb von Staedten

          # Bei jedem Plot:

          if loopPlot.getBonusType(iPlotOwner) != -1:
           # ab Bronzezeit
           if pBarbPlayer.getCurrentEra() > 0:
            # Horse - 1.5% Appearance
            if loopPlot.getBonusType(iPlotOwner) == bonus_horse: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if myRandom(75) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_WILD_HORSE")

                    # Check Owner
                    iNewUnitOwner = iBarbPlayer
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PFERDEZUCHT")):
                        iNewUnitOwner = iPlotOwner
                        iUnitType = gc.getInfoTypeForString("UNIT_HORSE")
                      elif gc.getPlayer(iPlotOwner).isHuman():
                        CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_INFO_DOM_HORSE",("",)), None, 2, gc.getBonusInfo(bonus_horse).getButton(), ColorTypes(14), x, y, True, True)

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pferd erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Camel - 1.5% Appearance
            elif loopPlot.getBonusType(iPlotOwner) == bonus_camel: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if myRandom(75) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_WILD_CAMEL")

                    # Check Owner
                    iNewUnitOwner = iBarbPlayer
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_KAMELZUCHT")):
                        iNewUnitOwner = iPlotOwner
                        iUnitType = gc.getInfoTypeForString("UNIT_CAMEL")
                      elif gc.getPlayer(iPlotOwner).isHuman():
                        CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_INFO_DOM_CAMEL",("",)), None, 2, gc.getBonusInfo(bonus_camel).getButton(), ColorTypes(14), x, y, True, True)

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Kamel erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Elefant - 1.5% Appearance (ab Eisenzeit)
            elif loopPlot.getBonusType(iPlotOwner) == bonus_ivory and pBarbPlayer.getCurrentEra() >= 2: # and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS):
              #if loopPlot.getImprovementType() == -1:
              if loopPlot.getNumUnits() == 0:
                  if myRandom(75) == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_ELEFANT")

                    # Check Owner
                    iNewUnitOwner = iBarbPlayer
                    if iPlotOwner != -1:
                      if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
                        iNewUnitOwner = iPlotOwner
                      elif gc.getPlayer(iPlotOwner).isHuman():
                        CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_INFO_DOM_ELEFANT",("",)), None, 2, gc.getBonusInfo(bonus_ivory).getButton(), ColorTypes(14), x, y, True, True)

                    # Add Unit
                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Elefant erschaffen",iNewUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# --------- Strandgut -----------
# -- PAE V: Treibgut -> Strandgut
def doStrandgut():

     iTreibgut = gc.getInfoTypeForString("UNIT_TREIBGUT")
     iStrandgut = gc.getInfoTypeForString("UNIT_STRANDGUT")
     iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

     (loopUnit, iter) = pBarbPlayer.firstUnit(false)
     while loopUnit:
       if loopUnit.getUnitType() == iTreibgut:
         pPlot = loopUnit.plot()
         if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_COAST"):

           lPlots = []
           iX = pPlot.getX()
           iY = pPlot.getY()
           iRange = 1
           for i in range(-iRange, iRange+1):
             for j in range(-iRange, iRange+1):
               loopPlot = plotXY(iX, iY, i, j)
               if loopPlot == None or loopPlot.isNone(): continue
               if loopPlot.isPeak() or loopPlot.isUnit() or loopPlot.getFeatureType() == iDarkIce: continue
               lPlots.append(loopPlot)

           if len(lPlots) > 0:
             iPlot = myRandom(len(lPlots))
             # Create Strandgut
             pBarbPlayer.initUnit(iStrandgut, lPlots[iPlot].getX(), lPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
             # Disband Treibgut
             loopUnit.kill(1,iBarbPlayer)
       (loopUnit, iter) = pBarbPlayer.nextUnit(iter, false)
     # --------- Strandgut -----------

##### Goody-Doerfer erstellen (goody-huts / GoodyHuts / Goodies / Villages) ####
# PAE V: Treibgut erstellen
# PAE V: Barbarenfort erstellen
def setGoodyHuts():
    # Keine extra GoodyHuts bei MultiBarbPlayer
    # Keine Festungen mit deaktvierten Barbaren
    if not bMultiPlayer or bBarbForts:

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

        if gc.getTeam(pBarbPlayer.getTeam()).isHasTech(iTech): bFlot = True
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
        iNumTries = iMaxHuts
        for i in range(iNumTries):
            iX = myRandom(iMapW)
            iY = myRandom(iMapH)

            if iNumSetGoodies >= iMaxHuts: break

            # Terrain checken
            loopPlot = CyMap().plot(iX, iY)
            if loopPlot != None and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater():
                    if not loopPlot.isPeak() and loopPlot.getImprovementType() == -1 and loopPlot.getNumUnits() == 0 and not loopPlot.isActiveVisible(0):
                        if loopPlot.getOwner() == -1 or loopPlot.getOwner() == iBarbPlayer:
                            bSet = True
                            iRange = 5
                            # Im Umkreis von 5 Feldern soll kein weiteres Goody oder City sein
                            for x in range(-iRange,iRange+1):
                              for y in range(-iRange,iRange+1):
                                loopPlot2 = plotXY(iX, iY, x, y)
                                if loopPlot2 != None and not loopPlot2.isNone():
                                  if loopPlot2.isGoody() or loopPlot2.isCity():
                                    bSet = False
                                    break
                              if not bSet: break

                            # Goody setzen oder Barbarenfort
                            if bSet:
                              # No extra Goody Huts in MultiBarbPlayer Mode
                              if bMultiPlayer: imp = -1
                              else: imp = impGoody

                              # Barbarian Forts nur mit aktivierten Barbaren
                              if bBarbForts:
                                if bRageBarbs:
                                  if loopPlot.isHills( ) or myRandom(2) == 1: imp = impBarbFort
                                elif loopPlot.isHills() and myRandom(2) == 1: imp = impBarbFort
                              loopPlot.setImprovementType(imp)
                              iNumSetGoodies += 1
                              #loopPlot.isActiveVisible(0)

                              # Einheit in die Festung setzen
                              if imp == impBarbFort: setFortDefence(loopPlot)

                              # ***TEST***
                              #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Goody Dorf/Festung/Nix gesetzt",imp)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                # isWater
                elif bFlot:
                    if not bMultiPlayer:
                        if loopPlot.getOwner() == -1:
                            if loopPlot.getTerrainType() == terrOzean:
                                if iNumSetFlotsam < iMaxFlot:
                                    # Treibgut setzen
                                    pBarbPlayer.initUnit(iUnit, loopPlot.getX(), loopPlot.getY(), UnitAITypes.UNITAI_EXPLORE_SEA, DirectionTypes.DIRECTION_SOUTH)
                                    iNumSetFlotsam += 1
     # -------------------------------

# leere Festung mit barbarischen Einheiten belegen
def setFortDefence(pPlot):
    # inits
    pTeam = gc.getTeam(pBarbPlayer.getTeam())

    iPromo = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") # Moves -1
    iPromo2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") # Moves -2

    iAnz = 1
    if bRageBarbs: iAnz += 2

    # Einheit herausfinden
    #iUnit = gc.getInfoTypeForString("UNIT_LIGHT_ARCHER")
    #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_REFLEXBOGEN")): iUnit = gc.getInfoTypeForString("UNIT_REFLEX_ARCHER")
    #elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_ARCHERY3")): iUnit = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
    #elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_ARCHERY2")): iUnit = gc.getInfoTypeForString("UNIT_ARCHER")
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
    #pTeam = gc.getTeam(pPlayer.getTeam())

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
    barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
    iUnitTypeShip = gc.getInfoTypeForString("UNIT_SEEVOLK")
    iUnitTypeWarrior1 = gc.getInfoTypeForString("UNIT_SEEVOLK_2")
    iUnitTypeWarrior2 = gc.getInfoTypeForString("UNIT_SEEVOLK_3")

    # Handicap: 0 (Settler) - 8 (Deity)
    # Worldsize: 0 (Duell) - 5 (Huge)
    iRange = 1 + gc.getMap().getWorldSize() + gc.getGame().getHandicapType()

    for i in range (iRange):
      # Diese Koordinaten entsprechen ungefaehr dem Mittelmeer: Ships(range):3 | X: 19-59(40) | Y:9-37(28)
      #iRandX = 19 + myRandom(40)
      #iRandY = 9 + myRandom(28)

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
            barbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
            barbPlayer.initUnit(iUnitTypeWarrior1, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            barbPlayer.initUnit(iUnitTypeWarrior2, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doVikings():
  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
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
        barbPlayer.initUnit(iUnitTypeShip, iRandX, iRandY, UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
        for j in range (4):
          barbPlayer.initUnit(iUnitTypeUnit, iRandX, iRandY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doHandelskarren():
  barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
  iUnitTypeMerchant1 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANT")
  iUnitTypeMerchant2 = gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN")
  iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
  iMapW = gc.getMap().getGridWidth()
  iMapH = gc.getMap().getGridHeight()
  for i in range (4):
    iRandX = myRandom(iMapW)
    iRandY = myRandom(iMapH)
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

def doHuns():
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
        loopPlot = CyMap().plot(iRandX, iRandY)
        if None != loopPlot and not loopPlot.isNone():
          if loopPlot.getFeatureType() != iDarkIce:
            if not loopPlot.isUnit() and not loopPlot.isWater() and not loopPlot.isOwned() and not loopPlot.isPeak():
              bPlot = True
              break

      # wenn ein Plot gefunden wurde
      if bPlot:

        # Hunnen versuchen zu erstellen  1 == 2: Ausgeschaltet!
        iMaxPlayers = gc.getMAX_PLAYERS()
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
              j = iMaxPlayers-i
              pPlayer = gc.getPlayer(j)
              if not pPlayer.isAlive():
                iHunsID = j
                break

          if iHunsID > 0:
            # Hunnen erstellen
            LeaderHuns = gc.getInfoTypeForString("LEADER_ATTILA")
            gc.getGame().addPlayer(iHunsID,LeaderHuns,CivHuns)
            pPlayer = gc.getPlayer(iHunsID)
            
            iX = loopPlot.getX()
            iY = loopPlot.getY()
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
            iX = loopPlot.getX()
            iY = loopPlot.getY()
            for _ in range(iHuns):
                barbPlayer.initUnit(iUnitType, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
