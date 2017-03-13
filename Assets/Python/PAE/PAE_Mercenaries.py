# Mercenary feature
# By Flunky

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random
import PyHelpers

### Defines
gc = CyGlobalContext()
localText = CyTranslator()

### Globals
PAEInstanceHiringModifier = {}

# Reminder: How to use ScriptData: CvUtil.getScriptData(pUnit, ["b"], -1), CvUtil.addScriptData(pUnit, "b", eBonus) (add uses string, get list of strings)
# getScriptData returns string => cast might be necessary
# Update (Ramk): No, CvUtil-Functions unpack an dict. You could directly use int, etc.

# Used keys for UnitScriptData:
# "x"/"y": coordinates of plots where bonus was picked up (merchants)
# "b": index of bonus stored in merchant/cultivation unit (only one at a time)
# "originCiv": original owner of the bonus stored in merchant (owner of the city where it was bought)

def myRandom (num):
    #return gc.getGame().getMapRandNum(num, None)
    if num <= 1: return 0
    else: return random.randint(0, num-1)

def onModNetMessage(argsList):
    global PAEInstanceHiringModifier
    # Hire or Commission Mercenary Menu
    iData0, iData1, iData2, iData3, iData4 = argsList
    if iData0 == 707:
        # iData1, iData2, ...
        # 707, iCityID, -1, -1, iPlayer
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)
        iCity = iData1
        pCity = pPlayer.getCity(iCity)

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_MAIN" + str(1 + myRandom(5)),(pCity.getName(),)))
        popupInfo.setData1(iCity) # CityID
        popupInfo.setData2(iPlayer)
        popupInfo.setOnClickedPythonCallback("popupMercenariesMain") # EntryPoints/CvScreenInterface und CvGameUtils -> 708, 709 usw
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE",("", )), "Art/Interface/Buttons/Actions/button_action_mercenary_hire.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN",("", )), "Art/Interface/Buttons/Actions/button_action_mercenary_assign.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # Hire Mercenaries
    elif iData0 == 708:
        # iData1, iData2, ... iData5 = iPlayer
        # 708, iCityID, iButtonID (Typ), iButtonID (Unit), iButtonID (Cancel)

        iCity = iData1
        iTypeButton = iData2
        iUnitButton = iData3
        iPlayer = iData4
        doHireMercenariesPopup(iCity, iTypeButton, iUnitButton, iPlayer)

    # Commission Mercenaries (CIV)
    elif iData0 == 709:
        # iData1, iData2, ...
        # 709, (1) -1 (2) iButtonId (CIV) , -1, -1, iPlayer
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        # Check neighbours
        lNeighbors = []
        iRange = gc.getMAX_PLAYERS()
        for iLoopPlayer in range (iRange):
            pLoopPlayer = gc.getPlayer(iLoopPlayer)
            if iLoopPlayer != gc.getBARBARIAN_PLAYER() and iLoopPlayer != iPlayer:
                if pLoopPlayer.isAlive():
                    if gc.getTeam(pLoopPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
                        lNeighbors.append(iLoopPlayer)


        if iData1 != -1 and iData1 < len(lNeighbors):
            iData0 = 710
            iData1 = lNeighbors[iData1]

        # First screen (Civilizations)
        else:
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN1",("",)))
            popupInfo.setOnClickedPythonCallback("popupMercenariesAssign1") # EntryPoints/CvScreenInterface -> 709
            popupInfo.setData3(iPlayer)

            # List neighbors ---------
            # Friendly >= +10
            # Pleased >= +3
            # Cautious: -
            # Annoyed: <= -3
            # Furious: <= -10
            # ATTITUDE_FRIENDLY
            # ATTITUDE_PLEASED
            # ATTITUDE_CAUTIOUS
            # ATTITUDE_ANNOYED
            # ATTITUDE_FURIOUS
            if len(lNeighbors) == 0:
                popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN1_1",("",)))
            else:
                for iLoopPlayer in lNeighbors:
                    pLoopPlayer = gc.getPlayer(iLoopPlayer)
                    eAtt = pLoopPlayer.AI_getAttitude(iPlayer)
                    if   eAtt == AttitudeTypes.ATTITUDE_FRIENDLY: szBuffer = "<color=0,255,0,255>"
                    elif eAtt == AttitudeTypes.ATTITUDE_PLEASED:  szBuffer = "<color=0,155,0,255>"
                    elif eAtt == AttitudeTypes.ATTITUDE_CAUTIOUS: szBuffer = "<color=255,255,0,255>"
                    elif eAtt == AttitudeTypes.ATTITUDE_ANNOYED:  szBuffer = "<color=255,180,0,255>"
                    elif eAtt == AttitudeTypes.ATTITUDE_FURIOUS:  szBuffer = "<color=255,0,0,255>"

                    szBuffer = szBuffer + " (" + localText.getText("TXT_KEY_"+str(eAtt), ()) + ")"
                    popupInfo.addPythonButton(pLoopPlayer.getCivilizationShortDescription(0) + szBuffer, gc.getCivilizationInfo(pLoopPlayer.getCivilizationType()).getButton())
                    #popupInfo.addPythonButton(gc.getCivilizationInfo(pLoopPlayer.getCivilizationType()).getText(), gc.getCivilizationInfo(pLoopPlayer.getCivilizationType()).getButton())

            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
            popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
            popupInfo.addPopup(iPlayer)


    # Commission Mercenaries (Inter/national mercenaries)
    # on-site
    # local
    # international
    # elite
    if iData0 == 710:
        # Werte von 709 weitervererbt
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2",("",)))
        popupInfo.setOnClickedPythonCallback("popupMercenariesAssign2") # EntryPoints/CvScreenInterface -> 711
        popupInfo.setData1(iData1) # iTargetPlayer
        popupInfo.setData3(iPlayer) # iPlayer

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_1",("", )), gc.getCivilizationInfo(gc.getPlayer(iData1).getCivilizationType()).getButton())
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_2",("", )), gc.getCivilizationInfo(pPlayer.getCivilizationType()).getButton())
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_3",("", )), "Art/Interface/Buttons/Actions/button_action_merc_international.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN2_4",("", )), "Art/Interface/Buttons/Actions/button_action_merc_elite.dds")

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (mercenary size)
    # small
    # medium
    # large
    # army
    elif iData0 == 711:
        # iData1, iData2, iData3, ...
        # 710, iTargetPlayer, iFaktor, -1, iPlayer
        # iFaktor:
        # 1: Urban (iTargetCiv) +200 Kosten
        # 2: Own units          +300
        # 3: international      +400
        # 4: elite              +500
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3",("", )) )
        popupInfo.setOnClickedPythonCallback("popupMercenariesAssign3") # EntryPoints/CvScreenInterface -> 712
        popupInfo.setData1(iData1) # iTargetPlayer
        popupInfo.setData2(iData2) # iFaktor
        popupInfo.setData3(iPlayer) # iPlayer

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_1",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries1.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_2",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries2.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_3",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries3.dds")
        if iData2 != 4: popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN3_4",("", )), "Art/Interface/Buttons/Actions/button_action_mercenaries4.dds")

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (primary unit types)
    # defensice
    # ranged combat
    # offensive
    # city attack
    elif iData0 == 712:
        # iData1, iData2, iData3, ...
        # 710, iTargetPlayer, iFaktor, -1, iPlayer
        # iFaktor:
        # 10: small group    +0
        # 20: medium group   +150
        # 30: big group      +300
        # 40: huge group     +400
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4",("", )) )
        popupInfo.setOnClickedPythonCallback("popupMercenariesAssign4") # EntryPoints/CvScreenInterface -> 713
        popupInfo.setData1(iData1) # iTargetPlayer
        popupInfo.setData2(iData2) # iFaktor
        popupInfo.setData3(iPlayer) # iPlayer

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_1",("", )), "Art/Interface/Buttons/Promotions/tarnung.dds")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_2",("", )), ",Art/Interface/Buttons/Promotions/Cover.dds,Art/Interface/Buttons/Promotions_Atlas.dds,2,5")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_3",("", )), ",Art/Interface/Buttons/Promotions/Shock.dds,Art/Interface/Buttons/Promotions_Atlas.dds,4,5")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN4_4",("", )), ",Art/Interface/Buttons/Promotions/CityRaider1.dds,Art/Interface/Buttons/Promotions_Atlas.dds,5,2")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_UNITCOMBAT_NAVAL",("", )), ",Art/Interface/Buttons/Promotions/Naval_Units.dds,Art/Interface/Buttons/Promotions_Atlas.dds,3,7")

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (siege units)
    elif iData0 == 713:
        # iData1, iData2, iData3, ...
        # 710, iTargetPlayer, iFaktor, -1, iPlayer
        # iFaktor:
        # 100: defensive
        # 200: ranged
        # 300: offensive
        # 400: city raiders
        # 500: naval units
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5",("", )) )
        popupInfo.setOnClickedPythonCallback("popupMercenariesAssign5") # EntryPoints/CvScreenInterface -> 714
        popupInfo.setData1(iData1) # iTargetPlayer
        popupInfo.setData2(iData2) # iFaktor
        popupInfo.setData3(iPlayer) # iPlayer

        if gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_MECHANIK")) > 0:
          iUnit = gc.getInfoTypeForString("UNIT_BATTERING_RAM2")
          szName = localText.getText("TXT_KEY_UNIT_BATTERING_RAM2_PLURAL", ())
        elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_WEHRTECHNIK")) > 0:
          iUnit = gc.getInfoTypeForString("UNIT_BATTERING_RAM")
          szName = localText.getText("TXT_KEY_UNIT_BATTERING_RAM_PLURAL", ())
        elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_BELAGERUNG")) > 0:
          iUnit = gc.getInfoTypeForString("UNIT_RAM")
          szName = localText.getText("TXT_KEY_UNIT_RAM_PLURAL", ())
        else: iUnit = -1

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_1",("", )), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")
        if iUnit != -1:
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 2, 50)), gc.getUnitInfo(iUnit).getButton())
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 4, 90)), gc.getUnitInfo(iUnit).getButton())
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN5_2",(szName, 6, 120)), gc.getUnitInfo(iUnit).getButton())

        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (confirmation)
    elif iData0 == 714:
        # iData1, iData2, iData3, ...
        # 710, iTargetPlayer, iFaktor, -1, iPlayer
        # iFaktor:
        # 1000: no siege +0
        # 2000: 2x       +50
        # 3000: 4x       +90
        # 4000: 6x       +120
        iPlayer = iData4
        pPlayer = gc.getPlayer(iPlayer)

        # Kosten berechnen
        sFaktor = str(iData2)
        iCost = 0
        # siege units
        if sFaktor[0] == "2":   iCost += 50
        elif sFaktor[0] == "3": iCost += 90
        elif sFaktor[0] == "4": iCost += 120
        # size
        if sFaktor[2] == "2":   iCost += 150
        elif sFaktor[2] == "3": iCost += 300
        elif sFaktor[2] == "4": iCost += 400
        # inter/national
        if sFaktor[3] == "1":   iCost += 200
        elif sFaktor[3] == "2": iCost += 300
        elif sFaktor[3] == "3": iCost += 400
        elif sFaktor[3] == "4": iCost += 500
        # ----------

        szText = ""
        if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM")):
          iCost -= iCost/4
          szText = CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN_BONUS",(25,))

        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_ASSIGN6",(gc.getPlayer(iData1).getCivilizationShortDescription(0), iCost, szText)) )
        popupInfo.setOnClickedPythonCallback("popupMercenariesAssign6") # EntryPoints/CvScreenInterface -> 715
        popupInfo.setData1(iData1) # iTargetPlayer
        popupInfo.setData2(iData2) # iFaktor
        popupInfo.setData3(iPlayer) # iPlayer

        # Confirm
        popupInfo.addPythonButton(CyTranslator().getText( "TXT_KEY_POPUP_MERCENARIES_ASSIGN6_" + str(1 + myRandom(13)) , ("", ) ), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
        popupInfo.addPopup(iPlayer)

    # Commission Mercenaries (confirmation)
    elif iData0 == 715:
        # iData1, iData2, iData3, ...
        # 715, iTargetPlayer, iFaktor, -1, iPlayer
        # iFaktor: 1111 - 4534
        doCommissionMercenaries(iData1,iData2,iData4)

    # Mercenaries Torture / Folter
    elif iData0 == 716:
        # iData1, iData2, iData3
        # 716, iMercenaryCiv, iPlayer
        iPlayer = iData2
        iMercenaryCiv = iData1
        pPlayer = gc.getPlayer(iPlayer)

        if pPlayer.getGold() < 80:
          if gc.getPlayer(iPlayer).isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
            popupInfo.addPopup(iPlayer)
        else:
          pPlayer.changeGold(-80)
          if 0 == myRandom(2): doFailedMercenaryTortureMessage(iPlayer)
          else:
            # Check neighbours
            lNeighbors = []
            iRange = gc.getMAX_PLAYERS()
            for iLoopPlayer in xrange (iRange):
              pLoopPlayer = gc.getPlayer(iLoopPlayer)
              if iLoopPlayer != gc.getBARBARIAN_PLAYER():
                if pLoopPlayer.isAlive():
                  if gc.getTeam(pLoopPlayer.getTeam()).isHasMet(pPlayer.getTeam()) or iLoopPlayer == iPlayer:
                    lNeighbors.append(iLoopPlayer)

            # select neighbours if more than 5
            while len(lNeighbors) > 5:
              iRand = myRandom(len(lNeighbors))
              if lNeighbors[iRand] != iMercenaryCiv:
                lNeighbors.remove(lNeighbors[iRand])

            szText = CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE2",("",)) + localText.getText("[NEWLINE]", ())
            # List neighbors ---------
            # ATTITUDE_FRIENDLY
            # ATTITUDE_PLEASED
            # ATTITUDE_CAUTIOUS
            # ATTITUDE_ANNOYED
            # ATTITUDE_FURIOUS
            for iLoopPlayer in lNeighbors:
              pLoopPlayer = gc.getPlayer(iLoopPlayer)
              eAtt = pLoopPlayer.AI_getAttitude(iPlayer)
              if   eAtt == AttitudeTypes.ATTITUDE_FRIENDLY: szBuffer = "<color=0,255,0,255>"
              elif eAtt == AttitudeTypes.ATTITUDE_PLEASED:  szBuffer = "<color=0,155,0,255>"
              elif eAtt == AttitudeTypes.ATTITUDE_CAUTIOUS: szBuffer = "<color=255,255,0,255>"
              elif eAtt == AttitudeTypes.ATTITUDE_ANNOYED:  szBuffer = "<color=255,180,0,255>"
              elif eAtt == AttitudeTypes.ATTITUDE_FURIOUS:  szBuffer = "<color=255,0,0,255>"

              szText = szText + localText.getText("[NEWLINE][ICON_STAR] <color=255,255,255,255>", ()) + pLoopPlayer.getCivilizationShortDescription(0) + szBuffer + " (" + localText.getText("TXT_KEY_"+str(eAtt), ()) + ")"



            szText = szText + localText.getText("[NEWLINE][NEWLINE]<color=255,255,255,255>", ()) + CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE2_1",("", ))
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
            popupInfo.setText(szText)
            popupInfo.setData1(iMercenaryCiv) # iMercenaryCiv
            popupInfo.setData2(iPlayer) # iPlayer
            popupInfo.setOnClickedPythonCallback("popupMercenaryTorture2") # EntryPoints/CvScreenInterface und CvGameUtils -> 717
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES1",(75,50)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES2",(50,25)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_YES3",(25,10)), "")
            popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
            popupInfo.addPopup(iPlayer)


    # Mercenaries Torture 2
    elif iData0 == 717:
        # iData1, iData2, iData3, iData4
        # 717, iMercenaryCiv, iPlayer, iButtonId
        iPlayer = iData2
        iMercenaryCiv = iData1
        pPlayer = gc.getPlayer(iPlayer)

        if iData3 == 0:
          iGold = 75
          iChance = 10
        elif iData3 == 1:
          iGold = 50
          iChance = 5
        elif iData3 == 2:
          iGold = 25
          iChance = 2

        if pPlayer.getGold() < iGold:
          if gc.getPlayer(iPlayer).isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
            popupInfo.addPopup(iPlayer)
        else:

          pPlayer.changeGold(-iGold)
          if iChance < myRandom(20): doFailedMercenaryTortureMessage(iPlayer)
          else:
            if iPlayer != iMercenaryCiv:
              CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_1",(gc.getPlayer(iMercenaryCiv).getCivilizationShortDescription(0),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_1",(gc.getPlayer(iMercenaryCiv).getCivilizationShortDescription(0), )))
              popupInfo.addPopup(iPlayer)
            else:
              CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_2",("",)), None, 2, None, ColorTypes(8), 0, 0, False, False)
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE3_2",("", )))
              popupInfo.addPopup(iPlayer)

