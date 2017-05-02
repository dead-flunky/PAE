### Imports
from CvPythonExtensions import *
import random
import re

import CvUtil
### Defines
gc = CyGlobalContext()

# PAE - InstanceChanceModifier for units in getting Fighting-Promotions (per turn)
# [PlayerID, UnitID]
PAEInstanceFightingModifier = []

def myRandom (num):
      if num <= 1: return 0
      else: return random.randint(0, num-1)


# Upgrade Veteran Unit to Elite Unit - Belobigung
# CommandUpgrade geht nur, wenn
# - die Einheit auch wirklich zu dieser Einheit laut XML upgegradet werden kann
# - alle Vorraussetzungen fuer die neuen Einheit erfuellt sind
# - im eigenen Territorium
#pUnit.doCommand (CommandTypes.COMMAND_UPGRADE, gc.getInfoTypeForString("UNIT_TRIARII2"), 0)
def doUpgradeVeteran(pUnit, iNewUnit, bChangeCombatPromo):
    if not iNewUnit in xrange(gc.getNumUnitInfos()):
        # ***TEST***
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Upgrade Veteran: Invalid New Unit Type",iNewUnit)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return
    if pUnit != None and not pUnit.isNone():
        pUnitOwner = gc.getPlayer(pUnit.getOwner())
        if pUnitOwner != None and not pUnitOwner.isNone():
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

            pUnit.kill(1,pUnit.getOwner())

# Unit Rang Promos (PAE, ModMessage:751)
def doUpgradeRang(iPlayer,iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pUnit = pPlayer.getUnit(iUnit)
    iUnitType = pUnit.getUnitType()
    iNewUnit = -1

    # Rome
    if iUnitType == gc.getInfoTypeForString("UNIT_LEGION"):    iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_OPTIO")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION2"): iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_OPTIO2")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_OPTIO"):  iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_CENTURIO")
    elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"): iNewUnit = gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2")
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
    elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES"): iNewUnit = gc.getInfoTypeForString("UNIT_ROME_COMITATENSES2")
    elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES2"): iNewUnit = gc.getInfoTypeForString("UNIT_ROME_COMITATENSES3")

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
        if pPlayer.isHuman(): pPlayer.changeGold(-100)
    else:
        # ***TEST***
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Upgrade by Rank: this unit should have no rank ",iUnitType)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        
        

# PAE UNIT FORMATIONS ------------------------------
def canDoFormation (pUnit, iFormation):
    if not pUnit.canMove(): return False
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")): return False

    lMelee = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN")]
    lArcher = [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]

    iUnitType = pUnit.getUnitType()
    iUnitCombatType = pUnit.getUnitCombatType()
    pPlayer = gc.getPlayer(pUnit.getOwner())
    pTeam = gc.getTeam(pPlayer.getTeam())

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
                if iUnitType not in UnitArray: return True


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
                if iUnitType not in UnitArray: return True

        # Partherschuss oder Kantabrischer Kreis
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER") or iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
            UnitArray = [
                #gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"),
                gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
                gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"),
                gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"),
                gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"),
                gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER")
            ]
            if iUnitType in UnitArray:
                # Partherschuss
                if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                        CivArray = [
                            gc.getInfoTypeForString("CIVILIZATION_HETHIT"),
                            gc.getInfoTypeForString("CIVILIZATION_PHON"),
                            gc.getInfoTypeForString("CIVILIZATION_ISRAEL"),
                            gc.getInfoTypeForString("CIVILIZATION_PERSIA"),
                            gc.getInfoTypeForString("CIVILIZATION_BABYLON"),
                            gc.getInfoTypeForString("CIVILIZATION_SUMERIA"),
                            gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"),
                            gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"),
                            gc.getInfoTypeForString("CIVILIZATION_PARTHER"),
                            gc.getInfoTypeForString("CIVILIZATION_HUNNEN"),
                            gc.getInfoTypeForString("CIVILIZATION_INDIA"),
                            gc.getInfoTypeForString("CIVILIZATION_BARBARIAN")
                        ]
                        if pUnit.getCivilizationType() in CivArray:
                            return True
                # Kantabrischer Kreis
                elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                        return True

        # Keil (fuer schwere Kavallerie)
        elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"),
                    gc.getInfoTypeForString("UNIT_EQUITES"),
                    gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2"),
                    gc.getInfoTypeForString("UNIT_HORSEMAN_DECURIO"),
                    gc.getInfoTypeForString("UNIT_LEGION_TRIBUN"),
                    gc.getInfoTypeForString("UNIT_CATAPHRACT"),
                    gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"),
                    gc.getInfoTypeForString("UNIT_CLIBANARII"),
                    gc.getInfoTypeForString("UNIT_CLIBANARII_ROME"),
                    gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"),
                    gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),
                    gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"),
                    gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),
                    gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT")
                ]
                if iUnitType in UnitArray:
                    return True

    # Melee and Spear
    elif iUnitCombatType in lMelee:
        # Fortress
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS") and pUnit.baseMoves() == 1: return True
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2") and pUnit.baseMoves() > 1: return True

        # Schildwall
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_WARRIOR"),
                    gc.getInfoTypeForString("UNIT_KURZSCHWERT"),
                    gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"),
                    gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"),
                    gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
                    gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
                    gc.getInfoTypeForString("UNIT_AXEMAN"),
                    gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"),
                    gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR")
                ]
                if iUnitType not in UnitArray:
                    return True


        # Drill: Manipel, Phalanx, ...
        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
            # Roman Legion (Kohorte)
            if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_LEGION"),
                    gc.getInfoTypeForString("UNIT_LEGION2"),
                    gc.getInfoTypeForString("UNIT_LEGION_OPTIO"),
                    gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"),
                    gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"),
                    gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"),
                    gc.getInfoTypeForString("UNIT_PRAETORIAN2"),
                    gc.getInfoTypeForString("UNIT_PRAETORIAN3")
                ]
                if pUnit.getUnitType() in UnitArray:
                    return True
            # Treffen-Taktik
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    return True
            # Manipel
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
                    return True
            # Phalanx-Arten (nur Speer)
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                        return True
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                        return True
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"):
                if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                        return True
            # Geschlossene Formation (alle Melee)
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
                    return True
            # Testudo
            elif iFormation == gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                    UnitArray = [
                        gc.getInfoTypeForString("UNIT_LEGION"),
                        gc.getInfoTypeForString("UNIT_LEGION2"),
                        gc.getInfoTypeForString("UNIT_LEGION_OPTIO"),
                        gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"),
                        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"),
                        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"),
                        gc.getInfoTypeForString("UNIT_PRAETORIAN2"),
                        gc.getInfoTypeForString("UNIT_PRAETORIAN3")
                    ]
                    if pUnit.getUnitType() in UnitArray:
                        return True
        # -- Drill end

        # Keil
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_KEIL"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                return True
        # Zangenangriff
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
                return True
        # Flankenschutz (nur Speer)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"):
            if iUnitCombatType == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    return True
        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                return True


    # Archers
    elif iUnitCombatType in lArcher:
        # Elefantengasse (auch weiter unten fuer Bogen)
        if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_GASSE"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                return True


    # Flucht
    if iFormation == gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"):
        if pUnit.getDamage() >= 70:
            UnitCombatArray = [
                gc.getInfoTypeForString("UNITCOMBAT_MELEE"),
                gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),
                gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),
                gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"),
                gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
                gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")
            ]
            if iUnitCombatType in UnitCombatArray:
                if pUnit.baseMoves() == 1:
                    return True

    return False
  # can do Formationen / Formations End ------

