### Imports
import re
from CvPythonExtensions import *

import CvUtil
import PAE_City
import PAE_Lists as L
### Defines
gc = CyGlobalContext()

# PAE - InstanceChanceModifier for units in getting Fighting-Promotions (per turn)
# [PlayerID, UnitID]
PAEInstanceFightingModifier = []

def stackDoTurn(iPlayer, iGameTurn):
    pPlayer = gc.getPlayer(iPlayer)
    iTeam = pPlayer.getTeam()
    pTeam = gc.getTeam(iTeam)

    PlotArrayRebellion = []
    PlotArraySupply = []
    PlotArrayStackAI = []
    lHealerPlots = []
    lFormationPlots = []
    iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
    iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")

    # Plots herausfinden
    #if iPlayer != gc.getBARBARIAN_PLAYER():
    # iPlayer > -1: wegen einrueckung!
    # PAE Better AI:
    # HI: 20 : 40 Units
    # AI: 30 : 50 Units

    iStackLimit1 = 20
    iStackLimit2 = 40
    if not pPlayer.isHuman():
        iStackLimit1 += 20
        iStackLimit2 += 20

    (sUnit, pIter) = pPlayer.firstUnit(False)
    while sUnit:
        # tmpA: OBJECTS (tmpPlot) KANN MAN NICHT mit NOT IN in einer Liste pruefen!
        tmpA = [sUnit.getX(), sUnit.getY()]
        tmpPlot = sUnit.plot()
        if not tmpPlot.isWater():
            if sUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                if tmpA not in lHealerPlots:
                    lHealerPlots.append(tmpA)
            # PAE V: bei den Staedten gibts ne eigene funktion bei city supply
            if not tmpPlot.isCity():
                if tmpA not in PlotArraySupply:
                    # 1. Instanz - Versorgung auf Land
                    tmpAnz = tmpPlot.getNumDefenders(iPlayer)
                    if tmpAnz >= 6:
                        # AI Stack ausserhalb einer Stadt, in feindlichem Terrain
                        if not pPlayer.isHuman():
                            tmpOwner = tmpPlot.getOwner()
                            if tmpOwner != -1 and tmpOwner != iPlayer:
                                if tmpA not in PlotArrayStackAI:
                                    if pTeam.isAtWar(gc.getPlayer(tmpOwner).getTeam()):
                                        PlotArrayStackAI.append(tmpA)

                        if tmpAnz >= iStackLimit1:
                            PlotArraySupply.append(tmpA)
                            # 2. Instanz - Rebellionsgefahr auf Land
                            if tmpAnz >= iStackLimit2:
                                PlotArrayRebellion.append(tmpA)
                            # ***TEST***
                            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Stack (Zeile 3377)", tmpPlot.getNumDefenders(iPlayer))), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # PAE V - Formations ++++

        # AI Formations
        if not pPlayer.isHuman():
            if tmpPlot.getNumUnits() > 2:
                if tmpA not in lFormationPlots:
                    if not tmpPlot.isCity():
                        doAIPlotFormations(tmpPlot, iPlayer)
                    lFormationPlots.append(tmpA)
            # more than 50% damage -> go defensive
            elif sUnit.getDamage() > 50:
                doAIUnitFormations(sUnit, False, False, False)

            # Missing fort on a plot
            if sUnit.isHasPromotion(iPromoFort) or sUnit.isHasPromotion(iPromoFort2):
                iImp = tmpPlot.getImprovementType()
                if iImp > -1:
                    if gc.getImprovementInfo(iImp).getDefenseModifier() < 10 or tmpPlot.getOwner() != sUnit.getOwner():
                        doUnitFormation(sUnit, -1)
                else:
                    doUnitFormation(sUnit, -1)

        (sUnit, pIter) = pPlayer.nextUnit(pIter, False)
    # while end

    # AI Stacks vor einer gegnerischen Stadt ---------------------------------------
    for h in PlotArrayStackAI:
        pPlotEnemyCity = None
        for x in range(3):
            for y in range(3):
                loopPlot = gc.getMap().plot(h[0]-1+x, h[1]-1+y)
                if loopPlot is not None and not loopPlot.isNone():
                    iLoopPlotOwner = loopPlot.getOwner()
                    if iLoopPlotOwner != -1 and loopPlot.isCity():
                        if pTeam.isAtWar(gc.getPlayer(iLoopPlotOwner).getTeam()):
                            pPlotEnemyCity = loopPlot
                            break
            if pPlotEnemyCity is not None:
                break

        # vor den Toren der feindlichen Stadt
        if pPlotEnemyCity is not None:
            # Bombardement
            pStackPlot = gc.getMap().plot(h[0], h[1])
            iNumUnits = pStackPlot.getNumUnits()
            for i in range(iNumUnits):
                pUnit = pStackPlot.getUnit(i)
                if pUnit.getOwner() == iPlayer:
                    if pUnit.isRanged():
                        if not pUnit.isMadeAttack() and pUnit.getImmobileTimer() <= 0:
                            # getbestdefender -> getDamage
                            pBestDefender = pPlotEnemyCity.getBestDefender(-1, -1, pUnit, 1, 0, 0)
                            # Ab ca 50% Schaden aufhoeren
                            if pBestDefender.getDamage() < 55:
                                pUnit.rangeStrike(pPlotEnemyCity.getX(), pPlotEnemyCity.getY())
                            else:
                                break


    # +++++ Aufladen der Versorger UNIT_SUPPLY_WAGON ---------------------------------------
    for h in lHealerPlots:
        loopPlot = gc.getMap().plot(h[0], h[1])
        iX = h[0]
        iY = h[1]
        # Init
        lHealer = []
        iSupplyChange = 0

        # Units calc
        iRange = loopPlot.getNumUnits()
        for iUnit in range(iRange):
            pLoopUnit = loopPlot.getUnit(iUnit)
            if pLoopUnit.getOwner() == iPlayer:
                if pLoopUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                    lHealer.append(pLoopUnit)

        # Plot properties
        bDesert = loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT")

        # Inits for Supply Units (nur notwendig, wenns Versorger gibt)
        if lHealer:
            iLoopOwner = loopPlot.getOwner()
            # Eigenes Terrain
            if iLoopOwner == iPlayer:
                if loopPlot.isCity():
                    pCity = loopPlot.getPlotCity()
                    # PAE V
                    if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                        iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer)
                   # PAE IV
                   #if pCity.happyLevel() - pCity.unhappyLevel(0) == 0 or pCity.goodHealth() - pCity.badHealth(False) == 0: iSupplyChange += 25
                   #elif pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
                else:
                    eImprovement = loopPlot.getImprovementType()
                    if eImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT"):
                        iSupplyChange += 35
                    elif eImprovement == gc.getInfoTypeForString("IMPROVEMENT_FORT2"):
                        iSupplyChange += 35
                    elif eImprovement == gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"):
                        iSupplyChange += 25
                # PAE V: deaktiviert (weil Einheitengrenze sowieso vom Verbrauch abgezogen wird)
                #else: iSupplyChange += 20
            # Fremdes Terrain
            else:
                lImpFood = [
                    gc.getInfoTypeForString("IMPROVEMENT_FARM"),
                    gc.getInfoTypeForString("IMPROVEMENT_PASTURE"),
                    gc.getInfoTypeForString("IMPROVEMENT_PLANTATION"),
                    gc.getInfoTypeForString("IMPROVEMENT_BRUNNEN")
                ]
                if iLoopOwner != -1:
                    pLoopOwner = gc.getPlayer(iLoopOwner)
                    iTeamPlot = pLoopOwner.getTeam()
                    pTeamPlot = gc.getTeam(iTeamPlot)

                    # Versorger auf Vassalenterrain - Aufladechance - Stadt: 100%, Land 20%
                    if pTeamPlot.isVassal(iTeam):
                        if loopPlot.isCity():
                            pCity = loopPlot.getPlotCity()
                            # PAE V
                            if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                                iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(iLoopOwner)
                            # PAE IV
                            #if pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
                        elif CvUtil.myRandom(10, "Versorger_1") < 2:
                            iSupplyChange += 20
                        if pPlayer.isHuman():
                            CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_SUPPLY_RELOAD_1", (pLoopOwner.getCivilizationAdjective(3), 0)), None, 2, lHealer[0].getButton(), ColorTypes(8), iX, iY, True, True)

                    # Versorger auf freundlichem Terrain - Aufladechance 30%, 20% oder 10%
                    elif not pTeam.isAtWar(iTeamPlot):
                        # Attitudes
                        #-11 and lower = Gracious
                        #-1 through -10 = Polite
                        #0 = Cautious
                        #1-10 = Annoyed
                        #11 through 100 = Furious
                        iAtt = pLoopOwner.AI_getAttitude(iPlayer)
                        if iAtt < -10:
                            iChance = 3
                        elif iAtt < 0:
                            iChance = 2
                        elif iAtt == 0:
                            iChance = 1
                        else:
                            iChance = 0
                        if iChance > 0 and CvUtil.myRandom(10, "Versorger_2") < iChance:
                            if loopPlot.isCity():
                                pCity = loopPlot.getPlotCity()
                                # PAE V
                                if pCity.getYieldRate(0) - loopPlot.getNumDefenders(iPlayer) > 0:
                                    iSupplyChange += pCity.getYieldRate(0) - loopPlot.getNumDefenders(iLoopOwner)
                                # PAE IV
                                #if pCity.happyLevel() - pCity.unhappyLevel(0) > 0 and pCity.goodHealth() - pCity.badHealth(False) > 0: iSupplyChange += 50
                            else:
                                iSupplyChange += 20
                            if pPlayer.isHuman() and iSupplyChange > 0:
                                CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_SUPPLY_RELOAD_2", (pLoopOwner.getNameKey(), 0)), None, 2, lHealer[0].getButton(), ColorTypes(8), iX, iY, True, True)


                    # Versorger steht auf feindlichem Terrain
                    else:
                        # Plot wird beschlagnahmt
                        if loopPlot.getImprovementType() in lImpFood:
                            iSupplyChange += 10
                        #if loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_OASIS"): iSupplyChange += 10

                 # Neutrales Terrain
                elif loopPlot.getImprovementType() in lImpFood:
                    iSupplyChange += 10

            #if loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_OASIS"): iSupplyChange += 10

            # Fluss
            if loopPlot.isRiver():
                iSupplyChange += 10

            # ++++ Supply Units update ------------
            # 1. Aufladen
            for loopUnit in lHealer:
                if iSupplyChange <= 0:
                    break
                iSupplyChange = fillSupply(loopUnit, iSupplyChange)


    # +++++ Versorgung der Armee - supply wagon ---------------------------------------
    if PlotArraySupply:
        # gc.getInfoTypeForString("UNIT_SUPPLY_WAGON") # Tickets: 200
        # gc.getInfoTypeForString("UNIT_DRUIDE") # Tickets: 100
        # gc.getInfoTypeForString("UNIT_BRAHMANE") # Tickets: 100
        # => UNITCOMBAT_HEALER

        for h in PlotArraySupply:
            loopPlot = gc.getMap().plot(h[0], h[1])
            # Init
            iMounted = 0
            iMelee = 0
            lHealer = []
            iSupplyChange = 0
            iNumUnits = loopPlot.getNumUnits()
            # PAE V: Stack Limit mit iStackLimit1 einbeziehen
            # iHungryUnits = iNumUnits - iStackLimit1
            iHungryUnits = loopPlot.getNumDefenders(iPlayer) - iStackLimit1
            # Units calc
            for i in range(iNumUnits):
                pLoopUnit = loopPlot.getUnit(i)
                if pLoopUnit.getOwner() == iPlayer:
                    iUnitType = pLoopUnit.getUnitCombatType()
                    if iUnitType == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                        lHealer.append(pLoopUnit)
                    elif iHungryUnits > 0:
                        if iUnitType in L.LMountedSupplyCombats:
                            iMounted += 1
                            iHungryUnits -= 1
                        elif iUnitType in L.LMeleeSupplyCombats:
                            iMelee += 1
                            iHungryUnits -= 1

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("UNITCOMBAT_MELEE", iMelee)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("UNITCOMBAT_HEALER", len(lHealer))), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Plot properties
            bDesert = (loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"))

            # 1. Versorgen
            for loopUnit in lHealer:
                if iMounted <= 0 and iMelee <= 0:
                    break
                iSupplyValue = getSupply(loopUnit)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Supply Unit init "+str(loopUnit.getID()), iSupplyValue)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                if iSupplyValue > 0:
                    # Mounted Units
                    if bDesert:
                        if iSupplyValue > iMounted * 2:
                            iSupplyValue -= iMounted * 2
                            iMounted = 0
                        else:
                            iCalc = iSupplyValue / 2
                            iSupplyValue -= iCalc * 2
                            iMounted -= iCalc
                    else:
                        iSupplyValue -= iMounted
                        if iSupplyValue < 0:
                            iMounted = (-1)*iSupplyValue
                            iSupplyValue = 0
                        else:
                            iMounted = 0

                    # Melee Units
                    iSupplyValue -= iMelee
                    if iSupplyValue < 0:
                        iMelee = (-1)*iSupplyValue
                        iSupplyValue = 0
                    else:
                        iMelee = 0
                    setSupply(loopUnit, iSupplyValue)

                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",( "Supply Unit changed", iSupplyValue)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # 2. Units verletzen
            iSum = iMounted + iMelee
            if iSum > 0:
                iRange = loopPlot.getNumUnits()
                for iUnit in range(iRange):
                    if iSum <= 0:
                        break
                    xUnit = loopPlot.getUnit(iUnit)
                    if xUnit.getUnitCombatType() in L.LMountedSupplyCombats:
                        xDamage = xUnit.getDamage()
                        if xDamage + 25 < 100:
                            xUnit.changeDamage(15, False)
                            if gc.getPlayer(xUnit.getOwner()).isHuman():
                                CyInterface().addMessage(xUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_PLOT", (xUnit.getName(), 15)), None, 2, None, ColorTypes(12), loopPlot.getX(), loopPlot.getY(), True, True)
                            iSum -= 1
                    elif xUnit.getUnitCombatType() in L.LMeleeSupplyCombats:
                        xDamage = xUnit.getDamage()
                        if xDamage + 30 < 100:
                            xUnit.changeDamage(20, False)
                            if gc.getPlayer(xUnit.getOwner()).isHuman():
                                CyInterface().addMessage(xUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_PLOT", (xUnit.getName(), 20)), None, 2, None, ColorTypes(12), loopPlot.getX(), loopPlot.getY(), True, True)
                            iSum -= 1


    # +++++ Rebellious STACKs ---------------
    # Stack can become independent / rebellious
    # per Unit 0.5%, aber nur jede 3te Runde
    if PlotArrayRebellion and iGameTurn % 3 == 0:
        doStackRebellion(iPlayer, PlotArrayRebellion, iStackLimit2)

def doStackRebellion(iPlayer, PlotArrayRebellion, iStackLimit2):
    if iPlayer == -1:
        return

    pPlayer = gc.getPlayer(iPlayer)
    bAtWar = False
    iRange = gc.getMAX_PLAYERS()
    for i in range(iRange):
        if gc.getPlayer(i).isAlive():
            if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(i).getTeam()):
                bAtWar = True
                break

    iPromoLeader = gc.getInfoTypeForString('PROMOTION_LEADER')
    iPromoHero = gc.getInfoTypeForString('PROMOTION_HERO')
    # Loyale Einheiten sind dem Feldherren loyal gewesen!
    #      iPromoLoyal = gc.getInfoTypeForString('PROMOTION_LOYALITAT')

    for h in PlotArrayRebellion:
        sPlot = gc.getMap().plot(h[0], h[1])
        iNumUnits = sPlot.getNumUnits()
        iX = h[0]
        iY = h[1]
        iPlotOwner = sPlot.getOwner()

        # (Inaktiv: 30 / 5 = 4. Daher ziehe ich 5 ab, damit es bei 1% beginnt)
        #iPercent = int(iNumUnits / 2)
        iPercent = 0

        # wenn Krieg ist -20%
        if bAtWar:
            iPercent -= 20

        # for each general who accompanies the stack: -10%
        iCombatSiege = gc.getInfoTypeForString('UNITCOMBAT_SIEGE')
        iCombatUnits = 0
        for i in range(iNumUnits):
            pLoopUnit = sPlot.getUnit(i)
            if pLoopUnit.getOwner() == iPlayer:
                if pLoopUnit.isMilitaryHappiness():
                    if pLoopUnit.getUnitCombatType() != iCombatSiege:
                        iCombatUnits += 1
                if pLoopUnit.isHasPromotion(iPromoLeader):
                    iPercent -= 20
                if pLoopUnit.isHasPromotion(iPromoHero):
                    iPercent -= 10

        if iCombatUnits >= iStackLimit2:
            # PAE better AI
            if pPlayer.isHuman():
                iPercent += iCombatUnits
            else:
                iPercent += iCombatUnits / 2
        else:
            iPercent = -1

        # Loyale Einheiten sind dem Feldherren loyal gewesen!
        #if sPlot.getUnit(i).isHasPromotion(iPromoLoyal): fPercent -= 0.1
        # auf eigenem Terrain -2, auf feindlichem +2, auf neutralem 0
        #if iPlotOwner == iPlayer: iPercent -= 1
        #elif iPlotOwner != -1: iPercent += 1

        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("iPlayer", iPlayer)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Units", iNumUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("iPercent", iPercent)), None, 2, None, ColorTypes(10), 0, 0, False, False)


        if iPercent > 0:
            iBarbarianPlayer = gc.getBARBARIAN_PLAYER()
            pBarbarianPlayer = gc.getPlayer(iBarbarianPlayer)
            iRand = CvUtil.myRandom(100, "STACKs_1")
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("iRand", iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # PAE IV Update: 1. Check
            if iRand < iPercent:
                # PAE IV Update: 2. Check: 25% Rebellion, 75% Meldung
                # PAE V: 2. Check: 20% Rebellion, 80% Meldung
                iRand = CvUtil.myRandom(5, "STACKs_2")
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("2.Check", iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                # Rebellious stack
                if iRand == 1:
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("REBELLION", 1)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(10), sPlot.getX(), sPlot.getY(), True, True)

                    # Einen guenstigen Plot auswaehlen
                    rebelPlotArray = []
                    rebelPlotArrayB = []
                    for i in range(3):
                        for j in range(3):
                            loopPlot = gc.getMap().plot(sPlot.getX() + i - 1, sPlot.getY() + j - 1)
                            if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                                if loopPlot.isHills():
                                    rebelPlotArray.append(loopPlot)
                                if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                                    rebelPlotArrayB.append(loopPlot)

                    if not rebelPlotArray:
                        rebelPlotArray = rebelPlotArrayB

                    # es kann rebelliert werden
                    if rebelPlotArray:
                        iRebelPlot = CvUtil.myRandom(len(rebelPlotArray), "STACKs_3")
                        pRebelPlot = rebelPlotArray[iRebelPlot]
                        #Anzahl der rebellierenden Einheiten
                        iNumRebels = CvUtil.myRandom(iNumUnits, "STACKs_4")
                        if iNumRebels < 10:
                            iNumRebels = 9

                        # kleine Rebellion
                        if iNumRebels * 2 < iNumUnits:
                            text = CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_1", ("Units", iNumUnits))
                            if pPlayer.isHuman():
                                CyInterface().addMessage(iPlayer, True, 5, text, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), iX, iY, True, True)
                            PAE_City.doNextCityRevolt(iX, iY, iPlayer, gc.getBARBARIAN_PLAYER())

                        # grosse Rebellion (+ Generalseinheit)
                        else:
                            if pPlayer.isHuman():
                                text = CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_2", ("Units", iNumUnits))
                                CyInterface().addMessage(iPlayer, True, 5, text, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), iX, iY, True, True)

                            listNamesStandard = ["Adiantunnus", "Divico", "Albion", "Malorix", "Inguiomer", "Archelaos", "Dorimachos", "Helenos", "Kerkidas", "Mikythos", "Philopoimen", "Pnytagoras", "Sophainetos", "Theopomopos", "Gylippos", "Proxenos", "Theseus", "Balakros", "Bar Kochba", "Julian ben Sabar", "Justasas", "Patricius", "Schimon bar Giora", "Artaphernes", "Harpagos", "Atropates", "Bahram Chobin", "Datis", "Schahin", "Egnatius", "Curius Aentatus", "Antiochos II", "Spartacus", "Herodes I", "Calgacus", "Suebonius Paulinus", "Maxentus", "Sapor II", "Alatheus", "Saphrax", "Honorius", "Aetius", "Achilles", "Herodes", "Heros", "Odysseus", "Anytos"]
                            iName = CvUtil.myRandom(len(listNamesStandard), "GG_name")

                            iUnitType = gc.getInfoTypeForString("UNIT_GREAT_GENERAL")
                            unit = pBarbarianPlayer.initUnit(iUnitType, pRebelPlot.getX(), pRebelPlot.getY(), UnitAITypes.UNITAI_GENERAL, DirectionTypes.DIRECTION_SOUTH)
                            unit.setName(listNamesStandard[iName])
                            PAE_City.doNextCityRevolt(iX, iY, iPlayer, iBarbarianPlayer)
                            PAE_City.doNextCityRevolt(iX, iY, iPlayer, iBarbarianPlayer)

                        # PopUp
                        if pPlayer.isHuman():
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(text)
                            popupInfo.addPopup(iPlayer)

                        # ***TEST***
                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Stack Rebellion (Zeile 2028)", iPlayer)), None, 2, None, ColorTypes(10), sPlot.getX(), sPlot.getY(), True, True)

                        # Units become rebels
                        for i in range(iNumRebels):
                            # Zufallsunit, getnumunits muss jedesmal neu ausgerechnet werden, da ja die rebell. units auf diesem plot wegfallen
                            iRand = CvUtil.myRandom(sPlot.getNumDefenders(iPlayer), "rebels")
                            #Unit kopieren
                            pRandUnit = sPlot.getUnit(iRand)
                            if pRandUnit.getOwner() == iPlayer:
                                rebell(pRandUnit, pBarbarianPlayer, pRebelPlot)

                        # Meldung an den Spieler auf dem Territorium einer dritten Partei
                        if iPlotOwner != -1:
                            if iPlotOwner != iPlayer and gc.getPlayer(iPlotOwner).isHuman():
                                CyInterface().addMessage(iPlotOwner, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_4", (pPlayer.getCivilizationAdjective(1),)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), iX, iY, True, True)

                        # ***TEST***
                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Rebellisches Stack (Zeile 1557)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)



                # ne kleine Warnung ausschicken
                else:
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_0", ("",)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), iX, iY, True, True)
                    else:
                        # AI kills a weak unit to prevent a rebellion
                        #iST = seekUnit = seekST = 0
                        #for i in range(iNumUnits):
                        #  iST = sPlot.getUnit(i).baseCombatStr()
                        #  if iST < seekST and iST > 0 or seekST == 0:
                        #   seekUnit = i
                        #   seekST = iST
                        #pUnit = sPlot.getUnit(seekUnit)
                        ## pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                        #pUnit.kill(True, -1)  # RAMK_CTD
                        #pUnit = None

                        # AI teilt Stack (jede 4. Einheit)
                        for i in range(iNumUnits):
                            if i % 4 == 1:
                                pLoopUnit = sPlot.getUnit(i)
                                if pLoopUnit.getOwner() == iPlayer:
                                    pLoopUnit.jumpToNearestValidPlot()

                        # Meldung an den Spieler auf dem Territorium einer dritten Partei
                        if iPlotOwner != -1:
                            if iPlotOwner != iPlayer and gc.getPlayer(iPlotOwner).isHuman():
                                CyInterface().addMessage(iPlotOwner, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_STACK_REBELS_3", (pPlayer.getCivilizationAdjective(1),)), "AS2D_REBELLION", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), iX, iY, True, True)


# +++++ Rebellious Stack -- end ---------------------------------------------

# Upgrade Veteran Unit to Elite Unit - Belobigung
# CommandUpgrade geht nur, wenn
# - die Einheit auch wirklich zu dieser Einheit laut XML upgegradet werden kann
# - alle Vorraussetzungen fuer die neuen Einheit erfuellt sind
# - im eigenen Territorium
#pUnit.doCommand (CommandTypes.COMMAND_UPGRADE, gc.getInfoTypeForString("UNIT_TRIARII2"), 0)
def doUpgradeVeteran(pUnit, iNewUnit, bChangeCombatPromo):
    if not iNewUnit in range(gc.getNumUnitInfos()):
        # ***TEST***
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Upgrade Veteran: Invalid New Unit Type %d", iNewUnit)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return
    if pUnit is not None and not pUnit.isNone():
        pUnitOwner = gc.getPlayer(pUnit.getOwner())
        if pUnitOwner is not None and not pUnitOwner.isNone():
            iPromoCombat3 = gc.getInfoTypeForString("PROMOTION_COMBAT3")
            iPromoCombat4 = gc.getInfoTypeForString("PROMOTION_COMBAT4")
            iPromoCombat5 = gc.getInfoTypeForString("PROMOTION_COMBAT5")
            iPromoCombat6 = gc.getInfoTypeForString("PROMOTION_COMBAT6")

            NewUnit = pUnitOwner.initUnit(iNewUnit, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            forbiddenPromos = []
            if pUnit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH1"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH2"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_SKIRMISH3"))
            else:
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"))

            if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5"))
            elif iNewUnit == gc.getInfoTypeForString("UNIT_PRAETORIAN"):
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_RANG_ROM_1"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_RANG_ROM_2"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_RANG_ROM_3"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_RANG_ROM_4"))
                forbiddenPromos.append(gc.getInfoTypeForString("PROMOTION_RANG_ROM_5"))

            iRange = gc.getNumPromotionInfos()
            for j in range(iRange):
                if j not in forbiddenPromos:
                    if pUnit.isHasPromotion(j):
                        NewUnit.setHasPromotion(j, True)

            # Einheit: Rang -2
            if bChangeCombatPromo:
                if NewUnit.isHasPromotion(iPromoCombat6):
                    NewUnit.setHasPromotion(iPromoCombat6, False)
                    NewUnit.setHasPromotion(iPromoCombat5, False)
                elif NewUnit.isHasPromotion(iPromoCombat5):
                    NewUnit.setHasPromotion(iPromoCombat5, False)
                    NewUnit.setHasPromotion(iPromoCombat4, False)
                elif NewUnit.isHasPromotion(iPromoCombat4):
                    NewUnit.setHasPromotion(iPromoCombat4, False)
                    NewUnit.setHasPromotion(iPromoCombat3, False)

            NewUnit.setExperience(pUnit.getExperience(), -1)
            NewUnit.setLevel(pUnit.getLevel())

            copyName(NewUnit, pUnit.getUnitType(), pUnit.getName())

            # if unit was a general  (PROMOTION_LEADER)
            if pUnit.getLeaderUnitType() > -1:
                NewUnit.setLeaderUnitType(pUnit.getLeaderUnitType())
                pUnit.setLeaderUnitType(-1) # avoids ingame message "GG died in combat"

            NewUnit.setDamage(pUnit.getDamage(), -1)
            NewUnit.setImmobileTimer(1)

            # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit.kill(True, -1)  # RAMK_CTD
            pUnit = None

# Unit Rang Promos (PAE, ModMessage:751)
def doUpgradeRang(iPlayer, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pUnit = pPlayer.getUnit(iUnit)
    iUnitType = pUnit.getUnitType()
    iNewUnit = -1

    # Rome
    if iUnitType == gc.getInfoTypeForString("UNIT_LEGION"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_OPTIO")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION2"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_OPTIO2")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_OPTIO"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_CENTURIO")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_TRIBUN")
        setLegionName(pUnit)
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_TRIBUN")
        setLegionName(pUnit)
    elif iUnitType == gc.getInfoTypeForString("UNIT_EQUITES") or iUnitType == gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2"):
        iNewUnit = gc.getInfoTypeForString("UNIT_HORSEMAN_DECURIO")
    elif iUnitType == gc.getInfoTypeForString("UNIT_HORSEMAN_DECURIO"):
        iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_TRIBUN")
        setLegionName(pUnit)
    elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES"):
        iNewUnit = gc.getInfoTypeForString("UNIT_ROME_COMITATENSES2")
    elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES2"):
        iNewUnit = gc.getInfoTypeForString("UNIT_ROME_COMITATENSES3")

    if iNewUnit == -1:
        # Kelten, Germanen, Gallier, etc.
        lGermanen = [
            gc.getInfoTypeForString("CIVILIZATION_GERMANEN"),
            gc.getInfoTypeForString("CIVILIZATION_CELT"),
            gc.getInfoTypeForString("CIVILIZATION_GALLIEN"),
            gc.getInfoTypeForString("CIVILIZATION_DAKER"),
            gc.getInfoTypeForString("CIVILIZATION_BRITEN"),
            gc.getInfoTypeForString("CIVILIZATION_VANDALS")
        ]
        if pPlayer.getCivilizationType() in lGermanen:
            iNewUnit = gc.getInfoTypeForString("UNIT_STAMMESFUERST")

    # Neue Einheit
    if iNewUnit != -1:
        # ScriptData leeren
        CvUtil.removeScriptData(pUnit, "P")
        doUpgradeVeteran(pUnit, iNewUnit, False)
        if pPlayer.isHuman():
            pPlayer.changeGold(-100)
    else:
        # ***TEST***
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Upgrade by Rank: this unit should have no rank ", iUnitType)), None, 2, None, ColorTypes(10), 0, 0, False, False)



# PAE UNIT FORMATIONS ------------------------------
def canDoFormation(pUnit, iFormation):
    if not pUnit.canMove() or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")):
        return False

    iUnitType = pUnit.getUnitType()
    iUnitCombatType = pUnit.getUnitCombatType()
    pPlayer = gc.getPlayer(pUnit.getOwner())
    pTeam = gc.getTeam(pPlayer.getTeam())

    bCanDo = False
    # Naval
    if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL") or iFormation == gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_WORKBOAT"),
                    gc.getInfoTypeForString("UNIT_KILIKIEN"),
                    gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),
                    gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),
                    gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),
                    gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE")
                ]
                if iUnitType not in UnitArray:
                    bCanDo = True


    # Mounted mit Fernangriff
    elif iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
        # Fourage
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
                    gc.getInfoTypeForString("UNIT_KAMPFHUND"),
                    gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
                    gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
                    gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
                    gc.getInfoTypeForString("UNIT_BURNING_PIGS")
                ]
                if iUnitType not in UnitArray:
                    bCanDo = True

        # Partherschuss oder Kantabrischer Kreis
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER") or iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
            if iUnitType in L.LUnitPartherschuss:
                # Partherschuss
                if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                        if pUnit.getCivilizationType() in L.LCivPartherschuss:
                            bCanDo = True
                # Kantabrischer Kreis
                elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                        bCanDo = True

        # Keil (fuer schwere Kavallerie)
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                if iUnitType in L.LKeilUnits:
                    bCanDo = True

    # Melee and Spear
    elif iUnitCombatType in L.LMeleeSupplyCombats:
        # Fortress
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") and pUnit.baseMoves() == 1:
            bCanDo = True
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") and pUnit.baseMoves() > 1:
            bCanDo = True

        # Schildwall
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
                if iUnitType not in L.LSchildwallUnits:
                    bCanDo = True

        # Drill: Manipel, Phalanx, ...
        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
            # Roman Legion (Kohorte)
            if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"):
                if pUnit.getUnitType() in L.LDrillUnits:
                    bCanDo = True
            # Treffen-Taktik
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    bCanDo = True
            # Manipel
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
                    bCanDo = True
            # Phalanx-Arten (nur Speer)
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                        bCanDo = True
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                        bCanDo = True
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                        bCanDo = True
            # Geschlossene Formation (alle Melee)
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
                    bCanDo = True
            # Testudo
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                    if pUnit.getUnitType() in L.LTestsudoUnits:
                        bCanDo = True
        # -- Drill end

        # Keil
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                bCanDo = True
        # Zangenangriff
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
                bCanDo = True
        # Flankenschutz (nur Speer)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"):
            if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    bCanDo = True
        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                bCanDo = True

    # Archers
    elif iUnitCombatType in L.LArcherCombats:
        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                bCanDo = True

    # Flucht
    if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"):
        if pUnit.getDamage() >= 70:
            if iUnitCombatType in L.LFluchtCombats:
                if pUnit.baseMoves() == 1:
                    bCanDo = True

    return bCanDo
  # can do Formationen / Formations End ------