# Test for actually required techs and bonusses
def getAvailableUnits(lNeighbors, lTestUnits):
    lUnits = []
    for pNeighbor in lNeighbors:
        if len(lTestUnits) == len(lUnits): break
        for eLoopUnit in lTestUnits:
            if eLoopUnit not in lUnits:
                if canTrain(eLoopUnit, pNeighbor):
                    lUnits.append(eLoopUnit)
    return lUnits

def getCost(eUnit, iMultiplier, bCivicSoeldner, iExtraMultiplier = 1):
    iCost = gc.getUnitInfo(eUnit).getProductionCost() * iExtraMultiplier
    iCost += (iCost / 10) * 2 * iMultiplier
    if bCivicSoeldner: iCost -= iCost/4
    return int(iCost)

# Einheiten einen Zufallsrang vergeben (max. Elite)
def doMercenaryRanking (pUnit, iMinRang, iMaxRang):
    lRang = [
        gc.getInfoTypeForString("PROMOTION_COMBAT1"),
        gc.getInfoTypeForString("PROMOTION_COMBAT2"),
        gc.getInfoTypeForString("PROMOTION_COMBAT3"),
        gc.getInfoTypeForString("PROMOTION_COMBAT4"),
        gc.getInfoTypeForString("PROMOTION_COMBAT5"),
    ]
    # zwischen 0 und einschließlich iMaxRang
    iRang = myRandom(iMaxRang+1)
    iRang = max(iMinRang, iRang)
    iRang = min(4, iRang)

    for iI in range(iRang):
        #CyInterface().addMessage(pUnit.getOwner(), True, 10, str(lRang[iI]), None, 2, gc.getUnitInfo(eUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
        pUnit.setHasPromotion(lRang[iI], True)
        pUnit.setLevel(iRang+1)