# PAE UNIT FORMATIONS ------------------------------
def doUnitFormation (pUnit, iNewFormation):
    pPlayer = gc.getPlayer(pUnit.getOwner())

    FormationArray = [
        gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"),
        gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"),    # TECH_CLOSED_FORM
        gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"),        # TECH_PHALANX
        gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"),       # TECH_PHALANX2
        gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"),         # TECH_PHALANX2
        gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"),        # TECH_MANIPEL
        gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"),        # TECH_TREFFEN
        gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"),        # TECH_MARIAN_REFORM
        gc.getInfoTypeForString("PROMOTION_FORM_KEIL"),           # TECH_HUFEISEN
        gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"),  # TECH_HORSEBACK_RIDING_2
        gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"),  # TECH_TREFFEN
        gc.getInfoTypeForString("PROMOTION_FORM_GASSE"),          # TECH_GEOMETRIE2
        gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"),        # TECH_MARIAN_REFORM
        gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"),
        gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"),
        gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"),        # TECH_BRANDSCHATZEN
        gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"),     # TECH_LOGIK
        gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE")     # TECH_LOGIK
    ]
    # Human
    if pPlayer.isHuman():
        # stehende Fortress-Einheiten sollen fuer die KI stehend bleiben
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"))
        FormationArray.append(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"))

        # Fuer alle Einheiten dieser Gruppe
        pPlot = pUnit.plot()

        iNumUnits = pPlot.getNumUnits()
        for i in range (iNumUnits):
            loopUnit = pPlot.getUnit(i)
            if loopUnit.IsSelected():
                # Formation geben
                if iNewFormation != -1:
                    if canDoFormation (loopUnit, iNewFormation):
                        # Formationen auf NULL setzen
                        for j in FormationArray:
                            #if loopUnit.isHasPromotion(j):
                            loopUnit.setHasPromotion(j, False)
                        # Formation geben
                        loopUnit.setHasPromotion(iNewFormation, True)
                # Formationen entfernen
                else:
                    # Formationen auf NULL setzen
                    for j in FormationArray:
                        #if loopUnit.isHasPromotion(j):
                        loopUnit.setHasPromotion(j, False)
    # AI
    else:
        # Formationen auf NULL setzen
        for j in FormationArray:
            #if loopUnit.isHasPromotion(j):
            pUnit.setHasPromotion(j, False)
        # Formation geben
        if iNewFormation != -1:
            pUnit.setHasPromotion(iNewFormation, True)

    # Unit den Fortify Modus erzwingen - hat keinen effekt?!
    #if iNewFormation == gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"):
    #  pPlot = gc.getMap().plot( pUnit.getX(), pUnit.getY() )
    #  #pUnit.getGroup().setActivityType (ActivityTypes.ACTIVITY_SLEEP)
    #  pUnit.getGroup().pushMission (MissionTypes.MISSION_FORTIFY,0,0,0,False,False,MissionAITypes.NO_MISSIONAI,pPlot,pUnit)


def doAIPlotFormations (pPlot, iPlayer):
    bContinue = False
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
        if not gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
            return
    elif not gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
        return

    # City
    iRange = 1
    iX = pPlot.getX()
    iY = pPlot.getY()
    for x in range(-iRange, iRange+1):
        for y in range(-iRange, iRange+1):
          loopPlot = plotXY(iX, iY, x, y)
          if loopPlot != None and not loopPlot.isNone():
            if loopPlot.isCity():
              pCity = loopPlot.getPlotCity()
              if pCity.getOwner() != iPlayer:
                if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
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
    for i in range (iRange):
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
        else: iStackStatus = 3

        if iStackStatus == 3:
          # deactivated
          i = 0
          for unit in lPlayerUnits:
            if unit.getUnitCombatType() != gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
              doUnitFormation(unit, gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT"))
        else:
          i = 0
          for unit in lPlayerUnits:
            if not bSupplyUnit:
              if unit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                UnitArray = []
                UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
                UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
                if unit.getUnitType() not in UnitArray:
                  lMountedUnits.append(unit)
            if i <= iLimit: doAIUnitFormations (unit, True, bCity, bElefant)
            else: doAIUnitFormations (unit, False, bCity, bElefant)
            i += 1

          # Fourage - Supply
          if not bSupplyUnit:
           if len(lMountedUnits):
            iLevel = 10
            if gc.getTeam(gc.getPlayer(iPlayer).getTeam()).isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
              pUnit = lMountedUnits[0]
              for unit in lMountedUnits:
                if unit.getLevel() < iLevel:
                  pUnit = unit
                  iLevel = unit.getLevel()
              doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"))


def doAIUnitFormations (pUnit, bOffensive, bCity, bElefant):
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")): return
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")): return
    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")): return
    if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pUnit.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE: return

    iUnitType = pUnit.getUnitType()
    pUnitOwner = gc.getPlayer(pUnit.getOwner())
    pTeam = gc.getTeam(pUnitOwner.getTeam())

    lMelee  = [
        gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN")
    ]
    lArcher = [
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
        gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")
    ]

    # Naval
    if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
            UnitArray = [
                gc.getInfoTypeForString("UNIT_KILIKIEN"),
                gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),
                gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),
                gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),
                gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE")
            ]
            if pUnit.getUnitType() not in UnitArray:
                # Keil oder Zange
                if bOffensive:
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"))
                    return
                else:
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"))
                    return


    # Wald, Schild, Zange, Phalanx, Keil
    #pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())

    # Formation im Wald
    #iFeatType1 = gc.getInfoTypeForString("FEATURE_FOREST")
    #iFeatType2 = gc.getInfoTypeForString("FEATURE_JUNGLE")
    #iFeatType3 = gc.getInfoTypeForString("FEATURE_DICHTERWALD")
    #if pPlot.getFeatureType() == iFeatType1 or pPlot.getFeatureType() == iFeatType2 or pPlot.getFeatureType() == iFeatType3:

    # Mounted
    elif pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
        UnitArray = []
        #UnitArray.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"))
        UnitArray.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
        if iUnitType in UnitArray:
            CivArray = []
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HETHIT"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PHON"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ISRAEL"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PERSIA"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BABYLON"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SUMERIA"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PARTHER"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HUNNEN"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_INDIA"))
            CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BARBARIAN"))
            if pUnit.getCivilizationType() in CivArray and pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"))
                return
            elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"))
                return

        if bOffensive:
            # Keil (auch weiter unten fuer Melee)
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                UnitArray = [
                    gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"),
                    gc.getInfoTypeForString("UNIT_EQUITES"),
                    gc.getInfoTypeForString("UNIT_LEGION_TRIBUN"),
                    gc.getInfoTypeForString("UNIT_CATAPHRACT"),
                    gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"),
                    gc.getInfoTypeForString("UNIT_CLIBANARII"),
                    gc.getInfoTypeForString("UNIT_CLIBANARII_ROME"),
                    gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"),
                    gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),
                    gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"),
                    gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),
                    gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT")
                ]
                if pUnit.getUnitType() in UnitArray:
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KEIL"))
                    return

    # Melee and Spear
    elif pUnit.getUnitCombatType() in lMelee:
        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
            # Legionaries
            UnitArray = []
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION2"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
            UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN3"))

            # Testudo
            if bCity:
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                    if pUnit.getUnitType() in UnitArray and myRandom(2) == 0:
                        doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"))
                        return

            # Kohorte / Legion (ersetzt alles)
            if pUnit.getUnitType() in UnitArray:
                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"))
                return


        # Elefantengasse
        if bElefant:
            if myRandom(4) == 0:
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
                    return


        # Offensive
        if bOffensive:
            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
                # Treffen-Taktik ersetzt Manipel
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"))
                    return
                # Manipel ersetzt Phalanx, Manipular-Phalanx und Schiefe Phalanx
                elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"))
                    return
                # Phalanx-Arten und Geschlossene Formation
                else:                    
                    # Phalanx nur Speer
                    if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                        # Manipular-Phalanx und Schiefe Phalanx ersetzt Phalanx
                        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):
                            # Schiefe Schlachtordnung
                            if myRandom(2) == 0:
                                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"))
                                return
                            # Manipular-Phalanx
                            else:
                                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"))
                                return
                        # Phalanx
                        elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                            doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"))
                            return
                # Geschlossene Formation (alle Melee mit Drill)
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"))
                    return
        # Defensive
        else:
            # Flankenschutz (nur Speer)
            if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                    doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"))
                    return
            # Zangenangriff (dem Keil vorziehen)
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"))
                return

        # Restlichen Units, falls oben nix draus wurde
        # Schildwall
        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
            UnitArray = [
                gc.getInfoTypeForString("UNIT_WARRIOR"),
                gc.getInfoTypeForString("UNIT_KURZSCHWERT"),
                gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"),
                gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"),
                gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
                gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
                gc.getInfoTypeForString("UNIT_AXEMAN"),
                gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"),
                gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR")
            ]

            if pUnit.getUnitType() not in UnitArray:
                doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"))
                return

    # Archer, vor allem Skirmisher
    elif bElefant and pUnit.getUnitCombatType() in lArcher:
        # Elefantengasse
        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
            #if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
            doUnitFormation(pUnit, gc.getInfoTypeForString("PROMOTION_FORM_GASSE"))
            return

  # PAE UNIT FORMATIONS END ------------------------------


