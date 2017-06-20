# Trade and Cultivation feature
# From BoggyB

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil

import PAE_Unit
import PAE_Trade
### Defines
gc = CyGlobalContext()

### Globals
lCorn = [] # Lists of cultivatable bonuses
lLivestock = []
lPlantation = []
lCultivatable = [] # = lCorn + lLivestock + lPlantation + BONUS_HORSE
lCultivationUnits = [] # List of cultivation units
bInitialized = False # Whether global variables are already initialised

# Reminder: How to use ScriptData: CvUtil.getScriptData(pUnit, ["b"], -1), CvUtil.addScriptData(pUnit, "b", eBonus) (add uses string, get list of strings)
# getScriptData returns string => cast might be necessary
# Update (Ramk): No, CvUtil-Functions unpack an dict. You could directly use int, etc.

# Used keys for UnitScriptData:
# "b": index of bonus stored in merchant/cultivation unit (only one at a time)

def init():
    global bInitialized
    global lCorn
    global lLivestock
    global lCultivatable
    global lPlantation
    global lCultivationUnits

    if not bInitialized:
        # BonusClass indices
        eGrain = gc.getInfoTypeForString("BONUSCLASS_GRAIN")
        # WHEAT, GERSTE, HAFER, ROGGEN, HIRSE, RICE
        eLivestock = gc.getInfoTypeForString("BONUSCLASS_LIVESTOCK")
        # COW, PIG, SHEEP
        ePlantation = gc.getInfoTypeForString("BONUSCLASS_PLANTATION")
        # GRAPES, OLIVES, DATTELN

        iNumBonuses = gc.getNumBonusInfos()
        for eBonus in range(iNumBonuses):
            pBonusInfo = gc.getBonusInfo(eBonus)
            iClass = pBonusInfo.getBonusClassType()
            if iClass == eGrain:
                lCorn.append(eBonus)
            elif iClass == eLivestock:
                lLivestock.append(eBonus)
            elif iClass == ePlantation:
                lPlantation.append(eBonus)

        lCultivatable = lCorn + lLivestock + lPlantation + [gc.getInfoTypeForString("BONUS_HORSE")]

        lCultivationUnits = [gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")]

        bInitialized = True


def _getCitiesInRange(pPlot, iPlayer):
    iX = pPlot.getX()
    iY = pPlot.getY()
    lCities = []
    iRange = 2
    for x in range(-iRange, iRange+1):
        for y in range(-iRange, iRange+1):
            # Ecken weglassen
            if (x == -2 or x == 2) and (y == -2 or y == 2):
                continue
            pLoopPlot = plotXY(iX, iY, x, y)
            if pLoopPlot is not None and not pLoopPlot.isNone():
                #if (iPlayer == -1 or pLoopPlot.getOwner() == iPlayer) and pLoopPlot.isCity():
                if pLoopPlot.getOwner() == iPlayer and pLoopPlot.isCity():
                    lCities.append(pLoopPlot.getPlotCity())
    return lCities

def _isCityCultivationPossible(pCity):

    iMax = getCityCultivationAmount(pCity)
    iBonusAnzahl = getCityCultivatedBonuses(pCity)

    return iBonusAnzahl < iMax

def getCityCultivationAmount(pCity):
    if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_METROPOLE")):
        iAnz = 4
    elif pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_PROVINZ")):
        iAnz = 3
    elif pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STADT")):
        iAnz = 2
    else: 
        iAnz = 1
    return iAnz

def getCityCultivatedBonuses(pCity):

    iAnz = 0
    for i in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(i)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            iLoopBonus = pLoopPlot.getBonusType(-1)
            if iLoopBonus in lCultivatable:
                iAnz += 1
    return iAnz


def _isBonusCultivationChance(iPlayer, pPlot, eBonus, bVisibleOnly=True):
    """Returns chance to cultivate eBonus on pPlot. Currently: either 0 (impossible) or 80 (possible)
        bVisibleOnly: Non-cultivatable bonuses cannot be replaced. If there is an invisible (tech reveal) bonus on pPlot, player receives NO information.
        In particular, the normal cultivation chance will be displayed, but bVisibleOnly=False prevents invisible bonus from removal.
    """
    # Variety of invalid situations
    if (eBonus not in lCultivatable
        or pPlot is None or pPlot.isNone()
        or pPlot.getOwner() != iPlayer
        or pPlot.isCity()
        or pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_DARK_ICE") or pPlot.isPeak() or pPlot.isWater()):
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "peak/water/black ice", None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    eTeam = -1
    if bVisibleOnly:
        eTeam = pPlot.getTeam()
    ePlotBonus = pPlot.getBonusType(eTeam)
    if ePlotBonus != -1 and (ePlotBonus not in lCultivatable or ePlotBonus == eBonus):
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "uncultivatable bonus present", None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    # Fertility conditions
    if (not canHaveBonus(pPlot, eBonus, True)
        # or (eBonus in lCorn and not pPlot.isFreshWater()) # siehe https://www.civforum.de/showthread.php?97599-PAE-Bonusressourcen&p=7653686&viewfull=1#post7653686
        or (eBonus in lPlantation and 
            (eBonus == gc.getInfoTypeForString("BONUS_DATTELN") and not pPlot.isFreshWater())
            or (eBonus == gc.getInfoTypeForString("BONUS_OLIVES") and not pPlot.isCoastalLand())
            or (eBonus == gc.getInfoTypeForString("BONUS_GRAPES") and not pPlot.isFreshWater()))):
            return False

    # Regel: Resourcen pro Stadt und dessen Status (Flunky)
    lCities = _getCitiesInRange(pPlot, iPlayer)
    for pCity in lCities:
        if _isCityCultivationPossible(pCity):
            return True

    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "no city in range has capacity", None, 2, None, ColorTypes(10), 0, 0, False, False)
    return False

def canHaveBonus(pPlot, eBonus, bIgnoreLatitude):
    """Variation of the SDK version of the same name. Allows cultivation of ressources also if a non-fitting, removable feature is still on the plot (i.e. forest for wheat)"""
    if eBonus == -1:
        return True

    # ## ist hier schon was?
    # if pPlot.getBonusType() != -1:
        # return False
    ## Gipfel
    if pPlot.isPeak():
        return False
    ## wenn die Ressource auf Hügeln vorkommen muss
    if pPlot.isHills():
        if not gc.getBonusInfo(eBonus).isHills():
            return False
    ## xor auf Flachland
    elif pPlot.isFlatlands():
        if  not gc.getBonusInfo(eBonus).isFlatlands():
            return False
    ## Falls die Ressource [B]nicht[/B] am Flussufer vorkommen darf
    if gc.getBonusInfo(eBonus).isNoRiverSide():
        if pPlot.isRiverSide():
            return False

    ## Ist die Insel groß genug
    if gc.getBonusInfo(eBonus).getMinAreaSize() != -1:
        if pPlot.area().getNumTiles() < gc.getBonusInfo(eBonus).getMinAreaSize():
            return False
     ## Breitengrad
    if not bIgnoreLatitude:
        if pPlot.getLatitude() > gc.getBonusInfo(eBonus).getMaxLatitude():
            return False
        if pPlot.getLatitude() < gc.getBonusInfo(eBonus).getMinLatitude():
            return False
    ## Von einem Landplot erreichbar? Nimmt keine Rücksicht auf Gipfel oder sonstige Landfelder, auf denen man nicht gründen kann.
    if not pPlot.isPotentialCityWork():
        return False
    ## Ein Feature ist vorhanden
    if pPlot.getFeatureType() != -1:
        ## dann muss das Feature zugelassen sein und das Terrain drunter auch
        if gc.getBonusInfo(eBonus).isFeature(pPlot.getFeatureType()):
            if gc.getBonusInfo(eBonus).isFeatureTerrain(pPlot.getTerrainType()):
                return True
    ## aber wenn das Terrain passt, reicht das auch
    if gc.getBonusInfo(eBonus).isTerrain(pPlot.getTerrainType()):
        return True

    return False  

def doCultivateBonus(pPlot, pUnit, eBonus):
    """Cultivates eBonus on current plot (80% chance). Unit does not need to stand on pPlot (cultivation from city)"""
    if pPlot is None or pUnit is None or eBonus == -1:
        return False

    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    bOnlyVisible = False
    bCanCultivate = _isBonusCultivationChance(iPlayer, pPlot, eBonus, bOnlyVisible)
    iChance = 80
    #CyInterface().addMessage(iPlayer, True, 10, str(eBonus), None, 2, None, ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
    if bCanCultivate:
        if CvUtil.myRandom(100) < iChance:
            pPlot.setBonusType(eBonus)
            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_DONE", (gc.getBonusInfo(eBonus).getDescription(),)), None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(8), pPlot.getX(), pPlot.getY(), True, True)
            pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        else:
            CvUtil.removeScriptData(pUnit, "b")
            if pPlayer.isHuman():
                if pPlot.isCity():
                    pCity = pPlot.getPlotCity()
                else:
                    pCity = pPlot.getWorkingCity()
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_INFO_BONUSVERBREITUNG_NEG", (gc.getBonusInfo(eBonus).getDescription(), pCity.getName())), None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            pUnit.finishMoves()
            PAE_Unit.doGoToNextUnit(pUnit)
    return bCanCultivate


def getCityCultivationPlot(pCity, eBonus):
    """Cultivates eBonus on random plot within radius of iRange around pUnit (chance of success: 80%).
       Never replaces existing bonus.
    """
    iPlayer = pCity.getOwner()
    lPlotList = []
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            ePlotBonus = pLoopPlot.getBonusType(-1)
            if ePlotBonus == -1 and _isBonusCultivationChance(iPlayer, pLoopPlot, eBonus, False):
                lPlotList.append(pLoopPlot)

    if lPlotList:
        return lPlotList[CvUtil.myRandom(len(lPlotList))]
    return None

# Returns list of bonuses which can be cultivated by this particular cultivation unit
# Checks fertility conditions AND unit store
# if iIsCity == 1, 5x5 square is checked. Otherwise: Only current plot.
def isBonusCultivatable(pUnit):
    if not pUnit.getUnitType() in lCultivationUnits:
        return False

    eBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
    if eBonus == -1:
        return False

    pPlot = pUnit.plot()
    if pPlot.isCity():
        # Cultivation from city (comfort function), no replacement of existing bonuses
        return _bonusIsCultivatableFromCity(pUnit.getOwner(), pPlot.getPlotCity(), eBonus)
    else:
        # Cultivation on current plot, bonus can be replaced (player knows what he's doing)
        return _isBonusCultivationChance(pUnit.getOwner(), pPlot, eBonus)

# Returns True if eBonus can be (principally) cultivated by iPlayer from pCity
# Independent from cultivation unit, only checks fertility conditions
def _bonusIsCultivatableFromCity(iPlayer, pCity, eBonus, bVisibleOnly=True):
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            ePlotBonus = pLoopPlot.getBonusType(-1)
            if ePlotBonus == -1 and _isBonusCultivationChance(iPlayer, pLoopPlot, eBonus, bVisibleOnly):
                return True
    return False


# returns best plot within city radius
def AI_bestCultivation(pCity, iSkipN=-1, eBonus=-1):
    iPlayer = pCity.getOwner()
    if eBonus != -1:
        for iPass in range(2):
            for iI in range(gc.getNUM_CITY_PLOTS()):
                pLoopPlot = pCity.getCityIndexPlot(iI)
                if pLoopPlot is not None and not pLoopPlot.isNone():
                    ePlotBonus = pLoopPlot.getBonusType(pLoopPlot.getTeam())
                    eImprovement = pLoopPlot.getImprovementType()
                    bAlreadyImproved = False
                    if eImprovement != -1 and gc.getImprovementInfo(eImprovement).isImprovementBonusTrade(eBonus): bAlreadyImproved = True
                    # first pass: only plots without bonus or its improvement
                    if ePlotBonus == -1 or bAlreadyImproved or iPass > 0:
                        # second pass: no improved plots or matching improved plots
                        if eImprovement == -1 or bAlreadyImproved or iPass > 0:
                            if _isBonusCultivationChance(iPlayer, pLoopPlot, eBonus):
                                if iSkipN > 0:
                                    iSkipN -= 1
                                    continue
                                if iSkipN <= 0:
                                    return pLoopPlot
    else:
        return None
        # TODO: find overall best plot, i.e. prefer food and rare resources

# Lets pUnit cultivate bonus at nearest city
def doCultivation_AI(pUnit):

    if not pUnit.getUnitType() in lCultivationUnits:
        return False

    lFood = lCorn+lLivestock

    pUnitPlot = pUnit.plot()
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)

    lLocalCityBonuses = []
    pLocalCity = None
    if pUnitPlot.isCity() and iPlayer == pUnitPlot.getOwner():
        pLocalCity = pUnitPlot.getPlotCity()
        lLocalCityBonuses = _getCollectableGoods4Cultivation(pLocalCity)

    lCities = []
    # list of player's cities with distance (2-tuples (distance, city))
    # The nearest city which can still cultivate a bonus is chosen.
    (loopCity, pIter) = pPlayer.firstCity(False)
    while loopCity:
        iValue = 0
        pCityPlot = loopCity.plot()
        iDistance = CyMap().calculatePathDistance(pUnitPlot, pCityPlot)
        # exclude unreachable cities
        if iDistance != -1:
            if _isCityCultivationPossible(loopCity):
                if iDistance == 0:
                    iValue = 2
                else:
                    iValue = 1/iDistance
        if iValue != 0:
            lCities.append((iValue, loopCity))
        (loopCity, pIter) = pPlayer.nextCity(pIter, False)


    lSortedCities = sorted(lCities, key=lambda value: lCities[0], reverse=True)
    bDiscard = False
    for tTuple in lSortedCities:
        pLoopCity = tTuple[1]
        lCityBonuses = _getCollectableGoods4Cultivation(pLoopCity) # bonuses that city has access to
        # bonuses for which fertility conditions are met
        lBonuses = []
        for eBonus in lCityBonuses+lLocalCityBonuses:
            if _bonusIsCultivatableFromCity(iPlayer, pLoopCity, eBonus, False):
                lBonuses.append(eBonus)
        # has this city capacity to cultivate?
        # prefer food if possible
        lFoodIntersect = CvUtil.getIntersection(lBonuses, lFood)
        if lFoodIntersect:
            lBonuses = lFoodIntersect

        # kauf was, das es hier gibt und dort gebraucht wird und los geht's
        for eBonus in lBonuses:
            iLocalPrice = -1
            iPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iPlayer,pLoopCity.plot())
            if eBonus in lLocalCityBonuses:
                iLocalPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iPlayer,pLocalCity.plot())
            if iLocalPrice != -1 and iLocalPrice <= iPrice:
                #buy here. wait if not enough money
                doBuyBonus4Cultivation(pUnit,eBonus)
                pUnit.finishMoves()
                return True
            elif iPrice != -1:
                # move to destination
                pUnit.getGroup().pushMoveToMission(pLoopCity.getX(), pLoopCity.getY())
                return True

    # TODO get a ship
    return False

  #~ # Bonusverbreitung -------------------
  #~ # Schritt 1: Bonus verbreiten
  #~ # Schritt 2: Stadt mit Getreide fuellen
  #~ def doBonusverbreitung_AI (  pUnit ):
    #~ pUnitGroup = pUnit.getGroup()

    #~ if pUnitGroup.getMissionType(0) != 0:
      #~ # Inits
      #~ iOwner = pUnit.getOwner( )
      #~ pOwner = gc.getPlayer(iOwner)
      #~ lCities = PyPlayer(iOwner).getCityList()
      #~ iCities = len(lCities)
      #~ pPlot = pUnit.plot()

      #~ # Boni
      #~ lBonuses = []
      #~ # Gruppe 1
      #~ a1 = gc.getInfoTypeForString("BONUS_WHEAT")
      #~ a2 = gc.getInfoTypeForString("BONUS_GERSTE")
      #~ a3 = gc.getInfoTypeForString("BONUS_HAFER")
      #~ a4 = gc.getInfoTypeForString("BONUS_ROGGEN")
      #~ a5 = gc.getInfoTypeForString("BONUS_HIRSE")
      #~ a6 = gc.getInfoTypeForString("BONUS_RICE")
      #~ a1sum = pOwner.getNumAvailableBonuses(a1)
      #~ a2sum = pOwner.getNumAvailableBonuses(a2)
      #~ a3sum = pOwner.getNumAvailableBonuses(a3)
      #~ a4sum = pOwner.getNumAvailableBonuses(a4)
      #~ a5sum = pOwner.getNumAvailableBonuses(a5)
      #~ a6sum = pOwner.getNumAvailableBonuses(a6)
      #~ lBonuses.append(a1)
      #~ lBonuses.append(a2)
      #~ lBonuses.append(a3)
      #~ lBonuses.append(a4)
      #~ lBonuses.append(a5)
      #~ lBonuses.append(a6)
      #~ # Gruppe 2
      #~ b1 = gc.getInfoTypeForString("BONUS_COW")
      #~ b2 = gc.getInfoTypeForString("BONUS_PIG")
      #~ b3 = gc.getInfoTypeForString("BONUS_SHEEP")
      #~ b1sum = pOwner.getNumAvailableBonuses(b1)
      #~ b2sum = pOwner.getNumAvailableBonuses(b2)
      #~ b3sum = pOwner.getNumAvailableBonuses(b3)
      #~ lBonuses.append(b1)
      #~ lBonuses.append(b2)
      #~ lBonuses.append(b3)
      #~ # Gruppe 3
      #~ c1 = gc.getInfoTypeForString("BONUS_OLIVES")
      #~ c2 = gc.getInfoTypeForString("BONUS_DATTELN")
      #~ c1sum = pOwner.getNumAvailableBonuses(c1)
      #~ c2sum = pOwner.getNumAvailableBonuses(c2)
      #~ lBonuses.append(c1)
      #~ lBonuses.append(c2)
      #~ # Gruppe 4
      #~ d1 = gc.getInfoTypeForString("BONUS_CAMEL")
      #~ d1sum = pOwner.getNumAvailableBonuses(d1)
      #~ lBonuses.append(d1)

      #~ # Hat die KI Boni zum Verbreiten?
      #~ # Eigene Liste der Boni fuer die KI fuer schneller Abfragen
      #~ lAIBonuses = []
      #~ iRange = len(lBonuses)
      #~ for i in range (iRange):
        #~ if pOwner.getNumAvailableBonuses(lBonuses[i]) > 0:
          #~ lAIBonuses.append(lBonuses[i])

      #~ if len(lAIBonuses): bAIHasBonus = True
      #~ else: bAIHasBonus = False

      #~ # -------

      #~ # --- Zuerst diese Stadt checken
      #~ pThisPlotCity = None
      #~ if bAIHasBonus and pPlot.isCity():
        #~ # Inits
        #~ pThisPlotCity = pPlot.getPlotCity()
        #~ lNewBonus = []

        #~ # Moegliche Boni
        #~ iRange = len(lAIBonuses)
        #~ i=0
        #~ for i in range (iRange):
          #~ seekPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pThisPlotCity, lAIBonuses[i])
          #~ if seekPlot is not None and not seekPlot.isNone():

            #~ iBonusHier = seekPlot.getBonusType(iOwner)
            #~ # Unerforschte Resource?
            #~ if iBonusHier == -1: iBonusHier = seekPlot.getBonusType(-1)

            #~ # kein gleiches Bonusgut
            #~ if iBonusHier != lAIBonuses[i]:
              #~ # kein Bonusgut => fix dabei
              #~ if iBonusHier == -1: lNewBonus.append(lAIBonuses[i])
              #~ else:
                #~ # Boni der selben Gruppe herausfinden und vergleichen
                #~ if lAIBonuses[i] == a1:
                  #~ if a1sum+1 < a2sum and a2sum > 1 or a1sum+1 < a3sum and a3sum > 1 or a1sum+1 < a4sum and a4sum > 1 or a1sum+1 < a5sum and a5sum > 1 or a1sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a2:
                  #~ if a2sum+1 < a1sum and a1sum > 1 or a2sum+1 < a3sum and a3sum > 1 or a2sum+1 < a4sum and a4sum > 1 or a2sum+1 < a5sum and a5sum > 1 or a2sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a3:
                  #~ if a3sum+1 < a1sum and a1sum > 1 or a3sum+1 < a2sum and a2sum > 1 or a3sum+1 < a4sum and a4sum > 1 or a3sum+1 < a5sum and a5sum > 1 or a3sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a4:
                  #~ if a4sum+1 < a1sum and a1sum > 1 or a4sum+1 < a2sum and a2sum > 1 or a4sum+1 < a3sum and a3sum > 1 or a4sum+1 < a5sum and a5sum > 1 or a4sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a5:
                  #~ if a5sum+1 < a1sum and a1sum > 1 or a5sum+1 < a2sum and a2sum > 1 or a5sum+1 < a3sum and a3sum > 1 or a5sum+1 < a4sum and a4sum > 1 or a5sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a6:
                  #~ if a6sum+1 < a1sum and a1sum > 1 or a6sum+1 < a2sum and a2sum > 1 or a6sum+1 < a3sum and a3sum > 1 or a6sum+1 < a4sum and a4sum > 1 or a6sum+1 < a5sum and a5sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b1:
                  #~ if b1sum+1 < b2sum and b2sum > 1 or b1sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b2:
                  #~ if b2sum+1 < b1sum and b1sum > 1 or b2sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b3:
                  #~ if b3sum+1 < b1sum and b1sum > 1 or b3sum+1 < b2sum and b2sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == c1:
                  #~ if c1sum+1 < c2sum and c2sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == c2:
                  #~ if c2sum+1 < c1sum and c1sum > 1: lNewBonus.append(lAIBonuses[i])


        #~ # Wenn leer, dann gehts unten weiter (Stadt suchen)
        #~ if len(lNewBonus):
          #~ iRand = CvUtil.myRandom(len(lNewBonus))
          #~ iBonus = lNewBonus[iRand]

          #~ # Bonus verbreiten (aber nicht, wenn dieses bereits auf dem Plot ist)
          #~ if iBonus > -1:
              #~ loopPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pThisPlotCity, iBonus)
              #~ if loopPlot is not None and not loopPlot.isNone() and loopPlot.getBonusType(iOwner) != iBonus:

                #~ ### TEST ###
                #~ #CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iY",loopPlot.getY())), None, 2, None, ColorTypes(12), 0, 0, False, False)
                #~ #CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iX",loopPlot.getX())), None, 2, None, ColorTypes(12), 0, 0, False, False)

                #~ # KI 10% mehr Chance
                #~ if CvUtil.myRandom(100) < iChance + 10:
                  #~ loopPlot.setBonusType(iBonus)
                #~ pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                #~ return True

      #~ # --- Stadt gecheckt


      #~ # Alle moeglichen Staedte durchsuchen
      #~ pSeekCity = None
      #~ pSeekCityList = []
      #~ pSeekCity2 = None
      #~ iSeek2 = 0
      #~ iAIBoni = len(lAIBonuses)

      #~ # Check 1: Anzahl der bereits zugewiesenen Boni pro Stadt
      #~ # Check 2: Foodstorage
      #~ for iCity in range(iCities):
        #~ pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
        #~ bCheck = True

        #~ if pThisPlotCity is not None and not pThisPlotCity.isNone():
          #~ if pCity.getID() == pThisPlotCity.getID():
              #~ bCheck = False

        #~ # 1: BONUS
        #~ # anfangs leere Liste StadtBoni (falls eine stadt 2 gleiche boni hat)
        #~ if bAIHasBonus and bCheck:
          #~ lNewBonus = []
          #~ i=0
          #~ for i in range (iAIBoni):
            #~ seekPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pCity, lAIBonuses[i])
            #~ if seekPlot is not None:

             #~ iBonusHier = seekPlot.getBonusType(iOwner)
             #~ # Unerforschte Resource?
             #~ if iBonusHier == -1: iBonusHier = seekPlot.getBonusType(-1)

             #~ # kein gleiches Bonusgut
             #~ if iBonusHier != lAIBonuses[i]:
              #~ # kein Bonusgut => fix dabei
              #~ if iBonusHier == -1: lNewBonus.append(lAIBonuses[i])
              #~ else:
                #~ # Boni der selben Gruppe herausfinden und vergleichen
                #~ if lAIBonuses[i] == a1:
                  #~ if a1sum+1 < a2sum and a2sum > 1 or a1sum+1 < a3sum and a3sum > 1 or a1sum+1 < a4sum and a4sum > 1 or a1sum+1 < a5sum and a5sum > 1 or a1sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a2:
                  #~ if a2sum+1 < a1sum and a1sum > 1 or a2sum+1 < a3sum and a3sum > 1 or a2sum+1 < a4sum and a4sum > 1 or a2sum+1 < a5sum and a5sum > 1 or a2sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a3:
                  #~ if a3sum+1 < a1sum and a1sum > 1 or a3sum+1 < a2sum and a2sum > 1 or a3sum+1 < a4sum and a4sum > 1 or a3sum+1 < a5sum and a5sum > 1 or a3sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a4:
                  #~ if a4sum+1 < a1sum and a1sum > 1 or a4sum+1 < a2sum and a2sum > 1 or a4sum+1 < a3sum and a3sum > 1 or a4sum+1 < a5sum and a5sum > 1 or a4sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a5:
                  #~ if a5sum+1 < a1sum and a1sum > 1 or a5sum+1 < a2sum and a2sum > 1 or a5sum+1 < a3sum and a3sum > 1 or a5sum+1 < a4sum and a4sum > 1 or a5sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == a6:
                  #~ if a6sum+1 < a1sum and a1sum > 1 or a6sum+1 < a2sum and a2sum > 1 or a6sum+1 < a3sum and a3sum > 1 or a6sum+1 < a4sum and a4sum > 1 or a6sum+1 < a5sum and a5sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b1:
                  #~ if b1sum+1 < b2sum and b2sum > 1 or b1sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b2:
                  #~ if b2sum+1 < b1sum and b1sum > 1 or b2sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == b3:
                  #~ if b3sum+1 < b1sum and b1sum > 1 or b3sum+1 < b2sum and b2sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == c1:
                  #~ if c1sum+1 < c2sum and c2sum > 1: lNewBonus.append(lAIBonuses[i])
                #~ elif lAIBonuses[i] == c2:
                  #~ if c2sum+1 < c1sum and c1sum > 1: lNewBonus.append(lAIBonuses[i])

          #~ if len(lNewBonus):
            #~ pSeekCityList.append(pCity)


        #~ # 2: FOOD Storage
        #~ iFood = pCity.getFood()
        #~ if iSeek2 > iFood or iSeek2 == 0:
          #~ pSeekCity2 = pCity
          #~ iSeek2 = iFood


      #~ # Stadt fuer die Verbreitung auswaehlen
      #~ if len(pSeekCityList) > 0:
        #~ iRand = CvUtil.myRandom(len(pSeekCityList))
        #~ pSeekCity = pSeekCityList[iRand]


      #~ # Schritt 1: Bonus verbreiten
      #~ # Es gibt maximal 4 Plots zu bewirtschaften
      #~ if pSeekCity is not None and not pSeekCity.isNone():
        #~ pCity = pSeekCity

        #~ # Stadt aufsuchen
        #~ if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
          #~ pUnitGroup.clearMissionQueue()
          #~ pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
          #~ return True

      #~ # Schritt 2: Stadt mit Getreide fuellen
      #~ if pSeekCity2 is not None and not pSeekCity2.isNone():
        #~ pCity = pSeekCity2

        #~ # Stadt aufsuchen
        #~ if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
          #~ pUnitGroup.clearMissionQueue()
          #~ pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)

        #~ # Stadt mit Getreide auffuellen
        #~ else:
          #~ pCity.changeFood(50)
          #~ pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
          #~ return True

    #~ return