def doHireMercenary(iPlayer, eUnit, iMultiplier, bCivicSoeldner, pCity, iTimer, iExtraMultiplier = 1):
    iMinRanking = 1
    iMaxRanking = 3
    iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")

    pPlayer = gc.getPlayer(iPlayer)
    iCost = getCost(eUnit, iMultiplier, bCivicSoeldner, iExtraMultiplier)
    if pPlayer.getGold() < iCost:
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        return False
    else:
        if iPlayer == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound("AS2D_COINS")
        pPlayer.changeGold(-iCost)
        gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_HIRED",(pCity.getName(), gc.getUnitInfo(eUnit).getDescriptionForm(0))), None, 2, gc.getUnitInfo(eUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
        pNewUnit = pPlayer.initUnit(eUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        #CyInterface().addMessage(iPlayer, True, 10, str(iPromo), None, 2, gc.getUnitInfo(eUnit).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
        pNewUnit.setHasPromotion(iPromo, True)
        pNewUnit.setImmobileTimer(iTimer)
        # Unit Rang / Unit ranking
        doMercenaryRanking(pNewUnit,iMinRanking,iMaxRanking)

        # PAEInstanceHiringModifier per turn
        return True


def canTrain(eUnit, pPlayer):
    if not gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getUnitInfo(eUnit).getPrereqAndTech()):
        return False
    for iI in range(gc.getNUM_UNIT_AND_TECH_PREREQS()):
        if gc.getUnitInfo(eUnit).getPrereqAndTechs(iI) != TechTypes.NO_TECH:
            if not gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getUnitInfo(eUnit).getPrereqAndTechs(iI)):
                return False


    if gc.getUnitInfo(eUnit).getPrereqAndBonus() != BonusTypes.NO_BONUS:
        if not pPlayer.hasBonus(gc.getUnitInfo(eUnit).getPrereqAndBonus()):
            return False

    bRequiresBonus = False
    bNeedsBonus = True

    for iI in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
        if gc.getUnitInfo(eUnit).getPrereqOrBonuses(iI) != BonusTypes.NO_BONUS:
            bRequiresBonus = True
            if pPlayer.hasBonus(gc.getUnitInfo(eUnit).getPrereqOrBonuses(iI)):
                bNeedsBonus = False
                break

    if bRequiresBonus and bNeedsBonus:
        return False

    return True