# PAE UNIT FORMATIONS ------------------------------
def doUnitFormation(pUnit, iNewFormation):
    pPlayer = gc.getPlayer(pUnit.getOwner())

    # Human
    if pPlayer.isHuman():
        # Fuer alle Einheiten dieser Gruppe
        pPlot = pUnit.plot()

        iNumUnits = pPlot.getNumUnits()
        for i in range(iNumUnits):
            loopUnit = pPlot.getUnit(i)
            if loopUnit.IsSelected():
                # Formation geben
                if iNewFormation != -1:
                    if canDoFormation(loopUnit, iNewFormation):
                        # Formationen auf NULL setzen
                        for j in L.LFormationen:
                            #if loopUnit.isHasPromotion(j):
                            loopUnit.setHasPromotion(j, False)
                        # Formation geben
                        loopUnit.setHasPromotion(iNewFormation, True)
                # Formationen entfernen
                else:
                    # Formationen auf NULL setzen
                    for j in L.LFormationen:
                        #if loopUnit.isHasPromotion(j):
                        loopUnit.setHasPromotion(j, False)
    # AI
    else:
        # Formationen auf NULL setzen
        for j in L.LFormationen:
            #if loopUnit.isHasPromotion(j):
            pUnit.setHasPromotion(j, False)
        # Formation geben
        if iNewFormation != -1:
            pUnit.setHasPromotion(iNewFormation, True)