# Collect bonus on current plot ('stored' in cultivation unit)
def doCollectBonus4Cultivation(pUnit):
    iTeam = pUnit.getTeam()
    pPlot = pUnit.plot()
    eBonus = pPlot.getBonusType(iTeam) # If there is an invisible bonus on pPlot, it will not be removed
    if eBonus == -1:
        return False

    if eBonus not in lCultivatable:
        return False

    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eUnitBonus != -1:
        # TODO: Popup Ressource geladen, ueberschreiben?
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hatte bereits eine Ressource geladen. Die ist jetzt futsch.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    CvUtil.addScriptData(pUnit, "b", eBonus)
    pPlot.setBonusType(-1) # remove bonus

    # Handelsposten auch entfernen
    lImprovements = []
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"))
    lImprovements.append(gc.getInfoTypeForString("IMPROVEMENT_PASTURE"))
    if pPlot.getImprovementType() in lImprovements: pPlot.setImprovementType(-1)

    pUnit.finishMoves()
    return True

# List of selectable cultivation goods
def getCollectableGoods4Cultivation(pUnit):
    pPlot = pUnit.plot()
    if pPlot.isCity():
        pCity = pPlot.getPlotCity()
        lGoods = _getCollectableGoods4Cultivation(pCity)
    else:
        ePlotBonus = pPlot.getBonusType(pPlot.getTeam())
        if ePlotBonus != -1 and ePlotBonus in lCultivatable: lGoods = [ePlotBonus]

    return lGoods

    # Returns list of the cultivatable bonuses which pCity has access to / Liste kultivierbarer Ressis im Handelsnetz von pCity