# Failed Mercenary Torture (from 716 and 717)
def doFailedMercenaryTortureMessage(iPlayer):
    iRand = myRandom(8) + 1
    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_FAILED_0",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARY_TORTURE_FAILED_" + str(iRand),("", )))
    popupInfo.addPopup(iPlayer)

# AI Torture Mercenary Commission (cheaper for AI)
def doAIMercTorture(iPlayer, iMercenaryCiv):
  pPlayer = gc.getPlayer(iPlayer)
  iGold = pPlayer.getGold()

  if iGold >= 550:
    if 1 == myRandom(2):
      pPlayer.changeGold(-50)
      pPlayer.AI_changeAttitudeExtra(iMercenaryCiv,-2)
      doAIPlanAssignMercenaries(iMercenaryCiv)
      # nochmal, wenn AI in Geld schwimmt
      if pPlayer.getGold() >= 500: doAIPlanAssignMercenaries(iMercenaryCiv)
  elif iGold >= 350:
    if 1 == myRandom(2):
      pPlayer.changeGold(-50)
      pPlayer.AI_changeAttitudeExtra(iMercenaryCiv,-2)
      doAIPlanAssignMercenaries(iMercenaryCiv)

# AI Mercenary Commissions
def doAIPlanAssignMercenaries(iPlayer):
  pPlayer = gc.getPlayer(iPlayer)
  iFaktor = 0
  iCost = 0
  iSize = 0

  # Check neighbours
  # ATTITUDE_FRIENDLY
  # ATTITUDE_PLEASED
  # ATTITUDE_CAUTIOUS
  # ATTITUDE_ANNOYED
  # ATTITUDE_FURIOUS
  lNeighbors = []
  iRangeMaxPlayers = gc.getMAX_PLAYERS()
  for iLoopPlayer in range (iRangeMaxPlayers):
    pLoopPlayer = gc.getPlayer(iLoopPlayer)
    if iLoopPlayer != gc.getBARBARIAN_PLAYER() and iLoopPlayer != iPlayer:
      if pLoopPlayer.isAlive():
        if gc.getTeam(pLoopPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
          eAtt = pPlayer.AI_getAttitude(iLoopPlayer)
          if eAtt == AttitudeTypes.ATTITUDE_ANNOYED or eAtt == AttitudeTypes.ATTITUDE_FURIOUS:
            # Check: Coastal cities for naval mercenary units
            iAttackAtSea = 0
            iCoastalCities = 0
            iLandCities = 0
            iNumCities = pLoopPlayer.getNumCities()
            for i in range (iNumCities):
              if pLoopPlayer.getCity(i).isCoastal(6): iCoastalCities += 1
              else: iLandCities += 1

            if iCoastalCities > 0:
              if iCoastalCities >= iLandCities:
                if 1 == myRandom(2): iAttackAtSea = 1
              else:
                iChance = iNumCities - iCoastalCities
                if 0 == myRandom(iChance): iAttackAtSea = 1

            lNeighbors.append((iLoopPlayer,iAttackAtSea))

  # iFaktor: 1111 - 4434
  # ---- inter/national
  # urban 200+    iFaktor: +1
  # own 300+      iFaktor: +2
  #internat 400+  iFaktor: +3
  #elite 500+     iFaktor: +4

  # ---- size
  #small +0      iFaktor: +10
  #medium +150   iFaktor: +20
  #big +300      iFaktor: +30
  #huge +400     iFaktor: +40

  # ---- type
  #defense      iFaktor: +100
  #ranged       iFaktor: +200
  #offense      iFaktor: +300
  #city         iFaktor: +400
  #naval        iFaktor: +500

  # ---- siege
  #0           iFaktor: +1000
  #2 +50       iFaktor: +2000
  #4 +90       iFaktor: +3000
  #6 +120      iFaktor: +4000

  if len(lNeighbors) > 0:
    iRand = myRandom(len(lNeighbors))
    iTargetPlayer = lNeighbors[iRand][0]
    iTargetAtSea = lNeighbors[iRand][1]
    iGold = pPlayer.getGold()

    # inter/national
    if pPlayer.getTechScore() > gc.getPlayer(iTargetPlayer).getTechScore():
      if iGold > 1000:
        if 1 == myRandom(3):
          iFaktor += 3
          iCost += 400
        else:
          iFaktor += 2
          iCost += 300
      elif iGold > 500:
        iFaktor += 2
        iCost += 300
      else:
        iFaktor += 1
        iCost += 200
    else:
      if iGold > 1000:
        if 1 == myRandom(3):
          iFaktor += 3
          iCost += 400
        else:
          iFaktor += 1
          iCost += 200
      else:
        iFaktor += 1
        iCost += 200

    # size
    if pPlayer.getPower() > gc.getPlayer(iTargetPlayer).getPower():
      if iGold > iCost + 150:
        if 1 == myRandom(3):
          iFaktor += 10
          iSize = 1
        else:
          iFaktor += 20
          iCost += 150
          iSize = 2
      else:
        iFaktor += 10
        iSize = 1
    else:
      if iGold > iCost + 150:
        if 1 != myRandom(3):
          iFaktor += 10
          iSize = 1
        else:
          iFaktor += 20
          iCost += 150
          iSize = 2
      else:
        iFaktor += 10
        iSize = 1

    # type
    if iTargetAtSea == 1: iType = 5
    else: iType = 1 + myRandom(4)
    iFaktor += iType * 100

    # siege units
    if iType == 4:
      if iSize == 1: iFaktor += 1000
      else:
        if pPlayer.getPower() > gc.getPlayer(iTargetPlayer).getPower():
          if iGold > iCost + 50: iFaktor += 2000
          else: iFaktor += 1000
        else:
          if iGold > iCost + 90: iFaktor += 3000
          elif iGold > iCost + 50: iFaktor += 2000
          else: iFaktor += 1000
    else: iFaktor += 1000

    if iTargetPlayer != -1:
      doCommissionMercenaries(iTargetPlayer, iFaktor, iPlayer)


# Commission Mercenaries
def doCommissionMercenaries(iTargetPlayer, iFaktor, iPlayer):
    #  iTargetPlayer, iFaktor, iPlayer
    # iFaktor: 1111 - 4534
    # Naval attack: sFaktor[1] = 5
    pPlayer = gc.getPlayer(iPlayer)
    pPlayerCiv = gc.getCivilizationInfo(pPlayer.getCivilizationType())
    sFaktor = str(iFaktor)
    iCost = 0
    iSize = 0

    # siege units
    iSiegeUnitAnz = 0
    if sFaktor[0]   == "2": iCost +=  50
    elif sFaktor[0] == "3": iCost +=  90
    elif sFaktor[0] == "4": iCost += 120

    # size
    if sFaktor[2]   == "2": iCost += 150
    elif sFaktor[2] == "3": iCost += 300
    elif sFaktor[2] == "4": iCost += 400

    # inter/national/elite units
    if sFaktor[3]   == "1": iCost += 200
    elif sFaktor[3] == "2": iCost += 300
    elif sFaktor[3] == "3": iCost += 400
    elif sFaktor[3] == "4": iCost += 500
    # ----------

    if pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM")):
      iCost -= iCost/4

    if pPlayer.getGold() < iCost:
      if gc.getPlayer(iPlayer).isHuman():
        CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("",)), None, 2, None, ColorTypes(7), 0, 0, False, False)
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_NOT_ENOUGH_MONEY",("", )))
        popupInfo.addPopup(iPlayer)
    else:
      pPlayer.changeGold(-iCost)
      gc.getPlayer(gc.getBARBARIAN_PLAYER()).changeGold(iCost)

      # Siege Units
      iAnzSiege = 0
      iUnitSiege = -1
      if sFaktor[0] == "2":   iAnzSiege = 2
      elif sFaktor[0] == "3": iAnzSiege = 4
      elif sFaktor[0] == "4": iAnzSiege = 6

      if iAnzSiege > 0:
        if gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_MECHANIK")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_BATTERING_RAM2")
        elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_WEHRTECHNIK")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_BATTERING_RAM")
        elif gc.getGame().countKnownTechNumTeams(gc.getInfoTypeForString("TECH_BELAGERUNG")) > 0: iUnitSiege = gc.getInfoTypeForString("UNIT_RAM")
      # --------

      #  Techs for inter/national units
      lNeighbors = []
      # on-site
      if sFaktor[3] == "1": lNeighbors.append(gc.getPlayer(iTargetPlayer))
      # national (own)
      elif sFaktor[3] == "2": lNeighbors.append(pPlayer)
      # international or elite
      elif sFaktor[3] == "3" or sFaktor[3] == "4":
        iRange = gc.getMAX_PLAYERS()
        for iLoopPlayer in range (iRange):
          pLoopPlayer = gc.getPlayer(iLoopPlayer)
          # Nachbarn inkludieren
          if pLoopPlayer.isAlive():
            if gc.getTeam(pLoopPlayer.getTeam()).isHasMet(pPlayer.getTeam()):
              lNeighbors.append(pLoopPlayer)
      # ------------------

      # Unit initials
      # size and types
      iAnzSpear = 0
      iAnzAxe = 0
      iAnzSword = 0
      iAnzArcher = 0
      iAnzSlinger = 0
      iAnzShip1 = 0
      iAnzShip2 = 0
      if sFaktor[2] == "1":
        if sFaktor[1] == "1":
          iAnzSpear = 2
          iAnzAxe = 1
          iAnzSword = 0
          iAnzArcher = 1
          iAnzSlinger = 0
        elif sFaktor[1] == "2":
          iAnzSpear = 1
          iAnzAxe = 1
          iAnzSword = 0
          iAnzArcher = 2
          iAnzSlinger = 0
        elif sFaktor[1] == "3":
          iAnzSpear = 1
          iAnzAxe = 2
          iAnzSword = 0
          iAnzArcher = 1
          iAnzSlinger = 0
        elif sFaktor[1] == "4":
          iAnzSpear = 0
          iAnzAxe = 0
          iAnzSword = 2
          iAnzArcher = 2
          iAnzSlinger = 0
        elif sFaktor[1] == "5":
          iAnzShip1 = 1 # weak
          iAnzShip2 = 1 # strong

      elif sFaktor[2] == "2":
        if sFaktor[1] == "1":
          iAnzSpear = 3
          iAnzAxe = 2
          iAnzSword = 0
          iAnzArcher = 3
          iAnzSlinger = 0
        elif sFaktor[1] == "2":
          iAnzSpear = 1
          iAnzAxe = 2
          iAnzSword = 0
          iAnzArcher = 4
          iAnzSlinger = 1
        elif sFaktor[1] == "3":
          iAnzSpear = 2
          iAnzAxe = 4
          iAnzSword = 0
          iAnzArcher = 2
          iAnzSlinger = 0
        elif sFaktor[1] == "4":
          iAnzSpear = 1
          iAnzAxe = 1
          iAnzSword = 2
          iAnzArcher = 3
          iAnzSlinger = 1
        elif sFaktor[1] == "5":
          iAnzShip1 = 2
          iAnzShip2 = 2

      elif sFaktor[2] == "3":
        if sFaktor[1] == "1":
          iAnzSpear = 4
          iAnzAxe = 3
          iAnzSword = 0
          iAnzArcher = 4
          iAnzSlinger = 1
        elif sFaktor[1] == "2":
          iAnzSpear = 2
          iAnzAxe = 2
          iAnzSword = 0
          iAnzArcher = 5
          iAnzSlinger = 3
        elif sFaktor[1] == "3":
          iAnzSpear = 2
          iAnzAxe = 5
          iAnzSword = 0
          iAnzArcher = 2
          iAnzSlinger = 3
        elif sFaktor[1] == "4":
          iAnzSpear = 2
          iAnzAxe = 1
          iAnzSword = 4
          iAnzArcher = 3
          iAnzSlinger = 2
        elif sFaktor[1] == "5":
          iAnzShip1 = 3
          iAnzShip2 = 2

      elif sFaktor[2] == "4":
        if sFaktor[1] == "1":
          iAnzSpear = 5
          iAnzAxe = 5
          iAnzSword = 0
          iAnzArcher = 5
          iAnzSlinger = 1
        elif sFaktor[1] == "2":
          iAnzSpear = 3
          iAnzAxe = 3
          iAnzSword = 0
          iAnzArcher = 7
          iAnzSlinger = 3
        elif sFaktor[1] == "3":
          iAnzSpear = 3
          iAnzAxe = 7
          iAnzSword = 0
          iAnzArcher = 4
          iAnzSlinger = 2
        elif sFaktor[1] == "4":
          iAnzSpear = 2
          iAnzAxe = 2
          iAnzSword = 6
          iAnzArcher = 4
          iAnzSlinger = 2
        elif sFaktor[1] == "5":
          iAnzShip1 = 3
          iAnzShip2 = 3

      if pPlayer.getCurrentEra() > 2:
        iAnzSword += iAnzAxe
        iAnzAxe = 0
      # ----------

      # Set units

      # Elite
      lEliteUnits = []

      # UNIT_LIGHT_SPEARMAN: TECH_SPEERSPITZEN
      # UNIT_AXEWARRIOR: TECH_BEWAFFNUNG
      # UNIT_AXEMAN: TECH_BEWAFFNUNG2 + Bronze or Iron
      # UNITCLASS_KURZSCHWERT: TECH_BEWAFFNUNG3 + Bronze or Iron
      # UNIT_SPEARMAN: TECH_ARMOR + Bronze or Iron
      # UNIT_SCHILDTRAEGER: TECH_BEWAFFNUNG4 + Bronze or Iron
      # UNIT_SWORDSMAN: TECH_BEWAFFNUNG5 + Iron

      iUnitSpear   =  gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN")
      iUnitAxe     =  gc.getInfoTypeForString("UNIT_AXEWARRIOR")
      iUnitArcher  = gc.getInfoTypeForString("UNIT_ARCHER")
      iUnitSlinger = gc.getInfoTypeForString("UNIT_PELTIST")
      iUnitSword   = -1
      bLongsword = False

      iBonus1 = gc.getInfoTypeForString("BONUS_BRONZE")
      iBonus2 = gc.getInfoTypeForString("BONUS_IRON")
      for pNeighbor in lNeighbors:
        pNeighborTeam = gc.getTeam(pNeighbor.getTeam())

        # elite units
        if sFaktor[3] == "4":
          NeighborCapital = pNeighbor.getCapitalCity()
          kNeighborCiv = gc.getCivilizationInfo(pNeighbor.getCivilizationType())

          # Naval units
          if sFaktor[1] == "5":
            lNeighborUnits = [
                gc.getInfoTypeForString("UNIT_CARVEL_WAR"),
                gc.getInfoTypeForString("UNIT_QUINQUEREME"),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KONTERE")), # Gaulos
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL2")), # Quadrireme
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE1")) # Decareme
            ]

          # Land units
          else:
            lNeighborUnits = [
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL1")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL2")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL3")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL4")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SPECIAL5")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE1")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE2")),
                kNeighborCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE3")),
                gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"),
                gc.getInfoTypeForString("UNIT_SWORDSMAN")
            ]

          for iUnitElite in lNeighborUnits:
            if iUnitElite != None and iUnitElite != -1:
              # Naval units
              if sFaktor[1] == "5" and gc.getUnitInfo(iUnitElite).getDomainType() == DomainTypes.DOMAIN_SEA:
                if NeighborCapital.canTrain(iUnitElite,0,0):
                  lEliteUnits.append(iUnitElite)
              # Land units
              elif gc.getUnitInfo(iUnitElite).getDomainType() != DomainTypes.DOMAIN_SEA:
                if NeighborCapital.canTrain(iUnitElite,0,0):
                  lEliteUnits.append(iUnitElite)

        # normal units
        # else: Falls es keine Elite gibt, sollen normale Einheiten einspringen

        # Naval units
        if sFaktor[1] == "5":
          # UNIT_KONTERE: TECH_COLONIZATION2
          # UNIT_BIREME:  TECH_RUDERER2
          # UNIT_TRIREME: TECH_RUDERER3
          # UNIT_LIBURNE: TECH_WARSHIPS2
          # iAnzShip1 = weak
          # iAnzShip2 = strong
          iShip1 = -1
          iShip2 = -1
          if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_WARSHIPS2")):
            iShip1 = gc.getInfoTypeForString("UNIT_TRIREME")
            iShip2 = gc.getInfoTypeForString("UNIT_LIBURNE")
          elif pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_RUDERER3")):
            iShip1 = gc.getInfoTypeForString("UNIT_BIREME")
            iShip2 = gc.getInfoTypeForString("UNIT_TRIREME")
          elif pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_RUDERER2")):
            iShip1 = gc.getInfoTypeForString("UNIT_KONTERE")
            iShip2 = gc.getInfoTypeForString("UNIT_BIREME")
          elif pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_COLONIZATION2")):
            iShip1 = gc.getInfoTypeForString("UNIT_KONTERE")
            iShip2 = gc.getInfoTypeForString("UNIT_KONTERE")

        # Land units
        # PAE V Patch 3: nun auch fuer Besatzung der Schiffe
        #else:
        #if gc.getTeam(pNeighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARCHERY3")): iUnitArcher = gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER")
        if pNeighbor.hasBonus(iBonus1) or pNeighbor.hasBonus(iBonus2):
          if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_ARMOR")): iUnitSpear = gc.getInfoTypeForString("UNIT_SPEARMAN")
          if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_BUERGERSOLDATEN")): iUnitAxe = gc.getInfoTypeForString("UNIT_AXEMAN2")
          elif pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG2")): iUnitAxe = gc.getInfoTypeForString("UNIT_AXEMAN")
          if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")): iUnitSword = gc.getInfoTypeForString("UNIT_SCHILDTRAEGER")
          if iUnitSword == -1:
            if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG3")): iUnitSword = pPlayerCiv.getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT"))
        if not bLongsword:
          if pNeighbor.hasBonus(iBonus2):
            if pNeighborTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG5")): bLongsword = True

      # for neighbors

      # wenns schon langschwert gibt
      if bLongsword: iUnitSword = gc.getInfoTypeForString("UNIT_SWORDSMAN")

      # wenns noch keine Schwerter gibt
      if iUnitSword == -1:
        iAnzAxe += iAnzSword
        iAnzSword = 0

      # Choose plots
      # Initialise CIV cultural plots
      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

      CivPlots = []
      iRange = CyMap().numPlots()
      for iI in range(iRange):
        pPlot = CyMap().plotByIndex(iI)
        iX = pPlot.getX()
        iY = pPlot.getY()
        if pPlot.getFeatureType() == iDarkIce: continue
        if pPlot.getOwner() == iTargetPlayer:
          if not pPlot.isPeak() and not pPlot.isCity() and pPlot.getNumUnits() == 0:
            # Naval units
            if sFaktor[1] == "5":
              # Nicht auf Seen
              if pPlot.isWater() and not pPlot.isLake():
                CivPlots.append(pPlot)
            # Land units
            elif not pPlot.isWater():
              # Nicht auf Inseln
              iLandPlots = 0
              for x2 in range(3):
                for y2 in range(3):
                  loopPlot2 = gc.getMap().plot(iX-1+x2,iY-1+y2)
                  if loopPlot2 != None and not loopPlot2.isNone():
                    if not loopPlot2.isWater(): iLandPlots += 1

                  # earlier break
                  if x2 == 1 and y2 > 0 and iLandPlots <= 1:
                    break

                # earlier breaks
                if iLandPlots >= 5:
                  CivPlots.append(pPlot)
                  break
                elif x2 == 2 and iLandPlots <= 2:
                  break

      # Big stacks and elite only on border plots
      if sFaktor[2] == "4" or sFaktor[3] == "4":
        if len(CivPlots) > 0:
          NewCivPlots = []
          x2=0
          y2=0
          for loopPlot in CivPlots:
            iLX = loopPlot.getX()
            iLY = loopPlot.getY()
            bDone = False
            for x2 in [-1,0,1]:
              if bDone: break
              for y2 in [-1,0,1]:
                loopPlot2 = plotXY(iLX,iLY,x2,y2)
                if loopPlot2 == None or loopPlot2.isNone() or loopPlot2.getOwner() != loopPlot.getOwner():
                  NewCivPlots.append(loopPlot)
                  bDone = True
                  break

          if len(NewCivPlots) > 0:
            CivPlots = NewCivPlots

      # set units
      if len(CivPlots) > 0:
        iPlot = myRandom(len(CivPlots))
        iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
        # Loyality disabled for elite units
        iPromo2 = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
        iMinRanking = 0
        iMaxRanking = 4 # 4 = Veteran

        # instead of UnitAITypes.NO_UNITAI
        if sFaktor[1] == "4": UnitAI_Type = UnitAITypes.UNITAI_ATTACK_CITY
        else: UnitAI_Type = UnitAITypes.UNITAI_ATTACK

        # prevents CtD in MP
        #UnitAI_Type = UnitAITypes.NO_UNITAI

        ScriptUnit = []
        # set units
        # elite
        if sFaktor[3] == "4" and len(lEliteUnits) > 0:

          # Naval units
          if sFaktor[1] == "5":
            if sFaktor[2] == "1": iAnz = 2
            elif sFaktor[2] == "2": iAnz = 3
            elif sFaktor[2] == "3": iAnz = 4
            else: iAnz = 5
          # Land units
          else:
            if sFaktor[2] == "1": iAnz = 4
            elif sFaktor[2] == "2": iAnz = 8
            elif sFaktor[2] == "3": iAnz = 10
            else: iAnz = 12

          for i in range(iAnz):
            iRand = myRandom (len(lEliteUnits))
            NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lEliteUnits[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
            if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
            if NewUnit.isHasPromotion(iPromo2): NewUnit.setHasPromotion(iPromo2, False)
            # Unit Rang / Unit ranking
            doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
            NewUnit.setImmobileTimer(1)
            ScriptUnit.append(NewUnit)
          # Goldkarren
          gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
          gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

        # standard units
        else:
          if iAnzSpear > 0:
            for i in range(iAnzSpear):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSpear, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)
              ScriptUnit.append(NewUnit)
          if iAnzAxe > 0:
            for i in range(iAnzAxe):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitAxe, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)
              ScriptUnit.append(NewUnit)
          if iAnzSword > 0 and iUnitSword != -1:
            for i in range(iAnzSword):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSword, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)
              ScriptUnit.append(NewUnit)
          if iAnzArcher > 0:
            for i in range(iAnzArcher):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitArcher, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)
          if iAnzSlinger > 0:
            for i in range(iAnzSlinger):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSlinger, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)
          if iAnzSiege > 0 and iUnitSiege != -1:
            for i in range(iAnzSiege):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iUnitSiege, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_CITY, DirectionTypes.DIRECTION_SOUTH)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)

          # Vessels / Naval units : get land unit
          if iAnzShip1 > 0 or iAnzShip2 > 0:
            lUnit = []
            lUnit.append(iUnitSpear)
            lUnit.append(iUnitAxe)
            if iUnitSword != -1: lUnit.append(iUnitSword)

          if iAnzShip1 > 0 and iShip1 != -1:
            for i in range(iAnzShip1):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iShip1, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)

              # Cargo
              iRand = myRandom(len(lUnit))
              NewLandUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lUnit[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              NewLandUnit.setTransportUnit(NewUnit)

          if iAnzShip2 > 0 and iShip2 != -1:
            for i in range(iAnzShip2):
              NewUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(iShip2, CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)
              if not NewUnit.isHasPromotion(iPromo): NewUnit.setHasPromotion(iPromo, True)
              # Unit Rang / Unit ranking
              doMercenaryRanking(NewUnit,iMinRanking,iMaxRanking)
              NewUnit.setImmobileTimer(1)

              # Cargo
              iRand = myRandom(len(lUnit))
              NewLandUnit = gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(lUnit[iRand], CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAI_Type, DirectionTypes.DIRECTION_SOUTH)
              NewLandUnit.setTransportUnit(NewUnit)

          # Goldkarren bei Landeinheiten
          if not CivPlots[iPlot].isWater():
            gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(gc.getInfoTypeForString("UNIT_GOLDKARREN"), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)


        # Plot anzeigen
        CivPlots[iPlot].setRevealed (gc.getPlayer(iPlayer).getTeam(),1,0,-1)

        # Eine Einheit bekommt iPlayer als Auftraggeber
        if len(ScriptUnit) > 0:
          iRand = myRandom(len(ScriptUnit))
          CvUtil.addScriptData(ScriptUnit[iRand], "U", "MercFromCIV=" + str(iPlayer))

        # Meldungen
        if gc.getPlayer(iPlayer).isHuman():
          CyCamera().JustLookAtPlot(CivPlots[iPlot])
          if CivPlots[iPlot].isWater(): szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_3",(gc.getPlayer(iTargetPlayer).getCivilizationDescription(0),))
          else: szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_1",(gc.getPlayer(iTargetPlayer).getCivilizationDescription(0),))
          CyInterface().addMessage(iPlayer, True, 10, szText, None, 2, None, ColorTypes(8), 0, 0, False, False)
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(szText)
          popupInfo.addPopup(iPlayer)
        if gc.getPlayer(iTargetPlayer).isHuman():
          CyCamera().JustLookAtPlot(CivPlots[iPlot])
          if CivPlots[iPlot].isWater(): szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_4",("",))
          else: szText = CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_DONE_2",("",))
          CyInterface().addMessage(iTargetPlayer, True, 15, szText, "AS2D_THEIRDECLAREWAR", 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), CivPlots[iPlot].getX(), CivPlots[iPlot].getY(), True, True)
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(szText)
          popupInfo.addPopup(iTargetPlayer)

        # TEST
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Plots",len(CivPlots))), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Plots",int(sFaktor[1]))), None, 2, None, ColorTypes(10), 0, 0, False, False)