# PAE UNIT BATTLE PROMOTION
def doUnitGetsPromo (pUnitTarget, pUnitSource, pPlot, bMadeAttack):
    global PAEInstanceFightingModifier
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

    if pPlot.isCity(): bCity = True
    else: bCity = False

    lFirstPromos = []
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_WOODSMAN1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_GUERILLA1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_DESERT1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_JUNGLE1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_SUMPF1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"))
    lFirstPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"))

    iFirstPromos = 0
    for i in lFirstPromos:
      if pUnitTarget.isHasPromotion(i): iFirstPromos += 1

    iDivisor = 1
    # PAEInstanceFightingModifier for wins in the same turn
    if (pUnitTarget.getOwner(),pUnitTarget.getID()) in PAEInstanceFightingModifier: iDivisor = 5

    # Chances
    iChanceCityAttack = 20 / iDivisor
    iChanceCityDefense = 20 / iDivisor
    # Trait Conqueror / Eroberer: iChanceCityAttack*2
    if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")): iChanceCityAttack *= 2
    iChanceUnitType = 10 / iDivisor
    iChanceTerrain = 30 / (iFirstPromos*2 + 1) / iDivisor
    # Static chance of Promo 2-5 of a terrain
    iChanceTerrain2 = 5 / iDivisor


    # 1. chance: Either City or Open Field
    # City
    if bCity:
      iRand = myRandom(100)
      if bMadeAttack:
        # Attacker
        if iChanceCityAttack > iRand:
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")):
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
            iChanceUnitType = iChanceUnitType / 2
            # Trait Conquereror / Eroberer: Automatische Heilung bei Stadtangriffs-Promo / auto-healing when receiving city raider promo
            if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_EROBERER")): pUnitTarget.setDamage(0, -1)
        # Defender
      else:
        if iChanceCityDefense > iRand:
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")):
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
            iChanceUnitType = iChanceUnitType / 2
            # Trait Protective: Automatische Heilung bei Stadtverteidigungs-Promo / auto-healing when receiving city garrison promo
            if gc.getPlayer(pUnitTarget.getOwner()).hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")): pUnitTarget.setDamage(0, -1)

    # on open field
    else:
      iRandTerrain = myRandom(100)
      if iChanceTerrain > iRandTerrain:
        # either hill, terrain or feature, river

        # init unit promos and terrains
        lTerrain = []
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA5")) and pPlot.isHills():
          lTerrain.append("Hills")

        # thx to Dertuek:
        if bMadeAttack and pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
          if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")):
            pPlotAtt=pUnitTarget.plot()
            pPlotDef=pUnitSource.plot()
            if pPlotAtt.isWater() and not pPlotDef.isWater():
              lTerrain.append("River")
            elif pPlotAtt.isRiverSide():
              iDiffX=pPlotDef.getX()-pPlotAtt.getX()
              iDiffY=pPlotDef.getY()-pPlotAtt.getY()

              iDir = -1
              if iDiffX == 0 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTH
              elif iDiffX == 1 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTHEAST
              elif iDiffX == 1 and iDiffY == 0:
                iDir=DirectionTypes.DIRECTION_EAST
              elif iDiffX == 1 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTHEAST
              elif iDiffX == 0 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTH
              elif iDiffX == -1 and iDiffY == -1:
                iDir=DirectionTypes.DIRECTION_SOUTHWEST
              elif iDiffX == -1 and iDiffY == 0:
                iDir=DirectionTypes.DIRECTION_WEST
              elif iDiffX == -1 and iDiffY == 1:
                iDir=DirectionTypes.DIRECTION_NORTHWEST

              if iDir > -1:
                if pPlotAtt.isRiverCrossing(iDir):
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
        if not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT") and \
           not pUnitTarget.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE") :
          if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST") or pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN5")):
              lTerrain.append("Forest")
          elif pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE5")):
              lTerrain.append("Jungle")
          elif pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_SWAMP"):
            if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF5")):
              lTerrain.append("Swamp")

        if len(lTerrain) > 0:
          iChanceUnitType = iChanceUnitType / 2
          iRand = myRandom(len(lTerrain))
          if lTerrain[iRand] == "River":
            iNewPromo = gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")
          elif lTerrain[iRand] == "Hills":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA1")
          elif lTerrain[iRand] == "Forest":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN1")
          elif lTerrain[iRand] == "Jungle":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE1")
          elif lTerrain[iRand] == "Swamp":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_SUMPF1")
          elif lTerrain[iRand] == "Desert":
            if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT4")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT5")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT4")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT3")
            elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT2")
            else: iNewPromo = gc.getInfoTypeForString("PROMOTION_DESERT1")

          # Chances of Promos 2-5
          if iNewPromo not in lFirstPromos and iRandTerrain >= iChanceTerrain2: iNewPromo = -1


    if iNewPromo > -1:

      # naechste Chance verringern
      iChanceUnitType = iChanceUnitType / 2

      pUnitTarget.setHasPromotion(iNewPromo, True)
      PAEInstanceFightingModifier.append((pUnitTarget.getOwner(),pUnitTarget.getID()))
      if gc.getPlayer(pUnitTarget.getOwner()).isHuman():
        CyInterface().addMessage(pUnitTarget.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION",(pUnitTarget.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)

    # 2. chance: enemy combat type
    iNewPromo = -1
    iRand = myRandom(100)
    if iChanceUnitType > iRand:

      if pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COVER1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_COVER1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SKIRM1")

      #elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MELEE"):
      #  if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK2")):  iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK2")
      #  elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SHOCK")): iNewPromo = gc.getInfoTypeForString("PROMOTION_SHOCK")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_AXE1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SWORD1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
         if   pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR3")
         elif pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR2")
         elif not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_PARADE_SPEAR1")

      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_CHARIOT"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION1")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION1")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION2")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION2")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORMATION3")): iNewPromo = gc.getInfoTypeForString("PROMOTION_FORMATION3")
      elif pUnitSource.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SIEGE"):
        if not pUnitTarget.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CHARGE")):     iNewPromo = gc.getInfoTypeForString("PROMOTION_CHARGE")

      if iNewPromo > -1:
        pUnitTarget.setHasPromotion(iNewPromo, True)
        PAEInstanceFightingModifier.append((pUnitTarget.getOwner(),pUnitTarget.getID()))
        if gc.getPlayer(pUnitTarget.getOwner()).isHuman():
          CyInterface().addMessage(pUnitTarget.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION",(pUnitTarget.getName(),gc.getPromotionInfo(iNewPromo).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnitTarget.getX(), pUnitTarget.getY(), True, True)





def doRetireVeteran (pUnit):
    lPromos = []
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT3"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT4"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT5"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_COMBAT6"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG1"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG2"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG3"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG4"))
    lPromos.append(gc.getInfoTypeForString("PROMOTION_MORAL_NEG5"))
    #lPromos.append(gc.getInfoTypeForString("PROMOTION_HERO"))
    for iPromo in lPromos:
      if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)

    # Reduce XP
    pUnit.setExperience(pUnit.getExperience() / 2, -1)
    # Reduce Lvl: deactivated
    #if pUnit.getLevel() > 3:
    #  pUnit.setLevel(pUnit.getLevel() - 3)
    #else:
    #  pUnit.setLevel(1)