def doAIPlotFormations(pPlot, iPlayer):
    # bContinue = False
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    bSupplyUnit = False
    bCity = False
    bElefant = False
    lPlayerUnits = []
    lMountedUnits = []
    iCountDamage = 0
    iStackStatus = 0
    # 0: > 75% stength: 80% offensive
    # 1: > 50% strength: 50% offensive
    # 2: > 25% strength: 10% offensive
    # 3: < 25% strength: flight

    # Naval or Land
    if pPlot.isWater():
        if not pTeam.isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
            return
    elif not pTeam.isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
        return

    # City
    iRange = 1
    iX = pPlot.getX()
    iY = pPlot.getY()
    for x in range(-iRange, iRange+1):
        for y in range(-iRange, iRange+1):
            loopPlot = plotXY(iX, iY, x, y)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.isCity():
                    pCity = loopPlot.getPlotCity()
                    if pCity.getOwner() != iPlayer:
                        if pTeam.isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
                            bCity = True

    lUnitTypes = [
        #gc.getInfoTypeForString("UNITCOMBAT_MELEE"),
        gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"),
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
        gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"),
        gc.getInfoTypeForString("UNITCOMBAT_NAVAL")
    ]
    # Init Units
    iRange = pPlot.getNumUnits()
    for i in range(iRange):
        if pPlot.getUnit(i).getOwner() == iPlayer:
            if pPlot.getUnit(i).getUnitCombatType() in lUnitTypes:
                lPlayerUnits.append(pPlot.getUnit(i))
                # Supply
                if not bSupplyUnit:
                    if pPlot.getUnit(i).isHasPromotion(gc.getInfoTypeForString("PROMOTION_MEDIC2")):
                        bSupplyUnit = True
                iCountDamage += pPlot.getUnit(i).getDamage()

    # StackStatus
    iCountUnits = len(lPlayerUnits)
    iLimit = 0
    if iCountUnits > 0:
        if iCountUnits * 100 - iCountDamage > iCountUnits * 75:
            iStackStatus = 0
            iLimit = iCountUnits / 10 * 8
        elif iCountUnits * 100 - iCountDamage > iCountUnits * 50:
            iStackStatus = 1
            iLimit = iCountUnits / 2
        elif iCountUnits * 100 - iCountDamage > iCountUnits * 25:
            iStackStatus = 2
            iLimit = iCountUnits / 10
        else:
            iStackStatus = 3

        if iStackStatus == 3:
            for unit in lPlayerUnits:
                if unit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                    doUnitFormation(unit, gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"))
        else:
            i = 0
            for unit in lPlayerUnits:
                if not bSupplyUnit:
                    if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                        UnitArray = [
                            gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
                            gc.getInfoTypeForString("UNIT_KAMPFHUND"),
                            gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
                            gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
                            gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
                            gc.getInfoTypeForString("UNIT_BURNING_PIGS")
                        ]
                        if unit.getUnitType() not in UnitArray:
                            lMountedUnits.append(unit)
                if i <= iLimit:
                    doAIUnitFormations(unit, True, bCity, bElefant)
                else:
                    doAIUnitFormations(unit, False, bCity, bElefant)
                i += 1

            # Fourage - Supply
            if not bSupplyUnit:
                if lMountedUnits:
                    iLevel = 10
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
                        pUnit = lMountedUnits[0]
                        for unit in lMountedUnits:
                            if unit.getLevel() < iLevel:
                                pUnit = unit
                                iLevel = unit.getLevel()
                        doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))