# 2) Mercenaries
# PAE Better AI: AI has no cost malus when hiring units
def AI_doHireMercenaries(iPlayer, pCity, iMaintainUnits, iCityUnits, iEnemyUnits):
    pPlayer = gc.getPlayer(iPlayer)
    # Units amount 1:3
    iMultiplikator = 3
    if iMaintainUnits > 0 and iCityUnits * iMultiplikator <= iEnemyUnits and pPlayer.getGold() > 100:
        if pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_SOELDNERPOSTEN")):
            # Check neighbours
            lNeighbors = []
            iRange = gc.getMAX_PLAYERS()
            for iLoopPlayer in range (iRange):
                if pCity.isConnectedToCapital(iLoopPlayer):
                    lNeighbors.append(gc.getPlayer(iLoopPlayer))
            if len(lNeighbors) > 0:
                lUnits = doHireMercenariesINIT(pPlayer, lNeighbors)

                # KI zahlt die Haelfte und kein HiringModifierPerTurn
                iExtraMultiplier = 0.5
                bCivicSoeldner = pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM"))

                lArchers = lUnits[0]
                lList = []
                iMinCost = -1
                for eUnit in lArchers:
                    iCost = getCost(eUnit, 0, bCivicSoeldner, iExtraMultiplier)
                    if iCost < iMinCost or iMinCost == -1:
                        iMinCost = iCost
                    lList.append([eUnit, iCost])
                lArchers = lList

                lOtherUnits = lUnits[1]+lUnits[2]+lUnits[3]
                lList = []
                for eUnit in lOtherUnits:
                    iCost = getCost(eUnit, 0, bCivicSoeldner, iExtraMultiplier)
                    if iCost < iMinCost or iMinCost == -1:
                        iMinCost = iCost
                    lList.append([eUnit, iCost])
                lOtherUnits = lList

                # choose units
                iPromo = gc.getInfoTypeForString("PROMOTION_MERCENARY")
                # AI hires max 2 - 4 units per city and turn
                iHiredUnits = 0
                iHiredUnitsMax = 2 + myRandom(3)
                while iMaintainUnits > 0 and pPlayer.getGold() > 50 and pPlayer.getGold() > iMinCost and iHiredUnits < iHiredUnitsMax and iCityUnits * iMultiplikator < iEnemyUnits:
                    eUnit = -1
                    iGold = pPlayer.getGold()

                    iTry = 0
                    while iTry < 3:
                        if myRandom(10) < 7:
                            eUnit, iCost = lArchers[myRandom(len(lArchers))]
                        else:
                            eUnit, iCost = lOtherUnits[myRandom(len(lOtherUnits))]
                        if iCost <= 0: iCost = 50
                        if iCost <= iGold:
                            if doHireMercenary(iPlayer, eUnit, 0, bCivicSoeldner, pCity, 1, iExtraMultiplier):
                                iMaintainUnits -= 1
                                iCityUnits += 1
                                iHiredUnits += 1
                            break
                        else:
                            iTry += 1



