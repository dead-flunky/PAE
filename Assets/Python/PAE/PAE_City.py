### Imports
from CvPythonExtensions import *
import random

import PAE_Sklaven
import PAE_Unit
import PAE_Mercenaries
import CvUtil

### Defines
gc = CyGlobalContext()

# PAE Stadtstatus
iPopDorf = 3
iPopStadt = 6
iPopProvinz = 12
iPopMetropole = 20



def myRandom (num):
      if num <= 1: return 0
      else: return random.randint(0, num-1)


def doMessageCityGrowing(pCity):
    if pCity.isNone(): return

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
      CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_WILL_GROW",(pCity.getName(),iPop)), None, 2, None, ColorTypes(13), 0, 0, False, False)

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
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        else:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHAPPY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

      # MESSAGE: city gets/is unhealthy / Stadt wird/ist ungesund
      if pCity.goodHealth() - pCity.badHealth(False) + iBonusHealth <= 0:
        if pCity.goodHealth() - pCity.badHealth(False) == 0:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GETS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
        else:
          CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_IS_UNHEALTY",(pCity.getName(),)), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # -----------------


# PAE City status --------------------------
# Check City colony or province after events
# once getting a province: keep being a province
# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckCityState(pCity):
    global iPopDorf
    global iPopStadt
    global iPopProvinz
    global iPopMetropole

    if pCity.isNone(): return

    iBuildingSiedlung = gc.getInfoTypeForString("BUILDING_SIEDLUNG")
    iBuildingKolonie = gc.getInfoTypeForString("BUILDING_KOLONIE")
    iBuildingCity = gc.getInfoTypeForString("BUILDING_STADT")
    iBuildingProvinz = gc.getInfoTypeForString("BUILDING_PROVINZ")
    iBuildingMetropole = gc.getInfoTypeForString("BUILDING_METROPOLE")

    if pCity.getNumRealBuilding(iBuildingSiedlung) == 0:
      pCity.setNumRealBuilding(iBuildingSiedlung,1)

    if pCity.getPopulation() >= iPopDorf and pCity.getNumRealBuilding(iBuildingKolonie) == 0:
      pCity.setNumRealBuilding(iBuildingKolonie,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_1",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingKolonie).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    if pCity.getPopulation() >= iPopStadt and pCity.getNumRealBuilding(iBuildingCity) == 0:
      pCity.setNumRealBuilding(iBuildingCity,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_2",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Wachstum: Meldungen von kleinerem Status beginnend
    if pCity.getPopulation() >= iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 0:
      pCity.setNumRealBuilding(iBuildingProvinz,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_3",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() >= iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 0:
      pCity.setNumRealBuilding(iBuildingMetropole,1)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_5",(pCity.getName(),0)), "AS2D_WELOVEKING", 2, gc.getBuildingInfo(iBuildingMetropole).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # Falls extremer Bev.rueckgang: Meldungen von hoeheren Status beginnend
    if pCity.getPopulation() < iPopMetropole and pCity.getNumRealBuilding(iBuildingMetropole) == 1:
      pCity.setNumRealBuilding(iBuildingMetropole,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_6",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingProvinz).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)
    if pCity.getPopulation() < iPopProvinz and pCity.getNumRealBuilding(iBuildingProvinz) == 1:
      pCity.setNumRealBuilding(iBuildingProvinz,0)
      if gc.getPlayer(pCity.getOwner()).isHuman():
        CyInterface().addMessage(pCity.getOwner(), True, 15, CyTranslator().getText("TXT_INFO_CITYSTATUS_4",(pCity.getName(),0)), "AS2D_PLAGUE", 2, gc.getBuildingInfo(iBuildingCity).getButton(), ColorTypes(13), pCity.getX(), pCity.getY(), True, True)

    # AI and its slaves
    if not gc.getPlayer(pCity.getOwner()).isHuman():
       PAE_Sklaven.doAIReleaseSlaves(pCity)


# --------------------------------
# Methode auch in CvWorldBuilderScreen.py - immer beide aendern
def doCheckTraitBuildings (pCity):
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

#
def doCheckGlobalTraitBuildings(iPlayer, pCity = None, iOriginalOwner = -1):
    pOwner = gc.getPlayer(iPlayer)
    lGlobal = [
        (gc.getInfoTypeForString("TRAIT_MARITIME"),gc.getInfoTypeForString("BUILDING_TRAIT_MARITIME_GLOBAL")),
        (gc.getInfoTypeForString("TRAIT_CREATIVE"),gc.getInfoTypeForString("BUILDING_TRAIT_CREATIVE_GLOBAL")),
        (gc.getInfoTypeForString("TRAIT_PHILOSOPHICAL"), gc.getInfoTypeForString("BUILDING_TRAIT_PHILOSOPHICAL_GLOBAL"))
    ]

    for (iTrait, iBuilding) in lGlobal:
        # es wurde ein Traitbuilding erobert
        if pCity != None and pCity.getNumRealBuilding(iBuilding) > 0:
            pCity.setNumRealBuilding(iBuilding, 0)
            if iOriginalOwner != -1:
                doCheckGlobalBuilding (iOriginalOwner, iBuilding)

        if pOwner.hasTrait(iTrait):
            doCheckGlobalBuilding (iPlayer, iBuilding)



# Methode fuer lokalen Gebrauch
def doCheckGlobalBuilding (iPlayer, iBuilding):
    pPlayer = gc.getPlayer(iPlayer)
    (city,iter) = pPlayer.firstCity(False)
    if city != None and not city.isNone():
        city.setNumRealBuilding(iBuilding, 1)
        iCount = 0
        while city:
          if city.getNumBuilding(iBuilding) > 0:
            iCount += 1
            if iCount > 1: city.setNumRealBuilding(iBuilding, 0)
          (city,iter) = pPlayer.nextCity(iter, False)

# Begin Inquisition -------------------------------

def doInquisitorPersecution(pCity, pUnit):
    pPlayer = gc.getPlayer( pCity.getOwner( ) )
    iPlayer = pPlayer.getID( )

    iNumReligions = gc.getNumReligionInfos()
    # HI soll PopUp bekommen
    if pPlayer.isHuman():
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_INQUISITION",(pCity.getName(), )) )
        popupInfo.setData1(iPlayer)
        popupInfo.setData2(pCity.getID())
        popupInfo.setData3(pUnit.getID())
        popupInfo.setOnClickedPythonCallback("popupReliaustreibung") # EntryPoints/CvScreenInterface und CvGameUtils / 704
        for iReligion in range(iNumReligions):
          if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
            popupInfo.addPythonButton(gc.getReligionInfo(iReligion).getText(), gc.getReligionInfo(iReligion).getButton())
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_INQUISITION_CANCEL",("", )), "Art/Interface/Buttons/General/button_alert_new.dds")
        popupInfo.setFlags(popupInfo.getNumPythonButtons()-1)
        popupInfo.addPopup(iPlayer)

    ## AI
    #else:
        #ReligionArray = []
        #for iReligion in range(iRange):
          #if iReligion != pPlayer.getStateReligion() and pCity.isHasReligion(iReligion) and pCity.isHolyCityByType(iReligion) == 0:
            #ReligionArray.append(iReligion)

        #if len(ReligionArray) > 0:
          #iRand = myRandom(len(ReligionArray))
          #doInquisitorPersecution2(iPlayer, pCity.getID(), -1, ReligionArray[iRand], pUnit.getID())

    pUnit.kill(1,pUnit.getOwner())
  # -------------

def doInquisitorPersecution2(iPlayer, iCity, iButton, iReligion, iUnit):
    pPlayer = gc.getPlayer(iPlayer)
    pCity = pPlayer.getCity(iCity)
    szButton = gc.getUnitInfo(gc.getInfoTypeForString("UNIT_INQUISITOR")).getButton()
    iStateReligion = pPlayer.getStateReligion()
    iNumReligions = gc.getNumReligionInfos()
    # gets a list of all religions in the city except state religion
    lCityReligions = []
    for iReligionLoop in range(iNumReligions):
        if pCity.isHasReligion( iReligionLoop ):
            if pCity.isHolyCityByType(iReligionLoop) == 0 and iReligionLoop != iStateReligion:
                lCityReligions.append( iReligionLoop )

    # Wenn die Religion ueber PopUp kommt, muss sie mittels Buttonreihenfolge gefunden werden
    if iReligion == -1:
        iReligion = lCityReligions[iButton]

    if iReligion != -1:
        if iReligion != iStateReligion: iHC = -25
        else: iHC = 15

        # Does Persecution succeed
        iRandom = myRandom(100)
        if (iRandom < 95 - (len(lCityReligions) * 5) + iHC):

            pCity.setHasReligion(iReligion, 0, 0, 0)

            if pPlayer.isHuman():
                CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # remove its buildings
            iRange = gc.getNumBuildingInfos()
            for iBuildingLoop in range(iRange):
                if pCity.isHasBuilding(iBuildingLoop):
                    pBuilding = gc.getBuildingInfo(iBuildingLoop)
                    iRequiredReligion = pBuilding.getPrereqReligion( )
                    # Wunder sollen nicht betroffen werden
                    iBuildingClass = pBuilding.getBuildingClassType()
                    thisBuildingClass = gc.getBuildingClassInfo(iBuildingClass)
                    if iRequiredReligion == iReligion and thisBuildingClass.getMaxGlobalInstances() != 1:
                        pCity.setNumRealBuilding (iBuildingLoop,0)
                        #if pPlayer.isHuman():
                            ##Meldung dass das Gebaeude zerstoert wurde
                            #CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_Bildersturm",(pCity.getName(),)),"AS2D_PLAGUE",2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # increasing Anger or Sympathy for an AI
            iRange = gc.getMAX_PLAYERS()
            for iSecondPlayer in range(iRange):
                pSecondPlayer = gc.getPlayer(iSecondPlayer)
                pReligion = gc.getReligionInfo(iReligion)

                # increases Anger for all AIs which have this religion as State Religion
                if (iReligion == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                    pSecondPlayer.AI_changeAttitudeExtra(iPlayer,-2)
                # increases Sympathy for all AIs which have the same State Religion as the inquisitor
                elif (pPlayer.getStateReligion() == pSecondPlayer.getStateReligion() and pSecondPlayer.isAlive()):
                    pSecondPlayer.AI_changeAttitudeExtra(iPlayer,+1)

                # info for all
                if pSecondPlayer.isHuman():
                    iSecTeam = pSecondPlayer.getTeam()
                    if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                        CyInterface().addMessage(iSecondPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(10),pCity.getX(),pCity.getY(),True,True)

            # info for the player
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_NEG",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
            CyInterface().addMessage(iPlayer,True,20,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_GLOBAL_POS",(pCity.getName(),pReligion.getText())),None,2,szButton,ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

            # decrease population by 1, even if mission fails
            if pCity.getPopulation() > 1:
                pCity.changePopulation(-1)
                doCheckCityState(pCity)

        # Persecution fails
        elif pPlayer.isHuman():
            CyInterface().addMessage(iPlayer,True,15,CyTranslator().getText("TXT_KEY_MESSAGE_INQUISITION_FAIL",(pCity.getName(),)),"AS2D_SABOTAGE",2,szButton,ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


    # City Revolt
    pCity.changeOccupationTimer(1)
  # ------

# end Inquisition / Religionsaustreibung


  # City Revolt
  # iTurns = deaktiv
def doCityRevolt(pCity, iTurns):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    pPlot = pCity.plot()

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("City Revolt (Zeile 6485)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Strafe verschaerfen
    #iTurns = iTurns * 2

    # Einheiten stilllegen
    iRange = pPlot.getNumUnits()
    for iUnit in range (iRange):
        pPlot.getUnit(iUnit).setDamage(60, -1)
        if 1 == myRandom(2):
            pPlot.getUnit(iUnit).setImmobileTimer(iTurns)

    #Stadtaufruhr
    pCity.changeHurryAngerTimer (iTurns)

    iTurns = int (iTurns / 2)
    if iTurns < 2: iTurns = 2
    #pCity.changeOccupationTimer (iTurns)
    pCity.setOccupationTimer(iTurns)

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
            iCityCheck  = -1
            # City with forbidden palace shall not revolt
            #~ if gc.getTeam(pOwner.getTeam()).isHasTech(gc.getInfoTypeForString('TECH_POLYARCHY')): iBuilding = gc.getInfoTypeForString('BUILDING_PRAEFECTUR')
            #~ else: iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')
            iRange = pOwner.getNumCities()
            for i in range (iRange):
                pLoopCity = pOwner.getCity(i)
                if not pLoopCity.isNone():
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

            # Stadt soll revoltieren: 3 Runden
            if iRevoltCity != -1:
                pCity = pOwner.getCity(iRevoltCity)
                #pCity.setOccupationTimer(3)
                doCityRevolt(pCity,4)

                # Message for the other city revolt
                if (gc.getPlayer(iAttacker).isHuman()):
                    iRand = 1 + myRandom(6)
                    CyInterface().addMessage(iAttacker, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_1_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(8), pCity.getX(), pCity.getY(), True, True)
                elif (gc.getPlayer(iOwner).isHuman()):
                    iRand = 1 + myRandom(6)
                    CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_REVOLTS_2_"+str(iRand),(pCity.getName(),0)), "AS2D_REVOLTSTART", 2, "Art/Interface/Buttons/Techs/button_brandschatzen.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)

  # --- next city revolt

def doDesertification(pCity, pUnit):
    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iCurrentEra = pPlayer.getCurrentEra()
    iUnitCombatType = pUnit.getUnitCombatType()
    if iCurrentEra > 0 and iUnitCombatType > 0:
        if iUnitCombatType in [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]: return

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
                if pLoopPlot != None and not pLoopPlot.isNone():
                    iPlotFeature = pLoopPlot.getFeatureType()
                    if iPlotFeature in lFeatures:
                        iPlotImprovement = pLoopPlot.getImprovementType()
                        iLoopPlayer = pLoopPlot.getOwner()
                        if pLoopPlot.getBonusType(iLoopPlayer) != iBonusZedern:
                            if iLoopPlayer == iPlayer:
                                if iPlotImprovement == iMine: PlotArray1.append(pLoopPlot)
                                if iPlotImprovement == -1:
                                    if iPlotFeature == iFeatForest: PlotArray1.append(pLoopPlot)
                                    elif iPlotFeature == iFeatSavanna: PlotArray2.append(pLoopPlot)
                                    elif iPlotFeature == iFeatJungle: PlotArray3.append(pLoopPlot)
                                    elif iPlotFeature == iFeatDichterWald: PlotArray5.append(pLoopPlot)
                                elif iPlotImprovement != iHolzLager: PlotArray4.append(pLoopPlot)

                            elif iPlotImprovement != iHolzLager:
                                if iPlotFeature != iFeatDichterWald:
                                    # PAE V: no unit on the plot (Holzraub)
                                    if pLoopPlot.getNumUnits() == 0:
                                        PlotArray6.append(pLoopPlot)

            # Plot wird ausgewaehlt, nach Prioritaet zuerst immer nur Wald checken, wenn keine mehr da, dann Savanne, etc...
            # Wald: Chance: Bronzezeit: 4%, Eisenzeit: 5%, Klassik: 6%
            if len(PlotArray1) > 0:
                iChance = 30 - iCurrentEra * 5
                if myRandom(iChance) == 0: PlotArrayX = PlotArray1
            # Savanne: Bronze: 5%, Eisen: 10%, Klassik: 20%
            elif len(PlotArray2) > 0:
                iChance = 20 - iCurrentEra * 5
                if myRandom(iChance) == 0: PlotArrayX = PlotArray2
            # Dschungel: wie Wald
            elif len(PlotArray3) > 0:
                iChance = 30 - iCurrentEra * 5
                if myRandom(iChance) == 0: PlotArrayX = PlotArray3
            # Bewirt. Feld ohne Holzlager: wie Savanne
            elif len(PlotArray4) > 0:
                iChance = 20 - iCurrentEra * 5
                if myRandom(iChance) == 0: PlotArrayX = PlotArray4
            # Dichter Wald: Bronze: 2%, Eisen: 2.5%, Klassik: 3%
            elif len(PlotArray5) > 0:
                iChance = 60 - iCurrentEra * 10
                if myRandom(iChance) == 0: PlotArrayX = PlotArray5

            # Ausl. Feld 10%, erst wenn es nur mehr 1 Waldfeld gibt (das soll auch bleiben)
            if len(PlotArray1) + len(PlotArray2) + len(PlotArray3) + len(PlotArray4) + len(PlotArray5) < 2:
                PlotArrayX = [] # Feld leeren
                if len(PlotArray6) > 0 and myRandom(10) == 0: PlotArrayX = PlotArray6

            # Gibts einen Waldplot
            if len(PlotArrayX) > 0:
                iPlot = myRandom(len(PlotArrayX))
                pPlot = PlotArrayX[iPlot]
                iPlotPlayer = pPlot.getOwner()
                # Auswirkungen Feature (Wald) entfernen, Holzlager entfernen, Nachbar checken
                # Feature (Wald) entfernen
                # Dichten Wald zu normalen Wald machen
                if pPlot.getFeatureType() == iFeatDichterWald:
                    pPlot.setFeatureType(iFeatForest,0)
                else:
                    pPlot.setFeatureType(-1,0)
                    # Lumber camp entfernen
                    # Flunky: Holzlager-Felder werden garnicht erst ausgewaehlt
                    #if PlotArrayX[iPlot].getImprovementType() == iHolzLager: PlotArrayX[iPlot].setImprovementType(-1)

                # Meldung
                # Attention: AS2D_CHOP_WOOD is additional defined in XML/Audio/Audio2DScripts.xml   (not used, AS2D_BUILD_FORGE instead)
                if iPlotPlayer == iPlayer:
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_1",(pCity.getName(),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

                elif iPlotPlayer > -1 and iPlotPlayer != gc.getBARBARIAN_PLAYER():
                    pPlotPlayer = gc.getPlayer(iPlotPlayer)
                    CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_2",(pPlotPlayer.getCivilizationShortDescription(0),pPlotPlayer.getCivilizationAdjective(1))), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    CyInterface().addMessage(iPlotPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_RODUNG_3",(pPlayer.getCivilizationShortDescription(0),0)), 'AS2D_BUILD_FORGE', 2, ',Art/Interface/Buttons/Builds/BuildChopDown.dds,Art/Interface/Buttons/Actions_Builds_LeaderHeads_Specialists_Atlas.dds,7,8', ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
                    pPlotPlayer.AI_changeAttitudeExtra(iPlayer,-1)

    # Feature Waldrodung Ende

# Emigrant -----------------
def doEmigrant(pCity, pUnit):
    pPlot = pCity.plot()
    # Kultur auslesen
    txt = CvUtil.getScriptData(pUnit, ["p", "t"])
    if txt != "": iPlayerCulture = int(txt)
    else: iPlayerCulture = pUnit.getOwner()
    # Kultur = 100*Pop, max. 1000
    iCulture = pCity.getPopulation() * 100
    if iCulture > 1000: iCulture = 1000
    # Stadt Kultur geben
    pPlot.changeCulture(iPlayerCulture,iCulture,1)
    pUnit.kill(1,pUnit.getOwner())

    pCity.changePopulation(1)
    # PAE Provinzcheck
    doCheckCityState(pCity)

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Emigrant 2 City (Zeile 6458)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)


# disband city
def doDisbandCity(pCity, pUnit, pPlayer):
    iRand = myRandom(10)
    if iRand < 5:
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_OK",(pCity.getName(),)), "AS2D_PILLAGE", 2, None, ColorTypes(13), pCity.getX(), pCity.getY(), False, False)
        pPlayer.disband(pCity)
        #iUnitType = gc.getInfoTypeForString("UNIT_EMIGRANT")
        #pPlayer.initUnit(iUnitType, pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_RESERVE, DirectionTypes.DIRECTION_SOUTH)
    else:
        CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISBAND_CITY_NOT_OK",(pCity.getName(),)), "AS2D_CITY_REVOLT", 2, None, ColorTypes(7), pCity.getX(), pCity.getY(), False, False)
        pUnit.kill(1,pUnit.getOwner())

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
    if bSpread == True:
        pCity = PlagueCity
        iPlayer = PlagueCity.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        iThisTeam = pPlayer.getTeam()
        team = gc.getTeam(iThisTeam)

        #iMedicine1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE1')
        #iMedicine2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE2')
        #iMedicine3 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MEDICINE3')
        #iMedicine4 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HEILKUNDE')

        # City Revolt
        #if team.isHasTech(iMedicine1) or  team.isHasTech(iMedicine2) or  team.isHasTech(iMedicine3) or  team.isHasTech(iMedicine4): pCity.setOccupationTimer(2)
        #else: pCity.setOccupationTimer(3)

        # message for all
        iRange = gc.getMAX_PLAYERS()
        for iSecondPlayer in range(iRange):
            pSecondPlayer = gc.getPlayer(iSecondPlayer)
            if (pSecondPlayer.isHuman()):
                iSecTeam = pSecondPlayer.getTeam()
                if gc.getTeam(iSecTeam).isHasMet(pPlayer.getTeam()):
                    if pSecondPlayer.isHuman():
                      CyInterface().addMessage(iSecondPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD",(pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)

        if pPlayer.isHuman():
            CyInterface().addMessage(iPlayer, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_PEST_SPREAD",(pCityOrig.getName(), pCity.getName())), "AS2D_PLAGUE", 2, 'Art/Interface/Buttons/Actions/button_skull.dds', ColorTypes(13), pCity.getX(),  pCity.getY(), True, True)
        # end message

        # Plague building gets added into city => culture -50
        pCity.setNumRealBuilding(iBuildingPlague,1)
  # --- plague spread



# Provinz Rebellion / Statthalter
def doProvinceRebellion(pCity):
    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Provinzrebellion (Zeile 4578)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iPlayer = pCity.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    iBuilding = gc.getInfoTypeForString('BUILDING_PROVINZPALAST')

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
            if len(PlayerArray) > 0:
                iRand = myRandom(len(PlayerArray))
                iNewOwner = PlayerArray[iRand]
    # ----------------

    # Radius 5x5 Plots und dessen Staedte checken

    if not pCity.isCapital():
        iRange = 5
        iX = pCity.getX()
        iY = pCity.getY()
        for i in range (-iRange, iRange+1):
            for j in range (-iRange, iRange+1):
                loopPlot = plotXY(iX, iY, i, j)
                if loopPlot != None and not loopPlot.isNone():
                    if loopPlot.isCity():
                        loopCity = loopPlot.getPlotCity()
                        if pCity.getID() != loopCity.getID() and not loopCity.isGovernmentCenter() and loopCity.getOwner() == iPlayer:
                            iLoopX = iX+i
                            iLoopY = iY+j
                            iChance = 100
                            for i2 in range (-iRange, iRange+1):
                                for j2 in range (-iRange, iRange+1):
                                    loopPlot2 = plotXY(iLoopX, iLoopY, i2, j2)
                                    if loopPlot2 != None and not loopPlot2.isNone():
                                        if loopPlot2.isCity():
                                            loopCity2 = loopPlot2.getPlotCity()
                                            if pCity.getID() != loopCity2.getID():
                                                if loopCity2.isCapital():
                                                    iChance = 0
                                                    break
                                                elif loopCity2.isGovernmentCenter():
                                                    iChance = 50
                                if iChance == 0: break
                            if iChance > 0:
                                if myRandom(100) < iChance:
                                    doRenegadeCity(loopCity, iNewOwner, -1, -1, -1)
        doRenegadeCity(pCity, iNewOwner, -1, -1, -1)


# ueberlaufende Stadt / City renegade
# When Unit gets attacked: LoserUnitID (must not get killed automatically) , no unit = -1
def doRenegadeCity(pCity, iNewOwner, LoserUnitID, iWinnerX, iWinnerY):

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Renegade City (Zeile 4637)",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    iRebel = gc.getInfoTypeForString("UNIT_REBELL")
    iPartisan = gc.getInfoTypeForString("UNIT_FREEDOM_FIGHTER")
    lRebels = [iRebel, iPartisan]

    lTraitPromos = [gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")]
    iPromoLoyal = gc.getInfoTypeForString("PROMOTION_LOYALITAT")

    if iNewOwner == -1: iNewOwner = gc.getBARBARIAN_PLAYER()

    pNewOwner = gc.getPlayer(iNewOwner)

    iX = pCity.getX()
    iY = pCity.getY()
    pPlot = pCity.plot()
    iOldOwner = pCity.getOwner()

    # Einheiten auslesen bevor die Stadt ueberlaeuft
    UnitArray = []
    JumpArray = []
    
    for iUnit in range (pPlot.getNumUnits()):
        # Nicht die Einheit, die gerade gekillt wird killen, sonst Error
        pLoopUnit = pPlot.getUnit(iUnit)
        if LoserUnitID != pLoopUnit.getID():
            # Freiheitskaempfer, Rebellen oder Unsichtbare rauswerfen
            if pLoopUnit.getUnitType() in lRebels or pLoopUnit.getInvisibleType() > -1:
                JumpArray.append(pLoopUnit)
            elif pLoopUnit.getOwner() == iOldOwner:
                # Einige Einheiten bleiben loyal und fliehen
                if pLoopUnit.isHasPromotion(iPromoLoyal): iChance = 4
                else: iChance = 8
                iRand = myRandom(10)
                if iRand < iChance:
                    UnitArray.append(pLoopUnit)
                    if pLoopUnit.isCargo():
                        pLoopUnit.setTransportUnit(None)
                # else: Einheit kann sich noch aus dem Staub machen
                else: JumpArray.append(pLoopUnit)
            else: JumpArray.append(pLoopUnit)

    for pUnit in JumpArray:
        pUnit.jumpToNearestValidPlot()

    # Einheiten generieren
    for pLoopUnit in UnitArray:
        if pLoopUnit == None or pLoopUnit.isNone(): 
            # TEST
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 1 - Unit none",iOldOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)
            continue
        iUnitOwner = iNewOwner

        iUnitType = pLoopUnit.getUnitType()
        iUnitAIType = pLoopUnit.getUnitAIType()
        sUnitName = pLoopUnit.getName()
        iUnitCombatType = pLoopUnit.getUnitCombatType()

        # TEST
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Test 2 - iUnitOwner",iUnitOwner)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        # UnitAIType -1 (NO_UNITAI) -> UNITAI_UNKNOWN = 0 , ATTACK = 4, City Defense = 10
        # happened: Emigrant = 4 !
        if iUnitAIType in [-1, 0, 4]:
            if   iUnitType == gc.getInfoTypeForString('UNIT_SLAVE'): iUnitAIType = 0
            elif iUnitType == gc.getInfoTypeForString('UNIT_FREED_SLAVE'): iUnitAIType = 12
            elif iUnitType == gc.getInfoTypeForString('UNIT_EMIGRANT'): iUnitAIType = 2
            elif iUnitType == gc.getInfoTypeForString('UNIT_TRADE_MERCHANT'): iUnitAIType = 19
            elif iUnitType == gc.getInfoTypeForString('UNIT_TRADE_MERCHANTMAN'): iUnitAIType = 19
            else: iUnitAIType = 0

        # Slaves will be freed, nur wenn dessen Besitzer neu ist
        if iUnitType == gc.getInfoTypeForString('UNIT_SLAVE'):
            iUnitType = gc.getInfoTypeForString('UNIT_FREED_SLAVE')

        # Create a new unit
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",(gc.getUnitInfo(iUnitType).getDescription(),iUnitType)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Unit Typ",iUnitType)), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if iUnitType != -1:
            NewUnit = pNewOwner.initUnit(iUnitType, iX, iY, UnitAITypes(iUnitAIType), DirectionTypes.DIRECTION_SOUTH)

            # Emigrant und dessen Kultur
            if iUnitType == gc.getInfoTypeForString('UNIT_EMIGRANT'):
                CvUtil.addScriptData(NewUnit, "p", iOldOwner)

            PAE_Unit.copyName(NewUnit, iUnitType, sUnitName)

            if iUnitCombatType != -1:
                NewUnit.setExperience(pLoopUnit.getExperience(), -1)
                NewUnit.setLevel(pLoopUnit.getLevel())
                if pLoopUnit.getCaptureUnitType(gc.getPlayer(iOldOwner).getCivilizationType()) == -1:
                    NewUnit.setDamage(pLoopUnit.getDamage(), -1)

                # Check its promotions
                for iLoopPromo in range(gc.getNumPromotionInfos()):
                    if pLoopUnit.isHasPromotion(iLoopPromo):
                        # PAE V: Trait-Promotions
                        # 1. Agg Promo weg
                        # 2. Trait nur fuer Eigenbau: eroberte Einheiten sollen diese Trait-Promos nicht erhalten
                        if not iLoopPromo in lTraitPromos: # or pNewOwner.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")):
                            NewUnit.setHasPromotion(iLoopPromo, True)
        pLoopUnit.kill(1,pLoopUnit.getOwner())

    if iNewOwner == gc.getBARBARIAN_PLAYER():
        pNewOwner.initUnit(iPartisan,  iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
        pNewOwner.initUnit(iPartisan,  iX, iY, UnitAITypes(10), DirectionTypes.DIRECTION_SOUTH)
        pNewOwner.initUnit(iPartisan,  iX, iY, UnitAITypes(4), DirectionTypes.DIRECTION_SOUTH)

    # Stadt laeuft automatisch ueber (CyCity pCity, BOOL bConquest, BOOL bTrade)
    pNewOwner.acquireCity(pCity,0,1)
    #Pointer anpassen
    if pPlot.isCity():
        pCity = pPlot.getPlotCity()
        if pCity != None and not pCity.isNone():
            # Kultur auslesen
            iCulture = pCity.getCulture(iOldOwner)
            # Kultur regenerieren - funkt net
            if iCulture > 0:
                pCity.changeCulture(iNewOwner,iCulture,True)

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
    if pPlot != None and not pPlot.isNone():
        PlotArray = []
        iEnemyUnits = 0
        iRange = 1
        iX = pCity.getX()
        iY = pCity.getY()
        for x in range(-iRange, iRange+1):
            for y in range(-iRange, iRange+1):
                loopPlot = plotXY(iX, iY, x, y)
                if loopPlot != None and not loopPlot.isNone():
                    iNumUnits = loopPlot.getNumUnits()
                    if iNumUnits >= 4:
                        for i in range (iNumUnits):
                            iOwner = loopPlot.getUnit(i).getOwner()
                            if pTeam.isAtWar(gc.getPlayer(iOwner).getTeam()):
                                if not loopPlot.getUnit(i).isInvisible(pPlayer.getTeam(),0):
                                    PlotArray.append(loopPlot)
                                    iEnemyUnits += loopPlot.getNumUnits()
                                    break
        # Stadteinheiten durchgehen
        if len(PlotArray) > 0:
            # Schleife fuer Stadteinheiten
            # Bombardement
            iNumUnits = pPlot.getNumUnits()
            for i in range (iNumUnits):
                pUnit = pPlot.getUnit(i)
                if pUnit.isRanged():
                    if pUnit.getOwner() == iPlayer:
                        if not pUnit.isMadeAttack() and pUnit.getImmobileTimer() <= 0:
                            # getbestdefender -> getDamage
                            BestDefender = []
                            for plot in PlotArray:
                                pBestDefender = plot.getBestDefender(-1,-1,pUnit,1,0,0)
                                BestDefender.append((pBestDefender.getDamage(),plot))
                            # bestdefenderplot angreifen ->  pCityUnit.rangeStrike(x,y)
                            BestDefender.sort()
                            # Ab ca 50% Schaden aufhoeren
                            if BestDefender[0][0] < 55:
                                plot = BestDefender[0][1]
                                pUnit.rangeStrike(plot.getX(),plot.getY())
                            else:
                                break

            # AI - Extern Unit support
            iCityUnits = pPlot.getNumUnits()
            iMaintainUnits = pCity.getYieldRate(0) - iCityUnits
            # 1) Reservisten
            if iMaintainUnits > 0 and iCityUnits * 2 <= iEnemyUnits:
                iReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST
                if iReservists > 0:
                    # Einheiten definieren
                    lResUnits = []
                    # Schildtraeger fuer AI immer verfuegbar
                    lResUnits.append(gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"))
                    # Auxiliars
                    iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_AUXILIAR"))
                    if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()): lResUnits.append(iUnit)
                    iUnit = gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE")
                    if pTeam.isHasTech(gc.getUnitInfo(iUnit).getPrereqAndTech()) and pCity.hasBonus(gc.getInfoTypeForString("BONUS_HORSE")): lResUnits.append(iUnit)
                    # Archer
                    iUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"))
                    if pCity.canTrain(iUnit,0,0): lResUnits.append(iUnit)
                    else: lResUnits.append(gc.getInfoTypeForString("UNIT_ARCHER"))

                    while iReservists > 0 and iMaintainUnits > 0:
                        # choose unit
                        iRand = myRandom(len(lResUnits))
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
    if iMaintainUnits <= 0: return

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
      for i in range (iRange):
            pLoopUnit = pCityPlot.getUnit(i)
            if pLoopUnit.getUnitCombatType() != -1:
                if pLoopUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
                    (iExtraSupply, _) = PAE_Unit.getSupply(pLoopUnit)
                    if iExtraSupply <= iMaintainUnits:
                        iMaintainUnits -= iExtraSupply
                        iExtraSupply = 0
                    else:
                        iExtraSupply -= iMaintainUnits
                        iMaintainUnits = 0
                    # set new supply tickets
                    PAE_Unit.setSupply(pLoopUnit,iExtraSupply)
                else:
                    lUnitsAll.append(pLoopUnit)

            if iMaintainUnits == 0: break

      if iMaintainUnits > 0 and len(lUnitsAll) > 0:
          lUnits = random.sample(lUnitsAll, iMaintainUnits)
          # harm units
          if len(lUnits) > 0:
              # Betrifft Stadt
              # 20%: -1 Pop
              # 10%: FEATURE_SEUCHE
              iRand = myRandom(10)
              # - 1 Pop
              if iRand < 2 and popCity > 1:
                  pCity.changePopulation(-1)
                  bCheckCityState = True
                  if pPlayer.isHuman():
                      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_2",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
              # Seuche
              elif iRand == 2:
                  pCityPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_SEUCHE"),1)
                  if pPlayer.isHuman():
                      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_3",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
              # less food
              elif pCity.getFood() > 10:
                  # Warnung und -20% Food Storage
                  iFoodStoreChange = pCity.getFood() / 100 * 20
                  pCity.changeFood(-iFoodStoreChange)
                  if pPlayer.isHuman():
                      CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_1",(pCity.getName(),(pCity.getYieldRate(0) * iFactor - iCityUnits)*(-1))), None, 2, "Art/Interface/Buttons/General/button_alert_new.dds", ColorTypes(7), pCity.getX(), pCity.getY(), True, True)
              # ------

              # Betrifft Einheiten
              iJumpedOut = 0
              for unit in lUnits:
                  # Unit nicht mehr killen (Weihnachtsbonus :D ab 7.12.2012)
                  iDamage = unit.getDamage()
                  if iDamage < 70:
                      unit.changeDamage(30,False)
                      if gc.getPlayer(unit.getOwner()).isHuman():
                          CyInterface().addMessage(unit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_NOSUPPLY_CITY",(pCity.getName(),unit.getName(),30)), None, 2, None, ColorTypes(12), unit.getX(), unit.getY(), True, True)
                  else:
                      iJumpedOut += 1
                      if unit.getDamage() < 85: unit.setDamage(85,unit.getOwner())
                      unit.jumpToNearestValidPlot()
                      if gc.getPlayer(unit.getOwner()).isHuman():
                          CyInterface().addMessage(unit.getOwner(), True, 5, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4",(pCity.getName(),unit.getName())), None, 2, unit.getButton(), ColorTypes(12), unit.getX(), unit.getY(), True, True)

              # Wenn die Stadt durch Buildings stark heilt
              if iJumpedOut == 0:
                  # Chance rauszuwerfen 33%
                  if 1 == myRandom(3):
                      Einheiten = 1 + myRandom(len(lUnits))
                      lUnits2 = random.sample(lUnits, Einheiten)
                      for pUnit in lUnits2:
                          pUnit.jumpToNearestValidPlot()
                          if pPlayer.isHuman():
                              CyInterface().addMessage(pCity.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_UNITS_STARVATION_4",(pCity.getName(),pUnit.getName())), "AS2D_STRIKE", 2, pUnit.getButton(), ColorTypes(7), pUnit.getX(), pUnit.getY(), True, True)
