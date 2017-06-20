# Scenario PeloponnesianWarKeinpferd

# Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import PyHelpers

import PAE_City
# Defines
gc = CyGlobalContext()


def onEndGameTurn(iGameTurn):
    if iGameTurn == 228:
        # Athen (0) soll von 414 an mit Sparta (1) ewig den dekeleischen Krieg fuehren
        gc.getTeam(gc.getPlayer(0).getTeam()).setPermanentWarPeace(gc.getPlayer(1).getTeam(), true)


def onBeginPlayerTurn(iGameTurn, pPlayer):

    iTeam = pPlayer.getTeam()
    iAthen = 0
    iSparta = 1
    iKorinth = 2
    iTheben = 4
    iSyrakus = 16
    # Event 1: Poteidaia verlangt geringere Abgaben
    iTurnPotei = 8  # Runde, in der das Popup fuer den Menschen erscheinen soll
    # Die KI reagiert sofort noch in dieser Runde, der Mensch erhaelt erst in der naechsten Runde das Popup
    # Nur, wenn Poteidaia existiert + von Athen kontrolliert wird
    pPoteidaia = CyMap().plot(56, 46).getPlotCity()
    if iTeam == iAthen and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia is not None:
       if pPoteidaia.getOwner() == iAthen:
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia1")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_TRIBUT_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia1([iAiDecision])
    # Event 2: Krieg um Poteidaia
    iTurnPotei = 18  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    # Nur, wenn Poteidaia existiert + von Athen kontrolliert wird
    if iTeam == iAthen and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia is not None:
        if pPoteidaia.getOwner() == iAthen:
                # Event 2.1: Reaktion Athens
                # Poteidaia wechselt zu Korinth (Team 2)
            PAE_City.doRenegadeCity(pPoteidaia, 2, -1)
            pKorinth = gc.getPlayer(iKorinth)
            ePantodapoi = gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON")
            iRange = CvUtil.myRandom(3)
            # Korinth erhaelt 0 - 2 zusaetzliche makedonische Hilfstrupps in Poteidaia
            for i in range(iRange):
                pKorinth.initUnit(ePantodapoi, 56, 46, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 15, CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_WORLDNEWS", ()), None, 2, None, ColorTypes(11), 0, 0, False, False)
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia2")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_ATHEN_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia2([iAiDecision])
    # Nur, wenn Poteidaia existiert + von Korinth oder Athen kontrolliert wird (menschlicher Spieler spielt Korinth: zu diesem Zeitpunkt gehoert Poteidaia noch Athen; KI spielt Korinth: ist bereits zu Korinth gewechselt)
    elif iTeam == iKorinth and ((iGameTurn == iTurnPotei-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPotei and not pPlayer.isHuman())) and not pPoteidaia.isNone() and pPoteidaia is not None:
        if pPoteidaia.getOwner() == iKorinth or pPoteidaia.getOwner() == iAthen:
            # Event 2.2: Reaktion Korinths
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Poteidaia3")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_POTEIDAIA_KRIEG_KORINTH_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Poteidaia3([iAiDecision])
    # Event 3: Megara unterstuetzt Korinth
    iTurnMegaraAthen = 22  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    # Nur, wenn Megara existiert + von Korinth kontrolliert wird
    pMegara = CyMap().plot(55, 30).getPlotCity()
    if iTeam == iAthen and ((iGameTurn == iTurnMegaraAthen-1 and pPlayer.isHuman()) or (iGameTurn == iTurnMegaraAthen and not pPlayer.isHuman())) and not pMegara.isNone() and pMegara is not None:
        if pMegara.getOwner() == iKorinth:
            # Event 3.1: Reaktion Athens
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Megara1")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_ATHEN_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Megara1([iAiDecision])
    # Event 3.2: Reaktion Spartas (nur wenn Sparta noch keinen Krieg mit Athen hat)
    iTurnMegaraSparta = 23  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    # Nur, wenn Megara existiert + von Korinth kontrolliert wird
    if iTeam == iSparta and ((iGameTurn == iTurnMegaraSparta-1 and pPlayer.isHuman()) or (iGameTurn == iTurnMegaraSparta and not pPlayer.isHuman())) and not pMegara.isNone() and pMegara is not None:
        if pMegara.getOwner() == iKorinth and not gc.getTeam(iTeam).isAtWar(iAthen):
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Megara2")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_MEGARA_SPARTA_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Megara2([iAiDecision])
    # Event 4: Kriegseintritt Thebens
    iTurnPlataiai = 28  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    if iTeam == iTheben and ((iGameTurn == iTurnPlataiai-1 and pPlayer.isHuman()) or (iGameTurn == iTurnPlataiai and not pPlayer.isHuman())):
        if not gc.getTeam(iTeam).isAtWar(iAthen):  # Nur wenn Theben und Athen Frieden haben
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Plataiai1")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_PLATAIAI_THEBEN_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Plataiai1([iAiDecision])
    # Event 5: Volksversammlung Athens will Krieg gegen Syrakus
    # Event 5.1: Ankuendigung fuer Athen
    iTurnSyra1 = 194  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    pSyrakus = CyMap().plot(15, 24).getPlotCity()
    # Nur wenn Syrakus (Stadt) noch existiert und der Civ Syrakus gehoert
    if iTeam == iAthen and (iGameTurn == iTurnSyra1 - 1) and not pSyrakus.isNone() and pSyrakus is not None:
        if pSyrakus.getOwner() == iSyrakus:
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_SAVEMONEY", ()))
                popupInfo.addPopup(iPlayer)
    # Event 5.2: Athen waehlt Groesse der Flotte
    iTurnSyra2 = 204  # Runde, in der die Popups fuer den Menschen erscheinen sollen
    if iTeam == iAthen and ((iGameTurn == iTurnSyra2 - 1 and pPlayer.isHuman()) or (iGameTurn == iTurnSyra2 and not pPlayer.isHuman())):
        if not gc.getTeam(iTeam).isAtWar(iSyrakus):  # Nur wenn Syrakus und Athen Frieden haben
            if pPlayer.isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_DESC", ()))
                popupInfo.setOnClickedPythonCallback("peloponnesianWarKeinpferd_Syra1")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_1", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_2", ()), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_EVENT_SYRAKUS_ATHEN_OPTION_3", ()), "")
                popupInfo.addPopup(iPlayer)
            else:
                iAiDecision = CvUtil.myRandom(3)
                CvScreensInterface.peloponnesianWarKeinpferd_Syra1([iAiDecision])

    # Temporaere Effekte der Events rueckgaengig machen (Event 3.1 Handelsboykott, Event 3.2 Bronze fuer Sparta)
    if iGameTurn == iTurnMegaraAthen + 10:
        iAthen = 0
        iNordIonien = 12
        iSuedIonien = 13
        eHafen = gc.getInfoTypeForString("BUILDING_HARBOR")
        eMarkt = gc.getInfoTypeForString("BUILDING_MARKET")
        eHafenClass = gc.getBuildingInfo(eHafen).getBuildingClassType()
        eMarktClass = gc.getBuildingInfo(eMarkt).getBuildingClassType()
        lPlayer = [iAthen, iNordIonien, iSuedIonien]
        for iPlayer in lPlayer:
            pPlayer = gc.getPlayer(iPlayer)
            iNumCities = pPlayer.getNumCities()
            for iCity in range(iNumCities):
                pCity = pPlayer.getCity(iCity)
                if pCity is not None and not pCity.isNone():
                    if pCity.isHasBuilding(eHafen):
                        iStandard = 0  # Normaler Goldertrag ohne Event
                        pCity.setBuildingCommerceChange(eHafenClass, 0, iStandard)  # 0 = Gold
                    if pCity.isHasBuilding(eMarkt):
                        iStandard = 0
                        pCity.setBuildingCommerceChange(eMarktClass, 0, iStandard)  # 0 = Gold
    if iGameTurn == iTurnMegaraSparta + 10:
        # Bronze wird a
        eBronze = gc.getInfoTypeForString("BONUS_BRONZE")
        pCity = CyMap().plot(52, 23).getPlotCity()
        if pCity is not None and not pCity.isNone():
            if pCity.getFreeBonus(eBronze) > 1:
                pCity.changeFreeBonus(eBronze, -1)