def _getCollectableGoods4Cultivation(pCity):
    lGoods = []
    for eBonus in lCultivatable:
        if pCity.hasBonus(eBonus): lGoods.append(eBonus)
    return lGoods


# Price of cultivation goods
# regional (on plot): *1
# national: *2
# international: *3
def _calculateBonusBuyingPrice4Cultivation(eBonus, iBuyer, pPlot):

    iPrice = PAE_Trade.getBonusValue(eBonus)
    pCity = pPlot.getPlotCity()
    if pCity is None:
        # Bonus on plot: regional price
        if pPlot.getBonusType(pPlot.getTeam()) == eBonus:
            return iPrice
        else:
            return -1

    if not pCity.hasBonus(eBonus):
        return -1

    # Bonus in city radius: regional price
    for iI in range(gc.getNUM_CITY_PLOTS()):
        pLoopPlot = pCity.getCityIndexPlot(iI)
        if pLoopPlot is not None and not pLoopPlot.isNone():
            if pLoopPlot.getBonusType(pLoopPlot.getTeam()) == eBonus:
                return iPrice

    # Bonus in realm: national price
    iRange = CyMap().numPlots()
    for iI in range(iRange):
        pLoopPlot = CyMap().plotByIndex(iI)
        if pLoopPlot.getOwner() == iBuyer:
            if pLoopPlot.getBonusType(pLoopPlot.getTeam()) == eBonus:
                return iPrice * 2

    # Bonus international
    return iPrice * 3


