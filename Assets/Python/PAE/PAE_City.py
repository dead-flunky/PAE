# Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil

import PAE_Sklaven
import PAE_Unit
import PAE_Mercenaries

# Defines
gc = CyGlobalContext()

# PAE Stadtstatus
iPopDorf = 3
iPopStadt = 6
iPopProvinz = 12
iPopMetropole = 20

# PAE Statthaltertribut
PAEStatthalterTribut = {}  # Statthalter koennen nur 1x pro Runde entlohnt werden


def onModNetMessage(argsList):
    iData0, iData1, iData2, iData3, iData4 = argsList
    iData5 = iData4
    iData4 = iData3
    iData3 = iData2
    iData2 = iData1
    iData1 = iData0

    # Provinzhauptstadt Statthalter Tribut
    if iData1 == 678:
        # iData2 = iPlayer, iData3 = CityID, iData4 = Antwort [0,1,2] , iData5 = Tribut
        pPlayer = gc.getPlayer(iData2)
        pCity = pPlayer.getCity(iData3)
        iTribut = iData5
        iTribut2 = iData5 / 2

        iGold = pPlayer.getGold()
        bDoRebellion = False
        iAddHappiness = -1
        bPaid = False
        iRandRebellion = CvUtil.myRandom(100, "iRandRebellion")

        if iGold >= iTribut:
            if iData4 == 0:
                pPlayer.changeGold(-iTribut)
                iAddHappiness = 2
                bPaid = True
            elif iData4 == 1:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
                bPaid = True

        elif iGold >= iTribut2:
            if iData4 == 0:
                pPlayer.changeGold(-iTribut2)
                iAddHappiness = 1
                bPaid = True

        elif iGold > 0:
            if iData4 == 0:
                pPlayer.setGold(0)
                iAddHappiness = 0

        # Happiness setzen (Bug bei CIV, Man muss immer den aktuellen Wert + die Aenderung setzen)
        iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
        iBuildingHappiness = pCity.getBuildingHappiness(iBuilding)
        pCity.setBuildingHappyChange(gc.getBuildingInfo(iBuilding).getBuildingClassType(), iBuildingHappiness + iAddHappiness)

        # Chance einer Rebellion: Unhappy Faces * Capital Distance
        iCityHappiness = pCity.happyLevel() - pCity.unhappyLevel(0)
        if iCityHappiness < 0:
            # Abstand zur Hauptstadt
            if not pPlayer.getCapitalCity().isNone() and pPlayer.getCapitalCity() is not None:
                iDistance = plotDistance(pPlayer.getCapitalCity().getX(), pPlayer.getCapitalCity().getY(), pCity.getX(), pCity.getY())
            else:
                iDistance = 20
            iChance = iCityHappiness * (-1) * iDistance
            if iChance > iRandRebellion:
                bDoRebellion = True

        if bDoRebellion:
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_NEG", (pCity.getName(),)), "AS2D_REVOLTSTART", 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_NEG", (pCity.getName(), )))
            popupInfo.addPopup(iData2)
            doProvinceRebellion(pCity)
        elif bPaid:
            CyInterface().addMessage(iData2, True, 10, CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_REACTION_POS", (pCity.getName(),)), "AS2D_BUILD_BANK", 2, None, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
            szBuffer = CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN", (pCity.getName(), ))
            iRand = 1 + CvUtil.myRandom(23, "provinz_thx")
            szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_"+str(iRand), ())

            # 1 Unit as gift:
            lGift = []
            # Auxiliar
            lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR")))
            if pCity.canTrain(gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"), 0, 0):
                lGift.append(gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"))
            # Food
            lGift.append(gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"))
            # Slave
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")):
                lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
            # Mounted
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_CHARIOT"), 0, 0):
                    lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_CHARIOT")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"), 0, 0):
                    lGift.append(gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER")))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"), 0, 0):
                    lGift.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
            # Elefant
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"), 0, 0):
                    lGift.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))
            # Kamel
            if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")):
                lGift.append(gc.getInfoTypeForString("UNIT_CARAVAN"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"), 0, 0):
                    lGift.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                if pCity.canTrain(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"), 0, 0):
                    lGift.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))

            # Choose unit
            iRand = CvUtil.myRandom(len(lGift), "unitgift")

            # Auxiliars as gift:
            #iAnz = 1 + CvUtil.myRandom(3, "Auxiliars as gift")
            #if iAnz == 1: szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2_SINGULAR",("", ))
            #else: szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2_PLURAL",(iAnz, ))
            szBuffer = szBuffer + CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_THX_MAIN2", (gc.getUnitInfo(lGift[iRand]).getDescriptionForm(0),))

            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(szBuffer)
            popupInfo.addPopup(iData2)

            pPlayer.initUnit(lGift[iRand], pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

    # Statthalter / Tribut
    if iData1 == 737:
        # iData1, iData2, ... , iData5
        # First:  737, iCityID, iPlayer, -1, -1
        # Second: 737, iCityID, iPlayer, iButtonID (Typ), -1
        # Third:  737, iCityID, iPlayer, iTyp, iButtonID
        pPlayer = gc.getPlayer(iData3)
        pCity = pPlayer.getCity(iData2)

        if iData4 == -1:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_0", (pCity.getName(),)))
            popupInfo.setData1(iData2) # CityID
            popupInfo.setData2(iData3) # iPlayer
            popupInfo.setData3(-1) # iTyp (Einfluss oder Tribut)
            popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

            # Button 0: Einfluss verbessern
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_1", ()), "Art/Interface/Buttons/Actions/button_statthalter_einfluss.dds")
            # Button 1: Tribut fordern
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_2", ()), ",Art/Interface/Buttons/Civics/Decentralization.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,4,1")

            # Cancel button
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
            popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
            popupInfo.addPopup(iData3)

        # -- Einfluss verbessern --
        elif iData4 == 0:

            iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
            iBuildingHappiness = pCity.getExtraHappiness()
            # Button 0: kleine Spende
            iGold1 = pCity.getPopulation() * 16
            iHappy1 = 1
            # Button 1: grosse Spende
            iGold2 = pCity.getPopulation() * 28
            iHappy2 = 2

            # Gold-Check
            if iData5 == 0 and pPlayer.getGold() < iGold1:
                iData5 = -1
            if iData5 == 1 and pPlayer.getGold() < iGold2:
                iData5 = -1

            if iData5 == -1:

                szText = CyTranslator().getText("[H2]", ())\
                        + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_1", ()).upper()\
                        + CyTranslator().getText(r"[\H2][NEWLINE]", ())
                szText += CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG", ())
                szText += u": %d " % (abs(iBuildingHappiness))
                if iBuildingHappiness < 0:
                    szText += CyTranslator().getText("[ICON_UNHAPPY]", ())
                else:
                    szText += CyTranslator().getText("[ICON_HAPPY]", ())

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(szText)
                popupInfo.setData1(iData2) # CityID
                popupInfo.setData2(iData3) # iPlayer
                popupInfo.setData3(iData4) # iTyp (Einfluss oder Tribut)
                popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

                # Button 0: kleine Spende
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_GOLD1", (iGold1, iHappy1)), "Art/Interface/Buttons/Actions/button_statthalter_gold1.dds")
                # Button 1: grosse Spende
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_GOLD2", (iGold2, iHappy2)), "Art/Interface/Buttons/Actions/button_statthalter_gold2.dds")

                # Cancel button
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
                popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
                popupInfo.addPopup(iData3)

            # Triumphzug
            elif iData5 == 0:
                pCity.changeExtraHappiness(iHappy1)
                pPlayer.changeGold(-iGold1)
                iImmo = 2

            # Mehrtaegiges Fest
            elif iData5 == 1:
                pCity.changeExtraHappiness(iHappy2)
                pPlayer.changeGold(-iGold2)
                iImmo = 3

            if iData5 == 0 or iData5 == 1:
                if iData3 == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound("AS2D_COINS")
                    CyAudioGame().Play2DSound("AS2D_WELOVEKING")

                # Einheiten sind nun beschaeftigt
                pPlot = pCity.plot()
                iNumUnits = pPlot.getNumUnits()
                if iNumUnits > 0:
                    for k in range(iNumUnits):
                        if iData3 == pPlot.getUnit(k).getOwner():
                            pPlot.getUnit(k).setImmobileTimer(iImmo)

                # Do this only once per turn
                PAEStatthalterTribut.setdefault(iData3, 0)
                PAEStatthalterTribut[iData3] = 1

        # -- Tribut fordern --
        elif iData4 == 1:

            iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
            iBuildingHappiness = pCity.getExtraHappiness()
            iUnit1 = gc.getInfoTypeForString("UNIT_GOLDKARREN")
            iUnhappy1 = 2
            iUnit2 = gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
            iUnhappy2 = 1
            iUnit3 = gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")
            iUnhappy3 = 1
            iUnit4 = gc.getInfoTypeForString("UNIT_SLAVE")
            iUnhappy4 = 1

            if iData5 == -1:

                szText = CyTranslator().getText("[H2]", ())\
                        + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_2", ()).upper()\
                        + CyTranslator().getText(r"[\H2][NEWLINE]", ())
                szText += CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG", ())
                szText += u": %d " % (abs(iBuildingHappiness))
                if iBuildingHappiness < 0:
                    szText += CyTranslator().getText("[ICON_UNHAPPY]", ())
                else:
                    szText += CyTranslator().getText("[ICON_HAPPY]", ())

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(szText)
                popupInfo.setData1(iData2) # CityID
                popupInfo.setData2(iData3) # iPlayer
                popupInfo.setData3(iData4) # iTyp (Einfluss oder Tribut)
                popupInfo.setOnClickedPythonCallback("popupStatthalterTribut")

                # Button 0: Goldkarren
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT1", (gc.getUnitInfo(iUnit1).getDescriptionForm(0), iUnhappy1)), gc.getUnitInfo(iUnit1).getButton())
                # Button 1: Hilfstrupp
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT2", (gc.getUnitInfo(iUnit2).getDescriptionForm(0), iUnhappy2)), gc.getUnitInfo(iUnit2).getButton())
                # Button 2: Getreidekarren
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT3", (gc.getUnitInfo(iUnit3).getDescriptionForm(0), iUnhappy3)), gc.getUnitInfo(iUnit3).getButton())
                # Button 3: Sklave
                if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")):
                    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_TRIBUT4", (gc.getUnitInfo(iUnit4).getDescriptionForm(0), iUnhappy4)), gc.getUnitInfo(iUnit4).getButton())

                # Cancel button
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL", ("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
                popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
                popupInfo.addPopup(iData3)

            # Goldkarren
            elif iData5 == 0:
                # pCity.setBuildingHappyChange geht nicht, weil die Stadt auch Negatives positiv anrechnet
                pCity.changeExtraHappiness(-iUnhappy1)
                NewUnit = pPlayer.initUnit(iUnit1, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setImmobileTimer(1)
            # Hilfstrupp
            elif iData5 == 1:
                pCity.changeExtraHappiness(-iUnhappy2)
                NewUnit = pPlayer.initUnit(iUnit2, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                iRand = 1 + CvUtil.myRandom(3, "aux_promo")
                if iRand >= 1:
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
                if iRand >= 2:
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
                if iRand >= 3:
                    NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
                NewUnit.setImmobileTimer(1)
            # Getreide
            elif iData5 == 2:
                pCity.changeExtraHappiness(-iUnhappy3)
                NewUnit = pPlayer.initUnit(iUnit3, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setImmobileTimer(1)
            # Sklaven
            elif iData5 == 3:
                pCity.changeExtraHappiness(-iUnhappy4)
                NewUnit = pPlayer.initUnit(iUnit4, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                NewUnit.setImmobileTimer(1)

            if iData5 > -1:
                if iData3 == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound("AS2D_UNIT_BUILD_UNIT")

                # Do this only once per turn
                PAEStatthalterTribut.setdefault(iData3, 0)
                PAEStatthalterTribut[iData3] = 1

def doMessageCityGrowing(pCity):
    if pCity is None or pCity.isNone():
        return

    if pCity.getFoodTurnsLeft() == 1 and pCity.foodDifference(True) > 0 and not pCity.isFoodProduction() and not pCity.AI_isEmphasize(5):

        # Inits
        iBuildingDorf = gc.getInfoTypeForString("BUILDING_KOLONIE")
        iBuildingStadt = gc.getInfoTypeForString("BUILDING_STADT")
        iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
        iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")

        kBuildingDorf = gc.getBuildingInfo(iBuildingDorf)
        kBuildingStadt = gc.getBuildingInfo(iBuildingStadt)
        kBuildingProvinz = gc.getBuildingInfo(iBuildingProvinz)
        kBuildingMetropole = gc.getBuildingInfo(iBuildingMetropole)

        iPlayer = pCity.getOwner()
        # ---

        # MESSAGE: city will grow / Stadt wird wachsen
        iPop = pCity.getPopulation() + 1
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_WILL_GROW", (pCity.getName(), iPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

        # MESSAGE: city gets/is unhappy / Stadt wird/ist unzufrieden
        iBonusHealth = 0
        iBonusHappy = 0
        if iPop == iPopDorf:
            iBonusHealth = kBuildingDorf.getHealth()
            iBonusHappy = kBuildingDorf.getHappiness()
            # for iBonus in gc.getNumBonuses():
                # iAddHealth = kBuildingDorf.getBonusHealthChanges(iBonus)
                # if iAddHealth != -1:
                  # iBonusHealth += iAddHealth
                # iAddHappy = kBuildingDorf.getBonusHappinessChanges(iBonus)
                # if iAddHappy != -1:
                  # iBonusHappy += iAddHappy
        elif iPop == iPopStadt:
            iBonusHealth = kBuildingStadt.getHealth()
            iBonusHappy = kBuildingStadt.getHappiness()
        elif iPop == iPopProvinz:
            iBonusHealth = kBuildingProvinz.getHealth()
            iBonusHappy = kBuildingProvinz.getHappiness()
        elif iPop == iPopMetropole:
            iBonusHealth = kBuildingMetropole.getHealth()
            iBonusHappy = kBuildingMetropole.getHappiness()

        if pCity.happyLevel() - pCity.unhappyLevel(0) + iBonusHappy <= 0:
            if pCity.happyLevel() - pCity.unhappyLevel(0) == 0:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHAPPY", (pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            else:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHAPPY", (pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

        # MESSAGE: city gets/is unhealthy / Stadt wird/ist ungesund
        if pCity.goodHealth() - pCity.badHealth(False) + iBonusHealth <= 0:
            if pCity.goodHealth() - pCity.badHealth(False) == 0:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHEALTY", (pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            else:
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHEALTY", (pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # -----------------


# PAE City status --------------------------
# Check City colony or province after events
# once getting a province: keep being a province
def doCheckCityState(pCity):
    if pCity is None or pCity.isNone():
        return

    iBuildingSiedlung = gc.getInfoTypeForString("BUILDING_SIEDLUNG")
    iBuildingKolonie = gc.getInfoTypeForString("BUILDING_KOLONIE")
    iBuildingCity = gc.getInfoTypeForString("BUILDING_STADT")
    iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
    iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")

    if pCity.getNumRealBuilding(iBuildingSiedlung) == 0:
        pCity.setNumRealBuilding(iBuildingSiedlung, 1)

    if pCity.getPopulation() >= iPopDorf and pCity.getNumRealBuilding(iBuildingKolonie) == 0:
        pCity.setNumRealBuilding(iBuildingKolonie, 1)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_1", (pCity.getName(), 0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingKolonie).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    if pCity.getPopulation() >= iPopStadt and pCity.getNumRealBuilding(iBuildingCity) == 0:
        pCity.setNumRealBuilding(iBuildingCity, 1)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_2", (pCity.getName(), 0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Wachstum: Meldungen von kleinerem Status beginnend
    if pCity.getPopulation() >= iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 0:
        pCity.setNumRealBuilding(iBuildingProvinz, 1)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_3", (pCity.getName(), 0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() >= iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 0:
        pCity.setNumRealBuilding(iBuildingMetropole, 1)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_5", (pCity.getName(), 0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingMetropole).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Bev.rueckgang: Meldungen von hoeheren Status beginnend
    if pCity.getPopulation() < iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 1:
        pCity.setNumRealBuilding(iBuildingMetropole, 0)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_6", (pCity.getName(), 0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() < iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 1:
        pCity.setNumRealBuilding(iBuildingProvinz, 0)
        if gc.getPlayer(pCity.getOwner()).isHuman():
            CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_4", (pCity.getName(), 0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # AI and its slaves
    if not gc.getPlayer(pCity.getOwner()).isHuman():
        PAE_Sklaven.doAIReleaseSlaves(pCity)


# --------------------------------
# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckTraitBuildings(pCity):
    pOwner = gc.getPlayer(pCity.getOwner())
    # lokale Trait-Gebaeude
    iCreativeLocal = gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_LOCAL")
    eTraitCreative = gc.getInfoTypeForString("TRAIT_CREATIVE")
    # Tech, ab der Creative_Local gesetzt wird
    iTechCreativeLocal = gc.getInfoTypeForString("TECH_ALPHABET")

    # Alle nicht passenden Gebaeude entfernen
    # Nur lokale hinzufuegen, globale nicht
    if pOwner.hasTrait(eTraitCreative) and gc.getTeam(pOwner.getTeam()).isHasTech(iTechCreativeLocal):
        pCity.setNumRealBuilding(iCreativeLocal, 1)
    else:
        pCity.setNumRealBuilding(iCreativeLocal, 0)

def doCheckGlobalTraitBuildings(iPlayer, pCity=None, iOriginalOwner=-1):
    pOwner = gc.getPlayer(iPlayer)
    lGlobal = [
        (gc.getInfoTypeForString("TRAIT_MARITIME"), gc.getInfoTypeForString("BUILDING_TRAIT_MARITIME_GLOBAL")),
        (gc.getInfoTypeForString("TRAIT_CREATIVE"), gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_GLOBAL")),
        (gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL"), gc.getInfoTypeForString("BUILDING_TRAIT_PHILOSOPHICAL_GLOBAL"))
    ]

    for (iTrait, iBuilding) in lGlobal:
        # es wurde ein Traitbuilding erobert
        if pCity is not None and pCity.getNumRealBuilding(iBuilding) > 0:
            pCity.setNumRealBuilding(iBuilding, 0)
            if iOriginalOwner != -1:
                doCheckGlobalBuilding(iOriginalOwner, iBuilding)

        if pOwner.hasTrait(iTrait):
            doCheckGlobalBuilding(iPlayer, iBuilding)


# Methode fuer lokalen Gebrauch
def doCheckGlobalBuilding(iPlayer, iBuilding):
    pPlayer = gc.getPlayer(iPlayer)
    (loopCity, pIter) = pPlayer.firstCity(False)
    if loopCity is not None and not loopCity.isNone():
        loopCity.setNumRealBuilding(iBuilding, 1)
        iCount = 0
        while loopCity:
            if loopCity.getNumBuilding(iBuilding) > 0:
                iCount += 1
                if iCount > 1:
                    loopCity.setNumRealBuilding(iBuilding, 0)
            (loopCity, pIter) = pPlayer.nextCity(pIter, False)

# Begin Inquisition -------------------------------

def doInquisitorPersecution(pCity, pUnit):
    pPlayer = gc.getPlayer(pCity.getOwner())
    iPlayer = pPlayer.getID()

    iNumReligions = gc.getNumReligionInfos()
    # HI soll PopUp bekommen
    if pPlayer.isHuman():
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_INQUISITION", (pCity.getName(), )))
        popupInfo.setData1(iPlayer)
        popupInfo.setData2(pCity.getID())
        popupInfo.setData3(pUnit.getID())
        popupInfo.setOnClickedPythonCallback("popupReliaustreibung") # EntryPoints/CvScreenInterface und CvGameUtils / 704
        for iReligion in range(iNumReligions):
            if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
                popupInfo.addPythonButton(gc.getReligionInfo(iReligion).getText(), gc.getReligionInfo(iReligion).getButton())
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_INQUISITION_CANCEL", ("", )), "Art/Interface/Buttons/General/button_alert_new.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
    pUnit.kill(True, -1)  # RAMK_CTD

def doInquisitorPersecution2(iPlayer, iCity, iButton, iReligion, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pCity = pPlayer.getCity(iCity)
    szButton = gc.getUnitInfo(gc.getInfoTypeForString("UNIT_INQUISITOR")).getButton()
    iStateReligion = pPlayer.getStateReligion()
    iNumReligions = gc.getNumReligionInfos()
    # gets a list of all religions in the city except state religion
    lCityReligions = []
    for iReligionLoop in range(iNumReligions):
        if pCity.isHasReligion(iReligionLoop):
            if pCity.isHolyCityByType(iReligionLoop) == 0 and iReligionLoop != iStateReligion:
                lCityReligions.append(iReligionLoop)

    # Wenn die Religion ueber PopUp kommt, muss sie mittels Buttonreihenfolge gefunden werden
    if iReligion == -1:
        iReligion = lCityReligions[iButton]

    if iReligion != -1:
        if iReligion != iStateReligion:
            iHC = -25
        else:
            iHC = 15
        pUnit = pPlayer.getUnit(iUnit)
        if pUnit is not None and not pUnit.isNone():
            # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
            pUnit.kill(True, -1)  # RAMK_CTD

        # Does Persecution succeed
        iRandom = CvUtil.myRandom(100, "pers_success")
        if iRandom < 95 - (len(lCityReligions) * 5) + iHC:
            pCity.setHasReligion(iReligion, 0, 0, 0)
            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION", (pCity.getName(),)), "AS2D_PLAGUE", 2, szButton, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

            # remove its buildings
            iRange = gc.getNumBuildingInfos()
            for iBuildingLoop in range(iRange):
                if pCity.isHasBuilding(iBuildingLoop):
                    pBuilding = gc.getBuildingInfo(iBuildingLoop)
                    iRequiredReligion = pBuilding.getPrereqReligion()
                    # Wunder sollen nicht betroffen werden
                    iBuildingClass = pBuilding.getBuildingClassType()
                    thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
                    if iRequiredReligion == iReligion and thisBuildingClass.getMaxGlobalInstances() != 1:
                        pCity.setNumRealBuilding(iBuildingLoop, 0)
                        #if pPlayer.isHuman():
                            ##Meldung dass das Gebaeude zerstoert wurde
                            #CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_Bildersturm",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # increasing Anger or Sympathy for an AI
            iRange = gc.getMAX_PLAYERS()
            for iSecondPlayer in range(iRange):
                pSecondPlayer = gc.getPlayer(iSecondPlayer)
                pReligion = gc.getReligionInfo(iReligion)

                # increases Anger for all AIs which have this religion as State Religion
                if iReligion == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive():
                    pSecondPlayer.AI_changeAttitudeExtra(iPlayer, -2)
                # increases Sympathy for all AIs which have the same State Religion as the inquisitor
                elif pPlayer.getStateReligion() == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive():
                    pSecondPlayer.AI_changeAttitudeExtra(iPlayer, 1)

                # info for all
                if pSecondPlayer.isHuman():
                    iSecTeam = pSecondPlayer.getTeam()
                    if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                        CyInterface().addMessage(iSecondPlayer, True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL", (pCity.getName(), pReligion.getText())), None, 2, szButton, ColorTypes(10), pCity.getX(), pCity.getY(), True, True)

            # info for the player
            CyInterface().addMessage(iPlayer, True, 20, CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_NEG", (pCity.getName(), pReligion.getText())), None, 2, szButton, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            CyInterface().addMessage(iPlayer, True, 20, CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_POS", (pCity.getName(), pReligion.getText())), None, 2, szButton, ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

            # decrease population by 1, even if mission fails
            if pCity.getPopulation() > 1:
                pCity.changePopulation(-1)
                doCheckCityState(pCity)

        # Persecution fails
        elif pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 15, CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_FAIL", (pCity.getName(),)), "AS2D_SABOTAGE", 2, szButton, ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

    # City Revolt
    pCity.changeOccupationTimer(1)
  # ------

# end Inquisition / Religionsaustreibung

def doTurnCityRevolt(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = pCity.plot()
    bCityIsInRevolt = False

    # Conquered city (% culture / 10)
    iOriginalOwner = pCity.getOriginalOwner()
    if iOriginalOwner != iPlayer and gc.getPlayer(iOriginalOwner).isAlive():
        iForeignCulture = pPlot.calculateTeamCulturePercent(gc.getPlayer(iOriginalOwner).getTeam())
        if iForeignCulture >= 20:
            # Pro Einheit 1% Bonus
            if CvUtil.myRandom(100, "doTurnCityRevolt1") + pPlot.getNumDefenders(iPlayer) < iForeignCulture / 10:
                bCityIsInRevolt = True
                iCityRevoltTurns = 4
                text = "TXT_KEY_MESSAGE_CITY_REVOLT_YEARNING"
    # Nation is in anarchy (20%, AI 5%)
    if pPlayer.getAnarchyTurns() > 0:
        if pPlayer.isHuman():
            iTmp = 5
        else:
            iTmp = 20
        if CvUtil.myRandom(iTmp, "doTurnCityRevolt2") == 0:
            bCityIsInRevolt = True
            iCityRevoltTurns = pPlayer.getAnarchyTurns()
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_ANARCHY"
    # city has no state religion (3%, AI 1%)
    iRel = pPlayer.getStateReligion()
    if iRel != -1 and not pCity.isHasReligion(iRel):
        iBuilding = gc.getInfoTypeForString("BUILDING_STADT")
        if pCity.isHasBuilding(iBuilding):
            if pPlayer.isHuman():
                iTmp = 30
            else:
                iTmp = 100
            if CvUtil.myRandom(iTmp, "doTurnCityRevolt3") == 0:
                bCityIsInRevolt = True
                iCityRevoltTurns = 4
                text = "TXT_KEY_MESSAGE_CITY_REVOLT_RELIGION"
    # city is unhappy (3%, AI 1%)
    if pCity.unhappyLevel(0) > pCity.happyLevel():
        if pPlayer.isHuman():
            iTmp = 30
        else:
            iTmp = 100
        if CvUtil.myRandom(iTmp, "doTurnCityRevolt4") == 0:
            bCityIsInRevolt = True
            iCityRevoltTurns = 4
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_UNHAPPINESS"
    # high taxes
    # PAE V: not for AI
    if pPlayer.getCommercePercent(0) > 50 and pPlayer.isHuman():
        iChance = int((pPlayer.getCommercePercent(0) - 50) / 5)
        # Pro Happy Citizen 5% Nachlass
        iChance = iChance - pCity.happyLevel() + pCity.unhappyLevel(0)
        if iChance > 0 and CvUtil.myRandom(100, "doTurnCityRevolt5") < iChance:
            bCityIsInRevolt = True
            iCityRevoltTurns = iChance
            text = "TXT_KEY_MESSAGE_CITY_REVOLT_TAXES"

    # City Revolt PopUp / Human and AI
    if bCityIsInRevolt:
        # Einheiten senken Dauer
        if pPlot.getNumUnits() > pCity.getPopulation():
            iCityRevoltTurns = 2

        # Human PopUp 675
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText(text, (pCity.getName(),)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText(text, (pCity.getName(),)))
            popupInfo.setData1(iPlayer)
            popupInfo.setData2(pCity.getID())
            popupInfo.setData3(iCityRevoltTurns)
            popupInfo.setOnClickedPythonCallback("popupRevoltPayment")
            iGold = pCity.getPopulation()*10
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_1", (iGold,)), "")
            iGold = pCity.getPopulation()*5
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_2", (iGold,)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_REVOLT_CANCEL", ()), "")
            popupInfo.addPopup(iPlayer)

        # AI will pay (90%) if they have the money
        elif CvUtil.myRandom(100, "doTurnCityRevolt6") < 90:
            if pPlayer.getGold() > pCity.getPopulation() * 10:
                iBetrag = pCity.getPopulation() * 10
                iChance = 20
            elif pPlayer.getGold() > pCity.getPopulation() * 5:
                iBetrag = pCity.getPopulation() * 5
                iChance = 50
            else:
                iBetrag = 0
                iChance = 100
            pPlayer.changeGold(iBetrag)
            # even though, there is a chance of revolting
            if CvUtil.myRandom(100, "doTurnCityRevolt7") < iChance:
                # pCity.setOccupationTimer(iCityRevoltTurns)
                doCityRevolt(pCity, iCityRevoltTurns)
        else:
            # pCity.setOccupationTimer(iCityRevoltTurns)
            doCityRevolt(pCity, iCityRevoltTurns)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtrevolte PopUp (Zeile 4222)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

  # City Revolt
  # iTurns = deaktiv

def doCityRevolt(pCity, iTurns):
    pPlot = pCity.plot()

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City Revolt (Zeile 6485)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Strafe verschaerfen
    #iTurns = iTurns * 2

    # Einheiten stilllegen
    iRange = pPlot.getNumUnits()
    for iUnit in range(iRange):
        pPlot.getUnit(iUnit).setDamage(60, -1)
        if CvUtil.myRandom(2, "cityRevolt") == 1:
            pPlot.getUnit(iUnit).setImmobileTimer(iTurns)

    # Stadtaufruhr
    pCity.changeHurryAngerTimer(iTurns)

    iTurns = int(iTurns / 2)
    if iTurns < 2:
        iTurns = 2
    #pCity.changeOccupationTimer (iTurns)
    pCity.setOccupationTimer(iTurns)

    # iPlayer = pCity.getOwner()
    # pPlayer = gc.getPlayer(iPlayer)
#    if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#       iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_DESPOT_REVOLT')
#       if iEvent != -1 and gc.getGame().isEventActive(iEvent):
#          triggerData = pPlayer.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iPlayer, pCity.getID(), -1, -1, -1, -1)
#       else: pCity.setOccupationTimer(2)
#    else: pCity.setOccupationTimer(2)


# --- renegading city
# A nearby city of pCity will revolt
def doNextCityRevolt(iX, iY, iOwner, iAttacker):
    if iOwner != -1 and iOwner != gc.getBARBARIAN_PLAYER():
        pOwner = gc.getPlayer(iOwner)
        if pOwner.getNumCities() > 1:
            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Next City Revolt (Zeile 4766)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Stadtentfernung messen und naeheste Stadt definieren / die Stadt soll innerhalb 10 Plots entfernt sein.
            iRevoltCity = -1
            iCityCheck = -1
            # City with forbidden palace shall not revolt
            #~ if gc.getTeam(pOwner.getTeam()).isHasTech(gc.getInfoTypeForString('TECH_POLYARCHY')): iBuilding = gc.getInfoTypeForString('BUILDING_PRAEFECTUR')
            #~ else: iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
            iRange = pOwner.getNumCities()
            for i in range(iRange):
                pLoopCity = pOwner.getCity(i)
                if pLoopCity is not None and not pLoopCity.isNone():
                    if not pLoopCity.isCapital() and pLoopCity.getOccupationTimer() < 1 and not pLoopCity.isGovernmentCenter() and pLoopCity.getOwner() != iAttacker:
                        tmpX = pLoopCity.getX()
                        tmpY = pLoopCity.getY()
                        iBetrag = plotDistance(iX, iY, tmpX, tmpY)
                        if iBetrag > 0 and iBetrag < 11 and (iCityCheck == -1 or iCityCheck > iBetrag):
                            iCityCheck = iBetrag
                            iRevoltCity = i
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City",i)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Betrag",iBetrag)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Revolt",iRevoltCity)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Stadt soll revoltieren
            if iRevoltCity != -1:
                pCity = pOwner.getCity(iRevoltCity)
                # pCity.setOccupationTimer(3)
                doCityRevolt(pCity, 5)

                # Message for the other city revolt
                if gc.getPlayer(iAttacker).isHuman():
                    iRand = 1 + CvUtil.myRandom(6, "msg_cityRevolt")
                    CyInterface().addMessage(iAttacker, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_1_"+str(iRand), (pCity.getName(), 0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
                elif gc.getPlayer(iOwner).isHuman():
                    iRand = 1 + CvUtil.myRandom(6, "msg_ownerCityRevolt")
                    CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_2_"+str(iRand), (pCity.getName(), 0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # --- next city revolt

def doDesertification(pCity, pUnit):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iCurrentEra = pPlayer.getCurrentEra()
    iUnitCombatType = pUnit.getUnitCombatType()
    if iCurrentEra > 0 and iUnitCombatType > 0:
        if iUnitCombatType in [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"), gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]:
            return

        lNoForgeUnit = [
            gc.getInfoTypeForString("UNIT_WARRIOR"),
            gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
            gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
            gc.getInfoTypeForString("UNIT_HUNTER"),
            gc.getInfoTypeForString("UNIT_SCOUT"),
            gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"),
            gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
            gc.getInfoTypeForString("UNIT_KAMPFHUND"),
            gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
            gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
            gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
            gc.getInfoTypeForString("UNIT_BURNING_PIGS"),
            gc.getInfoTypeForString("UNIT_WORKBOAT"),
            gc.getInfoTypeForString("UNIT_DRUIDE"),
            gc.getInfoTypeForString("UNIT_BRAHMANE"),
            gc.getInfoTypeForString("UNIT_HORSE"),
            gc.getInfoTypeForString("UNIT_CAMEL"),
            gc.getInfoTypeForString("UNIT_ELEFANT")
        ]

        if pUnit.getUnitType() not in lNoForgeUnit:
            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Waldrodung",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            iHolzLager = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
            iMine = gc.getInfoTypeForString("IMPROVEMENT_MINE")

            iFeatForest = gc.getInfoTypeForString("FEATURE_FOREST")
            iFeatSavanna = gc.getInfoTypeForString("FEATURE_SAVANNA")
            iFeatJungle = gc.getInfoTypeForString("FEATURE_JUNGLE")
            iFeatDichterWald = gc.getInfoTypeForString("FEATURE_DICHTERWALD")

            lFeatures = [iFeatForest, iFeatSavanna, iFeatJungle, iFeatDichterWald]
            # nicht bei Zedernholz
            iBonusZedern = gc.getInfoTypeForString("BONUS_ZEDERNHOLZ")

            # Einen guenstigen Plot auswaehlen
            # Priority:
            # 1. Leerer Wald oder Mine
            # 2. Leere Savanne
            # 3. Leerer Dschungel
            # 4. Bewirtschaftetes Feld mit Wald aber ohne Holzlager
            # 5. Dichter Wald
            # 6. Wald im feindlichen Terrain (-1 Beziehung zum Nachbarn), aber nur wenn kein Holzlager drauf is
            PlotArray1 = []
            PlotArray2 = []
            PlotArray3 = []
            PlotArray4 = []
            PlotArray5 = []
            PlotArray6 = []
            PlotArrayX = []

            for iI in range(gc.getNUM_CITY_PLOTS()):
                pLoopPlot = pCity.getCityIndexPlot(iI)
                if pLoopPlot is not None and not pLoopPlot.isNone():
                    iPlotFeature = pLoopPlot.getFeatureType()
                    if iPlotFeature in lFeatures:
                        iPlotImprovement = pLoopPlot.getImprovementType()
                        iLoopPlayer = pLoopPlot.getOwner()
                        if pLoopPlot.getBonusType(iLoopPlayer) != iBonusZedern:
                            if iLoopPlayer == iPlayer:
                                if iPlotImprovement == iMine:
                                    PlotArray1.append(pLoopPlot)
                                if iPlotImprovement == -1:
                                    if iPlotFeature == iFeatForest:
                                        PlotArray1.append(pLoopPlot)
                                    elif iPlotFeature == iFeatSavanna:
                                        PlotArray2.append(pLoopPlot)
                                    elif iPlotFeature == iFeatJungle:
                                        PlotArray3.append(pLoopPlot)
                                    elif iPlotFeature == iFeatDichterWald:
                                        PlotArray5.append(pLoopPlot)
                                elif iPlotImprovement != iHolzLager:
                                    PlotArray4.append(pLoopPlot)

                            elif iPlotImprovement != iHolzLager:
                                if iPlotFeature != iFeatDichterWald:
                                    # PAE V: no unit on the plot (Holzraub)
                                    if pLoopPlot.getNumUnits() == 0:
                                        PlotArray6.append(pLoopPlot)

            # Plot wird ausgewaehlt, nach Prioritaet zuerst immer nur Wald checken, wenn keine mehr da, dann Savanne, etc...
            # Wald: Chance: Bronzezeit: 4%, Eisenzeit: 5%, Klassik: 6%
            if PlotArray1:
                iChance = 30 - iCurrentEra * 5
                if CvUtil.myRandom(iChance, "des1") == 0:
                    PlotArrayX = PlotArray1
            # Savanne: Bronze: 5%, Eisen: 10%, Klassik: 20%
            elif PlotArray2:
                iChance = 20 - iCurrentEra * 5
                if CvUtil.myRandom(iChance, "des2") == 0:
                    PlotArrayX = PlotArray2
            # Dschungel: wie Wald
            elif PlotArray3:
                iChance = 30 - iCurrentEra * 5
                if CvUtil.myRandom(iChance, "des3") == 0:
                    PlotArrayX = PlotArray3
            # Bewirt. Feld ohne Holzlager: wie Savanne
            elif PlotArray4:
                iChance = 20 - iCurrentEra * 5
                if CvUtil.myRandom(iChance, "des4") == 0:
                    PlotArrayX = PlotArray4
            # Dichter Wald: Bronze: 2%, Eisen: 2.5%, Klassik: 3%
            elif PlotArray5:
                iChance = 60 - iCurrentEra * 10
                if CvUtil.myRandom(iChance, "des5") == 0:
                    PlotArrayX = PlotArray5

            # Ausl. Feld 10%, erst wenn es nur mehr 1 Waldfeld gibt (das soll auch bleiben)
            if len(PlotArray1) + len(PlotArray2) + len(PlotArray3) + len(PlotArray4) + len(PlotArray5) < 2:
                PlotArrayX = []  # Feld leeren
                if PlotArray6 and CvUtil.myRandom(10, "des6") == 0:
                    PlotArrayX = PlotArray6

            # Gibts einen Waldplot
            if PlotArrayX:
                iPlot = CvUtil.myRandom(len(PlotArrayX), "des7")
                pPlot = PlotArrayX[iPlot]
                iPlotPlayer = pPlot.getOwner()
                # Auswirkungen Feature (Wald) entfernen, Holzlager entfernen, Nachbar checken
                # Feature (Wald) entfernen
                # Dichten Wald zu normalen Wald machen
                if pPlot.getFeatureType() == iFeatDichterWald:
                    pPlot.setFeatureType(iFeatForest, 0)
                else:
                    pPlot.setFeatureType(-1, 0)
                    # Lumber camp entfernen
                    # Flunky: Holzlager-Felder werden garnicht erst ausgewaehlt
                    #if PlotArrayX[iPlot].getImprovementType() == iHolzLager: PlotArrayX[iPlot].setImprovementType(-1)

                # Meldung
                # Attention: AS2D_CHOP_WOOD is additional defined in XML/Audio/Audio2DScripts.xml   (not used, AS2D_BUILD_FORGE instead)
                if iPlotPlayer == iPlayer:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_1", (pCity.getName(), 0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

                elif iPlotPlayer > -1 and iPlotPlayer != gc.getBARBARIAN_PLAYER():
                    pPlotPlayer = gc.getPlayer(iPlotPlayer)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_2", (pPlotPlayer.getCivilizationShortDescription(0), pPlotPlayer.getCivilizationAdjective(1))), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    if pPlotPlayer.isHuman():
                        CyInterface().addMessage(iPlotPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_3", (pPlayer.getCivilizationShortDescription(0), 0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    pPlotPlayer.AI_changeAttitudeExtra(iPlayer, -1)

    # Feature Waldrodung Ende

# Emigrant -----------------


def doEmigrant(pCity, pUnit):
    pPlot = pCity.plot()
    # Kultur auslesen
    txt = CvUtil.getScriptData(pUnit, ["p", "t"])
    if txt != "":
        iPlayerCulture = int(txt)
    else:
        iPlayerCulture = pUnit.getOwner()
    # Kultur = 100*Pop, max. 1000
    iCulture = pCity.getPopulation() * 100
    iCulture = min(1000, iCulture)
    # Stadt Kultur geben
    pPlot.changeCulture(iPlayerCulture, iCulture, 1)
    # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
    pUnit.kill(True, -1)  # RAMK_CTD

    pCity.changePopulation(1)
    # PAE Provinzcheck
    doCheckCityState(pCity)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant 2 City (Zeile 6458)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# disband city
def doDisbandCity(pCity, pUnit, pPlayer):
    iRand = CvUtil.myRandom(10, "disbandCity")
    if iRand < 8:
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_OK", (pCity.getName(),)), "AS2D_PILLAGE", 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), False, False)
        pPlayer.disband(pCity)
        iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
        pNewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
        pNewUnit.finishMoves()
        pUnit.finishMoves()
    else:
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_NOT_OK", (pCity.getName(),)), "AS2D_CITY_REVOLT", 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), False, False)
        # pUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pUnit.kill(True, -1)  # RAMK_CTD

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant disbands/shrinks City (Zeile 6474)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# Spreading Plague -------------------------
def doSpreadPlague(pCity):
    pCityOrig = pCity
    iX = pCity.getX()
    iY = pCity.getY()
    iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')
    bSpread = False

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pestausbreitung (Zeile 4818)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Umkreis von 5 Feldern
    iRange = 5
    iCityCheck = 0
    for i in range(-iRange, iRange+1):
        for j in range(-iRange, iRange+1):
            sPlot = plotXY(iX, iY, i, j)
            if sPlot.isCity():
                sCity = sPlot.getPlotCity()
                if sCity.isConnectedTo(pCity) and not sCity.isHasBuilding(iBuildingPlague) and sCity.getPopulation() > 3:
                    tmpX = sCity.getX()
                    tmpY = sCity.getY()
                    iBetrag = plotDistance(iX, iY, tmpX, tmpY)
                    if iBetrag > 0 and (not bSpread or iCityCheck > iBetrag):
                        iCityCheck = iBetrag
                        PlagueCity = sCity
                        bSpread = True

    # Handelsstaedte dieser Stadt
    if not bSpread:
        iTradeRoutes = pCity.getTradeRoutes()
        for i in range(iTradeRoutes):
            sCity = pCity.getTradeCity(i)
            if not sCity.isHasBuilding(iBuildingPlague) and sCity.getPopulation() > 3:
                PlagueCity = sCity
                bSpread = True
                break

    # Ausbreiten
    if bSpread:
        pCity = PlagueCity
        iPlayer = PlagueCity.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        iThisTeam = pPlayer.getTeam()
        # team = gc.getTeam(iThisTeam)

        #iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
        #iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
        #iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
        #iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

        # City Revolt
        #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4): pCity.setOccupationTimer(2)
        # else: pCity.setOccupationTimer(3)

        # message for all
        iRange = gc.getMAX_PLAYERS()
        for iSecondPlayer in range(iRange):
            pSecondPlayer = gc.getPlayer(iSecondPlayer)
            if pSecondPlayer.isHuman():
                iSecTeam = pSecondPlayer.getTeam()
                if gc.getTeam(iSecTeam).isHasMet(iThisTeam):
                    if pSecondPlayer.isHuman():
                        CyInterface().addMessage(iSecondPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD", (pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD", (pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
        # end message

        # Plague building gets added into city => culture -50
        pCity.setNumRealBuilding(iBuildingPlague, 1)
  # --- plague spread


# Provinz Rebellion / Statthalter
def doProvinceRebellion(pCity):
    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Provinzrebellion (Zeile 4578)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iPlayer = pCity.getOwner()
    # pPlayer = gc.getPlayer(iPlayer)
    # iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')

    iNewOwner = gc.getBARBARIAN_PLAYER()
    iOriginal = pCity.getOriginalOwner()

    iMaxPlayers = gc.getMAX_PLAYERS()
    # iNewOwner herausfinden
    # 1. Moeglichkeit: gab es einen Vorbesitzer
    if iOriginal != iPlayer and (gc.getPlayer(iOriginal).isAlive() or gc.getGame().countCivPlayersAlive() < iMaxPlayers):
        iNewOwner = iOriginal
    # 2. Moeglichkeit: Spieler mit hoechster Kultur heraussuchen
    else:
        iPlayerHC = pCity.findHighestCulture()
        if iPlayerHC != iPlayer and iPlayerHC != -1 and gc.getPlayer(iPlayerHC).isAlive():
            iNewOwner = iPlayerHC
        # 3. Moeglichkeit: weitere Spieler mit Fremdkultur
        else:
            PlayerArray = []
            for i in range(iMaxPlayers):
                if gc.getPlayer(i).isAlive():
                    if i != iPlayer and pCity.getCulture(i) > 0:
                        PlayerArray.append(i)
            if PlayerArray:
                iRand = CvUtil.myRandom(len(PlayerArray), "provReb")
                iNewOwner = PlayerArray[iRand]
    # ----------------

    # Radius 5x5 Plots und dessen Staedte checken

    if not pCity.isCapital():
        iRange = 5
        iX = pCity.getX()
        iY = pCity.getY()
        for i in range(-iRange, iRange+1):
            for j in range(-iRange, iRange+1):
                loopPlot = plotXY(iX, iY, i, j)
                if loopPlot is not None and not loopPlot.isNone():
                    if loopPlot.isCity():
                        loopCity = loopPlot.getPlotCity()
                        if pCity.getID() != loopCity.getID() and not loopCity.isGovernmentCenter() and loopCity.getOwner() == iPlayer:
                            iLoopX = iX+i
                            iLoopY = iY+j
                            iChance = 100
                            for i2 in range(-iRange, iRange+1):
                                for j2 in range(-iRange, iRange+1):
                                    loopPlot2 = plotXY(iLoopX, iLoopY, i2, j2)
                                    if loopPlot2 is not None and not loopPlot2.isNone():
                                        if loopPlot2.isCity():
                                            loopCity2 = loopPlot2.getPlotCity()
                                            if pCity.getID() != loopCity2.getID():
                                                if loopCity2.isCapital():
                                                    iChance = 0
                                                    break
                                                elif loopCity2.isGovernmentCenter():
                                                    iChance = 50
                                if iChance == 0:
                                    break
                            if CvUtil.myRandom(100, "provReb2") < iChance:
                                doRenegadeCity(loopCity, iNewOwner, -1)
        doRenegadeCity(pCity, iNewOwner, -1)

def doRenegadeOnCombatResult(pLoser, pCity, iWinnerPlayer):
    # Trait Protective: Staedte laufen nicht ueber / cities do not renegade
    if pCity.hasTrait(gc.getInfoTypeForString("TRAIT_PROTECTIVE")):
        return False

    if not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE) and pCity.isCapital():
        return False

    # ab PAE V: soll nur mehr Staedte betreffen
    iBuilding = gc.getInfoTypeForString("BUILDING_STADT")
    if pCity.isHasBuilding(iBuilding):
        iLoserPlayer = pLoser.getOwner()
        pLoserPlayer = gc.getPlayer(iLoserPlayer)
        pWinnerPlayer = gc.getPlayer(iWinnerPlayer)
        pLoserPlot = pLoser.plot()
        # ab PAE V: ab Tech Enslavement / Sklaverei (removed)
        #iTech = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
        iTeam = gc.getPlayer(pCity.getOwner()).getTeam()
        pTeam = gc.getTeam(iTeam)
        # if pTeam.isHasTech(iTech):

        # Anz Einheiten im Umkreis von 1 Feld, mit denen man im Krieg ist (military units)
        iUnitAnzahl = 0
        iX = pLoserPlot.getX()
        iY = pLoserPlot.getY()
        for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
            loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
            if loopPlot is not None and not loopPlot.isNone():
                iRange = loopPlot.getNumUnits()
                for iUnit in range(iRange):
                    pLoopUnit = loopPlot.getUnit(iUnit)
                    if pLoopUnit.isMilitaryHappiness():
                        if pTeam.isAtWar(gc.getPlayer(pLoopUnit.getOwner()).getTeam()):
                            iUnitAnzahl += 1

        # Anz Einheiten in der Stadt (military units)
        iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
        iUnitCity = 0
        iChanceUnits = 0
        iRange = pLoserPlot.getNumUnits()
        for iUnit in range(iRange):
            pLoopUnit = pLoserPlot.getUnit(iUnit)
            if pLoopUnit.canFight():
                iUnitCity += 1
                # loyal units ?
                if pLoopUnit.isHasPromotion(iPromoLoyal):
                    iChanceUnits += 3
                else:
                    iChanceUnits += 1

        bCityRenegade = False
        if iUnitCity > 1 and iUnitCity * 4 < iUnitAnzahl and pCity.getPopulation() > 1:
            # Per defense point +1%
            iChanceDefense = pCity.getNaturalDefense() + pCity.getTotalDefense(0) - pCity.getDefenseDamage()
            # Per happy smile +5%
            iChanceHappiness = (pCity.happyLevel() - pCity.unhappyLevel(0)) * 2
            # Wonders: 1st +20%, 2nd +16%, 3rd +12%, 8, 4, 0
            iNumNWs = pCity.getNumNationalWonders()
            if iNumNWs < 6:
                iChanceNWs = iNumNWs * (11 - iNumNWs) * 2
            else:
                iChanceNWs = 60
            iNumWWs = pCity.getNumWorldWonders()
            if iNumWWs < 6:
                iChanceWWs = iNumWWs * (11 - iNumWWs) * 2
            else:
                iChanceWWs = 60
            # City population +5% each pop
            iChancePop = pCity.getPopulation() * 2
            # City connected with capital?
            if not pCity.isConnectedToCapital(pCity.getOwner()):
                iChancePop -= 10
            else:
                iChancePop += 10
            # bei negativ Nahrung - !
            iChancePop += pCity.foodDifference(1) * 5
            # Abstand zur Hauptstadt
            pCapitalCity = pLoserPlayer.getCapitalCity()
            if not pCapitalCity.isNone() and pCapitalCity is not None:
                iDistance = plotDistance(pCapitalCity.getX(), pCapitalCity.getY(), pCity.getX(), pCity.getY())
            else:
                iDistance = 50
            # Total
            iChanceTotal = iChanceUnits + iChanceDefense + iChanceHappiness + iChanceNWs + iChanceWWs + iChancePop - iUnitAnzahl - iDistance

            if iChanceTotal < 100:
                iChanceTotal = 100 - iChanceTotal
                iRand = CvUtil.myRandom(100, "City renegades")
                if iRand < iChanceTotal:
                    bCityRenegade = True
            else:
                # don't feel too safe
                iChanceTotal = 1
            iChanceTotal = int(iChanceTotal)

            # Meldung an den Spieler
            if not bCityRenegade and pWinnerPlayer.isHuman():
                CyInterface().addMessage(iWinnerPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_CHANCE", (pCity.getName(), iChanceTotal)), None, 2, None, ColorTypes(14), 0, 0, False, False)

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("hier 1",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if bCityRenegade:
            # Goldvergabe
            if pLoserPlayer.getNumCities() > 0:
                iGold = int(pLoserPlayer.getGold() / pLoserPlayer.getNumCities())
                pLoserPlayer.changeGold(-iGold)
                pWinnerPlayer.changeGold(iGold)
                if pWinnerPlayer.isHuman():
                    CyInterface().addMessage(iWinnerPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_1", ("", iGold)), None, 2, None, ColorTypes(8), 0, 0, False, False)
                if pLoserPlayer.isHuman():
                    CyInterface().addMessage(iLoserPlayer, True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GOLD_2", ("", iGold)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            # City renegades
            doRenegadeCity(pCity, iWinnerPlayer, pLoser)
            # refresh the variable
            pAcquiredCity = pLoserPlot.getPlotCity()
            # Message
            if pWinnerPlayer.isHuman():
                if iWinnerPlayer == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound('AS2D_REVOLTSTART')
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                iRand = 1 + CvUtil.myRandom(5, "TXT_KEY_MESSAGE_CITY_RENEGADE_1_")
                popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_1_"+str(iRand), (pAcquiredCity.getName(), )))

                popupInfo.setData1(iWinnerPlayer)
                popupInfo.setData2(pAcquiredCity.getID())
                popupInfo.setData3(iLoserPlayer)
                popupInfo.setOnClickedPythonCallback("popupRenegadeCity")  # EntryPoints/CvScreenInterface und CvGameUtils / 706
                # Button 0: Keep
                iRand = 1 + CvUtil.myRandom(5, "TXT_KEY_POPUP_RENEGADE_CITY_KEEP_")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_KEEP_"+str(iRand), ()), ",Art/Interface/Buttons/Actions/FoundCity.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,1,4")
                # Button 1: Enslave
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_ENSLAVE_1", ()), ",Art/Interface/Buttons/Civics/Slavery.dds,Art/Interface/Buttons/Civics_Civilizations_Religions_Atlas.dds,8,2")
                # Button 2: Raze
                iRand = 1 + CvUtil.myRandom(5, "TXT_KEY_POPUP_RENEGADE_CITY_RAZE_")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_RENEGADE_CITY_RAZE_"+str(iRand), ()), ",Art/Interface/Buttons/Builds/BuildCityRuins.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,8,9")
                popupInfo.addPopup(iWinnerPlayer)

            if pLoserPlayer.isHuman():
                if iLoserPlayer == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound('AS2D_REVOLTSTART')
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                iRand = 1 + CvUtil.myRandom(5, "TXT_KEY_MESSAGE_CITY_RENEGADE_2_")
                popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_RENEGADE_2_"+str(iRand), (pAcquiredCity.getName(), )))
                popupInfo.addPopup(iLoserPlayer)

            return True
    return False


# ueberlaufende Stadt / City renegade
# When Unit gets attacked: LoserUnitID (must not get killed automatically) , no unit = -1
def doRenegadeCity(pCity, iNewOwner, LoserUnit):

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Renegade City (Zeile 4637)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iRebel = gc.getInfoTypeForString("UNIT_REBELL")
    iPartisan = gc.getInfoTypeForString("UNIT_FREEDOM_FIGHTER")
    lRebels = [iRebel, iPartisan]

    lTraitPromos = [gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")]
    iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")

    if iNewOwner == -1:
        iNewOwner = gc.getBARBARIAN_PLAYER()

    pNewOwner = gc.getPlayer(iNewOwner)

    iX = pCity.getX()
    iY = pCity.getY()
    pPlot = pCity.plot()
    iOldOwner = pCity.getOwner()

    # Einheiten auslesen bevor die Stadt ueberlaeuft
    UnitArray = []
    JumpArray = []

    LoserUnitID = LoserUnit.getID()
    iLoserOwner = LoserUnit.getOwner()
    for iUnit in range(pPlot.getNumUnits()):
        # Nicht die Einheit, die gerade gekillt wird killen, sonst Error
        pLoopUnit = pPlot.getUnit(iUnit)
        if (pLoopUnit.getOwner() != iLoserOwner or LoserUnitID != pLoopUnit.getID()) and not pLoopUnit.isDead():
            # Freiheitskaempfer, Rebellen oder Unsichtbare rauswerfen
            if pLoopUnit.getUnitType() in lRebels or pLoopUnit.getInvisibleType() > -1:
                JumpArray.append(pLoopUnit)
            elif pLoopUnit.getOwner() == iOldOwner:
                # Einige Einheiten bleiben loyal und fliehen
                if pLoopUnit.isHasPromotion(iPromoLoyal):
                    iChance = 4
                else:
                    iChance = 8
                iRand = CvUtil.myRandom(10, "renCity1")
                if iRand < iChance:
                    UnitArray.append(pLoopUnit)
                    if pLoopUnit.isCargo():
                        pLoopUnit.setTransportUnit(None)
                # else: Einheit kann sich noch aus dem Staub machen
                else:
                    JumpArray.append(pLoopUnit)
            else:
                JumpArray.append(pLoopUnit)

    for pUnit in JumpArray:
        pUnit.jumpToNearestValidPlot()

    # Einheiten generieren
    for pLoopUnit in UnitArray:
        if pLoopUnit is None or pLoopUnit.isNone():
            # TEST
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 1 - Unit none",iOldOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            continue

        iUnitType = pLoopUnit.getUnitType()
        iUnitAIType = pLoopUnit.getUnitAIType()
        iUnitCombatType = pLoopUnit.getUnitCombatType()

        # UnitAIType -1 (NO_UNITAI) -> UNITAI_UNKNOWN = 0 , ATTACK = 4, City Defense = 10
        if iUnitAIType in [-1, 0, 4]:
            if iUnitType == gc.getInfoTypeForString('UNIT_FREED_SLAVE'):
                iUnitAIType = UnitAITypes(gc.getInfoTypeForString("UNITAI_ENGINEER"))
            elif iUnitType == gc.getInfoTypeForString('UNIT_TRADE_MERCHANT'):
                iUnitAIType = 19
            elif iUnitType == gc.getInfoTypeForString('UNIT_TRADE_MERCHANTMAN'):
                iUnitAIType = 19
            else:
                iUnitAIType = 0

        # Slaves will be freed, nur wenn dessen Besitzer neu ist
        if iUnitType == gc.getInfoTypeForString('UNIT_SLAVE'):
            iUnitType = gc.getInfoTypeForString('UNIT_FREED_SLAVE')
            NewUnit = pNewOwner.initUnit(iUnitType, iX, iY, UnitAITypes(gc.getInfoTypeForString("UNITAI_ENGINEER")), DirectionTypes.DIRECTION_SOUTH)
            PAE_Unit.copyName(NewUnit, iUnitType, pLoopUnit.getName())
        # Emigrant und dessen Kultur
        elif iUnitType == gc.getInfoTypeForString('UNIT_EMIGRANT'):
            NewUnit = pNewOwner.initUnit(iUnitType, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            CvUtil.addScriptData(NewUnit, "p", iOldOwner)
            PAE_Unit.copyName(NewUnit, iUnitType, pLoopUnit.getName())
        elif iUnitType != -1:
            NewUnit = pNewOwner.initUnit(iUnitType, iX, iY, UnitAITypes(iUnitAIType), DirectionTypes.DIRECTION_SOUTH)
            PAE_Unit.copyName(NewUnit, iUnitType, pLoopUnit.getName())
            if iUnitCombatType != -1:
                PAE_Unit.initUnitFromUnit(NewUnit, pLoopUnit)
                NewUnit.setDamage(pLoopUnit.getDamage(), -1)
                # PAE V: Trait-Promotions
                # 1. Agg Promo weg
                # 2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten
                for iLoopPromo in lTraitPromos:
                    NewUnit.setHasPromotion(iLoopPromo, False)
        # pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
        pLoopUnit.kill(True, -1)  # RAMK_CTD

    if iNewOwner == gc.getBARBARIAN_PLAYER():
        pNewOwner.initUnit(iPartisan, iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
        pNewOwner.initUnit(iPartisan, iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
        pNewOwner.initUnit(iPartisan, iX, iY, UnitAITypes(4), DirectionTypes.DIRECTION_SOUTH)

    # Stadt laeuft automatisch ueber (CyCity pCity, BOOL bConquest, BOOL bTrade)
    pNewOwner.acquireCity(pCity, 0, 1)
    # Pointer anpassen
    if pPlot.isCity():
        pCity = pPlot.getPlotCity()
        if pCity is not None and not pCity.isNone():
            # Kultur auslesen
            iCulture = pCity.getCulture(iOldOwner)
            # Kultur regenerieren - funkt net
            if iCulture > 0:
                pCity.changeCulture(iNewOwner, iCulture, True)

            # Stadtgroesse kontrollieren
            iPop = pCity.getPopulation()
            if iPop < 1:
                pCity.setPopulation(1)

            # Kolonie/Provinz checken
            doCheckCityState(pCity)


def AI_defendAndHire(pCity, iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    pPlot = pCity.plot()
    # Auf welchen Plots befinden sich gegnerische Einheiten
    if pPlot is not None and not pPlot.isNone():
        PlotArray = []
        iEnemyUnits = 0
        iRange = 1
        iX = pCity.getX()
        iY = pCity.getY()
        for x in range(-iRange, iRange+1):
            for y in range(-iRange, iRange+1):
                loopPlot = plotXY(iX, iY, x, y)
                if loopPlot is not None and not loopPlot.isNone():
                    iNumUnits = loopPlot.getNumUnits()
                    if iNumUnits >= 4:
                        for i in range(iNumUnits):
                            iOwner = loopPlot.getUnit(i).getOwner()
                            if pTeam.isAtWar(gc.getPlayer(iOwner).getTeam()):
                                if not loopPlot.getUnit(i).isInvisible(pPlayer.getTeam(), 0):
                                    PlotArray.append(loopPlot)
                                    iEnemyUnits += loopPlot.getNumUnits()
                                    break
        # Stadteinheiten durchgehen
        if PlotArray:
            # Schleife fuer Stadteinheiten
            # Bombardement
            iNumUnits = pPlot.getNumUnits()
            for i in range(iNumUnits):
                pUnit = pPlot.getUnit(i)
                if pUnit.isRanged():
                    if pUnit.getOwner() == iPlayer:
                        if not pUnit.isMadeAttack() and pUnit.getImmobileTimer() <= 0:
                            # getbestdefender -> getDamage
                            BestDefender = []
                            for plot in PlotArray:
                                pBestDefender = plot.getBestDefender(-1, -1, pUnit, 1, 0, 0)
                                BestDefender.append((pBestDefender.getDamage(), plot))
                            # bestdefenderplot angreifen ->  pCityUnit.rangeStrike(x,y)
                            BestDefender.sort()
                            # Ab ca 50% Schaden aufhoeren
                            if BestDefender[0][0] < 55:
                                plot = BestDefender[0][1]
                                pUnit.rangeStrike(plot.getX(), plot.getY())
                            else:
                                break

            # AI - Extern Unit support
            iCityUnits = pPlot.getNumUnits()
            iMaintainUnits = pCity.getYieldRate(0) - iCityUnits
            # 1) Reservisten
            if iMaintainUnits > 0 and iCityUnits * 2 <= iEnemyUnits:
                iReservists = pCity.getFreeSpecialistCount(19)  # SPECIALIST_RESERVIST
                if iReservists > 0:
                    # Einheiten definieren
                    lResUnits = []
                    # Schildtraeger fuer AI immer verfuegbar
                    lResUnits.append(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"))
                    # Auxiliars
                    iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
                    if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()):
                        lResUnits.append(iUnit)
                    iUnit = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
                    if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE")):
                        lResUnits.append(iUnit)
                    # Archer
                    iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
                    if pCity.canTrain(iUnit, 0, 0):
                        lResUnits.append(iUnit)
                    else:
                        lResUnits.append(gc.getInfoTypeForString("UNIT_ARCHER"))

                    while iReservists > 0 and iMaintainUnits > 0:
                        # choose unit
                        iRand = CvUtil.myRandom(len(lResUnits), "AIdefend")
                        iUnit = lResUnits[iRand]

                        NewUnit = pPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                        NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
                        NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
                        NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
                        NewUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

                        pCity.changeFreeSpecialistCount(19, -1)
                        iReservists -= 1
                        iMaintainUnits -= 1
                        iCityUnits += 1

            # 2) Hire Mercenaries
            # Muessen Mercenaries angeheuert werden? AI Hire
            # 70% Archer
            # 30% Other
            # BETTER AI: half price
            PAE_Mercenaries.AI_doHireMercenaries(iPlayer, pCity, iMaintainUnits, iCityUnits, iEnemyUnits)


def doUnitSupply(pCity, iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    pCityPlot = pCity.plot()
    popCity = pCity.getPopulation()

    iFactor = 1
    iCityUnits = pCityPlot.getNumDefenders(iPlayer)
    iMaintainUnits = iCityUnits - pCity.getYieldRate(0)
    if iMaintainUnits <= 0:
        return

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("YieldRate " + pCity.getName(),pCity.getYieldRate(0))), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iCityUnits",iCityUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iMaintainUnits",iMaintainUnits)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # ab PAE Patch 3: nur HI
    # Handicap: 0 (Settler) - 8 (Deity) ; 5 = King
    if gc.getGame().getHandicapType() < 5 or pPlayer.isHuman():
        # choose units
        # calculate food supply from SUPPLY_WAGON
        iExtraSupply = 0
        lUnitsAll = []
        iRange = pCityPlot.getNumUnits()
        for i in range(iRange):
            pLoopUnit = pCityPlot.getUnit(i)
            if pLoopUnit.getUnitCombatType() != -1:
                if pLoopUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                    iExtraSupply = PAE_Unit.getSupply(pLoopUnit)
                    if iExtraSupply <= iMaintainUnits:
                        iMaintainUnits -= iExtraSupply
                        iExtraSupply = 0
                    else:
                        iExtraSupply -= iMaintainUnits
                        iMaintainUnits = 0
                    # set new supply tickets
                    PAE_Unit.setSupply(pLoopUnit, iExtraSupply)
                else:
                    lUnitsAll.append(pLoopUnit)

            if iMaintainUnits == 0:
                break
        numUnits = len(lUnitsAll)
        if iMaintainUnits > 0 and numUnits > 0:
            # harm units
            lUnitIndex = CvUtil.shuffle(numUnits, gc.getGame().getSorenRand())[:iMaintainUnits]

            # while len(lUnitIndex)<iMaintainUnits and iI < 3*numUnits:
                # iI += 1
                # iRand = CvUtil.myRandom(numUnits, "nextUnitSupply")
                # if not iRand in lUnitIndex:
                    # lUnitIndex.append(iRand)

            # Betrifft Stadt
            # 20%: -1 Pop
            # 10%: FEATURE_SEUCHE
            iRand = CvUtil.myRandom(10, "seuche")
            # - 1 Pop
            if iRand < 2 and popCity > 1:
                pCity.changePopulation(-1)
                # bCheckCityState = True
                if pPlayer.isHuman():
                    CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_2", (pCity.getName(), (pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # Seuche
            elif iRand == 2:
                pCityPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_SEUCHE"), 1)
                if pPlayer.isHuman():
                    CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_3", (pCity.getName(), (pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # less food
            elif pCity.getFood() > 10:
                # Warnung und -20% Food Storage
                iFoodStoreChange = pCity.getFood() / 100 * 20
                pCity.changeFood(-iFoodStoreChange)
                if pPlayer.isHuman():
                    CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_1", (pCity.getName(), (pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            # ------

            # Betrifft Einheiten
            iJumpedOut = 0
            for iI in lUnitIndex:
                pUnit = lUnitsAll[iI]
                # Unit nicht mehr killen (Weihnachtsbonus :D ab 7.12.2012)
                iDamage = pUnit.getDamage()
                if iDamage < 70:
                    pUnit.changeDamage(30, False)
                    if gc.getPlayer(pUnit.getOwner()).isHuman():
                        CyInterface().addMessage(pUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_CITY", (pCity.getName(), pUnit.getName(), 30)), None, 2, None, ColorTypes(12), pUnit.getX(), pUnit.getY(), True, True)
                else:
                    iJumpedOut += 1
                    if pUnit.getDamage() < 85:
                        pUnit.setDamage(85, pUnit.getOwner())
                    pUnit.jumpToNearestValidPlot()
                    if gc.getPlayer(pUnit.getOwner()).isHuman():
                        CyInterface().addMessage(pUnit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4", (pCity.getName(), pUnit.getName())), None, 2, pUnit.getButton(), ColorTypes(12), pUnit.getX(), pUnit.getY(), True, True)

            # Wenn die Stadt durch Buildings stark heilt
            if iJumpedOut == 0:
                # Chance rauszuwerfen 33%
                if CvUtil.myRandom(3, "toomany1") == 1:
                    Einheiten = max(1, CvUtil.myRandom(iMaintainUnits, "toomany2"))
                    lUnitIndex2 = CvUtil.shuffle(iMaintainUnits, gc.getGame().getSorenRand())[:Einheiten]
                    for iI in lUnitIndex2:
                        pUnit = lUnitsAll[lUnitIndex[iI]]
                        pUnit.jumpToNearestValidPlot()
                        if pPlayer.isHuman():
                            CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4", (pCity.getName(), pUnit.getName())), "AS2D_STRIKE", 2, pUnit.getButton(), ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)


def doJewRevolt(pCity):
    bRevolt = False
    iReligionType = gc.getInfoTypeForString("RELIGION_JUDAISM")
    iRangeMaxPlayers = gc.getMAX_PLAYERS()
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if pPlayer.getStateReligion() != iReligionType:
        if pCity.happyLevel() < pCity.unhappyLevel(0):
            iChance = 3
        else:
            iChance = 1
        iRand = CvUtil.myRandom(50, "doJewRevolt")
        if iRand < iChance:

            #CivIsrael = CvUtil.findInfoTypeNum(gc.getCivilizationInfo, gc.getNumCivilizationInfos(), 'CIVILIZATION_ISRAEL')
            CivIsrael = gc.getInfoTypeForString("CIVILIZATION_ISRAEL")
            bIsraelAlive = False

            for i in range(iRangeMaxPlayers):
                loopPlayer = gc.getPlayer(i)
                # Israeliten sollen nur dann auftauchen, wenn es nicht bereits Israeliten gibt
                if loopPlayer.getCivilizationType() == CivIsrael and loopPlayer.isAlive():
                    bIsraelAlive = True
                    break

            # Israel versuchen zu erstellen
            iCivID = -1
            if not bIsraelAlive:
                if gc.getGame().countCivPlayersAlive() < iRangeMaxPlayers:
                    # nach einer bestehenden ISRAEL ID suchen
                    for i in range(iRangeMaxPlayers):
                        loopPlayer = gc.getPlayer(i)
                        if loopPlayer.getCivilizationType() == CivIsrael and loopPlayer.isEverAlive():
                            iCivID = i
                            break
                    # freie PlayerID herausfinden
                    if iCivID == -1:
                        for i in range(iRangeMaxPlayers):
                            loopPlayer = gc.getPlayer(i)
                            if not loopPlayer.isEverAlive():
                                iCivID = i
                                break
                    # wenn keine nagelneue ID frei ist, dann eine bestehende nehmen
                    if iCivID == -1:
                        for i in range(iRangeMaxPlayers):
                            loopPlayer = gc.getPlayer(i)
                            if not loopPlayer.isAlive():
                                iCivID = i
                                break

            if iPlayer == gc.getGame().getActivePlayer():
                CyAudioGame().Play2DSound('AS2D_REVOLTSTART')

            # Einen guenstigen Plot auswaehlen
            rebelPlotArray = []
            rebelPlotArrayB = []
            for i in range(3):
                for j in range(3):
                    loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                    if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
                        if loopPlot.getOwner() == iPlayer:
                            if loopPlot.isHills():
                                rebelPlotArray.append(loopPlot)
                            elif not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                                rebelPlotArrayB.append(loopPlot)
            if not rebelPlotArray:
                rebelPlotArray = rebelPlotArrayB

            # es kann rebelliert werden
            if rebelPlotArray:
                if iCivID > -1:
                    # Israel erstellen
                    if CvUtil.myRandom(2, "doJewRevolt2") == 0:
                        CivLeader = gc.getInfoTypeForString("LEADER_SALOMO")
                    else:
                        CivLeader = gc.getInfoTypeForString("LEADER_DAVID")
                    gc.getGame().addPlayer(iCivID, CivLeader, CivIsrael)
                    newPlayer = gc.getPlayer(iCivID)
                    newTeam = gc.getTeam(newPlayer.getTeam())

                    # Techs geben
                    xTeam = gc.getTeam(pPlayer.getTeam())
                    iTechNum = gc.getNumTechInfos()
                    for iTech in range(iTechNum):
                        if gc.getTechInfo(iTech) is not None:
                            if xTeam.isHasTech(iTech):
                                if gc.getTechInfo(iTech).isTrade():
                                    newTeam.setHasTech(iTech, 1, iCivID, 0, 0)

                    iTech = gc.getInfoTypeForString("TECH_MILIT_STRAT")
                    if not newTeam.isHasTech(iTech):
                        newTeam.setHasTech(iTech, 1, iCivID, 0, 0)

                else:
                    newPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())

                bRevolt = True

                # Rebells x 1.5 of city pop
                iNumRebels = pCity.getPopulation() + pCity.getPopulation() / 2

                # City Revolt
                # pCity.setOccupationTimer(iNumRebelx)
                # City Defender damage
                doCityRevolt(pCity, pCity.getPopulation() / 2)

                # Krieg erklaeren
                pPlayer.AI_changeAttitudeExtra(iCivID, -4)
                pTeam = gc.getTeam(pPlayer.getTeam())
                pTeam.declareWar(newPlayer.getTeam(), 0, 6)

                newPlayer.setCurrentEra(3)
                newPlayer.setGold(500)

                rebelTypeArray = [
                    gc.getInfoTypeForString("UNIT_FREEDOM_FIGHTER"),
                    gc.getInfoTypeForString("UNIT_ARCHER"),
                    gc.getInfoTypeForString("UNIT_SPEARMAN"),
                    gc.getInfoTypeForString("UNIT_MACCABEE")
                ]
                for i in range(iNumRebels):
                    iPlot = CvUtil.myRandom(len(rebelPlotArray), "doJewRevolt3")
                    iUnitType = CvUtil.myRandom(len(rebelTypeArray), "doJewRevolt4")
                    newPlayer.initUnit(rebelTypeArray[iUnitType], rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

                for iAllPlayer in range(iRangeMaxPlayers):
                    ThisPlayer = gc.getPlayer(iAllPlayer)
                    iThisPlayer = ThisPlayer.getID()
                    iThisTeam = ThisPlayer.getTeam()
                    ThisTeam = gc.getTeam(iThisTeam)
                    if ThisTeam.isHasMet(pPlayer.getTeam()) and ThisPlayer.isHuman():
                        if iThisPlayer == iPlayer:
                            iColor = 7
                        else:
                            iColor = 10
                        CyInterface().addMessage(iThisPlayer, True, 5, CyTranslator().getText("TXT_KEY_JEWISH_REVOLT", (pPlayer.getCivilizationAdjective(1), pCity.getName())), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, 'Art/Interface/Buttons/Units/button_freedom_fighter.dds', ColorTypes(iColor), pCity.getX(), pCity.getY(), True, True)
                        if ThisPlayer.getStateReligion() == iReligionType:
                            ThisPlayer.AI_changeAttitudeExtra(iCivID, 2)

                    # ***TEST***
                    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Juedische Freiheitskaempfer (Zeile 4284)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return bRevolt


def provinceTribute(pCity):
    iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    bDoRebellion = False
    # PAE III
    #iCityIntervall = gc.getGame().getGameTurn() - pCity.getGameTurnFounded()
    # if iCityIntervall > 0 and iCityIntervall % 30 == 0 and iPlayer != -1:

    # PAE IV: 33 (3%), PAE V: 50 (2%)
    if not gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString('TECH_POLYARCHY')) and CvUtil.myRandom(50, "provinceTribute") < 1:
        iGold = pPlayer.getGold()
        iTribut = pCity.getPopulation() * 10
        iTribut += CvUtil.myRandom(iTribut / 2, "Tribut")
        iTribut2 = iTribut / 2
        iBuildingHappiness = pCity.getBuildingHappiness(iBuilding)
        # Human PopUp
        if pPlayer.isHuman():
            iRand = CvUtil.myRandom(11, "TXT_KEY_POPUP_PROVINZHAUPTSTADT_DEMAND_")
            szText = CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_DEMAND_"+str(iRand), (pCity.getName(), iTribut))
            szText += CyTranslator().getText("[NEWLINE][NEWLINE]", ()) + CyTranslator().getText("TXT_KEY_POPUP_STATTHALTER_HALTUNG", ())
            szText += u": %d " % (abs(iBuildingHappiness))
            if iBuildingHappiness < 0:
                szText += CyTranslator().getText("[ICON_UNHAPPY]", ())
            else:
                szText += CyTranslator().getText("[ICON_HAPPY]", ())

            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(szText)
            popupInfo.setData1(iPlayer)
            popupInfo.setData2(pCity.getID())
            popupInfo.setData3(iTribut)
            popupInfo.setOnClickedPythonCallback("popupProvinzPayment")

            if iGold >= iTribut:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_1", (iTribut,)), "")
            if iGold >= iTribut2:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_2", (iTribut2,)), "")
            if iGold > 0 and iGold < iTribut2:
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_2_1", (iGold,)), "")
            iRand = 1 + CvUtil.myRandom(10, "TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_3_")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PROVINZHAUPTSTADT_ANSWER_3_"+str(iRand), ()), "")

            popupInfo.addPopup(iPlayer)
        else:
            # AI
            # Wenn iGold > iTribut * 3: 1 - 20%, 2 - 80%, 3 - 0%
            # Wenn iGold > iTribut * 2: 1 - 10%, 2 - 80%, 3 - 10%
            # Wenn iGold >= iTribut:    1 -  0%, 2 - 80%, 3 - 20%
            # Wenn iGold >= iTribut2:   1 -  0%, 2 - 70%, 3 - 30%
            # Wenn iGold > 0:           1 -  0%, 2 - 60%, 3 - 40%
            iAddHappiness = -1
            iRand = CvUtil.myRandom(10, "provinceTribute2")
            iRandRebellion = CvUtil.myRandom(100, "provinceTribute3")
            bPaid = False

            if iGold > iTribut * 3:
                if iRand < 2:
                    pPlayer.changeGold(-iTribut)
                    iAddHappiness = 2
                else:
                    pPlayer.changeGold(-iTribut2)
                    iAddHappiness = 1
                bPaid = True

            elif iGold > iTribut * 2:
                if iRand == 0:
                    pPlayer.changeGold(-iTribut)
                    iAddHappiness = 2
                elif iRand < 9:
                    pPlayer.changeGold(-iTribut2)
                    iAddHappiness = 1
                bPaid = True

            elif iGold >= iTribut:
                if iRand < 8:
                    pPlayer.changeGold(-iTribut2)
                    iAddHappiness = 1
                    bPaid = True

            elif iGold >= iTribut2:
                if iRand < 7:
                    pPlayer.changeGold(-iTribut2)
                    iAddHappiness = 1
                    bPaid = True

            elif iGold >= 0:
                if iRand < 6:
                    pPlayer.setGold(0)
                    iAddHappiness = 0

            # Happiness setzen (Man muss immer den aktuellen Wert + die Aenderung setzen)
            pCity.setBuildingHappyChange(gc.getBuildingInfo(iBuilding).getBuildingClassType(), iBuildingHappiness + iAddHappiness)

            # Chance einer Rebellion: Unhappy Faces * Capital Distance
            iCityHappiness = pCity.happyLevel() - pCity.unhappyLevel(0)
            if iCityHappiness < 0:
                # Abstand zur Hauptstadt
                pCapital = pPlayer.getCapitalCity()
                if pCapital is not None and not pCapital.isNone():
                    iDistance = plotDistance(pCapital.getX(), pCapital.getY(), pCity.getX(), pCity.getY())
                else:
                    iDistance = 20
                iChance = iCityHappiness * (-1) * iDistance
                if iChance > iRandRebellion:
                    bDoRebellion = True

            if bDoRebellion:
                doProvinceRebellion(pCity)
            elif bPaid:
                eOrigCiv = gc.getCivilizationInfo(gc.getPlayer(pCity.getOriginalOwner()).getCivilizationType())
                # 1 Unit as gift:
                lGift = []
                lGift.append(eOrigCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR")))
                iUnit2 = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
                if pCity.canTrain(iUnit2, 0, 0):
                    lGift.append(iUnit2)
                # Food
                lGift.append(gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"))
                # Slave
                if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")):
                    lGift.append(gc.getInfoTypeForString("UNIT_SLAVE"))
                # Mounted
                if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_STABLE")):
                    lGift.append(gc.getInfoTypeForString("UNIT_HORSE"))
                    lMounted = [
                        gc.getInfoTypeForString("UNIT_CHARIOT"),
                        gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
                        gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN")
                    ]
                    for iUnit in lMounted:
                        if pCity.canTrain(iUnit, 0, 0):
                            lGift.append(eOrigCiv.getCivilizationUnits(iUnit))
                # Elefant
                if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                    lGift.append(gc.getInfoTypeForString("UNIT_ELEFANT"))
                    if pCity.canTrain(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"), 0, 0):
                        lGift.append(gc.getInfoTypeForString("UNIT_WAR_ELEPHANT"))

                iRand = CvUtil.myRandom(len(lGift), "provinceTribute4")
                CvUtil.spawnUnit(lGift[iRand], pCity.plot(), pPlayer)
    return bDoRebellion

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Provinz-HS Tribut-PopUp (Zeile 4367)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


def removeNoBonusNoBuilding(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    # Buildings with prereq bonus gets checked : remove chance 10%
    building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_BRONZE")
    if pCity.isHasBuilding(building):
        if CvUtil.myRandom(10, "BUILDING_SCHMIEDE_BRONZE") == 1:
            bonus0 = gc.getInfoTypeForString("BONUS_COPPER")
            # bonus1 = gc.getInfoTypeForString("BONUS_COAL")
            # bonus2 = gc.getInfoTypeForString("BONUS_ZINN")
            bonus = bonusMissing(pCity, building)
            if bonus is not None:
                pCity.setNumRealBuilding(building, 0)
                # Welche Resi
                if bonus == bonus0:
                    szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1"
                else:
                    szText = "TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_2"
                # Meldung
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText(szText, (pCity.getName(), gc.getBonusInfo(bonus).getDescription(), gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                    popupInfo.setText(CyTranslator().getText(szText, (pCity.getName(), gc.getBonusInfo(bonus).getDescription(), gc.getBuildingInfo(building).getDescription())))
                    popupInfo.addPopup(iPlayer)

    building = gc.getInfoTypeForString("BUILDING_BRAUSTAETTE")
    if pCity.isHasBuilding(building):
        if CvUtil.myRandom(10, "BUILDING_BRAUSTAETTE") == 1:
            # bonus1 = gc.getInfoTypeForString("BONUS_WHEAT")
            # bonus2 = gc.getInfoTypeForString("BONUS_GERSTE")
            # bonus3 = gc.getInfoTypeForString("BONUS_HAFER")
            # bonus4 = gc.getInfoTypeForString("BONUS_ROGGEN")
            # bonus5 = gc.getInfoTypeForString("BONUS_HIRSE")
            bonus = bonusMissing(pCity, building)
            if bonus is not None:
                pCity.setNumRealBuilding(building, 0)
                # Meldung
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3", (pCity.getName(), "", gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                    popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_3", (pCity.getName(), "", gc.getBuildingInfo(building).getDescription())))
                    popupInfo.addPopup(iPlayer)

    # building = gc.getInfoTypeForString("BUILDING_WINERY")
    # bonus = gc.getInfoTypeForString("BONUS_GRAPES")
    # building = gc.getInfoTypeForString("BUILDING_PAPYRUSPOST")
    # bonus = gc.getInfoTypeForString("BONUS_PAPYRUS")
    # building = gc.getInfoTypeForString("BUILDING_SCHMIEDE_MESSING")
    # bonus1 = gc.getInfoTypeForString("BONUS_COPPER")
    # bonus2 = gc.getInfoTypeForString("BONUS_ZINK")
    lBuildings = [
        gc.getInfoTypeForString("BUILDING_WINERY"),
        gc.getInfoTypeForString("BUILDING_PAPYRUSPOST"),
        gc.getInfoTypeForString("BUILDING_SCHMIEDE_MESSING")
    ]
    for building in lBuildings:
        if pCity.isHasBuilding(building):
            if CvUtil.myRandom(10, "removeNoBonusNoBuilding") == 1:
                bonus = bonusMissing(pCity, building)
                if bonus is not None:
                    pCity.setNumRealBuilding(building, 0)
                    # Meldung
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1", (pCity.getName(), gc.getBonusInfo(bonus).getDescription(), gc.getBuildingInfo(building).getDescription())), None, 2, gc.getBuildingInfo(building).getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                        popupInfo = CyPopupInfo()
                        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_CITY_NOBONUSNOBUILDING_1", (pCity.getName(), gc.getBonusInfo(bonus).getDescription(), gc.getBuildingInfo(building).getDescription())))
                        popupInfo.addPopup(iPlayer)


def bonusMissing(pCity, eBuilding):
    eBonus = gc.getBuildingInfo(eBuilding).getPrereqAndBonus()
    if eBonus != -1:
        if not pCity.hasBonus(gc.getBuildingInfo(eBuilding).getPrereqAndBonus()):
            return eBonus

    eRequiredBonus = None
    for iI in range(gc.getNUM_BUILDING_PREREQ_OR_BONUSES()):
        eBonus = gc.getBuildingInfo(eBuilding).getPrereqOrBonuses(iI)
        if eBonus != -1:
            eRequiredBonus = eBonus
            if pCity.hasBonus(gc.getBuildingInfo(eBuilding).getPrereqOrBonuses(iI)):
                eRequiredBonus = None
                break
    return eRequiredBonus

def onEmigrantBuilt(city, unit):
    iPlayer = city.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = city.plot()
    iPop = city.getPopulation()
    # Einheit die richtige Kultur geben
    # iPlayerCulture = city.findHighestCulture() Klappt nicht, da Kultur des Stadtplots benoetigt wird
    # Muss selbst bestimmt werden, da plot.findHighestCultureTeam() das Team, aber nicht die Civ zurueckgibt
    iRange = gc.getMAX_PLAYERS()
    iPlayerCulture = -1
    iValueCulture = -1
    for i in range(iRange):
        if pPlot.getCulture(i) > iValueCulture:
            iValueCulture = pPlot.getCulture(i)
            iPlayerCulture = i
    # Sollte auf dem Plot keine Kultur sein (geht eigentlich nicht...), gehoert der Auswanderer zur Kultur des Besitzers
    if iValueCulture < 1:
        iPlayerCulture = unit.getOwner()
    CvUtil.addScriptData(unit, "p", iPlayerCulture)
    # Pop*100 Kultur von dem Stadtplot abziehen (max. 1000) (es bleibt immer mind. 1 Kultur)
    iCultureMax = pPlot.getCulture(iPlayerCulture) - 1
    if iCultureMax > 1000:
        iCultureMax = 1000
    iCulture = iPop * 100
    if iCulture > iCultureMax:
        iCulture = iCultureMax
    pPlot.changeCulture(iPlayerCulture, -iCulture, 1)
    # Pop senken, Nahrungslager leeren
    city.setFood(0)
    if iPop > 3:
        if pPlayer.isHuman():
            city.changePopulation(-2)
        else:
            city.changePopulation(-1)
    else:
        city.setPopulation(1)
    doCheckCityState(city)
    # ***TEST***
    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Auswanderer gebaut. Pop",iPop)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(city.getName(),city.getOwner())), None, 2, None, ColorTypes(10), 0, 0, False, False)


def doEmigrantSpawn(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    popCity = pCity.getPopulation()
    popNeu = max(1, popCity - 2)
    text = ""
    bRevoltDanger = False
    iChance = 4
    iCityUnhappy = pCity.unhappyLevel(0) - pCity.happyLevel()
    iCityUnhealthy = pCity.badHealth(False) - pCity.goodHealth()
    if iCityUnhappy > 0 or iCityUnhealthy > 0:
        bRevoltDanger = True
        if iCityUnhealthy > 0:
            text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_2", (pCity.getName(), popNeu, popCity))
        else:
            text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS", (pCity.getName(), popNeu, popCity))
        if iCityUnhappy < 0:
            iCityUnhappy = 0
        if iCityUnhealthy <= 0:
            iCityUnhealthy = 0
        iChance = (iCityUnhappy + iCityUnhealthy) * 4  # * popCity
    elif pPlayer.getAnarchyTurns() > 0:
        bRevoltDanger = True
        text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_3", (pCity.getName(), popNeu, popCity))
    elif pPlayer.getStateReligion() != -1 and not pCity.isHasReligion(pPlayer.getStateReligion()):
        bRevoltDanger = True
        text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_4", (pCity.getName(), popNeu, popCity))
    elif pPlayer.getCommercePercent(0) > 50:
        iChance = int((pPlayer.getCommercePercent(0) - 50) / 5)
        # Pro Happy Citizen 5% Nachlass
        iChance = iChance - pCity.happyLevel() + pCity.unhappyLevel(0)
        bRevoltDanger = iChance > 0
        text = CyTranslator().getText("TXT_KEY_MESSAGE_CITY_EMIGRANTS_5", (pCity.getName(), popNeu, popCity))

    if bRevoltDanger:
        if CvUtil.myRandom(100, "doEmigrantSpawn") < iChance:
            iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
            NewUnit = pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

            # Einheit die richtige Kultur geben
            iPlayerCulture = pCity.findHighestCulture()
            if iPlayerCulture == -1:
                iPlayerCulture = iPlayer
            CvUtil.addScriptData(NewUnit, "p", iPlayerCulture)
            # Kultur von der Stadt abziehen
            iCulture = pCity.getCulture(iPlayerCulture)
            pCity.changeCulture(iPlayerCulture, -(iCulture/5), 1)

            pCity.setPopulation(popNeu)
            doCheckCityState(pCity)

            if pPlayer.isHuman() and text != "":
                CyInterface().addMessage(iPlayer, True, 10, text, "AS2D_REVOLTSTART", InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
            else:
                PAE_Sklaven.doAIReleaseSlaves(pCity)
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant verlaesst Stadt (Zeile 3624)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


def doLeprosy(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    bDecline = False
    if pCity.goodHealth() < pCity.badHealth(False):
        iChance = pCity.badHealth(False) - pCity.goodHealth()
        # PAE V: less chance for AI
        if not pPlayer.isHuman():
            iChance = iChance / 3

        if CvUtil.myRandom(100, "doLeprosy") < iChance:
            iOldPop = pCity.getPopulation()

            # Leprakolonie nimmt nur 1 POP
            iBuilding = gc.getInfoTypeForString('BUILDING_LEPRAKOLONIE')
            if pCity.isHasBuilding(iBuilding):
                iNewPop = max(1, iOldPop - 1)
                if pPlayer.isHuman():
                    CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_LEBRA_1", (pCity.getName(), )), "AS2D_PLAGUE", 2, None, ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
            else:
                iRandPop = CvUtil.myRandom(int(round(pCity.getPopulation() / 2)), "doLeprosy2") + 1
                iNewPop = max(1, iOldPop - iRandPop)
                # City Revolt
                # pCity.setOccupationTimer(1)
                if pPlayer.isHuman():
                    CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_LEBRA_2", (pCity.getName(), iNewPop, iOldPop)), "AS2D_PLAGUE", 2, None, ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

            pCity.setPopulation(iNewPop)
            bDecline = True

            if not pPlayer.isHuman():
                PAE_Sklaven.doAIReleaseSlaves(pCity)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Lepra (Zeile 3660)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    return bDecline


def doSpawnPest(pCity):
    iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if pCity.goodHealth() < pCity.badHealth(False):
        iChance = pCity.badHealth(False) - pCity.goodHealth()

        # PAE V: less chance for AI
        if not pPlayer.isHuman():
            iChance = iChance / 3

        if CvUtil.myRandom(100, "doSpawnPest") < iChance:
            iThisTeam = pPlayer.getTeam()
            # team = gc.getTeam(iThisTeam)

            #iMedicine1 = gc.getInfoTypeForString("TECH_MEDICINE1")
            #iMedicine2 = gc.getInfoTypeForString("TECH_MEDICINE2")
            #iMedicine3 = gc.getInfoTypeForString("TECH_MEDICINE3")
            #iMedicine4 = gc.getInfoTypeForString("TECH_HEILKUNDE")

            # City Revolt
            #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4): pCity.setOccupationTimer(2)
            # else: pCity.setOccupationTimer(3)
            # pCity.setOccupationTimer(1)

            # message for all
            iRange = gc.getMAX_PLAYERS()
            for iPlayer2 in range(iRange):
                pSecondPlayer = gc.getPlayer(iPlayer2)
                if pSecondPlayer.isHuman():
                    iSecTeam = pSecondPlayer.getTeam()
                    if gc.getTeam(iSecTeam).isHasMet(iThisTeam):
                        if pSecondPlayer.isHuman():
                            CyInterface().addMessage(iPlayer2, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLOBAL", (pCity.getName(), 0)), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLOBAL", (pCity.getName(), 0)), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
            # end message

            # Plague building gets added into city
            pCity.setNumRealBuilding(iBuildingPlague, 1)

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Pest (Zeile 3701)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


def doPlagueEffects(pCity):
    iBuildingPlague = gc.getInfoTypeForString('BUILDING_PLAGUE')
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    #iCulture = pCity.getBuildingCommerceByBuilding(2, iBuildingPlague)
    iCulture = pCity.getCulture(iPlayer)
    iX = pCity.getX()
    iY = pCity.getY()
    # Calculation var
    iHappiness = pCity.getBuildingHappiness(iBuildingPlague)

    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Culture",iCulture)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Happiness",iHappiness)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Plots rundherum mit SeuchenFeature belasten
    if iHappiness == -5:
        feat_seuche = gc.getInfoTypeForString('FEATURE_SEUCHE')
        for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
            loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
            if loopPlot is not None and not loopPlot.isNone():
                if not loopPlot.isWater() and not loopPlot.isPeak() and loopPlot.getFeatureType() == -1:
                    loopPlot.setFeatureType(feat_seuche, 0)

    # Downgrade Improvements
    if iHappiness == -4 or iHappiness == -2:
        for iI in range(gc.getNUM_CITY_PLOTS()):
            loopPlot = pCity.getCityIndexPlot(iI)
            if loopPlot is not None and not loopPlot.isNone():
                improv1 = gc.getInfoTypeForString('IMPROVEMENT_COTTAGE')
                improv2 = gc.getInfoTypeForString('IMPROVEMENT_HAMLET')
                improv3 = gc.getInfoTypeForString('IMPROVEMENT_VILLAGE')
                improv4 = gc.getInfoTypeForString('IMPROVEMENT_TOWN')
                iImprovement = loopPlot.getImprovementType()
                # 50% chance of downgrading
                iRand = CvUtil.myRandom(2, "doPlagueEffects")
                if iRand == 1:
                    if iImprovement == improv2:
                        loopPlot.setImprovementType(improv1)
                    elif iImprovement == improv3:
                        loopPlot.setImprovementType(improv2)
                    elif iImprovement == improv4:
                        loopPlot.setImprovementType(improv3)

    # decline City pop
    # iThisTeam = pPlayer.getTeam()
    # team = gc.getTeam(iThisTeam)

    #iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
    #iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
    #iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
    #iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

    # Change City Pop
    iOldPop = pCity.getPopulation()
    # there is no medicine against plague :)
    # if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4):
    # bis zu -2 pro turn
    iPopChange = 1 + CvUtil.myRandom(2, "doPlagueEffects2")

    # Slaves and Glads
    eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
    eSpecialistHouse = gc.getInfoTypeForString("SPECIALIST_SLAVE")
    eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
    eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")

    iCityGlads = pCity.getFreeSpecialistCount(eSpecialistGlad)
    iCitySlavesHaus = pCity.getFreeSpecialistCount(eSpecialistHouse)
    iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood)
    iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd)

    # Pop
    iNewPop = max(1, iOldPop - iPopChange)

    # Message new Pop
    if pPlayer.isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST", (pCity.getName(), iNewPop, iOldPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

    pCity.setPopulation(iNewPop)
    # end decline city pop

    # Sklaven sterben
    # Prio: Haus (min 1 bleibt), Food, Glads, Prod
    iSlaves = iCityGlads + iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
    while iSlaves > 0 and iPopChange > 0:
        if iCitySlavesHaus > 1:
            pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
            iCitySlavesHaus -= 1
            if pPlayer.isHuman():
                CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_HAUS", (pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCitySlavesFood > 0:
            pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
            iCitySlavesFood -= 1
            if pPlayer.isHuman():
                CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_FOOD", (pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCityGlads > 0:
            pCity.changeFreeSpecialistCount(eSpecialistGlad, -1)
            iCityGlads -= 1
            if pPlayer.isHuman():
                CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_GLAD", (pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        elif iCitySlavesProd > 0:
            pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
            iCitySlavesProd -= 1
            if pPlayer.isHuman():
                CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_PROD", (pCity.getName(),)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        iSlaves -= 1
        iPopChange -= 1

    # Hurt and kill units
    lMessageOwners = []
    for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
        loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
        if loopPlot is not None and not loopPlot.isNone():
            iRange = loopPlot.getNumUnits()
            for iUnit in range(iRange):
                iRand = CvUtil.myRandom(30, "doPlagueEffects3") + 15
                pLoopUnit = loopPlot.getUnit(iUnit)
                if pLoopUnit is not None:
                    if pLoopUnit.getDamage() + iRand < 100:
                        pLoopUnit.changeDamage(iRand, False)
                    sOwner = pLoopUnit.getOwner()
                    psOwner = gc.getPlayer(sOwner)
                    if pLoopUnit.getDamage() > 95:
                        if psOwner is not None and psOwner.isHuman():
                            CyInterface().addMessage(sOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_KILL_UNIT", (pLoopUnit.getName(), pCity.getName())), None, 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(12), loopPlot.getX(), loopPlot.getY(), True, True)
                        # pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                        pLoopUnit.kill(True, -1)  # RAMK_CTD
                    if psOwner is not None and psOwner.isHuman():
                        if sOwner not in lMessageOwners:
                            lMessageOwners.append(sOwner)
                            CyInterface().addMessage(sOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_2", (pCity.getName(), 0)), None, 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(12), iX, iY, True, True)

    # Change City Culture
    iCultureNew = max(0, iCulture - 50)
    pCity.setCulture(iPlayer, iCultureNew, 1)

    # Calculation
    if iHappiness >= -1:
        # Building erneut initialisieren. CIV BUG.
        pCity.setBuildingHappyChange(gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), 0)
        # Building entfernen
        pCity.setNumRealBuilding(iBuildingPlague, 0)
        # Message
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_DONE", (pCity.getName(), iNewPop, iOldPop)), "AS2D_WELOVEKING", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(8), pCity.getX(),  pCity.getY(), True, True)

    else:
        CvUtil.changeBuildingHappyChange(pCity, iBuildingPlague, +1)
        # # zum Gebaeude +1 Happiness addieren (-5,-4,..) - funkt leider nicht mit nur einer Zeile?!- Civ BUG?
        # if iHappiness == -5: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +1)
        # if iHappiness == -4: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +2)
        # if iHappiness == -3: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +3)
        # if iHappiness == -2: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +4)
        # if iHappiness == -1: pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), +5)
        # if iHappiness < -5:
        # pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuildingPlague).getBuildingClassType(), 0)
        # pCity.setNumRealBuilding(iBuildingPlague,0)
        # pCity.setNumRealBuilding(iBuildingPlague,1)

    # spread plague 10%
    if CvUtil.myRandom(10, "spread Plague") == 1:
        doSpreadPlague(pCity)


def doRevoltShrink(pCity):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    if CvUtil.myRandom(2, "doRevoltShrink") == 1:
        pCity.changePopulation(-1)
        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, False, 25, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLT_SHRINK", (pCity.getName(),)), "AS2D_REVOLTSTART", InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtpop sinkt wegen Revolte (Zeile 4126)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        return True
    return False


def doPartisans(pCity, iPreviousOwner):
    # Seek Plots
    rebelPlotArray = []
    PartisanPlot2 = []
    iX = pCity.getX()
    iY = pCity.getY()
    for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
        loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
        if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isUnit():
            if not loopPlot.isWater() and not loopPlot.isImpassable() and not loopPlot.isCity():
                if loopPlot.isHills():
                    rebelPlotArray.append(loopPlot)
                else:
                    PartisanPlot2.append(loopPlot)
    if not rebelPlotArray:
        rebelPlotArray = PartisanPlot2

    # Set Partisans
    if rebelPlotArray:
        pPreviousOwner = gc.getPlayer(iPreviousOwner)
        iThisTeam = pPreviousOwner.getTeam()
        team = gc.getTeam(iThisTeam)
        if team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"), 0, 0):
            iUnitType = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
        elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")) and pCity.canTrain(gc.getInfoTypeForString("UNIT_AXEMAN"), 0, 0):
            iUnitType = gc.getInfoTypeForString("UNIT_AXEMAN")
        elif team.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG")):
            iUnitType = gc.getInfoTypeForString("UNIT_AXEWARRIOR")
        else:
            iUnitType = gc.getInfoTypeForString("UNIT_WARRIOR")

        # Number of Partisans
        iAnzahl = CvUtil.myRandom(pCity.getPopulation()/2, "doPartisans") + 1
        for _ in range(iAnzahl):
            pPlot = rebelPlotArray[CvUtil.myRandom(len(rebelPlotArray), "doPartisansPlot")]
            pUnit = pPreviousOwner.initUnit(iUnitType, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            iDamage = CvUtil.myRandom(50, "doPartisansDamage")
            pUnit.setDamage(iDamage, iPreviousOwner)

        # PAE V: Reservisten
        iAnzahl = pCity.getFreeSpecialistCount(19)
        pCity.setFreeSpecialistCount(19, 0)
        for _ in range(iAnzahl):
            pPlot = rebelPlotArray[CvUtil.myRandom(len(rebelPlotArray), "doPartisansReservists")]
            pUnit = pPreviousOwner.initUnit(iUnitType, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
            iDamage = CvUtil.myRandom(25, "doPartisansReservistsDamage")
            pUnit.setDamage(iDamage, iPreviousOwner)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT1"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3"), True)
            pUnit.setHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4"), True)

        #iOwner = pCity.findHighestCulture()
#        if iPreviousOwner != -1 and iNewOwner != -1:
#          if not pPreviousOwner.isBarbarian() and pPreviousOwner.getNumCities() > 0:
#            if gc.getTeam(pPreviousOwner.getTeam()).isAtWar(gc.getPlayer(iNewOwner).getTeam()):
#              if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
#                iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_PARTISANS')
#                if iEvent != -1 and gc.getGame().isEventActive(iEvent) and pPreviousOwner.getEventTriggerWeight(iEvent) >= 0:
#                  triggerData = pPreviousOwner.initTriggeredData(iEvent, True, -1, pCity.getX(), pCity.getY(), iPreviousOwner, pCity.getID(), -1, -1, -1, -1)
# --- Ende Partisans -------------------------


def doCaptureSlaves(pCity, iNewOwner, iPreviousOwner):
    pPlayer = gc.getPlayer(iNewOwner)
    iTeam = pPlayer.getTeam()
    pTeam = gc.getTeam(iTeam)

    iTechEnslavement = gc.getInfoTypeForString("TECH_ENSLAVEMENT")
    if pTeam.isHasTech(iTechEnslavement):
        iSlaves = CvUtil.myRandom(pCity.getPopulation() - 1, "doCaptureSlaves") + 1

        # Trait Aggressive: Popverlust bleibt gleich / loss of pop remains the same
        iSetPop = max(1, pCity.getPopulation() - iSlaves)
        pCity.setPopulation(iSetPop)

        # Trait Aggressive: Slaves * 2
        if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
            iSlaves *= 2

        iUnit = gc.getInfoTypeForString("UNIT_SLAVE")
        pPlot = pCity.plot()
        for _ in range(iSlaves):
            CvUtil.spawnUnit(iUnit, pPlot, pPlayer)

        if pPlayer.isHuman():
            if iSlaves == 1:
                CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_1", (0, 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
            else:
                CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_2", (iSlaves, 0)), None, 2, None, ColorTypes(8), 0, 0, False, False)
        if gc.getPlayer(iPreviousOwner).isHuman():
            if iSlaves == 1:
                CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_3", (pCity.getName(), 0)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            else:
                CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_SLAVES_4", (pCity.getName(), iSlaves)), None, 2, None, ColorTypes(7), 0, 0, False, False)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadt erobert (Zeile 3182)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


def doSettledSlavesAndReservists(pCity):
    bRevolt = False
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pTeam = gc.getTeam(pPlayer.getTeam())
    pCityPlot = pCity.plot()
    iCityPop = pCity.getPopulation()

    eSpecialistGlad = gc.getInfoTypeForString("SPECIALIST_GLADIATOR")
    eSpecialistHouse = gc.getInfoTypeForString("SPECIALIST_SLAVE")
    eSpecialistFood = gc.getInfoTypeForString("SPECIALIST_SLAVE_FOOD")
    eSpecialistProd = gc.getInfoTypeForString("SPECIALIST_SLAVE_PROD")

    eSpecialistReserve = gc.getInfoTypeForString("SPECIALIST_RESERVIST")
    eSpecialistFreeCitizen = gc.getInfoTypeForString("SPECIALIST_CITIZEN2")

    iCityGlads = pCity.getFreeSpecialistCount(eSpecialistGlad)
    iCitySlavesHaus = pCity.getFreeSpecialistCount(eSpecialistHouse)
    iCitySlavesFood = pCity.getFreeSpecialistCount(eSpecialistFood)
    iCitySlavesProd = pCity.getFreeSpecialistCount(eSpecialistProd)
    iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd
    iCitySlaves2 = 0  # Unsettled Slaves in city

    iCityReservists = pCity.getFreeSpecialistCount(eSpecialistReserve)

    # Wenn es Sklaven gibt = verschiedene Sterbensarten
    if iCitySlaves > 0 or iCityReservists > 0:
        # Sklaventyp aussuchen, aber es soll max. immer nur 1 Typ pro Stadt draufgehn
        iTyp = -1

        # Haussklave 4%
        if iCitySlavesHaus > 0:
            if CvUtil.myRandom(100, "iCitySlavesHaus") < 4:
                iTyp = 2
        # Feldsklave 5%
        if iCitySlavesFood > 0 and iTyp == -1:
            if CvUtil.myRandom(100, "iCitySlavesFood") < 5:
                iTyp = 0
        # Bergwerkssklave 8%
        if iCitySlavesProd > 0 and iTyp == -1:
            if CvUtil.myRandom(100, "iCitySlavesProd") < 8:
                iTyp = 1
        # Reservist 3%
        if iCityReservists > 0 and iTyp == -1:
            if CvUtil.myRandom(100, "iCityReservists") < 3:
                iTyp = 3

        # Reservisten
        if iTyp == 3:
            pCity.changeFreeSpecialistCount(eSpecialistReserve, -1)
            if pPlayer.isHuman():
                iRand = 1 + CvUtil.myRandom(9, "Reservisten")
                CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DYING_RESERVIST_"+str(iRand), (pCity.getName(), "")), None, 2, ",Art/Interface/MainScreen/CityScreen/Great_Engineer.dds,Art/Interface/Buttons/Warlords_Atlas_2.dds,7,6", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        # Sklavensterben
        elif iTyp != -1:
            # PAE V: stehende Sklaven werden zugewiesen
            bErsatz = False
            iRangePlotUnits = pCityPlot.getNumUnits()
            for iUnit in range(iRangePlotUnits):
                pLoopUnit = pCityPlot.getUnit(iUnit)
                if pLoopUnit.getOwner() == iPlayer and pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                    # pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                    pLoopUnit.kill(True, -1)  # RAMK_CTD
                    bErsatz = True
                    break

            # Feldsklaven
            if iTyp == 0:
                if not bErsatz:
                    pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                    iCitySlavesFood -= 1
                if pPlayer.isHuman():
                    iRand = 1 + CvUtil.myRandom(16, "Feldsklaven")
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_FELD_"+str(iRand), (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

            # Bergwerkssklaven
            elif iTyp == 1:
                if not bErsatz:
                    pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                    iCitySlavesProd -= 1
                if pPlayer.isHuman():
                    iRand = 1 + CvUtil.myRandom(20, "Bergwerkssklaven")
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_MINE_"+str(iRand), (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

            # Haussklaven
            elif iTyp == 2:
                # A) Standard Sklavensterben
                # B) Tech Patronat: Hausklaven werden freie Buerger
                iRand = 0
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PATRONAT")):
                    iRand = 2

                # Dying
                if CvUtil.myRandom(iRand, "Haussklaven1") == 0:
                    if not bErsatz:
                        pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                        iCitySlavesHaus -= 1
                    if pPlayer.isHuman():
                        iRand = 1 + CvUtil.myRandom(14, "Haussklaven2")
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_HAUS_"+str(iRand), (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                # Patronat
                else:
                    bErsatz = False
                    pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                    iCitySlavesHaus -= 1
                    pCity.changeFreeSpecialistCount(eSpecialistFreeCitizen, +1)  # SPECIALIST_CITIZEN2
                    if pPlayer.isHuman():
                        iRand = 1 + CvUtil.myRandom(2, "Haussklaven3")
                        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_PATRONAT_"+str(iRand), (pCity.getName(), "")), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)

            if bErsatz:
                if pPlayer.isHuman():
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_SLAVES_ERSATZ", ("",)), None, 2, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
            else:
                # Gesamtsumme aendern
                iCitySlaves -= 1

    # Wenns mehr Sklaven als Einwohner gibt = Revolte
    if iCitySlaves + iCityGlads > iCityPop:
        # Calc factor
        iChance = (iCitySlaves + iCityGlads - iCityPop) * 10

        # rebel bonus when unhappy
        if pCity.happyLevel() < pCity.unhappyLevel(0):
            iChance += 25
        # Units that prevent a revolt
        iPromoHero = gc.getInfoTypeForString('PROMOTION_HERO')
        iRangePlotUnits = pCityPlot.getNumUnits()
        for iUnit in range(iRangePlotUnits):
            pLoopUnit = pCityPlot.getUnit(iUnit)
            if pLoopUnit.isHasPromotion(iPromoHero):
                iChance -= 25
            elif pLoopUnit.isMilitaryHappiness():
                iChance -= 2
            elif pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                iCitySlaves2 += 1
                iChance += 2
        # Buildings that prevent a revolt
        iBuilding = gc.getInfoTypeForString('BUILDING_COLOSSEUM')
        if pCity.isHasBuilding(iBuilding):
            iChance -= 5
        iBuilding = gc.getInfoTypeForString('BUILDING_BYZANTINE_HIPPODROME')
        if pCity.isHasBuilding(iBuilding):
            iChance -= 5
        # Civics that promotes/prevents a revolt
        if pPlayer.isCivic(14):
            iChance += 5
        if pPlayer.isCivic(15):
            iChance += 5
        if pPlayer.isCivic(16) or pPlayer.isCivic(17):
            iChance -= 5

        if iChance > 0:
            iRand = CvUtil.myRandom(100, "SKLAVENAUFSTAND")
            # Lets rebell
            if iRand < iChance:
                if iPlayer == gc.getGame().getActivePlayer():
                    CyAudioGame().Play2DSound('AS2D_REVOLTSTART')

                # Einen guenstigen Plot auswaehlen
                rebelPlotArray = []
                rebelPlotArrayB = []
                for i in range(3):
                    for j in range(3):
                        loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
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
                    bRevolt = True
                    # pruefen ob es einen Vorbesitzer fuer diese Stadt gibt
                    iPreviousOwner = pCity.findHighestCulture()
                    barbPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
                    if iPlayer != iPreviousOwner and iPreviousOwner != -1:
                        if gc.getTeam(pPlayer.getTeam()).isAtWar(gc.getPlayer(iPreviousOwner).getTeam()):
                            barbPlayer = gc.getPlayer(iPreviousOwner)

                    # Unsettled slaves
                    iNumRebels2 = 0
                    if iCitySlaves2 > 0:
                        iNumRebels2 = CvUtil.myRandom(iCitySlaves2 - 1, "Unsettled slaves2") + 1
                        iDone = 0
                        iRangePlotUnits = pCityPlot.getNumUnits()
                        for iUnit in range(iRangePlotUnits):
                            pLoopUnit = pCityPlot.getUnit(iUnit)
                            if iDone < iNumRebels2 and pLoopUnit.getUnitType() == gc.getInfoTypeForString("UNIT_SLAVE"):
                                # pLoopUnit.doCommand(CommandTypes.COMMAND_DELETE, -1, -1)
                                pLoopUnit.kill(True, -1)  # RAMK_CTD
                                iDone += 1

                    iNumRebels = 0
                    # SLAVE REVOLT (SKLAVENAUFSTAND)
                    if iCitySlaves > iCityGlads and iCitySlaves > 0:
                        iUnitType = gc.getInfoTypeForString("UNIT_REBELL")

                        # Settled slaves
                        iNumRebels = CvUtil.myRandom(iCitySlaves - 1, "Settled slaves") + 1
                        iNumRebTmp = iNumRebels
                        # Zuerst Feldsklaven
                        if iNumRebTmp >= iCitySlavesFood:
                            pCity.setFreeSpecialistCount(eSpecialistFood, 0)
                            iNumRebTmp -= iCitySlavesFood
                        else:
                            pCity.changeFreeSpecialistCount(eSpecialistFood, iNumRebTmp * (-1))
                            iNumRebTmp = 0
                        # Dann Bergwerkssklaven
                        if iNumRebTmp >= iCitySlavesProd and iNumRebTmp > 0:
                            pCity.setFreeSpecialistCount(eSpecialistProd, 0)
                            iNumRebTmp -= iCitySlavesProd
                        else:
                            pCity.changeFreeSpecialistCount(eSpecialistProd, iNumRebTmp * (-1))
                            iNumRebTmp = 0
                        # Der Rest Haussklaven
                        if iNumRebTmp >= iCitySlavesHaus and iNumRebTmp > 0:
                            pCity.setFreeSpecialistCount(eSpecialistHouse, 0)
                            # iNumRebTmp -= iCitySlavesHaus
                        else:
                            pCity.changeFreeSpecialistCount(eSpecialistHouse, iNumRebTmp * (-1))
                            # iNumRebTmp = 0

                    # GLADIATOR REVOLT (GLADIATORENAUFSTAND)
                    elif iCityGlads > 0:
                        iUnitType = gc.getInfoTypeForString("UNIT_GLADIATOR")
                        # Settled gladiators
                        iNumRebels = CvUtil.myRandom(iCityGlads - 1, "Settled gladiators")+1
                        pCity.changeFreeSpecialistCount(eSpecialistGlad, iNumRebels * (-1))

                    iNumRebels += iNumRebels2

                    if iNumRebels:
                        for _ in range(iNumRebels):
                            iPlot = CvUtil.myRandom(len(rebelPlotArray), "rebelPlotArray")
                            NewUnit = barbPlayer.initUnit(iUnitType, rebelPlotArray[iPlot].getX(), rebelPlotArray[iPlot].getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
                            NewUnit.setImmobileTimer(1)
                        # ***TEST***
                        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Rebell erstellt",iNumRebels)), None, 2, None, ColorTypes(10), 0, 0, False, False)

                        # City Defender damage
                        doCityRevolt(pCity, iNumRebels + 1)

                        iRangeMaxPlayers = gc.getMAX_PLAYERS()
                        for iLoopPlayer in range(iRangeMaxPlayers):
                            pLoopPlayer = gc.getPlayer(iLoopPlayer)
                            iLoopTeam = pLoopPlayer.getTeam()
                            pLoopTeam = gc.getTeam(iLoopTeam)
                            if pLoopTeam.isHasMet(pPlayer.getTeam()) and pLoopPlayer.isHuman():
                                if iLoopPlayer == iPlayer:
                                    iColor = 7
                                else:
                                    iColor = 10
                                if iNumRebels == 1:
                                    CyInterface().addMessage(iLoopPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT_ONE", (pCity.getName(), pPlayer.getCivilizationAdjective(1), iNumRebels)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(iColor), pCity.getX(), pCity.getY(), True, True)
                                else:
                                    CyInterface().addMessage(iLoopPlayer, True, 8, CyTranslator().getText("TXT_KEY_REBELL_REVOLT", (pCity.getName(), pPlayer.getCivilizationAdjective(1), iNumRebels)), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Units/button_slave.dds", ColorTypes(iColor), pCity.getX(), pCity.getY(), True, True)

            # KI soll Stadtsklaven freistellen 1:4
            elif not pPlayer.isHuman():
                if CvUtil.myRandom(4, "Stadtsklaven freistellen") == 1:
                    PAE_Sklaven.doAIReleaseSlaves(pCity)

    # Sklaven oder Gladiatoren: sobald das Christentum entdeckt wurde -> 2% per 3 turn revolt
    iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
    if not bRevolt and gc.getGame().isReligionFounded(iReligion):
        if pPlayer.getStateReligion() != iReligion:
            iRand = CvUtil.myRandom(50, "ChristentumSklavenRevolte")
            if iRand == 0:
                # City Defender damage
                doCityRevolt(pCity, 4)
                bRevolt = True
                # Message to players
                iRangeMaxPlayers = gc.getMAX_PLAYERS()
                for iLoopPlayer in range(iRangeMaxPlayers):
                    pLoopPlayer = gc.getPlayer(iLoopPlayer)
                    iLoopTeam = pLoopPlayer.getTeam()
                    pLoopTeam = gc.getTeam(iLoopTeam)
                    if pLoopTeam.isHasMet(pPlayer.getTeam()) and pLoopPlayer.isHuman():
                        if iLoopPlayer == iPlayer:
                            iColor = 7
                        else:
                            iColor = 10
                        CyInterface().addMessage(iLoopPlayer, True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS", (pCity.getName(), pPlayer.getCivilizationAdjective(1))), None, InterfaceMessageTypes.MESSAGE_TYPE_INFO, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(iColor), pCity.getX(), pCity.getY(), True, True)

                # 1 settled Slave (Slave or gladiator) gets killed
                if iCitySlaves > 0 or iCityGlads > 0:
                    bChristSlaves = False
                    if iCitySlaves > 0 and iCityGlads > 0:
                        iRand = CvUtil.myRandom(2, "1 settled Slave (Slave or gladiator) gets killed")
                        bChristSlaves = (iRand == 0) # 0 = Slaves, 1 = Glads
                    else:
                        bChristSlaves = (iCitySlaves > 0) # either slaves or glads

                    if bChristSlaves:
                        if iCitySlavesHaus > 0 and iCitySlavesFood > 0 and iCitySlavesProd > 0:
                            iRand = CvUtil.myRandom(3, "bChristSlaves")
                            if iRand == 1:
                                pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                            elif iRand == 2:
                                pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                            else:
                                pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                        elif iCitySlavesHaus > 0 and iCitySlavesFood > 0:
                            iRand = CvUtil.myRandom(2, "bChristSlaves2")
                            if iRand == 1:
                                pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                            else:
                                pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                        elif iCitySlavesHaus > 0 and iCitySlavesProd > 0:
                            iRand = CvUtil.myRandom(2, "bChristSlaves3")
                            if iRand == 1:
                                pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                            else:
                                pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)
                        elif iCitySlavesFood > 0 and iCitySlavesProd > 0:
                            iRand = CvUtil.myRandom(2, "bChristSlaves4")
                            if iRand == 1:
                                pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                            else:
                                pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                        elif iCitySlavesFood > 0:
                            pCity.changeFreeSpecialistCount(eSpecialistFood, -1)
                        elif iCitySlavesProd > 0:
                            pCity.changeFreeSpecialistCount(eSpecialistProd, -1)
                        else:
                            pCity.changeFreeSpecialistCount(eSpecialistHouse, -1)

                        if pPlayer.isHuman():
                            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS_1_SLAVE", (pCity.getName(), )), None, 2, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
                    else:
                        pCity.changeFreeSpecialistCount(eSpecialistGlad, -1)
                        if pPlayer.isHuman():
                            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_REVOLT_CHRISTIANS_1_GLAD", (pCity.getName(), )), None, 2, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

    # Christentum kommt in die Stadt 5%
    if iCitySlaves > 0 and not bRevolt:
        iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
        if gc.getGame().isReligionFounded(iReligion):
            iRand = CvUtil.myRandom(20, "RELIGION_CHRISTIANITY")
            if iRand == 1:
                if not pCity.isHasReligion(iReligion):
                    pCity.setHasReligion(iReligion, 1, 1, 0)
                    if pPlayer.isHuman():
                        CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_SLAVES_SPREAD_CHRISTIANITY", (pCity.getName(), )), None, 2, "Art/Interface/Buttons/Actions/button_kreuz.dds", ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
def doMissionaryForCivs(iPlayer):
    pPlayer = gc.getPlayer(iPlayer)
    pCity = None
    (loopCity, pIter) = pPlayer.firstCity(False)
    while loopCity:
        # find first valid city
        if not loopCity.isNone() and loopCity.getOwner() == pPlayer.getID():
            pCity = loopCity
            break
        (loopCity, pIter) = pPlayer.nextCity(pIter, False)
    if pCity is not None:
        # # -- Nordischer Missionar fuer Germanen/Vandalen
        # if gc.getGame().getGameTurnYear() == -2250:
            # Civ = gc.getInfoTypeForString("CIVILIZATION_GERMANEN")
            # iRel = gc.getInfoTypeForString("RELIGION_NORDIC")
            # #if gc.getGame().isReligionFounded(iRel):
            # if pPlayer.getCivilizationType() == Civ and pPlayer.getStateReligion() != iRel:
                # iUnitType = gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY")
                # pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
                # if (pPlayer.isHuman()):
                    # popupInfo = CyPopupInfo()
                    # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                    # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_GALLIEN_MISSIONAR",("", )))
                    # popupInfo.addPopup(iPlayer)

        # -- Griechischer Missionar fuer Rom
        if gc.getGame().getGameTurnYear() == -1000:
            iRel = gc.getInfoTypeForString("RELIGION_GREEK")
            if gc.getGame().isReligionFounded(iRel):
                if pPlayer.getStateReligion() != iRel:
                    CivArray = [gc.getInfoTypeForString("CIVILIZATION_ROME")]
                    if pPlayer.getCivilizationType() in CivArray:
                        iUnitType = gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY")
                        pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
                        if pPlayer.isHuman():
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_ROM_MISSIONAR", ("", )))
                            popupInfo.addPopup(iPlayer)

        # #-- Aegyptischer Missionar fuer Nubien
        # if gc.getGame().getGameTurnYear() == -3000:
            # Civ = gc.getInfoTypeForString("CIVILIZATION_NUBIA")
            # iRel = gc.getInfoTypeForString("RELIGION_EGYPT")
            # #if gc.getGame().isReligionFounded(iRel):
            # if pPlayer.getCivilizationType() == Civ and pPlayer.getStateReligion() != iRel:
                # iUnitType = gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY")
                # pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
                # if pPlayer.isHuman():
                    # popupInfo = CyPopupInfo()
                    # popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                    # popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_EGYPT_MISSIONAR",("", )))
                    # popupInfo.addPopup(iPlayer)

def catchGreatPeople(pCity, iNewOwner, iPreviousOwner, bAssimilation):
    """# --- gets captured: 50 % | can flee: 40 % | get killed: 10 %"""
    pNewOwner = gc.getPlayer(iNewOwner)
    pPreviousOwner = gc.getPlayer(iPreviousOwner)
    pCityPlot = pCity.plot()
    lUnits = [
        [gc.getInfoTypeForString("UNIT_PROPHET"), 3, 3, 3],
        [gc.getInfoTypeForString("UNIT_ARTIST"), 3, 3, 3],
        [gc.getInfoTypeForString("UNIT_SCIENTIST"), 3, 3, 3],
        [gc.getInfoTypeForString("UNIT_MERCHANT"), 3 , 3, 3],
        [gc.getInfoTypeForString("UNIT_ENGINEER"), 3, 3, 4],
        [gc.getInfoTypeForString("UNIT_GREAT_GENERAL"), 11, 3, 10],
        [gc.getInfoTypeForString("UNIT_GREAT_SPY"), 4, 3, 4],
    ]
    numGPTypes = len(lUnits)
    if bAssimilation:
        lNumGP = [0] * numGPTypes
    else:
        lNumGP = [
            pCity.getFreeSpecialistCount(8),  # SPECIALIST_GREAT_PRIEST
            pCity.getFreeSpecialistCount(9),  # SPECIALIST_GREAT_ARTIST
            pCity.getFreeSpecialistCount(10),  # SPECIALIST_GREAT_SCIENTIST
            pCity.getFreeSpecialistCount(11),  # SPECIALIST_GREAT_MERCHANT
            pCity.getFreeSpecialistCount(12),  # SPECIALIST_GREAT_ENGINEER
            pCity.getFreeSpecialistCount(13),  # SPECIALIST_GREAT_GENERAL
            pCity.getFreeSpecialistCount(14)  # SPECIALIST_GREAT_SPY
        ]
        # guenstigen Plot aussuchen
        # mit pCityPlot.getNearestLandPlot() ist es sonst immer der gleiche
        fleePlotArray = []
        iX = pCity.getX()
        iY = pCity.getY()
        for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
            loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
            if loopPlot is not None and not loopPlot.isNone() and not loopPlot.isCity():
                if not loopPlot.isPeak() and not loopPlot.isWater():
                    if loopPlot.getNumUnits() > 0:
                        iRange = loopPlot.getNumUnits()
                        for n in range(iRange):
                            if loopPlot.getUnit(n).getOwner() == iPreviousOwner:
                                fleePlotArray.append(loopPlot)
                                break
                    else:
                        fleePlotArray.append(loopPlot)
        if not fleePlotArray:
            fleePlotArray.append(pCityPlot.getNearestLandPlot())

    bText = pNewOwner.isHuman()
    iNumFleePlots = len(fleePlotArray)
    bAlive = pPreviousOwner.isAlive()
    for i in range(numGPTypes):
        iCityGP = lNumGP[i]
        lUnit = lUnits[i]
        iNewUnit = lUnit[0]
        for _ in range(iCityGP):
            iRand = CvUtil.myRandom(10, "catchGreatPeople")
            if iRand < 5:
                CvUtil.spawnUnit(iNewUnit, pCityPlot, pNewOwner)
                if bText:
                    iRand = 1 + CvUtil.myRandom(lUnit[1], "TXT_KEY_MESSAGE_CATCH_GP")
                    text = CyTranslator().getText("TXT_KEY_MESSAGE_CATCH_GP"+str(i+1)+"_"+str(iRand), (0, 0))
                    CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(14), 0, 0, False, False)
            elif iRand < 9 and bAlive and iNumFleePlots != 0:
                iJump2Plot = CvUtil.myRandom(iNumFleePlots, "catchGreatPeopleFleePlot")
                CvUtil.spawnUnit(iNewUnit, fleePlotArray[iJump2Plot], pPreviousOwner)
                if bText:
                    iRand = 1 + CvUtil.myRandom(lUnit[2], "TXT_KEY_MESSAGE_FLEE_GP")
                    text = CyTranslator().getText("TXT_KEY_MESSAGE_FLEE_GP"+str(i+1)+"_"+str(iRand), (0, 0))
                    CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)
            elif bText:
                iRand = 1 + CvUtil.myRandom(lUnit[3], "TXT_KEY_MESSAGE_UNCATCH_GP")
                text = CyTranslator().getText("TXT_KEY_MESSAGE_UNCATCH_GP"+str(i+1)+"_"+str(iRand), (0, 0))
                CyInterface().addMessage(iNewOwner, True, 10, text, None, 2, None, ColorTypes(7), 0, 0, False, False)

def correctCityBuildings(pCity, pPlayer, pPreviousOwner):
    # Provinzpalast und Praefectur muss raus, Bischofssitz kann bleiben
    # TODO: wuerd es nicht reichen, die Eroberungswahrscheinlichkeit auf 0 zu stellen?
    iBuilding = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
    if pCity.isHasBuilding(iBuilding):
        pCity.setNumRealBuilding(iBuilding, 0)
    iBuilding = gc.getInfoTypeForString("BUILDING_PRAEFECTUR")
    if pCity.isHasBuilding(iBuilding):
        pCity.setNumRealBuilding(iBuilding, 0)
    # Spezialgebaeude muessen raus, weil nicht die Building_X erobert werden, sondern die BuildingClass_X !!!
    for i in range(9):
        iBuilding = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_SPECIAL"+str(i+1)))
        if iBuilding is not None and iBuilding != -1:
            if pCity.isHasBuilding(iBuilding):
                pCity.setNumRealBuilding(iBuilding, 0)
    # Palisade - Stadtmauer - Hohe/Breite Mauern
    iBuildingPalisade = gc.getInfoTypeForString("BUILDING_PALISADE")
    # prereq: BUILDINGCLASS_PALISADE
    iBuildingWalls1 = gc.getInfoTypeForString("BUILDING_WALLS")
    iBuildingWalls2 = gc.getInfoTypeForString("BUILDING_OPPIDUM")
    # prereq: BUILDINGCLASS_WALLS
    iBuildingHighWalls1 = gc.getInfoTypeForString("BUILDING_HIGH_WALLS")
    iBuildingHighWalls2 = gc.getInfoTypeForString("BUILDING_CELTIC_DUN")
    iBuildingHighWalls3 = gc.getInfoTypeForString("BUILDING_HIGH_WALLS_GRECO")
    if pCity.isHasBuilding(iBuildingHighWalls1) or pCity.isHasBuilding(iBuildingHighWalls2) or pCity.isHasBuilding(iBuildingHighWalls3):
        if not pCity.isHasBuilding(iBuildingWalls1) and not pCity.isHasBuilding(iBuildingWalls2):
            iBuilding = gc.getCivilizationInfo(pPreviousOwner.getCivilizationType()).getCivilizationBuildings(gc.getInfoTypeForString("BUILDINGCLASS_WALLS"))
            pCity.setNumRealBuilding(iBuilding, 1)
    if pCity.isHasBuilding(iBuildingWalls1) or pCity.isHasBuilding(iBuildingWalls2):
        if not pCity.isHasBuilding(iBuildingPalisade):
            pCity.setNumRealBuilding(iBuildingPalisade, 1)

def doFreeTechMissionary(iTechType, iPlayer):
    pPlayer = gc.getPlayer(iPlayer)

    # Religionen
    lTechs = {
        gc.getInfoTypeForString("TECH_RELIGION_NORDIC"): gc.getInfoTypeForString("UNIT_NORDIC_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_CELTIC"): gc.getInfoTypeForString("UNIT_CELTIC_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_SUMER"): gc.getInfoTypeForString("UNIT_SUMER_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_GREEK"): gc.getInfoTypeForString("UNIT_GREEK_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_EGYPT"): gc.getInfoTypeForString("UNIT_EGYPT_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_PHOEN"): gc.getInfoTypeForString("UNIT_PHOEN_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_HINDU"): gc.getInfoTypeForString("UNIT_HINDU_MISSIONARY"),
        gc.getInfoTypeForString("TECH_RELIGION_ROME"): gc.getInfoTypeForString("UNIT_ROME_MISSIONARY"),
        gc.getInfoTypeForString("TECH_DUALISMUS"): gc.getInfoTypeForString("UNIT_ZORO_MISSIONARY"),
        gc.getInfoTypeForString("TECH_FRUCHTBARKEIT"): gc.getInfoTypeForString("UNIT_EXECUTIVE_2"),
        gc.getInfoTypeForString("TECH_MANUFAKTUREN"): gc.getInfoTypeForString("UNIT_EXECUTIVE_3"),
        gc.getInfoTypeForString("TECH_GLADIATOR"): gc.getInfoTypeForString("UNIT_EXECUTIVE_5"),
    }

    # Einheit erstellen
    try:
        iUnit = lTechs[iTechType]
        # Zufallsstadt auswaehlen
        lCities = []
        (loopCity, pIter) = pPlayer.firstCity(False)
        while loopCity:
            if not loopCity.isNone() and loopCity.getOwner() == iPlayer: #only valid cities
                lCities.append(loopCity)
            (loopCity, pIter) = pPlayer.nextCity(pIter, False)

        if lCities:
            iRandCity = lCities[CvUtil.myRandom(len(lCities), "doFreeTechMissionary")]
            NewUnit = pPlayer.initUnit(iUnit, iRandCity.getX(), iRandCity.getY(), UnitAITypes.UNITAI_MISSIONARY, DirectionTypes.DIRECTION_SOUTH)
            # Matriarchist
            if iTechType == gc.getInfoTypeForString("TECH_FRUCHTBARKEIT"):
                # Verschiedene Gottesanbeter
                lCivs = {
                    gc.getInfoTypeForString("CIVILIZATION_CELT"): "TXT_KEY_UNIT_MATRIACHAT_CELTS",
                    gc.getInfoTypeForString("CIVILIZATION_GERMANEN"): "TXT_KEY_UNIT_MATRIACHAT_GERMAN",
                    gc.getInfoTypeForString("CIVILIZATION_ROME"): "TXT_KEY_UNIT_MATRIACHAT_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_GREECE"): "TXT_KEY_UNIT_MATRIACHAT_GREEK",
                    gc.getInfoTypeForString("CIVILIZATION_ATHENS"): "TXT_KEY_UNIT_MATRIACHAT_GREEK",
                    gc.getInfoTypeForString("CIVILIZATION_THEBAI"): "TXT_KEY_UNIT_MATRIACHAT_GREEK",
                    gc.getInfoTypeForString("CIVILIZATION_SPARTA"): "TXT_KEY_UNIT_MATRIACHAT_GREEK",
                    gc.getInfoTypeForString("CIVILIZATION_EGYPT"): "TXT_KEY_UNIT_MATRIACHAT_EGYPT",
                    gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"): "TXT_KEY_UNIT_MATRIACHAT_PHOEN",
                    gc.getInfoTypeForString("CIVILIZATION_PHON"): "TXT_KEY_UNIT_MATRIACHAT_PHOEN",
                    gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"): "TXT_KEY_UNIT_MATRIACHAT_ILLYRIA",
                    gc.getInfoTypeForString("CIVILIZATION_BABYLON"): "TXT_KEY_UNIT_MATRIACHAT_BABYLON",
                    gc.getInfoTypeForString("CIVILIZATION_SUMERIA"): "TXT_KEY_UNIT_MATRIACHAT_SUMER",
                    gc.getInfoTypeForString("CIVILIZATION_HETHIT"): "TXT_KEY_UNIT_MATRIACHAT_HITTI",
                    gc.getInfoTypeForString("CIVILIZATION_PERSIA"): "TXT_KEY_UNIT_MATRIACHAT_PERSIA",
                    gc.getInfoTypeForString("CIVILIZATION_BERBER"): "TXT_KEY_UNIT_MATRIACHAT_BERBER",
                    gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"): "TXT_KEY_UNIT_MATRIACHAT_BERBER",
                    gc.getInfoTypeForString("CIVILIZATION_IBERER"): "TXT_KEY_UNIT_MATRIACHAT_IBERIA",
                    gc.getInfoTypeForString("CIVILIZATION_DAKER"): "TXT_KEY_UNIT_MATRIACHAT_DACIA",
                    gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"): "TXT_KEY_UNIT_MATRIACHAT_SCYTHS",
                }
                # Verschiedene Gottesanbeter
                try:
                    text = CyTranslator().getText(lCivs[pPlayer.getCivilizationType()], ("",))
                    text = text + " " + CyTranslator().getText("TXT_KEY_UNIT_KULT_FOLLOWER", ("",))
                    NewUnit.setName(text)
                except KeyError:
                    pass

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Matriachist bekommen (Zeile 2848)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Heroenkultist
            elif iTechType == gc.getInfoTypeForString("TECH_GLADIATOR"):
                lCivs = {
                    gc.getInfoTypeForString("CIVILIZATION_CELT"): "TXT_KEY_UNIT_HEROEN_CELTS",
                    gc.getInfoTypeForString("CIVILIZATION_GERMANEN"): "TXT_KEY_UNIT_HEROEN_GERMAN",
                    gc.getInfoTypeForString("CIVILIZATION_ROME"): "TXT_KEY_UNIT_HEROEN_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_GREECE"): "TXT_KEY_UNIT_HEROEN_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_ATHENS"): "TXT_KEY_UNIT_HEROEN_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_THEBAI"): "TXT_KEY_UNIT_HEROEN_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_SPARTA"): "TXT_KEY_UNIT_HEROEN_ROME",
                    gc.getInfoTypeForString("CIVILIZATION_EGYPT"): "TXT_KEY_UNIT_HEROEN_EGYPT",
                    gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"): "TXT_KEY_UNIT_HEROEN_PHOEN",
                    gc.getInfoTypeForString("CIVILIZATION_PHON"): "TXT_KEY_UNIT_HEROEN_PHOEN",
                    gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"): "TXT_KEY_UNIT_HEROEN_PHOEN",
                    gc.getInfoTypeForString("CIVILIZATION_BABYLON"): "TXT_KEY_UNIT_HEROEN_BABYLON",
                    gc.getInfoTypeForString("CIVILIZATION_SUMERIA"): "TXT_KEY_UNIT_HEROEN_SUMER",
                    gc.getInfoTypeForString("CIVILIZATION_HETHIT"): "TXT_KEY_UNIT_HEROEN_HITTI",
                    gc.getInfoTypeForString("CIVILIZATION_PERSIA"): "TXT_KEY_UNIT_HEROEN_PERSIA",
                }
                # Verschiedene Gottesanbeter
                try:
                    text = CyTranslator().getText(lCivs[pPlayer.getCivilizationType()], ("",))
                    text = text + " " + CyTranslator().getText("TXT_KEY_UNIT_KULT_FOLLOWER", ("",))
                    NewUnit.setName(text)
                except KeyError:
                    pass
    except KeyError:
        pass

def doFreeTechSettler(iTechType, pPlayer):
    lSettlerCivs = [
        gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"),
        gc.getInfoTypeForString("CIVILIZATION_PHON"),
        gc.getInfoTypeForString("CIVILIZATION_GREECE"),
        gc.getInfoTypeForString("CIVILIZATION_ATHENS"),
        gc.getInfoTypeForString("CIVILIZATION_THEBAI"),
        gc.getInfoTypeForString("CIVILIZATION_SPARTA"),
        gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"),
        gc.getInfoTypeForString("CIVILIZATION_PERSIA"),
        gc.getInfoTypeForString("CIVILIZATION_BABYLON"),
        gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"),
        gc.getInfoTypeForString("CIVILIZATION_ISRAEL"),
        gc.getInfoTypeForString("CIVILIZATION_LYDIA"),
        gc.getInfoTypeForString("CIVILIZATION_INDIA"),
        gc.getInfoTypeForString("CIVILIZATION_ROME")
    ]
    lSettlerTechs = [
        gc.getInfoTypeForString("TECH_GEOMETRIE"),
        gc.getInfoTypeForString("TECH_SCHIFFSBAU"),
        gc.getInfoTypeForString("TECH_DUALISMUS"),
        gc.getInfoTypeForString("TECH_RELIGION_CELTIC"),
        gc.getInfoTypeForString("TECH_RELIGION_NORDIC"),
        gc.getInfoTypeForString("TECH_RELIGION_ROME"),
        gc.getInfoTypeForString("TECH_PERSIAN_ROAD")
    ]
    if iTechType in lSettlerTechs or (iTechType == gc.getInfoTypeForString("TECH_COLONIZATION2") and pPlayer.getCivilizationType() in lSettlerCivs):
        # Einheit erstellen
        pCapital = pPlayer.getCapitalCity()
        if pCapital is not None and not pCapital.isNone():
            CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_SETTLER"), pCapital.plot(), pPlayer)


def getTechOnConquer(pCity, iPreviousOwner, iNewOwner):
    pPlayer = gc.getPlayer(iNewOwner)
    pPreviousOwner = gc.getPlayer(iPreviousOwner)
    pTeamOld = gc.getTeam(pPreviousOwner.getTeam())
    pTeamNew = gc.getTeam(pPlayer.getTeam())

    bGetTech = False
    if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ARCHIVE")) or pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_LIBRARY")):
        bGetTech = True
    iRand = CvUtil.myRandom(3, "getTechOnConquer")
    if iRand == 1 or bGetTech:
        bGetTech = False  # falls es keine Tech gibt, dann Forschungsbonus

        TechArray = []
        for i in range(gc.getNumTechInfos()):
            if pTeamOld.isHasTech(i) and not pTeamNew.isHasTech(i):
                if gc.getTechInfo(i) is not None and gc.getTechInfo(i).isTrade():
                    TechArray.append(i)
        if TechArray:
            bGetTech = True
            iTechRand = CvUtil.myRandom(len(TechArray), "getTechOnConquer2")
            iTech = TechArray[iTechRand]
            if pPlayer.getCurrentResearch() == iTech:
                pTeamNew.setResearchProgress(iTech, gc.getTechInfo(iTech).getResearchCost()-1, iNewOwner)
            pTeamNew.setHasTech(iTech, 1, iNewOwner, 0, 1)
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_POPUP_GETTING_TECH", (gc.getTechInfo(iTech).getDescription(), )))
                popupInfo.addPopup(iNewOwner)
            else:
                pPlayer.clearResearchQueue()
            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Tech erhalten (Zeile 3465)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Forschungsbonus auf derzeitige Forschung
    if not bGetTech:
        iTechOld = pPreviousOwner.getCurrentResearch()
        iTechNew = pPlayer.getCurrentResearch()

        #iEraPercent = gc.getEraInfo(gc.getTechInfo(iTechNew).getEra()).getResearchPercent()

        # Beim Gewinner: Ein Drittel der Zeit verkuerzen
        # Beim Verlierer: Ein Viertel der Zeit verlaengern
        # Forschungkosten != reale Kosten (+% in Era und Schwierigkeitsgrad)
        if iTechNew != -1:
            iProgress = int(gc.getTechInfo(iTechNew).getResearchCost() / 4) + pCity.getPopulation() * 10
            # Halber Wert bei unterentwickelter CIV
            if pPreviousOwner.getTechScore() < pPlayer.getTechScore():
                iProgress = iProgress / 2

            # No auto-grant, so set to 1 less of full amount => stimmt nicht, weil bei Cost nicht +% von Era und Schw.grad miteinberechnet wird
            # if pTeamNew.getResearchProgress(iTechNew) + iProgress >= gc.getTechInfo(iTechNew).getResearchCost():
            #  iProgress = pTeamNew.getResearchProgress(iTechNew) + iProgress - gc.getTechInfo(iTechNew).getResearchCost() - 1
            pTeamNew.changeResearchProgress(iTechNew, iProgress, iNewOwner)
            if pPlayer.isHuman():
                CyInterface().addMessage(iNewOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_CONQUER_RESEARCH_WINNER", (iProgress,)), None, 2, None, ColorTypes(8), 0, 0, False, False)

        if iTechOld != -1:
            iProgress = int(gc.getTechInfo(iTechOld).getResearchCost() / 4) + pCity.getPopulation() * 10
            iProgress = min(iProgress, pTeamOld.getResearchProgress(iTechOld))
            # Halber Wert bei unterentwickelter CIV
            if pPreviousOwner.getTechScore() < pPlayer.getTechScore():
                iProgress = iProgress / 2
            pTeamOld.changeResearchProgress(iTechOld, -iProgress, iPreviousOwner)
            if pPreviousOwner.isHuman():
                CyInterface().addMessage(iPreviousOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_CONQUER_RESEARCH_LOSER", (iProgress,)), None, 2, None, ColorTypes(7), 0, 0, False, False)

def getGoldkarren(pCity, pPlayer):
    iBeute = int(pCity.getPopulation() / 2)
    if iBeute > 0:
        for _ in range(iBeute):
            CvUtil.spawnUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), pCity.plot(), pPlayer)

def doRefugeeToNeighborCity(pCity, iPreviousOwner, iNewOwner):
    # --- Bevoelkerungszuwachs bei Nachbarstaedten (50% Chance pro Stadt fuer + 1 Pop)
    # --- PAE V Patch4: ab Pop 3 (sonst exploit)
    iX = pCity.getX()
    iY = pCity.getY()
    for x in range(-5, 6):
        for y in range(-5, 6):
            loopPlot = plotXY(iX, iY, x, y)
            if loopPlot is not None and not loopPlot.isNone():
                if loopPlot.isCity():
                    loopCity = loopPlot.getPlotCity()
                    iLoopOwner = loopCity.getOwner()
                    if iLoopOwner != -1 and iLoopOwner != iNewOwner:
                        iRand = CvUtil.myRandom(2, "doRefugeeToNeighborCity")
                        if iRand == 1:
                            loopCity.changePopulation(1)
                            if gc.getPlayer(iLoopOwner).isHuman():
                                CyInterface().addMessage(iLoopOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_POP", (pCity.getName(), loopCity.getName())), None, 2, "Art/Interface/Buttons/Units/button_emigrant.dds", ColorTypes(13), loopPlot.getX(), loopPlot.getY(), True, True)
                            # Kultur
                            iCulture = pCity.getCulture(iLoopOwner)
                            iPop = loopCity.getPopulation()
                            if iCulture > 1 and iPop > 0:
                                iChangeCulture = iCulture / iPop
                                loopCity.changeCulture(iPreviousOwner, iChangeCulture, 0)
                            # PAE Provinzcheck
                            doCheckCityState(loopCity)
                            # ***TEST***
                            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Stadtpop gewachsen durch Krieg (Zeile 3493)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

def removeSwamp(pCity, sText):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    bFeatSwamp = False
    terrain_swamp = gc.getInfoTypeForString('TERRAIN_SWAMP')
    terrain_grass = gc.getInfoTypeForString('TERRAIN_GRASS')
    iX = pCity.getX()
    iY = pCity.getY()
    for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
        loopPlot = plotDirection(iX, iY, DirectionTypes(iI))
        if loopPlot is not None and not loopPlot.isNone():
            if loopPlot.getTerrainType() == terrain_swamp:
                loopPlot.setTerrainType(terrain_grass, 1, 1)
                bFeatSwamp = True
    if bFeatSwamp and pPlayer.isHuman():
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText(sText,(pCity.getName(),)), None, 2, None, ColorTypes(14), iX, iY, False, False)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Sumpf wird entfernt (Zeile 2232)",1)), None, 2, None, ColorTypes(10), iX, iY, False, False)


def doMessageWonderCapture(pCity):
    iOwner = pCity.getOwner()
    if pCity.getNumWorldWonders() > 0:
        for i in range(gc.getNumBuildingInfos()):
            eLoopBuilding = gc.getBuildingInfo(i)
            if pCity.isHasBuilding(i):
                eBuildingClass = gc.getBuildingClassInfo(eLoopBuilding.getBuildingClassType())
                if eBuildingClass.getMaxGlobalInstances() == 1:
                    pPlayer = gc.getPlayer(iOwner)
                    for iLoopPlayer in range(gc.getMAX_PLAYERS()):
                        pLoopPlayer = gc.getPlayer(iLoopPlayer)
                        pLoopTeam = gc.getTeam(pLoopPlayer.getTeam())
                        if pLoopTeam.isHasMet(pPlayer.getTeam()) and pLoopPlayer.isHuman():
                            if iLoopPlayer == iOwner:
                                CyInterface().addMessage(iLoopPlayer, False, 10, CyTranslator().getText("TXT_KEY_WONDER_CAPTURE_YOU", (pPlayer.getName(), eLoopBuilding.getDescription())), '', 0, eLoopBuilding.getButton(), ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
                            else:
                                CyInterface().addMessage(iLoopPlayer, False, 10, CyTranslator().getText("TXT_KEY_WONDER_CAPTURE", (pPlayer.getName(), eLoopBuilding.getDescription())), '', 0, eLoopBuilding.getButton(), ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