def doAIUnitFormations(pUnit, bOffensive, bCity, bElefant):
    if (pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY"))
            or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"))
            or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"))):
        return
    if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pUnit.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:
        return

    lFormations = []
    # Naval
    if bOffensive:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))
    else:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))
    # Mounted
    lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
    lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
    if bOffensive:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))
    # Melee
    if bCity and CvUtil.myRandom(2, "Testudo") == 0:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))
    lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))
    # Elefantengasse
    if bElefant and (pUnit.getUnitCombatType() in L.LArcherCombats or CvUtil.myRandom(4, "Elefantengasse") == 0):
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
    if bOffensive:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))
        # Schiefe Schlachtordnung
        if CvUtil.myRandom(2, "Schiefe Schlachtordnung") == 0:
            lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))
        # Manipular-Phalanx
        else:
            lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))
        # Phalanx
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))
        # Geschlossene Formation (alle Melee mit Drill)
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))
    # Defensive
    else:
        # Flankenschutz (nur Speer)
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))
        # Zangenangriff (dem Keil vorziehen)
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))
    lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
    # Archer, vor allem Skirmisher
    if bElefant:
        lFormations.append(gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
    for iFormation in lFormations:
        if canDoFormation(pUnit, iFormation):
            doUnitFormation(pUnit, iFormation)
            return
  # PAE UNIT FORMATIONS END ------------------------------


# PAE UNIT BATTLE PROMOTION
def doUnitGetsPromo(pUnitTarget, pUnitSource, pPlot, bMadeAttack):
    # Unit promos --------------------
    # UNITCOMBAT_ARCHER: PROMOTION_COVER1
    # UNITCOMBAT_SKIRMISHER: PROMOTION_PARADE_SKIRM1
    # UNITCOMBAT_AXEMAN: PROMOTION_PARADE_AXE1
    # UNITCOMBAT_SWORDSMAN: PROMOTION_PARADE_SWORD1
    # UNITCOMBAT_SPEARMAN: PROMOTION_PARADE_SPEAR1

    # UNITCOMBAT_CHARIOT: PROMOTION_FORMATION1
    # UNITCOMBAT_MOUNTED: PROMOTION_FORMATION2
    # UNITCOMBAT_ELEPHANT: PROMOTION_FORMATION3
    # UNITCOMBAT_SIEGE: PROMOTION_CHARGE
    # Terrain promos -----------------
    # isHills: PROMOTION_GUERILLA1 - 5
    # FEATURE_FOREST, FEATURE_DICHTERWALD: PROMOTION_WOODSMAN1 - 5
    # FEATURE_JUNGLE: PROMOTION_JUNGLE1 - 5
    # TERRAIN_SWAMP: PROMOTION_SUMPF1 - 5
    # TERRAIN_DESERT: PROMOTION_DESERT1 - 5
    # Extra promos -------------------
    # City Attack: PROMOTION_CITY_RAIDER1 - 5
    # City Defense: PROMOTION_CITY_GARRISON1 - 5
    # isRiverSide(): PROMOTION_AMPHIBIOUS

    # pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT")
    # pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST")
    # pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MELEE")

    iNewPromo = -1
    iPlayer = pUnitTarget.getOwner()
    pPlayer = gc.getPlayer(iPlayer)

    bCity = pPlot.isCity()

    lFirstPromos = [
        gc.getInfoTypeForString("PROMOTION_WOODSMAN1"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA1"),
        gc.getInfoTypeForString("PROMOTION_DESERT1"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE1"),
        gc.getInfoTypeForString("PROMOTION_SUMPF1"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
    ]
    iFirstPromos = 0
    for i in lFirstPromos:
        if pUnitTarget.isHasPromotion(i):
            iFirstPromos += 1

    iDivisor = 1
    # PAEInstanceFightingModifier for wins in the same turn
    if (iPlayer, pUnitTarget.getID()) in PAEInstanceFightingModifier:
        iDivisor = 5

    # Chances
    iChanceCityAttack = 20 / iDivisor
    iChanceCityDefense = 20 / iDivisor
    # Trait Conqueror / Eroberer: iChanceCityAttack*2
    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")):
        iChanceCityAttack *= 2
    iChanceUnitType = 10 / iDivisor
    iChanceTerrain = 30 / (iFirstPromos*2 + 1) / iDivisor
    # Static chance of Promo 2-5 of a terrain
    iChanceTerrain2 = 5 / iDivisor


    # 1. chance: Either City or Open Field
    # City
    if bCity:
        iRand = CvUtil.myRandom(100, "cityPromo")
        if iChanceCityDefense > iRand:
            if bMadeAttack:
            # Attacker
                if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")):
                    lCityRaider = [
                        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"),
                        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2"),
                        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3"),
                        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4"),
                        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")
                    ]
                    for iPromo in lCityRaider:
                        if not pUnitTarget.isHasPromotion(iPromo):
                            iNewPromo = iPromo
                            break
                    iChanceUnitType = iChanceUnitType / 2
                    # Trait Conquereror / Eroberer: Automatische Heilung bei Stadtangriffs-Promo / auto-healing when receiving city raider promo
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")):
                        pUnitTarget.setDamage(0, -1)
            # Defender
            else:
                if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")):
                    lCityGarrison = [
                        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"),
                        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2"),
                        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3"),
                        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4"),
                        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")
                    ]
                    for iPromo in lCityGarrison:
                        if not pUnitTarget.isHasPromotion(iPromo):
                            iNewPromo = iPromo
                            break
                    iChanceUnitType = iChanceUnitType / 2
                    # Trait Protective: Automatische Heilung bei Stadtverteidigungs-Promo / auto-healing when receiving city garrison promo
                    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
                        pUnitTarget.setDamage(0, -1)

    # on open field
    else:
        iRandTerrain = CvUtil.myRandom(100, "fieldPromo")
        if iChanceTerrain > iRandTerrain:
            # either hill, terrain or feature, river
            # init unit promos and terrains
            lTerrain = []
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA5")) and pPlot.isHills():
                lTerrain.append("Hills")

            # thx to Dertuek:
            if bMadeAttack and pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
                if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")):
                    pPlotAttack = pUnitTarget.plot()
                    pPlotDefense = pUnitSource.plot()
                    if pPlotAttack.isWater() and not pPlotDefense.isWater():
                        lTerrain.append("River")
                    elif pPlotAttack.isRiverSide():
                        if pPlotAttack.isRiverCrossing(directionXYFromPlot(pPlotAttack, pPlotDefense)):
                            lTerrain.append("River")

            # old source code
            #if pPlot.isRiverSide() and bMadeAttack:
            #  if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")):
            #    if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
            #      lTerrain.append("River")

            if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"):
                if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT5")):
                    lTerrain.append("Desert")

            # Forest, Jungle and Swamp nicht fuer Mounted
            if (not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT")
                    and not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")
                    and not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT")
                    and not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE")):
                if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST") or pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
                    if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN5")):
                        lTerrain.append("Forest")
                elif pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                    if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE5")):
                        lTerrain.append("Jungle")
                elif pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_SWAMP"):
                    if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF5")):
                        lTerrain.append("Swamp")

            if lTerrain:
                iChanceUnitType = iChanceUnitType / 2
                iRand = CvUtil.myRandom(len(lTerrain), "terrainPromo")
                lPromos = []
                if lTerrain[iRand] == "River":
                    iNewPromo = gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")
                else:
                    if lTerrain[iRand] == "Hills":
                        lPromos = [
                            gc.getInfoTypeForString("PROMOTION_GUERILLA1"),
                            gc.getInfoTypeForString("PROMOTION_GUERILLA2"),
                            gc.getInfoTypeForString("PROMOTION_GUERILLA3"),
                            gc.getInfoTypeForString("PROMOTION_GUERILLA4"),
                            gc.getInfoTypeForString("PROMOTION_GUERILLA5")
                        ]
                    elif lTerrain[iRand] == "Forest":
                        lPromos = [
                            gc.getInfoTypeForString("PROMOTION_WOODSMAN1"),
                            gc.getInfoTypeForString("PROMOTION_WOODSMAN2"),
                            gc.getInfoTypeForString("PROMOTION_WOODSMAN3"),
                            gc.getInfoTypeForString("PROMOTION_WOODSMAN4"),
                            gc.getInfoTypeForString("PROMOTION_WOODSMAN5")
                        ]
                    elif lTerrain[iRand] == "Jungle":
                        lPromos = [
                            gc.getInfoTypeForString("PROMOTION_JUNGLE1"),
                            gc.getInfoTypeForString("PROMOTION_JUNGLE2"),
                            gc.getInfoTypeForString("PROMOTION_JUNGLE3"),
                            gc.getInfoTypeForString("PROMOTION_JUNGLE4"),
                            gc.getInfoTypeForString("PROMOTION_JUNGLE5")
                        ]
                    elif lTerrain[iRand] == "Swamp":
                        lPromos = [
                            gc.getInfoTypeForString("PROMOTION_SUMPF1"),
                            gc.getInfoTypeForString("PROMOTION_SUMPF2"),
                            gc.getInfoTypeForString("PROMOTION_SUMPF3"),
                            gc.getInfoTypeForString("PROMOTION_SUMPF4"),
                            gc.getInfoTypeForString("PROMOTION_SUMPF5")
                        ]
                    elif lTerrain[iRand] == "Desert":
                        lPromos = [
                            gc.getInfoTypeForString("PROMOTION_DESERT1"),
                            gc.getInfoTypeForString("PROMOTION_DESERT2"),
                            gc.getInfoTypeForString("PROMOTION_DESERT3"),
                            gc.getInfoTypeForString("PROMOTION_DESERT4"),
                            gc.getInfoTypeForString("PROMOTION_DESERT5")
                        ]

                    for iPromo in lPromos:
                        if not pUnitTarget.isHasPromotion(iPromo):
                            iNewPromo = iPromo
                            break

                # Chances of Promos 2-5
                if iNewPromo not in lFirstPromos and iRandTerrain >= iChanceTerrain2:
                    iNewPromo = -1

    if iNewPromo != -1:
        # naechste Chance verringern
        iChanceUnitType = iChanceUnitType / 2
        pUnitTarget.setHasPromotion(iNewPromo, True)
        PAEInstanceFightingModifier.append((pUnitTarget.getOwner(), pUnitTarget.getID()))
        if gc.getPlayer(pUnitTarget.getOwner()).isHuman():
            CyInterface().addMessage(pUnitTarget.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION", (pUnitTarget.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)

    # 2. chance: enemy combat type
    iNewPromo = -1
    iRand = CvUtil.myRandom(100, "combatTypePromo")
    if iChanceUnitType > iRand:
        if pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
            if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER2")
            elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER1")

        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"):
            if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")
            elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")

        #elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MELEE"):
        #  if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK2")):  iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK2")
        #  elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK")

        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"):
            if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")
            elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")

        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"):
            if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")
            elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")

        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
            if pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")
            elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")

        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION1")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION1")
        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION2")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION2")
        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION3")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION3")
        elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CHARGE")):
                iNewPromo = gc.getInfoTypeForString("PROMOTION_CHARGE")

        if iNewPromo > -1:
            pUnitTarget.setHasPromotion(iNewPromo, True)
            PAEInstanceFightingModifier.append((iPlayer, pUnitTarget.getID()))
            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION", (pUnitTarget.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)

def doRetireVeteran(pUnit):
    lPromos = [
        gc.getInfoTypeForString("PROMOTION_COMBAT3"),
        gc.getInfoTypeForString("PROMOTION_COMBAT4"),
        gc.getInfoTypeForString("PROMOTION_COMBAT5"),
        gc.getInfoTypeForString("PROMOTION_COMBAT6"),
        gc.getInfoTypeForString("PROMOTION_MORAL_NEG1"),
        gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"),
        gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"),
        gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"),
        gc.getInfoTypeForString("PROMOTION_MORAL_NEG5")
    ]
    # lPromos.append(gc.getInfoTypeForString("PROMOTION_HERO"))
    for iPromo in lPromos:
        if pUnit.isHasPromotion(iPromo):
            pUnit.setHasPromotion(iPromo, False)

    # Reduce XP
    pUnit.setExperience(pUnit.getExperience() / 2, -1)
    # Reduce Lvl: deactivated
    #if pUnit.getLevel() > 3:
    #  pUnit.setLevel(pUnit.getLevel() - 3)
    #else:
    #  pUnit.setLevel(1)

def convertToPirate(city, unit):
    """unused due to possible OOS with to many pirates"""
    iPlayer = city.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iUnitType = unit.getUnitType()
    if CvUtil.myRandom(4, "PiratenbauKI") == 1:
        if gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PIRACY")):
            lPirates = {
                gc.getInfoTypeForString("UNIT_KONTERE"): gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),
                gc.getInfoTypeForString("UNIT_BIREME"): gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),
                gc.getInfoTypeForString("UNIT_TRIREME"): gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),
                gc.getInfoTypeForString("UNIT_LIBURNE"): gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE")
            }
            try:
                iNewUnitType = lPirates[iUnitType]
                # unit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                unit.kill(True, -1)  # RAMK_CTD
                unit = pPlayer.initUnit(iNewUnitType, city.getX(), city.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            except KeyError:
                pass


def doMobiliseFortifiedArmy(pCity):
    """PAE V ab Patch 3: Wenn Hauptstadt angegriffen wird, sollen alle Einheiten in Festungen remobilisiert werden (Promo FORTRESS)"""
    pPlayer = gc.getPlayer(pCity.getOwner())
    if pCity is not None:
        iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
        iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
        (pUnit, pIter) = pPlayer.firstUnit(False)
        while pUnit:
            pUnit.setHasPromotion(iPromoFort, False)
            pUnit.setHasPromotion(iPromoFort2, False)
            (pUnit, pIter) = pPlayer.nextUnit(pIter, False)

# Handelsposten errichten
def doBuildHandelsposten(pUnit):
    iPrice = 30
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if pPlayer.getGold() < iPrice:
        # TODO: eigener Text
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS", ("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
        return
    pPlot = pUnit.plot()
    pPlot.setRouteType(0)
    pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"))
    CvUtil.addScriptData(pPlot, "p", iPlayer)
    pPlot.setCulture(iPlayer, 1, True)
    pPlot.setOwner(iPlayer)
    pPlayer.changeGold(-iPrice)
    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
    pUnit.kill(True, -1)  # RAMK_CTD
    pUnit = None

# isHills: PROMOTION_GUERILLA1
# FEATURE_FOREST, FEATURE_DICHTERWALD: PROMOTION_WOODSMAN1
# FEATURE_JUNGLE: PROMOTION_JUNGLE1
# TERRAIN_SWAMP: PROMOTION_SUMPF1
# TERRAIN_DESERT: PROMOTION_DESERT1
# City Attack: PROMOTION_CITY_RAIDER1
# City Defense: PROMOTION_CITY_GARRISON1
# isRiverSide: PROMOTION_AMPHIBIOUS

# PAE CITY builds UNIT -> auto promotions (land units)
def doCityUnitPromotions(pCity, pUnit):
    initChanceCity = 1  # ab Stadt: Chance * City Pop
    initChance = 3      # Chance * Plots
    #initChanceRiver = 2 # for PROMOTION_AMPHIBIOUS only
    # --------------
    # iCityAttack = 0
    # iCityDefense = 0
    iHills = 0
    iForest = 0
    iJungle = 0
    iSwamp = 0
    iDesert = 0
    # iRiver = 0

    if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")):
        if pCity.getPopulation() * initChanceCity > CvUtil.myRandom(100, "doCityUnitPromotions1"):
            if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
                iPromoGarrison = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
                if not pUnit.isHasPromotion(iPromoGarrison):
                    doGiveUnitPromo(pUnit, iPromoGarrison, pCity)
            elif pUnit.getUnitCombatType() in [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"), gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN")]:
                iPromoRaider = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
                if not pUnit.isHasPromotion(iPromoRaider):
                    doGiveUnitPromo(pUnit, iPromoRaider, pCity)

    # not for rams
    lRams = [
        gc.getInfoTypeForString("UNIT_RAM"),
        gc.getInfoTypeForString("UNIT_BATTERING_RAM"),
        gc.getInfoTypeForString("UNIT_BATTERING_RAM2")
    ]
    if pUnit.getUnitType() in lRams:
        return

    # Start seeking plots for promos
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            if pLoopPlot.isHills() or pLoopPlot.isPeak():
                iHills += 1
            #if pLoopPlot.isRiverSide():
                # iRiver += 1
            if pLoopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"):
                iDesert += 1
            elif pLoopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_SWAMP"):
                iSwamp += 1
            if pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
                iForest += 1
            elif pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
                iForest += 1
            elif pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                iJungle += 1

    # River - deactivated
    #if iRiver > 0:
    #  iRand = CvUtil.myRandom(100, "doCityUnitPromotions2")
    #  if iRiver * initChanceRiver > iRand:
    #    if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")): doGiveUnitPromo(pUnit, gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS"), pCity)

    # PAE V Patch 7: nur 1 Terrain Promo soll vergeben werden
    lPossiblePromos = []

    # Hills
    iPromoHills = gc.getInfoTypeForString("PROMOTION_GUERILLA1")
    if iHills and iHills * initChance > CvUtil.myRandom(100, "doCityUnitPromotions3"):
        if not pUnit.isHasPromotion(iPromoHills):
            lPossiblePromos.append(iPromoHills)

    # Desert
    iPromoDesert = gc.getInfoTypeForString("PROMOTION_DESERT1")
    if iDesert and iDesert * initChance > CvUtil.myRandom(100, "doCityUnitPromotions4"):
        if not pUnit.isHasPromotion(iPromoDesert):
            lPossiblePromos.append(iPromoDesert)

    # Forest
    iPromoForest = gc.getInfoTypeForString("PROMOTION_WOODSMAN1")
    if iForest and iForest * initChance > CvUtil.myRandom(100, "doCityUnitPromotions5"):
        if not pUnit.isHasPromotion(iPromoForest):
            lPossiblePromos.append(iPromoForest)

    # Swamp
    iPromoSumpf = gc.getInfoTypeForString("PROMOTION_SUMPF1")
    if iSwamp and iSwamp * initChance > CvUtil.myRandom(100, "doCityUnitPromotions6"):
        if not pUnit.isHasPromotion(iPromoSumpf):
            lPossiblePromos.append(iPromoSumpf)

    # Jungle
    iPromoJungle = gc.getInfoTypeForString("PROMOTION_JUNGLE1")
    if iJungle and iJungle * initChance > CvUtil.myRandom(100, "doCityUnitPromotions7"):
        if not pUnit.isHasPromotion(iPromoJungle):
            lPossiblePromos.append(iPromoJungle)

    # only 1 of the pot
    if lPossiblePromos:
        iPromo = lPossiblePromos[CvUtil.myRandom(len(lPossiblePromos), "doCityUnitPromotions8")]
        doGiveUnitPromo(pUnit, iPromo, pCity)


  # PAE CITY builds UNIT -> auto promotions (ships)
def doCityUnitPromotions4Ships(pCity, pUnit):
    initChance = 2
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iWater = 0
    # Start seeking plots for promos
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            if pLoopPlot.getFeatureType() == iDarkIce:
                continue
            if pLoopPlot.isWater():
                iWater += 1

    if iWater > 3:
        iRand = CvUtil.myRandom(10, "doCityUnitPromotions4Ships")
        if iWater * initChance > iRand:
            iPromo = gc.getInfoTypeForString("PROMOTION_NAVIGATION1")
            if not pUnit.isHasPromotion(iPromo):
                doGiveUnitPromo(pUnit, iPromo, pCity)


def doGiveUnitPromo(pUnit, iNewPromo, pCity):
    pUnit.setHasPromotion(iNewPromo, True)
    iPlayer = pUnit.getOwner()
    if gc.getPlayer(iPlayer).isHuman():
        if iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1") or iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"):
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_3", (pUnit.getName(), gc.getPromotionInfo(iNewPromo).getDescription(), pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
        else:
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_2", (pUnit.getName(), gc.getPromotionInfo(iNewPromo).getDescription(), pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)