def doBuyBonus4Cultivation(pUnit, eBonus):
    if not pUnit.getUnitType() in lCultivationUnits:
        return
    if eBonus == -1:
        return

    iBuyer = pUnit.getOwner()

    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eBonus == eUnitBonus:
        #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Das haben wir bereits geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return
    if eUnitBonus != -1:
        # TODO: Popup Ressource geladen, ueberschreiben?
        #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hat bereits eine Ressource geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return

    iPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iBuyer, pUnit.plot())
    if iPrice == -1:
        return

    pBuyer = gc.getPlayer(iBuyer)
    if pBuyer.getGold() < iPrice:
        CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS", ("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
        return

    pBuyer.changeGold(-iPrice)
    CvUtil.addScriptData(pUnit, "b", eBonus)

    if pBuyer.isHuman():
        CyInterface().addMessage(iBuyer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS", (gc.getBonusInfo(eBonus).getDescription(), -iPrice)), "AS2D_COINS", 2, None, ColorTypes(13), pUnit.getX(), pUnit.getY(), False, False)

    pUnit.finishMoves()
    PAE_Unit.doGoToNextUnit(pUnit)

# Creates popup with all possible cultivation bonuses of the plot or city
def doPopupChooseBonus4Cultivation(pUnit):
    if pUnit is None or pUnit.isNone():
        return False
    pPlot = pUnit.plot()
    iPlayer = pUnit.getOwner()

    lGoods = getCollectableGoods4Cultivation(pUnit)

    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_CHOOSE_BONUS", ("", )))
    popupInfo.setOnClickedPythonCallback("popupTradeChooseBonus4Cultivation")
    popupInfo.setData1(iPlayer)
    popupInfo.setData2(pUnit.getID())

    for eBonus in lGoods:
        sBonusDesc = gc.getBonusInfo(eBonus).getDescription()
        iPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iPlayer, pPlot)
        sText = CyTranslator().getText("TXT_KEY_BUY_BONUS", (sBonusDesc, iPrice))
        sBonusButton = gc.getBonusInfo(eBonus).getButton()
        popupInfo.addPythonButton(sText, sBonusButton)

    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
    popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
    popupInfo.addPopup(iPlayer)
