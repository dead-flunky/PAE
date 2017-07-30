# Trade and Cultivation feature
# From BoggyB

### Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil

import PAE_Unit
import PAE_Trade
import PAE_Lists as L
### Defines
gc = CyGlobalContext()

# Update (Ramk): CvUtil-Functions unpack an dict. You could directly use int, etc.
# Used keys for UnitScriptData:
# "b": index of bonus stored in merchant/cultivation unit (only one at a time)

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
            if iLoopBonus in L.LBonusCultivatable:
                iAnz += 1
    return iAnz


def _isBonusCultivationChance(iPlayer, pPlot, eBonus, bVisibleOnly=True):
    """
        Returns chance to cultivate eBonus on pPlot. Currently: either 0 (impossible) or 80 (possible)
        bVisibleOnly: Non-cultivatable bonuses cannot be replaced. If there is an invisible (tech reveal) bonus on pPlot, player receives NO information.
        In particular, the normal cultivation chance will be displayed, but bVisibleOnly=False prevents invisible bonus from removal.
    """
    # Variety of invalid situations
    if (eBonus not in L.LBonusCultivatable
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
    if ePlotBonus != -1 and (ePlotBonus not in L.LBonusCultivatable or ePlotBonus == eBonus):
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "uncultivatable bonus present", None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    # Fertility conditions
    if (not canHaveBonus(pPlot, eBonus, True)
            # or (eBonus in L.LBonusCorn and not pPlot.isFreshWater()) # siehe https://www.civforum.de/showthread.php?97599-PAE-Bonusressourcen&p=7653686&viewfull=1#post7653686
            or (eBonus in L.LBonusPlantation and
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
    ## wenn die Ressource auf Huegeln vorkommen muss
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

    ## Ist die Insel gross genug
    if gc.getBonusInfo(eBonus).getMinAreaSize() != -1:
        if pPlot.area().getNumTiles() < gc.getBonusInfo(eBonus).getMinAreaSize():
            return False
     ## Breitengrad
    if not bIgnoreLatitude:
        if pPlot.getLatitude() > gc.getBonusInfo(eBonus).getMaxLatitude():
            return False
        if pPlot.getLatitude() < gc.getBonusInfo(eBonus).getMinLatitude():
            return False
    ## Von einem Landplot erreichbar? Nimmt keine Ruecksicht auf Gipfel oder sonstige Landfelder, auf denen man nicht gruenden kann.
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
        if CvUtil.myRandom(100, "doCultivateBonus") < iChance:
            pPlot.setBonusType(eBonus)
            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_BONUSVERBREITUNG_DONE", (gc.getBonusInfo(eBonus).getDescription(),)), None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(8), pPlot.getX(), pPlot.getY(), True, True)
            # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit.kill(True, -1)  # RAMK_CTD
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
    """
        Cultivates eBonus on random plot within radius of iRange around pUnit (chance of success: 80%).
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
        return lPlotList[CvUtil.myRandom(len(lPlotList), "getCityCultivationPlot")]
    return None

# Returns list of bonuses which can be cultivated by this particular cultivation unit
# Checks fertility conditions AND unit store
# if iIsCity == 1, 5x5 square is checked. Otherwise: Only current plot.
def isBonusCultivatable(pUnit):
    if not pUnit.getUnitType() in L.LCultivationUnits:
        return False

    eBonus = int(CvUtil.getScriptData(pUnit, ["b"], -1))
    if eBonus == -1:
        return False

    pPlot = pUnit.plot()
    if pPlot.isCity():
        # Cultivation from city (comfort function), no replacement of existing bonuses
        return _bonusIsCultivatableFromCity(pUnit.getOwner(), pPlot.getPlotCity(), eBonus)
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
                    if eImprovement != -1 and gc.getImprovementInfo(eImprovement).isImprovementBonusTrade(eBonus):
                        bAlreadyImproved = True
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

    pUnitPlot = pUnit.plot()
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    eBonusOnBoard = CvUtil.getScriptData(pUnit, ["b"], -1)

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
    lFood = L.LBonusCorn+L.LBonusLivestock

    for iTry in range(2):
        for tTuple in lSortedCities:
            pLoopCity = tTuple[1]
            if eBonusOnBoard != -1:
                if _bonusIsCultivatableFromCity(iPlayer, pLoopCity, eBonusOnBoard, False):
                    if pUnit.atPlot(pLoopCity.plot()):
                        pPlot = getCityCultivationPlot(pLocalCity, eBonusOnBoard)
                        doCultivateBonus(pPlot, pUnit, eBonusOnBoard)
                    else:
                        pUnit.getGroup().pushMoveToMission(pLoopCity.getX(), pLoopCity.getY())
                    return True
            else:
                lCityBonuses = _getCollectableGoods4Cultivation(pLoopCity) # bonuses that city has access to
                # bonuses for which fertility conditions are met
                lBonuses = []
                for eBonus in lCityBonuses+lLocalCityBonuses:
                    # has this city capacity to cultivate?
                    if _bonusIsCultivatableFromCity(iPlayer, pLoopCity, eBonus, False):
                        lBonuses.append(eBonus)
                # prefer food if possible
                lFoodIntersect = CvUtil.getIntersection(lBonuses, lFood)
                if lFoodIntersect:
                    lBonuses = lFoodIntersect

                # kauf was, das es hier gibt und dort gebraucht wird und los geht's
                for eBonus in lBonuses:
                    iLocalPrice = -1
                    iPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iPlayer, pLoopCity.plot())
                    if eBonus in lLocalCityBonuses:
                        iLocalPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iPlayer, pLocalCity.plot())
                    if iLocalPrice != -1 and iLocalPrice < iPrice:
                        #buy here. wait if not enough money
                        doBuyBonus4Cultivation(pUnit, eBonus)
                        pUnit.finishMoves()
                        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Cultivation waits for money",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                        return True
                    elif iPrice != -1:
                        # move to destination
                        pUnit.getGroup().pushMoveToMission(pLoopCity.getX(), pLoopCity.getY())
                        return True
        # if we didn't find a city which could use the loaded bonus, delete it and refund the AI
        if eBonusOnBoard != -1:
            CvUtil.removeScriptData(pUnit, "b")
            iPrice = PAE_Trade.getBonusValue(eBonusOnBoard)
            pPlayer.changeGold(iPrice)

    # TODO get a ship
    return False


# Collect bonus on current plot ('stored' in cultivation unit)
def doCollectBonus4Cultivation(pUnit):
    iTeam = pUnit.getTeam()
    pPlot = pUnit.plot()
    eBonus = pPlot.getBonusType(iTeam) # If there is an invisible bonus on pPlot, it will not be removed
    if eBonus == -1:
        return False

    if eBonus not in L.LBonusCultivatable:
        return False

    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eUnitBonus != -1:
        # TODO: Popup Ressource geladen, ueberschreiben?
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hatte bereits eine Ressource geladen. Die ist jetzt futsch.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    CvUtil.addScriptData(pUnit, "b", eBonus)
    pPlot.setBonusType(-1) # remove bonus

    # Handelsposten auch entfernen
    lImprovements = [
        gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"),
        gc.getInfoTypeForString("IMPROVEMENT_PASTURE")
    ]
    if pPlot.getImprovementType() in lImprovements:
        pPlot.setImprovementType(-1)

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
        if ePlotBonus != -1 and ePlotBonus in L.LBonusCultivatable:
            lGoods = [ePlotBonus]

    return lGoods

    # Returns list of the cultivatable bonuses which pCity has access to / Liste kultivierbarer Ressis im Handelsnetz von pCity
def _getCollectableGoods4Cultivation(pCity):
    lGoods = []
    for eBonus in L.LBonusCultivatable:
        if pCity.hasBonus(eBonus):
            lGoods.append(eBonus)
    return lGoods


def _calculateBonusBuyingPrice4Cultivation(eBonus, iBuyer, pPlot):
    """
    # Price of cultivation goods
    # regional (on plot): *1
    # national: *2
    # international: *3
    """
    iPrice = PAE_Trade.getBonusValue(eBonus)
    pCity = pPlot.getPlotCity()
    if pCity is None:
        # Bonus on plot: regional price
        if pPlot.getBonusType(pPlot.getTeam()) == eBonus:
            return iPrice
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
    if not pUnit.getUnitType() in L.LCultivationUnits:
        return False
    if eBonus == -1:
        return False

    iBuyer = pUnit.getOwner()

    eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eBonus == eUnitBonus:
        #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Das haben wir bereits geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False
    if eUnitBonus != -1:
        # TODO: Popup Ressource geladen, ueberschreiben?
        #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hat bereits eine Ressource geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return False

    iPrice = _calculateBonusBuyingPrice4Cultivation(eBonus, iBuyer, pUnit.plot())
    if iPrice == -1:
        return False

    pBuyer = gc.getPlayer(iBuyer)
    if pBuyer.getGold() < iPrice:
        CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS", ("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
        return False

    pBuyer.changeGold(-iPrice)
    CvUtil.addScriptData(pUnit, "b", eBonus)

    if pBuyer.isHuman():
        CyInterface().addMessage(iBuyer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS", (gc.getBonusInfo(eBonus).getDescription(), -iPrice)), "AS2D_COINS", 2, None, ColorTypes(13), pUnit.getX(), pUnit.getY(), False, False)

    pUnit.finishMoves()
    PAE_Unit.doGoToNextUnit(pUnit)
    return True

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

def wine(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    eBonus = gc.getInfoTypeForString('BONUS_GRAPES')
    # sorted by priority
    lTerrains = [
        gc.getInfoTypeForString('TERRAIN_PLAINS'),
        gc.getInfoTypeForString('TERRAIN_GRASS')
    ]
    iFirstBlock = len(lTerrains)
    # Improvements fuer Prioritaet
    lImprovements = [
        gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"),
        gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"),
        gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP"),
        gc.getInfoTypeForString("IMPROVEMENT_FARM"),
        gc.getInfoTypeForString("IMPROVEMENT_MINE"),
        gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")
    ]
    iSecondBlock = len(lImprovements)

    # lPlotPrio = [[],[],[],[],[],[],[],[],[]]
    lPlotPrio = [[] for x in xrange(0, iFirstBlock + iSecondBlock + 1)]

    for iI in range(gc.getNUM_CITY_PLOTS()):
        loopPlot = pCity.getCityIndexPlot(iI)
        # die beste position finden:
        if loopPlot is not None and not loopPlot.isNone():
            # wenn bereits eine Weinressource im Umkreis der Stadt ist
            if loopPlot.getBonusType(-1) == eBonus:
                return []
            if loopPlot.getTerrainType() in lTerrains:
                if _canBuildingCultivate(loopPlot, iPlayer):
                    if loopPlot.getImprovementType() == -1:
                        if loopPlot.isHills():
                            for iJ in range(iFirstBlock):
                                if loopPlot.getTerrainType() == lTerrains[iJ]:
                                    lPlotPrio[iJ].append(loopPlot)
                        # 3. irgendeinen passenden ohne Improvement
                        else:
                            lPlotPrio[iFirstBlock].append(loopPlot)
                    # 4. nach Improvements selektieren
                    else:
                        for iJ in range(iSecondBlock):
                            if loopPlot.getImprovementType() == lImprovements[iJ]:
                                lPlotPrio[iJ + iFirstBlock + 1].append(loopPlot)
                                break

    return lPlotPrio


def horse(pCity):
    iPlayer = pCity.getOwner()
    # sorted by priority
    lTerrains = [
        gc.getInfoTypeForString('TERRAIN_PLAINS'),
        gc.getInfoTypeForString('TERRAIN_GRASS')
    ]
    iFirstBlock = len(lTerrains)

    # Improvements fuer Prioritaet
    # sorted by priority
    lImprovements = [
        gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"),
        gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"),
        gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP"),
        gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"),
        gc.getInfoTypeForString("IMPROVEMENT_FARM"),
        gc.getInfoTypeForString("IMPROVEMENT_QUARRY"),
        gc.getInfoTypeForString("IMPROVEMENT_HAMLET"),
        gc.getInfoTypeForString("IMPROVEMENT_COTTAGE_HILL"),
        gc.getInfoTypeForString("IMPROVEMENT_HAMLET_HILL"),
        gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"),
        gc.getInfoTypeForString("IMPROVEMENT_VILLAGE_HILL"),
        gc.getInfoTypeForString("IMPROVEMENT_TOWN")
    ]
    iSecondBlock = len(lImprovements)

    # lPlotPrio = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    lPlotPrio = [[] for x in xrange(0, iFirstBlock + iSecondBlock + 1)]

    for iI in range(gc.getNUM_CITY_PLOTS()):
        loopPlot = pCity.getCityIndexPlot(iI)
        # die beste position finden:
        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getTerrainType() in lTerrains:
                if _canBuildingCultivate(loopPlot, iPlayer):
                    if loopPlot.getImprovementType() == -1:
                        if not loopPlot.isHills():
                            for iJ in range(iFirstBlock):
                                if loopPlot.getTerrainType() == lTerrains[iJ]:
                                    lPlotPrio[iJ].append(loopPlot)
                        # 3. irgendeinen passenden ohne Improvement
                        else:
                            lPlotPrio[iFirstBlock].append(loopPlot)
                    # 4. nach Improvements selektieren
                    else:
                        for iJ in range(iSecondBlock):
                            if loopPlot.getImprovementType() == lImprovements[iJ]:
                                lPlotPrio[iJ + iFirstBlock + 1].append(loopPlot)
                                break
    return lPlotPrio

def camel(pCity):
    iPlayer = pCity.getOwner()
    eBonus = gc.getInfoTypeForString('BONUS_CAMEL')

    # Improvements fuer Prioritaet
    iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_CAMP")
    # sorted by priority
    lTerrains = [
        gc.getInfoTypeForString('TERRAIN_DESERT'),
        gc.getInfoTypeForString('TERRAIN_PLAINS')
    ]
    iFirstBlock = len(lTerrains)

    # lPlotPrio = [[],[],[],[],[]]
    lPlotPrio = [[] for x in xrange(0, iFirstBlock + 3)]

    for iI in range(gc.getNUM_CITY_PLOTS()):
        loopPlot = pCity.getCityIndexPlot(iI)
        # die beste position finden:
        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getBonusType(-1) == eBonus:
                return []
            if not loopPlot.isHills():
                if loopPlot.getTerrainType() in lTerrains:
                    if _canBuildingCultivate(loopPlot, iPlayer):
                        # 1. nach Improvements selektieren
                        if loopPlot.getImprovementType() == iImpType1:
                            lPlotPrio[0].append(loopPlot)
                        elif loopPlot.getImprovementType() == -1:
                            for iJ in range(iFirstBlock):
                                if loopPlot.getTerrainType() == lTerrains[iJ]:
                                    lPlotPrio[iJ+1].append(loopPlot)
                                    break
                            # 4. irgendeinen passenden ohne Improvement
                            else:
                                lPlotPrio[iFirstBlock+1].append(loopPlot)
                        else:
                            lPlotPrio[iFirstBlock+2].append(loopPlot)

    return lPlotPrio

def elephant(pCity):
    iPlayer = pCity.getOwner()

    lFeatures = [
        gc.getInfoTypeForString('FEATURE_JUNGLE'),
        gc.getInfoTypeForString('FEATURE_SAVANNA')
    ]
    iFirstBlock = len(lFeatures)
    lTerrains = [
        gc.getInfoTypeForString('TERRAIN_GRASS'),
        gc.getInfoTypeForString('TERRAIN_PLAINS')
    ]
    iSecondBlock = len(lTerrains)

    eBonus = gc.getInfoTypeForString('BONUS_IVORY')

    # Improvements fuer Prioritaet
    iImpCamp = gc.getInfoTypeForString("IMPROVEMENT_CAMP")

    # lPlotPrio = [[],[],[],[],[],[],[]]
    lPlotPrio = [[] for x in xrange(0, iFirstBlock + iSecondBlock + 3)]

    for iI in range(gc.getNUM_CITY_PLOTS()):
        loopPlot = pCity.getCityIndexPlot(iI)
        # die beste position finden:
        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getBonusType(-1) == eBonus:
                return None
            if not loopPlot.isHills():
                if loopPlot.getTerrainType() in lTerrains or loopPlot.getFeatureType() in lFeatures:
                    if _canBuildingCultivate(loopPlot, iPlayer):
                        if loopPlot.getImprovementType() == -1:
                            # 1. jungle, unworked
                            # 2. savanna, unworked
                            for iJ in range(iFirstBlock):
                                if loopPlot.getFeatureType() == lFeatures[iJ]:
                                    lPlotPrio[iJ].append(loopPlot)
                                    break
                            else:
                                # 4. grass, unworked
                                # 5. plains, unworked
                                for iJ in range(iSecondBlock):
                                    if loopPlot.getTerrainType() == lTerrains[iJ]:
                                        lPlotPrio[iJ + iFirstBlock + 1].append(loopPlot)
                                        break
                                else:
                                    # 6. irgendeinen passenden ohne Improvement
                                    lPlotPrio[iFirstBlock + iSecondBlock + 1].append(loopPlot)
                        # 3. nach Improvements selektieren
                        elif loopPlot.getImprovementType() == iImpCamp:
                            lPlotPrio[iFirstBlock].append(loopPlot)
                        # 7. irgendeinen passenden mit falschem Improvement
                        # TODO: kann gewachsene Huetten zerstoeren
                        else:
                            lPlotPrio[iFirstBlock + iSecondBlock + 2].append(loopPlot)
    return lPlotPrio


def dog(pCity):
    iPlayer = pCity.getOwner()
    lTerrains = [
        gc.getInfoTypeForString('TERRAIN_TUNDRA'),
        gc.getInfoTypeForString('TERRAIN_PLAINS'),
        gc.getInfoTypeForString('TERRAIN_GRASS'),
    ]
    iFirstBlock = len(lTerrains)

    # Improvements fuer Prioritaet
    lImprovements = [
        gc.getInfoTypeForString("IMPROVEMENT_CITY_RUINS"),
        # gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT"),
        gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP"),
        gc.getInfoTypeForString("IMPROVEMENT_FARM"),
        gc.getInfoTypeForString("IMPROVEMENT_MINE"),
        gc.getInfoTypeForString("IMPROVEMENT_COTTAGE")
    ]
    iSecondBlock = len(lImprovements)

    lPlotPrio = [[] for x in xrange(0, iFirstBlock + iSecondBlock + 1)]
    for iI in range(gc.getNUM_CITY_PLOTS()):
        loopPlot = pCity.getCityIndexPlot(iI)
        # die beste position finden:
        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getTerrainType() in lTerrains:
                if _canBuildingCultivate(loopPlot, iPlayer):
                    # unworked
                    if loopPlot.getImprovementType() == -1:
                        if not loopPlot.isHills():
                            for iJ in range(iFirstBlock):
                                if loopPlot.getTerrainType() == lTerrains[iJ]:
                                    lPlotPrio[iJ].append(loopPlot)
                                    break
                        # 3. irgendeinen passenden ohne Improvement
                        else:
                            lPlotPrio[iFirstBlock].append(loopPlot)
                    # 4. nach Improvements selektieren
                    else:
                        for iJ in range(iSecondBlock):
                            if loopPlot.getImprovementType() == lImprovements[iJ]:
                                lPlotPrio[iJ + iFirstBlock + 1].append(loopPlot)
                                break
    return lPlotPrio

def doBuildingCultivate(pCity, iBuildingType):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iImprovement = -1
    eBonus = -1
    bRemoveFeature = False
    bText = False
    sText = "dummy"
    lPlotPrio = []

    # WEIN - FEATURE ---------------------
    # Winzer / Vintager -> Winery / Weinverbreitung
    if iBuildingType == gc.getInfoTypeForString('BUILDING_WINERY') and CvUtil.myRandom(2, "Wein") == 1:
        lPlotPrio = wine(pCity)
        bRemoveFeature = True
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_WINERY')
        bText = True
        iRand = 1 + CvUtil.myRandom(4, "WeinText")
        sText = CyTranslator().getText("TXT_KEY_MESSAGE_VINTAGER_BUILT"+str(iRand), (pCity.getName(),))
        eBonus = gc.getInfoTypeForString('BONUS_WINE')

    # HORSE - FEATURE ---------------------
    # Pferdeverbreitung
    elif iBuildingType == gc.getInfoTypeForString('BUILDING_PFERDEZUCHT'):
        lPlotPrio = horse(pCity)
        bRemoveFeature = True
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_PASTURE')
        eBonus = gc.getInfoTypeForString('BONUS_HORSE')

    # KAMEL - FEATURE ---------------------
    # Kamelverbreitung
    elif iBuildingType == gc.getInfoTypeForString('BUILDING_CAMEL_STABLE'):
        lPlotPrio = camel(pCity)
        iImprovement = gc.getInfoTypeForString("IMPROVEMENT_CAMP")
        eBonus = gc.getInfoTypeForString('BONUS_CAMEL')

    # ELEFANT - FEATURE ---------------------
    # Elefantverbreitung
    elif iBuildingType == gc.getInfoTypeForString('BUILDING_ELEPHANT_STABLE'):
        lPlotPrio = elephant(pCity)
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_CAMP')
        eBonus = gc.getInfoTypeForString('BONUS_IVORY')

    # HUNDE - FEATURE ---------------------
    # Hundeverbreitung
    elif iBuildingType == gc.getInfoTypeForString('BUILDING_HUNDEZUCHT'):
        lPlotPrio = dog(pCity)
        iImprovement = gc.getInfoTypeForString('IMPROVEMENT_CAMP')
        eBonus = gc.getInfoTypeForString('BONUS_HUNDE')

    for lPlots in lPlotPrio:
        if lPlots:
            # ***TEST***
            # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Prio Loop",eBonus)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            pPlot = lPlots[CvUtil.myRandom(len(lPlots), "Gebaeudeverbreitung")]
            pPlot.setBonusType(eBonus)
            pPlot.setImprovementType(iImprovement)
            if bRemoveFeature:
                # Feature (Wald) entfernen
                pPlot.setFeatureType(-1, 0)
            if bText and pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, sText, None, 2, gc.getBonusInfo(eBonus).getButton(), ColorTypes(8), pPlot.getX(), pPlot.getY(), True, True)
            return

def _canBuildingCultivate(loopPlot, iPlayer):
    if not loopPlot.isPeak():
        if loopPlot.getBonusType(-1) == -1:
            if loopPlot.getOwner() == iPlayer or loopPlot.getOwner() == -1:
                if not loopPlot.isCity():
                    return True