def onEndPlayerTurn(iPlayer, iGameTurn):
    # Runde 1: In Runde 5 soll das mit Korkyra im Krieg liegende Epidamnos Vasall von Korinth werden
    if iGameTurn == 5:
        iCivKorinth = 2
        iCivKorkyra = 6
        iCivEpidamnos = 7
        iCivSparta = 1
        if iPlayer == iCivEpidamnos:

            iTeamKorinth = gc.getPlayer(iCivKorinth).getTeam()
            iTeamEpidamnos = gc.getPlayer(iCivEpidamnos).getTeam()
            pTeamEpidamnos = gc.getTeam(iTeamEpidamnos)

            if not pTeamEpidamnos.isVassal(iTeamKorinth):

                iTeamKorinth = gc.getPlayer(iCivKorinth).getTeam()
                gc.getTeam(iTeamKorinth).assignVassal(iTeamEpidamnos, 0)  # Vassal, but no surrender

                # Meldungen an die Spieler
                iRange = gc.getMAX_PLAYERS()
                for iLoopPlayer in range(iRange):
                    pLoopPlayer = gc.getPlayer(iLoopPlayer)
                    if pLoopPlayer.isHuman():
                        # Meldung Korkyra Human
                        if iLoopPlayer == iCivKorkyra:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_KERKYRA", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_KORKYRA", ("",)))
                            popupInfo.addPopup(iThisPlayer)
                        elif iLoopPlayer == iCivKorinth:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_ALL", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_KORINTH", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                        # Meldung an alle Humans
                        else:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_EPIDAMNOS_PLAYER_ALL", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
