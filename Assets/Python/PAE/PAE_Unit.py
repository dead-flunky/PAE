### Imports
from CvPythonExtensions import *
import random

### Defines
gc = CyGlobalContext()
    
def myRandom (num):
      if num <= 1: return 0
      else: return random.randint(0, num-1)
      

      

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
    pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)            
      
      
      
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