# ++++++++ Names for Legions +++++++++++++++++
# Reusing names of fallen Legions
def setLegionName(pUnit):
    pPlayer = gc.getPlayer(pUnit.getOwner())

    LegioUsedNames = []
    (loopUnit, pIter) = pPlayer.firstUnit(False)
    while loopUnit:
        sName = loopUnit.getName()
        if "Legio" in sName:
            LegioUsedNames.append(re.sub(r" \(.*?\)", "", sName))
        (loopUnit, pIter) = pPlayer.nextUnit(pIter, False)

    for sName in L.LegioNames:
        if sName not in LegioUsedNames:
            pUnit.setName(sName)
            break

def doBlessUnits(iX, iY, iOwner):
    pPlot = gc.getMap().plot(iX, iY)
    pPlayer = gc.getPlayer(iOwner)
    iPromo = gc.getInfoTypeForString("PROMOTION_BLESSED")
    iCost = 100

    iNumUnits = pPlot.getNumUnits()
    for i in range(iNumUnits):
        if pPlayer.getGold() < iCost:
            break
        loopUnit = pPlot.getUnit(i)
        if loopUnit.IsSelected():
            if not loopUnit.isHasPromotion(iPromo):
                # Gold abziehen
                pPlayer.changeGold(-iCost)
                # Formation geben
                loopUnit.setHasPromotion(iPromo, True)
                loopUnit.finishMoves()


def doUnitGetsHero(pWinner, pLoser):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
    pWinner.setExperience(pWinner.getExperience()+3, -1)
    if not pWinner.isHasPromotion(iPromoHero):
        pWinner.setHasPromotion(iPromoHero, True)
        if pWinnerPlayer.isHuman():
            if pLoser.isHasPromotion(iPromoLeader):
                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_3", (pWinner.getName(), pLoser.getName()))
                CyInterface().addMessage(iWinnerPlayer, True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
            else:
                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_4", (pWinner.getName(), 0))
                CyInterface().addMessage(iWinnerPlayer, True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
        return True
    return False

def getExperienceForLeader(pWinner, pLoser, bPromoHero):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
    bLeaderAnwesend = False
    pWinnerPlot = pWinner.plot()
    iNumUnits = pWinnerPlot.getNumUnits()
    for i in range(iNumUnits):
        pLoopUnit = pWinnerPlot.getUnit(i)
        if pLoopUnit.getOwner() == iWinnerPlayer:
            if pLoopUnit.isHasPromotion(iPromoLeader):
                bLeaderAnwesend = True
                # XP
                if CvUtil.myRandom(10, "XP") == 0:
                    pLoopUnit.setExperience(pLoopUnit.getExperience() + 1, -1)
                # First general in stack who doesnt possess hero promo gets it
                if bPromoHero:
                    if not pLoopUnit.isHasPromotion(iPromoHero):
                        pLoopUnit.setHasPromotion(iPromoHero, True)
                        bPromoHero = False
                        if pWinnerPlayer.isHuman():
                            if pLoser.isHasPromotion(iPromoLeader):
                                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_1", (pLoopUnit.getName(), pLoser.getName()))
                                CyInterface().addMessage(iWinnerPlayer, True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pLoopUnit.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
                            else:
                                txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_2", (pLoopUnit.getName(), 0))
                                CyInterface().addMessage(iWinnerPlayer, True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pLoopUnit.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)
    return bLeaderAnwesend


def removeMercenaryPromo(pWinner):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
    if pWinner.isHasPromotion(iPromoMercenary):
        if CvUtil.myRandom(20, "PROMOTION_MERCENARY") == 0:
            pWinner.setHasPromotion(iPromoMercenary, False)
            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_6", (pWinner.getName(),)), "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)

def doHunterHero(pWinner, pLoser):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    if gc.getUnitInfo(pWinner.getUnitType()).getCombat() < gc.getUnitInfo(pLoser.getUnitType()).getCombat():
        if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 4:
            if pLoser.isDead():
                if not pWinner.isHasPromotion(iPromoHero):
                    pWinner.setHasPromotion(iPromoHero, True)
                    pWinner.changeExperience(3, -1, 1, 0, 0)
                    if pWinnerPlayer.isHuman():
                        txtPopUpHero = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_HERO_5", (pWinner.getName(), pLoser.getName()))
                        CyInterface().addMessage(iWinnerPlayer, True, 10, txtPopUpHero, "AS2D_WELOVEKING", 2, pWinner.getButton(), ColorTypes(8), pWinner.getX(), pWinner.getY(), True, True)

                        popupInfo = CyPopupInfo()
                        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)  # Text PopUp only!
                        popupInfo.setText(txtPopUpHero)
                        popupInfo.addPopup(iWinnerPlayer)


def doRankPromo(pWinner):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    # ROM Pedes
    if pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_1")):
        if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_20")):
            iNumPromos = gc.getNumPromotionInfos()-1
            iPromo = iNumPromos
            iNewPromo = -1  # Fuer Pylint. Wert ueberschrieben bevor benutzt
            for iPromo in xrange(iNumPromos, 0, -1):
                iPromoType = gc.getPromotionInfo(iPromo).getType()
                if "_TRAIT_" in iPromoType:
                    break
                if "_RANG_ROM_LATE" in iPromoType:
                    continue
                if "_RANG_ROM_EQUES" in iPromoType:
                    continue
                if "_RANG_ROM_" in iPromoType:
                    if pWinner.isHasPromotion(iPromo) and iNewPromo != -1:
                        if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_5") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_9") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_14"):
                            # Auxiliar nur bis Promo V
                            if pWinner.getUnitType() != gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"):
                                CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                        else:
                            # Generaele: 20% Chance
                            if pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_14")):
                                iRand = CvUtil.myRandom(5, "RangGeneral")
                            # Offiziere: 33% Chance
                            elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_9")):
                                iRand = CvUtil.myRandom(3, "RangOffizier")
                            # Unteroffiziere: 50% Chance
                            elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_5")):
                                iRand = CvUtil.myRandom(2, "RangUnteroffizier")
                            else:
                                iRand = 1

                            if iRand == 1:
                                pWinner.setHasPromotion(iNewPromo, True)
                                # Der Kommandant Eurer Einheit (%s1) hat nun den Rang: %s2!
                                if pWinnerPlayer.isHuman():
                                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG", (pWinner.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                        break
                    else:
                        iNewPromo = iPromo
    # ROM Eques
    elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_1")):
        if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_5")):
            # Chance: 1:4
            if CvUtil.myRandom(4, "RangEques") == 1:
                iNumPromos = gc.getNumPromotionInfos() - 1
                for iPromo in xrange(iNumPromos, -1, -1): #-1 als zweites Argument, damit es bis 0 runterzaehlt.
                    iPromoType = gc.getPromotionInfo(iPromo).getType()
                    if "_TRAIT_" in iPromoType:
                        break
                    if "_RANG_ROM_EQUES" in iPromoType:
                        if pWinner.isHasPromotion(iPromo):
                            if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_EQUES_3"):
                                CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                            else:
                                pWinner.setHasPromotion(iNewPromo, True)
                                # Der Kommandant Eurer Einheit (%s1) hat nun den Rang: %s2!
                                if pWinnerPlayer.isHuman():
                                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG", (pWinner.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                            break

                        else:
                            iNewPromo = iPromo
    # ROM Late Antike
    elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_1")):
        if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_15")):
            iNumPromos = gc.getNumPromotionInfos()-1
            iPromo = iNumPromos
            for iPromo in xrange(iNumPromos, 0, -1):
                iPromoType = gc.getPromotionInfo(iPromo).getType()
                if "_TRAIT_" in iPromoType:
                    break
                if "_RANG_ROM_LATE" in iPromoType:
                    if pWinner.isHasPromotion(iPromo):
                        if iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_5") or iPromo == gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_10"):
                            CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
                        else:
                            # Offiziere: 20% Chance
                            if pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_10")):
                                iRand = CvUtil.myRandom(5, "RangLate10")
                            # Unteroffiziere: 33% Chance
                            elif pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_LATE_5")):
                                iRand = CvUtil.myRandom(3, "RangLate5")
                            else:
                                iRand = 1

                            if iRand == 1:
                                pWinner.setHasPromotion(iNewPromo, True)
                                # Der Kommandant Eurer Einheit (%s1) hat nun den Rang eines %s2!
                                if pWinnerPlayer.isHuman():
                                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG", (pWinner.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
                        break

                    else:
                        iNewPromo = iPromo

    # Ab Kriegerethos
    if gc.getTeam(pWinnerPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_KRIEGERETHOS")):
        # Kelten, Germanen, Gallier, etc.
        lGermanen = [
            gc.getInfoTypeForString("CIVILIZATION_GERMANEN"),
            gc.getInfoTypeForString("CIVILIZATION_CELT"),
            gc.getInfoTypeForString("CIVILIZATION_GALLIEN"),
            gc.getInfoTypeForString("CIVILIZATION_DAKER"),
            gc.getInfoTypeForString("CIVILIZATION_BRITEN"),
            gc.getInfoTypeForString("CIVILIZATION_VANDALS")
        ]
        if pWinnerPlayer.getCivilizationType() in lGermanen:
            if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_GER3")):
                iRand = CvUtil.myRandom(10, "PROMOTION_RANG_GER3")
                if iRand == 1:
                    iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER1")
                    if pWinner.isHasPromotion(iNewPromo):
                        iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER2")
                    if pWinner.isHasPromotion(iNewPromo):
                        iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_GER3")
                    pWinner.setHasPromotion(iNewPromo, True)
                    if pWinnerPlayer.isHuman():
                        CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG", (pWinner.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)
            else:
                CvUtil.addScriptData(pWinner, "P", "RangPromoUp")
        # Hunnen
        if pWinnerPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HUNNEN"):
            if not pWinner.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_HUN")):
                iRand = CvUtil.myRandom(30, "PROMOTION_RANG_HUN")
                if iRand == 1:
                    iNewPromo = gc.getInfoTypeForString("PROMOTION_RANG_HUN")
                    pWinner.setHasPromotion(iNewPromo, True)
                    if pWinnerPlayer.isHuman():
                        CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_CIV_RANG", (pWinner.getName(), gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)

def flee(pLoser, iWinnerPlayer, iWinnerDamage):
    """
        # Flucht der Einheit / Escape of units --------
        # Defending unit only (inaktiv)
        # Nur wenn die Einheit nicht desertiert hat: bUnitDone
        # if not bUnitDone and not pLoser.isAttacking():
        # PAE V: defending units in cities gets flight (hiding behind walls) with max 70%. units kept on the city plot
    """
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iLoserPlayer = pLoser.getOwner()
    pLoserPlayer = gc.getPlayer(iLoserPlayer)
    bUnitFlucht = False
    NewUnit = None
    # Eine einzelne kaperbare Unit darf nicht fluechten
    # if pLoser.getCaptureUnitType(pLoser.getOwner()) > -1 and pLoser.plot().getNumUnits() > 1:
    if pLoser.getCaptureUnitType(pLoser.getCivilizationType()) == -1:
        bIsCity = False
        pLoserPlot = pLoser.plot()
        if pLoserPlot.isCity():
            iChance = pLoserPlot.getPlotCity().getPopulation()
            if iChance > 7:
                iChance = 7
            bIsCity = True
            iMaxHealth = 30  # max 30%
        else:
            iPromoFlucht1 = gc.getInfoTypeForString("PROMOTION_FLUCHT1")
            iPromoFlucht2 = gc.getInfoTypeForString("PROMOTION_FLUCHT2")
            iPromoFlucht3 = gc.getInfoTypeForString("PROMOTION_FLUCHT3")
            if pLoser.isHasPromotion(iPromoFlucht3):
                iChance = 8  # Flucht 3 - 80%
                iMaxHealth = 20  # max 20%
            elif pLoser.isHasPromotion(iPromoFlucht2):
                iChance = 6  # Flucht 2 - 60%
                iMaxHealth = 15  # max 15%
            elif pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_TOWN"):
                bIsCity = True
                iChance = 5
                iMaxHealth = 12  # max 12%
            elif (pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE")
                  or pLoserPlot.getImprovementType() == gc.getInfoTypeForString("IMPROVEMENT_VILLAGE_HILL")):
                bIsCity = True
                iChance = 5
                iMaxHealth = 10  # max 10%
            elif pLoser.isHasPromotion(iPromoFlucht1):
                iChance = 4  # Flucht 1 - 40%
                iMaxHealth = 10  # max 10%
            elif pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:
                if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_UR") or pLoser.getLevel() > 2:
                    iChance = 8
                    iMaxHealth = 50
                else:
                    iChance = 3
                    iMaxHealth = 25
            else:
                iChance = 2
                iMaxHealth = 5  # max 5%

        # Bei Schiffen eine Extra-Berechnung
        if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
            if iWinnerDamage >= 50:
                iChance = 10  # 100%: somit muss man womoeglich ein Schiff 2x angreifen, bevor es sinkt
                iMaxHealth = 20
            else:
                iChance += 1
                iMaxHealth += 5

        # Berittene nochmal +10%, except in cities -10%
        iCombatMounted = gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")
        if pLoser.getUnitCombatType() == iCombatMounted:
            if bIsCity:
                iChance -= 1
            else:
                iChance += 1

        iRand = 1 + CvUtil.myRandom(10, "Escape")

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Fluchtchance (Zeile 2924)", iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Max Health (Zeile 2925)", iMaxHealth)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if iRand < iChance:
            bUnitFlucht = True

            # Create a new unit
            #pPlot = pLoser.plot()
            #if pPlot.getNumUnits() == 1: pLoser.jumpToNearestValidPlot()
            NewUnit = pLoserPlayer.initUnit(pLoser.getUnitType(), pLoser.getX(), pLoser.getY(), UnitAITypes(pLoser.getUnitAIType()), DirectionTypes.DIRECTION_SOUTH)
            if pLoser.isMadeAttack():
                NewUnit.finishMoves()

            if pLoser.getUnitCombatType() != -1 or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE:
                iRandHealth = 1 + CvUtil.myRandom(iMaxHealth, "EscapeHealth")
                NewUnit.setDamage(100 - iRandHealth, -1) # Max Health
                NewUnit.setExperience(pLoser.getExperience(), -1)
                NewUnit.setLevel(pLoser.getLevel())

                # Check its promotions
                iRange = gc.getNumPromotionInfos()
                for iPromotion in range(iRange):
                    # init all promotions the unit had
                    if pLoser.isHasPromotion(iPromotion):
                        NewUnit.setHasPromotion(iPromotion, True)

            copyName(NewUnit, pLoser.getUnitType(), pLoser.getName())

            if not bIsCity:
                NewUnit.jumpToNearestValidPlot()
            if pLoserPlayer.isHuman():
                CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE", (NewUnit.getName(), 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ESCAPE_2", (NewUnit.getName(), 0)), None, 2, None, ColorTypes(13), 0, 0, False, False)

            # if Unit was a leader (PROMOTION_LEADER)
            if pLoser.getLeaderUnitType() > -1:
                NewUnit.setLeaderUnitType(pLoser.getLeaderUnitType())
                pLoser.setLeaderUnitType(-1)  # avoids ingame message "GG died in combat"

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Einheit fluechtet (Zeile 2774)", iChance)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return bUnitFlucht, NewUnit