# PAE V ab Patch 3: Wenn Hauptstadt angegriffen wird, sollen alle Einheiten in Festungen remobilisiert werden (Promo FORTRESS)
def doMobiliseFortifiedArmy(iOwner):
    pPlayer = gc.getPlayer(iOwner)
    pCity = pPlayer.getCapitalCity()
    if pCity != None:
        iPromoFort = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
        iPromoFort2 = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
        (pUnit, iter) = pPlayer.firstUnit(False)
        while pUnit:
            pUnit.setHasPromotion(iPromoFort, False)
            pUnit.setHasPromotion(iPromoFort2, False)
            (pUnit, iter) = pPlayer.nextUnit(iter, False)

# Handelsposten errichten
def doBuildHandelsposten(pUnit):
    iPrice = 30
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if pPlayer.getGold() < iPrice:
        # TODO: eigener Text
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS",("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
        return
    pPlot = pUnit.plot()
    pPlot.setRouteType(0)
    pPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"))
    CvUtil.addScriptData(pPlot, "p", iPlayer)
    pPlot.setCulture(iPlayer,1,True)
    pPlot.setOwner(iPlayer)
    pPlayer.changeGold(-iPrice)
    pUnit.kill(1,pUnit.getOwner())



# isHills: PROMOTION_GUERILLA1
# FEATURE_FOREST, FEATURE_DICHTERWALD: PROMOTION_WOODSMAN1
# FEATURE_JUNGLE: PROMOTION_JUNGLE1
# TERRAIN_SWAMP: PROMOTION_SUMPF1
# TERRAIN_DESERT: PROMOTION_DESERT1
# City Attack: PROMOTION_CITY_RAIDER1
# City Defense: PROMOTION_CITY_GARRISON1
# isRiverSide: PROMOTION_AMPHIBIOUS