def doHireMercenariesPopup(iCity, iTypeButton, iUnitButton, iPlayer):

    pPlayer = gc.getPlayer(iPlayer)
    pCity = pPlayer.getCity(iCity)

    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE2",("", )) )
    popupInfo.setData1(iCity)
    popupInfo.setData3(iPlayer)

    # Check neighbours
    lNeighbors = []
    iRange = gc.getMAX_PLAYERS()
    for iLoopPlayer in range (iRange):
      if pCity.isConnectedToCapital(iLoopPlayer):
        lNeighbors.append(gc.getPlayer(iLoopPlayer))

    # inits
    lUnits = doHireMercenariesINIT(pPlayer, lNeighbors)

    lImmobile = [
      3,4,2,3,3
    ]

    lUCI = [
      gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ARCHER")),
      gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MELEE")),
      gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_MOUNTED")),
      gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT")),
      gc.getUnitCombatInfo(gc.getInfoTypeForString("UNITCOMBAT_NAVAL"))
    ]

    if iTypeButton == -1:
      if len(lNeighbors) == 0:
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
        popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_MERCENARIES_HIRE3",("", )))
        popupInfo.addPopup(iPlayer)
      else:
        popupInfo.setOnClickedPythonCallback("popupMercenariesHire")
        for i in range(len(lUCI)):
          if len(lUnits[i]) > 0:
            popupInfo.addPythonButton(lUCI[i].getDescription(), lUCI[i].getButton())

        #popupInfo.setData2(-1)
    else:
      popupInfo.setOnClickedPythonCallback("popupMercenariesHireUnits")
      popupInfo.setData2(iTypeButton)

      # PAEInstanceHiringModifier per turn
      iMultiplier = PAEInstanceHiringModifier.setdefault(iPlayer, 0)

      # Elephants
      if iTypeButton == 3: iExtraMultiplier = 2
      else: iExtraMultiplier = 1

      bCivicSoeldner = pPlayer.isCivic(gc.getInfoTypeForString("CIVIC_SOELDNERTUM"))

      lTypeUnits = lUnits[iTypeButton]
      # Hire Units
      if iUnitButton != -1:
          if doHireMercenary(iPlayer, lTypeUnits[iUnitButton], iMultiplier, bCivicSoeldner, pCity, lImmobile[iTypeButton], iExtraMultiplier):
            iMultiplier += 1
            PAEInstanceHiringModifier[iPlayer] = iMultiplier

      # redraw the list with new prices
      for eUnit in lTypeUnits:
          iCost = getCost(eUnit, iMultiplier, bCivicSoeldner, iExtraMultiplier)
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MESSAGE_MERCENARIES_UNIT_COST",(gc.getUnitInfo(eUnit).getDescriptionForm(0), iCost )), gc.getUnitInfo(eUnit).getButton())

      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MAIN_MENU_GO_BACK",("", )), ",Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5")

    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_ACTION_CANCEL",("", )), "Art/Interface/Buttons/Actions/Cancel.dds")
    popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
    popupInfo.addPopup(iPlayer)