def doAutomatedRanking(pWinner, pLoser):
    """
    # Feature - Automated Unit Ranking via Promotions: Trained, Experienced, Seasoned, Veteran, Elite, Legendary
    # Trainiert, Kampferfahren, Routiniert, Veteran, Elite, Legende
    # Each promotion gives +x% Strength
    # Animal Attack brings only 1st Ranking
    """
    if pLoser.isMilitaryHappiness() or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE or pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
        iPlayer = pWinner.getOwner()

        iCombat1 = gc.getInfoTypeForString('PROMOTION_COMBAT1')
        iCombat2 = gc.getInfoTypeForString('PROMOTION_COMBAT2')
        iCombat3 = gc.getInfoTypeForString('PROMOTION_COMBAT3')
        iCombat4 = gc.getInfoTypeForString('PROMOTION_COMBAT4')
        iCombat5 = gc.getInfoTypeForString('PROMOTION_COMBAT5')
        iCombat6 = gc.getInfoTypeForString('PROMOTION_COMBAT6')

        lPromo = [(iCombat1, 50), (iCombat2, 40), (iCombat3, 30), (iCombat4, 20), (iCombat5, 20), (iCombat6, 20)]

        iNeg1 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG1')
        iNeg2 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG2')
        iNeg3 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG3')
        iNeg4 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG4')
        iNeg5 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG5')

        lNeg = [(iNeg1, 10), (iNeg2, 10), (iNeg3, 20), (iNeg4, 20), (iNeg5, 20)]

        if not (pWinner.isHasPromotion(iCombat3) and pLoser.getOwner() == gc.getBARBARIAN_PLAYER()):
            iNewRank = -1
            if not pWinner.isHasPromotion(iCombat6):
                for iPromo, iChance in lPromo:
                    if not pWinner.isHasPromotion(iPromo):
                        iNewRank = iPromo
                        break

            # PAE for better AI: always gets it by 50%
            if not gc.getPlayer(pWinner.getOwner()).isHuman():
                iChance = 50

            if iNewRank == iCombat1 or iNewRank == iCombat2 or pLoser.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
                if iNewRank != -1 and CvUtil.myRandom(100, "automatedRanking") < iChance:
                    if (iPlayer, pWinner.getID()) not in PAEInstanceFightingModifier:
                        PAEInstanceFightingModifier.append((iPlayer, pWinner.getID()))
                        pWinner.setHasPromotion(iNewRank, True)
                        if gc.getPlayer(iPlayer).isHuman():                                                                # unitX.getDescription()
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RANKING", (pWinner.getName(), gc.getPromotionInfo(iNewRank).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewRank).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)

                # War weariness parallel ab Elite
                elif pWinner.isHasPromotion(iCombat5) and not pWinner.isHasPromotion(iNeg5):
                    if (iPlayer, pWinner.getID()) not in PAEInstanceFightingModifier:
                        for iPromo, iChance in lNeg:
                            if not pWinner.isHasPromotion(iPromo):
                                if iChance > CvUtil.myRandom(100, "war weariness"):
                                    PAEInstanceFightingModifier.append((iPlayer, pWinner.getID()))
                                    pWinner.setHasPromotion(iPromo, True)
                                    if gc.getPlayer(iPlayer).isHuman():
                                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_WAR_WEARINESS", (pWinner.getName(), gc.getPromotionInfo(iPromo).getDescription())), "AS2D_REBELLION", 2, gc.getPromotionInfo(iPromo).getButton(), ColorTypes(12), pWinner.getX(), pWinner.getY(), True, True)
                                    break


        # PAE V: Gewinner kann Mercenary-Promo ab Veteran verlieren
        # Better AI: 100%
        iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
        if pWinner.isHasPromotion(iCombat4) and pWinner.isHasPromotion(iPromoMercenary):
            bDoIt = False
            if gc.getPlayer(iPlayer).isHuman():
                iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
                iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
                iPromoLeadership = gc.getInfoTypeForString("PROMOTION_LEADERSHIP")

                if pWinner.isHasPromotion(iPromoLoyal) or pWinner.isHasPromotion(iPromoLeader) or pWinner.isHasPromotion(iPromoLeadership):
                    iChance = 2 #50%
                else:
                    iChance = 4 #25%

                if CvUtil.myRandom(iChance, "remove Mercenary promo") == 1:
                    bDoIt = True
            else:
                bDoIt = True

            if bDoIt:
                pWinner.setHasPromotion(iPromoMercenary, False)

        # PAE V: Old veterans needs more time to get fit again (elite needs longer)
        # Better AI: HI only
        if gc.getPlayer(iPlayer).isHuman():
            if pWinner.isHasPromotion(iCombat6):
                if pWinner.getDamage() < 50:
                    pWinner.setDamage(50, -1)
            elif pWinner.isHasPromotion(iCombat5):
                if pWinner.getDamage() < 70:
                    pWinner.setDamage(30, -1)
            #elif pWinner.isHasPromotion(iCombat4):
            #  if pWinner.getDamage() < 20: pWinner.setDamage(20, -1)