# PAE CITY builds UNIT -> auto promotions (land units)
def doCityUnitPromotions (pCity, pUnit):
    # check city radius (r): 1 plot = 3, 2 plots = 5
    r = 3
    initChanceCity = 1  # ab Stadt: Chance * City Pop
    initChance = 5      # Chance * Plots
    #initChanceRiver = 2 # for PROMOTION_AMPHIBIOUS only
    # --------------
    iCityAttack = 0
    iCityDefense = 0
    iHills = 0
    iForest = 0
    iJungle = 0
    iSwamp = 0
    iDesert = 0
    iRiver = 0

    if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")):
        if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):
            iPromoGarrison = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
            if pCity.getPopulation() * initChanceCity > myRandom(100):
                if not pUnit.isHasPromotion(iPromoGarrison):
                    doGiveUnitPromo(pUnit,iPromoGarrison,pCity)
        elif pUnit.getUnitCombatType() in [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN")]:
            iPromoRaider = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
            if pCity.getPopulation() * initChanceCity > myRandom(100):
                if not pUnit.isHasPromotion(iPromoRaider):
                    doGiveUnitPromo(pUnit,iPromoRaider,pCity)

    # not for rams
    lRams = []
    lRams.append(gc.getInfoTypeForString("UNIT_RAM"))
    lRams.append(gc.getInfoTypeForString("UNIT_BATTERING_RAM"))
    lRams.append(gc.getInfoTypeForString("UNIT_BATTERING_RAM2"))
    if pUnit.getUnitType() in lRams: return

    # Start seeking plots for promos
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot != None and not pLoopPlot.isNone():
            if pLoopPlot.isHills() or pLoopPlot.isPeak(): iHills += 1
            #if pLoopPlot.isRiverSide(): iRiver += 1
            if pLoopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"): iDesert += 1
            elif pLoopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_SWAMP"): iSwamp += 1
            if pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"): iForest += 1
            elif pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DICHTERWALD"): iForest += 1
            elif pLoopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"): iJungle += 1

    # River - deactivated
    #if iRiver > 0:
    #  iRand = myRandom(100)
    #  if iRiver * initChanceRiver > iRand:
    #    if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS")): doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_AMPHIBIOUS"),pCity)

    # PAE V Patch 7: nur 1 Terrain Promo soll vergeben werden
    lPossiblePromos = []

    # Hills
    iPromoHills = gc.getInfoTypeForString("PROMOTION_GUERILLA1")
    if iHills and iHills * initChance > myRandom(100):
        if not pUnit.isHasPromotion(iPromoHills):
            lPossiblePromos.append(iPromoHills)

    # Desert
    iPromoDesert = gc.getInfoTypeForString("PROMOTION_DESERT1")
    if iDesert and iDesert * initChance > myRandom(100):
        if not pUnit.isHasPromotion(iPromoDesert):
            lPossiblePromos.append(iPromoDesert)

    # Forest
    iPromoForest = gc.getInfoTypeForString("PROMOTION_WOODSMAN1")
    if iForest and iForest * initChance > myRandom(100):
        if not pUnit.isHasPromotion(iPromoForest):
            lPossiblePromos.append(iPromoForest)

    # Swamp
    iPromoSumpf = gc.getInfoTypeForString("PROMOTION_SUMPF1")
    if iSwamp and iSwamp * initChance > myRandom(100):
        if not pUnit.isHasPromotion(iPromoSumpf):
            lPossiblePromos.append(iPromoSumpf)

    # Jungle
    iPromoJungle = gc.getInfoTypeForString("PROMOTION_JUNGLE1")
    if iJungle and iJungle * initChance > myRandom(100):
        if not pUnit.isHasPromotion(iPromoJungle):
            lPossiblePromos.append(iPromoJungle)

    # only 1 of the pot
    if len(lPossiblePromos) > 0:
        iPromo = myRandom(len(lPossiblePromos))
        doGiveUnitPromo(pUnit,lPossiblePromos[iPromo],pCity)


  # PAE CITY builds UNIT -> auto promotions (ships)
def doCityUnitPromotions4Ships (pCity, pUnit):
    initChance = 2

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iWater = 0
    # Start seeking plots for promos
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot != None and not pLoopPlot.isNone():
                if pLoopPlot.getFeatureType() == iDarkIce: continue
                if pLoopPlot.isWater(): iWater += 1

    if iWater > 0:
        iRand = myRandom(10)
        if iWater * initChance > iRand:
            if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION1")):
                doGiveUnitPromo(pUnit,gc.getInfoTypeForString("PROMOTION_NAVIGATION1"),pCity)


def doGiveUnitPromo (pUnit, iNewPromo, pCity):
    pUnit.setHasPromotion(iNewPromo, True)
    if gc.getPlayer(pUnit.getOwner()).isHuman():
        if iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1") or iNewPromo == gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"):
            CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_3",(pUnit.getName(),gc.getPromotionInfo(iNewPromo).getDescription(),pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
        else:
            CyInterface().addMessage(pUnit.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_GETS_PROMOTION_2",(pUnit.getName(),gc.getPromotionInfo(iNewPromo).getDescription(),pCity.getName())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewPromo).getButton(), ColorTypes(13), pUnit.getX(), pUnit.getY(), True, True)
  # --------------------------------

# ++++++++ Names for Legions +++++++++++++++++
# Reusing names of fallen Legions
def setLegionName(pUnit):
    pPlayer = gc.getPlayer(pUnit.getOwner())

    LegioUsedNames = []
    (loopUnit, iter) = pPlayer.firstUnit(False)
    while loopUnit:
      sName = loopUnit.getName()
      if "Legio" in sName:
        LegioUsedNames.append(re.sub(" \(.*?\)","",sName))
      (loopUnit, iter) = pPlayer.nextUnit(iter, False)

    LegioNames = ["Legio I Adiutrix","Legio I Germanica","Legio I Italica","Legio I Macriana Liberatrix","Legio I Minervia","Legio I Parthica","Legio II Adiutrix","Legio II Augusta","Legio II Italica","Legio II Parthica","Legio II Traiana Fortis","Legio III Augusta","Legio III Cyrenaica","Legio III Gallica","Legio III Italica","Legio III Parthica","Legio III Macedonica","Legio IV Flavia Felix","Legio IV Scythica","Legio V Alaudae","Legio V Macedonica","Legio VI Ferrata","Legio VI Victrix","Legio VII Claudia","Legio VII Gemina","Legio VIII Augusta","Legio IX Hispana","Legio X Fretensis","Legio X Equestris","Legio XI Claudia","Legio XII Fulminata","Legio XIII Gemina","Legio XIV Gemina","Legio XV Apollinaris","Legio XV Primigenia","Legio XVI Gallica","Legio XVI Flavia Firma","Legio XVII","Legio XVIII","Legio XIX","Legio XX Valeria Victrix","Legio XXI Rapax","Legio XXII Deiotariana","Legio XXII Primigenia","Legio XXX Ulpia Victrix","Legio I Iulia Alpina","Legio I Armeniaca","Legio I Flavia Constantia","Legio I Flavia Gallicana","Legio I Flavia Martis","Legio I Flavia Pacis","Legio I Illyricorum","Legio I Iovia","Legio I Isaura Sagitaria","Legio I Martia","Legio I Maximiana","Legio I Noricorum","Legio I Pontica","Legio II Iulia Alpina","Legio II Armeniaca","Legio II Brittannica","Legio II Flavia Virtutis","Legio II Herculia","Legio II Isaura","Legio III Iulia Alpina","Legio III Diocletiana","Legio III Flavia Salutis","Legio III Herculia","Legio III Isaura","Legio IV Italica","Legio IV Martia","Legio IV Parthica","Legio V Iovia","Legio V Parthica","Legio VI Gallicana","Legio VI Herculia","Legio VI Hispana","Legio VI Parthica","Legio XII Victrix","Legio Thebaica"]
    iRange = len(LegioNames)
    for i in range(iRange):
      if LegioNames[i] not in LegioUsedNames:
        pUnit.setName(LegioNames[i])
        break
  # --- end Legion Names


def doBlessUnits(iX,iY,iOwner,iUnitID):
    pPlot = gc.getMap().plot(iX, iY)
    pPlayer = gc.getPlayer(iOwner)
    iPromo = gc.getInfoTypeForString("PROMOTION_BLESSED")
    iCost = 100

    iNumUnits = pPlot.getNumUnits()
    for i in range (iNumUnits):
      if pPlayer.getGold() < iCost: break
      loopUnit = pPlot.getUnit(i)
      if loopUnit.IsSelected():
        if not loopUnit.isHasPromotion(iPromo):
          # Gold abziehen
          pPlayer.changeGold(-iCost)
          # Formation geben
          loopUnit.setHasPromotion(iPromo, True)
          loopUnit.finishMoves()
  # -----------------

def doAutomatedRanking(pWinner, pLoser):
    if pLoser.isMilitaryHappiness() or pLoser.getUnitAIType() == UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() == UnitAITypes.UNITAI_EXPLORE or pLoser.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
        iPlayer = pWinner.getOwner()

        iCombat1 = gc.getInfoTypeForString('PROMOTION_COMBAT1')
        iCombat2 = gc.getInfoTypeForString('PROMOTION_COMBAT2')
        iCombat3 = gc.getInfoTypeForString('PROMOTION_COMBAT3')
        iCombat4 = gc.getInfoTypeForString('PROMOTION_COMBAT4')
        iCombat5 = gc.getInfoTypeForString('PROMOTION_COMBAT5')
        iCombat6 = gc.getInfoTypeForString('PROMOTION_COMBAT6')

        lPromo = [(iCombat1, 50),(iCombat2, 40),(iCombat3, 30),(iCombat4, 20),(iCombat5, 20),(iCombat6, 20)]

        iNeg1 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG1')
        iNeg2 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG2')
        iNeg3 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG3')
        iNeg4 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG4')
        iNeg5 = gc.getInfoTypeForString('PROMOTION_MORAL_NEG5')

        lNeg = [(iNeg1, 10),(iNeg2, 10),(iNeg3, 20),(iNeg4, 20),(iNeg5, 20)]

        if not (pWinner.isHasPromotion(iCombat3) and pLoser.getOwner() == gc.getBARBARIAN_PLAYER()):
            iNewRank = -1
            if not pWinner.isHasPromotion(iCombat6):
                for iPromo, iChance in lPromo:
                    if not pWinner.isHasPromotion(iPromo):
                        iNewRank = iPromo
                        break

            # PAE for better AI: always gets it by 50%
            if not gc.getPlayer(pWinner.getOwner()).isHuman(): iChance = 50

            if iNewRank == iCombat1 or iNewRank == iCombat2 or pLoser.getUnitAIType() != UnitAITypes.UNITAI_ANIMAL or pLoser.getUnitAIType() != UnitAITypes.UNITAI_EXPLORE:
                if iNewRank != -1 and iChance > myRandom(100):
                    if (iPlayer,pWinner.getID()) not in PAEInstanceFightingModifier:
                        PAEInstanceFightingModifier.append((iPlayer,pWinner.getID()))
                        pWinner.setHasPromotion(iNewRank, True)
                        if gc.getPlayer(iPlayer).isHuman():                                                                # unitX.getDescription()
                            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RANKING",(pWinner.getName(),gc.getPromotionInfo(iNewRank).getDescription())), "AS2D_IF_LEVELUP", 2, gc.getPromotionInfo(iNewRank).getButton(), ColorTypes(13), pWinner.getX(), pWinner.getY(), True, True)

                # War weariness parallel ab Elite
                elif pWinner.isHasPromotion(iCombat5) and not pWinner.isHasPromotion(iNeg5):
                    if (iPlayer,pWinner.getID()) not in PAEInstanceFightingModifier:
                        for iPromo, iChance in lNeg:
                            if not pWinner.isHasPromotion(iPromo):
                                if iChance > myRandom(100):
                                    PAEInstanceFightingModifier.append((iPlayer,pWinner.getID()))
                                    pWinner.setHasPromotion(iPromo, True)
                                    if gc.getPlayer(iPlayer).isHuman():
                                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_WAR_WEARINESS",(pWinner.getName(),gc.getPromotionInfo(iPromo).getDescription())), "AS2D_REBELLION", 2, gc.getPromotionInfo(iPromo).getButton(), ColorTypes(12), pWinner.getX(), pWinner.getY(), True, True)



        # PAE V: Gewinner kann Mercenary-Promo ab Veteran verlieren
        # Better AI: 100%
        iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
        if pWinner.isHasPromotion(iCombat4) and pWinner.isHasPromotion(iPromoMercenary):
            bDoIt = False
            if gc.getPlayer(iPlayer).isHuman():
                iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
                iPromoLeader = gc.getInfoTypeForString("PROMOTION_LEADER")
                iPromoLeadership = gc.getInfoTypeForString("PROMOTION_LEADERSHIP")

                if pWinner.isHasPromotion(iPromoLoyal) or pWinner.isHasPromotion(iPromoLeader) or pWinner.isHasPromotion(iPromoLeadership): iChance = 2 #50%
                else: iChance = 4 #25%

                if myRandom(iChance) == 1: bDoIt = True
            else: bDoIt = True

            if bDoIt:
                pWinner.setHasPromotion(iPromoMercenary, False)

        # PAE V: Old veterans needs more time to get fit again (elite needs longer)
        # Better AI: HI only
        if gc.getPlayer(iPlayer).isHuman():
            if pWinner.isHasPromotion(iCombat6):
                if pWinner.getDamage() < 50: pWinner.setDamage(50, -1)
            elif pWinner.isHasPromotion(iCombat5):
                if pWinner.getDamage() < 70: pWinner.setDamage(30, -1)
            #elif pWinner.isHasPromotion(iCombat4):
            #  if pWinner.getDamage() < 20: pWinner.setDamage(20, -1)


# Horse down
def doHorseDown(pPlot, pUnit):
    iUnitType = pUnit.getUnitType()
    iOwner = pUnit.getOwner()
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
            UnitName = re.sub(" \(.*?\)","",UnitName)
            NewUnit.setName(UnitName)
        # Check its promotions
        iRange = gc.getNumPromotionInfos()
        for iPromotion in range(iRange):
            # init all promotions the unit had
            if pUnit.isHasPromotion(iPromotion):
                NewUnit.setHasPromotion(iPromotion, True)
        pUnit.kill(1,pUnit.getOwner())
        NewUnit.finishMoves()

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Horse Down (Zeile 5014)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse down

# Horse up
def doHorseUp(pPlot, pUnit):
    iUnitType = pUnit.getUnitType()
    iOwner = pUnit.getOwner()
    iX = pUnit.getX()
    iY = pUnit.getY()
    iNewUnitType = -1

    # Pferd suchen und killen
    UnitHorse = gc.getInfoTypeForString("UNIT_HORSE")
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
        pUnit = pPlot.getUnit(iUnit)
        if pUnit.getUnitType() == UnitHorse:
            pUnit.kill(1,pUnit.getOwner())
            break

    lUnitAuxiliar = [
    gc.getInfoTypeForString("UNIT_AUXILIAR"),
    gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"),
    gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON")
    ]

    if iUnitType in lUnitAuxiliar:
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
            UnitName = re.sub("( \(.*?\))","",UnitName)
            NewUnit.setName(UnitName)
        # Check its promotions
        iRange = gc.getNumPromotionInfos()
        for iPromotion in range(iRange):
            # init all promotions the unit had
            if pUnit.isHasPromotion(iPromotion):
                NewUnit.setHasPromotion(iPromotion, True)
        pUnit.kill(1,pUnit.getOwner())

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Horse Up (Zeile 5057)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # end Horse up

# Trojanisches Pferd
def doTrojanHorse(pCity, pUnit):
    iCityPlayer = pCity.getOwner()
    iUnitPlayer = pUnit.getOwner()
    pCityPlayer = gc.getPlayer(pCity.getOwner())
    pUnitPlayer = gc.getPlayer(pUnit.getOwner())

    iDamage = pCity.getDefenseModifier(0)
    pCity.changeDefenseDamage(iDamage)

    if pCityPlayer != None and pUnitPlayer != None:
      if pCityPlayer.isHuman():
        CyInterface().addMessage(iCityPlayer,False,25,CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY",(pCity.getName(),pUnitPlayer.getCivilizationAdjective(2))),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,pUnit.getButton(),ColorTypes(11),pCity.getX(),pCity.getY(),True,True)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_CITY",(pCity.getName(),pUnitPlayer.getCivilizationAdjective(1) )))
        popupInfo.addPopup(iCityPlayer)
      if pUnitPlayer.isHuman():
        CyInterface().addMessage(iUnitPlayer,False,25,CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",(pCity.getName(),pCityPlayer.getCivilizationAdjective(2))),None,InterfaceMessageTypes.MESSAGE_TYPE_INFO,pUnit.getButton(),ColorTypes(11),pCity.getX(),pCity.getY(),True,True)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_TROJAN_HORSE_UNIT",(pCity.getName(),pCityPlayer.getCivilizationAdjective(1) )))
        popupInfo.addPopup(iUnitPlayer)

      if iCityPlayer == gc.getGame().getActivePlayer() or iUnitPlayer == gc.getGame().getActivePlayer():
          CyAudioGame().Play2DSound("AS2D_THEIRDECLAREWAR")

      pUnit.kill(1,pUnit.getOwner())

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Trojanisches Pferd (Zeile 9497)",0)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# PAE Feature: Auswirkungen, wenn ein General stirbt
def doDyingGeneral (pUnit):
    # Inits
    iPromoMercenary = gc.getInfoTypeForString("PROMOTION_MERCENARY")
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = pUnit.plot()
    iNumLeadersOnPlot = 0

    # Anzahl der Generaele des Spielers
    iLeader = 0
    (loopUnit, iter) = pPlayer.firstUnit(False)
    while loopUnit:
      if loopUnit.getLeaderUnitType() > -1:
        if loopUnit.getID() != pUnit.getID():
          iLeader += 1
      (loopUnit, iter) = pPlayer.nextUnit(iter, False)

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
    (loopCity, iter) = pPlayer.firstCity(False)
    while(loopCity):
      cityOwner = loopCity.getOwner()
      if not loopCity.isNone() and cityOwner == iPlayer: #only valid cities
        if 0 == myRandom(iLeader):
          # 2 bis 4 Runden Aufstand!
          iRand = 2 + myRandom(2)
          loopCity.changeHurryAngerTimer (iRand)
          # Stadt ohne Kulturgrenzen
          #iRand = 2 + myRandom(3)
          #loopCity.setOccupationTimer (iRand)
          if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 5, CyTranslator().getText("TXT_KEY_MAIN_CITY_RIOT",(loopCity.getName(),)), "AS2D_REVOLTSTART", 2, ",Art/Interface/Buttons/Promotions/Combat5.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,5,10", ColorTypes(7), loopCity.getX(), loopCity.getY(), True, True)
      (loopCity, iter) = pPlayer.nextCity(iter, False)

    # PopUp
    if pPlayer.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Text PopUp only!
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_GENERALSTOD",(pUnit.getName(),)) )
      popupInfo.addPopup(iPlayer)

  # --------------------------------

