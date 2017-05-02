# Plot features and events per turn

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random
import itertools
import PAE_Barbaren
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
            loopPlot = gc.getMap().plot(x,y)
            if loopPlot != None and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
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
                                    iOwner = int(CvUtil.getScriptData(loopPlot,["p","t"], loopPlot.getOwner()))
                                # Forts
                                elif loopPlot.getNumUnits() > 0:
                                    # Besitzer ist der mit den meisten Einheiten drauf
                                    OwnerArray = {}
                                    iNumUnits = loopPlot.getNumUnits()
                                    for i in range (iNumUnits):
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
                                        loopPlot.setCulture(iPlayerID,1,True)
                                        loopPlot.setOwner(iPlayerID)
                                    else:
                                        # TODO: das macht hidden culture in ehemals besiedeltem Gebiet kaputt.
                                        loopPlot.setCulture(iPlayerID,0,True)

                            # Lion - 2% Appearance
                            elif loopPlot.getBonusType(-1) == bonus_lion and loopPlot.getImprovementType() == -1:
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
                                elif pBarbPlayer.getCurrentEra() > 0 and gc.getGame().getGameTurn() % 5 == 0:
                                    # Einheiten) setzen
                                    createBarbUnit(loopPlot)
                        # Handelsposten entfernen, wenn der Plot in einem fremden Kulturkreis liegt
                        elif loopPlot.getImprovementType() == eHandelsposten:
                          iOwner = int(CvUtil.getScriptData(loopPlot,["p","t"], loopPlot.getOwner()))
                          if iOwner != iPlotOwner:
                            loopPlot.setImprovementType(-1)
                            if gc.getPlayer(iOwner).isHuman():
                              szText = CyTranslator().getText("TXT_KEY_INFO_CLOSED_TRADEPOST",("",));
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
                                if myRandom(75) == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1 and iPlotOwner != iBarbPlayer:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(iTechDom):
                                            iNewUnitOwner = iPlotOwner
                                            iUnitType = iUnitTypeDom
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText(sTextDom,("",)), None, 2, gc.getBonusInfo(bonus_horse).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                        # Camel - 1.5% Appearance
                        elif loopPlot.getBonusType(iPlotOwner) == bonus_camel:
                            iUnitType = gc.getInfoTypeForString("UNIT_WILD_CAMEL")
                            iUnitTypeDom = gc.getInfoTypeForString("UNIT_CAMEL")
                            iTechDom = gc.getInfoTypeForString("TECH_KAMELZUCHT")
                            sTextDom = "TXT_KEY_INFO_DOM_CAMEL"
                            if loopPlot.getNumUnits() == 0:
                                if myRandom(75) == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(iTechDom):
                                            iNewUnitOwner = iPlotOwner
                                            iUnitType = iUnitTypeDom
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText(sTextDom,("",)), None, 2, gc.getBonusInfo(bonus_camel).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

                        # Elefant - 1.5% Appearance (ab Eisenzeit)
                        elif loopPlot.getBonusType(iPlotOwner) == bonus_ivory and pBarbPlayer.getCurrentEra() >= 2:
                            iUnitType = gc.getInfoTypeForString("UNIT_ELEFANT")
                            if loopPlot.getNumUnits() == 0:
                                if myRandom(75) == 1:
                                    # Check Owner
                                    iNewUnitOwner = iBarbPlayer
                                    if iPlotOwner != -1:
                                        if gc.getTeam(gc.getPlayer(iPlotOwner).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
                                            iNewUnitOwner = iPlotOwner
                                        elif gc.getPlayer(iPlotOwner).isHuman():
                                            CyInterface().addMessage(iPlotOwner, True, 10, CyTranslator().getText("TXT_KEY_INFO_DOM_ELEFANT",("",)), None, 2, gc.getBonusInfo(bonus_ivory).getButton(), ColorTypes(14), x, y, True, True)
                                    # Add Unit
                                    gc.getPlayer(iNewUnitOwner).initUnit(iUnitType, x, y, UnitAITypes.UNITAI_EXPLORE, DirectionTypes.DIRECTION_SOUTH)

# --------- Strandgut -----------
# -- PAE V: Treibgut -> Strandgut
# TODO: globale Liste mit Treibguetern fuer Zeitersparnis
def doStrandgut():
    iBarbPlayer = gc.getBARBARIAN_PLAYER()
    pBarbPlayer = gc.getPlayer(iBarbPlayer)
    iTreibgut = gc.getInfoTypeForString("UNIT_TREIBGUT")
    iStrandgut = gc.getInfoTypeForString("UNIT_STRANDGUT")
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    eCoast = gc.getInfoTypeForString("TERRAIN_COAST")

    (loopUnit, iter) = pBarbPlayer.firstUnit(false)
    while loopUnit:
        if loopUnit.getUnitType() == iTreibgut:
            pPlot = loopUnit.plot()
            if pPlot.getTerrainType() == eCoast:
                lPlots = []
                iX = pPlot.getX()
                iY = pPlot.getY()
                iRange = 1
                for i in range(-iRange, iRange+1):
                    for j in range(-iRange, iRange+1):
                        loopPlot = plotXY(iX, iY, i, j)
                        if loopPlot == None or loopPlot.isNone(): continue
                        if loopPlot.isWater(): continue
                        if loopPlot.isPeak() or loopPlot.isUnit() or loopPlot.getFeatureType() == iDarkIce: continue
                        lPlots.append(loopPlot)

                if len(lPlots) > 0:
                    iPlot = myRandom(len(lPlots))
                    # Create Strandgut
                    pBarbPlayer.initUnit(iStrandgut, lPlots[iPlot].getX(), lPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                    # Disband Treibgut
                    loopUnit.kill(1,loopUnit.getOwner())
        (loopUnit, iter) = pBarbPlayer.nextUnit(iter, false)
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

        # TODO: geht das nicht schneller?
        # Bis zu iNumTries soll versucht werden, ein Dorf zu erstellen
        iNumTries = iMaxHuts
        for i in range(iNumTries):
            iX = myRandom(iMapW)
            iY = myRandom(iMapH)

            if iNumSetGoodies >= iMaxHuts: break

            # Terrain checken
            loopPlot = gc.getMap().plot(iX, iY)
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
                              if imp == impBarbFort: PAE_Barbaren.setFortDefence(loopPlot)

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


# New Seewind-Feature together with Elwood (ideas) and the TAC-Team (diagonal arrows)
def doSeewind():
    terr_ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
    feat_ice = gc.getInfoTypeForString("FEATURE_ICE")

    iNumDirection = 8
    lFeatWind = [
        gc.getInfoTypeForString("FEATURE_WIND_N"),
        gc.getInfoTypeForString("FEATURE_WIND_NE"),
        gc.getInfoTypeForString("FEATURE_WIND_E"),
        gc.getInfoTypeForString("FEATURE_WIND_SE"),
        gc.getInfoTypeForString("FEATURE_WIND_S"),
        gc.getInfoTypeForString("FEATURE_WIND_SW"),
        gc.getInfoTypeForString("FEATURE_WIND_W"),
        gc.getInfoTypeForString("FEATURE_WIND_NW"),
    ]

    iWindplots = 6 # amount of wind arrows (plots) per wind
    OceanPlots = []
    lDirection = []
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    # get all ocean plots
    for i in range (iMapW):
      for j in range (iMapH):
        loopPlot = gc.getMap().plot(i, j)
        if loopPlot != None and not loopPlot.isNone():
          if loopPlot.getFeatureType() == iDarkIce: continue
          if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
            OceanPlots.append(loopPlot)

    if len(OceanPlots) > 0:
        #  0 = WORLDSIZE_DUEL
        #  1 = WORLDSIZE_TINY
        #  2 = WORLDSIZE_SMALL
        #  3 = WORLDSIZE_STANDARD
        #  4 = WORLDSIZE_LARGE
        #  5 = WORLDSIZE_HUGE
     iMaxEffects = (gc.getMap().getWorldSize() + 1) * 2
     for i in range (iMaxEffects):
      # get first ocean plot
      iRand = myRandom(len(OceanPlots))
      loopPlot = OceanPlots[iRand]
      # First direction
      iDirection = myRandom(iNumDirection)

      # Start Windplots
      for j in range (iWindplots):
         if loopPlot != None and not loopPlot.isNone():
          if loopPlot.getFeatureType() == iDarkIce: continue
          if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
            loopPlot.setFeatureType(lFeatWind[iDirection],0)
            iDirection = (iDirection+myRandom(3)-1)%iNumDirection
            loopPlot = plotDirection(loopPlot.getX(), loopPlot.getY(), DirectionTypes(iDirection))


# ++++++++++++++++++ Historische Texte ++++++++++++++++++++++++++++++++++++++++++++++

def doHistory():
    iGameYear = gc.getGame().getGameTurnYear()
    txts = 0

    if iGameYear == -3480: txts = 4
    elif iGameYear == -3000: txts = 5
    elif iGameYear == -2680: txts = 4
    elif iGameYear == -2000: txts = 6
    elif iGameYear == -1680: txts = 5
    elif iGameYear == -1480: txts = 7
    elif iGameYear == -1280: txts = 5
    elif iGameYear == -1200: txts = 6
    elif iGameYear == -1000: txts = 5
    elif iGameYear == -800: txts = 6
    elif iGameYear == -750: txts = 3
    elif iGameYear == -700: txts = 6
    elif iGameYear == -615: txts = 5
    elif iGameYear == -580: txts = 5
    elif iGameYear == -540: txts = 4
    elif iGameYear == -510: txts = 5
    elif iGameYear == -490: txts = 5
    elif iGameYear == -450: txts = 4
    elif iGameYear == -400: txts = 5
    elif iGameYear == -350: txts = 7
    elif iGameYear == -330: txts = 4
    elif iGameYear == -260: txts = 3
    elif iGameYear == -230: txts = 5
    elif iGameYear == -215: txts = 4
    elif iGameYear == -200: txts = 4
    elif iGameYear == -150: txts = 5
    elif iGameYear == -120: txts = 2
    elif iGameYear == -100: txts = 2
    elif iGameYear == -70: txts = 3
    elif iGameYear == -50: txts = 2
    elif iGameYear == -30: txts = 2
    elif iGameYear == -20: txts = 2
    elif iGameYear == -10: txts = 3
    elif iGameYear == 10: txts = 3
    elif iGameYear == 60: txts = 4
    elif iGameYear == 90: txts = 3
    elif iGameYear == 130: txts = 3
    elif iGameYear == 210: txts = 3
    elif iGameYear == 250: txts = 2
    elif iGameYear == 280: txts = 2
    elif iGameYear == 370: txts = 2
    elif iGameYear == 400: txts = 2
    elif iGameYear == 440: txts = 3

    if txts > 0:
     iRand = myRandom(txts)

     # iRand 0 bedeutet keinen Text anzeigen. Bei mehr als 2 Texte immer einen einblenden
     if txts > 2: iRand += 1

     if iRand > 0:
       text = "TXT_KEY_HISTORY_"
       if iGameYear < 0:
         text = text + str(iGameYear * (-1)) + "BC_" + str(iRand)
       else:
         text = text + str(iGameYear) + "AD_" + str(iRand)

       text = CyTranslator().getText("TXT_KEY_HISTORY",("",)) + " " + CyTranslator().getText(text,("",))
       CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 15, text, None, 2, None, ColorTypes(14), 0, 0, False, False)