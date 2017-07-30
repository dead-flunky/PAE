# Trade and Cultivation feature
# From BoggyB
### Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil
import PAE_Unit
import PAE_Lists as L
### Defines
gc = CyGlobalContext()

### Globals
bInitialized = False # Whether global variables are already initialised
iMaxCitiesSpecialBonus = 3
iCitiesSpecialBonus = 0 # Cities with Special Trade Bonus

# Update (Ramk): CvUtil-Functions unpack an dict. You could directly use int, etc.

# Used keys for UnitScriptData:
# "x"/"y": coordinates of plots where bonus was picked up (merchants)
# "b": index of bonus stored in merchant/cultivation unit (only one at a time)
# "originCiv": original owner of the bonus stored in merchant (owner of the city where it was bought)

# For automated trade routes:
# "autX1"/"autX2"/"autY1"/"autY2": coordinates of cities in trade route
# "autB1": bonus bought in city 1/sold in city 2
# "autB2": bonus bought in city 2/sold in city 1
# "autA": if False, automated route is currently inactive
# "autLTC": latest turn when "doAutomateMerchant" was called for this unit. Sometimes it is called multiple times per turn, this prevents unnecessary calculations

# Used keys for CityScriptData:
# "b": free bonuses acquired via turns and until which turn they are available,
# e.g. {43:4, 23:8, 12:10} key: bonus index (int), value: num turns (int)

def init():
    global bInitialized
    global iCitiesSpecialBonus

    if not bInitialized:
        # Cities mit Special Trade Bonus herausfinden
        iRange = gc.getMAX_PLAYERS()
        for i in range(iRange):
            loopPlayer = gc.getPlayer(i)
            if loopPlayer.isAlive() and not loopPlayer.isBarbarian():
                (loopCity, pIter) = loopPlayer.firstCity(False)
                while loopCity:
                    if not loopCity.isNone() and loopCity.getOwner() == loopPlayer.getID(): #only valid cities
                        if CvUtil.getScriptData(loopCity, ["tsb"], -1) != -1:
                            iCitiesSpecialBonus += 1
                            if iCitiesSpecialBonus == iMaxCitiesSpecialBonus:
                                break
                    (loopCity, pIter) = loopPlayer.nextCity(pIter, False)
            if iCitiesSpecialBonus == iMaxCitiesSpecialBonus:
                break
        bInitialized = True

# --- Trade in cities ---