# Next Unit after NetMessage
def doGoToNextUnit(pUnit):
    # go to and select next Unit
    pUnit.getGroup().pushMission (MissionTypes.MISSION_SKIP,0,0,0,False,False,MissionAITypes.NO_MISSIONAI,pUnit.plot(),pUnit)

def copyName(NewUnit, iUnitType, sUnitName):
    if sUnitName != gc.getUnitInfo(iUnitType).getText():
        sUnitName = re.sub(" \(.*?\)","",sUnitName)
        NewUnit.setName(sUnitName)

def initSupply(pUnit):
    (_, iMaxSupply) = getSupply(pUnit)
    setSupply(pUnit,iMaxSupply)

def fillSupply(pUnit, iChange):
    (iCurrentSupply, iMaxSupply) = getSupply(pUnit)
    if iCurrentSupply != iMaxSupply:
        if iCurrentSupply + iChange > iMaxSupply:
            iChange -= (iMaxSupply - iCurrentSupply)
            iCurrentSupply = iMaxSupply
        else:
            iCurrentSupply += iChange
            iChange = 0

    setSupply(pUnit,iCurrentSupply)
    return iChange

def setSupply(pUnit,iValue):
    CvUtil.addScriptData(pUnit,"s",iValue)

def getSupply(pUnit):
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

    # kein Eintrag == Fabrikneu
    iCurrentSupply = CvUtil.getScriptData(pUnit, ["s"], iMaxSupply)
    if iCurrentSupply > iMaxSupply:
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Current Supply is bogus",iCurrentSupply)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        setSupply(pUnit, iMaxSupply)
        iCurrentSupply = iMaxSupply
    return (iCurrentSupply, iMaxSupply)