# Horse down
def doHorseDown(pUnit):
    iUnitType = pUnit.getUnitType()
    # iOwner = pUnit.getOwner()
    iX = pUnit.getX()
    iY = pUnit.getY()
    iNewUnitType = -1

    if iUnitType == gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"):
        if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME") or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
            iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_ROME")
        elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
            iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON")
        else:
            iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR")

    elif iUnitType == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_FOEDERATI")
    #elif iUnitType == gc.getInfoTypeForString('UNIT_PRAETORIAN_RIDER'):
    #    iNewUnitType = gc.getInfoTypeForString('UNIT_PRAETORIAN')
    elif iUnitType == gc.getInfoTypeForString('UNIT_MOUNTED_SACRED_BAND_CARTHAGE'):
        iNewUnitType = gc.getInfoTypeForString('UNIT_SACRED_BAND_CARTHAGE')
    elif iUnitType == gc.getInfoTypeForString('UNIT_MOUNTED_SCOUT'):
        if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE"):
            iNewUnitType = gc.getInfoTypeForString("UNIT_SCOUT_GREEK")
        else:
            iNewUnitType = gc.getInfoTypeForString("UNIT_SCOUT")

    if iNewUnitType != -1:
        # Create horse unit
        NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(gc.getInfoTypeForString("UNIT_HORSE"), iX, iY, UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()

        # Create a new unit
        NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnitType, iX, iY, UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.setExperience(pUnit.getExperience(), -1)
        NewUnit.setLevel(pUnit.getLevel())
        NewUnit.setDamage(pUnit.getDamage(), -1)
        if pUnit.getName() != gc.getUnitInfo(iUnitType).getText():
            UnitName = pUnit.getName()
            UnitName = re.sub(r" \(.*?\)", "", UnitName)
            NewUnit.setName(UnitName)
        # Check its promotions
        iRange = gc.getNumPromotionInfos()
        for iPromotion in range(iRange):
            # init all promotions the unit had
            if pUnit.isHasPromotion(iPromotion):
                NewUnit.setHasPromotion(iPromotion, True)
        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit.kill(True, -1)  # RAMK_CTD
        pUnit = None
        NewUnit.finishMoves()

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Horse Down (Zeile 5014)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse down

# Horse up
def doHorseUp(pPlot, pUnit):
    iUnitType = pUnit.getUnitType()
    # iOwner = pUnit.getOwner()
    iX = pUnit.getX()
    iY = pUnit.getY()
    iNewUnitType = -1

    # Pferd suchen und killen
    UnitHorse = gc.getInfoTypeForString("UNIT_HORSE")
    iRange = pPlot.getNumUnits()
    for iUnit in range(iRange):
        pUnit = pPlot.getUnit(iUnit)
        if pUnit.getUnitType() == UnitHorse:
            # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit.kill(True, -1)  # RAMK_CTD
            pUnit = None
            break

    if iUnitType in L.LUnitAuxiliar:
        iNewUnitType = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
    elif iUnitType == gc.getInfoTypeForString("UNIT_FOEDERATI"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN")
    #elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN"):
    #    iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER")
    elif iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE")
    elif iUnitType == gc.getInfoTypeForString("UNIT_SCOUT") or iUnitType == gc.getInfoTypeForString("UNIT_SCOUT_GREEK"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT")

    if iNewUnitType != -1:
        # Create a new unit
        NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnitType, iX, iY, UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.setExperience(pUnit.getExperience(), -1)
        NewUnit.setLevel(pUnit.getLevel())
        NewUnit.changeMoves(-60)
        NewUnit.setDamage(pUnit.getDamage(), -1)
        if pUnit.getName() != gc.getUnitInfo(iUnitType).getText():
            UnitName = pUnit.getName()
            UnitName = re.sub(r"( \(.*?\))", "", UnitName)
            NewUnit.setName(UnitName)
        # Check its promotions
        iRange = gc.getNumPromotionInfos()
        for iPromotion in range(iRange):
            # init all promotions the unit had
            if pUnit.isHasPromotion(iPromotion):
                NewUnit.setHasPromotion(iPromotion, True)
        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit.kill(True, -1)  # RAMK_CTD
        pUnit = None

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Horse Up (Zeile 5057)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse up

# Trojanisches Pferd
def doTrojanHorse(pCity, pUnit):
    iCityPlayer = pCity.getOwner()
    iUnitPlayer = pUnit.getOwner()
    pCityPlayer = gc.getPlayer(pCity.getOwner())
    pUnitPlayer = gc.getPlayer(pUnit.getOwner())

    iDamage = pCity.getDefenseModifier(0)
    pCity.changeDefenseDamage(iDamage)

    if pCityPlayer is not None and pUnitPlayer is not None:
        if pCityPlayer.isHuman():
            CyInterface().addMessage(
                iCityPlayer, False, 25,
                CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY",
                                       (pCity.getName(),
                                        pUnitPlayer.getCivilizationAdjective(2))),
                None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, pUnit.getButton(),
                ColorTypes(11), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY", (pCity.getName(), pUnitPlayer.getCivilizationAdjective(1))))
            popupInfo.addPopup(iCityPlayer)
        if pUnitPlayer.isHuman():
            CyInterface().addMessage(
                iUnitPlayer, False, 25,
                CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",
                                       (pCity.getName(),
                                        pCityPlayer.getCivilizationAdjective(2))),
                None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, pUnit.getButton(),
                ColorTypes(11), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText(
                "TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",
                (pCity.getName(), pCityPlayer.getCivilizationAdjective(1))))
            popupInfo.addPopup(iUnitPlayer)

        if iCityPlayer == gc.getGame().getActivePlayer() or iUnitPlayer == gc.getGame().getActivePlayer():
            CyAudioGame().Play2DSound("AS2D_THEIRDECLAREWAR")

        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit.kill(True, -1)  # RAMK_CTD
        pUnit = None

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Trojanisches Pferd (Zeile 9497)", 0)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# PAE Feature: Auswirkungen, wenn ein General stirbt
def doDyingGeneral(pUnit, iWinnerPlayer=-1):
    # PROMOTION_LEADER
    if pUnit.getLeaderUnitType() > -1:
        # Inits
        iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
        iPlayer = pUnit.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)
        pPlot = pUnit.plot()
        iNumLeadersOnPlot = 0

        # Anzahl der Generaele des Spielers
        iLeader = 0
        (loopUnit, pIter) = pPlayer.firstUnit(False)
        while loopUnit:
            if loopUnit.getLeaderUnitType() > -1:
                if loopUnit.getID() != pUnit.getID():
                    iLeader += 1
            (loopUnit, pIter) = pPlayer.nextUnit(pIter, False)

        # Units: bekommen Mercenary-Promo
        iNumUnits = pPlot.getNumUnits()
        # 1. Check Generals im Stack
        for i in range(iNumUnits):
            pLoopUnit = pPlot.getUnit(i)
            if pLoopUnit.getOwner() == iPlayer:
                if pLoopUnit.getLeaderUnitType() > -1:
                    iNumLeadersOnPlot += 1

        # 2. Vergabe der Promo
        for i in range(iNumUnits):
            pLoopUnit = pPlot.getUnit(i)
            if pLoopUnit.getOwner() == iPlayer:
                if i % iNumLeadersOnPlot == 0:
                    pLoopUnit.setHasPromotion(iPromoMercenary, True)

        # Cities: Stadtaufruhr
        (loopCity, pIter) = pPlayer.firstCity(False)
        while loopCity:
            cityOwner = loopCity.getOwner()
            if not loopCity.isNone() and cityOwner == iPlayer: #only valid cities
                if CvUtil.myRandom(iLeader, "Stadtaufruhr1") == 0:
                    # 2 bis 4 Runden Aufstand!
                    iRand = 2 + CvUtil.myRandom(2, "Stadtaufruhr2")
                    loopCity.changeHurryAngerTimer(iRand)
                    # Stadt ohne Kulturgrenzen
                    #iRand = 2 + CvUtil.myRandom(3, "Stadtaufruhr3")
                    #loopCity.setOccupationTimer (iRand)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MAIN_CITY_RIOT", (loopCity.getName(),)), "AS2D_REVOLTSTART", 2, ",Art/Interface/Buttons/Promotions/Combat5.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,5,10", ColorTypes(7), loopCity.getX(), loopCity.getY(), True, True)
            (loopCity, pIter) = pPlayer.nextCity(pIter, False)

        # PopUp
        if pPlayer.isHuman():
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Text PopUp only!
            popupInfo.setText(CyTranslator().getText(
                "TXT_KEY_POPUP_GENERALSTOD", (pUnit.getName(),)))
            popupInfo.addPopup(iPlayer)

        if iWinnerPlayer != -1:
            pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
            # War Weariness
            pTeam.changeWarWeariness(pWinnerPlayer.getTeam(), 10)

            # PAE Movie
            if pPlayer.isHuman() and pPlayer.isTurnActive() or pWinnerPlayer.isHuman() and pWinnerPlayer.isTurnActive():

                if pPlayer.getCurrentEra() > 2 or pWinnerPlayer.getCurrentEra() > 2:
                    iVids = 13
                else:
                    iVids = 11
                # GG dying movies (CvWonderMovieScreen)
                iMovie = 1 + CvUtil.myRandom(iVids, "GGDyingMovie")

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                popupInfo.setData1(iMovie)  # dynamicID in CvWonderMovieScreen
                popupInfo.setData2(-1)  # fix pCity.getID()
                popupInfo.setData3(4)  # fix PAE Movie ID for GG dies
                popupInfo.setText(u"showWonderMovie")
                if pPlayer.isHuman():
                    popupInfo.addPopup(iPlayer)
                elif pWinnerPlayer.isHuman():
                    popupInfo.addPopup(iWinnerPlayer)

def doRenegadeUnit(pLoser, pWinner, pLoserPlayer, pWinnerPlayer):
    bUnitDone = False
    iLoserUnitType = pLoser.getUnitType()
    # Winner gets Loser Unit
    if CvUtil.myRandom(3, "actualRenegade") == 0:
        # Piratenschiffe werden normale Schiffe
        iNewUnitType = iLoserUnitType
        if pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
            if iLoserUnitType == gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"):
                iNewUnitType = gc.getInfoTypeForString("UNIT_KONTERE")
            elif iLoserUnitType == gc.getInfoTypeForString("UNIT_PIRAT_BIREME"):
                iNewUnitType = gc.getInfoTypeForString("UNIT_BIREME")
            elif iLoserUnitType == gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"):
                iNewUnitType = gc.getInfoTypeForString("UNIT_TRIREME")
            elif iLoserUnitType == gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"):
                iNewUnitType = gc.getInfoTypeForString("UNIT_LIBURNE")

        # Create a new unit
        NewUnit = pWinnerPlayer.initUnit(iNewUnitType, pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        NewUnit.finishMoves()

        if pLoser.getUnitCombatType() != -1:
            NewUnit.setDamage(90, -1)
            NewUnit.setExperience(pLoser.getExperience(), -1)
            NewUnit.setLevel(pLoser.getLevel())
            # Check its promotions
            iRange = gc.getNumPromotionInfos()
            for iPromotion in range(iRange):
                # init all promotions of the loser unit
                if pLoser.isHasPromotion(iPromotion):
                    NewUnit.setHasPromotion(iPromotion, True)

            iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
            iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
            # PAE V: Loyal weg, Mercenary dazu
            if NewUnit.isHasPromotion(iPromoLoyal):
                NewUnit.setHasPromotion(iPromoLoyal, False)
            if not NewUnit.isHasPromotion(iPromoMercenary):
                NewUnit.setHasPromotion(iPromoMercenary, True)

            # Remove formations
            doUnitFormation(NewUnit, -1)

            # PAE V: Trait-Promotions
            # 1. Agg und Protect Promos weg
            # (2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten) Stimmt nicht, sie erhalten die Promo bei initUnit() sowieso
            if not pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
                iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")
                if NewUnit.isHasPromotion(iPromo):
                    NewUnit.setHasPromotion(iPromo, False)

        if pWinnerPlayer.isHuman():
            CyInterface().addMessage(pWinnerPlayer.getID(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_DESERTION_1", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
        if pLoserPlayer.isHuman():
            CyInterface().addMessage(pLoserPlayer.getID(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_DESERTION_2", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
        bUnitDone = True

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Gewinner (" + str(pWinner.getOwner()) + ") bekommt Verlierer (" + str(pLoser.getOwner()) + ")", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Winner gets Slave
    elif pWinner.getDomainType() == DomainTypes.DOMAIN_LAND:
        # Ausnahmen
        if pLoser.getUnitType() not in L.LUnitNoSlaves:
            iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
            iThisTeam = pWinnerPlayer.getTeam()
            team = gc.getTeam(iThisTeam)
            if team.isHasTech(iTechEnslavement):
                # Create a slave unit
                NewUnit = pWinnerPlayer.initUnit(gc.getInfoTypeForString("UNIT_SLAVE"), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.finishMoves()
                if pWinnerPlayer.isHuman():
                    CyInterface().addMessage(pWinnerPlayer.getID(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_1", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(14), 0, 0, False, False)
                if pLoserPlayer.isHuman():
                    CyInterface().addMessage(pLoserPlayer.getID(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_SLAVERY_2", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(12), 0, 0, False, False)
                bUnitDone = True
                # ***TEST***
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Gewinner bekommt Sklave (Zeile 2627)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return bUnitDone

def unsettledSlaves(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    lSlaves = []
    eUnitSlave = gc.getInfoTypeForString("UNIT_SLAVE")
    (loopUnit, pIter) = pPlayer.firstUnit(False)
    while loopUnit:
        if not loopUnit.isDead(): #is the unit alive and valid?
            if loopUnit.getUnitType() == eUnitSlave and loopUnit.getMoves() > 0:
                lSlaves.append(loopUnit)
        (loopUnit, pIter) = pPlayer.nextUnit(pIter, False)

    for pUnit in lSlaves:
        # Nicht auf Hoher See (als Cargo von Schiffen), Kueste schon
        pPlot = pUnit.plot()
        if pPlot.getTerrainType() != gc.getInfoTypeForString("TERRAIN_OCEAN"):
            iChance = 8
            # Civic that increase rebelling
            if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_VOELKERRECHT")):
                iChance += 4
            # Military units decrease odds
            if pPlot.getNumDefenders(pUnit.getOwner()) > 0:
                iChance -= 4

            if iChance > CvUtil.myRandom(100, "Stehende Sklaven"):
                # wenn das Christentum gegruendet wurde / if christianity was found
                # Christ : Rebell = 1 : 4
                iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
                if gc.getGame().isReligionFounded(iReligion) and CvUtil.myRandom(4, "Stehende Sklaven Christ") == 1:
                    iUnitType = gc.getInfoTypeForString("UNIT_CHRISTIAN_MISSIONARY")
                    pPlayer.initUnit(iUnitType, pUnit.getX(), pUnit.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_2_CHRIST", (0,)), None, 2, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(14), pUnit.getX(), pUnit.getY(), True, True)
                    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pUnit.kill(True, -1)  # RAMK_CTD
                    pUnit = None

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Sklave zu Christ. Missionar (Zeile 1275)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                else:
                    # Ein Sklave auf fremden Terrain kann nicht rebellieren sondern verschwindet oder macht einen Fluchtversuch 50:50
                    if pPlot.getOwner() != pUnit.getOwner():
                        if pPlayer.isHuman():
                            iRand = 1 + CvUtil.myRandom(4, "FluchtversuchText")
                            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_LOST_"+str(iRand), (0, "")), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
                        # Barbareneinheit erschaffen
                        if CvUtil.myRandom(2, "Fluchtversuch") == 1:
                            # Einen guenstigen Plot auswaehlen
                            rebelPlotArray = []
                            for i in range(3):
                                for j in range(3):
                                    loopPlot = gc.getMap().plot(pUnit.getX() + i - 1, pUnit.getY() + j - 1)
                                    if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                                        if not loopPlot.isImpassable() and not loopPlot.isWater() and not loopPlot.isPeak():
                                            rebelPlotArray.append(loopPlot)
                            if rebelPlotArray:
                                pPlot = rebelPlotArray[CvUtil.myRandom(len(rebelPlotArray), "Fluchtversuch3")]
                                iUnitType = gc.getInfoTypeForString("UNIT_SLAVE")
                                CvUtil.spawnUnit(iUnitType, pPlot, gc.getPlayer(gc.getBARBARIAN_PLAYER()))

                        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                        pUnit.kill(True, -1)  # RAMK_CTD
                        pUnit = None
                        # ***TEST***
                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Slave lost in enemy territory (Zeile 1297)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                    else:
                        # Einen guenstigen Plot auswaehlen
                        rebelPlotArray = []
                        rebelPlotArrayB = []
                        for i in range(3):
                            for j in range(3):
                                loopPlot = gc.getMap().plot(pUnit.getX() + i - 1, pUnit.getY() + j - 1)
                                if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                                    if loopPlot.getOwner() == iPlayer:
                                        if loopPlot.isHills():
                                            rebelPlotArray.append(loopPlot)
                                        if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                                            rebelPlotArrayB.append(loopPlot)

                        if not rebelPlotArray:
                            rebelPlotArray = rebelPlotArrayB

                        # es kann rebelliert werden
                        if rebelPlotArray:
                            pPlot = rebelPlotArray[CvUtil.myRandom(len(rebelPlotArray), "rebelPlotArray3")]
                            iUnitType = gc.getInfoTypeForString("UNIT_REBELL")
                            CvUtil.spawnUnit(iUnitType, pPlot, gc.getPlayer(gc.getBARBARIAN_PLAYER()))
                            if pPlayer.isHuman():
                                CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_2_REBELL", (0,)), None, 2, "Art/Interface/Buttons/Units/button_rebell.dds", ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                            # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                            pUnit.kill(True, -1)  # RAMK_CTD
                            pUnit = None
                            # ***TEST***
                            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Sklave zu Rebell (Zeile 1327)", 1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

# Next Unit after NetMessage
def doGoToNextUnit(pUnit):
    # go to and select next Unit
    pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)

def copyName(NewUnit, iUnitType, sUnitName):
    if sUnitName != gc.getUnitInfo(iUnitType).getText():
        sUnitName = re.sub(r" \(.*?\)", "", sUnitName)
        NewUnit.setName(sUnitName)

def initSupply(pUnit):
    iMaxSupply = getMaxSupply(pUnit)
    setSupply(pUnit, iMaxSupply)

def fillSupply(pUnit, iChange):
    iMaxSupply = getMaxSupply(pUnit)
    iCurrentSupply = getSupply(pUnit)
    if iCurrentSupply != iMaxSupply:
        if iCurrentSupply + iChange > iMaxSupply:
            iChange -= (iMaxSupply - iCurrentSupply)
            iCurrentSupply = iMaxSupply
        else:
            iCurrentSupply += iChange
            iChange = 0

    setSupply(pUnit, iCurrentSupply)
    return iChange

def setSupply(pUnit, iValue):
    CvUtil.addScriptData(pUnit, "s", iValue)

def getSupply(pUnit):
    iMaxSupply = getMaxSupply(pUnit)

    # kein Eintrag == Fabrikneu
    iCurrentSupply = CvUtil.getScriptData(pUnit, ["s"], iMaxSupply)
    if iCurrentSupply > iMaxSupply:
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Current Supply is bogus", iCurrentSupply)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        setSupply(pUnit, iMaxSupply)
        iCurrentSupply = iMaxSupply
    return iCurrentSupply

def getMaxSupply(pUnit):
    eDruide = gc.getInfoTypeForString("UNIT_DRUIDE")
    eBrahmane = gc.getInfoTypeForString("UNIT_BRAHMANE")
    # Maximalwert herausfinden
    if pUnit.getUnitType() == eDruide or pUnit.getUnitType() == eBrahmane:
        iMaxSupply = 100
    else:
        iMaxSupply = 200
    # Trait Strategist / Stratege: +50% Kapazitaet / +50% capacity
    if gc.getPlayer(pUnit.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_STRATEGE")):
        iMaxSupply += int(iMaxSupply/2)
    return iMaxSupply


def renegade(pWinner, pLoser):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iLoserPlayer = pLoser.getOwner()
    pLoserPlayer = gc.getPlayer(iLoserPlayer)
    pLoserPlot = pLoser.plot()
    pWinnerPlot = pWinner.plot()
    iWinnerUnitAIType = pWinner.getUnitAIType()
    iWinnerUnitType = pWinner.getUnitType()
    iLoserUnitAIType = pLoser.getUnitAIType()
    iLoserUnitType = pLoser.getUnitType()

    bUnitRenegades = True

    iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
    iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
    iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
    iPromoLeadership = gc.getInfoTypeForString("PROMOTION_LEADERSHIP")
    iPromoHero = gc.getInfoTypeForString("PROMOTION_HERO")
    iPromoBrander = gc.getInfoTypeForString("PROMOTION_BRANDER")
    #iPromoSurrender = gc.getInfoTypeForString("PROMOTION_FORM_WHITEFLAG")
    lUnitAI = [UnitAITypes.UNITAI_ANIMAL, UnitAITypes.UNITAI_EXPLORE]
    # Ausnahmen - using UnitArray from above
    if iWinnerUnitAIType in lUnitAI:
        bUnitRenegades = False
    elif iWinnerUnitType in L.LUnitWildAnimals:
        bUnitRenegades = False
    elif iLoserUnitAIType in lUnitAI:
        bUnitRenegades = False
    elif(iLoserUnitType in L.LUnitWarAnimals or
         iLoserUnitType in L.LUnitDomesticated or
         iLoserUnitType in L.LUnitLootLessSeaUnits or
         iLoserUnitType in L.LUnitCanBeDomesticated or
         iLoserUnitType in L.LUnitWildAnimals):
        bUnitRenegades = False
    elif pWinner.isNoCapture():
        # PAE V: Piraten sollen nur kentern: UnitInfos.xml: bNoCapture=1
        bUnitRenegades = False
    # elif pLoser.isHasPromotion(iPromoSurrender): bUnitRenegades = True
    elif pLoser.isHasPromotion(iPromoLoyal) and not pLoser.isHasPromotion(iPromoMercenary):
        bUnitRenegades = False
    elif pLoser.isHasPromotion(iPromoLeader) or pLoser.isHasPromotion(iPromoBrander) or pWinner.isNoCapture():
        bUnitRenegades = False
    elif pLoser.hasCargo() and pLoser.canAttack():
        bUnitRenegades = False
    elif pLoserPlot.getNumUnits() == 1 and pLoser.getCaptureUnitType(pLoser.getCivilizationType()) != -1:
        bUnitRenegades = False
    # Attacking from Coast
    elif pWinner.isCargo():
        if pWinnerPlot.isWater():
            iNumCargoSpace = 0
            iNumCargoUnits = 0
            iRange = pWinnerPlot.getNumUnits()
            for i in range(iRange):
                pLoopUnit = pWinnerPlot.getUnit(i)
                if pLoopUnit.getOwner() == iWinnerPlayer:
                    iNumCargoSpace += pLoopUnit.cargoSpace()
                    iNumCargoUnits += pLoopUnit.getCargo()
            if iNumCargoSpace <= iNumCargoUnits:
                bUnitRenegades = False

    if bUnitRenegades:
        # if pLoser.isHasPromotion(iPromoSurrender): iRandMax = 0 #100%
        iUnitRenegadeChance = 20  # 10%
        if pWinner.isHasPromotion(iPromoLeader):
            iUnitRenegadeChance += 20
        if pWinner.isHasPromotion(iPromoHero):
            iUnitRenegadeChance += 10
        if pWinner.isHasPromotion(iPromoLeadership):
            iUnitRenegadeChance += 10
        if pLoser.isHasPromotion(iPromoHero):
            iUnitRenegadeChance -= 10
        if pLoser.isHasPromotion(iPromoLeadership):
            iUnitRenegadeChance -= 10
        # Trait Charismatic: Mehr Ueberlaeufer / more renegades
        if pWinnerPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CHARISMATIC")):
            iUnitRenegadeChance += 10
        if pLoserPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_CHARISMATIC")):
            iUnitRenegadeChance -= 10
        if pLoser.isHasPromotion(iPromoMercenary):
            iUnitRenegadeChance += 10
        iRand = CvUtil.myRandom(100, "renegade")
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST", ("Einheit allegiance Chance (Zeile 4150)", iRand)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        # Winner gets Loser Unit
        if iRand < iUnitRenegadeChance:
            bUnitRenegades = doRenegadeUnit(pLoser, pWinner, pLoserPlayer, pWinnerPlayer)
        else:
            bUnitRenegades = False
    return bUnitRenegades


def doNavalOnCombatResult(pWinner, pLoser, bWinnerIsDead):
    bUnitDone = False
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iLoserUnitType = pLoser.getUnitType()

    if not bWinnerIsDead:
        # ---- Schiffe sollen nach dem Angriff die Haelfte der uebrigen Bewegungspunkte haben "
        pWinner.changeMoves((pWinner.maxMoves()-pWinner.getMoves())/2)

    # Seeeinheiten (Treibgut erzeugen)
    iUnitTreibgut = gc.getInfoTypeForString("UNIT_TREIBGUT")
    # ---- SEA: Schiffe sollen Treibgut erzeugen
    if pLoser.getUnitType() not in L.LUnitLootLessSeaUnits:
        # Treibgut Chance 50%
        if CvUtil.myRandom(2, "Treibgut") == 0:
            terrain1 = gc.getInfoTypeForString("TERRAIN_OCEAN")
            terrain2 = gc.getInfoTypeForString("TERRAIN_COAST")
            iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

            # Freie Plots finden
            SeaPlots = []
            iX = pLoser.getX()
            iY = pLoser.getY()
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
                if loopPlot is not None and not loopPlot.isNone():
                    if loopPlot.getFeatureType() == iDarkIce:
                        continue
                    if not loopPlot.isPeak() and not loopPlot.isCity() and not loopPlot.isHills():
                        if loopPlot.getTerrainType() == terrain1 or loopPlot.getTerrainType() == terrain2:
                            if not loopPlot.isUnit():
                                SeaPlots.append(loopPlot)

            if SeaPlots:
                if gc.getUnitInfo(iLoserUnitType).getProductionCost() > 180:
                    iMaxTreibgut = 2
                else:
                    iMaxTreibgut = 1
                barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())

                for _ in range(iMaxTreibgut):
                    if not SeaPlots:
                        break
                    iRand = CvUtil.myRandom(len(SeaPlots), "SeaPlots")
                    loopPlot = SeaPlots[iRand]
                    # Unit erzeugen
                    CvUtil.spawnUnit(iUnitTreibgut, loopPlot, barbPlayer)
                    if pWinnerPlayer.isHuman():
                        CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_UNIT_ERSTELLT", (gc.getUnitInfo(iUnitTreibgut).getDescription(),)), None, 2, gc.getUnitInfo(iUnitTreibgut).getButton(), ColorTypes(11), loopPlot.getX(), loopPlot.getY(), True, True)
                    # Plot aus der Liste entfernen
                    SeaPlots.remove(loopPlot)

    # --- Treibgut gibt Sklaven oder Gold, wenn iCargo nicht voll is
    elif pLoser.getUnitType() == iUnitTreibgut:
        bUnitDone = True
        bMove2NextPlot = False
        # Ist ein freier Platz am Schiff?
        if not bWinnerIsDead and pWinner.getCargo() < pWinner.cargoSpace():
            # Treibgut einfangen
            iRand = CvUtil.myRandom(3, "Treibgut einfangen")
            if iRand == 0:
                iUnit = gc.getInfoTypeForString("UNIT_SLAVE")
                NewUnit = pWinnerPlayer.initUnit(iUnit, pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setTransportUnit(pWinner)
                NewUnit.finishMoves()
                if pWinnerPlayer.isHuman():
                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_SLAVE", ("",)), None, 2, gc.getUnitInfo(iUnit).getButton(), ColorTypes(8), pLoser.getX(), pLoser.getY(), True, True)
            elif iRand == 1:
                iRand = 11 + CvUtil.myRandom(20, "Treibgut einfangen3")
                pWinnerPlayer.changeGold(iRand)
                if pWinnerPlayer.isHuman():
                    CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MONEY_UNIT_KILLED", ("", iRand)), None, 2, gc.getUnitInfo(iUnitTreibgut).getButton(), ColorTypes(8), pLoser.getX(), pLoser.getY(), True, True)
            # Treibgut nicht eingefangen
            else:
                # Einheit Treibgut neu erzeugen
                bMove2NextPlot = True
                if pWinnerPlayer.isHuman():
                    iRand = 1 + CvUtil.myRandom(9, "Treibgut einfangen4")
                    szText = CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_CATCHME"+str(iRand), ())
                    CyInterface().addMessage(iWinnerPlayer, True, 10, szText, None, 2, gc.getUnitInfo(iUnitTreibgut).getButton(), ColorTypes(11), pLoser.getX(), pLoser.getY(), True, True)
        # Cargo voll
        else:
            # Einheit Treibgut neu erzeugen
            bMove2NextPlot = True
            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_UNIT_TREIBGUT_NOSPACE", ("",)), None, 2, gc.getUnitInfo(iUnitTreibgut).getButton(), ColorTypes(11), pLoser.getX(), pLoser.getY(), True, True)

        # Treibgut soll nicht ausserhalb der Kulturgrenze wiederauftauchen (jumpToNearestValidPlot), sondern gleich 1 Plot daneben (sofern frei)
        if bMove2NextPlot:
            lNewPlot = []
            iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
            iX = pLoser.getX()
            iY = pLoser.getY()
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
                if loopPlot is not None and not loopPlot.isNone():
                    if loopPlot.getFeatureType() != iDarkIce:
                        if not loopPlot.isUnit():
                            if loopPlot.isWater():
                                lNewPlot.append(loopPlot)
            pJumpPlot = None
            if lNewPlot:
                iRand = CvUtil.myRandom(len(lNewPlot), "Treibgut einfangen5")
                pJumpPlot = lNewPlot[iRand]
            elif pLoser.jumpToNearestValidPlot():
                pJumpPlot = pLoser.plot()
            if pJumpPlot != None:
                # Create unit
                CvUtil.spawnUnit(iUnitTreibgut, pJumpPlot, gc.getPlayer(gc.getBARBARIAN_PLAYER()))
    return bUnitDone

def doLoserLoseHorse(pLoser, iWinnerPlayer):
    iLoserPlayer = pLoser.getOwner()
    pLoserPlayer = gc.getPlayer(iLoserPlayer)
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    pLoserPlot = pLoser.plot()
    iLoserUnitType = pLoser.getUnitType()
    bDoIt = False
    iNewUnitType = -1
    if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_FOEDERATI")
        bDoIt = True
    elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_PRAETORIAN")
        bDoIt = True
    elif pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"):
        iNewUnitType = gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE")
        bDoIt = True
    # exclude basic chariots
    elif gc.getUnitInfo(pLoser.getUnitType()).getPrereqAndBonus() == gc.getInfoTypeForString("BONUS_HORSE"):
        bDoIt = True

    if bDoIt:
        iRand = CvUtil.myRandom(10, "mountedToMelee")
        if iRand == 0 and iNewUnitType != -1:
            # Create a new unit
            NewUnit = pLoserPlayer.initUnit(iNewUnitType, pLoser.getX(), pLoser.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            NewUnit.setExperience(pLoser.getExperience(), -1)
            NewUnit.setLevel(pLoser.getLevel())
            NewUnit.finishMoves()
            NewUnit.setDamage(50, -1)
            # Check its promotions
            iRange = gc.getNumPromotionInfos()
            for iPromotion in range(iRange):
                # init all promotions the unit had
                if pLoser.isHasPromotion(iPromotion):
                    NewUnit.setHasPromotion(iPromotion, True)

            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_LOST_HORSE_1", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            if pLoserPlayer.isHuman():
                CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_LOST_HORSE_2", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            return True
        if iRand <= 2:
            # Create horse unit
            iUnitType = gc.getInfoTypeForString("UNIT_HORSE")
            # Seek a Plot
            rebelPlotArray = []
            iX = pLoser.getX()
            iY = pLoser.getY()
            for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
                loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
                if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                    if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                        rebelPlotArray.append(loopPlot)

            # Create Barbarian Horse Unit
            if rebelPlotArray:
                barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                iPlot = CvUtil.myRandom(len(rebelPlotArray), "horseLost")
                CvUtil.spawnUnit(iUnitType, rebelPlotArray[iPlot], barbPlayer)
            else:
                CvUtil.spawnUnit(iUnitType, pLoserPlot, pLoserPlayer)
            if pLoserPlayer.isHuman():
                CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_ONLY_HORSE_LEFT", (gc.getUnitInfo(iLoserUnitType).getDescription(), 0)), None, 2, None, ColorTypes(6), 0, 0, False, False)
            return True
    return False

def huntingResult(pLoser, pWinner):
    iWinnerPlayer = pWinner.getOwner()
    pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
    iWinnerUnitType = pWinner.getUnitType()
    iLoserUnitType = pLoser.getUnitType()
    if pLoser.getCaptureUnitType(pWinnerPlayer.getCivilizationType()) != -1:
        # unit will be captured, thus not butchered
        return

    iJagd = gc.getInfoTypeForString("TECH_HUNTING")
    team = gc.getTeam(pWinnerPlayer.getTeam())
    if team.isHasTech(iJagd):
        iX = pWinner.getX()
        iY = pWinner.getY()
        CityArray = []
        for x in range(-4, 5):
            for y in range(-4, 5):
                loopPlot = plotXY(iX, iY, x, y)
                if loopPlot is not None and not loopPlot.isNone():
                    if loopPlot.isCity():
                        pCity = loopPlot.getPlotCity()
                        if pCity.getOwner() == iWinnerPlayer:
                            CityArray.append(pCity)
        if CityArray:
            lJagd = {
                gc.getInfoTypeForString("UNIT_BOAR"): (5, 4),
                gc.getInfoTypeForString("UNIT_DEER"): (3, 4),
                gc.getInfoTypeForString("UNIT_WILD_CAMEL"): (3, 4),
                gc.getInfoTypeForString("UNIT_BEAR"): (4, 4),
                gc.getInfoTypeForString("UNIT_WILD_HORSE"): (4, 5),
                gc.getInfoTypeForString("UNIT_ELEFANT"): (6, 3)
            }
            try:
                iFoodMin, iFoodRand = lJagd[iLoserUnitType]
            except KeyError:
                # Lion, Wolf, etc. 2 - 3
                iFoodMin = 2
                iFoodRand = 2

            # Hunter gets full bonus
            if iWinnerUnitType == gc.getInfoTypeForString("UNIT_HUNTER"):
                iFoodAdd = iFoodMin + iFoodRand - 1
            else:
                iFoodAdd = CvUtil.myRandom(iFoodRand, "Hunt") + iFoodMin
            iCity = CvUtil.myRandom(len(CityArray), "HuntCity")
            CityArray[iCity].changeFood(iFoodAdd)
            if pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_ADD_FOOD", (pWinner.getName(), CityArray[iCity].getName(), iFoodAdd)), None, 2, pLoser.getButton(), ColorTypes(13), pLoser.getX(), pLoser.getY(), True, True)

def rebell(pOldUnit, pNewPlayer, pPlot):
    iUnitType = pOldUnit.getUnitType()
    pNewUnit = pNewPlayer.initUnit(iUnitType, pPlot.getX(), pPlot.getY(), UnitAITypes(pOldUnit.getUnitAIType()), DirectionTypes.DIRECTION_SOUTH)
    pNewUnit = initUnitFromUnit(pOldUnit, pNewUnit)
    # Original unit killen
    # pOldUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
    pOldUnit.kill(True, -1)  # RAMK_CTD


def convert(pOldUnit, iNewUnit, pPlayer):
    pNewUnit = pPlayer.initUnit(iNewUnit, pOldUnit.getX(), pOldUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes(pOldUnit.getFacingDirection()))
    pNewUnit = initUnitFromUnit(pOldUnit, pNewUnit)
    # 1 Bewegungspunkt Verlust
    pNewUnit.changeMoves(pOldUnit.getMoves() + 60)
    ## extra fuer Piraten
    # Veteran und Mercenary Promo checken
    # Veteran ohne Mercenary bleibt ohne Mercenary
    iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
    if pOldUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")):
        if not pOldUnit.isHasPromotion(iPromoMercenary):
            if pNewUnit.isHasPromotion(iPromoMercenary):
                pNewUnit.setHasPromotion(iPromoMercenary, False)

    # Original unit killen
    pOldUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)


def initUnitFromUnit(pOldUnit, pNewUnit):
    pNewUnit.setExperience(pOldUnit.getExperience(), -1)
    pNewUnit.setLevel(pOldUnit.getLevel())
    pNewUnit.setDamage(pOldUnit.getDamage(), -1)
    copyName(pNewUnit, pOldUnit.getUnitType(), pOldUnit.getName())
    # Check its promotions
    iRange = gc.getNumPromotionInfos()
    for j in range(iRange):
        if pOldUnit.isHasPromotion(j):
            pNewUnit.setHasPromotion(j, True)
    return pNewUnit