# Unit stores bonus, owner pays, if UnitOwner != CityOwner: city owner gets money
def doBuyBonus(pUnit, eBonus, iCityOwner):

    if not pUnit.getUnitType() in L.LTradeUnits:
        return

    if eBonus != -1:
        iBuyer = pUnit.getOwner()
        pBuyer = gc.getPlayer(iBuyer)

        eUnitBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
        if eBonus == eUnitBonus:
            #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Das haben wir bereits geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            return
        if eUnitBonus != -1:
            # TODO: Popup Ressource geladen, ueberschreiben?
            #CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Die Einheit hat bereits eine Ressource geladen.",)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            return

        iPrice = _calculateBonusBuyingPrice(eBonus, iBuyer, iCityOwner)
        if pBuyer.getGold() < iPrice:
            CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_NO_GOODS", ("",)), None, 2, "Art/Interface/PlotPicker/Warning.dds", ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
            return
        pBuyer.changeGold(-iPrice)

        iGewinnGold = iPrice
        # iGewinnWissen = 0

        pSeller = gc.getPlayer(iCityOwner)
        if iBuyer != iCityOwner:
            iGewinnGold = int(iPrice / 10 * pSeller.getCurrentEra())
            pSeller.changeGold(iGewinnGold)
            #iGewinnWissen = int(iPrice / 4 * pSeller.getCurrentEra())
            #doResearchPush(iBuyer, iGewinnWissen)
            #doResearchPush(iCityOwner, iGewinnWissen)

        CvUtil.addScriptData(pUnit, "b", eBonus)
        CvUtil.addScriptData(pUnit, "originCiv", iCityOwner)
        CvUtil.addScriptData(pUnit, "x", pUnit.getX())
        CvUtil.addScriptData(pUnit, "y", pUnit.getY())
        if pSeller.isHuman() and iBuyer != iCityOwner:
            sBonusName = gc.getBonusInfo(eBonus).getDescription()
            CyInterface().addMessage(iCityOwner, True, 10, CyTranslator().getText("TXT_KEY_BONUS_BOUGHT", (pBuyer.getName(), pBuyer.getCivilizationShortDescriptionKey(), pUnit.plot().getPlotCity().getName(), sBonusName, iGewinnGold)), "AS2D_COINS", 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)

        if pBuyer.isHuman():
            CyInterface().addMessage(iBuyer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_COLLECT_GOODS", (gc.getBonusInfo(eBonus).getDescription(), -iPrice)), "AS2D_COINS", 2, None, ColorTypes(13), 0, 0, False, False)

        pUnit.finishMoves()
        PAE_Unit.doGoToNextUnit(pUnit)


def doSellBonus(pUnit, pCity):
    """Unit's store is emptied, unit owner gets money, city gets bonus, research push"""
    eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eBonus != -1:
        iPrice = calculateBonusSellingPrice(pUnit, pCity)
        iBuyer = pCity.getOwner()
        pBuyer = gc.getPlayer(iBuyer)
        iSeller = pUnit.getOwner()
        pSeller = gc.getPlayer(iSeller)

        pSeller.changeGold(iPrice)
        iGewinnWissen = 0

        iOriginCiv = CvUtil.getScriptData(pUnit, ["originCiv"], -1) # where the goods come from
        CvUtil.removeScriptData(pUnit, "b")
        if iOriginCiv != iBuyer:

            #iGewinnGold = int(iPrice / 10 * pSeller.getCurrentEra())
            #pSeller.changeGold(iGewinnGold)
            iGewinnWissen = int(iPrice / 4 * pSeller.getCurrentEra())
            _doResearchPush(iBuyer, iGewinnWissen)
            _doResearchPush(iSeller, iGewinnWissen)
            _doCityProvideBonus(pCity, eBonus, 3)

            # Chance: Buyer has bonus or not (fuer Handelsstrasse)
            if pBuyer.hasBonus(eBonus):
                iChance = 10
            else:
                iChance = 20

            # Trade route / Handelsstrasse
            if eBonus in L.LBonusLuxury + L.LBonusRarity:
                if not CvUtil.hasBonusIgnoreFreeBonuses(pCity, eBonus) and pUnit.getDomainType() != gc.getInfoTypeForString("DOMAIN_SEA"):
                    # Rarities doubles chance
                    if eBonus in L.LBonusRarity:
                        iChance *= 2
                    if CvUtil.myRandom(100, "Handelsstrasse") < iChance:
                        iOriginX = CvUtil.getScriptData(pUnit, ["x"], -1)
                        iOriginY = CvUtil.getScriptData(pUnit, ["y"], -1)
                        pOriginPlot = CyMap().plot(iOriginX, iOriginY)
                        if pOriginPlot is not None and not pOriginPlot.isNone():
                            if pOriginPlot.isCity():
                                iRouteType = gc.getInfoTypeForString("ROUTE_TRADE_ROAD")
                                pOriginCity = pOriginPlot.getPlotCity()
                                #CyInterface().addMessage(iSeller, True, 10, "Vor Traderoute", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                                pPlotTradeRoad = getPlotTradingRoad(pOriginPlot, pUnit.plot())
                                #CyInterface().addMessage(iSeller, True, 10, "Nach Traderoute", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                                if pPlotTradeRoad is not None:
                                    pPlotTradeRoad.setRouteType(iRouteType)
                                    if pBuyer.isHuman():
                                        CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT", (pSeller.getName(), pSeller.getCivilizationShortDescriptionKey(), pCity.getName(), pOriginCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)
                                    if pSeller.isHuman() and iBuyer != iSeller:
                                        CyInterface().addMessage(iSeller, True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_BUILT2", (pCity.getName(), pOriginCity.getName())), "AS2D_WELOVEKING", 2, "Art/Terrain/Routes/handelsstrasse/button_handelsstrasse.dds", ColorTypes(10), pPlotTradeRoad.getX(), pPlotTradeRoad.getY(), True, True)
                                    if iBuyer != iSeller and iSeller == gc.getGame().getActivePlayer() or iBuyer == gc.getGame().getActivePlayer():
                                        CyAudioGame().Play2DSound("AS2D_WELOVEKING")
                                # Sobald von einer Stadt 3 Handelsstrassen (bzw 2 bei einer Kuestenstadt) weggehen,
                                # wird es zum Handelszentrum (Building: 100% auf Trade Routes)
                                iBuilding = gc.getInfoTypeForString("BUILDING_HANDELSZENTRUM")
                                if not pOriginCity.isHasBuilding(iBuilding):
                                    iAnz = 0
                                    iMax = 3
                                    if pOriginCity.isCoastal(4):
                                        iMax = 2
                                    for i in range(8):
                                        pLoopPlot = plotDirection(iOriginX, iOriginY, DirectionTypes(i))
                                        if pLoopPlot is not None and not pLoopPlot.isNone():
                                            if pLoopPlot.getRouteType() == iRouteType:
                                                iAnz += 1
                                            if iAnz >= iMax:
                                                break
                                    if iAnz >= iMax:
                                        pOriginCity.setNumRealBuilding(iBuilding, 1)
                                        if pOriginCity.getOwner() == gc.getGame().getActivePlayer():
                                            CyInterface().addMessage(pOriginCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_TRADE_ROUTE_HANDELSZENTRUM", (pOriginCity.getName(),)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuilding).getButton(), ColorTypes(10), pOriginCity.getX(), pOriginCity.getY(), True, True)
        else:
            pSeller.changeGold(iPrice)
        sBonusName = gc.getBonusInfo(eBonus).getDescription()
        if pBuyer.isHuman() and iBuyer != iSeller:
            CyInterface().addMessage(iBuyer, True, 10, CyTranslator().getText("TXT_KEY_BONUS_SOLD", (pSeller.getName(), pSeller.getCivilizationShortDescriptionKey(), pCity.getName(), sBonusName, iGewinnWissen)), None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
        else:
            CyInterface().addMessage(iSeller, True, 10, CyTranslator().getText("TXT_KEY_BONUS_SOLD2", (pCity.getName(), pBuyer.getCivilizationShortDescriptionKey(), sBonusName, iPrice, iGewinnWissen)), None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
        if iSeller == gc.getGame().getActivePlayer() or iBuyer == gc.getGame().getActivePlayer():
            CyAudioGame().Play2DSound("AS2D_COINS")

        # Special Order
        if iOriginCiv != iBuyer:
            if eBonus in L.LBonusLuxury + L.LBonusRarity:
                _doCheckCitySpecialBonus(pUnit, pCity, eBonus)
        pUnit.finishMoves()

# Player gets research points for current project (called when foreign goods are sold to player's cities)
def _doResearchPush(iPlayer1, iValue1):
    pPlayer1 = gc.getPlayer(iPlayer1)
#    pPlayer2 = gc.getPlayer(iPlayer2)
    pTeam1 = gc.getTeam(pPlayer1.getTeam())
#    pTeam2 = gc.getTeam(pPlayer2.getTeam())
    eTech1 = pPlayer1.getCurrentResearch()
#    eTech2 = pPlayer2.getCurrentResearch()
    if eTech1 != -1:
        pTeam1.changeResearchProgress(eTech1, iValue1, iPlayer1)
#    if eTech2 != -1: pTeam2.changeResearchProgress(eTech2, iValue2, iPlayer2)

# City can use bonus for x turns
def _doCityProvideBonus(pCity, eBonus, iTurn):
    # ScriptData value is dict, e.g. {43:4; 23:8; 12:10}
    # Key is 'iBonus' and value is 'iTurns'

    bonusDict = CvUtil.getScriptData(pCity, ["b"], {})

    # compatibility
    if isinstance(bonusDict, str):
        # Konvertiere altes Format "iB,iTurn;..." in dict
        tmp = [paar.split(",") for paar in str(bonusDict).split(";")]
        bonusDict = dict([map(int, pair) for pair in tmp])

    if not eBonus in bonusDict:
        pCity.changeFreeBonus(eBonus, 1)

    # Addiere alten und neuen Rundenwert
    iCurrentTurn = gc.getGame().getGameTurn()
    bonusDict[eBonus] = iTurn + bonusDict.setdefault(eBonus, iCurrentTurn)
    CvUtil.addScriptData(pCity, "b", bonusDict)


# Called each turn (onCityDoTurn, EventManager), makes sure free bonus disappears after x turns
def doCityCheckFreeBonuses(pCity):
    bonusDict = CvUtil.getScriptData(pCity, ["b"], {})
    bUpdate = False
    # compatibility
    if isinstance(bonusDict, str):
        # Konvertiere altes Format "iB,iTurn;..." in dict
        tmp = [paar.split(",") for paar in str(bonusDict).split(";")]
        bonusDict = dict([map(int, pair) for pair in tmp])
        bUpdate = True

    lRemove = []
    lAdd = {}
    for eBonus in bonusDict:
        iTurn = bonusDict[eBonus]

        # alte Saves korrigieren str->int
        if isinstance(eBonus, str):
            lRemove.append(eBonus)
            eBonus = int(eBonus)
            lAdd[eBonus] = iTurn

        if iTurn <= gc.getGame().getGameTurn():
            pCity.changeFreeBonus(eBonus, -1) # Time over: remove bonus from city
            lRemove.append(eBonus)
            bUpdate = True

    # alte Saves korrigieren str->int
    bonusDict.update(lAdd)

    for eBonus in lRemove:
        bonusDict.pop(eBonus, None)
    if bUpdate:
        CvUtil.addScriptData(pCity, "b", bonusDict)


# Creates popup with all the affordable bonuses for UnitOwner (bonuses too expensive for UnitOwner are cut)
def doPopupChooseBonus(pUnit, pCity):
    if pCity is None or pCity.isNone() or pUnit is None or pUnit.isNone():
        return False
    iBuyer = pUnit.getOwner()
    iSeller = pCity.getOwner()
    lGoods = getCitySaleableGoods(pCity, iBuyer)

    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_CHOOSE_BONUS", ("", )))
    popupInfo.setOnClickedPythonCallback("popupTradeChooseBonus")
    popupInfo.setData1(pUnit.getOwner())
    popupInfo.setData2(pUnit.getID())

    for eBonus in lGoods:
        sBonusDesc = gc.getBonusInfo(eBonus).getDescription()
        iPrice = _calculateBonusBuyingPrice(eBonus, iBuyer, iSeller)
        sText = CyTranslator().getText("TXT_KEY_BUY_BONUS", (sBonusDesc, iPrice))
        sBonusButton = gc.getBonusInfo(eBonus).getButton()
        popupInfo.addPythonButton(sText, sBonusButton)

    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
    popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
    popupInfo.addPopup(iBuyer)

# --- End of trade in cities

# --- Price stuff (trade) ---

# Basis value for each bonus
# auch in TXT_KEY_TRADE_ADVISOR_WERT_PANEL
def getBonusValue(eBonus):
    if eBonus == -1 or eBonus in L.LBonusUntradeable:
        return -1
    if eBonus in L.LBonusCorn + L.LBonusLivestock + L.LBonusPlantation:
        return 20
    elif eBonus in L.LBonusLuxury:
        return 40
    elif eBonus in L.LBonusRarity:
        return 50
    return 30 # strategic bonus ressource


# Price player pays for buying bonus
def _calculateBonusBuyingPrice(eBonus, iBuyer, iSeller):
    if iBuyer == -1 or iSeller == -1:
        return -1
    iValue = getBonusValue(eBonus)
    pBuyer = gc.getPlayer(iBuyer)
    pSeller = gc.getPlayer(iSeller)
    if pBuyer.getTeam() == pSeller.getTeam():
        iAttitudeModifier = 100
    else:
        # Furious = 0, Annoyed = 1, Cautious = 2, Pleased = 3, Friendly = 4
        iAttitudeModifier = 125 - 5*pSeller.AI_getAttitude(iBuyer)
    return (iValue * iAttitudeModifier) / 100


# Money player gets for selling bonus
def calculateBonusSellingPrice(pUnit, pCity):
    if not pUnit.getUnitType() in L.LTradeUnits:
        return -1
    eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
    if eBonus == -1:
        return -1
    iValue = getBonusValue(eBonus)
    #iValue += iValue / 2 # besserer Verkaufswert fuer bessere Bonusgueter (Luxusgut)
    iBuyer = pCity.getOwner()
    iSeller = pUnit.getOwner()
    pBuyer = gc.getPlayer(iBuyer)
    pSeller = gc.getPlayer(iSeller)
    if CvUtil.hasBonusIgnoreFreeBonuses(pCity, eBonus): # allows "cancellation" of buying / Bonus direkt nach Einkauf wieder verkaufen (ohne Gewinn)
        return _calculateBonusBuyingPrice(eBonus, iSeller, iBuyer) # Switch positions of seller and buyer

    if pBuyer.getTeam() == pSeller.getTeam():
        iModifier = 100
    else:
        # Furious = 0, Annoyed = 1, Cautious = 2, Pleased = 3, Friendly = 4
        iModifier = 100 + 5*pSeller.AI_getAttitude(iBuyer)
    return (iValue * iModifier * (100+pCity.getPopulation()*5)) / 10000
# --- End of price stuff (trade) ---

# --- Automated trade routes (popups for HI) ---

# Erzeugt Popup fuer Erstellung einer automatisierten Handelsroute, wird insgesamt sechsmal pro Route aufgerufen:
# Civ waehlen => Stadt waehlen => Bonus waehlen => Civ waehlen => Stadt waehlen => Bonus waehlen
# iType = 1, 2, ...., 6 gibt an, an welcher Stelle im Prozess man gerade ist (1: erste Civ waehlen, ..., 6: zweiten Bonus waehlen)
# iData1/2: Ggf. noetige, zusaetzliche Informationen
def doPopupAutomatedTradeRoute(pUnit, iType, iData1, iData2):
    iUnitOwner = pUnit.getOwner()
    if iType == 1 or iType == 4:
        # Choose civilization 1 (iType == 1) or civilization 2 (iType == 4)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        if iType == 1:
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CIV_1", ("", )))
        else:
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CIV_2", ("", )))
        popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCiv")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iType == 1)
        lCivs = getPossibleTradeCivs(iUnitOwner)
        for iPlayer in lCivs:
            pPlayer = gc.getPlayer(iPlayer)
            sText = pPlayer.getCivilizationShortDescription(0) + " (" + pPlayer.getName() + ")"
            sButton = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getButton()
            popupInfo.addPythonButton(sText, sButton)

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)
    elif iType == 2 or iType == 5:
        # Choose city 1 (iType == 2) or city 2 (iType == 5)
        iCityOwner = iData1
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_CITY", ("", )))
        if iType == 2:
            popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCity1")
        else:
            popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseCity2")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iCityOwner)
        bWater = False
        if pUnit.getDomainType() == DomainTypes.DOMAIN_SEA:
            bWater = True
        lCities = getPossibleTradeCitiesForCiv(iUnitOwner, iCityOwner, bWater)
        sButton = ",Art/Interface/Buttons/Actions/FoundCity.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,1,4"
        for pCity in lCities:
            sText = pCity.getName()
            popupInfo.addPythonButton(sText, sButton)
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)
    elif iType == 3 or iType == 6:
        # Choose bonus to buy in selected city.
        pCity = gc.getPlayer(iData1).getCity(iData2)
        sCityName = pCity.getName()
        lGoods = getCitySaleableGoods(pCity, -1)
        lGoods.append(-1)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_TRADE_ROUTE_CHOOSE_BONUS", (sCityName, )))
        popupInfo.setOnClickedPythonCallback("popupTradeRouteChooseBonus")
        popupInfo.setData1(iUnitOwner)
        popupInfo.setData2(pUnit.getID())
        popupInfo.setData3(iType == 3)
        for eBonus in lGoods:
            if eBonus != -1:
                sText = gc.getBonusInfo(eBonus).getDescription()
                sButton = gc.getBonusInfo(eBonus).getButton()
                popupInfo.addPythonButton(sText, sButton)
            else:
                sText = CyTranslator().getText("TXT_KEY_NO_BONUS", ("", ))
                sButton = "Art/Interface/Buttons/Techs/button_x.dds"
                popupInfo.addPythonButton(sText, sButton)
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iUnitOwner)
# --- End of automated trade routes for HI ---

# --- Helper functions ---
def getCitySaleableGoods(pCity, iBuyer):
    """ Returns a list of the tradeable bonuses within pCity's range (radius of 2) + bonuses from buildings (bronze etc.). Only goods within the team's culture are considered.
        if iBuyer != -1: Bonuses the buying player cannot afford (not enough money) are excluded
    """
    if pCity is None or pCity.isNone():
        return []
    iCityOwnerTeam = pCity.getTeam()
    iCityOwner = pCity.getOwner()
    # pCityOwner = gc.getPlayer(iCityOwner)
    if iBuyer != -1:
        iMaxPrice = gc.getPlayer(iBuyer).getGold()
    lGoods = []
    iX = pCity.getX()
    iY = pCity.getY()
    for x in range(5): # check plots
        for y in range(5):
            pLoopPlot = gc.getMap().plot(iX + x - 2, iY + y - 2)
            if pLoopPlot is not None and not pLoopPlot.isNone():
                if pLoopPlot.getTeam() != iCityOwnerTeam:
                    continue
                # plot needs to have suitable improvement and city needs to have access to bonus (=> connection via trade route (street))
                eBonus = pLoopPlot.getBonusType(iCityOwnerTeam)
                eImprovement = pLoopPlot.getImprovementType()
                if eImprovement != -1 and eBonus != -1 and eBonus not in lGoods and eBonus not in L.LBonusUntradeable:
                    if gc.getImprovementInfo(eImprovement).isImprovementBonusMakesValid(eBonus) and CvUtil.hasBonusIgnoreFreeBonuses(pCity, eBonus):
                        if iBuyer == -1 or _calculateBonusBuyingPrice(eBonus, iBuyer, iCityOwner) <= iMaxPrice: # Max price
                            lGoods.append(eBonus)
    iMaxNumBuildings = gc.getNumBuildingInfos()
    for iBuilding in range(iMaxNumBuildings): # check buildings
        if pCity.isHasBuilding(iBuilding):
            eBonus = gc.getBuildingInfo(iBuilding).getFreeBonus()
            if eBonus != -1 and eBonus not in L.LBonusUntradeable and eBonus not in lGoods and CvUtil.hasBonusIgnoreFreeBonuses(pCity, eBonus):
                if iBuyer == -1 or _calculateBonusBuyingPrice(eBonus, iBuyer, iCityOwner) <= iMaxPrice: # Max price
                    lGoods.append(eBonus)
    return lGoods

# Returns list of civs iPlayer can trade with (has met and peace with). List always includes iPlayer himself.
def getPossibleTradeCivs(iPlayer):
    pTeam = gc.getTeam(gc.getPlayer(iPlayer).getTeam())
    lCivList = []
    for iCiv in range(gc.getMAX_PLAYERS()):
        iCivTeam = gc.getPlayer(iCiv).getTeam()
        if pTeam.isHasMet(iCivTeam) and not pTeam.isAtWar(iCivTeam):
            lCivList.append(iCiv)
    return lCivList

# Returns list of cities which 1. belong to iPlayer2 and 2. are visible to iPlayer1
def getPossibleTradeCitiesForCiv(iPlayer1, iPlayer2, bWater):
    iTeam1 = gc.getPlayer(iPlayer1).getTeam()
    pPlayer2 = gc.getPlayer(iPlayer2)
    lCityList = []
    (loopCity, pIter) = pPlayer2.firstCity(False)
    while loopCity:
        if not loopCity.isNone() and loopCity.getOwner() == iPlayer2: #only valid cities
            if loopCity.isRevealed(iTeam1, 0):
                if not bWater or loopCity.isCoastal(4):
                    lCityList.append(loopCity)
        (loopCity, pIter) = pPlayer2.nextCity(pIter, False)
    return lCityList

def getPlotTradingRoad(pSource, pDest):
    """Gibt Plot zurueck, auf dem das naechste Handelsstrassen-Stueck entstehen soll bzw. ob die Strasse schon fertig ist. Von Pie.
    """
    # Nur auf gleichem Kontinent
    if pSource.getArea() == pDest.getArea():
        iSourceX = pSource.getX()
        iSourceY = pSource.getY()
        iDestX = pDest.getX()
        iDestY = pDest.getY()

        # wenn pSource = pTarget (Haendler ueber Schiff im Hafen)
        if iSourceX != iDestX or iSourceY != iDestY:
            iTradeRoad = gc.getInfoTypeForString("ROUTE_TRADE_ROAD")
            bSourceGerade = False
            # Herausfinden, ob bei pSource eine GERADE Strasse gebaut wurde
            # um zu verhindern, dass 2 Routen erstellt werden:
            #-------#
            #   --X #
            #  / /  #
            # X--   #
            #-------#
            # wenn es noch keine Strasse in der Stadt gibt => egal
            # wenn es eine Strasse gibt, dann den Umkreis checken
            if pSource.getRouteType() == iTradeRoad:
                iBest = 0
                for i in range(3):
                    for j in range(3):
                        loopPlot = gc.getMap().plot(iSourceX + i - 1, iSourceY + j - 1)
                        if loopPlot is not None and not loopPlot.isNone():
                            if loopPlot.getRouteType() == iTradeRoad:
                                iTmp = gc.getMap().calculatePathDistance(loopPlot, pDest)
                                if iBest == 0:
                                    iBest = iTmp
                                elif iTmp == iBest and (i == 1 or j == 1):
                                    bSourceGerade = True
                                elif iTmp < iBest:
                                    bSourceGerade = (i == 1 or j == 1)

            # Den naechsten Plot fuer die Handelsstrasse herausfinden
            if pDest.getRouteType() != iTradeRoad:
                return pDest # Wenn die Stadt noch keine Handelsstrasse hat
            iBestX = iDestX
            iBestY = iDestY
            pBest = pDest
            while iBestX != iSourceX or iBestY != iSourceY:
                i = 0
                j = 0
                iBest = 0
                for i in range(3):
                    for j in range(3):
                        loopPlot = gc.getMap().plot(iBestX + i - 1, iBestY + j - 1)
                        if loopPlot is not None and not loopPlot.isNone():
                            if not loopPlot.isPeak() and not loopPlot.isWater():
                                iTmp = gc.getMap().calculatePathDistance(loopPlot, pSource)
                                # Beenden, wenn kein Weg moeglich
                                if iTmp == -1:
                                    return None
                                # wenn Distanz null ist, wurde der letzte Plot gefunden
                                elif iTmp == 0:
                                    if loopPlot.getRouteType() == iTradeRoad:
                                        return None
                                    return loopPlot
                                if iBest == 0 or iTmp < iBest:
                                    iBest = iTmp
                                    pBest = loopPlot
                                elif iTmp == iBest:
                                    # Bei gleichen Entfernungen (max. 3 Moeglichkeiten: schraeg - gerade (- schraeg))
                                    # Wenn bei der Quelle eine GERADE Strasse verlaeuft, dann schraeg bauen. Sonst umgekehrt.
                                    if (i == 1 or j == 1) and not bSourceGerade:
                                        pBest = loopPlot
                if pBest.getRouteType() != iTradeRoad:
                    return pBest

                iBestX = pBest.getX()
                iBestY = pBest.getY()
    return None
# --- End of helper functions ---

# --- AI and automated trade routes ---

# Lets pUnit shuttle between two cities (defined by UnitScriptData). Used by AI and by HI (automated trade routes).
def doAutomateMerchant(pUnit, bAI):
    # DEBUG
    # iHumanPlayer = gc.getGame().getActivePlayer()
    bTradeRouteActive = int(CvUtil.getScriptData(pUnit, ["autA", "t"], 0))
    if bTradeRouteActive and pUnit.getGroup().getLengthMissionQueue() == 0:
        iPlayer = pUnit.getOwner()
        # DEBUG
        # pPlayer = gc.getPlayer(iPlayer)
        # s = pPlayer.getName()
        pUnitPlot = pUnit.plot()
        iTurn = gc.getGame().getGameTurn()
        # Verhindern, dass mehrmals pro Runden geprueft wird, um Rundenzeit zu sparen
        # Z.B. bei bedrohten Einheiten ruft Civ die Funktion sonst 100 Mal auf, weiss nicht wieso...
        iLastTurnChecked = CvUtil.getScriptData(pUnit, ["autLTC"], -1)
        if iLastTurnChecked >= iTurn:
            return False
        else:
            CvUtil.addScriptData(pUnit, "autLTC", iTurn)
        pUnit.getGroup().clearMissionQueue()
        eStoredBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
        iX1 = CvUtil.getScriptData(pUnit, ["autX1"], -1)
        iY1 = CvUtil.getScriptData(pUnit, ["autY1"], -1)
        iX2 = CvUtil.getScriptData(pUnit, ["autX2"], -1)
        iY2 = CvUtil.getScriptData(pUnit, ["autY2"], -1)
        eBonus1 = CvUtil.getScriptData(pUnit, ["autB1"], -1) # bonus bought in city 1
        eBonus2 = CvUtil.getScriptData(pUnit, ["autB2"], -1) # bonus bought in city 2
        pCityPlot1 = CyMap().plot(iX1, iY1)
        pCityPlot2 = CyMap().plot(iX2, iY2)
        pCity1 = pCityPlot1.getPlotCity()
        pCity2 = pCityPlot2.getPlotCity()
        if pCity1 is None or pCity1.isNone() or pCity2 is None or pCity2.isNone():
            # delete invalid trade route
            CvUtil.removeScriptData(pUnit, "autA")
            CvUtil.removeScriptData(pUnit, "autLTC")
            CvUtil.removeScriptData(pUnit, "autX1")
            CvUtil.removeScriptData(pUnit, "autY1")
            CvUtil.removeScriptData(pUnit, "autX2")
            CvUtil.removeScriptData(pUnit, "autY2")
            CvUtil.removeScriptData(pUnit, "autB1")
            CvUtil.removeScriptData(pUnit, "autB2")
            return False
        if pUnit.atPlot(pCityPlot1) or pUnit.atPlot(pCityPlot2):
            if pUnit.atPlot(pCityPlot1):
                pCurrentCity = pCity1
                pNewCity = pCity2
                eBonusBuy = eBonus1
                eBonusSell = eBonus2
            elif pUnit.atPlot(pCityPlot2):
                pCurrentCity = pCity2
                pNewCity = pCity1
                eBonusBuy = eBonus2
                eBonusSell = eBonus1
            if eBonusSell != -1 and eStoredBonus == eBonusSell:
                doSellBonus(pUnit, pCurrentCity)
            # HI: if player does not have enough money, trade route is cancelled
            # AI: if AI does not have enough money, AI buys bonus nonetheless (causes no known errors)
            ## doBuyBonus doesn't work this way. AIs traderoute will be deactivated as well. 
            if bAI:
                iBuyer = -1
            else:
                iBuyer = iPlayer
            lCitySaleableGoods = getCitySaleableGoods(pCurrentCity, iBuyer)
            if eBonusBuy == -1:
                pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
                # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy == -1 " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
            elif eBonusBuy in lCitySaleableGoods:
                if eStoredBonus != eBonusBuy:
                    # if not already acquired / Wenn Bonus nicht bereits gekauft wurde
                    doBuyBonus(pUnit, eBonusBuy, pCurrentCity.getOwner())
                pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
                # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy in lCitySaleable " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
            elif eStoredBonus == eBonusBuy:
                pUnit.getGroup().pushMoveToMission(pNewCity.getX(), pNewCity.getY())
                # CyInterface().addMessage(iHumanPlayer, True, 10, "Mission eBonusBuy == eStoredBonus " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
            else:
                # bonus is no longer available (or player does not have enough money) => cancel automated trade route
                CvUtil.addScriptData(pUnit, "autA", 0) # deactivate route
                # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
                return False
        else:
            # unit is anywhere => send to city 1
            iDistance1 = CyMap().calculatePathDistance(pUnitPlot, pCityPlot1)
            iDistance2 = CyMap().calculatePathDistance(pUnitPlot, pCityPlot2)
            if iDistance1 == -1 and iDistance2 == -1:
                # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
                return False # plot unreachable
            elif iDistance1 == -1:
                pUnit.getGroup().pushMoveToMission(pCityPlot2.getX(), pCityPlot2.getY())
            elif iDistance2 == -1 or iDistance1 <= iDistance2:
                pUnit.getGroup().pushMoveToMission(pCityPlot1.getX(), pCityPlot1.getY())
            else:
                pUnit.getGroup().pushMoveToMission(pCityPlot2.getX(), pCityPlot2.getY())
    ##        if iDistance != -1: pUnit.getGroup().pushMoveToMission(pCityPlot1.getX(), pCityPlot1.getY())
    ##        else:
    ##            CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns False " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
    ##            return False # plot unreachable
        # CyInterface().addMessage(iHumanPlayer, True, 10, "doAutomateMerchant returns True " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        # Am Ende eine Runde warten, da die Einheit sonst, wenn sie bei Erreichen einer Stadt noch Bewegungspunkte hat, einen neuen Befehl verlangt
        pUnit.getGroup().pushMission(MissionTypes.MISSION_SKIP, 0, 0, 0, True, False, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
        return True
    return False

# Weist der Einheit eine moeglichst kurze Handelsroute zu, die moeglichst so verlaeuft, dass an beiden Stationen ein Luxusgut eingeladen wird
def doAssignTradeRoute_AI(pUnit):
    # iHumanPlayer = -1 (Needed for test messages, otherwise unnecessary)
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    pUnitPlot = pUnit.plot()

    if pPlayer.getGold() < 50:
        return

    # friedliche Nachbarn raussuchen
    lNeighbors = []
    iRange = gc.getMAX_PLAYERS()
    for iLoopPlayer in range(iRange):
        pLoopPlayer = gc.getPlayer(iLoopPlayer)
        if pLoopPlayer.isAlive() and iLoopPlayer != iPlayer:
            if pTeam.isHasMet(pLoopPlayer.getTeam()):
                if pTeam.isOpenBorders(pLoopPlayer.getTeam()):
                    # widerspricht ohnehin open borders
                    # if not pTeam.isAtWar(pLoopPlayer.getTeam()):
                    # Distanz mittels Abstand zur Hauptstadt herausfinden
                    (loopCity, pIter) = pLoopPlayer.firstCity(False)
                    while loopCity:
                        if not loopCity.isNone() and loopCity.getOwner() == iLoopPlayer: #only valid cities
                            if loopCity.isCapital():
                                iDistance = CyMap().calculatePathDistance(pUnitPlot, loopCity.plot())
                                if iDistance != -1:
                                    lNeighbors.append([iDistance, iLoopPlayer])
                        (loopCity, pIter) = pLoopPlayer.nextCity(pIter, False)
                    # if not pLoopPlayer.getCity(0).isNone():
                        # iDistance = CyMap().calculatePathDistance(pUnitPlot, pLoopPlayer.getCity(0).plot())
                        # if iDistance != -1:
                            # lNeighbors.append([iDistance, iLoopPlayer])

    lNeighbors.sort() # sort by distance
    lNeighbors = lNeighbors[:5] # only check max. 5 neighbors
    # Liste aller Staedte des Spielers mit verfuegbaren Luxusguetern. Staedte ohne Luxusgut ausgelassen.
    lPlayerLuxuryCities = _getPlayerLuxuryCities(iPlayer)
    iMaxDistance = 20 # Wie weit die KI einen Haendler max. schickt
    iMinDistance = -1
    bBothDirections = False
    pBestPlayerCity = None
    pBestNeighborCity = None
    for [iDistance, iNeighbor] in lNeighbors:
        lNeighborLuxuryCities = _getPlayerLuxuryCities(iNeighbor)
        # Sucht nach Paar von Staedten, zwischen denen Luxushandel moeglich ist, mit min. Distanz.
        # Routen, bei denen in beiden Staedten Luxus eingekauft werden kann, der in der anderen Stadt wieder verkauft
        # werden kann (=> Bonus NICHT in beiden Staedten), werden bevorzugt (dann ist bBothDirections = True).
        # Sonst wird eine Route gewaehlt, bei der der Haendler nur in eine Richtung handelt (andere Richtung Leertransport)
        for [pNeighborCity, lNeighborCityLuxury] in lNeighborLuxuryCities:
            for [pPlayerCity, lPlayerCityLuxury] in lPlayerLuxuryCities:
                pCityPlotPlayer = pPlayerCity.plot()
                pCityPlotNeighbor = pNeighborCity.plot()
                # Handelsstrasse existiert schon => andere Route waehlen
                if getPlotTradingRoad(pCityPlotPlayer, pCityPlotNeighbor) is not None:
                    continue
                #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "Keine Handelsstrasse", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                bDirection1 = False
                bDirection2 = False
                for eBonus in lNeighborCityLuxury:
                    if not pPlayerCity.hasBonus(eBonus):
                        bDirection1 = True
                        break
                for eBonus in lPlayerCityLuxury:
                    if not pNeighborCity.hasBonus(eBonus):
                        bDirection2 = True
                        break
                iDistance = CyMap().calculatePathDistance(pCityPlotPlayer, pCityPlotNeighbor)
                if iDistance != -1 and iDistance < iMaxDistance:
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "iDistance != -1", None, 2, None, ColorTypes(8), pUnit.getX(), pUnit.getY(), False, False)
                    if bDirection1 and bDirection2:
                        if iMinDistance == -1 or iDistance < iMinDistance or not bBothDirections:
                            bBothDirections = True
                            iMinDistance = iDistance
                            pBestPlayerCity = pPlayerCity
                            pBestNeighborCity = pNeighborCity
                            # Wenn Route, die in beide Richtungen funktioniert, gefunden wurde, abbrechen (spart Rechenzeit)
                            # Route ist zwar ggf. nicht optimal, aber gut genug (beide Richtungen, Abstand <= iMaxDistance)
                            break
                    elif (bDirection1 or bDirection2) and not bBothDirections:
                        if iMinDistance == -1 or iDistance < iMinDistance:
                            iMinDistance = iDistance
                            pBestPlayerCity = pPlayerCity
                            pBestNeighborCity = pNeighborCity
            # Wenn Route, die in beide Richtungen funktioniert, gefunden wurde, abbrechen (spart Rechenzeit)
            # Route ist zwar ggf. nicht optimal, aber gut genug (beide Richtungen, Abstand <= iMaxDistance)
            if bBothDirections:
                break
        if bBothDirections:
            break

    if pBestPlayerCity is not None and pBestNeighborCity is not None:
        # s = pPlayer.getName()
        # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, "Stadt gefunden " + s, None, 2, None, ColorTypes(7), pUnit.getX(), pUnit.getY(), False, False)
        lPlayerLuxuries = _getCityLuxuries(pBestPlayerCity)
        lNeighborLuxuries = _getCityLuxuries(pBestNeighborCity)
        eBonus1 = -1
        eBonus2 = -1
        for eBonus in lPlayerLuxuries:
            if not pBestNeighborCity.hasBonus(eBonus):
                eBonus1 = eBonus
                break
        for eBonus in lNeighborLuxuries:
            if not pBestPlayerCity.hasBonus(eBonus):
                eBonus2 = eBonus
                break
        CvUtil.addScriptData(pUnit, "autX1", pBestPlayerCity.getX())
        CvUtil.addScriptData(pUnit, "autY1", pBestPlayerCity.getY())
        CvUtil.addScriptData(pUnit, "autX2", pBestNeighborCity.getX())
        CvUtil.addScriptData(pUnit, "autY2", pBestNeighborCity.getY())
        CvUtil.addScriptData(pUnit, "autB1", eBonus1) # bonus bought in city 1
        CvUtil.addScriptData(pUnit, "autB2", eBonus2) # bonus bought in city 2
        CvUtil.addScriptData(pUnit, "autA", 1)
        return True

    return False

# Returns list of iPlayer's cities and the luxuries in their reach (saleable). Cities without luxuries are skipped.
# e.g. returns [ [pCity1, [3, 34, 7]], [pCity2, [3, 7, 13] ]
def _getPlayerLuxuryCities(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    lCityList = []
    (loopCity, pIter) = pPlayer.firstCity(False)
    while loopCity:
        if not loopCity.isNone() and loopCity.getOwner() == pPlayer.getID(): #only valid cities
            lLuxuryGoods = _getCityLuxuries(loopCity)
            if lLuxuryGoods:
                lCityList.append([loopCity, lLuxuryGoods])
        (loopCity, pIter) = pPlayer.nextCity(pIter, False)
    return lCityList

# Returns list of the luxuries in reach of pCity (saleable). Used by AI trade route determination.
def _getCityLuxuries(pCity):
    lBonuses = getCitySaleableGoods(pCity, -1)
    lBonuses2 = CvUtil.getIntersection(L.LBonusRarity, lBonuses)
    if lBonuses2:
        return lBonuses2
    lBonuses2 = CvUtil.getIntersection(L.LBonusLuxury, lBonuses)
    if lBonuses2:
        return lBonuses2
    return lBonuses

############# Cities with special bonus order #################
# tsb: TradeSpecialBonus
# tst: TradeSpecialTurns
def doUpdateCitiesWithSpecialBonus(iGameTurn):
    global iCitiesSpecialBonus
    # Cities mit Special Trade Bonus herausfinden
    for i in range(gc.getMAX_PLAYERS()):
        loopPlayer = gc.getPlayer(i)
        if loopPlayer.isAlive() and not loopPlayer.isBarbarian():
            (loopCity, pIter) = loopPlayer.firstCity(False)
            while loopCity:
                if not loopCity.isNone() and loopCity.getOwner() == loopPlayer.getID(): #only valid cities
                    iTurn = CvUtil.getScriptData(loopCity, ["tst"], -1)
                    if iTurn != -1 and iTurn <= iGameTurn:
                        eBonus = CvUtil.getScriptData(loopCity, ["tsb"], -1)
                        CvUtil.removeScriptData(loopCity, "tsb")
                        CvUtil.removeScriptData(loopCity, "tst")
                        iCitiesSpecialBonus -= 1
                        if eBonus != -1:
                            iCityOwner = loopCity.getOwner()
                            pPlayer = gc.getPlayer(iCityOwner)
                            pTeam = gc.getTeam(pPlayer.getTeam())
                            iActivePlayer = gc.getGame().getActivePlayer()
                            if pTeam.isHasMet(gc.getPlayer(iActivePlayer).getTeam()):
                                CyInterface().addMessage(iActivePlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_1", (loopCity.getName(), gc.getBonusInfo(eBonus).getDescription())), None, 2, None, ColorTypes(13), 0, 0, False, False)
                (loopCity, pIter) = loopPlayer.nextCity(pIter, False)

def addCityWithSpecialBonus(iGameTurn):
    global iCitiesSpecialBonus
    lTurns = [20, 25, 30, 35, 40]
    # Max 3 cities
    if iCitiesSpecialBonus >= iMaxCitiesSpecialBonus:
        return

    lNewCities = []
    for i in range(gc.getMAX_PLAYERS()):
        loopPlayer = gc.getPlayer(i)
        if loopPlayer.isAlive() and not loopPlayer.isHuman() and not loopPlayer.isBarbarian():
            (loopCity, pIter) = loopPlayer.firstCity(False)
            while loopCity:
                if not loopCity.isNone() and loopCity.getOwner() == loopPlayer.getID(): #only valid cities
                    iTurn = CvUtil.getScriptData(loopCity, ["tst"], -1)
                    if iTurn == -1:
                        lNewCities.append(loopCity)
                (loopCity, pIter) = loopPlayer.nextCity(pIter, False)

    iTry = 0
    lNewBonus = []
    while lNewCities and iTry < 3:
        # Stadt auswaehlen
        pCity = lNewCities[CvUtil.myRandom(len(lNewCities), "city addCityWithSpecialBonus")]
        # Dauer auswaehlen
        iTurns = lTurns[CvUtil.myRandom(len(lTurns), "turns addCityWithSpecialBonus")]
        # Bonusgut herausfinden
        for iBonus in L.LBonusLuxury + L.LBonusRarity:
            if not pCity.hasBonus(iBonus):
                lNewBonus.append(iBonus)
        # Bonus setzen wenn die Stadt nicht eh schon alles hat.
        if lNewBonus:
            # Globale Variable setzen
            iCitiesSpecialBonus += 1
            CvUtil.addScriptData(pCity, "tst", iGameTurn+iTurns)
            eBonus = lNewBonus[CvUtil.myRandom(len(lNewBonus), "bonus addCityWithSpecialBonus")]
            CvUtil.addScriptData(pCity, "tsb", eBonus)
            iCityOwner = pCity.getOwner()
            pPlayer = gc.getPlayer(iCityOwner)
            pTeam = gc.getTeam(pPlayer.getTeam())
            iActivePlayer = gc.getGame().getActivePlayer()
            if pTeam.isHasMet(gc.getPlayer(iActivePlayer).getTeam()):
                CyInterface().addMessage(iActivePlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_2", (pCity.getName(), gc.getBonusInfo(eBonus).getDescription())), None, 2, None, ColorTypes(11), 0, 0, False, False)
            break
        else:
            iTry += 1
            lNewCities.remove(pCity)

# In doSellBonus
def _doCheckCitySpecialBonus(pUnit, pCity, eBonus):
    global iCitiesSpecialBonus
    eCityBonus = CvUtil.getScriptData(pCity, ["tsb"], -1)
    if eCityBonus != -1 and eCityBonus == eBonus:
        iCitiesSpecialBonus -= 1
        CvUtil.removeScriptData(pCity, "tsb")
        CvUtil.removeScriptData(pCity, "tst")
        iPlayer = pUnit.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        if iPlayer != gc.getGame().getActivePlayer():
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_3", (pPlayer.getName(),)), None, 2, None, ColorTypes(13), 0, 0, False, False)
        else:
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_4", ("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)
        # Belohnungen
        lGift = []
        # Military unit as gift:
        if CvUtil.myRandom(5, "Military unit as gift") == 1:
            eCiv = gc.getCivilizationInfo(gc.getPlayer(pCity.getOwner()).getCivilizationType())
            eOrigCiv = gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType())
            lUnits = [
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_WAR_ELEPHANT")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CAMEL_CATAPHRACT")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR_HORSE")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL4")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL5")),
                eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR")),
            ]
            # Mounted
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                lUnits.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
                # Sonderweg mit eOrigCiv
                if pCity.canTrain(eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")), 0, 0):
                    lGift.append(eOrigCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")))
                if pCity.canTrain(eCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")), 0, 0):
                    lGift.append(eOrigCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")))
            for iUnit in lUnits:
                if pCity.canTrain(iUnit, 0, 0):
                    lGift.append(iUnit)
            # Set AI Type
            iNewUnitAIType = UnitAITypes.UNITAI_ATTACK
            # Message : Stadt schenkt Truppen
            if pPlayer.isHuman():
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_5", ("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)
        # Standard gift
        if not lGift:
            lGift.append(gc.getInfoTypeForString("UNIT_GOLDKARREN"))
            # Slave
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")) and not pCity.isHasReligion(gc.getInfoTypeForString("RELIGION_CHRISTIANITY")):
                lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
            # Mounted
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
            # Elefant
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
            # Kamel
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_CAMEL"))
            # Set AI Type
            iNewUnitAIType = UnitAITypes.NO_UNITAI
            # Message : Stadt schenkt Kostbarkeiten
            if pPlayer.isHuman():
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TRADE_SPECIAL_6", ("",)), "AS2D_WELOVEKING", 2, None, ColorTypes(13), 0, 0, False, False)
        for _ in range(3):
            # Choose units
            iNewUnit = lGift[CvUtil.myRandom(len(lGift), "Choose gift units")]
            # Create units
            pPlayer.initUnit(iNewUnit, pCity.getX(), pCity.getY(), iNewUnitAIType, DirectionTypes.DIRECTION_SOUTH)