def doHireMercenariesINIT(pPlayer, lNeighbors):
    lArchers = [
      gc.getInfoTypeForString("UNIT_PELTIST"),
      gc.getInfoTypeForString("UNIT_ARCHER"),
      gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"),
      gc.getInfoTypeForString("UNIT_SKIRMISHER"),
    ]
    lEarlyInfantry = [
      gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
      gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
      gc.getInfoTypeForString("UNIT_AXEMAN"),
      gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_KURZSCHWERT")),
      gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),
      gc.getInfoTypeForString("UNIT_SPEARMAN"),
    ]
    lInfantry = [
      gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"),
      gc.getInfoTypeForString("UNIT_SPEARMAN"),
      gc.getInfoTypeForString("UNIT_AXEMAN2"),
      gc.getInfoTypeForString("UNIT_SWORDSMAN"),
      gc.getInfoTypeForString("UNIT_WURFAXT"),
    ]
    lEarlyMounted = [
      gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT"),
      gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"),
      gc.getInfoTypeForString("UNIT_CHARIOT"),
    ]
    lMounted = [
      gc.getInfoTypeForString("UNIT_CHARIOT"),
      gc.getInfoTypeForString("UNIT_HORSEMAN"),
      gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
      gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),
    ]
    lElephants = [
      gc.getInfoTypeForString("UNIT_WAR_ELEPHANT")
    ]

    lShips = [
      gc.getInfoTypeForString("UNIT_KONTERE"),
      gc.getInfoTypeForString("UNIT_BIREME"),
      gc.getInfoTypeForString("UNIT_TRIREME"),
      gc.getInfoTypeForString("UNIT_QUADRIREME"),
      gc.getInfoTypeForString("UNIT_LIBURNE"),
    ]

    if pPlayer.getCurrentEra() <= 2:
      lInfantry = lEarlyInfantry
      lMounted = lEarlyMounted

    # Archers: Peltist (Steinschleuderer?) geht immer
    lTemp = lArchers[:1]+getAvailableUnits(lNeighbors, lArchers[1:])
    ## ab Plaenkler duerfen alle Kompositbogis
    if not lArchers[3] in lTemp:
      for pNeighbor in lNeighbors:
        if gc.getTeam(pNeighbor.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_SKIRMISH_TACTICS")):
          lTemp.append(lArchers[3])
          break
    lArchers = lTemp
    # Melee: Speer und Axt bzw. Schildtraeger und Speerkaempfer gehen immer
    lInfantry = lInfantry[:2]+getAvailableUnits(lNeighbors, lInfantry[2:])
    lMounted = getAvailableUnits(lNeighbors, lMounted)
    lElephants = getAvailableUnits(lNeighbors, lElephants)
    lShips = getAvailableUnits(lNeighbors, lShips)

    lUnits = [
      lArchers, lInfantry, lMounted, lElephants, lShips
    ]

    return lUnits
